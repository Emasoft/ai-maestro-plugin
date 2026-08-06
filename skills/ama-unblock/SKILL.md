---
name: ama-unblock
user-invocable: false
description: "MANAGER/CHIEF-OF-STAFF fleet-continuity workflow (governance R42.8): detect an agent session that is stuck — blocked on an AskUserQuestion, a permission prompt, a rate-limit or API-error banner (red text) — diagnose WHY from the terminal-read verdict (block-state) plus the hook record (read-prompt), then resume it by answering its own pending prompt, or escalate to the USER. Blocked-work is the ONLY case where a MANAGER/COS may act on another agent's session; every other cross-agent influence goes via AMP messaging. Trigger with 'agent is stuck', 'session blocked', 'answer its pending prompt', 'worker not responding', 'resume the fleet', 'why is the agent waiting'. Self-unblocking (your own prompt) is ama-session, not this. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-session.sh:*), Bash(amp-send.sh:*), Bash(jq:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-unblock — MANAGER/COS work-continuity interventions on blocked sessions

## Overview

A blocked agent session is blocked **forever** unless something answers it: an
`AskUserQuestion` menu or a permission prompt never resolves itself, and a
blocked agent cannot read its AMP inbox — messaging reaches an agent only at
its next turn, and a blocked agent has no next turn. This is the one hole in
the messaging-only model, and governance **R42.8** is the sanctioned patch
(USER grant 2026-08-05, `ai-maestro#125`; capability record `ai-maestro#128`):

> **The single carve-out is R42.8**: a MANAGER or CHIEF-OF-STAFF may UNBLOCK
> an agent stalled on a permission/question prompt. Unblocking answers a
> prompt the agent itself raised; it confers **no power to direct** that
> agent. Everything else — tasking, corrections, coordination — is AMP per
> the R6 communication graph.

The workflow: **DETECT → DIAGNOSE → READ → DECIDE → ANSWER → VERIFY →
NOTIFY**, entirely through the frozen `aimaestro-session.sh` — the exception
verbs are **`block-state`, `read-prompt` and `answer` ONLY**. `inject`,
`slash` and `queue` are NOT exception verbs: they deliver an arbitrary
command, so they express the CALLER's decision (R42.1 exactly) and stay
SELF-ONLY for every title — the server 403s them cross-agent.

## The authority gate — R42.8's eight constraints, READ THIS FIRST

1. **(a) Blocked-only.** The sole trigger is an agent stalled on a prompt. A
   working, idle-but-unblocked, or merely SLOW agent is untouchable — *"it
   would be faster if I typed it"* is an R42.1 violation, not an unblock.
2. **(b) Unblock, never drive.** Answer ONLY the pending prompt. Nothing
   appended, no new work, no redirection. Work is still assigned by AMP alone.
3. **(c) Title-scoped and exhaustive.** MANAGER: any agent on the host
   **except an ASSISTANT**. CHIEF-OF-STAFF: **its own team only**, same
   exclusion. Every other title: none.
4. **(d) Never an ASSISTANT.** An ASSISTANT's session is the surface a human
   talks *through* — an injected answer is indistinguishable from something
   its human typed, laundering an agent's instruction into apparent human
   intent. (A USER has no terminal; there is no USER-target case.)
5. **(e) Identity prompts ESCALATE.** A prompt asking the agent to vouch for
   the CALLER's own authority goes to the human, never answered by the
   caller — self-certification through a second channel proves nothing, and
   a spoofer performs the identical act. No agent is the authority on
   identity; the ai-maestro SERVER is the sole notary.
6. **(f) Read before answer.** Never answer a prompt you have not read
   (`read-prompt` + the `block-state` evidence). An unblock interrupts
   nothing — the agent is already stopped, waiting.
7. **(g) Server-enforced, failing closed.** AID_AUTH + governance title;
   `answer` returns **409 unless the target is actually blocked**. The
   refusal IS the check — a 403/409 is information, never an obstacle to
   engineer around.
8. **(h) Audited.** Every accepted call lands in the agent ops ledger.

## The two read verbs are NOT alternatives

- **`read-prompt <agent>`** returns what the plugin **HOOK recorded**.
  Measured across 419 live chat-state files: it carries permission prompts,
  and carries AskUserQuestion **never** (0/419 question texts) — for the one
  prompt shape that blocks an agent forever it answers `null` and the agent
  looks fine. (CORE issue `#59` tracks fixing the hook capture.)
