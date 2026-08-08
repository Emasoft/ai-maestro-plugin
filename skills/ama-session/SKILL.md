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

**SELF ONLY for every verb in this skill's ordering — no title exempts you
(governance R42, IRON).** `inject`, `slash`, `queue` and `state --pane` are
self-only for MANAGER and CHIEF-OF-STAFF exactly as for everyone else: they
deliver an arbitrary command, so they express the CALLER's decision. The
server 403s them cross-agent.

**The one carve-out is R42.8, and it is NOT in this skill.** A MANAGER (any
agent but an ASSISTANT) or a CHIEF-OF-STAFF (its own team only) may
`block-state` / `read-prompt` / `answer` **another** agent that is stalled on
a prompt — answering the prompt that agent itself raised, nothing more. That
workflow, its eight constraints and its escalation rules live in
`ama-unblock`. Everything below is the SELF case.

Since `TRDD-D3RP7KQZ`: **an agent may drive its own surface; it may never
reconfigure itself.** Every verb in this skill acts on the agent's **own**
id by default (inferred from the environment), and that is the only
permitted target.

> **R42 — No Agent May Drive Another Agent; messaging is the ONLY channel**
> (CRITICAL, IRON, USER-set). R42.1: *no agent may inject a command,
> keystroke, prompt, or queued input into another agent's session — by API,
> by CLI, or by tmux — **to assign, redirect, or perform that agent's
> work***. R42.2: *no title is exempt* — MANAGER and CHIEF-OF-STAFF are
> bound exactly as every other agent is, holding exactly one narrow power
> the others lack (R42.8 unblocking), which is **not** a power to direct.
> R42.4 preserves self-drive, which is what this skill is for.
>
> **This supersedes the title-keyed targeting this skill used to teach**
> ("another agent requires MANAGER, or COS for its own team"). That was the
> pre-R42 `send-command` model, and R42 revoked the cross-agent *command*
> case entirely (`TRDD-BF3JN4TL`). To influence another agent, send it a
> message (**AMP — `amp-send.sh`**, not the harness's own `SendMessage`
> tool, which reaches the session directly and is graph-checked by nobody;
> see `agent-messaging`) and let it decide — an injected command *is* the
> recipient's own action, which bypasses its judgment and its governance
> title.
>
> **R42.8 is a carve-out from the WORK ban, not a hole in it.** An unblock
> answers a prompt the target itself raised: it supplies a missing input, it
> does not author an instruction. Smuggling work through an unblock ("while
> I have the prompt, also run X") is an R42.1 violation, not a permitted
> use — which is exactly why `inject`/`slash`/`queue` are excluded from the
> exception and stay self-only here.
>
> **A 403 is not the boundary.** All agents run under one OS uid, so
> `tmux send-keys -t <other>` succeeds regardless of what the API permits.
> R42 is enforced at the API and *mandated by rule* — tamper-EVIDENT, not
> tamper-proof. Do not treat "the call would fail" as the reason to comply.
**Nothing in this skill ever reconfigures anything** — role, plugin, team,
MCP, hooks, sub-agents, and title are refused on self for every title,
MANAGER included; that is `ai-maestro-agents-management`'s domain (and it
too is self-refused for configuration).

**Strict vs non-strict** (who can call what, and how they authenticate):
`block-state`, `answer` and `queue` are **strict** — an agent authenticates
by AID + title, a human needs a fresh sudo-token. `inject`, `slash`,
`slash-keys`, `state`, `read-prompt`, `queue-list`, `queue-cancel` are
**non-strict**.

**`read-prompt` returns what the plugin HOOK recorded, so what it can tell you
depends on the installed version.** Before the `#59` fix the hook did not record
an `AskUserQuestion`'s text at all (measured 0 of 419 live chat-state files), so
a `null` did NOT mean "no prompt is pending"; fixed versions record the question,
its normalized choices, and `questionCount`. Every record carries `writerVersion`
so a reader can tell which it is holding — for the self case you can usually see
your own prompt directly;
for the cross-agent case that is why `block-state` reads the terminal.

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
| `state <agent>` | `--pane` | non-strict (`--pane` is self-only) |
| `read-prompt <agent>` | — | non-strict; cross-agent only under R42.8 (`ama-unblock`) |
| `block-state <agent>` | `--match "<regex>"` | **strict**; the terminal read — cross-agent only under R42.8 (`ama-unblock`) |
| `answer <agent>` | `--option <key>` \| `--text "<answer>"` | **strict**; cross-agent only under R42.8 (`ama-unblock`) |

## Output

Each subcommand prints its result on STDOUT (JSON where noted — pipe to
`jq`); errors go to STDERR with a non-zero exit code. `queue` returns the
enqueued entry id (needed for `queue-cancel`).

## Error Handling

| Symptom | Likely cause |
|---|---|
| 403 targeting another agent with `inject`/`slash`/`queue`/`state --pane` | expected — R42 forbids these for every title, MANAGER included. Send the agent a message instead; do not look for a title that permits it |
| 403 targeting another agent with `block-state`/`read-prompt`/`answer` | the R42.8 title matrix refused you (not MANAGER/COS-of-that-team, or the target is an ASSISTANT). See `ama-unblock` |
| 409 on a cross-agent `answer` | the target is not actually blocked — R42.8(a). Not a bug: an unblock has no meaning for a working agent |
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

Drives an agent's **own** terminal/state — and only its own; R42 (IRON)
forbids targeting another agent, with no title exemption. The single
sanctioned cross-agent exception — a MANAGER/COS resuming a **blocked**
session through the server-gated unblock verbs — is `ama-unblock`, not this
skill. Never reconfigures an agent (role,
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

- `Skill(skill: "ama-unblock")` — the MANAGER/COS-only, blocked-sessions-only
  cross-agent exception (detect / diagnose / resume a stuck fleet member).
- `Skill(skill: "ama-panel")` — drive the agent's HTML dashboard panel.
- `Skill(skill: "ai-maestro-agents-management")` — agent lifecycle and
  configuration (a different authority than driving your own terminal).
- `Skill(skill: "team-governance")` — the titles (MANAGER/COS/…) this
  skill's cross-agent targeting rule is keyed on.
