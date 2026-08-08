---
name: ama-unblock
user-invocable: false
description: "MANAGER/CHIEF-OF-STAFF workflow (governance R42.8) for a stuck agent session — blocked on an AskUserQuestion, a permission prompt, or a rate-limit/API-error banner. Diagnose with block-state plus read-prompt, then resume it by answering its own pending prompt, or escalate to the USER. This is the ONLY case where a MANAGER/COS may act on another agent's session. Trigger with 'agent is stuck', 'session blocked', 'answer its pending prompt', 'worker not responding', 'why is the agent waiting'. Self-unblocking is ama-session. Loaded by ai-maestro-plugin"
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
the messaging-only model, and governance **R42.8** is the sanctioned patch —
**ratified**, `Explicit (USER — 2026-08-05, ai-maestro#125, TRDD-AODXPI5E)`,
published in `docs/GOVERNANCE-RULES.md` **v5.3.3** on `Emasoft/ai-maestro@governance-rules`.

> ## THE EXCEPTION VERBS — exactly three, and the list is exhaustive
>
> **`block-state`, `read-prompt` and `answer` ONLY** (v5.3.3, verified at tip
> `e46764f6`). `inject`, `slash` and `queue` are **explicitly not** exception
> verbs — they deliver an arbitrary command, so they express the CALLER's
> decision (R42.1) and stay SELF-ONLY for every title; the server 403s them
> cross-agent.
>
> **The dividing line is CALLER DECISION, not read-vs-write.** `block-state` and
> `read-prompt` are both READS carrying no decision of the caller's, which is why
> the inject/slash/queue exclusion never touched them.
>
> **⚠ Do NOT "restore" a narrower list.** Doc 5.3.2 omitted `block-state`; 5.3.3
> corrected it, because the server had always granted it — `lib/sudo-guard.ts`
> routes `block-state` through the **same `unblock-prompt` action** as the other
> two. A guard pinning two verbs locks out the pane-authoritative detection read.
>
> **Why `block-state` is load-bearing:** `read-prompt` reads the hook's
> chat-state record, and a MANAGER measured `AskUserQuestion` present in **0 of
> 419** of them — a figure now cited in the ratified row itself. That 0/419 is
> **CORE's own `#59` defect**, fixed in this tree and **not yet published**, so
> consumers still run the pre-fix writer. **Check `writerVersion` before reading
> a null** — on a pre-fix writer a null `read-prompt` is that known gap; on a
> fixed writer a null is REAL. Even once the fix ships, `block-state` stays in
> the list: it is the pane-authoritative read.

**This skill has been wrong about that list three times in two days**, always by
reading the row without first resolving the branch TIP. The provenance is in
[references/r42-8-authority.md](references/r42-8-authority.md) — read it before
you "correct" anything here.

> **The single carve-out is R42.8**: a MANAGER or CHIEF-OF-STAFF may UNBLOCK
> an agent stalled on a permission/question prompt. Unblocking answers a
> prompt the agent itself raised; it confers **no power to direct** that
> agent. Everything else — tasking, corrections, coordination — is AMP per
> the R6 communication graph.

