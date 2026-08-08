"""Tests for the ai-maestro-hook.cjs Claude Code event hook.

`scripts/ai-maestro-hook.cjs` reads a hook event on stdin and writes agent
chat-state to ~/.aimaestro/chat-state/<cwd-hash>.json. Exactly as it runs in
production, these tests drive it end-to-end as a real Node subprocess (no mocks,
per this project's no-mock rule) under a throwaway HOME, then assert the
persisted state.

Covers the regressions fixed alongside #17/#20/#21:
 - #17: subagentCount is a persistent counter; a state write that omits it
   (idle_prompt / permission_prompt) must carry the prior value through, while
   a handler that passes an explicit value (SessionStart → 0) still wins.
 - #20: AskUserQuestion is captured on PreToolUse and cleared on PostToolUse.
 - #21: an elicitation_dialog notification is handled (status 'elicitation').
 - debugLog hardening: the very first event on a fresh HOME (no ~/.aimaestro
   yet) must still write state instead of crashing on ENOENT.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOK = PLUGIN_ROOT / "scripts" / "ai-maestro-hook.cjs"
CWD = "/tmp/ai_maestro_hook_test_cwd"

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None,
    reason="node is required to exercise the ai-maestro-hook (no mock substitute)",
)


def _state_path(home: str, cwd: str = CWD) -> Path:
    cwd_hash = hashlib.sha256(cwd.encode()).hexdigest()[:16]
    return Path(home) / ".aimaestro" / "chat-state" / f"{cwd_hash}.json"


def run_hook(event: dict, home: str, cwd: str = CWD) -> None:
    """Drive the hook with one event under the given HOME (real subprocess)."""
    env = os.environ.copy()
    env["HOME"] = home
    proc = subprocess.run(
        ["node", str(HOOK)],
        input=json.dumps({**event, "cwd": cwd}),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )
    # The hook must never hard-fail — it exits 0 even on an internal error.
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"


def run_hooks_concurrently(events: list[dict], home: str, cwd: str = CWD) -> None:
    """Fire every event as a REAL concurrent process, maximally overlapped.

    Every process is spawned BEFORE any is awaited. Spawning-and-waiting one at a
    time would serialize them and the test would pass against the racy code —
    which is the only way this suite can lie about #61.
    """
    payloads = [json.dumps({**event, "cwd": cwd}) for event in events]
    procs = _spawn_hooks(home, len(events))
    _feed_and_wait(procs, payloads)


def _spawn_hooks(home: str, count: int) -> list[subprocess.Popen[str]]:
    env = os.environ.copy()
    env["HOME"] = home
    return [
        subprocess.Popen(
            ["node", str(HOOK)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        for _ in range(count)
    ]


def _feed_and_wait(procs: list[subprocess.Popen[str]], payloads: list[str]) -> None:
    for proc, payload in zip(procs, payloads):
        assert proc.stdin is not None
        proc.stdin.write(payload)
        proc.stdin.close()
    for proc in procs:
        assert proc.stdout is not None and proc.stderr is not None
        assert proc.wait(timeout=60) == 0, f"hook exited {proc.returncode}: {proc.stderr.read()}"
        proc.stdout.close()
        proc.stderr.close()


def read_debug_log(home: str) -> str:
    log = Path(home) / ".aimaestro" / "chat-state" / "hook-debug.log"
    return log.read_text() if log.exists() else ""


def read_state(home: str, cwd: str = CWD) -> dict:
    return json.loads(_state_path(home, cwd).read_text())


@pytest.fixture()
def home(tmp_path: Path) -> str:
    return str(tmp_path)


def test_first_event_on_fresh_home_writes_state(home: str) -> None:
    """A fresh HOME has no ~/.aimaestro; the first event must still write state
    (debugLog used to crash on ENOENT before any dir existed)."""
    run_hook({"hook_event_name": "SessionStart"}, home)
    assert _state_path(home).exists()
    assert read_state(home)["status"] == "active"


def test_subagent_count_preserved_across_idle_prompt(home: str) -> None:
    """#17: idle_prompt omits subagentCount → it must carry the prior value."""
    run_hook({"hook_event_name": "SubagentStart", "agent_id": "a1"}, home)
    run_hook({"hook_event_name": "Notification", "notification_type": "idle_prompt"}, home)
    s = read_state(home)
    assert s["status"] == "waiting_for_input"
    assert s["subagentCount"] == 1


