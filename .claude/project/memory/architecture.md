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
