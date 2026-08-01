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
- **Skills** (`skills/`) — AMP messaging, AID identity, agent management, docs
  search, code-graph query, MCP discovery, planning, network security,
  conversation-transcript memory search (`memory-search`), and the `ama-*`
  PRRD/TRDD/Kanban governance skills.
- **Commands** (`commands/`) — the 12 `/amp-*` AMP slash commands.
- **Scripts** (`scripts/`) — AMP/AID shell scripts installed to PATH, the
  PRRD/TRDD/Kanban Python pillar scripts, `publish.py` (release pipeline),
  `install-memgrep.sh`, and the bundled `memgrep` Rust crate.
- **Rules** — CORE ships **zero** governance rules (retired core#35/#33, 2026-07-23).
  Per the 3-pillars SPEC ownership split: the IND universal bases
  (`trdd-design-tasks`, `prrd-design-rules`, `universal-kanban`) are shipped
  globally to `~/.claude/rules/` by the **ai-maestro-janitor**; the DEP overlays
  (`aimaestro-trdd-approval`, `aimaestro-manager-approval-defaults`, …) are seeded
  per agent-workdir by **ai-maestro**. CORE's skills reference those homes; the old
  `rules/` dir + `install-governance-rules.cjs` SessionStart installer were removed.
  CORE **declares a plugin dependency on `ai-maestro-janitor`** in
  `.claude-plugin/plugin.json` (`dependencies[]`, marketplace `ai-maestro-plugins`,
  `>=0.58.0`), so the janitor — and therefore its `~/.claude/rules/` IND bases — is
  GUARANTEED installed+enabled wherever CORE is, not merely assumed present.
- **Publish / CI pipeline** — `scripts/publish.py` is the canonical CPV release
  pipeline. **The validator pin and this gate's failure modes live on
  [[publish-and-validation-gate]]** — do not restate the version here; it has already
  gone stale once (this bullet still read `@v3.5.0` after two bumps). The ref is one
  constant mirrored at three sites, all of which move together; local
  `--gate` includes a **jscpd** copy-paste gate (**G3b**, #143) on top of the standard
  version/lint/validate gates. The **type gate is mypy** (`mypy scripts/
  --ignore-missing-imports`, in `release.yml` + publish.py G2), **not Pyright**.[^2]
- **Dependency scanning** — `.github/dependabot.yml` (added 2026-07-25, `886778d`)
  covers **github-actions**, **cargo** (`/scripts/memgrep`) and **uv**. Note that
  Dependabot **ALERTS** are a separate mechanism from this config, and for the Rust
  surface they are **blind**: the dependency graph resolves 0 cargo packages against
  125 crates in `scripts/memgrep/Cargo.lock`. Audit crates with **OSV**, never with
  the alert count.[^3]
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
