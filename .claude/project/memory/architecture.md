---
name: architecture
description: "how does ai-maestro-plugin work — overview, the main parts (skills, AMP/AID scripts, PRRD/TRDD/Kanban governance, memgrep), where the key pieces live / are the dependencies safe / dependabot reports no alerts / why did a native cross-session send report refused and is the transport enforcing R6 now"
ocd: 2026-06-16
lmd: 2026-09-04
metadata:
  node_type: memory
  type: project
  tier: hub
  functionality: architecture
  globs: ["skills/**", "commands/**", "scripts/**", "rules/**", ".claude-plugin/**"]
publish-globally: false
split-lineage: cc9840b5939c4effac960eb58cab1b1e
---
^GZEM1EU9 [desc:"ai-maestro-plugin is the umbrella core plugin of the AI Maestro ecosystem: shared skills, AMP messaging, AID identity, governance, PRRD/TRDD/Kanban, and it hosts the memgrep recall engine", keywords: what_is_ai-maestro-plugin ai-maestro-plugin_overview what_does_the_core_plugin_do umbrella_plugin_ecosystem where_does_AMP_messaging_live where_does_AID_identity_live where_is_memgrep_hosted what_hosts_the_recall_engine PRRD_TRDD_Kanban_home core_plugin_scope]
ai-maestro-plugin is the umbrella core plugin of the AI Maestro ecosystem — the
shared skills, AMP inter-agent messaging, AID Ed25519 identity, governance, and
the universal PRRD/TRDD/Kanban workflow every role plugin inherits. It also
hosts the `memgrep` markdown-recall engine (Rust crate + prebuilt release-asset
binaries) consumed by the other ecosystem plugins.

## Parts map
^4ZM0NELC [desc:"skills/ ships 28 skills: AMP/AID/agent-mgmt/MCP-discovery/planning/network-security/memory-search, plus ama-* frozen-CLI wrappers each needing an allowed-tools Bash entry", keywords: how_many_skills_does_core_ship skills_directory_contents ama-_skill_wrappers frozen_CLI_wrapper_pattern allowed-tools_missing_looks_like_tool_missing permission_blocked_skill ama-session_ama-panel_ama-continuity wiki-memory_recall_skill memory-search_skill_location]
- **Skills** (`skills/`, 28) — AMP messaging, AID identity, agent management,
  MCP discovery, planning, network security, wiki-memory recall
  (`memory-search`), the `ama-*` PRRD/TRDD/Kanban governance skills, and the
  `ama-*` wrappers over ai-maestro's **frozen CLI** layer. The frozen-CLI
  wrappers are one-skill-per-script by convention (`ama-session`→`aimaestro-session.sh`,
  `ama-panel`→`…-panel.sh`, `ama-continuity`, `ama-portfolio`, `ama-settings`,
  `ama-statusline`), each declaring `allowed-tools: Bash(<script>:*)` — a skill
  that names a script without that entry is permission-blocked in a way that
  reads as "the tool is missing", so the allowed-tools line is not boilerplate.
^B9AJI64E [desc:"commands/ ships 14 slash commands: 12 amp-* commands plus /memory-search and /team-governance (added 2026-08-02)", keywords: how_many_commands_does_core_ship commands_directory_contents amp-_slash_commands_list memory-search_command team-governance_command_added_date slash_command_count]
- **Commands** (`commands/`) — 14: the 12 `/amp-*` AMP slash commands plus
  `/memory-search` and `/team-governance` (added 2026-08-02, D2).
^IGGD5U2I [desc:"scripts/ hosts AMP/AID shell scripts, the PRRD/TRDD/Kanban python pillar, and publish.py; CORE ships no memgrep crate or installer since ownership moved to ai-maestro-janitor", keywords: where_do_amp_aid_scripts_live does_core_ship_memgrep_crate memgrep_ownership_ai-maestro-janitor why_was_cargo_removed_from_core test_core_does_not_ship_a_rival_memgrep publish.py_location prrd_trdd_kanban_python_scripts]
- **Scripts** (`scripts/`) — AMP/AID shell scripts installed to PATH, the
  PRRD/TRDD/Kanban Python pillar scripts, and `publish.py` (release pipeline).
  **No memgrep crate and no installer**: ownership was ruled to the
  ai-maestro-janitor (`ai-maestro#106`, 2026-08-02) and CORE's copy — a strict
  subset under an identical `version = "0.1.0"` — was removed. CORE CONSUMES
  memgrep, it does not ship it. The guardrail is executable, not prose:
  `tests/test_memory_protocol_components.py::test_core_does_not_ship_a_rival_memgrep`
  fails if the crate, the installer, or the release job returns.