def test_subagent_count_preserved_across_permission_prompt(home: str) -> None:
    """#17: permission_prompt also must not drop the counter."""
    run_hook({"hook_event_name": "SubagentStart", "agent_id": "a1"}, home)
    run_hook({"hook_event_name": "Notification", "notification_type": "permission_prompt"}, home)
    assert read_state(home)["subagentCount"] == 1


def test_explicit_subagent_count_still_wins(home: str) -> None:
    """A handler that RESETS the counter (SessionStart → 0) wins over the carry."""
    run_hook({"hook_event_name": "SubagentStart", "agent_id": "a1"}, home)
    run_hook({"hook_event_name": "SessionStart"}, home)
    assert read_state(home)["subagentCount"] == 0


def test_askuserquestion_captured_on_pretooluse(home: str) -> None:
    """#20: PreToolUse AskUserQuestion records the question so the dashboard
    shows the agent waiting, not idle."""
    run_hook(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": "Pick one?", "options": [{"label": "A"}]}]},
        },
        home,
    )
    s = read_state(home)
    assert s["status"] == "waiting_for_input"
    assert s["notificationType"] == "question"
    assert len(s["questions"]) == 1
    assert s["message"] == "Pick one?"


def test_askuserquestion_cleared_on_posttooluse(home: str) -> None:
    """#20: the answer returning clears the question-blocked state."""
    run_hook(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": "Pick one?"}]},
        },
        home,
    )
    run_hook({"hook_event_name": "PostToolUse", "tool_name": "AskUserQuestion"}, home)
    s = read_state(home)
    assert s["status"] in ("active", "subagents_running")
    assert s.get("notificationType") is None


def test_askuserquestion_choices_normalized_to_key_label(home: str) -> None:
    """#59: the question's choices are stored in the same {key,label} shape the
    permission path emits, so one consumer reads both prompt kinds alike."""
    run_hook(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "AskUserQuestion",
            "tool_input": {
                "questions": [
                    {
                        "question": "Which bucket?",
                        "options": [
                            {"label": "staging", "description": "safe"},
                            {"label": "prod", "description": "live"},
                        ],
                    }
                ]
            },
        },
        home,
    )
    opts = read_state(home)["options"]
    assert [o["key"] for o in opts] == ["1", "2"]
    assert [o["label"] for o in opts] == ["staging", "prod"]


def test_permission_prompt_does_not_clobber_a_pending_question(home: str) -> None:
    """#59 REGRESSION: Claude Code emits Notification(permission_prompt) for an
    AskUserQuestion block too. That handler used to wipe `questions` and downgrade
    the type, so read-prompt answered null for the one prompt shape that blocks an
    agent forever (measured 0 questions captured across 419 live state files)."""
    run_hook(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": "Which bucket?", "options": [{"label": "staging"}]}]},
        },
        home,
    )
    run_hook({"hook_event_name": "Notification", "notification_type": "permission_prompt"}, home)
    s = read_state(home)
    assert s["notificationType"] == "question", "the specific classification must survive the generic one"
    assert len(s["questions"]) == 1
    assert s["message"] == "Which bucket?"
    assert len(s["options"]) == 1


def test_idle_prompt_does_not_clobber_a_pending_question(home: str) -> None:
    """#59 review: the clobber fix was applied only to the permission_prompt branch. An
    unanswered AskUserQuestion IS a session sitting without input, so the timer-driven
    idle_prompt fires on exactly the blocked agent — and relabelling it 'idle_prompt',
    the one value every consumer reads as healthy, made a MANAGER's fleet sweep skip it."""
    run_hook(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": "Which bucket?", "options": [{"label": "staging"}]}]},
        },
        home,
    )
    run_hook({"hook_event_name": "Notification", "notification_type": "idle_prompt"}, home)
    s = read_state(home)
    assert s["notificationType"] == "question", "a blocked agent must not be relabelled idle"
    assert len(s["questions"]) == 1


