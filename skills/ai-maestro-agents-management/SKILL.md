---
name: ai-maestro-agents-management
user-invocable: false
description: "Manage AI agent lifecycle via CLI. Use when creating, listing, deleting, configuring, or looking up an agent's consolidated config (launch args, title, role-plugin, teams, GitHub repo, Docker, pending tasks, AID public key). Trigger with 'create an agent', 'list the agents', 'delete this agent', 'what is this agent's config / title / teams / AID key'. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-agent.sh:*), Bash(jq:*), Bash(tmux:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "3.3.1"
---

## Overview

Manage AI agents through the frozen `aimaestro-agent.sh` CLI (which resolves the API base + your agent identity internally — never call `/api/*` directly, R23). Covers the full agent lifecycle: creation, configuration, hibernation, plugin/skill management, import/export, and reading an agent's consolidated config (`config <agent>`). For inter-agent messaging, use the `agent-messaging` skill instead.

**Authorization & identity (R26–R28, security-first).** An agent's identity — **TITLE / ROLE / NAME / AID** — is **conferred** by the USER / MANAGER / own-team COS and is **immutable to the agent itself** (R26): creating or configuring an agent CONFERS identity; an agent never self-assigns or self-changes its own title/role/name/AID (NAME/AID change only on compromise, via the proper authority). Agents **self-install ONLY through this core plugin's skills** — this skill IS that install surface — after **MANAGER** (no team) / **own-COS** (in team) approval, and the **server CPV-scans every extension before install** (R27); never install via a raw client CLI or bypass the scan. Every operation authenticates by the caller's **AID**: the CLI sends it, the **server** runs the **3-check** (AID → derived TITLE → portfolio approval/mandate token) and never trusts a client-supplied id/title/scope, and the skill **never asserts its own title** (R28). Full text: the [`team-governance`](../team-governance/references/GOVERNANCE-RULES.md) bundled rules, R26–R28.