The workflow: **DETECT → DIAGNOSE → READ → DECIDE → ANSWER → VERIFY →
NOTIFY**, entirely through the frozen `aimaestro-session.sh`. **Never call the
ai-maestro server API directly; this CLI resolves the API base and your
identity internally (core#11).** That matters more here than anywhere else in
the plugin: R42.8 is enforced at the API by title and blocked-state, so
reaching past the CLI is not a shortcut around a missing verb — it is an
attempt to perform an unblock without the gate that makes unblocking legal.
If a verb you need does not exist, that is the answer; file it, do not route
around it. The exception verbs are **`block-state`, `read-prompt` and
`answer` ONLY**. `inject`,
`slash` and `queue` are NOT exception verbs: they deliver an arbitrary
command, so they express the CALLER's decision (R42.1 exactly) and stay
SELF-ONLY for every title — the server 403s them cross-agent.

## The authority gate — READ [the eight constraints](references/r42-8-authority.md) FIRST

The four that decide whether you may act at all, in one line each; the full
eight, with their reasoning, are in the reference:

- **(a) Blocked-only** — a working, idle, or merely SLOW agent is untouchable.
  *"It would be faster if I typed it"* is an R42.1 violation, not an unblock.
- **(c) Title-scoped** — MANAGER: any agent on the host **except an ASSISTANT**.
  COS: **its own team only**, same exclusion. Every other title: none.
- **(e) Identity prompts ESCALATE** — never self-certify through a second
  channel; a spoofer performs the identical act.
- **(g) Server-enforced, failing closed** — `answer` 409s unless the target is
  really blocked. **The refusal IS the check**, never an obstacle to route around.

## The two read verbs are NOT alternatives

- **`read-prompt <agent>`** returns what the plugin **HOOK recorded** — so it is
  only as good as the target's installed plugin version. Before the `#59` fix it
  carried AskUserQuestion **never** (measured 0/419), answering `null` for the one
  prompt shape that blocks an agent forever. **Check `writerVersion` before
  reading a `null` as either answer.**
- **`block-state <agent>`** reads the **TERMINAL** — the only source reflecting
  the screen *now*, and the **authority**. `reason ∈ ask_user | permission |
  rate_limited | api_error | idle | active | unknown`.

Use both. `hookDisagreed: true` means resolve toward the pane. The verdict's
full JSON shape, the `--match` server-side pane search, the three measured facts
about `status` / `updatedAt` / `field`, and the **tmux host caveat** (an iTerm-
hosted agent may be unreadable by `block-state` while the janitor cannot rescue
it either — both paths down at once, silently) are in
[references/reading-blocked-state.md](references/reading-blocked-state.md).
**Read that caveat before concluding any unreadable agent is healthy.**

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

`interim` means this server predates the capability, so **the R42.8 exception is
NOT in force here**: escalate to the USER with what evidence you can gather, and
do **not** fall back to raw `tmux send-keys` or any other direct pane access.
Being unable to unblock is the correct behavior until the gate exists — the gate
IS the safety property. Why, and what `interim` still permits:
[references/r42-8-authority.md](references/r42-8-authority.md).

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

A **403** means the title matrix refused you; a **409** means the target is not
actually blocked. Both are the gate working — re-read `block-state`, never force.
The full symptom table (including the `writerVersion` null and the
`questionCount > 1` multi-question trap) is in
[references/reading-blocked-state.md](references/reading-blocked-state.md).

## Scope

Cross-agent, MANAGER/COS-only, **blocked-sessions-only** — the R42.8
carve-out, nothing more. Everything self-targeted (your own prompt, your own
queue) is `ama-session`. Tasking, corrections, and coordination are AMP
(`agent-messaging`). Window/limit self-recovery is `ama-continuity`. Agent
reconfiguration is `ai-maestro-agents-management` (R42.6 — a separate,
non-injection authority). This skill never reconfigures anything and never
touches a session that is merely SLOW — slow is not blocked.

## Resources

- [references/r42-8-authority.md](references/r42-8-authority.md) — the eight constraints in full, the provenance of three wrong verb lists, and what an `interim` install still permits.
  > Contents · The eight constraints · Provenance — why this file records a mistake · Feature detection — older installs
- [references/reading-blocked-state.md](references/reading-blocked-state.md) — the `block-state` JSON shape, `--match`, the three measured facts, the tmux host caveat, and the error table.
  > Contents · The two read verbs are NOT alternatives · Three measured facts every consumer must know · HOST CAVEAT — the terminal read is tmux-backed · Error handling
- `Emasoft/ai-maestro@governance-rules` — **the authoritative rule text**:
  `docs/GOVERNANCE-RULES.md` (v5.3.3, carries R42.8), `rules/aimaestro/` (5
  overlay rules), `design/specs/role-plugins-spec.md`. These live on the
  **unmerged `governance-rules` branch**, so a query against `main` 404s and
  **that 404 means nothing**. Always read the row itself rather than any
  plugin's summary of it — including this one.
- `ai-maestro#125` — the amendment request that carried R42.8, and the USER
  verdict on it. It is still OPEN; **an open issue is not evidence the rule is
  unratified** (that inference is what went wrong here — see the provenance
  note above). Comment `5224811566` reconciles the timeline for anyone who
  measured between the 2026-08-05 grant and the 2026-08-08 publication.
- `ai-maestro#128` — the capability's design record (USER directives verbatim).
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
