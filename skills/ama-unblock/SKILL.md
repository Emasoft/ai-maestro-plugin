---
name: ama-unblock
user-invocable: false
description: "MANAGER/CHIEF-OF-STAFF fleet-continuity workflow: detect an agent session that is stuck — blocked on an AskUserQuestion, a permission prompt, a frozen input field, a rate-limit or API-error banner (red text), a trust/login prompt — diagnose WHY from the hook state plus the classified terminal evidence, then resume it with the right gated intervention or escalate to the USER. Blocked-work is the ONLY sanctioned direct-command case; every other cross-agent influence goes via AMP messaging. Trigger with 'agent is stuck', 'session blocked', 'answer its pending prompt', 'worker not responding', 'resume the fleet', 'why is the agent waiting'. Self-unblocking (your own prompt) is ama-session, not this. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-session.sh:*), Bash(amp-send.sh:*), Bash(jq:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-unblock — MANAGER/COS work-continuity interventions on blocked sessions

## Overview

A blocked agent session is blocked **forever** unless something answers it: an
`AskUserQuestion` menu, a permission prompt, a frozen input field, or a client
error banner never resolves itself, and a blocked agent cannot read its AMP
inbox — messaging reaches an agent only at its next turn, and a blocked agent
has no next turn. This is the ONE hole in the messaging-only model, and this
skill is the sanctioned patch for it (USER directive 2026-08-06, tracked in
`ai-maestro#128`):

> **Blocked-work is the ONLY case where a MANAGER or CHIEF-OF-STAFF may act
> directly on another agent's session. Everything else — tasking, corrections,
> coordination — goes via AMP per the R6 communication graph.**

