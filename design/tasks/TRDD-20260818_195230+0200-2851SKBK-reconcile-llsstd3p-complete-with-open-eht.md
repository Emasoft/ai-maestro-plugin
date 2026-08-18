---
trdd-id: 2851SKBK
title: LLSSTD3P sits at complete while its EHT SNG93TTD is still open — reconcile per rule 9
column: complete
created: 2026-08-18T19:52:30+0200
updated: 2026-08-18T19:57:34+0200
implementation-commits: [d52173d]
current-owner: ai-maestro-plugin-session
task-type: infra
priority: normal
approval-tier: 0
labels: [phase2, plugin-self-audit, governance]
---

# Reconcile the LLSSTD3P rule-9 violation

Phase-2 card for Phase-1 audit finding 2 (evidence:
`reports/plugin-self-audit/20260816_165645+0200-axis2-governance.md`).

`TRDD-LLSSTD3P` carries `column: complete` with `eht: [SNG93TTD]`, and `TRDD-SNG93TTD` is
`column: dev`. TRDD rule 9: a parent cannot reach `complete` until every EHT is terminal.
The violation predates this program (it existed when SNG93TTD sat at `todo`).

## Decision to make in dev

Two honest resolutions; pick one and record why in the card:
1. **Finish SNG93TTD** (already in dev) — the violation dissolves when it reaches a
   terminal column. Preferred if the harness work completes in reasonable time.
2. **Un-complete LLSSTD3P** — revert it to the column it should have held pending its EHT
   (with `blocked-by: [SNG93TTD]` and `pre-block-column:` recorded), acknowledging the
   `complete` transition was invalid when made. Use if SNG93TTD stalls.

Do NOT resolve it by editing the `eht:` list — deleting the dependency to silence the rule
destroys the reason the EHT exists.

## Resolution taken (2026-08-18)

**Resolution 2, refined.** SNG93TTD's harness is not near completion (its design
consultation was killed and not re-run), so waiting on resolution 1 would leave the board
lying for days. LLSSTD3P moved `complete → blocked` with `blocked-by: [SNG93TTD]` and
`pre-block-column: complete` — per rule 6, `blocked` applies whenever `blocked-by:` is
non-empty, and the pre-block column records that the card returns to `complete`
legitimately the moment its EHT is terminal. `eht:` untouched.

## Acceptance

- [x] `grep "^column:" TRDD-*LLSSTD3P*.md TRDD-*SNG93TTD*.md` no longer violates rule 9
      (LLSSTD3P: blocked, SNG93TTD: dev); resolved via column state, not `eht:` surgery.
