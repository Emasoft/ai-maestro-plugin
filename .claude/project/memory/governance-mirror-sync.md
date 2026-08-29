---
name: governance-mirror-sync
description: "governance blob sha mismatch / mirror looks stale but is not / which branch does the mirror track / is my governance mirror out of date / our skill teaches something a governance rule forbids / bundled governance rules are stale / why did nobody notice the rule violation / did we check the new governance rules against the skills / is the v5.2.0 contradiction sweep done / which rules had violations in core skills"
ocd: 2026-08-05
lmd: 2026-08-29
metadata:
  node_type: memory
  type: project
  tier: component
  globs: ["skills/**"]
publish-globally: false
split-lineage: cc9840b5939c4effac960eb58cab1b1e
---

# governance-mirror-sync

`skills/team-governance/references/GOVERNANCE-RULES.md` is a vendored mirror of
upstream's `docs/GOVERNANCE-RULES.md`: what its own `branch:`/`synced-blob:` fields
actually mean, why CORE tracks `main`, and the state of the v5.2.0 contradiction sweep.

^ATOM-4ZIF-ICEA [desc: "the mirrored GOVERNANCE-RULES.md branch: field is UPSTREAM's own frontmatter and is NOT sync provenance, and CORE tracks main which can lag the governance-rules branch", keywords: governance_blob_sha_mismatch mirror_looks_stale_but_is_not branch_field_says_governance-rules_but_synced-blob_is_main false_drift_alarm_on_GOVERNANCE-RULES which_branch_does_the_mirror_track 44be10d5d351_vs_ceb4ac163bc0 two_sessions_disagree_about_the_governance_blob synced-blob_does_not_match_what_a_peer_reports is_my_governance_mirror_out_of_date spec_half_falsifies_a_single-file_blob_comparison, ocd: 2026-08-29, lmd: 2026-08-29]

**`branch: governance-rules` inside `skills/team-governance/references/GOVERNANCE-RULES.md` is
part of UPSTREAM's own frontmatter — it sits directly above upstream's `changelog:` and the
mirror reproduces it verbatim. It does NOT say which branch this copy was taken from.** Only
`synced-blob:` and `synced-at:` are CORE-added provenance. Reading `branch:` as provenance
manufactures a drift alarm out of a correctly-synced file; it is adjacent to `changelog:` and
reads exactly like provenance, so a faithful mirror and a mislabelled one look identical.

**CORE tracks `main`, deliberately.** Verified 2026-08-29 via the GitHub API:
`docs/GOVERNANCE-RULES.md` @main = `44be10d5d351…` (what the mirror pins, exact match) and
@governance-rules = `ceb4ac163bc0…`. These are NOT two branches that disagree — `main` simply
lags by one commit (`41266cf14ab2`, 2026-08-26, R6.6/R6.9 prose corrected to match code,
TRDD-2XV78BND). Same lineage, one behind. Mirroring `governance-rules` instead would ship
content that has not landed, and `docs/GOVERNANCE-RULES.md` is the PRIMARY EMANATION per its
own §0 while `main` is the default branch — so tracking `main` is correct and
`tests/test_governance_mirror_stamp.py` fires exactly when `main` advances, which is when the
resync should happen. No manual watch is needed. See [[publish-and-validation-gate]].

**Comparing ONE file cannot tell "branch fork" from "branch lag".** The pair
`design/specs/governance-spec.md` + `docs/GOVERNANCE-RULES.md` can: on 2026-08-29 a peer's pin
`spec=b96efb43adc9 + rules=44be10d5d351` looked like main because its rules half matched main,
but main's spec half is `6a4a1c9fa600`, so the pair was `governance-rules@928c96b3bed7` all
along. Fetch BOTH halves before concluding anything structural about which branch a stamp
belongs to.


^ATOM-GFBT-KR76 [desc:"CORE's vendored GOVERNANCE-RULES.md mirror lags upstream, so skills get written against superseded semantics and the artifact that would contradict them is the stale one", keywords: our_skill_teaches_something_a_governance_rule_forbids bundled_governance_rules_are_stale why_did_nobody_notice_the_rule_violation mirror_lags_upstream_so_skills_were_written_pre_rule R42_cross_agent_driving_forbidden, ocd: 2026-08-05, lmd: 2026-08-05]

