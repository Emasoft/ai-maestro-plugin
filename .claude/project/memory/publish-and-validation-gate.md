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
(`.cpv-audit-consent.json` at plugin root, shipped via `claude-plugins-validation#194`/PR [^5]
#195): each entry pins (file, ruleId, sha256 of the **FULL stripped disk line** — NOT the
scanner's truncated `[:200]` lineContent) and turns that already-demoted finding into a
visible consented WARNING. Consequences: any edit to a consented mirror line re-blocks
publish until the registry is regenerated (that is the feature); a registry can never touch
a live finding; muting rules or editing the verbatim mirror body remain forbidden. [^4]


^ATOM-H2ZK-LGHZ [desc:"The release commit staged with git add -A, sweeping UNTRACKED files into a public irreversible commit; it now stages tracked paths BY NAME and exits non-zero rather than falling back", keywords: publish_committed_a_file_I_never_staged release_commit_contains_a_scratch_file git_add_-A_in_publish untracked_swept_into_a_release how_does_publish_stage_files, type: project, ocd: 2026-08-11, lmd: 2026-08-11]

`publish.py`'s commit stage ran `git add -A`. Stage 1 checks the tree is clean, but stages
7-9 (version bump, README badge, changelog, `uv.lock`) all run AFTER that check — so any
scratch note, tool temp output, or report appearing in that window was swept into a
**pushed, tagged, irreversible** release commit with nobody reviewing the diff.

Replaced by `_stage_tracked_modifications()`: reads `git status --porcelain=v1 -uall`,
stages tracked paths BY NAME, prints the list, names any untracked paths it is skipping,
and **exits non-zero when the porcelain is unreadable** — the tempting fallback there is
exactly `git add -A`, and it would fire precisely when nobody can see what is being staged.

Three details that matter in practice: porcelain prints `R  old -> new`, so a rename must
stage the RIGHT side; paths with spaces/unicode arrive quoted and need the quotes stripped;
and `git add --` before the paths stops a file named like a flag from becoming one.

Found by the INTEGRATOR session in its own copy of the shared scaffold — *"worth a grep in
your tree too if it shares the scaffold"* — and CORE did. Filed upstream as `CPV#206`.


^ATOM-40UG-ZR2T [desc:"git-cliff --unreleased with -o OVERWRITES CHANGELOG.md, so every release destroyed its predecessor's section; --prepend fixes it, and the lost sections are rebuildable from the tags", keywords: CHANGELOG_lost_its_old_versions only_one_section_in_the_changelog changelog_history_destroyed_on_release git-cliff_overwrote_the_file release_notes_contain_the_whole_history, type: project, ocd: 2026-08-11, lmd: 2026-08-11]

Step 9 ran `git-cliff --bump --unreleased --tag <v> -o CHANGELOG.md`. With `--unreleased`,
git-cliff emits ONLY the current range and the redirect truncates the file — so **every
release deleted its predecessor's section**. CORE's changelog carried 5 sections when the
tags said 47. Fix: `--prepend CHANGELOG.md` (the `-o` form survives only for a repo where
the file does not exist yet).

**The loss is recoverable**: `git-cliff --output CHANGELOG.md` over ALL tags (no
`--unreleased`) rebuilds the history from the commits, which were the real record all
along — 5 to 47 sections here, back to `## [2.1.0]`.

**The two changes are ONE change.** Step 11 passed the same file to
`gh release create --notes-file`, so the file and the notes were identical BY ACCIDENT
while the file held one section. Making it cumulative without also extracting just the
newest section publishes the entire project history as every release's notes.

**And the lesson that generalises:** the canonical fix shipped in CPV's emitter at v5.3.0,
but this repo's `publish.py` is DRIFTED from that scaffold (`RC-PIPELINE-DRIFT-001`), so
bumping the CPV pin to v5.4.0 delivered **none** of it. I bumped the pin and briefly
believed the fix had arrived with it. **Verify the behaviour, not the version.**


^ATOM-FX5I-7JNB [desc:"Publish died twice on a concurrent .git/index.lock; it now waits (bounded) before every index-writing git subcommand and takes --no-optional-locks on its own reads", keywords: publish_died_at_the_commit_step Unable_to_create_index.lock_during_publish release_left_bump_artifacts_on_disk publish_and_the_heartbeat_collide, type: project, ocd: 2026-08-11, lmd: 2026-08-11]

Two publishes died at step 10 (`Unable to create '.git/index.lock'`), each leaving the
version-bump artifacts on disk. Cause measured on git 2.55.0: **`git status` WRITES
`.git/index.lock`** to refresh its stat cache, and **fails SOFT** (exit 0 even when denied
it). So any read-only-looking background sweep that runs `git status` on the repo (a
periodic drift detector, an IDE indexer, another agent session) silently kills the writer
while reporting success. Full measurement lives in the USER-scope page
[[git-concurrent-readers-take-the-index-lock]].

Two changes here: `run()` awaits the lock before every index-writing subcommand
(`add|commit|rm|mv|checkout|restore|reset|stash`), centralised there so a `git add` added
later inherits it; and publish's own two `git status` reads take `--no-optional-locks`, so
the pipeline stops creating the lock it guards against.

The git dir is resolved with `git rev-parse --absolute-git-dir`, never `cwd/.git` — in a
linked worktree `.git` is a FILE, so a path guess would watch a lock that never appears and
the wait would pass instantly: green precisely when not working.

**Scope limit worth knowing:** the wait lives in `publish.py`'s runner, so a plain shell
`git commit` by the agent does NOT get it, and has hit the same lock since.

## Notes and lessons learned

[^1]: [id:ATOM-998W-KR6T, status:valid, desc:"a version restated in a second page is a fact that will go stale silently — name the owning page instead", keywords:"the_docs_say_one_version_and_the_code_says_another my_architecture_page_still_cites_the_old_pin where_should_a_version_number_live two_pages_disagree_about_a_dependency_version stale_version_in_an_overview_page", ocd:2026-08-01, lmd:2026-08-01] DO NOT restate a pinned version number in an overview/hub page that another page already owns, BECAUSE nothing fails when the copy rots — `architecture.md` still read "pinned `@v3.5.0`" after two bumps (v3.5.0 -> v3.22.3 -> v4.2.1) and would have told the next reader to validate against a version this repo has not used since 2026-07-26. DO name the owning page ([[publish-and-validation-gate]]) and let the version live in exactly one place, next to the command that proves it.
[^2]: [id:ATOM-2LQ6-O5ZA, status:valid, desc:"mark a local sha AS local at the point of citation — knowing the rule did not stop me repeating it three times in one day", keywords:"i_cited_a_sha_nobody_can_fetch gh_api_commits_returns_422_no_commit_found they_cannot_see_the_commit_i_referenced how_should_i_cite_an_unpushed_commit my_memory_had_the_rule_and_i_broke_it_anyway", ocd:2026-08-02, lmd:2026-08-02] DO NOT cite a bare sha as evidence while the delivery gate is held, and DO NOT rely on REMEMBERING that rule, BECAUSE a bare sha reads as a promise the reader can verify — and the correct next step ("fetch it and check") silently cannot be taken, so the fallback is to trust the citation. Measured 2026-08-02: a peer ran `gh api repos/…/commits/07db70e` → **422 No commit found** and checked three repos before concluding it was a delivery gap, not a typo; **all SIX shas I cited that day were local-only**, and I had authored the atom above warning about this a few hours earlier. It did not fire because I wrote it about CLOSING issues and then cited shas in *discussion* — a rule scoped to one surface does not generalize itself. DO write the marker INTO the citation — `07db70e (local, unpushed)` — which is mechanical, needs no recall, and distinguishes "not fetched yet" from "not fetchable"; the peer proposed it after making the identical mistake, which is how a convention beats a memory.
[^3]: [id:ATOM-L3C0-JQGE, status:valid, desc:"A fail-fast job reveals its next defect only after the previous one is fixed — so N red causes look like N regressions.", keywords:"i_fixed_the_ci_failure_and_a_new_one_appeared does_each_fix_cause_the_next_failure cheap_fail_first_job_aborts_before_later_steps three_red_causes_stacked_in_one_job is_the_job_clean_after_one_green_step", ocd:2026-08-04, lmd:2026-08-04] DO NOT read "I fixed it and now something ELSE fails" as having caused a regression, BECAUSE a cheap-fail-first job aborts at its first failing step, so every later step's defects are invisible until that one is green: on 2026-08-04 the Lint job hid three independent, all pre-existing causes behind each other — actionlint SC2086, then Commitlint's rejected `deps:` prefix, then 19 cspell words — and each fix looked like it broke the next thing. DO expect a fail-fast pipeline to reveal defects one at a time, budget for several rounds rather than one, and confirm a job is CLEAN by reading every step's status, never by seeing the previously-failing step turn green.
[^4]: [id:ATOM-GSVC-UQT2, status:valid, supersedes:ATOM-QHY3-BTGA, desc:"RESOLVED 2026-08-06: CPV v5.2.0 shipped the consent registry (PR #195, hardened at merge — lineSha256 = sha256 of the FULL stripped disk line, NOT the [:200] lineContent recipe); v3.0.5 published clea", keywords:"consent_registry_hash_recipe_full_line_not_truncated editing_the_governance_mirror_re-blocks_publish regenerate_cpv_audit_consent_after_mirror_edits publish_unblocked_by_cpv_v5.2.0 lineSha256_recipe_changed_at_merge", ocd:2026-08-06, lmd:2026-08-06] DO NOT hash consent-registry entries with the scanner's truncated `line.strip()[:200]` lineContent recipe, BECAUSE the merged v5.2.0 semantics hash the FULL stripped line read from disk (the maintainer closed the truncation hole at merge) — two of core's three entries silently failed to match until regenerated, and any future edit to a consented mirror line re-blocks publish by design. DO regenerate `.cpv-audit-consent.json` with full-line sha256 after ANY edit to the governance mirror, and expect the finding to re-block until you do — that is the feature, not a bug. SUPERSEDED BODY: The v5.2.0 governance-mirror sync cannot publish until upstream `claude-plugins-validation#194` ships: skillaudit's A2A_* patterns match the mirror's own rule TABLE ROWS (R22.4/R42.1/R42.7 — prose FORBIDDING the attacks), the demote lands at NIT, and NIT blocks `--strict`. Verified against BOTH the pinned CPV v4.2.1 and latest v5.1.5 (same 3 findings, rc=4), so bumping `CPV_REF` does not help. No sanctioned path exists for this content class: the issue-#101 audit-consent sentinel anchors only to FENCED markdown blocks (table rows have no fence), the issue-#38 doc-only suppression deliberately excludes `skills/*/references/` (instruction-loadable), and the "needs review" demote state has no recordable verdict. Resolutions that are FORBIDDEN: muting the rule, editing the verbatim mirror body, relocating the mirror out of references/ (breaks the skill's discovery contract). The only move is the upstream fix; then re-run `publish.py --patch`.
[^5]: [id:ATOM-Z4T6-NB25, status:valid, desc:"The correct consent-hash recipe is the NAIVE one — the trap only catches you if you reach for the scanner's lineContent field because it looks authoritative", keywords:"consent_entry_matches_nothing_and_I_do_not_know_why my_lineSha256_is_right_but_publish_still_blocks which_field_do_I_hash_for_cpv_audit_consent lineContent_looks_authoritative_so_I_used_it did_I_dodge_the_truncation_trap_without_knowing consent_file_present_but_validator_predates_the_feature consent_registry_is_a_no-op_on_an_old_CPV_pin", ocd:2026-08-07, lmd:2026-08-07] DO NOT reach for the scanner report's `lineContent` field when building a `.cpv-audit-consent.json` entry, and DO NOT assume a present consent file is doing anything. BECAUSE the correct hash is the NAIVE one — read the line off disk and `sha256(line.strip())` — so the trap only catches whoever reaches past the file for the report's field because it looks more authoritative; CPV's own 5.2.0 source says the truncation was closed deliberately, since hashing a 200-char-truncated value would let an edit BEYOND char 200 silently inherit the old consent. Two agents hit this the same day and the one who got it right did so by ACCIDENT (obvious path = correct path, on an 880-char line that would otherwise have bitten). Separately: a perfectly valid consent file against a pre-#194 validator is not a subtle failure but a NO-OP — the gate that runs is whatever `CPV_REF` pins. DO hash the full stripped disk line, and before debugging a non-matching entry CHECK THE PINNED VALIDATOR VERSION FIRST (`grep -rn "claude-plugins-validation@v" scripts/publish.py .github/workflows/*.yml`) — consent needs CPV >= v5.2.0 to exist at all.