^UJT2B0PU [desc:"CORE ships zero governance rules; IND universal bases come from the janitor's rules dir, DEP overlays from ai-maestro per workdir, guaranteed by a plugin.json dependency with no version pin", keywords: does_core_ship_governance_rules where_do_trdd-design-tasks_prrd-design-rules_universal-kanban_live ai-maestro-janitor_dependency_guarantee install-governance-rules_removed core-35_core-33_retired plugin_dependencies_field_no_version_pin unconstrained_dependency_is_safer]
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
^MP7FE8YO [desc:"scripts/publish.py is the canonical CPV release pipeline; validator pin + gate failures live on publish-and-validation-gate; local --gate adds jscpd G3b; type gate is mypy, not pyright", keywords: what_runs_the_release_pipeline publish.py_canonical_gate jscpd_copy_paste_gate_G3b mypy_type_gate_not_pyright where_is_cpv_validator_version_pinned scripts_publish.py_gates]
- **Publish / CI pipeline** — `scripts/publish.py` is the canonical CPV release
  pipeline. **The validator pin and this gate's failure modes live on
  [[publish-and-validation-gate]]** — do not restate the version here; it has already
  gone stale once (this bullet still read `@v3.5.0` after two bumps). The ref is one
  constant mirrored at three sites, all of which move together; local
  `--gate` includes a **jscpd** copy-paste gate (**G3b**, #143) on top of the standard
  version/lint/validate gates. The **type gate is mypy**
  (`mypy scripts/ --ignore-missing-imports`, in `release.yml` + publish.py G2),
  **not Pyright**.[^2]
^ZYEFT734 [desc:"dependabot.yml (added 2026-07-25) covers github-actions and uv only; the cargo entry was removed with the crate so Rust dependencies are unscanned despite zero alerts looking clean", keywords: does_dependabot_scan_cargo_dependencies dependabot.yml_ecosystems_covered is_memgrep_rust_crate_scanned_for_vulnerabilities zero_dependabot_alerts_does_not_mean_safe rust_blindness_lesson_now_janitors cargo_entry_removed_2026-08-02]
- **Dependency scanning** — `.github/dependabot.yml` (added 2026-07-25, `886778d`)
  covers **github-actions** and **uv**. The **cargo** entry was REMOVED 2026-08-02
  with the crate: an ecosystem pointing at a deleted directory scans nothing while
  still looking like Rust coverage. The Rust-blindness lesson below is now the
  **janitor's** to own, and it transfers wholesale — that crate is what ships as
  prebuilt binaries ecosystem-wide.[^3]
^YMCTTVLA [desc:"this plugin uses the janitor's global wiki-memory system for recall/write/update; see the PROACTIVE MEMORY CONTRACT in the repo CLAUDE.md", keywords: how_does_memory_work_in_ai-maestro-plugin wiki-memory_system_janitor recall_write_update_memory_contract where_is_the_proactive_memory_contract_documented does_core_have_its_own_memory_system]
- **Memory** — this plugin USES the janitor's global wiki-memory system (recall /
  write / update); see the PROACTIVE MEMORY CONTRACT in the repo CLAUDE.md.

## Applies to
- [[publish-and-validation-gate]] — the release/validate gate: where the CPV validator
  ref is pinned (one constant, three sites) and why a `--strict` run can go red with
  zero content change.
- [[trdd-id-and-approval-vocabulary]] — the two ratified governance models CORE taught
  wrongly until 2026-07-21/22: the TRDD id (UPPERCASE base36, legacy lowercase ids
  permanently valid) and `min-approval-requirement:` (titles, not the retired numeric tiers).
- [[test-guard-methodology]] — anti-vacuity test-guard patterns across CORE's suite:
  first-match slice-selection bugs, the two container-stamp guards, and coverage-census
  scoping gaps.
- [[prrd-lib-atomicity-and-locking]] — `scripts/prrd-trdd/prrd_lib.py`'s atomic
  temp+rename `write_prrd` and the cross-process file lock two independent PRRD
  writers share.
- [[governance-mirror-sync]] — the vendored `GOVERNANCE-RULES.md` mirror: what its
  `branch:`/`synced-blob:` fields actually mean, why CORE tracks `main`, and the
  v5.2.0 contradiction-sweep result.
- [[hooks-runtime]] — `ai-maestro-hook.cjs`'s state-carry fields and
  `directory-guard.cjs`'s abstain/allow/deny contract.
- [[amp-native-transport]] — why a native cross-session `SendMessage` never returns a
  comm-graph 403, and what a 2.1.238 `refused` reply does and does not prove.

## See also
- (lateral links to other functionality hubs, once they exist)

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
