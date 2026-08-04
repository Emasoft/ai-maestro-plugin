---
name: ama-continuity
user-invocable: false
description: "Read this host's rate-limit and cache health, and keep the agent's own session alive, via the frozen aimaestro-continuity.sh CLI — the 5h/7d window percentages, cache TTL, and a next_action recommendation, plus idempotent self-resume and self-restart. Use before launching a long batch or agent fan-out, when a session may have stalled on a rate limit, or to decide whether there is budget to continue. Trigger with 'how much of my rate-limit window is left', 'am I about to hit the 5h cap', 'make sure I'm resumed', 'restart my own session'. R42 self-only. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-continuity.sh:*), Bash(aid-auth.sh:*), Bash(jq:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-continuity — window health and self-resume

## Overview

`ama-continuity` wraps the frozen `aimaestro-continuity.sh` CLI: the surface an
agent uses to answer *"do I have budget to start this, and am I still alive?"*
It reports the account's rate-limit windows and can resume or restart the
**caller's own** session. It never calls the AI Maestro API directly.

## R42 — these verbs are SELF-ONLY by construction

`status` and `ensure-resume` take the **caller's own** `<self>` (its agent UUID,
or a name/alias). `restart-self` takes **no target at all** — the server derives
it from the caller's AID. There is no "restart that other agent" here, and that
is deliberate: a cross-agent restart is a denial-of-service primitive.

## What `status` actually returns

Five fields, **metadata only — no token is returned**:

| field | meaning |
|---|---|
| `account_healthy` | whether the account is currently usable |
| `window_5h_pct` | how much of the 5-hour window is consumed |
| `window_7d_pct` | how much of the 7-day window is consumed |
| `cache_ttl_minutes` | the prompt-cache TTL in force |
| `next_action` | the CLI's own recommendation |

**Read `window_7d_pct` before a fan-out, not after.** The 7-day window is the one
that strands long work: a batch that starts at 90% and needs 20% will die
mid-flight, and the cost of the abandoned half is already spent. `next_action` is
a recommendation, not a gate — you are still the one deciding.

## Prerequisites

- AI Maestro running; `aimaestro-continuity.sh` on `PATH` (installed by
  `install-messaging.sh`; re-run it if missing).
- **Agent callers must export `AID_AUTH`**: `export AID_AUTH="$(aid-auth.sh)"`.

## Instructions

1. **Before a long or fan-out job**, check the windows:

   ```bash
   aimaestro-continuity.sh status "$SELF" | jq '.'
   ```

   Decide from `window_5h_pct` / `window_7d_pct` whether the work fits. If it
   does not, shrink the batch — do not start it and hope.

2. **Idempotent self-resume** — safe to call unconditionally; a no-op when the
   agent is already live:

   ```bash
   aimaestro-continuity.sh ensure-resume "$SELF"
   ```

3. **Self-restart**, only when a resume is not enough:

   ```bash
   aimaestro-continuity.sh restart-self
   aimaestro-continuity.sh restart-self --force   # override the running-subagents refusal
   ```

   The bare form **refuses while this agent still has running subagents** — that
   refusal is the feature. `--force` discards their in-flight work, so use it when
   you know the subagents are stuck, not to skip past an inconvenient error.

### Quick CLI Reference

| Subcommand | Target | Notes |
|---|---|---|
| `status <self>` | own account | 5 fields, metadata only, no token |
| `ensure-resume <self>` | own session | idempotent — no-op if already live |
| `restart-self [--force]` | own session (implicit) | refuses with running subagents unless `--force` |

## Output

JSON on STDOUT (pipe to `jq`). `status` returns the five fields above;
`ensure-resume` reports whether it acted or was a no-op.

## Error Handling

| Symptom | Likely cause |
|---|---|
| auth/401-shaped failure | `AID_AUTH` not exported |
| `restart-self` refuses | this agent still has running subagents — stop them, or `--force` if they are genuinely stuck |
| `status` fields look stale | the reading is per-account for THIS host; another host's sessions are not in it |

## Examples

<example>
Decide whether a 40-agent fan-out fits in the remaining budget.
→ `aimaestro-continuity.sh status "$SELF" | jq '.window_7d_pct, .next_action'` —
if the 7-day window is already high, cut the batch rather than starting it.
</example>

<example>
A heartbeat suspects this session stalled after a rate limit.
→ `aimaestro-continuity.sh ensure-resume "$SELF"` — idempotent, so it is safe to
call even when nothing is wrong.
</example>

## Scope

The caller's OWN window health and session liveness. Another agent's lifecycle is
`ai-maestro-agents-management`; terminal/state control is `ama-session`.

## Use also

- `Skill(skill: "ama-session")` — drive this agent's terminal once it is live.
- `Skill(skill: "agent-identity")` — where `AID_AUTH` comes from.
