---
name: publish-and-validation-gate
description: "why does local publish.py validate disagree with CI / which CPV version does this repo validate against and where is it pinned / the strict gate went red and I changed no code / is exit 4 a real failure or a NIT / when may I bump the CPV pin"
ocd: 2026-08-01
lmd: 2026-08-01
metadata:
  node_type: memory
  type: project
  tier: component
---

# publish-and-validation-gate

## Governed by
- [[architecture]] — the hub; `scripts/publish.py` is the canonical CPV release
  pipeline listed in its parts map. The hub points here for the validator pin and
  the gate's failure modes rather than restating them.


^ATOM-5EQC-RUFU [desc:"the CPV validator ref is ONE constant mirrored at 3 sites; a partial bump silently splits local G3 from CI while both report passed", keywords: local_validate_and_ci_validate_disagree both_gates_said_passed_but_used_different_validators where_is_the_cpv_version_pinned i_bumped_the_validator_and_ci_still_uses_the_old_one cpv_ref_constant, type: project, ocd: 2026-08-01, lmd: 2026-08-01]

The CPV validator ref lives as ONE constant, `CPV_REF` in `scripts/publish.py`, and is mirrored verbatim in `.github/workflows/ci.yml` and `.github/workflows/release.yml`. All three MUST move in the same commit. A bump that misses one leaves the local G3 gate and CI validating with DIFFERENT validators while both report "passed" — that silent split is the whole reason the constant exists. Verify with `grep -rn "claude-plugins-validation@v" scripts/publish.py .github/workflows/*.yml` and confirm exactly one distinct version. [^1]


^ATOM-GL5C-YX00 [desc:"a red --strict gate after a pure git mv was CPV scoping design/archived/ but not design/tasks/; fixed upstream in CPV v4.2.1", keywords: strict_gate_went_red_and_i_changed_no_code exit_4_nit_3_after_moving_files git_mv_turned_validation_red validator_scans_one_lifecycle_folder_but_not_its_sibling is_a_nit_a_real_failure, type: project, ocd: 2026-08-01, lmd: 2026-08-01]

Archiving terminal TRDDs (a pure `git mv` into `design/archived/`, zero content change) once took this repo from exit 0 to exit 4 / NIT=3: CPV `--strict` scanned `design/archived/` but NOT `design/tasks/`, because the exclusion was keyed on the LITERAL path `design/tasks` rather than on the lifecycle corpus. The findings were prose inside terminal TRDD bodies, which the TRDD rules freeze, so there was no source-side fix and the gate was held honestly red rather than green by suppression. Fixed upstream in CPV v4.2.1 — all four lifecycle zones clear, with a non-lifecycle `design/notes/` control still firing so it cannot decay into a blanket `design/` mute. Filed as `Emasoft/claude-plugins-validation#184`.


^ATOM-C2YQ-S4MC [desc:"publish.py G4 sets AIMAESTRO_CLI_REQUIRED=1 so absent frozen CLIs FAIL the release gate instead of silently skipping the skill contracts", keywords: why_does_publish_set_aimaestro_cli_required skill_cli_contracts_skipped_during_publish tests_passed_but_the_cli_checks_never_ran release_gate_green_with_skipped_tests publish_g4_env_var, ocd: 2026-08-02, lmd: 2026-08-02]

**`publish.py` G4 runs `pytest tests/` with `AIMAESTRO_CLI_REQUIRED=1`** (`ce2cd41`).

G4 is MANDATORY and blocks on failures and on zero-collected — but **not on SKIPS**. The
frozen-CLI contracts in `tests/test_skill_cli_contracts.py` skip when a CLI is off `PATH`,
which is correct in CI (the runner has no ai-maestro) and *wrong at publish*: publish runs on
a developer machine where all six CLIs exist, so a skip there means the install broke — and
the release would ship skills whose taught flags and subcommands were never verified, with
the gate still green.

The var is set BY `publish.py`, not left to a human to export: a guard nobody enables is not
a guard. CI leaves it unset and keeps skipping.


^ATOM-ETJG-U10G [desc:"local and remote can report the SAME version, so only git ancestry proves a commit reached the remote", keywords: my_resolution_cites_a_commit_nobody_else_can_see is_this_commit_actually_pushed local_and_remote_both_say_the_same_version how_do_i_prove_a_fix_reached_the_remote, ocd: 2026-08-02, lmd: 2026-08-02]

**A version string cannot tell local from remote.** Measured 2026-08-02: both local `main` and
`origin/main` reported `2.11.0` while 54 commits were local-only.

The only reliable test:

```bash
git merge-base --is-ancestor <sha> origin/main   # false => local-only, unverifiable outside
```

