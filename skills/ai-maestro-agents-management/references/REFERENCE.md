# AI Maestro Agent Management — Full Reference

## Table of Contents

- [CLI Quick Reference](#cli-quick-reference)
- [Session and Data Preservation](#session-and-data-preservation)
- [Agent Lifecycle Commands](#agent-lifecycle-commands)
  - [List Agents](#1-list-agents)
  - [Create Agent](#2-create-agent)
  - [Show Agent](#3-show-agent)
  - [Update Agent](#4-update-agent)
  - [Rename Agent](#5-rename-agent)
  - [Delete Agent](#6-delete-agent)
  - [Hibernate Agent](#7-hibernate-agent)
  - [Wake Agent](#8-wake-agent)
  - [Restart Agent](#9-restart-agent)
  - [Export Agent](#10-export-agent)
  - [Import Agent](#11-import-agent)
- [Skill Management](#skill-management)
  - [List Skills](#12-list-skills)
  - [Install Skill](#13-install-skill)
  - [Uninstall Skill](#14-uninstall-skill)
  - [Add/Remove Skills in Registry](#15-addremove-skills-in-registry)
- [Plugin Management](#plugin-management)
  - [Normal Plugins vs Role Plugins](#normal-plugins-vs-role-plugins)
  - [List Plugins](#16-list-plugins)
  - [Install Plugin](#17-install-plugin)
  - [Uninstall Plugin](#18-uninstall-plugin)
  - [Enable/Disable Plugin](#19-enabledisable-plugin)
  - [Update, Reload, Validate, Clean](#20-update-reload-validate-clean)
  - [Manage Marketplaces](#21-manage-marketplaces)
- [MCP Servers](#22-mcp-servers)
- [LSP Servers](#23-lsp-servers)
- [Standalone Elements](#24-standalone-elements)
- [Session Management](#25-session-management)
- [Claude Code Configuration Reference](#claude-code-configuration-reference)
  - [Scope System](#scope-system)
  - [Configuration File Locations](#configuration-file-locations)
  - [Element Types](#element-types)
  - [Element Internal Structure](#element-internal-structure)
  - [Plugin Structure](#plugin-structure)
- [Output Formats](#output-formats)
- [Script Architecture](#script-architecture)
- [Scenarios](#scenarios)
- [Decision Guide](#decision-guide)
- [Troubleshooting](#troubleshooting)
- [Error Messages](#error-messages)

---

<!-- Decoupled per MANAGER core#11 (TRDD-90c8ad35): agents use the `aimaestro-agent.sh` CLI verbs (list/show/create/update/delete/rename/hibernate/wake/export/import/plugin/skill) — the primary surface shown in each section + the CLI Quick Reference table. The runnable raw-HTTP request blocks have been REMOVED; each section's `**Maps to:**` line documents the endpoint the verb wraps (reference only — never call `/api/*` directly). The governance/title bits in "Auto-install triggers" (`/api/governance/manager`, `/api/teams/.../chief-of-staff`, `ChangeTitle`) describe SERVER-side behaviour, not agent curls; the assign-MANAGER/COS-title verbs stay DECOUPLE-BLOCKED (gov-password residual class, pending an ai-maestro follow-up). -->

## CLI Quick Reference

| CLI Command | API Equivalent |
|-------------|----------------|
| `aimaestro-agent.sh list` | `GET /api/agents` |
| `aimaestro-agent.sh show <agent>` | `GET /api/agents/{id}` |
| `aimaestro-agent.sh create <name> --dir <path>` | `POST /api/agents` |
| `aimaestro-agent.sh update <agent> [opts]` | `PATCH /api/agents/{id}` |
| `aimaestro-agent.sh delete <agent> --confirm` | `DELETE /api/agents/{id}` |
| `aimaestro-agent.sh rename <old> <new>` | `PATCH /api/agents/{id}` with `name` field |
| `aimaestro-agent.sh hibernate <agent>` | `POST /api/agents/{id}/hibernate` |
| `aimaestro-agent.sh wake <agent>` | `POST /api/agents/{id}/wake` |
| `aimaestro-agent.sh export <agent>` | `GET /api/agents/{id}/export` |
| `aimaestro-agent.sh import <file>` | `POST /api/agents/import` |
| `aimaestro-agent.sh plugin list <agent>` | `GET /api/agents/{id}/local-plugins` |
| `aimaestro-agent.sh skill list <agent>` | `GET /api/agents/{id}/skills` |

---

## Session and Data Preservation

**NEVER destroy a tmux session or chat history for configuration changes.**

| Operation | Session Impact | Use Instead |
|-----------|---------------|-------------|
| Install/uninstall/switch plugin | Graceful restart (send `/exit`, re-launch `claude` in same session) | NEVER hibernate+wake |
| Update settings (task, model, tags, args) | No restart needed | Direct API/CLI update |
| Change role plugin | Uninstall old, install new, graceful restart | NEVER hibernate+wake |
| Rename agent | `tmux rename-session` (preserves session) | NEVER delete+recreate |

**Only `hibernate` and `delete --confirm` may destroy the tmux session.**

---

## Agent Lifecycle Commands

### 1. List Agents

```bash
aimaestro-agent.sh list --status online
```

Status filters: `offline`, `hibernated`, `all` (default). Output formats: `--format table` (default), `--format json`, `--format names`, `--json`, `-q` (quiet).

**API:** `GET http://localhost:23000/api/agents`

### 2. Create Agent

```bash
aimaestro-agent.sh create my-api --dir ~/projects/my-api
aimaestro-agent.sh create backend-service \
  --dir ~/projects/backend \
  --task "Implement user authentication with JWT" \
  --tags "api,auth,security"
aimaestro-agent.sh create debug-agent --dir ~/projects/debug -- --verbose --debug
```

**`--dir` is required.** Options: `-p/--program`, `-m/--model`, `--no-session`, `--no-folder`, `--force-folder`.

**What it does:** Checks name uniqueness, creates folder, inits git, creates CLAUDE.md, registers in AI Maestro, creates tmux session.

**Maps to:** `POST /api/agents` (handled by the CLI — never call it directly, core#11).

### 3. Show Agent

```bash
aimaestro-agent.sh show my-api
```

JSON output: `--format json`. Shows: ID, persona name, title, role, working directory, model, tags, task, session status, plugins, skills.

**API:** `GET http://localhost:23000/api/agents/{id}`

### 4. Update Agent

```bash
aimaestro-agent.sh update backend-api --task "Focus on payment integration"
aimaestro-agent.sh update backend-api --add-tag "critical"
aimaestro-agent.sh update backend-api --tags "api,payments,v2"
aimaestro-agent.sh update backend-api --remove-tag "deprecated"
aimaestro-agent.sh update backend-api --args "--continue --chrome"
aimaestro-agent.sh update backend-api --model opus
```

Options: `-t/--task`, `-m/--model`, `--tags`, `--add-tag`, `--remove-tag`, `--args`.

**Maps to:** `PATCH /api/agents/{id}` (handled by the CLI; additional fields available server-side: label, name, workingDirectory, avatar, role, team).

### 5. Rename Agent

```bash
aimaestro-agent.sh rename old-name new-name
aimaestro-agent.sh rename old-name new-name --rename-session --rename-folder -y
```

**Maps to:** `PATCH /api/agents/{id}` with the `name` field (handled by the CLI).

### 6. Delete Agent

```bash
aimaestro-agent.sh delete my-api --confirm
aimaestro-agent.sh delete my-api --confirm --keep-folder --keep-data
```

**Maps to:** `DELETE /api/agents/{id}` (handled by the CLI; the `--keep-folder` / `--keep-data` flags control retention, soft-delete by default).

### 7. Hibernate Agent

```bash
aimaestro-agent.sh hibernate my-api
```

Kills tmux session, preserves data/registry/memory/plugins. Agent can be woken later.

**API:** `POST http://localhost:23000/api/agents/{id}/hibernate`

### 8. Wake Agent

```bash
aimaestro-agent.sh wake my-api
aimaestro-agent.sh wake my-api --attach
```

Restores hibernated agent: creates tmux session, launches `claude`.

**API:** `POST http://localhost:23000/api/agents/{id}/wake`

### 9. Restart Agent

```bash
aimaestro-agent.sh restart my-api
aimaestro-agent.sh restart my-api --wait 5
```

Hibernate then wake. Default wait: 3s. Cannot restart your own session.

### 10. Export Agent

```bash
aimaestro-agent.sh export my-api
aimaestro-agent.sh export my-api -o /tmp/my-api-backup.agent.json
```

Default output: `<agent>.agent.json` in current directory.

**API:** `GET http://localhost:23000/api/agents/{id}/export` (save the response body to `agent-backup.json`)

### 11. Import Agent

```bash
aimaestro-agent.sh import my-api.agent.json
aimaestro-agent.sh import backup.agent.json --name new-agent --dir ~/projects/new
```

**Maps to:** `POST /api/agents/import` (handled by the CLI).

---

## Skill Management

### 12. List Skills

```bash
aimaestro-agent.sh skill list my-api
```

**API:** `GET http://localhost:23000/api/agents/{id}/skills`

### 13. Install Skill

```bash
aimaestro-agent.sh skill install my-api ./my-skill.skill
aimaestro-agent.sh skill install my-api ./path/to/skill-folder --scope project
aimaestro-agent.sh skill install my-api ./debug-skill --scope local --name debug-helper
```

Scopes: `user` (default), `project`, `local`.

### 14. Uninstall Skill

```bash
aimaestro-agent.sh skill uninstall my-api debug-helper
aimaestro-agent.sh skill uninstall my-api debug-helper --scope project
```

### 15. Add/Remove Skills in Registry

Registry commands manage metadata without filesystem changes.

```bash
aimaestro-agent.sh skill add my-api custom-skill --type custom --path /path/to/skill
aimaestro-agent.sh skill remove my-api custom-skill
```

**Registry vs Filesystem:** `list/add/remove` manage AI Maestro registry metadata. `install/uninstall` manage actual files on disk.

| Scope | Location | Access |
|-------|----------|--------|
| `user` | `~/.claude/skills/<name>/` | All projects |
| `project` | `<agent-dir>/.claude/skills/<name>/` | All collaborators |
| `local` | `<agent-dir>/.claude/skills/<name>/` | You only (gitignored) |

---

## Plugin Management

### Normal Plugins vs Role Plugins

**Normal plugins** add features (skills, hooks, MCP, etc.). Installed with any scope.

**Role plugins** define an agent's job specialization. Must pass the quad-match rule:

| # | Rule | Example |
|---|------|---------|
| 1 | `plugin.json` name matches directory name | `"name": "architect-agent"` |
| 2 | `<plugin-name>.agent.toml` exists at root | `architect-agent.agent.toml` |
| 3 | `[agent].name` in TOML matches plugin name | `name = "architect-agent"` |
| 4 | `agents/<plugin-name>-main-agent.md` exists | `agents/architect-agent-main-agent.md` |

| Aspect | Normal Plugin | Role Plugin |
|--------|--------------|-------------|
| Purpose | Add features | Define job specialization |
| Scope | User or local | Always local |
| Per agent | Multiple | One at a time |
| Has .agent.toml | No | Yes (required) |
| Stored in | Any marketplace | `ai-maestro-plugins` marketplace (8 defaults) or the local `ai-maestro-local-roles-marketplace` at `~/agents/role-plugins/marketplace/` (custom). For non-Claude clients the role-plugins container holds per-client subfolders (`marketplace-claude/`, `marketplace-codex/`, …); see R20 in the bundled governance rules. |

### Role-Plugin Installation Architecture

**Default role-plugins** (8 predefined, from `Emasoft/ai-maestro-plugins` marketplace — one per governance title per R11):

| Role Plugin | Governance Binding |
|-------------|-------------------|
| `ai-maestro-assistant-manager-agent` | Auto-installed when MANAGER title assigned |
| `ai-maestro-chief-of-staff` | Auto-installed when COS title assigned |
| `ai-maestro-orchestrator-agent` | Auto-installed when ORCHESTRATOR title assigned |
| `ai-maestro-architect-agent` | Auto-installed when ARCHITECT title assigned |
| `ai-maestro-integrator-agent` | Auto-installed when INTEGRATOR title assigned |
| `ai-maestro-programmer-agent` | Auto-installed when MEMBER title assigned |
| `ai-maestro-maintainer-agent` | Auto-installed when MAINTAINER title assigned |
| `ai-maestro-autonomous-agent` | Auto-installed when AUTONOMOUS title assigned (mandatory — no "no plugin" state per R11.3) |

**Custom role-plugins** — Created by Haephestos from `.agent.toml` profiles. Stored in the local `ai-maestro-local-roles-marketplace` container at `~/agents/role-plugins/marketplace/` (Claude-format) or `~/agents/role-plugins/marketplace-<client>/` for other clients. The container also has an `.abstract/` IR hub feeding all per-client emitters.

**Key principles:**

1. **On-demand install** — Role-plugins are NOT pre-installed. Downloaded when user selects from dropdown or governance title is assigned. Uses `claude plugin install <name> --scope local`.
2. **Always local scope** — All role-plugins use `--scope local` (agent's working directory only).
3. **One at a time** — An agent can have at most one active role-plugin. Installing a new one replaces the previous.

### Governance Title → Role-Plugin Binding

Per R11.1 every title (including AUTONOMOUS and MAINTAINER) has a default role-plugin; there is **no "no role-plugin" state** for a persisted agent. R11.6 lets multiple plugins serve one title (UI shows a dropdown when ≥2 are compatible).

| Title | Default Role-Plugin | Auto-installed? | Swap allowed? |
|-------|---------------------|:---------------:|:-------------:|
| MANAGER | `ai-maestro-assistant-manager-agent` | Yes | No (locked) |
| CHIEF-OF-STAFF | `ai-maestro-chief-of-staff` | Yes | No (locked) |
| ORCHESTRATOR | `ai-maestro-orchestrator-agent` | Yes | Yes (compatible plugin) |
| ARCHITECT | `ai-maestro-architect-agent` | Yes | Yes (compatible plugin) |
| INTEGRATOR | `ai-maestro-integrator-agent` | Yes | Yes (compatible plugin) |
| MEMBER | `ai-maestro-programmer-agent` | Yes | Yes (compatible plugin) |
| MAINTAINER | `ai-maestro-maintainer-agent` | Yes | Yes (compatible plugin) |
| AUTONOMOUS | `ai-maestro-autonomous-agent` | Yes | Yes (compatible plugin) |

**Auto-install triggers:**

- `POST /api/governance/manager` — assigns MANAGER → installs manager plugin
- `POST /api/teams/{id}/chief-of-staff` — assigns COS → installs COS plugin
- `POST /api/teams` with `type: "closed"` + `chiefOfStaffId` — creates team + auto-installs COS plugin
- `ChangeTitle(<title>)` (any title via `PATCH /api/agents/{id}`) — swaps to the title's default role-plugin
- `ChangeTeam` — joining a team auto-runs `ChangeTitle('member')`; leaving auto-runs `ChangeTitle('autonomous')`

Auto-installations are non-blocking: title assignment succeeds even if plugin install fails (per R17.9 the agent is flagged `corePluginMissing: true`).

### 16. List Plugins

```bash
aimaestro-agent.sh plugin list my-api
```

**API:** `GET http://localhost:23000/api/agents/{id}/local-plugins`

### 17. Install Plugin

```bash
aimaestro-agent.sh plugin install my-api my-plugin
aimaestro-agent.sh plugin install my-api my-plugin --scope local --no-restart
```

Scopes: `user` (default), `project`, `local`. Triggers graceful restart by default.

### 18. Uninstall Plugin

```bash
aimaestro-agent.sh plugin uninstall my-api my-plugin
aimaestro-agent.sh plugin uninstall my-api my-plugin --force
```

### 19. Enable/Disable Plugin

```bash
aimaestro-agent.sh plugin enable my-api my-plugin
aimaestro-agent.sh plugin disable my-api my-plugin
```

Per-project control with `--scope local`:

```bash
claude plugin disable plugin-name@marketplace-name --scope local
claude plugin enable plugin-name@marketplace-name --scope local
```

**Note:** Only plugins support per-project enable/disable. Standalone elements can only be shadowed by local elements with the same name.

A plugin may declare `"defaultEnabled": false` in `plugin.json` (2.1.154+) so it installs disabled; users opt in via `/plugin` or `claude plugin enable`. Dependency-aware (2.1.147+): `disable` refuses when another enabled plugin depends on the target, and `enable` force-enables transitive dependencies.

### 20. Update, Reload, Validate, Clean

```bash
aimaestro-agent.sh plugin update my-api my-plugin
aimaestro-agent.sh plugin reinstall my-api my-plugin
aimaestro-agent.sh plugin load my-api /path/to/plugin
aimaestro-agent.sh plugin validate my-api /path/to/plugin
aimaestro-agent.sh plugin clean my-api
aimaestro-agent.sh plugin clean my-api --dry-run
```

**Prune orphaned plugin dependencies (Claude Code 2.1.121+).** Removes
auto-installed plugins that are no longer referenced by any installed
plugin. Safe to run periodically; the host CLI handles the cleanup, no
AI Maestro round-trip is needed.

```bash
claude plugin prune
```

**Reload skills without restart (2.1.152+).** `/reload-skills` re-scans skill
directories live; a `SessionStart` hook may return `reloadSkills: true` to do the
same automatically. **Scaffold a new plugin (2.1.157+):** `claude plugin init
<name>` creates the skeleton under `.claude/skills`. Plugin-bundled stdio MCP
servers receive `CLAUDE_PROJECT_DIR` (2.1.157+) and `CLAUDE_CODE_SESSION_ID`
(2.1.169+) in their environment, matching hooks and Bash.

### 21. Manage Marketplaces

```bash
aimaestro-agent.sh plugin marketplace list my-api
aimaestro-agent.sh plugin marketplace add my-api owner/repo
aimaestro-agent.sh plugin marketplace add my-api https://github.com/o/r.git#v1.0.0
aimaestro-agent.sh plugin marketplace remove my-api my-marketplace --force
aimaestro-agent.sh plugin marketplace update my-api
aimaestro-agent.sh plugin marketplace update my-api my-marketplace
```

Source formats: `owner/repo`, `github:owner/repo`, HTTPS/SSH URLs, `#branch`, local paths.

---

## 22. MCP Servers

**Always use `claude mcp` CLI. Never edit `~/.claude.json` directly.**

```bash
# Add local-scoped (default)
claude mcp add --scope local --transport stdio <name> -- <command> [args...]
claude mcp add --scope local --transport http <name> <url>

# With env vars or auth headers
claude mcp add --scope local --transport stdio --env API_KEY=xxx myserver -- npx my-mcp-server
claude mcp add --scope local --transport http --header "Authorization: Bearer token" myapi https://api.example.com/mcp

# User-scoped / project-scoped
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp/
claude mcp add --scope project --transport http shared-api https://api.company.com/mcp

# List / get / remove
claude mcp list
claude mcp get <name>
claude mcp remove <name>

# Add from JSON
claude mcp add-json <name> '{"type":"http","url":"https://api.example.com/mcp"}'
```

Storage: user-scoped in `~/.claude.json` top-level, local-scoped in `~/.claude.json` under `projects[path]`, project-scoped in `.mcp.json`.

## 23. LSP Servers

LSP servers only exist inside plugins. No standalone LSP servers.

```bash
aimaestro-agent.sh plugin install my-api lsp-plugin-name
aimaestro-agent.sh plugin disable my-api lsp-plugin-name
aimaestro-agent.sh plugin enable my-api lsp-plugin-name
```

## 24. Standalone Elements

Skills, agents, rules, commands can be installed as standalone files:

```bash
# Skills — folder with SKILL.md
mkdir -p ~/.claude/skills/my-skill && cat > ~/.claude/skills/my-skill/SKILL.md << 'EOF'
---
description: My custom skill
---
# My Skill
Instructions here...
EOF

# Agents — .md files
cat > ~/.claude/agents/my-agent.md << 'EOF'
---
name: my-agent
description: Custom agent persona
---
You are a specialized agent...
EOF

# Rules — .md files
cat > ~/.claude/rules/my-rule.md << 'EOF'
# My Rule
Always follow this convention...
EOF

# Commands — .md files (trigger with /command-name)
cat > ~/.claude/commands/my-command.md << 'EOF'
---
description: My custom command
---
Execute this when the user runs /my-command...
EOF
```

User-scoped: `~/.claude/`. Local-scoped: `.claude/`. Local overrides user-level.

## 25. Session Management

```bash
aimaestro-agent.sh session add my-api
aimaestro-agent.sh session remove my-api --index 1
aimaestro-agent.sh session remove my-api --all
aimaestro-agent.sh session exec my-api "git status"
tmux attach-session -t my-api
```

---

## Claude Code Configuration Reference

### Scope System

| Scope | Meaning | Precedence |
|-------|---------|------------|
| `local` | Private to you in current project | Highest |
| `project` | Shared via version control | Middle |
| `user` | Across all your projects | Lowest |

### Configuration File Locations

| File | Stores | Managed by |
|------|--------|------------|
| `~/.claude.json` | MCP servers (user + local), plugin data | `claude mcp` CLI |
| `~/.claude/settings.json` | User-scoped settings | `claude config` |
| `.claude/settings.local.json` | Local-scoped settings | `claude config` |
| `.claude/settings.json` | Project-scoped settings | `claude config` |
| `.mcp.json` | Project-scoped MCP servers | `claude mcp add --scope project` |

### Element Types

| Element | Standalone? | In plugins? | Managed by |
|---------|------------|-------------|------------|
| Skills | Yes (folder+SKILL.md) | Yes | File ops |
| Agents | Yes (.md) | Yes | File ops |
| Rules | Yes (.md) | Yes | File ops |
| Commands | Yes (.md) | Yes | File ops |
| Hooks | Yes (settings.json) | Yes (hooks.json) | Settings edit |
| MCP Servers | Yes (`claude mcp`) | Yes (.mcp.json) | `claude mcp` CLI |
| LSP Servers | No | Yes (.lsp.json) | Plugin install |
| Output Styles | Yes (.md) | Yes | File ops |

### Element Internal Structure

**Skills** — Folder with `SKILL.md` + optional YAML frontmatter. Fields: `description`, `name`, `version`, `author`, `tags`, `globs`, `allowed-tools`, `disallowed-tools`. `disallowed-tools` (Claude Code 2.1.152+) removes the named tools from the model while the skill is active — the inverse of `allowed-tools`.

**Agents** — `.md` file with optional frontmatter. Fields: `name`, `description`, `model` (optional — omit to inherit the session model; pin only when a specific tier is required). A dispatched sub-agent may itself spawn sub-agents, nested up to 5 levels deep (2.1.172+); `subagent_type` matching is case- and separator-insensitive (2.1.140+, e.g. `"Code Reviewer"` resolves to `code-reviewer`).

**Rules** — `.md` file. First non-heading line used as preview.

**Commands** — `.md` file. Triggered with `/<filename>`. Fields: `description`, `argument-hint`, `allowed-tools`, `disallowed-tools` (2.1.152+). Quote any frontmatter value that starts with `[` (e.g. `argument-hint: "[path] [--flag]"`) so YAML does not parse it as a flow sequence.

**Hooks** — In `hooks/hooks.json` (plugins) or settings files. Fields: `event`, `matcher`, `command`, `type`, `sync`.

**MCP Servers** — Via `claude mcp add` or plugin `.mcp.json`. Fields: `type`, `command`+`args` or `url`, `env`, `headers`.

**LSP Servers** — Plugin `.lsp.json` only. Fields: `command`, `extensionToLanguage`.

**Output Styles** — `.md` in `output-styles/`. Fields: `name`, `description`, `keep-coding-instructions`.

### Plugin Structure

```
plugin-dir/
  .claude-plugin/plugin.json   # REQUIRED
  skills/                      # Optional
  agents/                      # Optional
  commands/                    # Optional
  hooks/hooks.json             # Optional
  rules/                       # Optional
  .mcp.json                    # Optional
  .lsp.json                    # Optional
  output-styles/               # Optional
```

---

## Output Formats

### List Output (table)

```
+--------------------+----------+---------------------------------+--------------+
| Agent              | Status   | Working Directory               | Tags         |
+--------------------+----------+---------------------------------+--------------+
| backend-api        | online   | ~/projects/backend              | api, prod    |
| frontend-dev       | online   | ~/projects/frontend             | ui           |
+--------------------+----------+---------------------------------+--------------+
```

### Show Output (pretty)

```
Agent: backend-api
  ID:          a1b2c3d4-e5f6-7890-abcd-ef1234567890
  Status:      online
  Program:     claude-code
  Model:       sonnet
  Created:     2025-01-15T10:30:00Z
  Working Directory: ~/projects/backend
  Sessions (1): [0] backend-api (online)
  Task: Implement REST API endpoints
  Skills (2): git-workflow, agent-messaging
  Tags: api, production, critical
```

---

## Script Architecture

- **`aimaestro-agent.sh`** — Thin dispatcher (~108 lines), routes commands.
- **`agent-helper.sh`** — Shared utilities: colors, `resolve_agent`, API URL resolution.
- **`agent-core.sh`** — Security scanning (ToxicSkills), validation, Claude CLI helpers.
- **`agent-commands.sh`** — CRUD: list, show, create, delete, update, rename, export, import.
- **`agent-session.sh`** — Session lifecycle: session add/remove/exec, hibernate, wake, restart.
- **`agent-skill.sh`** — Skill management: list/add/remove/install/uninstall.
- **`agent-plugin.sh`** — Plugin management (10 subcommands) + marketplace (4 subcommands).

All modules in `~/.local/bin/` (installed) or `scripts/` (source).

---

## Scenarios

### Set Up New Development Environment

```bash
aimaestro-agent.sh create backend-api --dir ~/projects/my-app/backend \
  --task "Build REST API" --tags "api,typescript"
aimaestro-agent.sh create frontend-ui --dir ~/projects/my-app/frontend \
  --task "Build React dashboard" --tags "react,frontend"
aimaestro-agent.sh list
```

### End of Day

```bash
aimaestro-agent.sh hibernate frontend-ui
aimaestro-agent.sh hibernate data-processor
```

### Resume Work

```bash
aimaestro-agent.sh wake frontend-ui --attach
```

### Backup and Restore

```bash
aimaestro-agent.sh export backend-api -o backups/backend-$(date +%Y%m%d).json
aimaestro-agent.sh import backups/backend-20250201.json --name new-api --dir ~/projects/new
```

### Install Marketplace and Plugins

```bash
aimaestro-agent.sh plugin marketplace add data-processor github:my-org/ai-plugins
aimaestro-agent.sh plugin install data-processor data-analysis-tool
```

---

## Decision Guide

| Goal | Command |
|------|---------|
| New project/agent | `create` |
| Free resources | `hibernate` |
| Resume work | `wake` |
| Change task/tags | `update` |
| Add Claude extensions | `plugin install` |
| Backup/migrate | `export` / `import` |

---

## Troubleshooting

**Agent not found:** `aimaestro-agent.sh list` then `tmux list-sessions`

**CLI not found:** `which aimaestro-agent.sh` — should be in `~/.local/bin`

**API not running:** request `http://localhost:23000/api/hosts/identity` with curl; if it does not answer, `pm2 restart ai-maestro`

**Agent stuck:** `aimaestro-agent.sh restart my-api`

**Plugin not loading:** `aimaestro-agent.sh plugin validate my-api /path` then restart.

**Cannot restart self:** Exit Claude Code (`/exit` or Ctrl+C), then run `claude` again.

---

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Agent name required" | Missing argument | Add agent name |
| "Agent working directory not found" | Dir deleted/moved | Update or recreate |
| "Claude CLI is required" | claude not installed | `npm i -g @anthropic-ai/claude-code` |
| "Failed to add marketplace" | Invalid URL/network | Check URL and connectivity |
| "Cannot restart the current session" | Restarting self | Exit and restart manually |
| "Failed to get API base URL" | API down | Check AI Maestro is running |

---

## References

- [AI Maestro Documentation](https://github.com/Emasoft/ai-maestro)
