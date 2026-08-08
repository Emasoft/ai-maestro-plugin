#!/usr/bin/env python3
"""The bundled governance mirror must carry a checkable pointer, and someone must have looked.

WHAT WENT WRONG. The mirror sat at catalog v5.2.0 for three days carrying NO R42.8
at all, while the deployed `aimaestro-session.sh help` printed "Cross-agent limits
(R42 / R42.8)". Five parties reconciled real enforcement against a document that
never mentioned the rule and concluded it was unratified. Separately, three CORE
surfaces taught an R29.1 miscount the USER had deleted 25 days earlier. Nothing
flagged either one, because nothing this repo shipped ever declared a version that
could be checked against reality.

WHAT THIS DOES NOT DO — and the omission is the design, not a shortcut. It never
fetches. A network-fetching test collapses "stale" and "offline" into one red, and
two states with opposite correct responses sharing one signal is how a gate earns
the reputation that gets it switched off. So this asserts the POINTER, never the
VALUE:

  * the stamp exists and is well-formed        (structure)
  * the banner and the frontmatter agree       (catches a hand-edit of one half)
  * `synced-at` is not older than MAX_AGE_DAYS (catches "nobody has looked")

Only the third could have caught either incident, and it makes an honest claim: it
measures OUR diligence, never upstream's state. It CANNOT tell you the mirror is
current — only that nobody has checked recently, which is exactly the defect that
bit. The failure message says so, because a reader who mistakes this for a currency
check has a well-falsified guard defending a premise it never tested.

WHY THE BLOB AND NOT THE COMMIT. `3P-VER-05` of `design/specs/3-pillars-spec.md`
FORBIDS the branch commit sha as a change signal: it moves on every unrelated
commit, so a consumer polls, sees movement, refetches, gets a byte-identical
document, and records "checked, current" — manufacturing confidence. Measured
upstream: the tip moved across four unrelated commits while the spec blob sat
unchanged for 13 days. A blob sha changes iff those bytes change.

Design credit: the pointer-not-value split and the staleness arm are the
ai-maestro-autonomous-agent session's, adopted after it found a 25-day miss in its
own tree using them.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pytest
import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MIRROR = PLUGIN_ROOT / "skills" / "team-governance" / "references" / "GOVERNANCE-RULES.md"

# Generous on purpose. The fix must be cheaper than the bypass, or this becomes
# the gate everyone learns to bump without looking — which is worse than no gate,
# because then the stamp lies with a green check on it. 30 days still catches the
# 25-day R29.1 class and never fires on an ordinary working week.
MAX_AGE_DAYS = 30

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.S)


@pytest.fixture(scope="module")
def mirror_text() -> str:
    assert MIRROR.is_file(), f"{MIRROR.relative_to(PLUGIN_ROOT)} is missing"
    return MIRROR.read_text()


@pytest.fixture(scope="module")
def frontmatter(mirror_text: str) -> dict:
    m = _FRONTMATTER.match(mirror_text)
    assert m, "the mirror has no YAML frontmatter block"
    data = yaml.safe_load(m.group(1))
    assert isinstance(data, dict), "the mirror's frontmatter is not a mapping"
    return data


def test_the_stamp_exists_and_is_well_formed(frontmatter: dict) -> None:
    """version + blob + read-date, each in a shape a machine can act on."""
    assert frontmatter.get("version"), "no `version:` — nothing to compare upstream against"
    blob = str(frontmatter.get("synced-blob", ""))
    assert re.fullmatch(r"[0-9a-f]{12,40}", blob), (
        f"`synced-blob: {blob!r}` is not a git blob sha. It is the ONLY field that "
        f"answers 'is this copy current?' in one call — 3P-VER-05 forbids the branch "
        f"commit sha for that, because the tip moves on unrelated commits."
    )
    assert isinstance(frontmatter.get("synced-at"), date), (
        "`synced-at:` must be an unquoted ISO date. Without it the stamp records what "
        "was seen but not when — and an undated pin cannot go stale, it can only be "
        "silently wrong."
    )


def test_the_commit_sha_is_not_a_frontmatter_field(frontmatter: dict) -> None:
    """One pointer in the frontmatter, and it is the blob.

    `synced-commit` lived here beside `synced-blob` and I polled the wrong one for a
    week. Leaving the FORBIDDEN pointer next to the correct one invites exactly the
    mistake the stamp exists to prevent; the commit belongs in the banner prose,
    labelled provenance.
    """
    assert "synced-commit" not in frontmatter, (
        "`synced-commit` is back in the frontmatter. 3P-VER-05 forbids the branch sha "
        "as a change signal — keep it as prose in the banner, not as a field a script "
        "or a reader might poll."
    )


def test_the_banner_and_the_frontmatter_agree(mirror_text: str, frontmatter: dict) -> None:
    """A hand-edit of one half must not pass.

    The banner restates the version for a human reader; the frontmatter carries it
    for a machine. Re-syncing touches several places, and the version appears in
    three of them — this is what caught the pair drifting during the v5.3.3 sync.
    """
    version = str(frontmatter["version"])
    blob = str(frontmatter["synced-blob"])
    banner = mirror_text[: mirror_text.find("# Team Governance")]
    # Substring, not a backticked form: the blob is cited as the `expected:` line
    # inside the polling command's fence, which is where a reader comparing the
    # command's output actually needs it. Pinning the MARKUP would fail on a
    # correct doc and get this test deleted; the invariant is that the value is
    # there to compare against, not how it is decorated.
    assert blob in banner, (
        f"the banner does not cite the stamped blob {blob} — a reader running the "
        f"polling command has nothing to compare its output against"
    )
    assert version in banner, f"the banner does not cite the stamped version {version}"


def test_someone_has_actually_looked_recently(frontmatter: dict) -> None:
    """The load-bearing arm — and the only honest claim of the three.

    It asserts NOTHING about upstream. It says a human or agent last verified this
    copy N days ago, which is the fact the two incidents turned on: both were
    unnoticed drift, neither was a wrong stamp.
    """
    synced: date = frontmatter["synced-at"]
    age = (date.today() - synced).days
    assert age <= MAX_AGE_DAYS, (
        f"The governance mirror was last verified {age} days ago "
        f"(synced-at: {synced}, limit {MAX_AGE_DAYS}).\n"
        f"\n"
        f"THIS DOES NOT MEAN THE MIRROR IS STALE. It means nobody has checked — a "
        f"claim about our diligence, not about upstream. It cannot tell the two apart, "
        f"and it is not trying to.\n"
        f"\n"
        f"Confirm it in one call (no re-sync needed if the blob still matches):\n"
        f"  gh api 'repos/Emasoft/ai-maestro/contents/docs/GOVERNANCE-RULES.md"
        f"?ref=governance-rules' --jq .sha\n"
        f"\n"
        f"  matches `synced-blob` -> bump `synced-at:` to today and you are done\n"
        f"  differs               -> re-sync the body, then update version + blob + date\n"
        f"\n"
        f"A differing blob says something moved, never WHAT — it is a prompt to "
        f"re-read, not an answer."
    )
