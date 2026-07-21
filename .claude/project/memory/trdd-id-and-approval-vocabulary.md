---
name: trdd-id-and-approval-vocabulary
description: "why are some TRDD ids lowercase and others uppercase / can I rename a TRDD id to make it conformant / my TRDD lookup finds nothing even though the card exists / find -name vs -iname on TRDD files / what replaced approval-tier: N / is it maestro or user at the top of the approval ladder / where is the tier-floor table and should a skill restate it / two plugins ship the same rule filename"
ocd: 2026-07-22
lmd: 2026-07-22
metadata:
  node_type: memory
  type: project
  tier: component
  functionality: governance
  globs: ["rules/trdd-*.md", "skills/ama-trdd-*/**", "skills/ama-proposal-approvals/**"]
---

# TRDD ids and the approval vocabulary — two ratified models CORE taught wrongly

Both were migrated on 2026-07-21/22 under MANAGER rulings (`core#30`, `core#32`, `core#33`,
`core#34`). The facts below are the ratified end state; the **lessons** carry the WHY, which
is the part that stops the next agent "fixing" them back.

## 1. The TRDD id: 8-char UPPERCASE base36, and legacy lowercase ids are permanent

The id **IS** the canonical identifier — an 8-char UPPERCASE base36 string (`A-Z0-9`).
**There is no UUID**; nothing derives from anything. Mint it and re-roll on collision:

```bash
while :; do
  TID=$(LC_ALL=C tr -dc 'A-Z0-9' < /dev/urandom | head -c 8)
  find design ~/.claude/projects/*/design -iname "TRDD-*-${TID}-*.md" 2>/dev/null \
    | grep -q . || break
done
```

**The UPPERCASE constraint binds at MINT time ONLY.** A large share of the existing corpus
carries 8-char **lowercase hex** ids from a retired `uuid4()`-derived recipe. They are
**permanently valid and non-conformant by design** — renaming one is forbidden.

**Every id READER must be case-insensitive, forever** — lookup, resolve, `npt:`/`eht:`/
`blocked-by:`/`parent-trdd:` edge resolution, the board renderer, and the collision check.
The collision check is the reader that *loses data*; the others merely fail to find the
card, which is the failure that actually fires.

## 2. `min-approval-requirement:` — titles, not numbers

```
none  <  orchestrator  <  chief-of-staff  <  manager  <  user
```

`member`/`architect`/`integrator` carry none-authority. A higher rung may approve a lower
one, never the reverse. **Absent means `none`.** `approval-tier: N` is RETIRED (decode
`0→none, 1→chief-of-staff, 2→manager, 3→user`, then rewrite to the title). `maestro` is a
deprecated READ-alias for `user` — accept on read, normalize, never write.

**Cite the floor, never restate it.** The objective tier-floor lives in exactly one place
(the TRDD approval-tiers rule, §D3). Skills state the principle and point at it.

## Governed by

- [[architecture]] — the functionality hub this component sits under (its `## Applies to`
  carries the reciprocal link).

## Notes and lessons learned

[^1]: [id:ATOM-TRDD-ID-IMMUTABLE, status:valid, keywords:"can_i_rename_a_trdd_id_to_make_it_conformant normalize_lowercase_ids_migration_pass 76_percent_of_the_board_is_non_conformant should_i_clean_up_the_ids", ocd:2026-07-22, lmd:2026-07-22]
  DO NOT normalize legacy lowercase TRDD ids to uppercase, BECAUSE the id is cited in
  IMMUTABLE commit subjects (one audited board: 13 ids across 80 commits, plus 26 ids in
  dependency edges) and those are the backtracking chain `git log --grep 'TRDD-<id>'` that
  traces a future bug to the TRDD that introduced it. DO leave them and make every reader
  case-insensitive — normalizing destroys provenance to satisfy a formatting rule.

[^2]: [id:ATOM-INAME-IS-PERMANENT, status:valid, keywords:"why_is_this_iname_and_not_name simplify_iname_back_to_name is_the_case_insensitive_lookup_a_migration_aid trdd_lookup_finds_nothing_though_the_card_exists", ocd:2026-07-22, lmd:2026-07-22]
  DO NOT "simplify" a TRDD `find -iname` back to `-name`, BECAUSE the corpus contains
  permanently-unrenameable lowercase ids, so a case-sensitive check reports a case-folding
  id as FREE and the write overwrites that card on macOS/Windows (case-insensitive
  filesystems) — silent, unrecoverable. DO keep `-iname` and keep the reason written at the
  site; a bare flag reads as defensive style and gets cleaned up.

[^3]: [id:ATOM-PROBABILITY-IS-THE-WRONG-AXIS, status:valid, keywords:"is_the_collision_risk_actually_likely how_should_i_argue_severity_for_a_rare_bug low_probability_so_deprioritize", ocd:2026-07-22, lmd:2026-07-22]
  DO NOT argue a data-loss defect's severity from its probability, BECAUSE a low per-event
  chance (~1e-9 here) invites deprioritization and someone will compute it anyway. DO carry
  it on silent + unrecoverable + cheap-mitigation, and check whether the LIKELIER failure is
  something else entirely — here it was conformance (a case-sensitive lookup deterministically
  missing 76% of a board), which fires every time, no collision required.

[^4]: [id:ATOM-CITE-DONT-RESTATE, status:valid, keywords:"should_the_skill_quote_the_policy_table_or_link_it duplicated_policy_went_stale restating_a_rule_into_four_skills", ocd:2026-07-22, lmd:2026-07-22]
  DO NOT restate a policy table into the skills that consume it, BECAUSE N copies drift and
  the reader cannot tell which is stale — this is exactly how the 5-column kanban vocabulary
  and the numeric approval tiers both went stale. DO state the principle and cite ONE
  canonical source by NAME + section, never by absolute path (a path couples every consumer
  to one install layout, and the path is what rots).

[^5]: [id:ATOM-TWO-PLUGINS-ONE-RULENAME, status:valid, keywords:"two_plugins_ship_the_same_rule_filename which_copy_of_the_rule_is_installed contradictory_rule_content install_ordering_luck", ocd:2026-07-22, lmd:2026-07-22]
  DO NOT assume the rule file loaded in a session is the one THIS repo ships, BECAUSE CORE
  and ai-maestro-janitor both ship `rules/trdd-design-tasks.md` with CONTRADICTORY id models
  (janitor's base36 copy is what is installed; CORE's teaches the retired uuid4 scheme and
  reasons from it) — the correct one is live by install ORDERING, not by design. DO diff the
  installed copy against the repo copy before trusting either, and treat "which plugin owns
  this filename" as a `manager`-floor decision, not a doc edit.
