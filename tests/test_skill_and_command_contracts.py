"""Structural contracts every skill and command must satisfy.

Real tests only (no mocks): each assertion reads the shipped files and checks an
invariant that has ALREADY been violated in this repo at least once. They are
written as corpus-wide sweeps rather than one file per skill because the failures
they catch are *class* failures — a convention drifting across 28 skills — and a
per-skill stub would not have caught any of them.

Provenance of each contract, so nobody "simplifies" one away as boilerplate:

- name/dir agreement + parseable frontmatter — the cheapest possible guard; a
  skill whose `name:` disagrees with its directory is silently unaddressable.
- the `/name` promise (D2, TRDD-546UDAZF) — 13 skills advertised "Trigger with
  /<name>" while declaring `user-invocable: false` with no `commands/<name>.md`.
  Typing the promised command did nothing; the description was lying to the user.
- README table vs disk, BOTH directions — the table had drifted both ways at
  once: 2 phantom rows for deleted skills AND 3 shipped skills missing entirely.
  A one-directional check would have caught neither half.
- allowed-tools covers the script the skill teaches (core#51) — `allowed-tools`
  gates Bash per binary, so a skill that instructs an agent to run a script it
  does not list is permission-blocked in a way that surfaces as "the tool is
  missing" rather than "the skill forgot to allow it".
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = PLUGIN_ROOT / "skills"
COMMANDS_DIR = PLUGIN_ROOT / "commands"

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.S)


def _frontmatter(path: Path) -> dict:
    """Parse a markdown file's YAML frontmatter, or fail the calling test."""
    m = _FRONTMATTER.match(path.read_text())
    assert m, f"{path.relative_to(PLUGIN_ROOT)} has no YAML frontmatter block"
    data = yaml.safe_load(m.group(1))
    assert isinstance(data, dict), f"{path.relative_to(PLUGIN_ROOT)} frontmatter is not a mapping"
    return data


def _skill_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def _command_files() -> list[Path]:
    return sorted(COMMANDS_DIR.glob("*.md"))


def test_the_corpus_is_not_empty() -> None:
    """Guard the sweeps below: an empty glob would make every one vacuously pass."""
    # Without this, deleting skills/ entirely would turn this file green.
    assert len(_skill_files()) >= 20, "skills/ looks empty or unreadable"
    assert len(_command_files()) >= 10, "commands/ looks empty or unreadable"


@pytest.mark.parametrize("skill", _skill_files(), ids=lambda p: p.parent.name)
def test_skill_frontmatter_is_valid(skill: Path) -> None:
    """Every SKILL.md parses and its `name:` matches its directory name."""
    fm = _frontmatter(skill)
    assert fm.get("name"), f"{skill.parent.name}: missing `name:`"
    assert fm["name"] == skill.parent.name, (
        f"{skill.parent.name}: `name: {fm['name']}` disagrees with its directory"
    )
    assert str(fm.get("description", "")).strip(), f"{skill.parent.name}: empty `description:`"


@pytest.mark.parametrize("command", _command_files(), ids=lambda p: p.stem)
def test_command_frontmatter_is_valid(command: Path) -> None:
    """Every command wrapper parses and its `name:` matches its filename."""
    fm = _frontmatter(command)
    assert fm.get("name") == command.stem, (
        f"{command.name}: `name: {fm.get('name')}` disagrees with its filename"
    )
    assert str(fm.get("description", "")).strip(), f"{command.name}: empty `description:`"


@pytest.mark.parametrize("skill", _skill_files(), ids=lambda p: p.parent.name)
def test_skill_does_not_promise_a_slash_command_it_lacks(skill: Path) -> None:
    """A description may only advertise `/<name>` if that surface really exists.

    D2: `user-invocable: false` means "not in the slash-command palette", so the
    promise is only true when a `commands/<name>.md` wrapper backs it.

    THE DEFAULT IS TRUE, and getting that wrong inverts this test. An ABSENT
    `user-invocable` means the skill IS invocable as `/<name>` — per the spec, and
    as CPV implements it (`validate_skill_comprehensive.py`:
    `is_user_invocable = frontmatter.get("user-invocable", True)  # default True
    per spec`). An earlier draft of this test treated absent as NOT invocable and
    flagged 10 skills whose promises were perfectly truthful; "fixing" those would
    have stripped accurate trigger information out of 10 working skills. Only an
    EXPLICIT `false` opts out.
    """
    fm = _frontmatter(skill)
    name = skill.parent.name
    promises = f"/{name}" in str(fm.get("description", ""))
    user_invocable = bool(fm.get("user-invocable", True))
    has_wrapper = (COMMANDS_DIR / f"{name}.md").exists()
    assert not (promises and not user_invocable and not has_wrapper), (
        f"{name}: description promises `/{name}` but user-invocable is false and "
        f"commands/{name}.md does not exist — typing it would do nothing"
    )


def test_readme_skills_table_matches_disk_exactly() -> None:
    """The README skills table and skills/ agree in BOTH directions.

    Phantom rows advertise capabilities that no longer ship; missing rows hide
    ones that do. This repo has had both at the same time.
    """
    readme = (PLUGIN_ROOT / "README.md").read_text().splitlines()
    start = next(i for i, ln in enumerate(readme) if ln.startswith("## Skills"))
    rows: set[str] = set()
    for line in readme[start + 1 :]:
        if line.startswith("## "):
            break
        m = re.match(r"^\|\s*`([^`]+)`", line)
        if m:
            rows.add(m.group(1))
    on_disk = {p.parent.name for p in _skill_files()}
    assert rows == on_disk, (
        f"README skills table drifted from disk.\n"
        f"  phantom rows (in README, not on disk): {sorted(rows - on_disk)}\n"
        f"  missing rows (on disk, not in README): {sorted(on_disk - rows)}"
    )


# Skills that TEACH a frozen ai-maestro CLI must be ALLOWED to run it. Keyed on
# the script each skill is the wrapper for, so a new ama-* wrapper that forgets
# its allowed-tools entry fails here instead of at an agent's first invocation.
FROZEN_CLI_WRAPPERS = {
    "ama-session": "aimaestro-session.sh",
    "ama-unblock": "aimaestro-session.sh",
    "ama-panel": "aimaestro-panel.sh",
    "ama-continuity": "aimaestro-continuity.sh",
    "ama-portfolio": "aimaestro-portfolio.sh",
    "ama-settings": "aimaestro-settings.sh",
    "ama-statusline": "aimaestro-statusline.sh",
}


@pytest.mark.parametrize(("skill_name", "script"), sorted(FROZEN_CLI_WRAPPERS.items()))
def test_frozen_cli_wrapper_allows_the_script_it_teaches(skill_name: str, script: str) -> None:
    """`allowed-tools` gates Bash per binary — a wrapper must allow its own CLI."""
    skill = SKILLS_DIR / skill_name / "SKILL.md"
    assert skill.is_file(), f"{skill_name}: SKILL.md missing"
    fm = _frontmatter(skill)
    allowed = str(fm.get("allowed-tools", ""))
    assert f"Bash({script}" in allowed, (
        f"{skill_name}: teaches `{script}` but allowed-tools does not permit it — "
        f"an agent following this skill is permission-blocked, which reads as "
        f"'the tool is missing'. allowed-tools was: {allowed!r}"
    )
    assert script in skill.read_text(), f"{skill_name}: allows `{script}` but never teaches it"
