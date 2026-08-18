---
trdd-id: JQ0T7MRC
title: publish.py RATIFIED_BASELINE_RULESETS is the PAIR — the refusal guard cannot see baseline-tag-protect
column: dev
created: 2026-08-18T21:05:00+0200
updated: 2026-08-18T21:05:00+0200
current-owner: ai-maestro-plugin-session
task-type: bugfix
priority: high
approval-tier: 0
labels: [phase2, plugin-self-audit, governance]
---

# Extend the baseline refusal guard from PAIR to TRIO

Found by the adversarial ai_review of commit 94a7883; ownership settled by hub measurement
and re-verified here first-hand: the CPV template carries NO `RATIFIED_BASELINE_RULESETS`
constant at all (grep over the CPV cache: 0 hits, positive control `baseline-history-protect`
→ 2 hits), so this is CORE-local, not the fleet template defect.

`scripts/publish.py:851` — `RATIFIED_BASELINE_RULESETS = ("baseline-history-protect",
"baseline-pr-and-checks")`. The constant feeds the `--install-branch-rules` REFUSAL guard
(`:924-931`): any ratified name present on the origin → refuse to run
`cpv-setup-branch-rules` (which would add a non-ratified ruleset and advise deleting
`baseline-pr-and-checks`; claude-plugins-validation#203). Missing `baseline-tag-protect`
means a repo carrying ONLY the tag ruleset (branch pair not yet applied, or mid-migration)
slips past the guard. Adding the third name strictly STRENGTHENS the refusal.

Collateral staleness in the same function: the docstring `:906` still lists
`required_linear_history` among history-protect's rules (removed by the 2026-08-08 Tier-3
ruling), and `:930` prints "The ratified pair IS the baseline".

## Acceptance

- [ ] Constant names the ratified TRIO.
- [ ] `:930` message and the `:905-906` docstring no longer assert the pair / the removed rule.
- [ ] `tests/test_install_branch_rules_guard.py` passes (updated if it pinned the pair).
