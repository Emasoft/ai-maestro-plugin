---
name: architecture
description: "how does ai-maestro-plugin work — overview, the main parts (skills, AMP/AID scripts, PRRD/TRDD/Kanban governance, memgrep), where the key pieces live / are the dependencies safe / dependabot reports no alerts"
ocd: 2026-06-16
lmd: 2026-07-25
metadata:
  node_type: memory
  type: project
  tier: hub
  functionality: architecture
  globs: ["skills/**", "commands/**", "scripts/**", "rules/**", ".claude-plugin/**"]
---
ai-maestro-plugin is the umbrella core plugin of the AI Maestro ecosystem — the
shared skills, AMP inter-agent messaging, AID Ed25519 identity, governance, and
the universal PRRD/TRDD/Kanban workflow every role plugin inherits. It also
hosts the `memgrep` markdown-recall engine (Rust crate + prebuilt release-asset
binaries) consumed by the other ecosystem plugins.

## Parts map
- **Skills** (`skills/`, 28) — AMP messaging, AID identity, agent management,
  MCP discovery, planning, network security, wiki-memory recall
  (`memory-search`), the `ama-*` PRRD/TRDD/Kanban governance skills, and the
  `ama-*` wrappers over ai-maestro's **frozen CLI** layer. The frozen-CLI
  wrappers are one-skill-per-script by convention (`ama-session`→`aimaestro-session.sh`,
  `ama-panel`→`…-panel.sh`, `ama-continuity`, `ama-portfolio`, `ama-settings`,
  `ama-statusline`), each declaring `allowed-tools: Bash(<script>:*)` — a skill
  that names a script without that entry is permission-blocked in a way that
  reads as "the tool is missing", so the allowed-tools line is not boilerplate.
- **Commands** (`commands/`) — 14: the 12 `/amp-*` AMP slash commands plus
  `/memory-search` and `/team-governance` (added 2026-08-02, D2).
- **Scripts** (`scripts/`) — AMP/AID shell scripts installed to PATH, the
  PRRD/TRDD/Kanban Python pillar scripts, and `publish.py` (release pipeline).
  **No memgrep crate and no installer**: ownership was ruled to the
  ai-maestro-janitor (`ai-maestro#106`, 2026-08-02) and CORE's copy — a strict
  subset under an identical `version = "0.1.0"` — was removed. CORE CONSUMES
  memgrep, it does not ship it. The guardrail is executable, not prose:
  `tests/test_memory_protocol_components.py::test_core_does_not_ship_a_rival_memgrep`
  fails if the crate, the installer, or the release job returns.
