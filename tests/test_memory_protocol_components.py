"""Tests for the memgrep memory-hosting components this plugin ships.

Real tests only (no mocks, per this project's no-mock rule):

- `scripts/install-memgrep.sh` is exercised as a real subprocess. The
  network-download path is NOT tested here (it would race the very release
  that publishes the assets — see release.yml `build-memgrep`); instead we
  test the deterministic paths: idempotency when a memgrep binary is on
  PATH, argument validation, and bash syntax.
- The vendored crate (`scripts/memgrep/`) is verified structurally — files
  exist, the release workflow attaches checksummed binaries.
- The memgrep crate's own behavior is covered by its bundled Rust suite
  (`cargo test --manifest-path scripts/memgrep/Cargo.toml`, run by CI's
  test-memgrep job), not duplicated here.

Note: the curated-note memory protocol itself (recall/write/update) was
retired from this plugin in favor of the janitor's GLOBAL wiki-memory skills
(`/janitor-memory-{recall,write,update}`); this plugin now only HOSTS the
memgrep engine those skills depend on. The transcript-search skill
(`memory-search`) stays and points at the global skills as its complement.
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = PLUGIN_ROOT / "scripts" / "install-memgrep.sh"


def _run(
    *args: str, env_overrides: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Run install-memgrep.sh with optional env overrides, capturing output."""
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        ["bash", str(INSTALL_SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
        check=False,
    )


class TestInstallScript:
    """install-memgrep.sh deterministic paths — syntax, idempotency, arg guard."""

    def test_script_exists_and_is_executable(self) -> None:
        """The installer ships with the plugin and carries the exec bit."""
        assert INSTALL_SCRIPT.is_file()
        assert INSTALL_SCRIPT.stat().st_mode & stat.S_IXUSR

    def test_bash_syntax_is_valid(self) -> None:
        """bash -n parses the installer without errors."""
        proc = subprocess.run(
            ["bash", "-n", str(INSTALL_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr

    def test_idempotent_when_memgrep_on_path(self, tmp_path: Path) -> None:
        """A memgrep already on PATH short-circuits the installer with exit 0."""
        # A REAL executable on PATH (not a mock of the script under test):
        # the script's `command -v memgrep` check must find this and exit 0
        # without attempting any download or build.
        fake_bin = tmp_path / "memgrep"
        fake_bin.write_text("#!/bin/sh\necho 'memgrep 0.0-test'\n")
        fake_bin.chmod(0o755)
        proc = _run(env_overrides={"PATH": f"{tmp_path}:{os.environ['PATH']}"})
        assert proc.returncode == 0, proc.stderr
        assert "already installed" in proc.stdout

    def test_unknown_argument_is_rejected(self) -> None:
        """An unrecognized flag fails fast with exit 2 (fail-fast contract)."""
        proc = _run("--definitely-not-a-flag")
        assert proc.returncode == 2
        assert "unknown argument" in proc.stderr

    def test_version_flag_requires_value(self) -> None:
        """--version with no tag argument exits non-zero instead of proceeding."""
        proc = _run("--version")
        assert proc.returncode != 0


class TestCanonicalArtifacts:
    """The memgrep memory-hosting artifacts this plugin ships for the ecosystem."""

    def test_memgrep_crate_is_vendored_complete(self) -> None:
        """scripts/memgrep ships Cargo.toml + Cargo.lock + sources + its own tests."""
        crate = PLUGIN_ROOT / "scripts" / "memgrep"
        assert (crate / "Cargo.toml").is_file()
        assert (crate / "Cargo.lock").is_file()  # --locked builds need it
        assert (crate / "SKILL.md").is_file()
        assert (crate / "src" / "main.rs").is_file()
        assert (crate / "tests" / "cli.rs").is_file()

    def test_memory_search_disambiguates_from_global_wiki_recall(self) -> None:
        """memory-search points at the janitor GLOBAL wiki-memory skills as its complement."""
        text = (PLUGIN_ROOT / "skills" / "memory-search" / "SKILL.md").read_text()
        assert "/janitor-memory-recall" in text
        assert "/janitor-memory-write" in text

    def test_release_workflow_builds_checksummed_binaries(self) -> None:
        """release.yml has the build-memgrep matrix attaching tarball + sha256 per platform."""
        wf = (PLUGIN_ROOT / ".github" / "workflows" / "release.yml").read_text()
        assert "build-memgrep:" in wf
        for platform in ("darwin-arm64", "darwin-x64", "linux-x64"):
            assert platform in wf
        assert ".sha256" in wf