`skills/team-governance/references/GOVERNANCE-RULES.md` is a **vendored mirror** of
`docs/GOVERNANCE-RULES.md` on the `governance-rules` branch of the ai-maestro repo, and it LAGS.
(Written out in prose rather than in git's compact ref notation: the scope-leak detector treats an
at-sign between two names as a user-and-host pair and flags the whole page as carrying a machine
identity. Note the shape is described here rather than spelled, or this very sentence re-trips it —
see janitor#209.) On 2026-08-05 it was
**v4.0.2** (synced 2026-06-18) against upstream **v5.2.0** — twelve rules behind.

That lag is not merely missing documentation, it silently produces WRONG SKILLS. Measured: three
skills (`ama-session`, `ama-panel`, `session-reference.md`) taught "targeting another agent requires
MANAGER (any) or CHIEF-OF-STAFF (own team)" — the pre-R42 `send-command` model. **R42 (CRITICAL,
IRON) landed upstream in v4.3.0 and forbids it absolutely, with no title exemption.** The skills
were not defiant; they were written before the rule reached this repo, and then nothing could
notice, because the artifact that would have contradicted them IS the stale mirror. Fixed `84aefa0`,
shipped v3.0.4.

**Therefore: before syncing the mirror, grep the skills for what the NEW rules contradict** — the
sync is the cheap half; the consequences are the work. `grep -rn "requires MANAGER\|MANAGER (any" skills/`
finds this class. The same reasoning applies to any plugin whose mirror predates a rule: a rule that
arrives by mirror only binds agents whose mirror arrived.

The mirror's own update procedure (its §0 banner) is NOT a `cp`: step 2 requires walking the §0
cross-reference index — every mirror, persona, enforcement site, API route, UI component, scenario
test — which spans repos and is why this is a reviewed change, never a drive-by.


^ATOM-SBNM-OHF2 [desc:"the v5.2.0 governance contradiction sweep (R41-R52 vs CORE skills) COMPLETED 2026-08-05: 3 real violations found and fixed (R42, R49, R44/R50.4), all other rules verified clean - do not re-run it", keywords: did_we_check_the_new_governance_rules_against_the_skills is_the_v5.2.0_contradiction_sweep_done which_rules_had_violations_in_core_skills R44_migrate_export_import_violation governance_mirror_lag_sweep_result do_not_redo_the_R41_R43_R48_R50_R51_checks, ocd: 2026-08-05, lmd: 2026-08-05]

The ATOM-GFBT-KR76 method (grep skills for what the new rules contradict BEFORE syncing the
mirror) was run to completion on 2026-08-05 across all 12 rules the bundled mirror (v4.0.2)
lags behind the canonical v5.2.0. Yield: R42 (3 skills taught cross-agent driving — fixed,
shipped v3.0.4), R49 (bare refusals in ama-proposal-approvals — fixed f0e95b7), R44/R50.4
(agents-management REFERENCE Decision Guide taught "migrate" = self-serve export/import,
predating R44's dual-MANAGER server-coordinated migration — fixed 1fb9b94, guard note added
at the Import section). R52 and R41/R43/R45-R48/R50-R51 verified CLEAN: the topics are
either untaught by CORE, deliberately DEP-deferred (approval/mandate rung semantics per
3P-BND-02 — their absence from the TRDD frontmatter schema is BY DESIGN, not a gap), or
consistent. Only the mirror SYNC itself remains, gated on the ai-maestro-plugin#56 answer
about which half CORE owns. A 3-for-12 violation rate on unchecked rules is why the sweep
must precede every future mirror sync.

## Governed by
- [[architecture]] — the functionality hub this component sits under (its `## Applies to`
  carries the reciprocal link).

## See also
- [[publish-and-validation-gate]] — the CLI-contract strictness (`tests/test_skill_cli_contracts.py`)
  this page's mirror-sync test fires alongside.

## Notes and lessons learned
(none yet)