def test_pending_question_is_bounded_by_session(home: str) -> None:
    """#59 review: a question cancelled with ESC emits no PostToolUse, so its record can
    linger. Unbounded, a later unrelated permission prompt would inherit it and republish
    its choices — and a MANAGER answering the menu it recognised would be answering the
    REAL prompt underneath, granting an unrelated permission."""
    run_hook(
        {
            "hook_event_name": "PreToolUse",
            "session_id": "session-A",
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": "Which bucket?", "options": [{"label": "staging"}]}]},
        },
        home,
    )
    # A DIFFERENT session's permission prompt must not inherit session-A's question.
    run_hook(
        {"hook_event_name": "Notification", "session_id": "session-B", "notification_type": "permission_prompt"},
        home,
    )
    s = read_state(home)
    assert s["notificationType"] == "permission_prompt", "a stale question must not cross sessions"
    assert not s.get("questions")


def test_question_state_carries_description_and_count(home: str) -> None:
    """#59 review: the question write dropped `description` (which the permission write it
    replaces always emitted), rendering a question-blocked agent as blocked-with-no-reason;
    and `options` describes questions[0] only, so consumers need the count to know."""
    run_hook(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "AskUserQuestion",
            "tool_input": {
                "questions": [
                    {"question": "Which bucket?", "options": [{"label": "staging"}]},
                    {"question": "Rerun tests?", "options": [{"label": "yes"}]},
                ]
            },
        },
        home,
    )
    s = read_state(home)
    assert s["description"] == "Which bucket?"
    assert s["questionCount"] == 2, "a caller must be able to tell one question from four"
    assert len(s["options"]) == 1, "options describe the FIRST question only"

    # …and both survive the permission_prompt that follows.
    run_hook({"hook_event_name": "Notification", "notification_type": "permission_prompt"}, home)
    s = read_state(home)
    assert s["description"] == "Which bucket?"
    assert s["questionCount"] == 2


def test_pending_question_survives_a_long_block(home: str) -> None:
    """#59: a blocked agent stays blocked for HOURS (17h observed), so the
    question carry-through must carry NO age bound — a 10s window would re-drop
    the question for exactly the long-block case the fix exists for."""
    run_hook(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": "Which bucket?"}]},
        },
        home,
    )
    # Backdate the record 17 hours, as a real long-blocked agent's would be.
    path = _state_path(home)
    state = json.loads(path.read_text())
    stale = datetime.now(timezone.utc) - timedelta(hours=17)
    state["updatedAt"] = stale.isoformat().replace("+00:00", "Z")
    path.write_text(json.dumps(state))

    run_hook({"hook_event_name": "Notification", "notification_type": "permission_prompt"}, home)
    s = read_state(home)
    assert s["notificationType"] == "question"
    assert len(s["questions"]) == 1


def test_genuine_permission_prompt_is_not_hijacked_after_an_answer(home: str) -> None:
    """#59 guard on the guard: once the question is answered, a real permission
    prompt must classify as permission_prompt — the question carry-through must
    not shadow later prompts."""
    run_hook(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": "Which bucket?"}]},
        },
        home,
    )
    run_hook({"hook_event_name": "PostToolUse", "tool_name": "AskUserQuestion"}, home)
    run_hook(
        {"hook_event_name": "PermissionRequest", "tool_name": "Bash", "tool_input": {"command": "ls"}},
        home,
    )
    run_hook({"hook_event_name": "Notification", "notification_type": "permission_prompt"}, home)
    s = read_state(home)
    assert s["notificationType"] == "permission_prompt"
    assert "questions" not in s or not s["questions"]


def test_stopfailure_records_a_durable_last_error(home: str) -> None:
    """#58: StopFailure writes a lastError record carrying type, message and time."""
    run_hook(
        {"hook_event_name": "StopFailure", "error_type": "rate_limit", "error": "429 slow down"},
        home,
    )
    s = read_state(home)
    assert s["status"] == "error"
    assert s["lastError"]["type"] == "rate_limit"
    assert s["lastError"]["message"] == "429 slow down"
    assert s["lastError"]["at"]


