---
name: ama-session
user-invocable: false
description: "Drive an agent's own terminal and read its own activity state via the frozen aimaestro-session.sh CLI — send or enqueue an allowlisted slash command (works even while busy/hibernated), type raw text into a live pane, read the 5-state activity, and read/answer a pending permission or AskUserQuestion prompt. Use when an agent must act on itself: arm its janitor heartbeat, answer a pending prompt, check if idle/busy, or queue work for later. Trigger with 'queue a command for when I'm idle', 'answer my pending prompt'. Not for reconfiguring an agent (role/plugin/team) — that is ai-maestro-agents-management. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-session.sh:*), Bash(jq:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-session — drive an agent's own terminal + read its own state

## Overview

`ama-session` wraps the frozen `aimaestro-session.sh` CLI (Tier A, §2.1 of
`SCRIPT-MANIFEST.md`): the surface an agent uses to act on **its own** tmux
pane and read **its own** activity state. It never talks to the AI Maestro
API directly — the CLI resolves the API base and the caller's identity
internally.

**Five things this skill can do:** send an allowlisted slash command, queue a
command for the agent's next safe idle prompt, inject raw text into a live
pane, read the agent's current activity state, and read/answer a pending
permission or `AskUserQuestion` prompt.

## The safety-ordered verb preference — read this before picking one

When you need another turn of work to happen in an agent's session, pick the
**first** of these that fits, in this order. Do not reach for a later one
just because it is more familiar:

1. **`slash <agent> <command-key>`** — send an **allowlisted** slash command
   (`compact`, `reload-plugins`, `janitor-arm`, …). Safest: the command-key is
   validated against a fixed allowlist server-side, so this can never inject
   arbitrary text.
2. **`queue <agent> --command-key <key> [--wake-first]`** (or
   `--command "<text>"`) — **the answer to "the agent is busy / mid-turn /
   hibernated."** The command is persisted server-side and fires at the
   agent's next **genuine idle prompt** (the subagent exit-gate must also be
   satisfied) — never mid-turn, never dropped. Add `--wake-first` to wake a
   hibernated agent immediately instead of waiting for someone else to; omit
   it and the command still fires the moment that agent next wakes on its
   own. This is why arming something on an agent **always succeeds** —
   "armed now" or "armed later," never "partially failed because it was
   asleep."
3. **`inject <agent> --command "<text>" [--no-newline] [--require-idle]`** —
   **the most dangerous verb in this set.** It types raw text into a *live*
   pane, which can interrupt an agent mid-turn. It is not sudo-gated the way
   `queue` is (tracked upstream as `ai-maestro#54` for reclassification).
   Use it only when you specifically need synchronous, immediate delivery
   and have confirmed (via `state`) that the pane is actually idle —
   `--require-idle` enforces that check CLI-side. **Never present this as
   the default path; a skill/agent that reaches for `inject` first will get
   itself (or another agent) interrupted mid-turn.**

Monitoring and unblocking a pending prompt sit outside that ordering — they
are read/answer operations, not "make something happen next" operations:

- **`state <agent> [--pane]`** — the agent's live 5-state activity
  (working / idle / waiting-permission / waiting-elicitation / hibernated,
  roughly — read the CLI's own output for the exact vocabulary).
- **`read-prompt <agent>`** — read a pending permission prompt or
  `AskUserQuestion` menu, if one is blocking the agent.
- **`answer <agent> --option <key> | --text "<answer>"`** — answer that
  pending prompt.
- **`slash-keys`** (no agent argument) — list the allowlisted command keys
  `slash` accepts.
- **`queue-list <agent>`** / **`queue-cancel <agent> <entryId>`** — inspect
  or cancel a still-pending queued command (FIFO).

## The authorization rule — READ THIS BEFORE TARGETING ANY `<agent>`

Since `TRDD-D3RP7KQZ`: **an agent may drive its own surface; it may never
reconfigure itself.** Every verb in this skill acts on the agent's **own**
id by default (inferred from the environment). Targeting **another** agent
requires **MANAGER** (any agent) or **CHIEF-OF-STAFF** (agents of its own
team only) — see the authorization table in
[references/session-reference.md](references/session-reference.md).
**Nothing in this skill ever reconfigures anything** — role, plugin, team,
MCP, hooks, sub-agents, and title are refused on self for every title,
MANAGER included; that is `ai-maestro-agents-management`'s domain (and it
too is self-refused for configuration).

**Strict vs non-strict** (who can call what, and how they authenticate):
`answer` and `queue` are **strict** — an agent authenticates by AID + title,
a human needs a fresh sudo-token. `inject`, `slash`, `slash-keys`, `state`,
`read-prompt`, `queue-list`, `queue-cancel` are **non-strict**.

## Prerequisites

- AI Maestro running; `aimaestro-session.sh` on `PATH` (installed by
  `install-messaging.sh`, which copies `scripts/*.sh` by glob — re-run it if
  the script is missing).
- The CLI resolves your agent identity + bearer token internally — no
  `Authorization` header to set by hand.
- `jq` for parsing JSON output.

## Instructions

