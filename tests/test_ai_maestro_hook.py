"""Tests for scripts/ai-maestro-hook.cjs — the AMP/AID notification glue.

`ai-maestro-hook.cjs` reads a Claude Code hook event on stdin and writes a
per-cwd state file to ``$HOME/.aimaestro/chat-state/<sha256(cwd)[:16]>.json``.
Exactly as the hook runs in production, these tests drive it end-to-end as a
real Node subprocess (no mocks, per this project's no-mock rule): an isolated
``$HOME`` gives each test its own state dir, and ``PATH`` is emptied so the
hook's fire-and-forget ``aimaestro-hook.sh`` CLI calls fail fast (ENOENT) —
hermetic and fast, no running server required.

Covers two fixes:
  * #21 — the Notification matcher now delivers ``elicitation_dialog`` and
    ``agent_needs_input``; every delivered type must have a real handler.
  * #17 — ``writeState`` must PRESERVE the cumulative ``subagentCount`` across
    interleaved non-subagent events (idle_prompt / permission_prompt) instead
    of dropping it, which used to floor the live counter at 0.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOK = PLUGIN_ROOT / "scripts" / "ai-maestro-hook.cjs"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(
    NODE is None,
    reason="node is required to exercise the ai-maestro hook (no mock substitute)",
)


def run_hook(event: dict, home: Path) -> None:
    """Feed one hook event to the real Node hook with an isolated HOME.

    PATH is emptied so the hook's outbound ``aimaestro-hook.sh`` calls ENOENT
    immediately (fire-and-forget, error-swallowing) — the state file is written
    synchronously before that, so the isolation cannot race the assertion.
    """
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["PATH"] = ""  # no aimaestro-hook.sh on PATH → CLI calls fail fast
    # Steady-state precondition: the chat-state dir exists (created by an earlier
    # session / the installer in real deployments). The hook's debugLog() runs
    # before writeState() creates the dir, so a truly cold dir would crash it —
    # a separate latent defect, out of scope for these fixes.
    (home / ".aimaestro" / "chat-state").mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [NODE, str(HOOK)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def read_state(home: Path, cwd: str) -> dict:
    cwd_hash = hashlib.sha256(cwd.encode()).hexdigest()[:16]
    state_file = home / ".aimaestro" / "chat-state" / f"{cwd_hash}.json"
    return json.loads(state_file.read_text())


def test_subagent_count_survives_interleaved_idle_prompt(tmp_path: Path) -> None:
    """#17: an idle_prompt Notification between SubagentStart and SubagentStop
    must NOT drop subagentCount; the Stop then decrements from the true base."""
    home = tmp_path / "home"
    home.mkdir()
    cwd = "/tmp/aim_hook_test_cwd_17"

    run_hook({"hook_event_name": "SubagentStart", "cwd": cwd, "agent_id": "a1"}, home)
    run_hook({"hook_event_name": "SubagentStart", "cwd": cwd, "agent_id": "a2"}, home)
    assert read_state(home, cwd)["subagentCount"] == 2

    # The corrupting event: a Notification handler that omits subagentCount.
    run_hook(
        {"hook_event_name": "Notification", "notification_type": "idle_prompt", "cwd": cwd},
        home,
    )
    mid = read_state(home, cwd)
    assert mid["status"] == "waiting_for_input"
    assert mid["subagentCount"] == 2, "idle_prompt dropped the subagent counter (#17)"

    # One subagent stops → 2 - 1 = 1. Pre-fix this floored to 0 (max(0, 0-1)).
    run_hook({"hook_event_name": "SubagentStop", "cwd": cwd, "agent_id": "a1"}, home)
    end = read_state(home, cwd)
    assert end["subagentCount"] == 1
    assert end["status"] == "subagents_running"


def test_elicitation_and_needs_input_have_handlers(tmp_path: Path) -> None:
    """#21: elicitation_dialog and agent_needs_input must each write a real
    blocking state (not be silently dropped by a matcher without a handler)."""
    home = tmp_path / "home"
    home.mkdir()
    cwd = "/tmp/aim_hook_test_cwd_21"

    run_hook(
        {"hook_event_name": "Notification", "notification_type": "elicitation_dialog", "cwd": cwd},
        home,
    )
    elic = read_state(home, cwd)
    assert elic["status"] == "elicitation"
    assert elic["notificationType"] == "elicitation_dialog"

    run_hook(
        {"hook_event_name": "Notification", "notification_type": "agent_needs_input", "cwd": cwd},
        home,
    )
    needs = read_state(home, cwd)
    assert needs["status"] == "needs_input"
    assert needs["notificationType"] == "agent_needs_input"


def test_notification_matcher_covers_every_handled_type() -> None:
    """#21: hooks.json's Notification matcher must deliver every type the
    handler branches for — a handled type absent from the matcher never fires."""
    hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text())
    matcher = hooks["hooks"]["Notification"][0]["matcher"]
    delivered = set(matcher.split("|"))
    required = {"idle_prompt", "permission_prompt", "elicitation_dialog", "agent_needs_input"}
    assert required <= delivered, f"matcher {matcher!r} is missing {required - delivered}"