def test_last_error_survives_later_events_within_a_session(home: str) -> None:
    """#58 REGRESSION: status/errorType describe only the CURRENT event, so the next
    event erased them and 'why did this agent stop' became unanswerable a second
    later. The pane cannot answer it either — it is a live tail, so a scrolled-off
    error is gone. lastError must carry through like subagentCount does."""
    run_hook(
        {"hook_event_name": "StopFailure", "error_type": "rate_limit", "error": "429 slow down"},
        home,
    )
    run_hook({"hook_event_name": "Notification", "notification_type": "idle_prompt"}, home)
    run_hook({"hook_event_name": "Stop"}, home)
    s = read_state(home)
    assert s["status"] in ("idle", "subagents_running"), "status reflects the CURRENT state"
    assert s["lastError"]["type"] == "rate_limit", "but the post-mortem must still be readable"


def test_session_start_clears_last_error(home: str) -> None:
    """Review of #58: with nothing ever clearing it, one 429 made every later record for
    this cwd report a rate_limit FOREVER, across every future session — a supervisor
    would read a weeks-old error as the current cause. A new session is a new life."""
    run_hook(
        {"hook_event_name": "StopFailure", "error_type": "rate_limit", "error": "429 slow down"},
        home,
    )
    assert read_state(home)["lastError"]["type"] == "rate_limit"
    run_hook({"hook_event_name": "SessionStart"}, home)
    assert read_state(home)["lastError"] is None, "a new session must not inherit the old stop reason"


def test_state_is_stamped_with_the_writing_plugin_version(home: str) -> None:
    """#60: consumers read state written by whatever version each agent has installed.
    Without a stamp a missing field is ambiguous in the direction that matters — 'no
    question pending' vs 'a version that clobbered it' (#59) demand opposite actions."""
    manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
    run_hook({"hook_event_name": "SessionStart"}, home)
    assert read_state(home)["writerVersion"] == manifest["version"]


def test_no_last_error_on_a_clean_session(home: str) -> None:
    """A healthy session reports lastError null — never a stale or invented one."""
    run_hook({"hook_event_name": "SessionStart"}, home)
    assert read_state(home)["lastError"] is None


def test_pretooluse_non_question_tool_is_ignored(home: str) -> None:
    """The PreToolUse matcher is AskUserQuestion-only; a stray non-question tool
    must not write a question state."""
    run_hook({"hook_event_name": "SessionStart"}, home)
    run_hook({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "ls"}}, home)
    # State is unchanged from SessionStart (no 'question' notificationType).
    assert read_state(home).get("notificationType") is None


def test_elicitation_dialog_handled(home: str) -> None:
    """#21: an elicitation_dialog notification is recorded (the hooks.json
    matcher was widened so CC actually delivers it)."""
    run_hook({"hook_event_name": "Notification", "notification_type": "elicitation_dialog"}, home)
    assert read_state(home)["status"] == "elicitation"


def test_agent_needs_input_marks_waiting_and_preserves_count(home: str) -> None:
    """CC 2.1.198: a background agent that blocks on input fires the
    agent_needs_input notification — it must surface as waiting_for_input (so a
    background AMP agent isn't shown idle) and carry the subagent counter."""
    run_hook({"hook_event_name": "SubagentStart", "agent_id": "a1"}, home)
    run_hook({"hook_event_name": "Notification", "notification_type": "agent_needs_input"}, home)
    s = read_state(home)
    assert s["status"] == "waiting_for_input"
    assert s["notificationType"] == "agent_needs_input"
    assert s["subagentCount"] == 1


def test_agent_completed_returns_to_idle(home: str) -> None:
    """CC 2.1.198: agent_completed flips a previously-blocked agent back to idle
    (mirrors Stop), instead of leaving a stale waiting_for_input state."""
    run_hook({"hook_event_name": "Notification", "notification_type": "agent_needs_input"}, home)
    run_hook({"hook_event_name": "Notification", "notification_type": "agent_completed"}, home)
    assert read_state(home)["status"] == "idle"


