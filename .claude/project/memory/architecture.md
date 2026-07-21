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
- **Rules** (`rules/`) — the governance ruleset (`prrd-design-rules`,
  `trdd-design-tasks`, `trdd-approval-tiers`, `manager-approval-defaults`)
  installed via `install-governance-rules.cjs`.
- **Memory** — this plugin USES the janitor's global wiki-memory system (recall /
  write / update); see the PROACTIVE MEMORY CONTRACT in the repo CLAUDE.md.

## Applies to
- [[trdd-id-and-approval-vocabulary]] — the two ratified governance models CORE taught
  wrongly until 2026-07-21/22: the TRDD id (UPPERCASE base36, legacy lowercase ids
  permanently valid) and `min-approval-requirement:` (titles, not the retired numeric tiers).

## See also
- (lateral links to other functionality hubs, once they exist)

## Notes and lessons learned
