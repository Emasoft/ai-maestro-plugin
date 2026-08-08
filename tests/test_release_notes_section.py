#!/usr/bin/env python3
"""A release ships ITS OWN changelog section, not the whole file.

Step 9 used to run `git-cliff --bump --unreleased -o CHANGELOG.md`, and with
`--unreleased` that writes only the current range — so the redirect OVERWROTE
the file and every release destroyed its predecessor's section. CHANGELOG.md
had carried exactly one version for its entire history while its own first line
promised "All notable changes to this project will be documented in this file."

It survived because step 11 passed that same one-section file to
`gh release create --notes-file`, so the file and the notes were the same thing
BY ACCIDENT. Switching step 9 to `--prepend` breaks that coupling: the file
becomes cumulative, and passing it whole would publish the entire project
history as every release's notes. The two changes are one change, and these
tests pin the half that is easy to forget.

Real files in tmp_path, no mocks — the function reads from disk, so a
substituted reader would test something else.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

CUMULATIVE = """\
# Changelog

All notable changes to this project will be documented in this file.

## [3.2.0] — 2026-08-09

### Features

- The newest thing

## [3.1.3] — 2026-08-08

### Bug Fixes

- An older thing

## [3.1.2] — 2026-08-08

### Bug Fixes

- An even older thing
"""


def _write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "CHANGELOG.md"
    p.write_text(text)
    return p


def test_extracts_only_the_newest_section(tmp_path: Path) -> None:
    """The newest version's section, and nothing below it."""
    got = publish._changelog_section(_write(tmp_path, CUMULATIVE), "3.2.0")
    assert got is not None
    assert "The newest thing" in got
    assert "An older thing" not in got, "leaked the previous release into these notes"
    assert "3.1.3" not in got


def test_a_version_that_is_not_the_newest_returns_none(tmp_path: Path) -> None:
    """Guards the prepend invariant rather than being permissive.

    Step 9 prepends, so the version being released is ALWAYS the first section.
    Finding a different heading first means the file is not the shape this code
    assumes — a parse failure, which the caller must be able to distinguish from
    "found it, it was empty". Silently scanning on would publish some OTHER
    release's notes under this tag, which is worse than shipping too much.
    """
    assert publish._changelog_section(_write(tmp_path, CUMULATIVE), "3.1.3") is None


def test_a_missing_version_returns_none_not_empty(tmp_path: Path) -> None:
    """None means "could not isolate" so the caller can fall back loudly.

    An empty string would publish a release with NO notes and no warning — the
    record lost silently. The caller ships the whole CHANGELOG on None instead:
    too many notes is editable after the fact, none is not.
    """
    assert publish._changelog_section(_write(tmp_path, CUMULATIVE), "9.9.9") is None


def test_an_unreadable_changelog_returns_none(tmp_path: Path) -> None:
    """A directory where a file was expected must not raise mid-release."""
    (tmp_path / "CHANGELOG.md").mkdir()
    assert publish._changelog_section(tmp_path / "CHANGELOG.md", "3.2.0") is None


def test_bare_mentions_in_the_notes_abort_the_publish() -> None:
    """A release body that would PAGE someone must stop the pipeline.

    The body is built from commit subjects, and a commit subject is written long
    before anyone thinks about GitHub notifications. `@name` there flows commit ->
    changelog -> --notes-file -> a published release that pings a real account,
    and redaction is not undo: the notification is already delivered.
    """
    import pytest as _pytest

    with _pytest.raises(SystemExit):
        publish._refuse_bare_mentions("- thanks @someone for the report", "v1.2.3")


def test_inert_at_shapes_do_not_abort_the_publish() -> None:
    """The forms `gh api markdown` proves do NOT notify must pass.

    A gate that reddens on `actions/checkout@v4` in a commit subject gets deleted
    within a week, and then nothing checks the shape that does page.
    """
    safe = "- bump actions/checkout@v4 and @types/node; contact user@example.com"
    publish._refuse_bare_mentions(safe, "v1.2.3")  # must not raise


def test_the_real_changelog_yields_the_current_version() -> None:
    """Against the shipped file at the shipped version — the end-to-end case.

    Falsify by reverting step 9 to `-o CHANGELOG.md`: this stays green (one
    section is trivially the newest), which is exactly why the prepend itself
    is pinned by the step-9 docstring and by the cumulative fixture above
    rather than by this test alone.
    """
    version = publish.get_current_version(ROOT)
    assert version, "could not read the plugin version"
    got = publish._changelog_section(ROOT / "CHANGELOG.md", version)
    assert got is not None, f"CHANGELOG.md has no `## [{version}]` heading"
    assert got.startswith(f"## [{version}]")
