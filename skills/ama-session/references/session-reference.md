# Session Control — Full Reference

## Table of Contents

- [Authorization matrix](#authorization-matrix)
- [How `queue` actually delivers](#how-queue-actually-delivers)
- [`slash` vs `queue` vs `inject` — the full decision table](#slash-vs-queue-vs-inject--the-full-decision-table)
- [Environment variables the CLI reads](#environment-variables-the-cli-reads)
- [Worked examples](#worked-examples)

---

## Authorization matrix

`queue`, `inject`, `slash`, `answer`, and every `panel` verb (see `ama-panel`)
are `send-command`-class actions. Who may act **on whom**:

| Caller | May act on |
|---|---|
| the human USER | any agent (needs a fresh sudo token) |
| MANAGER | any agent |
| CHIEF-OF-STAFF | agents of its own team only |
| any agent | **itself only** |

So the janitor running inside a MEMBER's session can arm *that* agent and no
other. A fleet-wide command must come from the MANAGER's session, or from
the human user. This is not a gap to route around — an agent that could
enqueue commands into a peer's terminal would have bypassed the whole
governance graph.

**Configuration is a separate, stricter axis.** Even MANAGER cannot use this
skill's verbs to reconfigure an agent's role plugin, extensions, MCP, hooks,
sub-agents, title, or team — those are refused on self for every title
(`ai-maestro-agents-management` is the correct skill, gated by its own
approval rules).

---

## How `queue` actually delivers

Verified end-to-end in the `ai-maestro` repo (TRDD-41FJM8A8):

1. `POST /api/agents/[id]/queue` → `enqueueCommand()` persists the entry to
   `~/.aimaestro/command-queue/<agentId>.json` (atomic write), then calls
   `onQueueEnqueued()`.
2. `onQueueEnqueued()` (`services/agents-core-service.ts`) checks whether a
   session exists. Hibernated + `--wake-first` → wakes the agent
   immediately. Hibernated without it → the entry is simply held.
3. The agent's own hook POSTs `idle_prompt` to the activity route on its
   *next* genuine idle prompt. That calls
   `drainCommandQueueForSession()` (`services/sessions-service.ts`), which
   dequeues FIFO and injects the held command via the same delivery path
   `inject` uses.

**Nothing polls.** The drain is hook-driven, so an idle or hibernated agent
costs nothing while its queue sits empty. This is why "the agent was
asleep" is never a partial-failure outcome for `queue` — only `inject` can
fail that way, because it demands a live pane *right now*.

---

## `slash` vs `queue` vs `inject` — the full decision table

| Situation | Use |
|---|---|
| The command is on the allowlist and you don't need it deferred | `slash` |
| The agent might be busy, mid-turn, or hibernated | `queue` (add `--wake-first` to wake it now) |
| You need synchronous delivery this instant, verified idle | `inject --require-idle` (last resort) |
| The command is not on the allowlist and cannot wait | `inject` — but reconsider whether it truly cannot wait; almost everything can |
| You just want to know if it's safe to interrupt | `state --pane`, then decide |
| The agent is blocked on a permission/`AskUserQuestion` prompt | `read-prompt` then `answer` |

`slash-keys` lists the exact allowlisted command keys — check it before
assuming a command-key exists; do not guess one for `slash` or `queue
--command-key`.

---

## Environment variables the CLI reads

| Var | Used for |
|---|---|
| `AID_AUTH` | the agent's own Bearer token (`export AID_AUTH="$(aid-auth.sh)"`) — every `aimaestro-*` script reads it |
| `AIMAESTRO_SESSION` / `~/.aimaestro/cli-session` | the human's session token (written by `aimaestro-governance.sh login`) |
| `AIMAESTRO_SUDO_TOKEN` | the human caller's fresh sudo token on a strict route (`answer`, `queue`) |
| `AIMAESTRO_API_BASE` | override the API base URL (default: this host) |

Resolution order (first match wins): `AID_AUTH` → `AIMAESTRO_SESSION` →
`~/.aimaestro/cli-session`. An agent's own identity always wins over a
stored human session, so the two never collide.

---

## Worked examples

### Arm a heartbeat on a possibly-hibernated agent

```bash
aimaestro-session.sh queue <agent> --command-key janitor-arm --when idle
# or, to wake it now instead of waiting for it to wake on its own:
aimaestro-session.sh queue <agent> --command-key janitor-arm --when idle --wake-first
```

### Check state before injecting

```bash
STATE=$(aimaestro-session.sh state <agent> --pane --format json 2>/dev/null || aimaestro-session.sh state <agent>)
echo "$STATE" | jq -r '.state // .' 2>/dev/null || echo "$STATE"
# only proceed to inject if idle
aimaestro-session.sh inject <agent> --command "/compact" --require-idle
```

### Answer a pending AskUserQuestion

```bash
aimaestro-session.sh read-prompt <agent>
aimaestro-session.sh answer <agent> --option approve
# or a free-text answer to an elicitation dialog:
aimaestro-session.sh answer <agent> --text "use the staging bucket"
```

### Cancel a queued command you no longer want to fire

```bash
aimaestro-session.sh queue-list <agent>
aimaestro-session.sh queue-cancel <agent> <entryId>
```
