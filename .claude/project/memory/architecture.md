---
name: architecture
description: "how does ai-maestro-plugin work — overview, the main parts (skills, AMP/AID scripts, PRRD/TRDD/Kanban governance, memgrep), where the key pieces live"
ocd: 2026-06-16
lmd: 2026-06-16
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
- **Memory** — this plugin USES the janitor's global wiki-memory system (recall /
  write / update); see the PROACTIVE MEMORY CONTRACT in the repo CLAUDE.md.

## Applies to
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