> **Recall first (proactive memory).** Before acting on a recurring problem, a design decision, or a repeated alert, recall prior lessons FIRST: `/janitor-memory-recall <symptom>` (shared wiki memory — index by the *symptom* / your words, not the fix's jargon) and `/memory-search <query>` (past discussion). See the proactive memory contract in the plugin `CLAUDE.md`.

The bundled [`GOVERNANCE-RULES.md`](../team-governance/references/GOVERNANCE-RULES.md) covers:

- §0. Canonical source + copies
- §TERMINOLOGY. Three-layer agent model (TITLE / ROLE / PERSONA)
- Overview
- R1. Teams and Groups
- R2. Team Name Rules
- R3. Role Hierarchy Rules
- R4. Agent Membership Rules
- R5. Transfer Rules
- R6. Messaging Rules (Communication Graph)
- R7. UI Robustness Rules
- R8. Data Integrity Rules
- R9. Manager Requirement
- R10. Agent Lifecycle Governance
- R11. Title-Plugin Binding
- R12. Minimum Team Composition (CRITICAL)
- R13. Role Boundaries (No Overstepping)
- R14. Team Resilience (Auto-Recovery)
- R15. Written Orders & GitHub Trail
- R16. Password Never Shared with Agents (CRITICAL)
- R17. Mandatory Core Plugin Installation (CRITICAL)
- R18. Plugin Continuity on Client Change (CRITICAL)
- R19. MAINTAINER Title
- R20. Marketplace Governance
- Invariants (Must Never Be Violated)
- R21. All-In-One Pipeline Architecture (CRITICAL — IRON)
- R22. GitHub Authorship Self-Identification (RESERVED — see issue #33)
- R23. Plugin↔Server Decoupling via the Frozen CLI Layer (CRITICAL — IRON)
- R24. Proactive Global Memory
- R25. Three-Pillars Task System (TRDD / PRRD / Kanban)
- R26. Identity Immutability — No Self-Mutation of Title / Role / Name / AID (CRITICAL — IRON)
- R27. Self-Install Only via Core-Plugin Skills, With Approval + CPV Scan (IRON)
- R28. Three-Check API Authorization (AID → Title → Portfolio Token) (CRITICAL — IRON)
- R29. MANAGER Team & Agent Lifecycle Authority (IRON)
- R30. COS Agent-Creation Requires a MANAGER Mandate; the 5-Member Base Is Invariant (IRON)
- R31. Incomplete-Team Freeze (IRON)
- R32. No Sudo Gates for Agents — AID Is Sufficient; Sudo Is USER-via-UI Only (CRITICAL — IRON)
- R33. Signed-Ledger Recovery of Agent Auth State (IRON)
- R34. The Signed Ledger Is the Ultimate Source of Truth (CRITICAL — IRON)
- R35. Foreign Agent/User Host Approval (CRITICAL — IRON)
- R36. Users Have AIDs; One MAESTRO Per Host (IRON)
- R37. MAESTRO and the Single MAESTRO-DELEGATE (CRITICAL — IRON)
- R38. Non-MAESTRO User Restrictions (IRON)
- R39. Users Have No Terminal/Client → the ASSISTANT Agent (CRITICAL — IRON)
- R40. Foreign-User Creation Approval (IRON)
- Role-Based Permission Matrix

## Prerequisites

- AI Maestro running (the `aimaestro-agent.sh` CLI resolves the API base + auth internally)
- `aimaestro-agent.sh` installed in `~/.local/bin/`
- tmux 3.0+, jq, Bash 4.0+

## Instructions

1. **Identify the operation** the user needs (create, list, show, config, update, delete, rename, hibernate, wake, restart, export, import, plugin/skill management).
2. **Run the CLI command** using `aimaestro-agent.sh <command> <agent> [options]`. Key commands:
   - `list [--status active|idle|offline]` — List agents. Exact match on the API's status enum, so the `online`/`hibernated` values the CLI's own `--help` advertises match nothing and exit 0 (ai-maestro#114)
   - `create <name> --dir <path> [--task "..."] [--tags "..."]` — Create agent
   - `show <agent>` — Show agent details
   - `config <agent>` — **One call, the consolidated config**: launch string/CLI args, governance title, role-plugin, teams, associated GitHub repo, whether it runs in Docker, pending tasks, and the AID public key
   - `update <agent> [--task|--tags|--model|--args]` — Update properties
   - `delete <agent> --confirm` — Delete agent
   - `hibernate <agent>` / `wake <agent>` — Suspend/restore
   - `restart <agent>` — Graceful restart
   - `export <agent>` / `import <file>` — Backup/restore
   - `plugin list|install|uninstall|enable|disable <agent> <plugin>`
   - `plugin marketplace list|add|remove|update <agent> <source>`
   - `skill list|install|uninstall|add|remove <agent> <skill>`
3. **Verify the result** by running `aimaestro-agent.sh show <agent>` or `list`.
4. **CRITICAL:** Never hibernate+wake for config changes. For plugin changes use a graceful restart — `aimaestro-continuity.sh restart-self [--force]` for your own session (feature-detect it first), or `aimaestro-agent.sh restart <agent>` for another agent. `/exit` + relaunch is the fallback for a host whose installed CLI predates `restart-self`, not the primary path. Use `update` for property changes (no restart needed). `config` is **read-only** — it never mutates anything; it's the one-call answer to "what is this agent's whole setup," not a setter.
5. **CRITICAL — self-configuration is always refused.** `config <agent>` is a read; it's fine on self. But **no agent may reconfigure itself** — role plugin, extensions, MCP, hooks, sub-agents, title, or team changes are refused on self for every title, MANAGER included (`TRDD-D3RP7KQZ`). Configuration changes on **another** agent go through this skill under the identity-immutability rules below (R26–R28) — never through `ama-session`'s terminal-drive verbs, which only reach an agent's own surface.

## Output

CLI returns formatted tables or JSON (`--format json`). API returns JSON. On success, exit code 0. On failure, descriptive error message and non-zero exit code.

## Error Handling

- If CLI not found: verify `~/.local/bin` is in PATH
- If API not responding: `pm2 restart ai-maestro`
- If agent not found: check `aimaestro-agent.sh list` and `tmux list-sessions`
- If plugin not loading after install: run `aimaestro-agent.sh restart <agent>`
- Restart own session: `aimaestro-continuity.sh restart-self [--force]` — it takes no target (the server derives the caller from its AID). Feature-detect it (`aimaestro-continuity.sh restart-self --help`) and only fall back to `/exit` + relaunch if the installed CLI lacks it; nothing propagates `scripts/*.sh` to `~/.local/bin` automatically (ai-maestro#56 §3)

## Examples

```bash
/ai-maestro-agents-management create my-api --dir ~/projects/api
```

Expected: Agent created with tmux session, registered in AI Maestro.

```bash
/ai-maestro-agents-management list --status online
```

Expected: Table of all online agents with status and working directory.

```bash
/ai-maestro-agents-management plugin install my-api my-plugin --scope local
```

Expected: Plugin installed, agent gracefully restarted.

```bash
/ai-maestro-agents-management config my-api
```

Expected: one JSON object — launch string/CLI args, governance title,
role-plugin, teams, associated GitHub repo, Docker yes/no, pending tasks,
and the AID public key. Read-only; no restart, no side effects.

## Checklist

Copy this checklist and track your progress:

- [ ] Identify target agent and operation
- [ ] Run the CLI command
- [ ] Verify result with `show` or `list`
- [ ] For plugin changes: confirm graceful restart completed
- [ ] For destructive ops (delete): confirm `--confirm` flag used

## Resources

- [Full CLI & API Reference](references/REFERENCE.md)
  - CLI Quick Reference
  - Session and Data Preservation
  - Agent Lifecycle Commands
  - List Agents
  - Create Agent
  - Show Agent
  - Get Consolidated Config
  - Update Agent
  - Rename Agent
  - Delete Agent
  - Hibernate Agent
  - Wake Agent
  - Restart Agent
  - Export Agent
  - Import Agent
  - Skill Management
  - List Skills
  - Install Skill
  - Uninstall Skill
  - Add/Remove Skills in Registry
  - Plugin Management
  - Normal Plugins vs Role Plugins
  - List Plugins
  - Install Plugin
  - Uninstall Plugin
  - Enable/Disable Plugin
  - Update, Reload, Validate, Clean
  - Manage Marketplaces
  - MCP Servers
  - LSP Servers
  - Standalone Elements
  - Session Management
  - Claude Code Configuration Reference
  - Scope System
  - Configuration File Locations
  - Element Types
  - Element Internal Structure
  - Plugin Structure
  - Output Formats
  - Script Architecture
  - Scenarios
  - Decision Guide
  - Troubleshooting
  - Error Messages
- Canonical governance rules (R3 titles, R10 lifecycle, R11 title-plugin
  binding, R17 mandatory `--scope local` install + R17.B core-plugin
  protection, R18 ChangeClient continuity, R20 marketplace governance;
  **R26 identity immutability, R27 self-install-only-via-core-skills +
  approval + CPV scan, R28 three-check AID authz**): see the
  `team-governance` skill, which bundles the canonical rules
  and embeds the full TOC.

## Use also

- `Skill(skill: "team-governance")` — assign agents to teams and govern titles.
- `Skill(skill: "agent-identity")` — the AID each managed agent authenticates by.
- `Skill(skill: "ama-session")` — an agent driving its **own** terminal/state
  (a different, narrower surface than this skill's lifecycle/configuration
  authority over agents in general).
