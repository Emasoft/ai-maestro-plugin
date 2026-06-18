---
name: ai-maestro-agents-management
user-invocable: false
description: "Manage AI agent lifecycle via CLI. Use when creating, listing, deleting, or configuring agents. Trigger with /ai-maestro-agents-management. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-agent.sh:*), Bash(jq:*), Bash(tmux:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "3.2.0"
---

## Overview

Manage AI agents through the frozen `aimaestro-agent.sh` CLI (which resolves the API base + your agent identity internally — never call `/api/*` directly, R23). Covers the full agent lifecycle: creation, configuration, hibernation, plugin/skill management, and import/export. For inter-agent messaging, use the `agent-messaging` skill instead.

**Authorization & identity (R26–R28, security-first).** An agent's identity — **TITLE / ROLE / NAME / AID** — is **conferred** by the USER / MANAGER / own-team COS and is **immutable to the agent itself** (R26): creating or configuring an agent CONFERS identity; an agent never self-assigns or self-changes its own title/role/name/AID (NAME/AID change only on compromise, via the proper authority). Agents **self-install ONLY through this core plugin's skills** — this skill IS that install surface — after **MANAGER** (no team) / **own-COS** (in team) approval, and the **server CPV-scans every extension before install** (R27); never install via a raw client CLI or bypass the scan. Every operation authenticates by the caller's **AID**: the CLI sends it, the **server** runs the **3-check** (AID → derived TITLE → portfolio approval/mandate token) and never trusts a client-supplied id/title/scope, and the skill **never asserts its own title** (R28). Full text: the [`team-governance`](../team-governance/references/GOVERNANCE-RULES.md) bundled rules, R26–R28.

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

1. **Identify the operation** the user needs (create, list, show, update, delete, rename, hibernate, wake, restart, export, import, plugin/skill management).
2. **Run the CLI command** using `aimaestro-agent.sh <command> <agent> [options]`. Key commands:
   - `list [--status online|offline|hibernated]` — List agents
   - `create <name> --dir <path> [--task "..."] [--tags "..."]` — Create agent
   - `show <agent>` — Show agent details
   - `update <agent> [--task|--tags|--model|--args]` — Update properties
   - `delete <agent> --confirm` — Delete agent
   - `hibernate <agent>` / `wake <agent>` — Suspend/restore
   - `restart <agent>` — Graceful restart
   - `export <agent>` / `import <file>` — Backup/restore
   - `plugin list|install|uninstall|enable|disable <agent> <plugin>`
   - `plugin marketplace list|add|remove|update <agent> <source>`
   - `skill list|install|uninstall|add|remove <agent> <skill>`
3. **Verify the result** by running `aimaestro-agent.sh show <agent>` or `list`.
4. **CRITICAL:** Never hibernate+wake for config changes. Use graceful restart (send `/exit`, re-launch) for plugin changes. Use `update` for property changes (no restart needed).

## Output

CLI returns formatted tables or JSON (`--format json`). API returns JSON. On success, exit code 0. On failure, descriptive error message and non-zero exit code.

## Error Handling

- If CLI not found: verify `~/.local/bin` is in PATH
- If API not responding: `pm2 restart ai-maestro`
- If agent not found: check `aimaestro-agent.sh list` and `tmux list-sessions`
- If plugin not loading after install: run `aimaestro-agent.sh restart <agent>`
- Cannot restart own session: exit Claude Code (`/exit`), then run `claude` again

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
