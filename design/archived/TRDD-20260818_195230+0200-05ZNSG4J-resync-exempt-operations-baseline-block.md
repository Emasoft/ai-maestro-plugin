---
trdd-id: 05ZNSG4J
title: exempt-operations.md baseline block is stale on two Tier-3 rulings and omits the ratified third ruleset
column: complete
created: 2026-08-18T19:52:30+0200
updated: 2026-08-18T19:57:34+0200
implementation-commits: [94a7883]
current-owner: ai-maestro-plugin-session
task-type: docs
priority: high
approval-tier: 0
labels: [phase2, plugin-self-audit, governance]
---

# Re-sync the ratified-baseline block in exempt-operations.md

Phase-2 card for Phase-1 audit findings 3 (restated) + 4 (evidence:
`reports/plugin-self-audit/20260816_165645+0200-axis2-governance.md` and DELEGATION.md).

`skills/ama-trdd-transition/references/exempt-operations.md:124-149` describes the
ratified GitHub baseline and is stale on three counts. It is a skill reference an AGENT
loads to decide EXEMPT vs NON-EXEMPT, so the staleness misleads agents, not just readers:

1. `:133` — `baseline-history-protect` shown with `bypass_actors: []`, the shape abolished
   by the USER's Tier-3 ruling of 2026-08-13 (owner must be able to push directly). The
   executable SSOT (janitor `branch_protection_lib.baseline_ruleset_payloads`) has emitted
   `[{actor_id: 5, actor_type: RepositoryRole, bypass_mode: always}]` since v3.3.0.
2. `:135` — still lists `required_linear_history`, removed by the USER's Tier-3 ruling of
   2026-08-08 ("never re-add it", janitor#14 / ai-maestro#140).
3. The block calls the baseline a PAIR. The ratified set is a TRIO — `baseline-tag-protect`
   (`target: tag`, `bypass_actors: []`, rules `deletion`+`update`) was ratified later on
   janitor#14. Canonical carriers in the ai-maestro repo:
   `rules/aimaestro/aimaestro-manager-approval-defaults.md:152`,
   `design/specs/baseline-github-rulesets-spec.md` §3,
   `tests/governance/baseline-spec-ratchet.test.ts:20` (pins the TRIO by name).
   This omission is exactly why two independent sessions mis-read the live third ruleset
   as an undocumented deviation — fixing it here is CORE's slice of the fleet
   "distribution defect" card.

## Constraints (from the hub, verified)

- `baseline-tag-protect` is correctly `bypass_actors: []` — do NOT sweep it into fix 1.
- Do not hardcode an approval count for pr-and-checks beyond what the spec states.
- Specs move FIRST: the canonical spec (`baseline-github-rulesets-spec.md` in ai-maestro)
  is already correct — this card only re-syncs CORE's mirror to it, so no spec edit needed.
- Do NOT touch `scripts/publish.py:906` (comment also naming `required_linear_history`):
  publish.py is CPV-template-owned and the hub is routing template fixes to CPV.

## Acceptance

- [x] The block describes the ratified TRIO, with per-ruleset bypass_actors matching the
      ai-maestro spec (history-protect: admin bypass per the 2026-08-13 ruling;
      tag-protect: empty), and names the canonical spec + ratchet test as the SSOT.
- [x] `required_linear_history` appears in the file only as a same-line removal note.
- [x] `grep -rn "required_linear_history" skills/` returns exactly that one removal-note
      line. Targeted tests: 96 passed.
