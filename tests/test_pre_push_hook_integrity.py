"""Tests for the pre-push hook's sha256 integrity pin (TRDD-71a2239a).

`.githooks/pre-push` is a STATIC committed bash hook (NOT generated). Its
sha256 is pinned in `.githooks/pre-push.sha256` so an out-of-band edit that
silently weakens the hook cannot be merged unseen: editing the hook forces a
matching pin update in the SAME commit, which CI re-verifies (a plain
`sha256sum -c` step in ci.yml AND release.yml). These tests are the
developer-local mirror of that CI gate, so the publish gate / `run-all-tests.py`
catches a desync BEFORE CI does.

Three things are asserted:
  1. The pin file exists and its leading digest equals sha256(.githooks/pre-push)
     — the same lockstep the CI `sha256sum -c` step enforces (fails the moment
     the hook is edited without re-pinning).
  2. publish.py's read-only `check_pre_push_hook_integrity` ABORTS (returns
     ok=False) on a MUTATED hook copy — driven against a tmp_path repo copy,
     never the real repo, and never rewriting anything.
  3. The same helper PASSES on a faithful (hook + pin) copy and FAILS when the
     pin is missing — proving a removed pin is itself caught.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REAL_HOOK = PLUGIN_ROOT / ".githooks" / "pre-push"
REAL_PIN = PLUGIN_ROOT / ".githooks" / "pre-push.sha256"

# Import publish.py's read-only integrity helper directly (the same code the
# publish gate runs). scripts/ is added to sys.path the way publish.py itself
# bootstraps its sibling module.
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
from publish import check_pre_push_hook_integrity  # noqa: E402


def _digest(path: Path) -> str:
    """sha256 hex digest of a file's bytes (binary read — no newline munging)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pinned_digest(pin: Path) -> str:
    """First whitespace-delimited token of a `sha256sum`-format pin file."""
    tokens = pin.read_text(encoding="utf-8").strip().split()
    return tokens[0] if tokens else ""


# ── 1. The committed pin matches the committed hook (the CI lockstep). ──


def test_pin_file_exists() -> None:
    """.githooks/pre-push and its .sha256 pin both exist in the repo."""
    assert REAL_HOOK.is_file(), f"{REAL_HOOK} must exist"
    assert REAL_PIN.is_file(), f"{REAL_PIN} must exist (the hook must be pinned)"


def test_pin_matches_hook() -> None:
    """The pinned digest equals sha256(.githooks/pre-push) — CI's `sha256sum -c`.

    Fails the instant someone edits the hook without re-pinning, which is the
    whole point: the desync is visible locally (here + the publish gate) before
    CI even runs.
    """
    assert _pinned_digest(REAL_PIN) == _digest(REAL_HOOK)


# ── 2/3. publish.py's read-only assert: PASS on a faithful copy, ABORT on a
#    mutated hook or a missing pin. Driven on tmp_path copies — never the real
#    repo, and the helper never writes anything. ──


def _make_repo_copy(tmp_path: Path, *, with_pin: bool = True) -> Path:
    """A throwaway repo root holding a copy of the hook (+ optionally its pin)."""
    root = tmp_path / "repo"
    (root / ".githooks").mkdir(parents=True)
    shutil.copy2(REAL_HOOK, root / ".githooks" / "pre-push")
    if with_pin:
        shutil.copy2(REAL_PIN, root / ".githooks" / "pre-push.sha256")
    return root


def test_integrity_passes_on_faithful_copy(tmp_path: Path) -> None:
    """check_pre_push_hook_integrity → ok on an unmodified hook+pin copy."""
    root = _make_repo_copy(tmp_path)
    ok, detail = check_pre_push_hook_integrity(root)
    assert ok, detail


def test_integrity_aborts_on_mutated_hook(tmp_path: Path) -> None:
    """A MUTATED hook copy → ok=False with the re-pin guidance message.

    Mutating the copy (appending a comment) changes its sha256; the pin still
    holds the original digest, so the helper must refuse — exactly the
    silent-weakening scenario the pin defends against.
    """
    root = _make_repo_copy(tmp_path)
    hook = root / ".githooks" / "pre-push"
    hook.write_text(hook.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
    ok, detail = check_pre_push_hook_integrity(root)
    assert not ok
    assert "pin wasn't updated" in detail


def test_integrity_aborts_on_missing_pin(tmp_path: Path) -> None:
    """A hook with NO pin file → ok=False (a removed pin is itself a regression)."""
    root = _make_repo_copy(tmp_path, with_pin=False)
    ok, detail = check_pre_push_hook_integrity(root)
    assert not ok
    assert "missing" in detail
