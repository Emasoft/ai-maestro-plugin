# R42.8 — the authority gate, its provenance, and interim installs

## Contents

- [The eight constraints](#the-eight-constraints)
- [Provenance — why this file records a mistake](#provenance--why-this-file-records-a-mistake)
- [Feature detection — older installs](#feature-detection--older-installs)

## The eight constraints

All eight are load-bearing. Read them before the first call, not after a refusal.

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

## Provenance — why this file records a mistake

On 2026-08-07 the skill said R42.8 was *not ratified*. That was measured
accurately — R42.8 was absent from three published copies at the time — but
concluded wrongly: the USER grant of 2026-08-05 was real and only the
**publication** lagged, landing 2026-08-08. *"I cannot verify this"* is not
*"this is not true"*, and asserting the stronger claim caused four role-plugins
to retract correct statements. **For an absence, "true but not yet published"
is always a live answer** — ask it before concluding.

The verb list then moved twice more in one morning: v5.3.2 (05:51Z) omitted
`block-state`, v5.3.3 (06:03Z) restored it after the hub checked
`lib/sudo-guard.ts` rather than the doc. **Twelve minutes.** Three separate
sessions read the row inside one of those windows and each published a list
that was correct when read and wrong within hours.

The transferable habit is not "measure more carefully" — every one of those
measurements was correct. It is: **resolve the branch TIP first, then read the
row.** Those are two different acts, and only the second was being done.

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
