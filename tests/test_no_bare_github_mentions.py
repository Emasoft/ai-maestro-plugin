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

  * inside a code span (`@x`) or an INERT fenced block -- GitHub does not linkify there.
    This is the fix the directive prescribes, so it must not also be a finding.
    EXCEPTION: a fence that BUILDS a GitHub body (`gh issue comment --body …`) is an
    EMITTER and IS scanned -- inert where it sits, but its output posts the handle bare.
    See `_strip_code`; credit to the MANAGER (ai-maestro#109), whose prose-only audit
    found 5 of 8 real leaks because the other 3 lived in runnable command examples.
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


# A fenced block that BUILDS a GitHub body is an EMITTER, not an exempt zone. Inside the
# document the handle is inert; the command's OUTPUT is a comment body carrying it bare.
# The doc is safe, running the doc is not -- so an emitter fence is scanned like prose.
_EMITS_GITHUB_BODY = re.compile(r"\bgh\s+(issue|pr|api)\b[^\n]*--(body|field|raw-field)\b")


def _strip_code(text: str) -> str:
    """Blank out fenced blocks and code spans -- EXCEPT fences that emit a GitHub body.

    Replaced with spaces rather than deleted so reported line numbers stay truthful; a
    finding that points at the wrong line sends the reader to innocent text.

    THE EMITTER CARVE-OUT (credit: the MANAGER, ai-maestro#109). Exempting every fence was
    wrong. Three of their eight leaks lived inside `gh issue comment --body "$(printf …)"`
    blocks: inert where they sat, so a prose-only audit correctly cleared the page -- while
    running it posted the handle bare. An audit of prose alone found 5 of 8. CORE has no
    such instance today (1 emitter line, and it builds no mention), but the hole was in the
    DETECTOR, and a detector is worth more than the absence of a current instance.
    """
    lines = text.splitlines()
    # First pass: mark which fenced regions are emitters, so we know before blanking.
    emitter_line = [False] * len(lines)
    start, in_fence = 0, False
    for i, raw in enumerate(lines):
        if raw.lstrip().startswith("```"):
            if in_fence and _EMITS_GITHUB_BODY.search("\n".join(lines[start:i])):
                for j in range(start, i):
                    emitter_line[j] = True
            start, in_fence = i + 1, not in_fence
    if in_fence and _EMITS_GITHUB_BODY.search("\n".join(lines[start:])):
        for j in range(start, len(lines)):
            emitter_line[j] = True

    # An UNTERMINATED trailing fence is scanned as PROSE, not exempted (credit: the MANAGER,
    # ai-maestro-janitor#171). A body ending mid-fence is malformed and the two guesses are not
    # symmetric: "exempt" silently drops the last block of the file from the scan, while "prose"
    # costs at most a false positive on text that is already broken. This guard's whole premise
    # is that a silent miss is the expensive failure, so it fails toward the noisy answer.
    fences = [i for i, raw in enumerate(lines) if raw.lstrip().startswith("```")]
    unterminated_from = fences[-1] if len(fences) % 2 else len(lines)

    out, in_fence = [], False
    for i, raw in enumerate(lines):
        if raw.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence and i < unterminated_from:
            out.append(raw if emitter_line[i] else "")
        else:
            out.append(re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), raw))
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
    """Falsifies the detector in BOTH directions — must fire, and must not over-fire.

    The three non-flagging cases are load-bearing: an email address and a pinned action
    version both contain `name@word`, and flagging either would train everyone to ignore
    this check.
    """
    stripped = _strip_code(sample)
    hit = any(m.group(1).lower() in _DANGEROUS for m in _BARE_MENTION.finditer(stripped))
    assert hit is should_flag, f"misclassified ({why}): {sample!r}"


@pytest.mark.parametrize(
    ("block", "should_flag", "why"),
    [
        (
            '```bash\ngh issue comment 1 --body "posted by @manager"\n```',
            True,
            "EMITTER: the fence builds a GitHub body carrying the handle bare",
        ),
        (
            "```bash\ngh api users/manager --jq .login\n```",
            False,
            "reads a user, emits no body — and carries no bare handle anyway",
        ),
        (
            "```bash\ngrep -rn '@manager' .\n```",
            False,
            "an ordinary fence is inert; exempting it is correct",
        ),
        (
            "```text\n_Posted by the Claude developing X (via the shared @owner gh auth)._\n```",
            False,
            "quoted DOC of the defect (archived TRDD) — inert, must not be flagged",
        ),
        (
            "intro\n```text\nthe @manager ruled on this",
            True,
            "UNTERMINATED fence — malformed, so scanned as prose rather than silently exempted",
        ),
        (
            "intro\n```text\nthe @manager ruled\n```\ntail",
            False,
            "the SAME text in a CLOSED fence stays exempt — the fix must not break the normal case",
        ),
    ],
)
def test_an_emitter_fence_is_scanned_but_an_inert_fence_is_not(block: str, should_flag: bool, why: str) -> None:
    """The carve-out the MANAGER's data forced (ai-maestro#109).

    Both directions matter. Missing an emitter posts a real page; flagging an inert fence
    would redden the archived TRDD that documents this very defect, and a guard that
    reddens on its own post-mortem gets deleted.
    """
    stripped = _strip_code(block)
    hit = any(m.group(1).lower() in _DANGEROUS for m in _BARE_MENTION.finditer(stripped))
    assert hit is should_flag, f"misclassified ({why}): {block!r}"