1. **Identify what you actually need**: a fire-and-forget command (→ `slash`
   or `queue`), synchronous text injection (→ `inject`, last resort), or a
   read/answer of a pending prompt (→ `state` / `read-prompt` / `answer`).
2. For a command, follow the preference order above — try `slash` first; if
   the command-key you need is not allowlisted, use `queue`; only use
   `inject` when you have a specific reason `queue` will not do (and you
   have verified idleness).
3. Before injecting, check state:

   ```bash
   aimaestro-session.sh state "$(aimaestro-agent.sh resolve --cwd .)" --pane
   ```

4. Send / enqueue / inject:

   ```bash
   aimaestro-session.sh slash <agent> janitor-arm
   aimaestro-session.sh queue <agent> --command-key janitor-arm --when idle --wake-first
   aimaestro-session.sh inject <agent> --command "/compact" --require-idle
   ```

5. To unblock yourself when waiting on a permission prompt or
   `AskUserQuestion`:

   ```bash
   aimaestro-session.sh read-prompt <agent>
   aimaestro-session.sh answer <agent> --option approve
   aimaestro-session.sh answer <agent> --text "use the staging bucket"
   ```

6. To inspect or cancel a queued command:

   ```bash
   aimaestro-session.sh queue-list <agent>
   aimaestro-session.sh queue-cancel <agent> <entryId>
   ```

### Quick CLI Reference

| Subcommand | Flags | Verb class |
|---|---|---|
| `slash <agent> <command-key>` | — | non-strict, allowlisted |
| `slash-keys` | — (no agent) | non-strict |
| `queue <agent>` | `--command "<text>"` \| `--command-key <key>`; `--when idle\|online\|now-if-idle-else-queue`; `--wake-first` | **strict** |
| `queue-list <agent>` | — | non-strict |
| `queue-cancel <agent> <entryId>` | — | non-strict |
| `inject <agent> --command "<text>"` | `--no-newline`, `--require-idle` | non-strict, but the most dangerous |
| `state <agent>` | `--pane` | non-strict |
| `read-prompt <agent>` | — | non-strict |
| `answer <agent>` | `--option <key>` \| `--text "<answer>"` | **strict** |

## Output

Each subcommand prints its result on STDOUT (JSON where noted — pipe to
`jq`); errors go to STDERR with a non-zero exit code. `queue` returns the
enqueued entry id (needed for `queue-cancel`).

## Error Handling

| Symptom | Likely cause |
|---|---|
| 403 targeting another agent | you are not MANAGER, and not that agent's own-team COS |
| 403 on any verb attempting self-reconfiguration | not this skill's job — configuration is refused on self for every title |
| `queue` accepted but nothing ran yet | expected — it fires at the next genuine idle prompt, not immediately (unless `--wake-first` on a hibernated agent) |
| `inject` silently did nothing / landed mid-output | you skipped the `state` check; re-run with `--require-idle` |
| 401 from a human terminal | there is no USER auth path in the script layer yet (`Emasoft/ai-maestro#55`) — this skill is agent-facing |

## Examples

<example>
Arm the janitor heartbeat on an agent, whether it's live, busy, or asleep.
→ `aimaestro-session.sh queue <agent> --command-key janitor-arm --when idle`
(add `--wake-first` to arm it right now instead of waiting for it to wake on
its own). Delivery is eventual, never conditional — "armed now" or "armed
later," never "failed because it was asleep."
</example>

<example>
An agent is blocked on its own pending permission prompt.
→ `aimaestro-session.sh read-prompt <self>` to see the menu, then
`aimaestro-session.sh answer <self> --option approve` to clear it.
</example>

<example>
Check whether an agent is safe to interrupt before injecting text.
→ `aimaestro-session.sh state <agent> --pane` first; only `inject` with
`--require-idle` if it reports idle.
</example>

## Scope

Drives an agent's **own** terminal/state, or another agent's when the caller
is MANAGER (any) / COS (own team). Never reconfigures an agent (role,
plugin, team, MCP, hooks, sub-agents, title) — that is
`ai-maestro-agents-management`, refused on self regardless of title. Driving
the HTML side panel is `ama-panel`. Server-mediated TRDD search/read is
`ama-trdd-server`.

## Resources

- [references/session-reference.md](references/session-reference.md) —
  the full authorization table, the queue's server-side delivery mechanics
  (why a hibernated target is never waited on), and worked examples.
  > Contents · Authorization matrix (who may target whom) · How `queue` actually delivers (verified end-to-end) · `slash` vs `queue` vs `inject` — the full decision table · Environment variables the CLI reads · Worked examples
- `.claude/rules/aimaestro-manager-approval-defaults.md` — the
  EXEMPT/NON-EXEMPT operation lists this skill's strict/non-strict split
  mirrors (the ai-maestro DEP overlay, seeded into every agent workdir).

## Use also

- `Skill(skill: "ama-panel")` — drive the agent's HTML dashboard panel.
- `Skill(skill: "ai-maestro-agents-management")` — agent lifecycle and
  configuration (a different authority than driving your own terminal).
- `Skill(skill: "team-governance")` — the titles (MANAGER/COS/…) this
  skill's cross-agent targeting rule is keyed on.
