"""Tests for install-governance-rules.cjs (issue #16 — safe refresh semantics).

The SessionStart hook installs the four bundled governance rules into
~/.claude/rules/ and, per #16, refreshes them on a version bump WITHOUT clobbering
a copy the user has customized. Exactly as it runs in production, these tests
drive it as a real Node subprocess (no mocks) against a throwaway HOME and a
throwaway bundled-rules dir, so every case — fresh install, no-op, safe refresh,
and preserve-user-edit — is exercised end-to-end.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = PLUGIN_ROOT / "scripts" / "install-governance-rules.cjs"
RULE_NAMES = [
    "trdd-design-tasks.md",
    "trdd-approval-tiers.md",
    "prrd-design-rules.md",
    "manager-approval-defaults.md",
]

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None,
    reason="node is required to exercise the installer (no mock substitute)",
)


@pytest.fixture()
def sandbox(tmp_path: Path):
    """A self-contained (scripts/, rules/, home/) tree so srcDir = <copy>/../rules
    and HOME = home. Returns (run, rules_dir, dest_dir)."""
    scripts = tmp_path / "scripts"
    rules = tmp_path / "rules"
    home = tmp_path / "home"
    scripts.mkdir()
    rules.mkdir()
    home.mkdir()
    shutil.copy(INSTALLER, scripts / INSTALLER.name)
    for name in RULE_NAMES:
        (rules / name).write_text(f"v1 {name}\n")
    dest = home / ".claude" / "rules"

    def run() -> str:
        proc = subprocess.run(
            ["node", str(scripts / INSTALLER.name)],
            capture_output=True,
            text=True,
            env={"HOME": str(home), "PATH": __import__("os").environ.get("PATH", "")},
            timeout=30,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        return proc.stdout

    return run, rules, dest


def test_fresh_install(sandbox) -> None:
    """First run installs all four rules and writes the stamp file."""
    run, _, dest = sandbox
    out = run()
    assert "installed 4" in out
    for name in RULE_NAMES:
        assert (dest / name).read_text() == f"v1 {name}\n"
    assert (dest / ".ai-maestro-governance-stamps.json").exists()


def test_rerun_same_version_is_silent_noop(sandbox) -> None:
    """A second run with no version change emits nothing and changes nothing."""
    run, _, _ = sandbox
    run()
    assert run().strip() == ""


def test_version_bump_refreshes_unmodified_copy(sandbox) -> None:
    """A changed bundled rule refreshes an on-disk copy the user has NOT touched."""
    run, rules, dest = sandbox
    run()
    (rules / "trdd-design-tasks.md").write_text("v2 trdd-design-tasks.md\n")
    out = run()
    assert "refreshed 1" in out
    assert (dest / "trdd-design-tasks.md").read_text() == "v2 trdd-design-tasks.md\n"


def test_user_modified_copy_is_preserved_on_bump(sandbox) -> None:
    """The #8 invariant: a user-customized rule is NEVER clobbered, even when the
    bundled version changes."""
    run, rules, dest = sandbox
    run()
    (dest / "prrd-design-rules.md").write_text("USER EDIT\n")
    (rules / "prrd-design-rules.md").write_text("v2 prrd-design-rules.md\n")
    out = run()
    assert "prrd-design-rules.md" not in out  # not refreshed
    assert (dest / "prrd-design-rules.md").read_text() == "USER EDIT\n"  # preserved


def test_stamp_records_installed_hashes(sandbox) -> None:
    """The stamp file records a hash per installed rule so future bumps can tell
    an unmodified copy from a customized one."""
    run, _, dest = sandbox
    run()
    stamps = json.loads((dest / ".ai-maestro-governance-stamps.json").read_text())
    assert set(stamps.keys()) == set(RULE_NAMES)
    assert all(isinstance(v, str) and len(v) == 64 for v in stamps.values())  # sha256 hex
