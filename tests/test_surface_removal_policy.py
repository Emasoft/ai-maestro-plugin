"""Removals of agent-facing surfaces need a tombstone + a MAJOR bump (ai-maestro#118).

Other plugins cite this plugin's skills/commands/scripts BY NAME IN PROSE, so a
removal breaks dependents even though nothing imports anything — and the break is
silent: a dangling citation is just prose that stopped being true. Two removals
already shipped as MINOR bumps this way. The README's "Versioning and removal
policy" section states the rule; this test makes it enforceable at publish time:

  - a surface present in the latest release tag and absent from HEAD is legal ONLY
    if the tag's copy was already a TOMBSTONE stub (the surface spent >= 1 release
    telling readers where it went), and
  - any non-tombstone removal additionally requires the MAJOR version to have moved.

Non-vacuity (the MANAGER's caveat on ai-maestro#118): the failure mode of this
kind of test is passing on an empty needle, so it asserts the tag actually
yielded surfaces before asserting anything about their removal. Everything runs
on LOCAL git (tags + object store) — no network — so it cannot be starved into
an always-skip in the publish pipeline, which runs from the full clone that
creates the tags in the first place.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(PLUGIN_ROOT), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _latest_release_tag() -> str | None:
    tags = [t for t in _git("tag", "--list", "v*").split() if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
    if not tags:
        return None
    return max(tags, key=lambda t: tuple(int(x) for x in t[1:].split(".")))


def _surfaces(tree: str) -> set[str]:
    """Agent-facing surfaces at a git tree: skills/<name>, commands/<name>, scripts/<name>."""
    out = _git("ls-tree", "-r", "--name-only", tree)
    surfaces: set[str] = set()
    for line in out.splitlines():
        m = re.match(r"^(skills/[^/]+)/SKILL\.md$", line)
        if m:
            surfaces.add(m.group(1))
            continue
        if re.match(r"^commands/[^/]+\.md$", line) or re.match(r"^scripts/[^/]+\.(sh|py)$", line):
            surfaces.add(line)
    return surfaces


def _tag_blob(tag: str, path: str) -> str:
    return _git("show", f"{tag}:{path}")


def test_removed_surfaces_were_tombstoned_and_major_bumped() -> None:
    """Every surface removed since the last release tag was a TOMBSTONE there, or the MAJOR moved."""
    tag = _latest_release_tag()
    if tag is None:
        pytest.skip("no vX.Y.Z release tag visible — publish pipeline always has them")

    tagged = _surfaces(tag)
    assert tagged, f"non-vacuity: {tag} yielded zero surfaces — the extractor rotted"
    current = _surfaces("HEAD")
    assert current, "non-vacuity: HEAD yielded zero surfaces — the extractor rotted"

    removed = sorted(tagged - current)
    if not removed:
        return  # nothing removed since the last release — the common, green case

    version = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]
    tag_major = int(tag[1:].split(".")[0])
    head_major = int(version.split(".")[0])

    hard_removals: list[str] = []
    for surface in removed:
        blob_path = f"{surface}/SKILL.md" if surface.startswith("skills/") else surface
        body = _tag_blob(tag, blob_path)
        # A stub whose body opens with TOMBSTONE spent its release telling
        # readers where the surface went; dropping it now is the policy working.
        if not body.lstrip().startswith("TOMBSTONE"):
            hard_removals.append(surface)

    assert not hard_removals or head_major > tag_major, (
        f"surfaces removed since {tag} without a tombstone release AND without a "
        f"MAJOR bump (version {version}): {hard_removals} — per README 'Versioning "
        f"and removal policy', ship a TOMBSTONE stub for one release, then remove "
        f"under a MAJOR whose CHANGELOG names it"
    )
    assert not hard_removals, (
        f"surfaces removed since {tag} whose {tag} copy was not a TOMBSTONE stub: "
        f"{hard_removals} — even under a MAJOR, each removal ships a one-release "
        f"tombstone naming its successor first (README 'Versioning and removal policy')"
    )


def test_current_tombstones_are_well_formed() -> None:
    """A TOMBSTONE stub must name a successor or state there is none — a bare marker helps nobody."""
    stubs = [
        p
        for p in PLUGIN_ROOT.glob("skills/*/SKILL.md")
        if p.read_text(encoding="utf-8").lstrip().startswith("TOMBSTONE")
    ]
    for stub in stubs:
        body = stub.read_text(encoding="utf-8")
        assert re.search(r"successor|replaced by|no replacement", body, re.IGNORECASE), (
            f"{stub.relative_to(PLUGIN_ROOT)} is a TOMBSTONE with no successor line"
        )
