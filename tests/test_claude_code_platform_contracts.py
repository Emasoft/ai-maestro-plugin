"""Platform contracts this plugin must keep to stay loadable by current Claude Code.

Each rule here corresponds to a Claude Code change that BREAKS A PLUGIN SILENTLY -- the
plugin still installs, still validates, and simply stops doing part of its job. That is
the whole reason these are tests rather than a note: a hand audit of the changelog
answers the question once, for the version that happened to be current that day.

The rules, with the release that introduced each:

  * 2.1.207 -- `${user_config.*}` inside a SHELL-FORM hook command is now REJECTED
    (shell-injection fix). The sanctioned forms are exec form (`args` array) or
    `$CLAUDE_PLUGIN_OPTION_<KEY>` read inside the script. A hook that trips this does
    not error loudly; it stops running.
  * 2.1.218 -- an agent `name` containing `:` is rejected (`:` is reserved for plugin
    namespacing).
  * 2.1.210 -- `Write(path)`, `NotebookEdit(path)` and `Glob(path)` permission rules
    produce a startup warning; `Edit(path)` / `Read(path)` are the intended spellings.
  * 2.1.221 -- a skill or command named after a terminal-only built-in (`/help`,
    `/feedback`, ...) is un-invocable in non-interactive sessions, so it works when a
    human tries it and fails in exactly the automated runs nobody is watching.
  * 2.1.224 -- `SendMessage` / `ListAgents` added a native session-to-session transport
    that never reaches the ai-maestro server. Any text asserting the comm graph is
    enforced by a 403 became a claim about ONE of two transports, and the unpoliced one
    is the one an agent reaches for by reflex when told to "send it a message".

Plus one invariant that is ours rather than the platform's, and which every future hook
addition can break: EVERY event in `hooks/hooks.json` must have a handler, and every
handler must be reachable from an event. Both directions matter -- an unhandled event
forks a node process on every fire to do nothing, and an unreachable handler is dead
code that reads as live coverage.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOKS_JSON = PLUGIN_ROOT / "hooks" / "hooks.json"
HOOK_SCRIPT = PLUGIN_ROOT / "scripts" / "ai-maestro-hook.cjs"

# Interpolation the 2.1.207 fix rejects in a shell-form command.
_USER_CONFIG = re.compile(r"\$\{\s*user_config\.")

# Permission-rule spellings that warn at startup (2.1.210).
_WARNING_RULE = re.compile(r"^(Write|Glob|NotebookEdit)\(")

# The claim that makes a 403 mention safe: the native transport is NOT policed. Naming
# `SendMessage` is not enough on its own -- the ARCHITECT role-plugin's counterexample on
# ai-maestro#131 was a body that named the tool and still opened with "violations return
# HTTP 403", which passes a keyword scan while making exactly the false promise. Kept as a
# permissive alternation of the SEMANTIC forms rather than one blessed sentence: a gate
# that reddens on correct writing gets deleted, and then nothing checks the property.
# The OPERATIVE claim, in each phrasing this corpus actually uses. A keyword survives the
# deletion of the rule it belongs to, because the RATIONALE around a rule repeats its
# keywords; a fragment of the rule's own SENTENCE does not, because commentary describes a
# rule in different words than the rule states it. That divergence is the signal these ride
# (CHIEF-OF-STAFF, ai-maestro#131 — "claim collocation", after my distance predicate was
# measured and rejected).
#
# Keep each 3-6 words: long fragments red on a comma edit, short ones survive ordinary
# rewording and die on deletion. Matched against whitespace-collapsed lowercase text so
# rewrapping and blockquote prefixes do not red them. Adding a claiming file with a SIXTH
# phrasing reds this deliberately — add the phrasing here in the same commit.
_OPERATIVE_CLAIMS = (
    "never received is not permission",
    "describes messages sent over",
    "scope of that enforcement: amp only",
    "exists only on the amp path",
    "no server in the path",
    "recipient, not the transport",
    "transport does not excuse you",
)


def _collapsed(text: str) -> str:
    return re.sub(r"\s+", " ", text).lower()


_NOT_POLICED = re.compile(
    r"no 403|cannot return (one|a 403)|not enforced|nothing on (that|it) path can|"
    r"no server in the path|without touching the (ai-maestro )?server|never (reaches|traverses) the server|"
    r"returns no(thing| such| error| 403)|no place for one|unpoliced",
    re.IGNORECASE,
)

# Terminal-only built-ins: a plugin skill with one of these names loads fine and is
# simply un-invocable headlessly (2.1.221).
_TERMINAL_BUILTINS = frozenset(
    {"help", "feedback", "clear", "compact", "config", "model", "status", "resume", "login", "logout", "doctor"}
)

# Every hook event Claude Code dispatches, taken from the 2.1.222 binary's own event enum
# rather than from docs -- docs lag, and this list decides whether a hook ever runs.
# Refresh when a release adds events (the block is contiguous, starting at PreToolUse):
#   strings -a "$(readlink "$(command -v claude)")" | grep -A18 -x 'PreToolUse'
_KNOWN_HOOK_EVENTS = frozenset(
    {
        "PreToolUse", "PostToolUse", "PostToolUseFailure", "PostToolBatch", "PermissionDenied",
        "Notification", "UserPromptSubmit", "UserPromptExpansion", "SessionStart", "SessionEnd",
        "Stop", "StopFailure", "SubagentStart", "SubagentStop", "PreCompact", "PostCompact",
        "PermissionRequest", "Setup", "TeammateIdle", "TaskCreated", "TaskCompleted",
        "Elicitation", "ElicitationResult", "ConfigChange", "InstructionsLoaded", "CwdChanged",
        "FileChanged", "DirectoryAdded", "MessageDisplay",
    }
)


def _hook_entries() -> list[tuple[str, dict]]:
    """(event, hook-entry) for every hook this plugin registers."""
    hooks = json.loads(HOOKS_JSON.read_text())["hooks"]
    return [(event, hook) for event, matchers in hooks.items() for m in matchers for hook in m["hooks"]]


def test_every_hook_uses_exec_form_and_no_user_config_interpolation() -> None:
    """2.1.207: a shell-form command carrying `${user_config.*}` is rejected at runtime.

    Checked as two separate assertions because they fail for different reasons and a
    reader needs to know which: exec form is the structural fix, and the interpolation
    is the specific thing that is refused.
    """
    for event, hook in _hook_entries():
        assert "args" in hook, f"{event}: hook uses shell form; use exec form (`command` + `args`)"
        blob = hook["command"] + " " + " ".join(hook["args"])
        assert not _USER_CONFIG.search(blob), (
            f"{event}: `${{user_config.*}}` in a hook command is REJECTED since 2.1.207 — "
            "read $CLAUDE_PLUGIN_OPTION_<KEY> inside the script instead"
        )


def test_hooks_json_and_handler_cases_agree_in_both_directions() -> None:
    """Every registered event has a handler, and every handler is reachable.

    The dead-handler half is the one that rots quietly: a `case` for an event nobody
    registers looks like working coverage in a code read and never executes.
    """
    events = set(json.loads(HOOKS_JSON.read_text())["hooks"])
    src = HOOK_SCRIPT.read_text()
    cases = set(re.findall(r"case '([A-Za-z]+)':", src))

    # The directory guard is a separate script with its own entry point, so its events
    # are legitimately absent from the notifier's switch.
    guarded = {event for event, hook in _hook_entries() if any("directory-guard" in a for a in hook.get("args", []))}

    assert not (events - cases - guarded), f"hooks.json events with no handler: {sorted(events - cases - guarded)}"
    assert not (cases - events), f"handler cases no event reaches: {sorted(cases - events)}"


def test_every_registered_hook_event_is_one_claude_code_actually_dispatches() -> None:
    """A hook on an event name Claude Code does not have is DEAD CONFIG, and it is silent.

    The parity test above proves hooks.json and the handler agree with EACH OTHER. Both can
    agree on a name the platform never dispatches -- a typo, or an event renamed by a
    release. Nothing warns: registration succeeds, the handler is present and reachable in a
    code read, and it simply never runs. That is indistinguishable from a handler whose
    condition never matched, which is why it can sit dead for months.

    Verified 2026-08-05 against 2.1.222: all 12 registered events are valid, so this locks a
    passing state rather than reporting a defect. The 17 unused events are deliberate -- a
    hook costs a process spawn on every occurrence, so coverage is a design choice, not a
    completeness target. This test says nothing about which events SHOULD be registered.
    """
    declared = set(json.loads(HOOKS_JSON.read_text())["hooks"])
    assert declared, "hooks.json registered no events at all -- this contract would pass vacuously"

    unknown = sorted(declared - _KNOWN_HOOK_EVENTS)
    assert not unknown, (
        f"hooks.json registers {unknown}, which Claude Code does not dispatch. Either the name "
        f"is a typo, or a release renamed the event -- in both cases the handler never runs and "
        f"nothing reports it. Check the current enum with:\n"
        f"  strings -a \"$(readlink \"$(command -v claude)\")\" | grep -A18 -x 'PreToolUse'\n"
        f"If the event is genuinely new, add it to _KNOWN_HOOK_EVENTS; do NOT delete the hook "
        f"to make this pass without confirming which of the two causes it is."
    )


def test_no_agent_name_contains_a_colon() -> None:
    """2.1.218: `:` is reserved for plugin namespacing and now rejects the agent file.

    NOTE: this plugin currently ships no agents, so this passes with nothing to check.
    That is deliberate, not an oversight — it is the guard that catches the FIRST agent
    added later, when nobody will remember the constraint. Verified by falsification
    against a temp tree rather than by a green run here, since a green run proves
    nothing while `agents/` is empty.
    """
    offenders = []
    for path in (PLUGIN_ROOT / "agents").rglob("*.md") if (PLUGIN_ROOT / "agents").is_dir() else []:
        match = re.search(r"^name:\s*(.+)$", path.read_text(), re.MULTILINE)
        if match and ":" in match.group(1):
            offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {match.group(1).strip()}")
    assert not offenders, "agent names containing ':' are rejected since 2.1.218:\n  " + "\n  ".join(offenders)


def test_no_permission_rule_uses_a_warning_spelling() -> None:
    """2.1.210: Write()/Glob()/NotebookEdit() rules warn at startup; Edit()/Read() do not."""
    offenders = []
    for path in PLUGIN_ROOT.rglob("*.json"):
        if "_dev" in path.parts or ".git" in path.parts or "node_modules" in path.parts:
            continue
        try:
            blob = json.loads(path.read_text())
        except (ValueError, UnicodeDecodeError):
            continue
        for rule in _iter_permission_rules(blob):
            if _WARNING_RULE.match(rule):
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {rule}")
    assert not offenders, "permission rules that warn at startup (use Edit()/Read()):\n  " + "\n  ".join(offenders)


def _iter_permission_rules(blob: object):
    """Yield every string under a `permissions` allow/deny/ask list, at any depth."""
    if isinstance(blob, dict):
        for key, value in blob.items():
            if key == "permissions" and isinstance(value, dict):
                for bucket in ("allow", "deny", "ask"):
                    yield from (r for r in value.get(bucket, []) if isinstance(r, str))
            else:
                yield from _iter_permission_rules(value)
    elif isinstance(blob, list):
        for item in blob:
            yield from _iter_permission_rules(item)


def test_no_skill_or_command_shadows_a_terminal_only_builtin() -> None:
    """2.1.221: such a name is invocable interactively and dead in headless runs.

    That asymmetry is the danger — it passes every manual check and fails only where
    nobody is watching.
    """
    offenders = []
    for root in ("skills", "commands"):
        base = PLUGIN_ROOT / root
        if not base.is_dir():
            continue
        for path in base.rglob("*.md"):
            if "_dev" in path.parts:
                continue
            match = re.search(r"^name:\s*(.+)$", path.read_text(), re.MULTILINE)
            name = match.group(1).strip() if match else path.parent.name
            if name.lower() in _TERMINAL_BUILTINS:
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: /{name}")
    assert not offenders, "names shadowing terminal-only built-ins (2.1.221):\n  " + "\n  ".join(offenders)


def test_the_scanners_actually_scanned() -> None:
    """Never-vacuous guard: every check above passes trivially on an empty corpus.

    Five of the six tests in this file are 'assert no offenders'. Without this, a broken
    glob or a moved directory turns the whole file green while checking nothing — the
    exact failure that made the CLI-contract suite pass vacuously earlier in this
    plugin's history.
    """
    assert HOOKS_JSON.is_file(), "hooks/hooks.json missing — the hook checks scanned nothing"
    assert HOOK_SCRIPT.is_file(), "scripts/ai-maestro-hook.cjs missing — the parity check scanned nothing"
    assert len(_hook_entries()) >= 10, f"only {len(_hook_entries())} hook entries parsed; the reader is broken"
    skills = [p for p in (PLUGIN_ROOT / "skills").rglob("*.md") if "_dev" not in p.parts]
    assert len(skills) >= 40, f"only {len(skills)} skill files found; the glob is broken"


def test_no_403_claim_travels_without_the_transport_that_cannot_return_one() -> None:
    """2.1.224: a comm-graph 403 is evidence about AMP and about nothing else.

    Every file that tells an agent a forbidden edge returns HTTP 403
    `title_communication_forbidden` must, in the same file, name the native
    `SendMessage` transport that returns no such thing — otherwise the claim reads as
    "every send is checked", and the agent routes around its own comm graph believing
    the server has it covered.

    Naming the transport IS the scope, which is why that is what is asserted rather
    than a phrase: a prose marker can be reworded into meaninglessness while still
    matching, and a file that mentions `SendMessage` at all cannot still be claiming
    AMP is the only way agents reach each other.

    Measured on `ai-maestro#131`: 7 of 7 role-plugin personas asserted the 403, 0 of 7
    named the transport. CORE's four files were in the same state; this test is what
    keeps them out of it.

    A GUARD'S SCOPE IS PART OF ITS CLAIM. This scanned `skills/` only until 2026-08-11,
    and was green while `tests/scenarios/governance-scenarios.md` carried an unscoped
    403 in a PASS criterion — a scenario satisfied by an agent that routes around AMP is
    the failure it exists to catch, sitting in the file consulted when behaviour is
    judged. Found by the AUTONOMOUS role-plugin hitting the identical defect
    (`ai-maestro#143`): after fixing its persona, its `test_persona_*` guards stayed
    green while the claim survived in a governance checklist and an adversarial fixture.
    "I fixed the file I was thinking about" is not "the plugin is fixed", and in a green
    run those are indistinguishable.

    `design/` is excluded on their advice: terminal TRDDs are FROZEN by rule, so a guard
    demanding an edit there would force a rule violation to go green. `CHANGELOG.md` is
    excluded for the same reason — it records what past releases said, and correcting
    history is not the same as correcting a claim.

    MEASURED BLIND SPOT — this guard is word-presence, so RATIONALE can satisfy it after
    the RULE is gone (the CHIEF-OF-STAFF's finding, `ai-maestro#131`). Deleting the two
    operative paragraphs from `skills/agent-messaging/SKILL.md` (790 chars — the ones that
    actually say the 403 describes AMP and that a 403 you never received is not permission)
    leaves this **GREEN**: three other `SendMessage` mentions and the "unpoliced INBOUND"
    heading survive in the prose written *around* the rule. Documenting why a rule exists
    is what weakens a keyword-shaped guard over it — the words are present either way, so
    only POSITION separates the rule from the commentary.

    Per-file redundancy, measured, which is what decides exploitability:

        skills/agent-messaging/SKILL.md              SendMessage x5   scoping x4  <- soft
        skills/agent-messaging/reference/…           x1  x2
        skills/team-governance/SKILL.md              x1  x1
        skills/team-governance/references/REFERENCE  x1  x2
        tests/scenarios/governance-scenarios.md      x1  x1

    Four of five are unique-term, so deleting their operative line DOES redden this.

    A DISTANCE PREDICATE WAS MEASURED AND REJECTED — do not re-propose one. Requiring the
    scoping evidence within N chars of each 403 mention cannot separate the cases: real
    worst-gaps are 506 / **7915** / 292 / **7213** / 497 against the gutted file's 1610, so
    any threshold catching the defect reddens two CORRECT files whose 403 lives in a rules
    table far from the scoping section. A guard that reddens on correct writing gets
    deleted, taking its real coverage with it.

    THE FIX IS THE CLAIM ARM BELOW, not distance. A fragment of the rule's own SENTENCE is
    what rationale cannot reproduce — commentary describes a rule in different words than
    the rule states it, and the more a rule is explained the more distinctive its own
    statement becomes relative to the prose around it. No distance is involved, so the
    7915/7213 false positives never arise. All five files carry one; the gutted seed loses
    both of the two it removed. (Prescription from the CHIEF-OF-STAFF on `ai-maestro#131`,
    re-measured here rather than adopted — their first framing, "assert at rule POSITION",
    is what the distance measurement above killed, and they withdrew it.)

    RESIDUAL BLIND SPOT, narrower than it was and still real: the corpus arm is ANY-OF, so
    a file carrying several claims survives losing some. That is why the one file with
    redundant keywords gets `test_the_soft_file_keeps_every_one_of_its_operative_claims`,
    one assertion per claim. Neither arm catches a rule WEAKENED in place.
    """
    roots = ("skills", "commands", "docs", "tests/scenarios")
    files = [p for r in roots for p in (PLUGIN_ROOT / r).rglob("*.md") if (PLUGIN_ROOT / r).is_dir()]
    files.append(PLUGIN_ROOT / "README.md")
    claims = sorted(
        p
        for p in files
        if p.is_file() and "_dev" not in p.parts and "title_communication_forbidden" in p.read_text()
    )
    assert claims, "no file asserts the comm-graph 403 — the scanner is broken, not the corpus clean"
    unnamed = [p.relative_to(PLUGIN_ROOT).as_posix() for p in claims if "SendMessage" not in p.read_text()]
    assert not unnamed, (
        "these assert a 403 enforces the comm graph without naming the transport that "
        f"cannot return one (Claude Code 2.1.224): {unnamed}"
    )
    unscoped = [
        p.relative_to(PLUGIN_ROOT).as_posix() for p in claims if not _NOT_POLICED.search(p.read_text())
    ]
    assert not unscoped, (
        "these name the transport but never say it is UNPOLICED, so the 403 still reads as "
        f"covering every send: {unscoped}"
    )
    # The arm the two keyword arms above cannot provide: a fragment of the rule's own
    # SENTENCE, which rationale prose does not reproduce. Measured — all five files carry
    # one; the gutted soft file loses two of its four.
    claimless = [
        p.relative_to(PLUGIN_ROOT).as_posix()
        for p in claims
        if not any(c in _collapsed(p.read_text()) for c in _OPERATIVE_CLAIMS)
    ]
    assert not claimless, (
        "these carry the 403 keywords but no OPERATIVE claim sentence — the scoping may have "
        f"been deleted while the prose about it survived: {claimless}. Either restore the "
        f"claim or add its new phrasing to _OPERATIVE_CLAIMS in the same commit."
    )


@pytest.mark.parametrize(
    "claim",
    [
        "never received is not permission",
        "describes messages sent over",
        "recipient, not the transport",
        "transport does not excuse you",
    ],
)
def test_the_soft_file_keeps_every_one_of_its_operative_claims(claim: str) -> None:
    """One assertion per claim, because ONE file is exploitable and the others are not.

    `skills/agent-messaging/SKILL.md` is the only claiming file with redundant keywords
    (`SendMessage` x5, scoping evidence x4), so the corpus-wide any-of arm above cannot
    protect it: deleting two of its three operative paragraphs leaves the other two
    matching, and the file still passes. Measured, not assumed — the gutted seed retains
    exactly `recipient, not the transport` and `transport does not excuse you`.

    Split one-per-claim so a failure NAMES the sentence that vanished rather than saying
    the file changed. The cost is real and accepted: rewording one of these four reds this
    test. That is the correct coupling — changing a rule's operative claim should require
    acknowledging the test over it, which is a different act from adding a paragraph of
    rationale, and adding rationale must NOT red.

    Does NOT catch a rule WEAKENED in place (`MUST` -> `SHOULD`, a scope quietly narrowed);
    no predicate here measures that.
    """
    body = _collapsed((PLUGIN_ROOT / "skills" / "agent-messaging" / "SKILL.md").read_text())
    assert claim in body, (
        f"the operative claim {claim!r} is gone from agent-messaging/SKILL.md. Its keywords "
        f"still pass the corpus arm, so nothing else here would have caught this."
    )


@pytest.mark.parametrize(
    ("body", "should_pass"),
    [
        # The ARCHITECT's counterexample: names the tool, still promises enforcement.
        ("The graph is ENFORCED at the API — violations return 403. See SendMessage.", False),
        # A bare name-drop with no claim about policing at all.
        ("Use SendMessage to reach another session.", False),
        # The forms CORE's own files use.
        ("native SendMessage never reaches the server, so no 403 is possible", True),
        ("SendMessage is not enforced by validateMessageRoute()", True),
        ("SendMessage reaches the session with no server in the path", True),
    ],
)
def test_the_not_policed_matcher_rejects_a_bare_name_drop(body: str, should_pass: bool) -> None:
    """Falsifies the matcher, not just the corpus.

    The first case is the one that matters: it is the real body the ARCHITECT found in its
    own persona (ai-maestro#131), and the previous guard — which asserted only that
    `SendMessage` appears — passed it. A file can name the transport and still tell the
    reader every send is checked, which is the entire failure being guarded against.
    """
    assert bool(_NOT_POLICED.search(body)) is should_pass, f"misclassified: {body!r}"


@pytest.mark.parametrize(
    ("rule", "should_flag"),
    [
        ("Write(src/**)", True),
        ("Glob(**/*.ts)", True),
        ("NotebookEdit(nb/**)", True),
        ("Edit(src/**)", False),
        ("Read(src/**)", False),
        ("Bash(git status)", False),
        ("WriteFileTool(x)", False),
    ],
)
def test_permission_rule_matcher_classifies_both_directions(rule: str, should_flag: bool) -> None:
    """Falsifies the matcher, not just the corpus.

    `WriteFileTool(x)` is the load-bearing negative: a substring match on "Write" would
    flag it, and a rule that fires on correct spellings is one people delete.
    """
    assert bool(_WARNING_RULE.match(rule)) is should_flag, f"misclassified: {rule}"
