# Session Control — Full Reference

## Table of Contents

- [Authorization matrix](#authorization-matrix)
- [How `queue` actually delivers](#how-queue-actually-delivers)
- [`slash` vs `queue` vs `inject` — the full decision table](#slash-vs-queue-vs-inject--the-full-decision-table)
- [Environment variables the CLI reads](#environment-variables-the-cli-reads)
- [Worked examples](#worked-examples)

---

## Authorization matrix

`queue`, `inject`, `slash`, `state --pane`, and every `panel` verb (see
`ama-panel`) are `send-command`-class actions — they deliver an arbitrary
command, so they express the CALLER's decision. Who may act **on whom**:

| Caller | May act on (`send-command`-class) | May `block-state`/`read-prompt`/`answer` (R42.8) |
|---|---|---|
| the human USER | any agent (needs a fresh sudo-token) | any agent (sudo-token) |
| MANAGER | **itself only** — no title exemption (R42.2) | any agent on the host **except an ASSISTANT**, and only while that agent is BLOCKED |
| CHIEF-OF-STAFF | **itself only** — no title exemption (R42.2) | **its own team only**, same ASSISTANT exclusion, same blocked-only condition |
| any other agent | **itself only** | **itself only** |

The right-hand column is the **R42.8 carve-out** and nothing wider: it
answers a prompt the target itself raised, carries no work, and 409s unless
the target is genuinely blocked. The workflow that governs it —
constraints, escalation cases, the anti-patterns — is the `ama-unblock`
skill. `answer` moved out of the `send-command` column because an answer to
a pending prompt supplies a missing INPUT; it does not author an
instruction.

> **Revised for governance R42 (CRITICAL, IRON, USER-set).** The MANAGER/COS
> rows previously read "any agent" and "agents of its own team" — that was the
> pre-R42 `send-command` model, which R42 **revoked entirely** for the
> cross-agent case (`TRDD-BF3JN4TL`). R42.1 forbids injecting a command,
> keystroke, prompt, or queued input into another agent's session by API, CLI,
> **or tmux**, *to assign, redirect, or perform that agent's work*; R42.2
> states no title is exempt from THAT. To influence a peer, send it a message —
> a message lands in an inbox and the recipient decides; an injected command
> *is* the recipient's own action and bypasses its judgment entirely.
>
> **R42.8 is RATIFIED** — `Explicit (USER — 2026-08-05, ai-maestro#125,
> TRDD-AODXPI5E)`, published in `docs/GOVERNANCE-RULES.md` **v5.3.3** on
> `Emasoft/ai-maestro@governance-rules`. The ratified verbs are **`block-state`,
> `read-prompt` and `answer` ONLY**; `inject`/`slash`/`queue` stay SELF-ONLY for
> every title. The dividing line is **caller decision, not read-vs-write** — the
> two reads carry none. 5.3.2 omitted `block-state` and 5.3.3 corrected it; do
> not "restore" the two-verb list (see `ama-unblock`).
>
> *(On 2026-08-07 this file said R42.8 was a pending proposal. The measurement
> was right — it was absent from every published copy then — but the conclusion
> was not: the grant was real and only publication lagged. An open issue is not
> evidence a rule is unratified.)*
>
> **R42.8 added the single carve-out** shown in the second
> column above: MANAGER/COS may unblock an agent stalled on a prompt, via
> `block-state`/`read-prompt`/`answer` only. It exists because a blocked agent
> cannot read its inbox — messaging reaches an agent at its next turn, and a
> blocked agent has no next turn — so without it a stalled peer stays stalled
> forever. It is not a general cross-agent path: `inject`, `slash` and `queue`
> stay self-only for every title precisely because they could carry work.

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
| `AIMAESTRO_SUDO_TOKEN` | the human caller's fresh sudo-token on a strict route (`answer`, `queue`) |
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
