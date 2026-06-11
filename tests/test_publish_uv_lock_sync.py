"""Tests for the uv.lock editable-self-entry sync in scripts/publish.py.

publish.py bumps plugin.json, pyproject.toml, and the per-script ``__version__``
vars — but uv.lock also carries an editable entry for THIS package
(``source = { editable = "." }``) whose ``version`` mirrors pyproject's
``[project].version``. Before this sync existed, every bump left uv.lock one
version behind, which surfaced as a dirty tree on the next ``uv`` call and
forced a manual follow-up commit. These tests pin the two functions that close
that gap:

  * ``update_uv_lock`` — surgically rewrites ONLY the editable self-entry's
    version line (deterministic, offline, no dependency re-resolution).
  * ``check_version_consistency`` — now also reads the editable self-entry so a
    stale lock is caught at the version-consistency gate.

No mocks: every test runs the real functions against real uv.lock text written
to a tmp dir, exactly as the publish gate runs them.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make scripts/ importable without installing the plugin as a package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import publish  # noqa: E402  (sys.path mutation above is intentional)

# A minimal but realistic uv.lock: an editable self-entry followed by a normal
# registry dependency that shares NO version string, so we can prove the sync
# touches only the self-entry.
_LOCK_WITH_EDITABLE = """\
version = 1
revision = 3
requires-python = ">=3.12"

[[package]]
name = "ai-maestro-plugin"
version = "2.7.1"
source = { editable = "." }

[package.optional-dependencies]
dev = [
    { name = "pytest" },
]

[[package]]
name = "pytest"
version = "8.4.0"
source = { registry = "https://pypi.org/simple" }
"""

_LOCK_NO_EDITABLE = """\
version = 1

[[package]]
name = "pytest"
version = "8.4.0"
source = { registry = "https://pypi.org/simple" }
"""


def _write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


class TestUpdateUvLock:
    """update_uv_lock rewrites only the editable self-entry version, offline."""

    def test_bumps_only_the_editable_self_entry(self, tmp_path: Path) -> None:
        """A bump rewrites the editable self-entry and leaves dependencies untouched."""
        _write(tmp_path, "uv.lock", _LOCK_WITH_EDITABLE)
        changed, msg = publish.update_uv_lock(tmp_path, "2.8.0")
        assert changed is True
        assert "2.8.0" in msg
        new = (tmp_path / "uv.lock").read_text(encoding="utf-8")
        # Exactly one line now reads 2.8.0 — the self-entry, never the pytest dep.
        assert new.count('version = "2.8.0"') == 1
        assert 'version = "8.4.0"' in new  # the dependency version is preserved
        # And the changed line is the one immediately above the editable marker.
        match = publish._UV_LOCK_EDITABLE_VERSION_VALUE_RE.search(new)
        assert match is not None and match.group(1) == "2.8.0"

    def test_missing_uv_lock_is_noop_success(self, tmp_path: Path) -> None:
        """A plugin that ships no uv.lock is a no-op success, never a failure."""
        changed, msg = publish.update_uv_lock(tmp_path, "9.9.9")
        assert changed is True
        assert "not present" in msg
        assert not (tmp_path / "uv.lock").exists()

    def test_lock_without_editable_self_entry_is_noop_success(self, tmp_path: Path) -> None:
        """A lock with only registry deps (no editable self-entry) is skipped cleanly."""
        _write(tmp_path, "uv.lock", _LOCK_NO_EDITABLE)
        before = (tmp_path / "uv.lock").read_text(encoding="utf-8")
        changed, msg = publish.update_uv_lock(tmp_path, "9.9.9")
        assert changed is True
        assert "no editable self-entry" in msg
        # The file is untouched.
        assert (tmp_path / "uv.lock").read_text(encoding="utf-8") == before

    def test_idempotent_when_already_at_target(self, tmp_path: Path) -> None:
        """Re-running at the same version reports 'already at' and rewrites nothing new."""
        _write(tmp_path, "uv.lock", _LOCK_WITH_EDITABLE)
        publish.update_uv_lock(tmp_path, "2.8.0")
        first = (tmp_path / "uv.lock").read_text(encoding="utf-8")
        changed, msg = publish.update_uv_lock(tmp_path, "2.8.0")
        assert changed is True
        assert "already at 2.8.0" in msg
        assert (tmp_path / "uv.lock").read_text(encoding="utf-8") == first


class TestConsistencyChecksUvLock:
    """check_version_consistency now folds the editable self-entry into the gate."""

    def _scaffold(self, tmp_path: Path, plugin_ver: str, pyproject_ver: str, lock_ver: str) -> None:
        (tmp_path / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        (tmp_path / ".claude-plugin" / "plugin.json").write_text(
            '{"name": "ai-maestro-plugin", "version": "%s"}\n' % plugin_ver, encoding="utf-8"
        )
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "ai-maestro-plugin"\nversion = "%s"\n' % pyproject_ver, encoding="utf-8"
        )
        (tmp_path / "uv.lock").write_text(
            _LOCK_WITH_EDITABLE.replace('version = "2.7.1"', 'version = "%s"' % lock_ver, 1),
            encoding="utf-8",
        )

    def test_all_sources_aligned_passes(self, tmp_path: Path) -> None:
        """When plugin.json, pyproject, and uv.lock agree, the consistency gate passes."""
        self._scaffold(tmp_path, "3.0.0", "3.0.0", "3.0.0")
        ok, msg = publish.check_version_consistency(tmp_path)
        assert ok is True
        assert "3.0.0" in msg

    def test_stale_uv_lock_is_detected(self, tmp_path: Path) -> None:
        """A bumped pyproject/plugin.json with an un-synced uv.lock is flagged by name."""
        self._scaffold(tmp_path, "3.0.0", "3.0.0", "2.9.9")
        ok, msg = publish.check_version_consistency(tmp_path)
        assert ok is False
        assert "uv.lock:editable=2.9.9" in msg
