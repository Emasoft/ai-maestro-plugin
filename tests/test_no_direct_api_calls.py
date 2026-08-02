"""IRON RULE: no shipped surface may instruct a DIRECT call to the ai-maestro server API.

USER directive (2026-06-15, restated 2026-08-02), tracked as core#11 and ai-maestro R23:
agents call the frozen `aimaestro-*`/`amp-*`/`aid-*` CLIs, which resolve the API base and the
caller's identity internally. A plugin must not embed endpoint knowledge. The separation is
absolute -- a skill that teaches `curl .../api/...` hands every reader a way around the auth,
identity, and governance the CLI layer enforces.

Until now that rule was enforced ONLY by hand-auditing `grep -rn '/api/'`, which is why this
file exists: a hand audit does not run on the skill someone adds next month. CORE was verified
compliant by hand on 2026-08-02; this converts that one-time verification into a standing one.

WHAT COUNTS AS A VIOLATION (and why the definition is this narrow)

`grep '/api/'` alone is useless here -- 75 of its hits in this repo are the rule being STATED,
not broken: decoupling comments, `**Maps to:**` reference notes, and explicit "Do NOT call
/api/* directly (core#11)" prohibitions. A guard that flagged those would fire on the very
documentation that enforces the rule, and would be deleted within a week.

So a violation is RUNNABLE + HTTP + ai-maestro:
  runnable  -- inside a fenced code block (markdown), or a non-comment line (.sh/.py)
  HTTP      -- invokes an HTTP client (curl/wget/fetch/requests/urlopen/http)
  ai-maestro-- the URL carries `/api/` or $AIMAESTRO_API_BASE, and the host is not GitHub

DELIBERATE EXEMPTIONS -- do not "tighten" these without reading why:
  * GitHub (`api.github.com`, `raw.githubusercontent.com`) -- core#11 scopes the rule to the
    ai-maestro server's own API. `gh` and GitHub REST are explicitly out of scope.
  * A reachability probe to the server ROOT (`http://host:23000/`) is not an API call.
    network-security/SKILL.md:68 does exactly this and is annotated as such. Flagging it would
    be a false positive on a correct skill -- the failure mode this suite has already produced
    four times in one session (id:ATOM-FP3O-ZGLD).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SEARCH_ROOTS = ("skills", "commands", "scripts", "hooks")

_HTTP_CLIENT = re.compile(r"\b(curl|wget|fetch|requests\.(get|post|put|delete|patch)|urlopen)\b")
_AIMAESTRO_TARGET = re.compile(r"/api/|\$\{?AIMAESTRO_API_BASE")
_GITHUB_HOST = re.compile(r"api\.github\.com|raw\.githubusercontent\.com|github\.com")


def _runnable_lines(path: Path) -> list[tuple[int, str]]:
    """Lines an agent would actually EXECUTE, not lines that merely mention a thing.

    Markdown -> only inside fenced blocks. Shell/Python -> only non-comment lines.
    `lstrip()` on the fence marker is load-bearing: a fence nested in a numbered list is
    indented, and anchoring at column 0 makes the whole block invisible -- which would make
    this guard pass vacuously. (Same bug already cost a debugging cycle in
    test_skill_cli_contracts.py; the guard below is why it cannot happen silently here.)
    """
    lines: list[tuple[int, str]] = []
    text = path.read_text(errors="replace")
    if path.suffix == ".md":
        in_fence = False
        for number, raw in enumerate(text.splitlines(), start=1):
            if raw.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence and not raw.lstrip().startswith("#"):
                lines.append((number, raw))
    else:
        for number, raw in enumerate(text.splitlines(), start=1):
            stripped = raw.lstrip()
            if stripped and not stripped.startswith(("#", "//", "*")):
                lines.append((number, raw))
    return lines


def _shipped_files() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        base = PLUGIN_ROOT / root
        if not base.is_dir():
            continue
        for suffix in ("*.md", "*.sh", "*.py"):
            files.extend(p for p in base.rglob(suffix) if "_dev" not in p.parts)
    return sorted(files)


def _violations_in(path: Path) -> list[str]:
    found: list[str] = []
    for number, line in _runnable_lines(path):
        if not _HTTP_CLIENT.search(line):
            continue
        if not _AIMAESTRO_TARGET.search(line):
            continue
        if _GITHUB_HOST.search(line):
            continue
        found.append(f"{path.relative_to(PLUGIN_ROOT)}:{number}: {line.strip()[:120]}")
    return found


def test_no_shipped_surface_calls_the_ai_maestro_api_directly() -> None:
    """The iron rule, made executable.

    If this fails, do NOT satisfy it by deleting the line: find the frozen CLI verb that
    wraps the endpoint and teach that instead. If no verb exists, the endpoint's logic
    belongs in the ai-maestro project as a new CLI verb -- file it there (core#11), and mark
    the site DECOUPLE-BLOCKED with the issue number in the meantime.
    """
    violations = [v for path in _shipped_files() for v in _violations_in(path)]
    assert not violations, (
        "Direct ai-maestro API call(s) in a shipped surface. Agents must call the frozen "
        "CLI layer, which resolves the API base and the caller's identity internally "
        "(core#11 / R23):\n  " + "\n  ".join(violations)
    )


# A skill that NAMES a frozen CLI is teaching the boundary whether it means to or not.
_FROZEN_CLI_NAMED = re.compile(r"\b(aimaestro-[a-z-]+\.sh|amp-[a-z-]+\.sh|aid-[a-z-]+\.sh)\b")
# Accepted ways of stating the boundary. Deliberately permissive on WORDING and strict on
# MEANING: each pattern pairs a negation with the API. Prose is preferred, but an HTML
# comment counts -- it is still text the reading agent receives.
_BOUNDARY_STATED = re.compile(
    r"never (call |curl |its |the )?[^.]{0,40}api"
    r"|not (call|curl) [^.]{0,40}api"
    r"|must not call[^.]{0,40}api"
    r"|forbidden[^.]{0,40}api"
    r"|may (curl|call)[^.]{0,40}api directly"
    r"|/api/\*? directly"
    r"|decoupl[^.]{0,60}api"
    r"|decoupled per manager core#11",
    re.I,
)


def _prose(text: str) -> str:
    """Collapse newlines so a boundary sentence that WRAPS still matches.

    Markdown prose is hard-wrapped, so `ama-statusline` states the rule as
    "...may curl the AI\\nMaestro API directly" -- a matcher bounded by `\\n` calls that
    skill silent and sends someone to "fix" a skill that is already correct. Bounding on
    `.` only (sentence end) after collapsing is what makes the check about MEANING rather
    than about where the author happened to wrap.
    """
    return " ".join(text.split())


def test_every_skill_naming_a_frozen_cli_also_states_the_boundary() -> None:
    """The INSTRUCT half of the iron rule -- not offending is not instructing.

    USER directive (2026-08-02): "all plugins must instruct in their skills to use the
    ai-maestro scripts, never the api directly". `test_no_shipped_surface_calls_...` above
    only proves CORE does not OFFEND. That is the easy half, and it is greppable.

    This is the half that is NOT greppable as an absence: a skill that names
    `aimaestro-agent.sh` in a routing table while never saying the API is off-limits teaches
    the reader that the script is one option among several. The reader then reaches for the
    API the first time the CLI lacks a verb -- which is exactly the situation that arises in
    practice (ai-maestro-janitor#167: a wake-gate field with no CLI flag).

    Credit: this gap was identified by the ai-maestro-janitor Claude on janitor#168 after CORE's
    own audit missed it; measured here it held for 9 of the 13 CORE skills that name a CLI,
    three of them written the same day. Verified independently before acting on it.
    """
    silent: list[str] = []
    for skill in sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md")):
        text = _prose(skill.read_text())
        if not _FROZEN_CLI_NAMED.search(text):
            continue  # does not touch the boundary; nothing to state
        if not _BOUNDARY_STATED.search(text):
            silent.append(skill.parent.name)
    assert not silent, (
        "These skills name a frozen ai-maestro CLI but never tell the reader the API is "
        "off-limits. Naming the script is not the same as forbidding the alternative -- add "
        "one sentence (e.g. 'Never call the ai-maestro server API directly; this CLI resolves "
        "the API base and your identity internally (core#11).'):\n  " + "\n  ".join(silent)
    )


def test_the_scanner_actually_scans() -> None:
    """Never-vacuous guard: the sweep above asserts nothing if the corpus reads as empty."""
    files = _shipped_files()
    assert len(files) >= 40, f"only {len(files)} shipped files found; the glob is broken"
    runnable = sum(len(_runnable_lines(p)) for p in files)
    assert runnable >= 200, f"only {runnable} runnable lines extracted; the extractor is broken"


@pytest.mark.parametrize(
    ("sample", "should_flag", "why"),
    [
        ('curl -s "$AIMAESTRO_API_BASE/api/agents"', True, "the exact banned shape"),
        ('curl -s "http://localhost:23000/api/governance"', True, "hardcoded endpoint"),
        ("requests.get(f'{base}/api/teams')", True, "python client"),
        ('curl -s "https://api.github.com/repos/x/y"', False, "GitHub is out of scope"),
        ('curl -sL "https://raw.githubusercontent.com/o/r/main/f"', False, "GitHub raw"),
        ('curl -s -o /dev/null "http://$(tailscale ip -4):23000/"', False, "root reachability probe"),
        ("aimaestro-agent.sh list --json", False, "the CLI layer — the correct form"),
    ],
)
def test_violation_detector_classifies_known_shapes(sample: str, should_flag: bool, why: str) -> None:
    """Falsifies the detector in BOTH directions — it must fire, and must not over-fire.

    The false-positive half matters as much as the true-positive half: a guard that flags a
    correct skill gets "fixed" by breaking working documentation.
    """
    flagged = bool(_HTTP_CLIENT.search(sample) and _AIMAESTRO_TARGET.search(sample) and not _GITHUB_HOST.search(sample))
    assert flagged is should_flag, f"misclassified ({why}): {sample!r}"
