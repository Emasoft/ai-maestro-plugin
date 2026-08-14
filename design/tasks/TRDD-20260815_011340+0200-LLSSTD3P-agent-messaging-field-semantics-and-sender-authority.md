---
trdd-id: LLSSTD3P
title: agent-messaging — field-semantics reference and the sender-authority procedure as THE canonical check
column: todo
created: 2026-08-15T01:13:40+0200
updated: 2026-08-15T01:13:40+0200
current-owner: ai-maestro-plugin-session
task-type: docs
priority: high
external-refs: [ai-maestro#124]
npt: []
eht: [SNG93TTD]
---

# agent-messaging: field semantics + sender-authority verification

**Spec is the MANAGER durable work order** `ai-maestro#124` (comment `5198195161`,
2026-08-05) — the comment governs. Hub tracking card: `TRDD-BCECOHJ2` (blocked on this).
Verified 2026-08-15: 0 occurrences of `governanceTitle` in `skills/agent-messaging/SKILL.md`.

## Two server facts the content depends on (USER rulings, restated in the order)

1. The ai-maestro SERVER is the sole notary of identity (2026-08-05) — identity is
   ESTABLISHED by the server's verification, never ASSERTED by a party to the exchange.
2. Authority is the TITLE and nothing else; **there is no `role` field** (USER 2026-08-06
   verbatim: "role is not part of the taxonomy"). A `role:` key in old data is removed
   legacy, NEVER evidence about authority. The server ratchet forbids `governanceTitle ||
   role` fallbacks.

## The defect

The skill documents routing + the `amp-*` surface, and NOTHING about evaluating an inbound
message: no `--type` vocabulary, no sender-verification procedure. Agents improvise — the
2026-08-05 incident: an AUTONOMOUS agent read `registry.json` directly, misread the legacy
`role` key, refused a legitimate MANAGER mandate.

## Scope (from the order)

1. Field-semantics reference: `from to subject type priority reply-to context attachments`
   — meaning AND trust status each.
2. THE sender-authority procedure: `aimaestro-agent.sh show <sender>` → `Gov. Title:`
   (live on PATH since 2026-08-05); legacy-`role` warning adjacent; a NAME is never
   evidence about title.
3. What a recipient may/may not conclude: in-body claims self-certified; registry check is
   identity not provenance; signed tokens NOT yet enforced — state the limitation, pointer
   to #47/#27, no implied promise.
4. Failure path: silent compliance and silent refusal both wrong; refusal goes back naming
   the failed check.
5. Sender's obligation: a mandate names the check the recipient should run.
6. Mirror into every skill carrying the same guidance (e.g. references the role-plugins
   inherit) so it does not exist in only one place.

## Acceptance

- [ ] field table covers every field amp-send accepts + amp-read displays
- [ ] TITLE check documented as THE authority check, legacy-role warning adjacent
- [ ] verifiability limitation explicit, pointer to #47/#27
- [ ] failure-path both directions
- [ ] behavioural check → delegated to TRDD-SNG93TTD (EHT)

## Non-goals

No signed-mandate implementation (#47/#27). Document today's procedure honestly.
If either server fact contradicts repo content, SAY SO on the issue rather than work around.
