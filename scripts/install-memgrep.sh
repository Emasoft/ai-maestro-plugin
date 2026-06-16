#!/usr/bin/env bash
# install-memgrep.sh — install the memgrep memory-recall binary.
#
# Install order (first success wins):
#   1. Already on PATH                       -> nothing to do (idempotent).
#   2. Prebuilt release binary               -> download from this plugin's
#      GitHub release assets, verify sha256, install to ~/.local/bin.
#      End-users need NO Rust toolchain for this path.
#   3. cargo install --path scripts/memgrep  -> local build fallback for
#      platforms without a prebuilt asset (needs a Rust toolchain).
#
# If every path fails the script exits non-zero, but the memory-recall
# protocol still works: recall degrades to plain `grep` over the notes
# (see ~/.claude/rules/markdown-memory-recall.md). Degrade, never break.
#
# Usage:
#   install-memgrep.sh [--force] [--version vX.Y.Z]
#     --force            reinstall even if memgrep is already on PATH
#     --version vX.Y.Z   pin a specific plugin release (default: latest)
set -euo pipefail

REPO="Emasoft/ai-maestro-plugin"
INSTALL_DIR="${MEMGREP_INSTALL_DIR:-$HOME/.local/bin}"
FORCE=0
PIN_TAG=""

while [ $# -gt 0 ]; do
  case "$1" in
    --force) FORCE=1 ;;
    --version) PIN_TAG="${2:?--version needs a tag argument}"; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ "$FORCE" -eq 0 ] && command -v memgrep >/dev/null 2>&1; then
  echo "memgrep already installed: $(command -v memgrep) ($(memgrep --version 2>/dev/null || echo 'version unknown'))"
  exit 0
fi

# --- 1. resolve platform -> release asset suffix --------------------------
OS="$(uname -s)"
ARCH="$(uname -m)"
case "$OS-$ARCH" in
  Darwin-arm64)          PLATFORM="darwin-arm64" ;;
  Darwin-x86_64)         PLATFORM="darwin-x64" ;;
  Linux-x86_64)          PLATFORM="linux-x64" ;;
  Linux-aarch64)         PLATFORM="" ;;  # no prebuilt yet -> cargo fallback
  *)                     PLATFORM="" ;;
esac

# --- 2. prebuilt binary from GitHub release assets -------------------------
try_prebuilt() {
  [ -n "$PLATFORM" ] || return 1
  command -v curl >/dev/null 2>&1 || return 1
  command -v shasum >/dev/null 2>&1 || command -v sha256sum >/dev/null 2>&1 || return 1

  local tag="$PIN_TAG"
  if [ -z "$tag" ]; then
    # Resolve the latest release tag. gh is preferred (authenticated, no rate
    # limit); curl against the public API is the unauthenticated fallback.
    if command -v gh >/dev/null 2>&1; then
      tag="$(gh release view --repo "$REPO" --json tagName --jq .tagName 2>/dev/null || true)"
    fi
    if [ -z "$tag" ]; then
      tag="$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" 2>/dev/null \
             | grep -m1 '"tag_name"' | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/' || true)"
    fi
  fi
  [ -n "$tag" ] || { echo "could not resolve a release tag" >&2; return 1; }

  local asset="memgrep-${PLATFORM}.tar.gz"
  local base="https://github.com/$REPO/releases/download/$tag"
  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN

  echo "downloading $asset from release $tag ..."
  curl -fsSL -o "$tmp/$asset" "$base/$asset" || { echo "no prebuilt asset for $PLATFORM in $tag" >&2; return 1; }
  curl -fsSL -o "$tmp/$asset.sha256" "$base/$asset.sha256" || { echo "checksum file missing for $asset in $tag — refusing unverified install" >&2; return 1; }

  # Verify checksum BEFORE unpacking — never run/unpack an unverified blob.
  local expected actual
  expected="$(awk '{print $1}' "$tmp/$asset.sha256")"
  if command -v sha256sum >/dev/null 2>&1; then
    actual="$(sha256sum "$tmp/$asset" | awk '{print $1}')"
  else
    actual="$(shasum -a 256 "$tmp/$asset" | awk '{print $1}')"
  fi
  if [ "$expected" != "$actual" ]; then
    echo "sha256 MISMATCH for $asset (expected $expected, got $actual) — aborting" >&2
    return 1
  fi

  tar -xzf "$tmp/$asset" -C "$tmp"
  [ -f "$tmp/memgrep" ] || { echo "archive did not contain a memgrep binary" >&2; return 1; }
  mkdir -p "$INSTALL_DIR"
  install -m 0755 "$tmp/memgrep" "$INSTALL_DIR/memgrep"
  echo "installed prebuilt memgrep -> $INSTALL_DIR/memgrep (sha256 verified)"
  case ":$PATH:" in
    *":$INSTALL_DIR:"*) : ;;
    *) echo "NOTE: $INSTALL_DIR is not on PATH — add it to your shell profile." ;;
  esac
  return 0
}

# --- 3. cargo build fallback ------------------------------------------------
try_cargo() {
  command -v cargo >/dev/null 2>&1 || return 1
  # The crate lives inside the installed plugin; resolve its root relative to
  # this script so the path survives plugin-cache version changes.
  local plugin_root
  plugin_root="$(cd "$(dirname "$0")/.." && pwd)"
  [ -f "$plugin_root/scripts/memgrep/Cargo.toml" ] || { echo "scripts/memgrep not found under $plugin_root" >&2; return 1; }
  echo "building memgrep from source with cargo (this can take a minute) ..."
  cargo install --path "$plugin_root/scripts/memgrep" --locked
  echo "installed memgrep via cargo -> $(command -v memgrep || echo "$HOME/.cargo/bin/memgrep")"
  return 0
}

if try_prebuilt; then exit 0; fi
echo "prebuilt install unavailable — trying cargo fallback ..." >&2
if try_cargo; then exit 0; fi

cat >&2 <<'EOF'
memgrep could not be installed (no prebuilt asset for this platform and no
Rust toolchain). The memory-recall protocol still works WITHOUT memgrep:

    grep -rliE "<symptom>" "<memdir>"

recall degrades to plain grep — degrade, never break. To get memgrep later:
install Rust (https://rustup.rs) and re-run this script.
EOF
exit 1