- **`block-state <agent>`** reads the **TERMINAL** — the only source that
  reflects the screen *now*. Returns the structured verdict:

  ```json
  { "blocked": true, "reason": "ask_user",
    "field":   { "visible": true, "empty": true, "text": "" },
    "choices": [ { "key": "1", "label": "…" } ],
    "excerpt": [ "…the question, verbatim…" ],
    "hookDisagreed": false, "sessionName": "…" }
  ```

  `reason ∈ ask_user | permission | rate_limited | api_error | idle |
  active | unknown`. `--match "<regex>"` searches the pane **server-side**
  (only matching lines cross the boundary; requires the agent to be blocked).

Use both: the hook record is the fast hint, the pane verdict is the
**authority**, and `hookDisagreed: true` means exactly that — resolve toward
the pane (the hook is known to mislabel a live AskUserQuestion as
`permission_prompt`).

Three measured facts every consumer must know (`ai-maestro-plugin#58/#59`):

- **`status` cannot discriminate blocked from idle** — a blocked agent and a
  healthy idle one both read `waiting_for_input`. The discriminator is
  **`notificationType`** (`permission_prompt` / `elicitation_prompt` vs
  `idle_prompt`), not `status`.
- **Chat-state goes stale on exactly the agents that matter** — the hook
  writes on events and a blocked agent generates none (~17 h observed). So
  `updatedAt` is NOT a liveness signal, and "no recent event" is
  indistinguishable from "healthy" from the file alone.
- **`field`** (`visible`/`empty`/`text`) is how "the input field is clear"
  is checked on the ai-maestro channel — never by eyeballing a pane dump.

## The reason → action decision table

| `reason` | legal action | rule |
|---|---|---|
| `ask_user` | `answer --option <key>` (menu — `choices` present) or `answer --text "<answer>"` (freeform) | answer ONLY when the right choice is derivable from the target's own TRDD / mandate / task context; otherwise escalate to the USER. **Never guess** — a wrong answer silently steers hours of downstream work; an escalation costs minutes |
| `permission` | `answer --option <key>` | approve only in-mandate AND non-destructive; destructive or out-of-mandate ⇒ escalate. A MANAGER rubber-stamp deletes the last line of defense |
| `rate_limited` | **WAIT** — no verb | never type into a rate-limited session; it self-resumes when its janitor heartbeat fires after the window (`ama-continuity`), else report to the USER |
| `api_error` | **WAIT**, then escalate if persistent | usually transient/self-healing; there is deliberately no cross-agent nudge verb (`inject` is SELF-ONLY) — a stuck error banner is a USER report, not a keystroke |
| `idle` / `active` | **hands off** | not blocked. `answer` 409s by design — see constraint (a) |
| `unknown` | escalate with evidence | capture `excerpt` (plus a targeted `--match`) and report to the USER; never act on an unclassified state |

Identity-vouching prompts (any `reason`): escalate — constraint (e).

## The workflow

```bash
# 1. DETECT + DIAGNOSE — the terminal verdict (authority)
aimaestro-session.sh block-state <agent> | jq .

# 2. READ — constraint (f): both sources, never answer unread
aimaestro-session.sh read-prompt <agent>          # the hook record (may be null for ask_user)
#    …and read block-state's .excerpt / .choices yourself.

# 3. DECIDE — the table above + the derivability test:
#    can the right answer be read off the target's own TRDD, mandate, or task
#    state? If you need knowledge its context does not contain, escalate.

# 4. ANSWER — only the pending prompt, nothing else
aimaestro-session.sh answer <agent> --option <key>
aimaestro-session.sh answer <agent> --text "<answer>"

# 5. VERIFY — re-read the verdict
aimaestro-session.sh block-state <agent> | jq '{blocked, reason}'
#    blocked:false = resumed. Same reason still blocked = your answer did not
#    take: STOP and escalate with before/after excerpts — do not retry blind.
#    A NEW reason (a permission prompt often follows an answered question) =
#    re-enter at step 1; one answer per blocked-state, not per session.

# 6. NOTIFY — provenance (R41): the resumed agent must know the answer
#    came from you, not from its human
amp-send.sh <agent> "unblocked by <your-id>" \
  "Your pending <reason> prompt was answered by <your-id> with: <answer>. Reason: <one line>."
```