FANOUT = 16


def test_concurrent_subagent_starts_do_not_lose_updates(home: str) -> None:
    """#61: 16 simultaneous SubagentStarts must leave the counter at exactly 16.

    Each start is `read count, +1, write` in its OWN process. rename(2) makes the
    write atomic and does nothing for the read-then-write sequence, so before the
    lock two starts both read 5, both wrote 6, and the counter stayed 1 low
    forever — nothing recomputes it from truth, so a fan-out compounds the loss.
    Measured 5/5 undercount at this exact fan-out (15, 11, 14, 15, 13).
    """
    run_hooks_concurrently(
        [{"hook_event_name": "SubagentStart", "agent_id": f"a{i}"} for i in range(FANOUT)],
        home,
    )
    assert read_state(home)["subagentCount"] == FANOUT


def test_concurrent_stops_keep_the_restart_gate_shut_while_subagents_run(home: str) -> None:
    """#61's dangerous half: an undercount opens the restart gate on a busy agent.

    12 of 16 subagents finish; 4 are still working. The counter must read 4 and
    the status must stay `subagents_running`. Before the lock this reached 0 and
    flipped to `active` in 2 of 3 trials — and `active` with a zero count is the
    precondition for restart/autoContinue, the interlock governance R42.7(c)
    leans on. Asserting the STATUS as well as the count is deliberate: the count
    is the bug, the status is the harm.
    """
    run_hooks_concurrently(
        [{"hook_event_name": "SubagentStart", "agent_id": f"a{i}"} for i in range(FANOUT)],
        home,
    )
    run_hooks_concurrently(
        [{"hook_event_name": "SubagentStop", "agent_id": f"a{i}"} for i in range(12)],
        home,
    )
    s = read_state(home)
    assert s["subagentCount"] == 4
    assert s["status"] == "subagents_running"


def test_the_lock_is_actually_held_under_fanout(home: str) -> None:
    """The two tests above are only meaningful if the LOCK produced the result.

    withStateLock proceeds unlocked on deadline — by design, because a hook that
    can wedge is worse than the race it closes. But that fallback IS the old racy
    path, so a green count could equally mean "timed out and got lucky". The
    timeout logs `state_lock_timeout`; at this fan-out it must never appear.

    Falsify by dropping LOCK_TIMEOUT_MS to ~0: this reddens while the counts above
    may well stay green, which is exactly the confusion it exists to prevent.
    """
    run_hooks_concurrently(
        [{"hook_event_name": "SubagentStart", "agent_id": f"a{i}"} for i in range(FANOUT)],
        home,
    )
    assert "state_lock_timeout" not in read_debug_log(home)


def test_index_survives_concurrent_writers_from_different_cwds(home: str) -> None:
    """index.json is machine-global, so the per-cwd lock does not protect it.

    Every cwd on the host writes this one file, and it had neither a lock nor the
    tmp+rename the state file has: a lost entry reads downstream as "that agent
    has no state" rather than as corruption, and a torn write fails the parse for
    every agent at once.
    """
    cwds = [f"/tmp/ai_maestro_hook_index_{i}" for i in range(FANOUT)]
    _feed_and_wait(
        _spawn_hooks(home, len(cwds)),
        [json.dumps({"hook_event_name": "SessionStart", "cwd": cwd}) for cwd in cwds],
    )
    index = json.loads((Path(home) / ".aimaestro" / "chat-state" / "index.json").read_text())
    assert set(index) == set(cwds), f"lost {sorted(set(cwds) - set(index))}"


def test_notification_matcher_covers_every_handled_type() -> None:
    """#21 structural invariant (ported from PR #28): hooks.json's Notification
    matcher must deliver every type the handler branches for — a handled type
    absent from the matcher is unreachable dead code."""
    hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text())
    matcher = hooks["hooks"]["Notification"][0]["matcher"]
    delivered = set(matcher.split("|"))
    required = {
        "idle_prompt",
        "permission_prompt",
        "elicitation_dialog",
        "agent_needs_input",
        "agent_completed",
    }
    assert required <= delivered, f"matcher {matcher!r} is missing {required - delivered}"
