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


def run_hook(event: dict, home: str) -> None:
    """Drive the hook with one event under the given HOME (real subprocess)."""
    env = os.environ.copy()
    env["HOME"] = home
    proc = subprocess.run(
        ["node", str(HOOK)],
        input=json.dumps({**event, "cwd": CWD}),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )
    # The hook must never hard-fail — it exits 0 even on an internal error.
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"


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


def test_last_error_survives_later_events(home: str) -> None:
    """#58 REGRESSION: status/errorType describe only the CURRENT event, so the next
    event erased them and 'why did this agent stop' became unanswerable a second
    later. The pane cannot answer it either — it is a live tail, so a scrolled-off
    error is gone. lastError must carry through like subagentCount does."""
    run_hook(
        {"hook_event_name": "StopFailure", "error_type": "rate_limit", "error": "429 slow down"},
        home,
    )
    run_hook({"hook_event_name": "Notification", "notification_type": "idle_prompt"}, home)
    run_hook({"hook_event_name": "SessionStart"}, home)
    s = read_state(home)
    assert s["status"] == "active", "status correctly reflects the CURRENT state"
    assert s["lastError"]["type"] == "rate_limit", "but the post-mortem must still be readable"


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