**Do not cite a LOCAL-ONLY sha as evidence when closing an issue.** `main` is protected and
`publish.py` is the only path to the remote, so a batch can sit unpushed for days. An outside
reviewer opened `core#36` after catching exactly this twice — resolution claims citing commits
nobody else could see. Wait for the publish, or say explicitly that the commit is not yet on
the remote. [^2]


^ATOM-LIRS-K5Y5 [desc:"Mega-Linter lints only files changed vs the default branch, so a push TO main lints an EMPTY set and passes trivially while PRs inherit every latent finding in the files they touch.", keywords: ci_is_green_on_main_but_every_pr_fails_lint pr_fails_for_code_i_did_not_write megalinter_validate_all_codebase_false_changed_files_only local_publish_gate_passes_then_ci_goes_red why_main_never_catches_lint_errors, ocd: 2026-08-04, lmd: 2026-08-04]

`.mega-linter.yml` sets `VALIDATE_ALL_CODEBASE: false`, so Mega-Linter lints only what changed
against the default branch. On a push to `main` that set is EMPTY — it lints nothing and the Lint
job passes trivially. On a PR it diffs against `main` and lints whatever that PR touches, so a
one-line dependabot bump to `ci.yml` inherits every pre-existing finding in `ci.yml`. **Main is
structurally incapable of catching these; contributors always do.** Measured 2026-08-04: 19 unique
cspell errors (`anchore`, `PIPESTATUS`, `syft`, `Emasoft`, …) lived in `.github/workflows/` through
many green main builds and surfaced only on dependabot PRs.

The repo had already learned this for a DIFFERENT linter and written it into the same file:
`PYTHON_BANDIT_ARGUMENTS` carries the note that this setting "hides the noise until someone edits a
Python file — and then their PR fails CI for code they did not write (49 of the 57 findings on the
PR that added this line predate it)". Nobody generalised it to `SPELL_CSPELL`. When a linter is
added to `ENABLE_LINTERS`, sweep the whole tree with it ONCE and fix or dictionary the backlog,
because the setting guarantees the backlog lands on whoever next edits the file.

`publish.py` cannot substitute: it lints `scripts/` with ruff+mypy only. Workflow YAML, spelling,
copy-paste and shell are CI's job, so a clean local publish says nothing about them. [^3]


^ATOM-QHY3-BTGA [desc:"the governance mirror's rule tables DESCRIBE forbidden attacks; skillaudit flags them, and the .cpv-audit-consent.json registry is what lets them ride as visible consented WARNINGs — regenerate it on ANY mirror edit", keywords: publish_blocked_on_NIT_skillaudit governance_mirror_trips_the_security_scanner threat_description_prose_flagged_as_attack A2A_rules_flagged_in_references_file cpv_audit_consent_registry mirror_edit_reblocks_publish, ocd: 2026-08-05, lmd: 2026-08-06]

