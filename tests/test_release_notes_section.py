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

import inspect
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

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


def _seeded_repo(tmp_path: Path) -> Path:
    """A real git repo with one released section already in CHANGELOG.md."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git = ["git", "-C", str(repo)]
    subprocess.run([*git[:1], "init", "-q", str(repo)], check=True)
    subprocess.run([*git, "config", "user.email", "t@example.com"], check=True)
    subprocess.run([*git, "config", "user.name", "T"], check=True)
    shutil.copy(ROOT / "cliff.toml", repo / "cliff.toml")
    (repo / "a.txt").write_text("one\n")
    subprocess.run([*git, "add", "a.txt", "cliff.toml"], check=True)
    subprocess.run([*git, "commit", "-qm", "feat: the older thing"], check=True)
    subprocess.run([*git, "tag", "v0.1.0"], check=True)
    (repo / "CHANGELOG.md").write_text(
        "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        "## [0.1.0] — 2026-01-01\n\n### Features\n\n- the older thing\n"
    )
    (repo / "a.txt").write_text("two\n")
    subprocess.run([*git, "add", "a.txt"], check=True)
    subprocess.run([*git, "commit", "-qm", "fix: the newer thing"], check=True)
    return repo


@pytest.mark.skipif(shutil.which("git-cliff") is None, reason="git-cliff not installed")
def test_step_9_preserves_the_previous_release_section(tmp_path: Path) -> None:
    """Releasing v0.2.0 into a repo that already shipped v0.1.0 keeps BOTH sections.

    Runs the shipped `stage_changelog` against a real git repo and the real
    git-cliff — no mocks, because the defect lived entirely in which flag was
    handed to that binary, and a substituted runner would happily "pass" with
    the destructive flag still in the source.

    Falsification (measured): swap `--prepend CHANGELOG.md` for `-o CHANGELOG.md`
    in step 9 and the `0.1.0` assertion below fails — the older section is gone,
    which is what every release in this repo's history silently did.
    """
    repo = _seeded_repo(tmp_path)
    publish.stage_changelog(repo, "0.2.0", dry_run=False)
    text = (repo / "CHANGELOG.md").read_text()
    assert "## [0.2.0]" in text, "the new section was not written"
    assert "## [0.1.0]" in text, "PREVIOUS section destroyed — step 9 is overwriting again"
    assert text.index("## [0.2.0]") < text.index("## [0.1.0]"), "newest section must come first"


def test_step_9_never_redirects_over_an_existing_changelog() -> None:
    """The `-o CHANGELOG.md` form may appear ONLY on the file-does-not-exist path.

    A source-level guard, deliberately, and it is not redundant with the
    behavioural test above: the fix for this defect lives in CPV's canonical
    emitter, and this repo's publish.py is DRIFTED from that scaffold
    (RC-PIPELINE-DRIFT-001), so a future re-sync can silently reintroduce the
    upstream shape. Nothing outside this repo can catch that.
    """
    src = inspect.getsource(publish.stage_changelog)
    assert '"--prepend", "CHANGELOG.md"' in src, "step 9 no longer prepends"
    assert src.count('"-o", "CHANGELOG.md"') == 1, "a second redirect appeared in step 9"
    guard = src.index("if changelog.is_file():")
    assert guard < src.index('"--prepend"'), "the prepend must sit under the is_file() guard"
    assert guard < src.index('"-o"'), "the redirect must sit in the else branch"
