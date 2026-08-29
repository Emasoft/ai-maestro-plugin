---
name: test-guard-methodology
description: "why does my anti-vacuity test pass while checking nothing / first-match .find or .index selection bugs in test guards / is this .find a bug or correct / which stamp guards does CORE have / why does the PRRD stamp test skip / the CLI coverage census reports false gaps / do I need to scan commands/ as well as skills/ / anti-vacuity guard in the test suite / extractor scoping rules that look like bugs"
ocd: 2026-08-02
lmd: 2026-08-29
metadata:
  node_type: memory
  type: project
  tier: component
  globs: ["commands/**"]
publish-globally: false
split-lineage: cc9840b5939c4effac960eb58cab1b1e
---

# test-guard-methodology

Anti-vacuity and first-match-selection patterns across CORE's test suite — how a
guard can look green while asserting nothing, and which of the suite's
first-match `.find`/`.index` sites are real defects versus correct-as-written.

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

## Governed by
- [[architecture]] — the functionality hub this component sits under (its `## Applies to`
  carries the reciprocal link).

## See also
- [[publish-and-validation-gate]] — the validator pin and CI failure modes behind why
  `tests/test_skill_cli_contracts.py` runs strictly at publish time.

## Notes and lessons learned
(none yet)
