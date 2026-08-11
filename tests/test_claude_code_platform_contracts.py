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
    unscoped = [p.relative_to(PLUGIN_ROOT).as_posix() for p in claims if "SendMessage" not in p.read_text()]
    assert not unscoped, (
        "these assert a 403 enforces the comm graph without naming the transport that "
        f"cannot return one (Claude Code 2.1.224): {unscoped}"
    )


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