The skill teaches a six-step loop: **DETECT → DIAGNOSE → DECIDE → ACT →
VERIFY → NOTIFY**. The ACT step runs through **server-gated verbs only**
(never raw pane access), and those verbs plus the matching R42 exception
clause are being shipped by the AI Maestro server (`ai-maestro#128`). Until
they land, steps 1–3 and the USER-escalation path are fully operative — see
[Feature detection](#feature-detection--what-is-operative-today).

## The authority gate — READ THIS FIRST

Three conditions, ALL required, before the ACT step is even considered:

1. **WHO** — you hold the **MANAGER** title (any agent in the org) or
   **CHIEF-OF-STAFF** (agents of your own team only). No other title, ever.
2. **WHEN** — the target is **currently classified BLOCKED**, with **both
   evidence sources agreeing**: the hook-state broadcast AND the terminal
   classifier. One source alone, or disagreement, means `unknown_blocked` —
   and unknown means WAIT + escalate, never act.
3. **WHAT** — the intervention chosen is **legal for the diagnosed class**
   per the decision table below. There is no class whose legal action is
   "send the agent new work" — tasking a resumed agent is AMP's job.

If any condition fails, the correct move is an AMP message (agent will read
it next turn) or a report to the USER — not a workaround. R42 (IRON) still
governs: the server enforces the gate at the API, the ledger makes every
intervention auditable, and the absence of a gate verb means the exception
is **not in force** (see the tmux prohibition below).

## The blocked-class taxonomy and decision table

Eight classes. Learn the table; the `why-blocked` verb returns the class so
you never diagnose from raw text alone.

| class | what the session shows | legal action | rule |
|---|---|---|---|
| `ask_user_question` | AskUserQuestion menu with options | `--option <key>` | answer ONLY when the right option is derivable from the target's own TRDD / mandate / task context; otherwise escalate to the USER. **Never guess.** |
| `ask_user_freeform` | open question, free-text input | `--text "<answer>"` | same derivability rule |
| `permission_prompt` | tool-approval prompt | `--option <key>` | approve only if the pending action is in-mandate AND non-destructive; destructive or out-of-mandate ⇒ escalate |
| `input_field_blocked` | input field hidden / non-empty / stuck | `--nudge` | one clear/re-arm attempt (the server decides the exact keys), then escalate |
| `rate_limited` | red rate-limit banner, window countdown | `--wait` ONLY | never type into a rate-limited session; optionally `queue --when idle` a resume command for after the window |
| `api_error_retry` | red API-error / retry banner | `--nudge` | one retry nudge; if it recurs, escalate — repeated errors are an infrastructure problem, not a typing problem |
| `trust_prompt` | folder-trust / login / onboarding dialog | NONE | machine-trust and auth decisions are **human-only**, no exceptions |
| `unknown_blocked` | evidence sources disagree, or no pattern matched | `--wait` ONLY | capture the excerpt, escalate to the USER |

Two rules cut across every class:

- **Answer with the least-authority content that resumes work.** An answer
  you derive from the target's own task context carries the target's own
  authority; an answer you invent carries yours, wrongly.
- **One intervention per blocked-state.** If the session is still blocked
  after one intervention, STOP and escalate. The server's cooldown refuses a
  second attempt against an unchanged state — do not look for a way around
  it; a refused second attempt means your diagnosis was wrong.

## The workflow

### 1. DETECT — find blocked fleet members

```bash
aimaestro-session.sh state <agent>            # per-agent 5-state activity
```

Blocked signals: `waiting-permission`, `waiting-elicitation`, or a
long-stale `working`/`idle` on an agent whose kanban card says mid-task.
Staleness (time since last state change) is the blocked-duration signal —
a 2-minute wait is normal, a 2-hour one is a stall.

### 2. DIAGNOSE — get the classified WHY

```bash
aimaestro-session.sh why-blocked <agent> | jq .
```

Returns `{blocked, class, confidence, since, evidence:{hookState, excerpt,
promptStructure}}`. Read the excerpt yourself — the classifier picks the
class, but YOU are accountable for the answer's content. For the two prompt
classes, `promptStructure` carries the exact question and option keys.

### 3. DECIDE — apply the table

Look up the class → legal action. Then the derivability test: can the right
answer be read off the target's own TRDD, mandate, or current task state?
If you need knowledge the target's context does not contain — judgment
calls, credentials, product decisions — the answer is escalation, not
improvisation.

### 4. ACT — through the gated verb only

```bash
aimaestro-session.sh unblock <agent> --option <key>     # menu answer
aimaestro-session.sh unblock <agent> --text "<answer>"  # freeform answer
aimaestro-session.sh unblock <agent> --nudge            # input-field / retry recovery
aimaestro-session.sh unblock <agent> --wait             # explicit no-op + ledger entry
```

The verb is STRICT (AID + title, sudo-token for humans) and refuses:
non-MANAGER/COS callers, a target not currently classified blocked, an
action illegal for the class, evidence disagreement, and repeat attempts
against an unchanged state. Every acceptance is ledgered with the evidence
snapshot. A refusal is information, not an obstacle.

### 5. VERIFY — confirm resumption

```bash
aimaestro-session.sh why-blocked <agent> | jq '.blocked'
```

Re-check after a short wait. `false` = resumed. Still `true` with the same
class = your intervention did not take: STOP, escalate to the USER with the
before/after excerpts. Still `true` with a NEW class = re-enter the loop at
step 2 (a permission prompt often follows an answered question) — the
one-intervention rule applies per blocked-state, not per session.

### 6. NOTIFY — tell the target what happened

```bash
amp-send.sh <agent> "unblocked by <your-id>" \
  "Your pending <class> prompt was answered by <your-id> with: <answer>. Reason: <one line>. Ledger: <ref>."
```

The resumed agent's next turn MUST know the answer came from you, not from
the human user — a silent third-party answer corrupts the agent's
provenance model (R41): it would treat your judgment as USER authority.
The server may automate this notification; send it yourself until it does.

## Feature detection — what is operative TODAY

Probe before teaching yourself capabilities the install may not have:

```bash
aimaestro-session.sh why-blocked --help >/dev/null 2>&1 && echo full || echo interim
```

- **`full`** — the server has shipped the verbs and the R42 exception
  clause is in the governance catalog. The whole workflow above applies.
- **`interim`** — the verbs have not landed. Operative subset: DETECT
  (state reads), DIAGNOSE-lite (`read-prompt` where the server permits the
  read), and **escalation to the USER with the evidence you gathered**.
  The ACT step is NOT available, and — this is the load-bearing rule —

  > **absence of the gated verb means the R42 exception is NOT in force.
  > Do NOT fall back to raw `tmux send-keys`, `inject`, or any other
  > direct pane access against another agent. Not being able to unblock
  > is the correct behavior until the gate exists**; the gate IS the
  > safety property (classification precondition, evidence agreement,
  > cooldown, ledger), not an inconvenience layered on top of it.

A cross-agent 403 on `state`/`read-prompt` in interim mode is expected on
older servers — report what you could observe (dashboard state, kanban
staleness) and escalate; do not treat the 403 as a bug to engineer around.

## Anti-patterns (each has caused, or would cause, real harm)

- **Guessing an answer to a domain question** to keep the pipeline moving.
  A wrong answer silently steers hours of downstream work; a USER
  escalation costs minutes.
- **Approving a permission prompt you would not approve as the USER** —
  destructive commands, pushes, credential access. The permission gate is
  the last line of defense; a MANAGER rubber-stamp deletes it.
- **Injection loops** — re-sending variations after a failed intervention.
  The cooldown refuses it server-side; respect the same rule in interim
  mode where no server enforces it.
- **Using unblock verbs for tasking** ("while I have the terminal, run
  X…"). The exception covers RESUMING work, never DIRECTING it — direction
  is AMP.
- **Raw tmux as a fallback** — see above. Tamper-EVIDENT, not
  tamper-proof: the OS lets you, the rule and the ledger are why you don't.
- **Answering a trust/login prompt.** Never. Human-only.

## Error handling

| Symptom | Meaning |
|---|---|
| `why-blocked`: command not found / unknown verb | interim mode — server verbs not yet shipped; escalate-only |
| 403 on `unblock` | authority gate failed — wrong title, target not blocked, illegal action, or evidence disagreement; read the error body, do not retry blind |
| `unblock` refused: cooldown | a previous intervention already ran against this state — escalate, your diagnosis was wrong |
| 403 on cross-agent `state`/`read-prompt` | older server, reads not yet opened for MANAGER/COS — interim protocol |
| target resumed but did the wrong thing | your NOTIFY message is how it finds out and corrects — send it, then follow up via AMP |

## Scope

Cross-agent, MANAGER/COS-only, **blocked-sessions-only** — the single
sanctioned exception to messaging-only influence. Everything self-targeted
(your own prompt, your own queue) is `ama-session`. Tasking, corrections,
and coordination are AMP (`agent-messaging`). Window/limit self-recovery is
`ama-continuity`. Agent reconfiguration is `ai-maestro-agents-management`.
This skill never reconfigures anything and never touches a session that is
merely SLOW — slow is not blocked.

## Resources

- `ai-maestro#128` — the capability's design record: the USER directive
  verbatim, the verb contract, the class table, and the server's half.
- `design/tasks/TRDD-*-ZNGTF0FG-*.md` — CORE's implementation record.

## Use also

- `Skill(skill: "ama-session")` — the SELF half of the same CLI surface.
- `Skill(skill: "agent-messaging")` — AMP, the default channel for every
  non-blocked case.
- `Skill(skill: "team-governance")` — R42 and the titles this skill's
  authority gate is keyed on.
- `Skill(skill: "ama-continuity")` — an agent's own window-exhaustion
  self-resume (the self-side complement of the `rate_limited` class).