Strict-route auth: agents authorize by AID_AUTH + title; a HUMAN caller
needs `AIMAESTRO_SUDO_TOKEN` (`block-state`, `answer`, `queue` are strict).

## Feature detection — older installs

```bash
aimaestro-session.sh help 2>&1 | grep -q "block-state" && echo full || echo interim
```

- **`full`** — the R42.8 surface is present; the whole workflow applies.
- **`interim`** — the server predates the unblock capability. Operative
  subset: `read-prompt` where permitted, plus **escalation to the USER with
  whatever evidence you can gather**. And the load-bearing rule:

  > **Absence of the gated verbs means the R42.8 exception is NOT in force
  > on this install. Do NOT fall back to raw `tmux send-keys`, `inject`, or
  > any other direct pane access against another agent.** Not being able to
  > unblock is the correct behavior until the gate exists — the gate IS the
  > safety property (blocked-precondition, title matrix, 409, ledger), not
  > an inconvenience layered on top of it. All agents share one OS uid, so
  > tmux WOULD succeed: R42 is tamper-EVIDENT, not tamper-proof, and the
  > ledger-visible refusal to bypass it is what the rule buys.

## Anti-patterns (each has caused, or would cause, real harm)

- **Guessing an answer to a domain question** to keep the pipeline moving.
- **Approving a permission prompt you would not approve as the USER** —
  destructive commands, pushes, credential access.
- **Retry loops** — re-answering variations after a failed intervention;
  one answer per blocked-state, then escalate.
- **Smuggling work through an unblock** ("while I have the prompt: also run
  X"). Constraint (b): that is an R42.1 violation, not a permitted use.
- **Raw tmux as a fallback** — see above.
- **Answering an identity-vouching prompt.** Constraint (e). Never.
- **Polling `status` or trusting `updatedAt`** to decide who is blocked —
  the discriminator is `notificationType`, the authority is `block-state`.

## Error handling

| Symptom | Meaning |
|---|---|
| `block-state`: unknown command | interim mode — this server predates the capability; escalate-only |
| 403 on `block-state` / `read-prompt` / `answer` | title matrix failed — you are not MANAGER/COS, the target is out of your scope, or it is an ASSISTANT; the refusal is the check |
| 409 on `answer` / `--match` | the target is not actually blocked (constraint (a) / Gate 0b) — re-read `block-state`; if it says blocked and the server says 409, report the disagreement upstream, do not force |
| `read-prompt` returns null but the pane shows a menu | expected for AskUserQuestion (hook capture gap, CORE `#59`) — the `block-state` excerpt/choices are the readable copy |
| target resumed but did the wrong thing | your NOTIFY message is how it finds out and corrects — send it, then follow up via AMP |

## Scope

Cross-agent, MANAGER/COS-only, **blocked-sessions-only** — the R42.8
carve-out, nothing more. Everything self-targeted (your own prompt, your own
queue) is `ama-session`. Tasking, corrections, and coordination are AMP
(`agent-messaging`). Window/limit self-recovery is `ama-continuity`. Agent
reconfiguration is `ai-maestro-agents-management` (R42.6 — a separate,
non-injection authority). This skill never reconfigures anything and never
touches a session that is merely SLOW — slow is not blocked.

## Resources

- `ai-maestro#125` / `ai-maestro#128` — the R42.8 grant and the capability's
  design record (USER directives verbatim).
- `ai-maestro-plugin#58` / `#59` — the verified verb surface, the measured
  hook findings, and the hook-capture fix this skill's caveats cite.
- `design/tasks/TRDD-*-ZNGTF0FG-*.md` — CORE's implementation record.

## Use also

- `Skill(skill: "ama-session")` — the SELF half of the same CLI surface.
- `Skill(skill: "agent-messaging")` — AMP, the default channel for every
  non-blocked case.
- `Skill(skill: "team-governance")` — R42/R42.8 and the titles this skill's
  authority gate is keyed on.
- `Skill(skill: "ama-continuity")` — an agent's own window-exhaustion
  self-resume (the self-side complement of the `rate_limited` class).
