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

**API:** `curl http://localhost:23000/api/agents`

### 2. Create Agent

```bash
aimaestro-agent.sh create my-api --dir /Users/dev/projects/my-api
aimaestro-agent.sh create backend-service \
  --dir /Users/dev/projects/backend \
  --task "Implement user authentication with JWT" \
  --tags "api,auth,security"
aimaestro-agent.sh create debug-agent --dir /Users/dev/projects/debug -- --verbose --debug
```

**`--dir` is required.** Options: `-p/--program`, `-m/--model`, `--no-session`, `--no-folder`, `--force-folder`.

**What it does:** Checks name uniqueness, creates folder, inits git, creates CLAUDE.md, registers in AI Maestro, creates tmux session.

**API:**
```bash
curl -X POST http://localhost:23000/api/agents \
  -H "Content-Type: application/json" \
  -d '{"name":"my-api","workingDirectory":"/Users/dev/projects/my-api"}'
```

### 3. Show Agent

```bash
aimaestro-agent.sh show my-api
```

JSON output: `--format json`. Shows: ID, persona name, title, role, working directory, model, tags, task, session status, plugins, skills.

**API:** `curl http://localhost:23000/api/agents/{id}`

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

**API (additional fields: label, name, workingDirectory, avatar, role, team):**
```bash
curl -X PATCH http://localhost:23000/api/agents/{id} \
  -H "Content-Type: application/json" \
  -d '{"label":"Peter Bot","taskDescription":"Focus on payments"}'
```

### 5. Rename Agent

```bash
aimaestro-agent.sh rename old-name new-name
aimaestro-agent.sh rename old-name new-name --rename-session --rename-folder -y
```

**API:**
```bash
curl -X PATCH http://localhost:23000/api/agents/{id} \
  -H "Content-Type: application/json" \
  -d '{"name":"new-name"}'
```

### 6. Delete Agent

```bash
aimaestro-agent.sh delete my-api --confirm
aimaestro-agent.sh delete my-api --confirm --keep-folder --keep-data
```

**API (soft-delete default, `?hard=true` for permanent):**
```bash
curl -X DELETE http://localhost:23000/api/agents/{id}
curl -X DELETE "http://localhost:23000/api/agents/{id}?hard=true"
```

### 7. Hibernate Agent

```bash
aimaestro-agent.sh hibernate my-api
```

Kills tmux session, preserves data/registry/memory/plugins. Agent can be woken later.

**API:** `curl -X POST http://localhost:23000/api/agents/{id}/hibernate`

### 8. Wake Agent

```bash
aimaestro-agent.sh wake my-api
aimaestro-agent.sh wake my-api --attach
```

Restores hibernated agent: creates tmux session, launches `claude`.

**API:** `curl -X POST http://localhost:23000/api/agents/{id}/wake`

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

**API:** `curl http://localhost:23000/api/agents/{id}/export -o agent-backup.json`

### 11. Import Agent

```bash
aimaestro-agent.sh import my-api.agent.json
aimaestro-agent.sh import backup.agent.json --name new-agent --dir /Users/dev/projects/new
```

**API:**
```bash
curl -X POST http://localhost:23000/api/agents/import \
  -H "Content-Type: application/json" -d @agent-backup.json
```

---

## Skill Management

### 12. List Skills

```bash
aimaestro-agent.sh skill list my-api
```

**API:** `curl http://localhost:23000/api/agents/{id}/skills`

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
| Stored in | Any marketplace | `~/agents/role-plugins/` |

### 16. List Plugins

```bash
aimaestro-agent.sh plugin list my-api
```

**API:** `curl http://localhost:23000/api/agents/{id}/local-plugins`

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

### 20. Update, Reload, Validate, Clean

```bash
aimaestro-agent.sh plugin update my-api my-plugin
aimaestro-agent.sh plugin reinstall my-api my-plugin
aimaestro-agent.sh plugin load my-api /path/to/plugin
aimaestro-agent.sh plugin validate my-api /path/to/plugin
aimaestro-agent.sh plugin clean my-api
aimaestro-agent.sh plugin clean my-api --dry-run
```

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

**Skills** — Folder with `SKILL.md` + optional YAML frontmatter. Fields: `description`, `name`, `version`, `author`, `tags`, `globs`.

**Agents** — `.md` file with optional frontmatter. Fields: `name`, `description`, `model`.

**Rules** — `.md` file. First non-heading line used as preview.

**Commands** — `.md` file. Triggered with `/<filename>`. Field: `description`.

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
| backend-api        | online   | /Users/dev/projects/backend     | api, prod    |
| frontend-dev       | online   | /Users/dev/projects/frontend    | ui           |
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
  Working Directory: /Users/dev/projects/backend
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

**API not running:** `curl http://localhost:23000/api/hosts/identity` then `pm2 restart ai-maestro`

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

- [AI Maestro Documentation](https://github.com/23blocks-OS/ai-maestro)
- [Agent Registry Architecture](https://github.com/23blocks-OS/ai-maestro/blob/main/docs/AGENT-REGISTRY.md)
- [Plugin Development](https://github.com/23blocks-OS/ai-maestro/blob/main/docs/PLUGIN-DEVELOPMENT.md)
