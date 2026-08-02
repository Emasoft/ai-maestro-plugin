"""Behavioural contracts: what a skill TEACHES must exist in the CLI it teaches.

TRDD-YIOTS27H. `test_skill_and_command_contracts.py` reads every SKILL.md as *data* --
frontmatter, name/dir agreement, README rows, allowed-tools. Nothing there checks that a
taught subcommand or flag actually EXISTS, so a skill that teaches a renamed flag passes
that suite green and fails only in an agent's hands, where it surfaces as "the tool is
missing" rather than "the skill is wrong".

Three decisions from the card, each of which overturned the shape originally proposed.
They are recorded here because each was reached by measuring the shipped files, and a
later reader who re-derives them from intuition will get them wrong (I did, three times):

D1  Extract by SHAPE, from fenced code AND inline code spans -- NOT by fence.
    Measured across the 6 frozen CLIs: 42 mentions inside fenced blocks, 38 outside. The
    outside ones are not prose noise -- they are the `<example>` invocations, which carry
    flags and are therefore the lines most likely to drift. A fence-only extractor would
    miss ~47% AND would have needed an opt-in comment marker added to 28 skills.

D2  Check flags by SUBSTRING PRESENCE in --help, NEVER by parsing a flag list.
    A line-anchored parse (`^\\s*--[a-z-]+`) reported "no flags advertised" for
    aimaestro-continuity.sh and aimaestro-settings.sh and found only 6 of portfolio's.
    All false: these CLIs advertise flags INLINE inside a usage block --
    `set <path> --key <dot.path>`, `restart-self [--force]`. As substring presence, all 7
    flags ama-portfolio teaches are present.

D3  NOTHING a skill teaches is ever executed. Every check is static against --help, so the
    4 fenced blocks containing revoke/delete/git-commit/mint can never fire. That is why
    no opt-in marker is needed: the destructive-block problem dissolves instead of being
    solved.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = PLUGIN_ROOT / "skills"

# The frozen ai-maestro CLIs this repo ships wrappers for. Frozen is what makes checking
# them worthwhile: their surface is stable, so a mismatch is a real defect and not churn.
FROZEN_CLIS = (
    "aimaestro-session.sh",
    "aimaestro-panel.sh",
    "aimaestro-continuity.sh",
    "aimaestro-portfolio.sh",
    "aimaestro-settings.sh",
    "aimaestro-statusline.sh",
)

_INLINE_SPAN = re.compile(r"`([^`\n]+)`")
_LONG_FLAG = re.compile(r"--[a-z][a-z0-9-]*")
_SUBCOMMAND = re.compile(r"^[a-z][a-z0-9-]*$")
# Cut a candidate at the first shell separator so we never attribute a downstream
# command's flags to the CLI (`aimaestro-x.sh get | jq --raw-output` must not claim
# --raw-output is an aimaestro-x.sh flag).
_SEPARATOR = re.compile(r"(?:\|\||&&|[|;&><#])")
# A nested `$(other-cli --its-flag)` must be REMOVED before flags are read, or the inner
# command's flags get attributed to the outer one. Caught in the wild: ama-session teaches
# `aimaestro-session.sh state "$(aimaestro-agent.sh resolve --cwd .)" --pane`, and --cwd
# is aimaestro-agent.sh's -- the skill and the CLI were both correct, the extractor was not.
_CMD_SUBSTITUTION = re.compile(r"\$\([^()]*\)")

# Flags that belong to the SHELL or to a placeholder, not to the CLI under test.
_NOT_CLI_FLAGS = frozenset({"--"})


def _candidate_lines(text: str) -> list[str]:
    """Every line that could contain a command invocation (D1: fences AND inline spans).

    Backslash continuations inside fenced blocks are joined first, otherwise the flags on
    a wrapped invocation's second line are silently dropped -- those lines have no CLI
    token on them, so they would be skipped rather than mis-parsed. Coverage loss, not a
    false positive, but easy to avoid.
    """
    lines: list[str] = []
    in_fence = False
    pending = ""
    for raw in text.splitlines():
        # lstrip() is load-bearing: a fence nested in a numbered list is INDENTED
        # (`   ```bash`). Anchoring at column 0 silently swallowed ama-portfolio's whole
        # `mint` example -- the only place --binds-team/--kind/--ttl are taught -- and the
        # contracts still passed, because an extractor that finds nothing asserts nothing.
        if raw.lstrip().startswith("```"):
            in_fence = not in_fence
            if pending:
                lines.append(pending)
                pending = ""
            continue
        if in_fence:
            stripped = raw.rstrip()
            if stripped.endswith("\\"):
                pending += " " + stripped[:-1].strip()
                continue
            lines.append((pending + " " + stripped).strip() if pending else stripped)
            pending = ""
        else:
            lines.extend(_INLINE_SPAN.findall(raw))
    if pending:
        lines.append(pending)
    return lines


def _invocations(text: str, cli: str) -> list[tuple[str | None, set[str]]]:
    """Extract (subcommand, flags) for every invocation of `cli` in a SKILL.md."""
    found: list[tuple[str | None, set[str]]] = []
    for line in _candidate_lines(text):
        idx = line.find(cli)
        if idx == -1:
            continue
        tail = line[idx + len(cli) :]
        previous = None
        while previous != tail:  # loop: strip nested substitutions inside-out
            previous = tail
            tail = _CMD_SUBSTITUTION.sub(" ", tail)
        tail = _SEPARATOR.split(tail)[0]
        tokens = tail.split()
        subcommand = next((t for t in tokens if _SUBCOMMAND.match(t)), None)
        flags = {f for f in _LONG_FLAG.findall(tail)} - _NOT_CLI_FLAGS
        if subcommand or flags:
            found.append((subcommand, flags))
    return found


@lru_cache(maxsize=None)
def _help_text(cli: str) -> str:
    """The CLI's own --help, stdout+stderr. Cached: 6 CLIs x many assertions."""
    proc = subprocess.run(  # noqa: S603 - fixed argv, no shell, no user input
        [cli, "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return proc.stdout + proc.stderr


def _teachings(cli: str) -> dict[Path, list[tuple[str | None, set[str]]]]:
    out: dict[Path, list[tuple[str | None, set[str]]]] = {}
    for skill in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        invocations = _invocations(skill.read_text(), cli)
        if invocations:
            out[skill] = invocations
    return out


@pytest.mark.parametrize("cli", FROZEN_CLIS)
def test_every_flag_a_skill_teaches_is_advertised_by_the_cli(cli: str) -> None:
    """D2: each long flag taught for `cli` appears somewhere in that CLI's --help."""
    if shutil.which(cli) is None:
        pytest.skip(f"{cli} is not on PATH -- install ai-maestro to run this contract")
    help_text = _help_text(cli)
    assert help_text.strip(), f"{cli} --help produced nothing; cannot verify anything"

    missing: list[str] = []
    for skill, invocations in _teachings(cli).items():
        for _, flags in invocations:
            for flag in sorted(flags):
                if flag not in help_text:
                    missing.append(f"{skill.parent.name}: {cli} {flag}")
    assert not missing, (
        f"{cli}: these flags are taught by a skill but do not appear in its --help. "
        f"Either the CLI changed and the skill is now teaching a lie, or the flag is a "
        f"typo. Do NOT fix by deleting the flag from the skill without checking which.\n  " + "\n  ".join(missing)
    )


@pytest.mark.parametrize("cli", FROZEN_CLIS)
def test_every_subcommand_a_skill_teaches_is_advertised_by_the_cli(cli: str) -> None:
    """A renamed/removed subcommand is the loudest way a frozen CLI can break a skill."""
    if shutil.which(cli) is None:
        pytest.skip(f"{cli} is not on PATH -- install ai-maestro to run this contract")
    help_text = _help_text(cli)

    missing: list[str] = []
    for skill, invocations in _teachings(cli).items():
        for subcommand, _ in invocations:
            if subcommand and subcommand not in help_text:
                missing.append(f"{skill.parent.name}: {cli} {subcommand}")
    assert not missing, (
        f"{cli}: these subcommands are taught by a skill but do not appear in its --help:\n  " + "\n  ".join(missing)
    )


def test_the_extractor_actually_extracts() -> None:
    """Never skipped. Guards every assertion above against passing vacuously.

    Both contracts iterate over whatever the extractor returns, so an extractor that
    silently returns nothing turns them into unconditional greens -- the same vacuous-pass
    hazard `test_the_corpus_is_not_empty` guards in the structural suite. This asserts the
    extractor still finds the invocations we know are shipped, without needing any CLI on
    PATH.
    """
    portfolio = (SKILLS_DIR / "ama-portfolio" / "SKILL.md").read_text()
    invocations = _invocations(portfolio, "aimaestro-portfolio.sh")
    assert len(invocations) >= 5, f"extractor found only {len(invocations)} in ama-portfolio"

    subcommands = {s for s, _ in invocations}
    # `mint` and `verify` are the two taught WITH the CLI prefix. `list`/`revoke` are
    # taught BARE -- in the Quick-CLI-Reference table and in prose ("4. **Revoking** --
    # `revoke --subject <agent>`") -- so requiring a CLI token skips them. That is an
    # accepted coverage limit, not a bug: extracting a bare `list --subject` would
    # attribute any prose word to whichever CLI the page happens to be about.
    assert {"mint", "verify"} <= subcommands, (
        f"extractor missed a known subcommand; got {sorted(x for x in subcommands if x)}"
    )

    flags = set().union(*(f for _, f in invocations))
    # --binds-team appears ONLY in a fenced block; --binds only in an inline <example>
    # span. Requiring both proves D1's dual extraction really is dual.
    assert {"--subject", "--token", "--binds", "--binds-team"} <= flags, (
        f"extractor missed a known flag; got {sorted(flags)}"
    )


def test_a_separator_does_not_leak_a_downstream_commands_flags() -> None:
    """Never skipped. The extractor must not attribute piped-to flags to the CLI."""
    sample = "```bash\naimaestro-portfolio.sh list --json | jq --raw-output '.[]'\n```"
    (subcommand, flags) = _invocations(sample, "aimaestro-portfolio.sh")[0]
    assert subcommand == "list"
    assert flags == {"--json"}, f"leaked past the pipe: {sorted(flags)}"


def test_a_nested_command_substitution_does_not_leak_its_flags() -> None:
    """Never skipped. Regression for a real false positive this suite produced.

    The first run of this module reported `aimaestro-session.sh --cwd` as an undeclared
    flag. Both the skill and the CLI were correct: --cwd belongs to the aimaestro-agent.sh
    call nested in a `$(...)`. An extractor that reads inward manufactures defects in
    working skills, which is the most expensive kind of false positive -- someone
    "fixes" it by deleting a correct flag.
    """
    sample = '```bash\naimaestro-session.sh state "$(aimaestro-agent.sh resolve --cwd .)" --pane\n```'
    (subcommand, flags) = _invocations(sample, "aimaestro-session.sh")[0]
    assert subcommand == "state"
    assert flags == {"--pane"}, f"leaked into the substitution: {sorted(flags)}"