The governance mirror's rule TABLE ROWS (R22.4/R42.1/R42.7 — prose FORBIDDING attacks)
trip skillaudit's A2A_* patterns by design-collision: security documentation describes what
it forbids. The sanctioned path is the **audit-consent registry**
(`.cpv-audit-consent.json` at plugin root, shipped via `claude-plugins-validation#194`/PR
#195): each entry pins (file, ruleId, sha256 of the **FULL stripped disk line** — NOT the
scanner's truncated `[:200]` lineContent) and turns that already-demoted finding into a
visible consented WARNING. Consequences: any edit to a consented mirror line re-blocks
publish until the registry is regenerated (that is the feature); a registry can never touch
a live finding; muting rules or editing the verbatim mirror body remain forbidden. [^4]

## Notes and lessons learned

[^1]: [id:ATOM-998W-KR6T, status:valid, desc:"a version restated in a second page is a fact that will go stale silently — name the owning page instead", keywords:"the_docs_say_one_version_and_the_code_says_another my_architecture_page_still_cites_the_old_pin where_should_a_version_number_live two_pages_disagree_about_a_dependency_version stale_version_in_an_overview_page", ocd:2026-08-01, lmd:2026-08-01] DO NOT restate a pinned version number in an overview/hub page that another page already owns, BECAUSE nothing fails when the copy rots — `architecture.md` still read "pinned `@v3.5.0`" after two bumps (v3.5.0 -> v3.22.3 -> v4.2.1) and would have told the next reader to validate against a version this repo has not used since 2026-07-26. DO name the owning page ([[publish-and-validation-gate]]) and let the version live in exactly one place, next to the command that proves it.
[^2]: [id:ATOM-2LQ6-O5ZA, status:valid, desc:"mark a local sha AS local at the point of citation — knowing the rule did not stop me repeating it three times in one day", keywords:"i_cited_a_sha_nobody_can_fetch gh_api_commits_returns_422_no_commit_found they_cannot_see_the_commit_i_referenced how_should_i_cite_an_unpushed_commit my_memory_had_the_rule_and_i_broke_it_anyway", ocd:2026-08-02, lmd:2026-08-02] DO NOT cite a bare sha as evidence while the delivery gate is held, and DO NOT rely on REMEMBERING that rule, BECAUSE a bare sha reads as a promise the reader can verify — and the correct next step ("fetch it and check") silently cannot be taken, so the fallback is to trust the citation. Measured 2026-08-02: a peer ran `gh api repos/…/commits/07db70e` → **422 No commit found** and checked three repos before concluding it was a delivery gap, not a typo; **all SIX shas I cited that day were local-only**, and I had authored the atom above warning about this a few hours earlier. It did not fire because I wrote it about CLOSING issues and then cited shas in *discussion* — a rule scoped to one surface does not generalize itself. DO write the marker INTO the citation — `07db70e (local, unpushed)` — which is mechanical, needs no recall, and distinguishes "not fetched yet" from "not fetchable"; the peer proposed it after making the identical mistake, which is how a convention beats a memory.
[^3]: [id:ATOM-L3C0-JQGE, status:valid, desc:"A fail-fast job reveals its next defect only after the previous one is fixed — so N red causes look like N regressions.", keywords:"i_fixed_the_ci_failure_and_a_new_one_appeared does_each_fix_cause_the_next_failure cheap_fail_first_job_aborts_before_later_steps three_red_causes_stacked_in_one_job is_the_job_clean_after_one_green_step", ocd:2026-08-04, lmd:2026-08-04] DO NOT read "I fixed it and now something ELSE fails" as having caused a regression, BECAUSE a cheap-fail-first job aborts at its first failing step, so every later step's defects are invisible until that one is green: on 2026-08-04 the Lint job hid three independent, all pre-existing causes behind each other — actionlint SC2086, then Commitlint's rejected `deps:` prefix, then 19 cspell words — and each fix looked like it broke the next thing. DO expect a fail-fast pipeline to reveal defects one at a time, budget for several rounds rather than one, and confirm a job is CLEAN by reading every step's status, never by seeing the previously-failing step turn green.
[^4]: [id:ATOM-GSVC-UQT2, status:valid, supersedes:ATOM-QHY3-BTGA, desc:"RESOLVED 2026-08-06: CPV v5.2.0 shipped the consent registry (PR #195, hardened at merge — lineSha256 = sha256 of the FULL stripped disk line, NOT the [:200] lineContent recipe); v3.0.5 published clea", keywords:"consent_registry_hash_recipe_full_line_not_truncated editing_the_governance_mirror_re-blocks_publish regenerate_cpv_audit_consent_after_mirror_edits publish_unblocked_by_cpv_v5.2.0 lineSha256_recipe_changed_at_merge", ocd:2026-08-06, lmd:2026-08-06] DO NOT hash consent-registry entries with the scanner's truncated `line.strip()[:200]` lineContent recipe, BECAUSE the merged v5.2.0 semantics hash the FULL stripped line read from disk (the maintainer closed the truncation hole at merge) — two of core's three entries silently failed to match until regenerated, and any future edit to a consented mirror line re-blocks publish by design. DO regenerate `.cpv-audit-consent.json` with full-line sha256 after ANY edit to the governance mirror, and expect the finding to re-block until you do — that is the feature, not a bug. SUPERSEDED BODY: The v5.2.0 governance-mirror sync cannot publish until upstream `claude-plugins-validation#194` ships: skillaudit's A2A_* patterns match the mirror's own rule TABLE ROWS (R22.4/R42.1/R42.7 — prose FORBIDDING the attacks), the demote lands at NIT, and NIT blocks `--strict`. Verified against BOTH the pinned CPV v4.2.1 and latest v5.1.5 (same 3 findings, rc=4), so bumping `CPV_REF` does not help. No sanctioned path exists for this content class: the issue-#101 audit-consent sentinel anchors only to FENCED markdown blocks (table rows have no fence), the issue-#38 doc-only suppression deliberately excludes `skills/*/references/` (instruction-loadable), and the "needs review" demote state has no recordable verdict. Resolutions that are FORBIDDEN: muting the rule, editing the verbatim mirror body, relocating the mirror out of references/ (breaks the skill's discovery contract). The only move is the upstream fix; then re-run `publish.py --patch`.
