"""No shipped file may teach a BARE `@name` — it pages a real GitHub user.

USER directive (2026-08-02, verbatim): *"when writing in github issues and comments never
use the `@<name>` syntax outside of a code block, since it triggers paging of other users!"*

This is not a style rule. **Every AI Maestro role name is a registered GitHub account**,
verified with `gh api users/<h>`:

    @manager       REAL - manager      (User)
    @janitor       REAL - janitor      (User)
    @owner         REAL - owner        (Organization)
    @role          REAL - ROLE         (Organization)
    @core          REAL - core         (Organization)
    @orchestrator  REAL - orchestrator (Organization)

So an agent writing "the @manager ruled X" in an issue body notifies a stranger who has
nothing to do with this project. Four were paged by mistake on 2026-08-02 (`@owner`,
`@role`, `@manager`, `@janitor`) by at least two different agents. The root cause was
PRRD G1.1's own recommended self-ID line, which contained a bare `@owner` -- so the rule
mandating GitHub writes was itself the leak (fixed: G1.1 -> G1.2, TRDD-NRQ5CG6I).

WHY THIS GUARDS THE TEMPLATES RATHER THAN THE AGENTS

A template is only safe if its LITERAL form is harmless, because literal pasting is the
expected failure mode, not an aberration. `<plugin-or-role>` is safe -- angle brackets read
as a slot nobody pastes verbatim. `@owner` is unsafe for the opposite reason: it looks like
finished text. Neither agent that leaked misunderstood the rule; each copied a placeholder
that happened to be a valid username.

WHAT IS EXEMPT, AND WHY EACH EXEMPTION IS SAFE

  * inside a code span (`@x`) or a fenced block -- GitHub does not linkify there. This is
    the fix the directive prescribes, so it must not also be a finding.
  * an email address (`user@gmail.com`) -- not a mention; the `@` is preceded by a word
    character, which is exactly what distinguishes it.
  * a version/ref suffix (`actions/checkout@v5`, `pkg@1.2.3`, `x@sha256`) -- same test:
    something precedes the `@`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SEARCH_ROOTS = ("skills", "commands", "design", "docs")

# A mention only fires when the `@` starts a token -- `a@b.com` and `checkout@v5` do not
# notify anyone. `(?<![\w/@.-])` is what encodes that, and it is the whole false-positive
# defence: without it every email address and every pinned action version becomes a finding.
_BARE_MENTION = re.compile(r"(?<![\w/@.\-])@([A-Za-z][A-Za-z0-9-]{1,38})\b")

# Handles that are known-registered GitHub accounts AND are words this ecosystem uses
# constantly in prose -- the intersection that makes this repo unusually exposed.
_DANGEROUS = frozenset({"manager", "janitor", "owner", "role", "core", "orchestrator", "gmail", "default", "other"})


def _strip_code(text: str) -> str:
    """Blank out fenced blocks and code spans -- the exempt zones.

    Replaced with spaces rather than deleted so reported line numbers stay truthful; a
    finding that points at the wrong line sends the reader to innocent text.
    """
    out = []
    in_fence = False
    for raw in text.splitlines():
        if raw.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), raw))
    return "\n".join(out)


def _shipped_markdown() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        base = PLUGIN_ROOT / root
        if base.is_dir():
            files.extend(p for p in base.rglob("*.md") if "_dev" not in p.parts)
    return sorted(files)


def _bare_mentions_in(path: Path) -> list[str]:
    found: list[str] = []
    for number, line in enumerate(_strip_code(path.read_text()).splitlines(), start=1):
        for m in _BARE_MENTION.finditer(line):
            if m.group(1).lower() in _DANGEROUS:
                found.append(f"{path.relative_to(PLUGIN_ROOT)}:{number}: @{m.group(1)}")
    return found


def test_no_shipped_file_teaches_a_bare_at_mention() -> None:
    """A bare `@name` in shipped prose is a real page the moment anyone copies it."""
    violations = [v for p in _shipped_markdown() for v in _bare_mentions_in(p)]
    assert not violations, (
        "Bare `@name` in shipped prose — each resolves to a REAL GitHub account and pages a "
        "stranger when copied into an issue or comment (PRRD G1.2). Fix by backticking the "
        "handle (`@name`), not by deleting the sentence:\n  " + "\n  ".join(violations)
    )


def test_the_scanner_actually_scans() -> None:
    """Never-vacuous guard: an empty corpus would make the sweep pass unconditionally."""
    files = _shipped_markdown()
    assert len(files) >= 40, f"only {len(files)} markdown files found; the glob is broken"


@pytest.mark.parametrize(
    ("sample", "should_flag", "why"),
    [
        ("the @manager ruled on this", True, "bare role name — pages a real User"),
        ("via the shared @owner gh auth", True, "the exact line that leaked"),
        ("ask the @janitor to re-arm", True, "bare role name"),
        ("via the shared `@owner` gh auth", False, "backticked — the prescribed fix"),
        ("mail fmuaddib@gmail.com for access", False, "email, not a mention"),
        ("uses: actions/checkout@v5", False, "version pin, not a mention"),
        ("the MANAGER ruled on this", False, "no @ at all — the safest form"),
    ],
)
def test_detector_classifies_known_shapes(sample: str, should_flag: bool, why: str) -> None:
    """Falsified in BOTH directions — must fire, and must not over-fire.

    The three non-flagging cases are load-bearing: an email address and a pinned action
    version both contain `name@word`, and flagging either would train everyone to ignore
    this check.
    """
    stripped = _strip_code(sample)
    hit = any(m.group(1).lower() in _DANGEROUS for m in _BARE_MENTION.finditer(stripped))
    assert hit is should_flag, f"misclassified ({why}): {sample!r}"