- **Rules** — CORE ships **zero** governance rules (retired core#35/#33, 2026-07-23).
  Per the 3-pillars SPEC ownership split: the IND universal bases
  (`trdd-design-tasks`, `prrd-design-rules`, `universal-kanban`) are shipped
  globally to `~/.claude/rules/` by the **ai-maestro-janitor**; the DEP overlays
  (`aimaestro-trdd-approval`, `aimaestro-manager-approval-defaults`, …) are seeded
  per agent-workdir by **ai-maestro**. CORE's skills reference those homes; the old
  `rules/` dir + `install-governance-rules.cjs` SessionStart installer were removed.
  CORE **declares a plugin dependency on `ai-maestro-janitor`** in
  `.claude-plugin/plugin.json` (`dependencies[]`, marketplace `ai-maestro-plugins`),
  so the janitor — and therefore its `~/.claude/rules/` IND bases — is
  GUARANTEED installed+enabled wherever CORE is, not merely assumed present.
  The entry carries **no `version` key** — read the manifest for the current shape
  rather than trusting a number quoted here (this bullet claimed `>=0.58.0` until
  2026-08-01, a constraint the manifest has never contained — the SECOND fact on this
  bullet to rot this way, after the CPV pin; the lesson lives on
  [[publish-and-validation-gate]]). Unconstrained is also the *safer* shape: a version-constrained
  dependency that cannot resolve **disables** the depending plugin rather than
  degrading, so a pin is a liability unless something actually needs it.
- **Publish / CI pipeline** — `scripts/publish.py` is the canonical CPV release
  pipeline. **The validator pin and this gate's failure modes live on
  [[publish-and-validation-gate]]** — do not restate the version here; it has already
  gone stale once (this bullet still read `@v3.5.0` after two bumps). The ref is one
  constant mirrored at three sites, all of which move together; local
  `--gate` includes a **jscpd** copy-paste gate (**G3b**, #143) on top of the standard
  version/lint/validate gates. The **type gate is mypy**
  (`mypy scripts/ --ignore-missing-imports`, in `release.yml` + publish.py G2),
  **not Pyright**.[^2]
- **Dependency scanning** — `.github/dependabot.yml` (added 2026-07-25, `886778d`)
  covers **github-actions** and **uv**. The **cargo** entry was REMOVED 2026-08-02
  with the crate: an ecosystem pointing at a deleted directory scans nothing while
  still looking like Rust coverage. The Rust-blindness lesson below is now the
  **janitor's** to own, and it transfers wholesale — that crate is what ships as
  prebuilt binaries ecosystem-wide.[^3]
- **Memory** — this plugin USES the janitor's global wiki-memory system (recall /
  write / update); see the PROACTIVE MEMORY CONTRACT in the repo CLAUDE.md.


^ATOM-LQAH-GVMK [desc:"the mirror-stamp banner slice refuses unless its heading occurs EXACTLY once — refuse-on-ambiguity alone misses absence, where .find(-1) swallows the whole document", keywords: my_guard_is_green_but_asserts_nothing test_passes_because_the_slice_is_the_whole_file find_returned_-1_and_the_slice_swallowed_everything banner_and_frontmatter_agree_passes_vacuously upstream_renamed_a_heading_and_my_test_went_green first_match_slice_selection refuse_on_ambiguity_is_not_enough, ocd: 2026-08-12, lmd: 2026-08-12]

**`tests/test_governance_mirror_stamp.py` selects its banner by ARITY, not position** —
`_prefix_before_unique_heading` refuses unless `# Team Governance` occurs **exactly once**,
and the predicate is `count != 1`, *not* `count > 1`.

The shape it replaced, `text[: text.find(anchor)]`, could not fail: `.find` returns `-1` when
the anchor is ABSENT, so the slice became the whole document minus one character and both
`x in banner` assertions passed because the document trivially contains its own frontmatter
values. Measured on the real mirror: **10,095 -> 214,697 chars**, green while asserting nothing.

**The trigger comes from outside this repo.** That heading lives in a MIRRORED upstream
document, so its owner renaming it — an ordinary edit nobody here controls or observes — makes
the guard vacuous on the *next sync*.

Both shapes ship as COMMITTED controls (absent, duplicated); the absent one re-measures its own
premise, `len(slice) == len(doc) - 1`, instead of inheriting `.find` semantics from a docstring.
Simulating the pre-fix shape reddens both — while the test they protect stays **green**. A guard
cannot detect its own vacuity; only a seeded control can.

From `Emasoft/ai-maestro#131` (ARCHITECT + CHIEF-OF-STAFF, five rounds). Both their defects were
ambiguity, this tree's was absence — so their package adopted verbatim measures green here and
misses the only real defect. See also [[publish-and-validation-gate]].


^ATOM-QV47-5DR0 [desc:"the five other first-match sites in CORE's suite are correct and must NOT be 'fixed' — and the corpus a selector runs over is part of the selector, which is how the audit nearly filed a false positive", keywords: grep_says_the_anchor_occurs_twice_but_the_test_passes is_this_.find_a_bug_or_correct do_not_tighten_the_release-notes_source_guard inspect.getsource_narrows_the_corpus false_positive_from_counting_across_the_whole_file which_first-match_sites_are_safe, ocd: 2026-08-12, lmd: 2026-08-12]

**Five of CORE's six first-match `.find`/`.index` sites are correct — do not "fix" them.**
`tests/test_release_notes_section.py` slices `inspect.getsource(publish.stage_changelog)`, where
every anchor (`if changelog.is_file():`, `"--prepend"`, `"-o"`) occurs exactly once and `.index`
**raises** rather than returning `-1`; `tests/test_skill_cli_contracts.py:125` guards `idx == -1`
explicitly and scans every candidate line instead of selecting one. Changing either is motion,
not correctness. Only the mirror-stamp banner slice was a real defect ([[architecture]] atom on
arity, `ATOM-LQAH-GVMK`).

**The audit nearly filed a false positive against the correct one, and the reason generalises.**
Counting `"-o"` across the WHOLE of `scripts/publish.py` gives **2**, which reads as ambiguity —
but the second is `["ps", "-p", str(pid), "-o", "ppid=,args="]` at line 976, a thousand lines
outside the function the test actually slices. Within `inspect.getsource(stage_changelog)` the
count is 1.

**The corpus is part of the selector.** A first-match detector that greps FILES rather than the
slice's real scope manufactures exactly this finding in any tree that narrows with
`inspect.getsource`, a section extractor, or a fixture — and the finding looks identical to a
true one. Measure in the same corpus the selector runs in, or the count means nothing.


^ATOM-X19C-BCK7 [desc:"CORE's two container-stamp guards (PRRD prrd-version/updated, and the governance-mirror version/synced-blob) — what each asserts, and the residue neither closes", keywords: prrd-version_is_stale my_hand_edit_did_not_bump_the_stamp why_does_the_PRRD_test_skip governance_mirror_synced-at_guard which_stamp_guards_does_CORE_have updated_field_predates_the_last_commit, ocd: 2026-08-12, lmd: 2026-08-12]

**CORE ships TWO container-stamp guards, and they exist because both fields had already gone
quietly wrong.** Neither is redundant with the other; they guard different documents with
different witnesses.

1. **`tests/test_prrd_trdd_pillars.py::TestOurOwnPRRDStampIsNotStale`** — `design/requirements/PRRD.md`.
   Three arms: a CLEAN-file arm (witness = the newest commit touching the file), a DIRTY-file arm
   (witness = the clock, because while the file is modified the newest commit has not moved and
   the clean arm is blind), and a PRECONDITION arm pinning that blindness so the two cannot
   silently merge. Plus well-formedness — a malformed `prrd-version:` makes the next
   `prrd-edit.py` bump restart at `0.1` and lose the document's history.
2. **`tests/test_governance_mirror_stamp.py`** — the bundled `GOVERNANCE-RULES.md` mirror.
   Asserts the POINTER (`version:` + `synced-blob:` + `synced-at:`), **never fetches**, because a
   network test collapses "stale" and "offline" into one red and a gate with two opposite correct
   responses on one signal gets switched off.

**The PRRD stamp was 52 days stale and the cause was NOT forgetfulness.** `prrd-edit.py`
already sets both fields on every mutation; `acbea84` edited the file BY HAND, so the tool's
invariant never applied. That is why these guards assert the ARTIFACT against git, not the tool
— a tool-side guard stays green through exactly this. Restored to `2.0` (the tool bumps MAJOR on
a golden change, and `G1.1 -> G1.2` is one) rather than inventing `1.6`, which would name a
version no reader could look up.

**Known residue, measured, do not assume it is covered:** `fresh stamp + body edited on the same
day` is GREEN on both arms. Only a content hash closes it; none is implemented. See
[[publish-and-validation-gate]]. Cross-tree provenance: `Emasoft/ai-maestro#145`.


^ATOM-53N0-V0IF [desc:"write_prrd in scripts/prrd-trdd/prrd_lib.py is atomic temp+rename because it re-emits the WHOLE PRRD — a failed plain write partially ERASED the project constitution (#54)", keywords: the_PRRD_came_back_half_empty_after_a_crash a_failed_write_destroyed_the_rules_file why_is_write_prrd_not_a_simple_write_text is_my_atomicity_test_actually_testing_anything os.replace_across_filesystems why_must_the_temp_file_be_a_sibling, ocd: 2026-08-13, lmd: 2026-08-13]

`write_prrd` in `scripts/prrd-trdd/prrd_lib.py` writes ATOMICALLY via temp+rename, and the reason
is severity, not tidiness: `render_prrd` re-emits the WHOLE document from a parsed model, so the
previous `p.write_text(render_prrd(doc))` truncated the target first. A crash, a full disk, or a
SIGKILL mid-write did not leave one rule wrong — it left the project's constitution PARTIALLY
ERASED (`edfdae9`, #54).

Three details carry the guarantee and NONE is incidental:

- **The temp is a SIBLING of the target.** `os.replace` is atomic only WITHIN one filesystem. A
  `/tmp` staging file silently degrades to a cross-device copy — and still passes on a dev box
  where `/tmp` and the repo are the same mount, so the regression is invisible exactly where it
  is tested.
- **`fsync` precedes the rename**, so the bytes are durable before the name points at them.
- **The `finally` unlink** is a no-op after a successful replace and removes the temp on every
  failure path, so a crash cannot litter `design/requirements/`.

Atomicity is not serialisation: the locking half of #54 landed separately — see `ATOM-JONB-6FIU` on this page. What proves this atomicity is tested rather than asserted is `ATOM-FLE3-FVEX`.

^ATOM-FLE3-FVEX [desc:"the write_prrd atomicity suite is only meaningful because of its 5th test — the falsification control that re-runs the OLD body and asserts it DOES destroy the file", keywords: my_atomicity_test_passes_but_would_it_pass_on_the_broken_version_too how_do_I_know_an_injected-failure_test_reaches_the_failure_window a_suite_that_became_a_tautology_without_anyone_noticing testing_os.replace_was_actually_called_not_just_that_content_changed, ocd: 2026-08-13, lmd: 2026-08-13]

The `write_prrd` atomicity suite (see `ATOM-53N0-V0IF` on this page) is meaningful ONLY because of
its fifth test. Every other assertion in it would ALSO pass against the old `write_text` one-liner,
because the interesting states exist only when a write dies partway — so passing proves nothing
about atomicity on its own.

The fifth test re-runs the OLD body against the SAME injected failure and asserts it DOES destroy
the file. That is the control: if it ever stops holding, the injection no longer reaches the
truncation window and the whole suite has quietly become a tautology that cannot fail.

Two assertions in the same suite exist for the same reason — that `os.replace` is actually CALLED
(not merely that the file's content changed, which a plain write also achieves), and that its
source is a SIBLING of the target, since the cross-device degradation has no other witness on a
box where the temp dir and the repo share a mount.

## Applies to
- [[publish-and-validation-gate]] — the release/validate gate: where the CPV validator
  ref is pinned (one constant, three sites) and why a `--strict` run can go red with
  zero content change.
- [[trdd-id-and-approval-vocabulary]] — the two ratified governance models CORE taught
  wrongly until 2026-07-21/22: the TRDD id (UPPERCASE base36, legacy lowercase ids
  permanently valid) and `min-approval-requirement:` (titles, not the retired numeric tiers).

## See also
- (lateral links to other functionality hubs, once they exist)


^ATOM-KHHQ-8HU7 [desc:"three test layers guard the 28 skills: structural contracts, frozen-CLI behavioural contracts, and the executable no-direct-API iron rule", keywords: what_tests_guard_the_skills is_there_a_check_that_skills_teach_real_commands how_is_the_no_direct_api_rule_enforced why_does_my_new_skill_fail_the_test_suite skill_contract_tests_layers, ocd: 2026-08-02, lmd: 2026-08-02]

Three layers guard the 28 skills / 14 commands. They are complementary — none subsumes another:

| file | layer | catches |
|---|---|---|
| `tests/test_skill_and_command_contracts.py` | **structural** (78) | `name:`/dir drift, empty description, a `/name` promise with no surface, README-vs-disk in BOTH directions, `allowed-tools` missing the script a wrapper teaches |
| `tests/test_skill_cli_contracts.py` | **behavioural** (15) | a taught flag or subcommand that does not exist in the frozen CLI's own `--help` — see [[publish-and-validation-gate]] for why publish runs it strictly |
| `tests/test_no_direct_api_calls.py` | **governance** (9) | any runnable instruction to call the ai-maestro server API directly (the iron rule; `core#11`) |

Each sweep layer also ships a **never-skipped anti-vacuity guard** — see the next atom.


^ATOM-KHHQ-8HU8 [desc:"every sweep-style skill test ships a never-skipped anti-vacuity guard, and the two extractors' scoping rules must not be tightened", keywords: my_skill_test_passes_but_checks_nothing anti_vacuity_guard_in_the_test_suite why_does_the_api_guard_ignore_comments extractor_scoping_rules_that_look_like_bugs indented_bash_fence_not_detected, ocd: 2026-08-02, lmd: 2026-08-02]

**Every sweep-style layer ships a never-skipped anti-vacuity guard**
(`test_the_corpus_is_not_empty`, `test_the_extractor_actually_extracts`,
`test_the_scanner_actually_scans`). Not ceremony: a sweep asserts only over what its extractor
returns, so an extractor that silently finds nothing turns every assertion above it into an
unconditional green. That bug has already happened here — an indented ```` ```bash ```` fence
inside a numbered list was invisible to the extractor, so the CLI contracts passed while
checking nothing, and only the guard caught it.

**Two scoping rules that look like bugs and are not** — do not "tighten" either:

- The API guard counts only RUNNABLE context (fenced blocks; non-comment code lines). A bare
  `grep '/api/'` matches 75 sites in this repo and **all 75 are the rule being stated**, not
  broken, so a content-only guard would redden loudest on its own prohibitions.
- The CLI extractor requires the CLI token on the same line, strips `$(...)` first, and cuts at
  shell separators. Without those it attributes a nested or piped command's flags to the outer
  CLI — it once reported `aimaestro-session.sh --cwd` when `--cwd` belonged to a nested
  `aimaestro-agent.sh`, and "fixing" that would have deleted a correct flag from a correct skill.


^ATOM-QH18-L06J [desc:"the agent-facing CLI census must scan commands/ as well as skills/ — grepping only skills/ reports false coverage gaps", keywords: cli_not_covered_by_any_skill coverage_audit_reported_gaps_that_are_not_real is_this_script_skill_faced amp_statusline_looks_uncovered, ocd: 2026-08-02, lmd: 2026-08-02]

**Scan BOTH `skills/` and `commands/` when auditing agent-facing CLI coverage.** A census over
`skills/` alone reported 6 uncovered CLIs on 2026-08-02; all 6 resolved:

- `amp-statusline.sh` — covered by `commands/amp-statusline.md`, invisible to a `skills/`-only grep
- `aimaestro-agent.py` — same surface as the covered `aimaestro-agent` / `.sh`
- `amp-helper.sh`, `amp-security.sh`, `aid-helper.sh`, `amp-name-resolve.sh` — internal libs,
  correctly NOT skill-faced (TRDD-P83T33EN). `amp-name-resolve.sh` is *sourced* by 5 amp entry
  points which expose `--name` themselves, so an agent never calls it directly.

Record deliberate exclusions in the commit that makes them, or the next sweep re-files them as
oversights.


^ATOM-KXTI-U3Q2 [desc:"the PreToolUse directory-guard ABSTAINS (emits nothing) wherever it has no jurisdiction; returning allow there is a permission bypass, not a no-op", keywords: directory_guard_returns_allow_or_abstains why_does_the_pretooluse_guard_emit_nothing permission_prompts_suppressed_by_our_own_hook non_agent_session_guard_behaviour is_it_safe_to_return_allow_from_our_guard, ocd: 2026-08-05, lmd: 2026-08-05]

`scripts/directory-guard.cjs` (PreToolUse, matcher `Bash|Write|Edit|NotebookEdit`) has exactly three
outcomes, and the third is load-bearing: **deny** where a sandboxed write escapes its root, **allow**
only where it affirmatively vouches for a write inside a resolved `AGENT_WORK_DIR`, and **abstain —
emit no stdout at all** on every path where it has no jurisdiction (an ordinary non-agent session, or
a tool outside the matcher).

`permissionDecision: "allow"` is NOT "step aside". It is an affirmative override that skips the
user's permission prompt AND their configured rules, so returning it from a no-jurisdiction path
silently auto-approves the four highest-risk tools for anyone who installs the plugin. That shipped
in 2.9.0–2.11.0 and was fixed in `0683e1b`; the guard reached that state by fixing an earlier
fail-CLOSED bug (#22, a deny that bricked every interactive session) and over-correcting straight to
allow, skipping abstain. Abstaining satisfies #22 equally well — it does not deny — without granting.

`tests/test_directory_guard_bash.py::test_non_agent_session_without_work_dir_abstains_instead_of_allowing`
requires EMPTY stdout and names `allow` explicitly in its failure message, so a future
over-correction fails loudly instead of passing as "not denied".


^ATOM-2JGQ-JEAV [desc:"CLAUDE.md claims the memory contract is repeated in each agents/ prompt, but CORE ships no agents at all — the stated safeguard does not exist", keywords: claude_md_says_agents_prompts_repeat_the_memory_contract does_core_ship_any_agents where_are_the_agent_prompts sub_agents_do_not_inherit_the_memory_contract agents_directory_missing, ocd: 2026-08-05, lmd: 2026-08-05]

`CLAUDE.md` (the PROACTIVE MEMORY CONTRACT section) states the contract "is repeated in each
`agents/` prompt for that reason", justifying it with "sub-agents inherit nothing". **CORE ships
zero agents**: there is no `agents/` directory, `plugin.json` has no `agents` key, and the only
files matching `*agent*` are SKILLS *about* agents (`agent-identity`, `agent-messaging`,
`ai-maestro-agents-management`, `agent-repo-workflow`).

So the safeguard the sentence promises is absent — any sub-agent CORE spawns receives no memory
contract, while the file asserts otherwise. Verified 2026-08-05. Left unfixed deliberately:
`CLAUDE.md` is the owner's instruction file, and the fix is a judgement call between dropping the
clause and actually adding the agent prompts it promises.

Related: `tests/test_claude_code_platform_contracts.py::test_no_agent_name_contains_a_colon` scans
`agents/` and therefore currently proves nothing (it guards `if ... .is_dir() else []`). That is
correct behaviour for an optional directory, not a broken glob — but it means the 2.1.218 colon
rule has no live coverage here.


^ATOM-N3UF-12WL [desc:"CORE registers 12 of Claude Code's 29 hook events; TeammateIdle is the one with a real AMP fit, deliberately NOT adopted pending a decision", keywords: which_hook_events_could_core_still_adopt teammate_idle_hook_for_amp_inbox how_many_hook_events_does_claude_code_have should_core_register_more_hooks unused_hook_events, ocd: 2026-08-05, lmd: 2026-08-05]

Claude Code 2.1.222 dispatches **29** hook events; CORE registers **12**, all valid (locked by
`test_every_registered_hook_event_is_one_claude_code_actually_dispatches`, commit `61db3f6`). The
authoritative list comes from the binary's own enum, not the docs:

    strings -a "$(readlink "$(command -v claude)")" | grep -A18 -x 'PreToolUse'

The 17 unregistered events are a DESIGN CHOICE, not a gap — each hook costs a process spawn per
occurrence. One is worth revisiting: **`TeammateIdle`**, which exposes `executeTeammateIdleHooks`
and the string "TeammateIdle hook prevented continuation", i.e. it can stop an idle teammate from
halting. That is a direct fit for AMP — an idle teammate could drain its inbox instead of stopping.

Deliberately NOT built (2026-08-05): adding it changes behaviour for every plugin inheriting CORE,
so it is a proposal awaiting the owner, not alignment work. Also unregistered and plausibly useful
later: `TaskCreated`/`TaskCompleted` (kanban), `DirectoryAdded`, `ConfigChange`.


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


^ATOM-JONB-6FIU [desc:"prrd_lib.prrd_lock mirrors ai-maestro withJsonLock byte-for-byte (<file>.lock mkdir-dir, 30s/20s/50ms) and must span each edit's whole parse-to-write, not just the write", keywords: two_writers_edit_the_prrd_concurrently lost_update_last_writer_wins_on_prrd prrd_lock_protocol_mkdir_lockdir why_does_prrd_lock_span_parse_to_write prrdgrep_and_prrd-edit_interop where_do_the_lock_constants_come_from, ocd: 2026-08-05, lmd: 2026-08-05]

Two independent writers edit `design/requirements/PRRD.md`: CORE's `prrd-edit.py` and
ai-maestro's `prrdgrep`. They exclude each other ONLY because the lock protocol matches
byte-for-byte — the lock is the DIRECTORY `<file>.lock` beside the target, acquired with a
bare non-recursive mkdir (EEXIST == held), stale-broken past 30s of lockdir mtime, released
by recursively deleting the lockdir, 20s max wait at 50ms polls (`prrd_lib.prrd_lock`,
shipped for #54). The constants were READ from `ai-maestro lib/json-io.ts::withJsonLock`,
never chosen — change them only in lockstep with that source. The lock must span each edit
op's WHOLE parse→write (as prrd-edit.py does): serialising only the write still loses
updates, because both editors parse the same base and the last full re-emission drops the
other's rule. `write_prrd` also takes the lock re-entrantly for direct library callers.
Real-process race + blocked-writer tests: `tests/test_prrd_write_lock.py`.


^ATOM-TKLL-H9B7 [desc:"ai-maestro-hook writeState has two CARRY-THROUGH fields (subagentCount, lastError) — a write that omits one must preserve the prior value, or a later event silently erases state a supervisor needs", keywords: hook_drops_state_after_the_next_event why_did_this_agent_stop lastError_missing errorType_gone_a_second_later subagentCount_reset_to_zero_mid_fanout, ocd: 2026-08-06, lmd: 2026-08-06]

`writeState` in `scripts/ai-maestro-hook.cjs` has TWO carry-through fields, and both exist
because a later event silently erased state a supervisor needed: `subagentCount` (#17) and
`lastError` (#58 — `status:'error'` and `errorType` describe only the CURRENT event, so the next
event of any kind made "why did this agent stop" unanswerable; the terminal cannot answer it
either, being a live tail that a scrolled-off error has left). `lastError` carries its own `at` so
a consumer judges staleness instead of being told nothing happened. An explicit value always wins
over the carry, so a handler resets deliberately (`subagentCount: 0`, `lastError: null`). [^4]

^ATOM-VN4C-8QRP [desc:"a GENERIC hook notification must never overwrite a more SPECIFIC classification that is still pending — Notification(permission_prompt) fires for AskUserQuestion blocks too and used to clobber the captured question", keywords: askuserquestion_not_captured_in_chat-state read-prompt_returns_null_but_a_menu_is_on_screen notificationType_is_permission_prompt_for_a_question blocked_agent_looks_healthy question_text_never_recorded, ocd: 2026-08-06, lmd: 2026-08-06]

The `Notification(permission_prompt)` handler must NOT clobber a pending `AskUserQuestion`.
Claude Code emits that notification for question blocks too, and the handler used to rebuild
state from a whitelist keeping only a recent `permission_request` — dropping `questions` and
downgrading `notificationType` from `question` to `permission_prompt` about a second after
`PreToolUse` had captured it. Measured server-side: question text captured **0 of 419** live
state files, so `read-prompt` answered `null` for the one prompt shape that blocks an agent
forever and a stalled agent read as healthy (#59). The invariant: **a GENERIC notification never
overwrites a more SPECIFIC classification that is still pending.** That carry-through takes **no
age bound** — `PostToolUse` is what ends the state, and a blocked agent stays blocked for hours
(17h observed), so any window would re-drop the question in exactly the case it exists for.


^ATOM-P29X-WO6W [desc:"A comm-graph 403 is evidence about AMP only: Claude Code 2.1.224's native SendMessage reaches another session with no server in the path, so a forbidden send returns nothing at all", keywords: 403_not_returned forbidden_send_no_error SendMessage_bypasses_the_comm_graph agent_messaged_another_agent_directly communication_graph_not_enforced ListAgents_cross-session AMP_is_the_only_channel_is_false R42.3_wording unpoliced_transport, ocd: 2026-08-08, lmd: 2026-08-08]

Claude Code **2.1.224** added `SendMessage` / `ListAgents` — a native session-to-session
transport between live Claude Code sessions on one machine that **never reaches the
ai-maestro server**. `validateMessageRoute()` is not consulted, so a forbidden edge over
that path returns **no** HTTP 403 `title_communication_forbidden`; nothing on it can.

**A 403 you never received is not permission.** R6 and R42 bind an agent on both
transports; only AMP can tell it when it broke them. `amp-send.sh` is the verb that gets
signed, routed, graph-checked and recorded.

Measured 2026-08-08 (`ai-maestro#131`, filed by the ASSISTANT role-plugin): **7 of 7**
role-plugin personas asserted server enforcement, **0 of 7** named the transport. CORE was
in the same state — 4 files asserting the 403, 0 mentioning `SendMessage` — which was worse,
because those personas inherit their messaging contract from CORE's `agent-messaging`.

Fixed in CORE v3.1.9 across `agent-messaging` (SKILL + detailed-guide) and `team-governance`
(SKILL + REFERENCE), guarded by
`tests/test_claude_code_platform_contracts.py::test_no_403_claim_travels_without_the_transport_that_cannot_return_one`.

The rule-text half is NOT fixed and is not CORE's: R42.3 ("messaging is the ONLY channel")
is false as written, and R42 is `CRITICAL — IRON, USER-set` ⇒ Tier 3. Tracked as A1 of
`TRDD-OH3N6OXJ`, open with the USER. The clean split: plugin text is each plugin's to fix
today; rule text is ONE user request, not seven reinterpretations.

## Notes and lessons learned
[^1]: [id:ATOM-ARCH-0001, status:valid, keywords:"install-governance-rules install a governance rule ~/.claude/rules SessionStart hook re-add rules directory", ocd:2026-07-23, lmd:2026-07-23]
  DO NOT re-add a `rules/` directory or an `install-governance-rules.cjs` SessionStart installer to
  CORE, BECAUSE the 3-pillars SPEC (`3P-BND`) assigns rule ownership away from CORE: IND universal
  bases → the ai-maestro-janitor (`~/.claude/rules/`), DEP overlays → ai-maestro (per agent-workdir
  `.claude/rules/aimaestro-*.md`). CORE shipping its own copies was redundant + generation-skewed
  (its INERT copy silently taught retired vocabulary while the janitor's copy actually won). DO leave
  CORE shipping zero governance rules and let its skills reference those two homes (retired core#35/#33).
  The universal home is not "hoped for": CORE declares a `dependencies[]` entry on `ai-maestro-janitor`
  in `.claude-plugin/plugin.json`, which GUARANTEES the janitor (and its `~/.claude/rules/` install) is
  present wherever CORE is — the sanctioned mechanism (plugin-dependencies spec). DO NOT "fix" a
  missing-rule worry by re-bundling; add/adjust the dependency instead.

[^2]: [id:ATOM-ARCH-0002, status:valid, keywords:"publish.py pyright errors kwargs not assignable _infer_bump_type _pid not accessed type gate mypy not pyright IDE diagnostics blocking", ocd:2026-07-24, lmd:2026-07-24]
  DO NOT "fix" the Pyright ✘ advisories the IDE shows on `scripts/publish.py` (the
  `(cmd, **kwargs)` callable-assignability on the `try/except ImportError`
  `gh_with_retry`/`git_with_retry` shim, and the `_`-prefixed unused `_infer_bump_type` /
  `_pid`), BECAUSE the pipeline's actual type gate is **mypy** (`mypy scripts/
  --ignore-missing-imports`), which passes clean — Pyright and mypy infer the import-shim
  union and unused module-level defs differently, and `_infer_bump_type` pre-existed at
  `6c1cf63` (not introduced by the CPV upgrade). DO run the gate command to judge type
  health, not the IDE Pyright panel; a green mypy is the authoritative signal.

[^3]: [id:ATOM-ARCH-0003, status:valid, keywords:"dependabot reports no alerts zero open alerts are the rust dependencies safe cargo crates never scanned dependency graph resolves no cargo memgrep vulnerable crate osv advisory check", ocd:2026-07-25, lmd:2026-07-25]
  DO NOT read "0 open Dependabot alerts" as evidence that memgrep's Rust dependencies are
  clean, BECAUSE the dependency graph for this repo resolves 15 packages (9 pypi, 5
  github-actions, 1 self) and **zero cargo** — while `scripts/memgrep/Cargo.lock` holds 125
  crates and has been on the default branch since `3de7401`. Alerts are genuinely ENABLED
  (`vulnerability-alerts` → 204, `dependabot_security_updates: enabled`) and genuinely
  return `[]`, which is what makes it dangerous: the empty list looks like a clean bill of
  health and is actually total blindness. Verified 2026-07-25 by querying OSV with the
  lockfile directly — **5 of 141 packages carried advisories**, including RUSTSEC-2026-0190
  in `anyhow`, a DIRECT dependency (fixed in `3334030`). This surface has the widest blast
  radius in the repo: memgrep ships as prebuilt release binaries consumed ecosystem-wide, so
  a vulnerable crate reaches every consumer as a compiled artifact with nothing ever
  alerting. DO audit crates against OSV (POST the lockfile's name+version pairs to
  `api.osv.dev/v1/querybatch`) and treat the alert count as covering only Actions and Python.
[^4]: [id:ATOM-IW75-RF2M, status:valid, desc:"writerVersion must come from __dirname, never $CLAUDE_PLUGIN_ROOT — a wrong stamp is worse than none (#60, 2026-08-06)", keywords:"plugin_version_stamp_on_chat-state writerVersion_field CLAUDE_PLUGIN_ROOT_wrong_plugin_version how_does_the_hook_know_its_own_version is_the_version_stamp_redundant stale_producer_detection", ocd:2026-08-06, lmd:2026-08-06] DO NOT resolve the plugin version (or any plugin-root path) inside `scripts/ai-maestro-hook.cjs` from `$CLAUDE_PLUGIN_ROOT`, and DO NOT drop the `writerVersion` stamp as redundant. BECAUSE that env var names whichever plugin's context spawned the hook process, not this plugin, so it can stamp ANOTHER plugin's version onto our state record — and a wrong stamp is worse than none, since `writerVersion` is the one field a fleet consumer trusts to decide the producer is current (it is what lets the server distinguish 'no question pending' from 'this agent still runs the #59 clobber bug', which demand opposite actions). DO resolve from `__dirname`, whose value is the file's own location and cannot be wrong; the regression test passes with `CLAUDE_PLUGIN_ROOT` deliberately pointed elsewhere, so keep it that way.
