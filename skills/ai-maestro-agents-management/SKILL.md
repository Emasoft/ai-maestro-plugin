---
name: ai-maestro-agents-management
description: Creates, manages, and orchestrates AI agents using the AI Maestro CLI. Use when the user asks to "create agent", "list agents", "delete agent", "rename agent", "hibernate agent", "wake agent", "install plugin", "show agent", "export agent", "restart agent", "install skill", "install marketplace", or any agent lifecycle management task.
allowed-tools: Bash
compatibility: Requires AI Maestro (aimaestro.dev) with Bash shell access
metadata:
  author: 23blocks
  version: 3.0.0
---

# AI Maestro Agent Management

Manage AI agents through the `aimaestro-agent.sh` CLI and the AI Maestro REST API.

This skill covers the full agent lifecycle: creation, configuration, hibernation, plugin/skill management, and import/export. For inter-agent messaging, use the `agent-messaging` skill instead.

## Session and Data Preservation (CRITICAL)

**NEVER destroy a tmux session or chat history for configuration changes.**

| Operation | Session Impact | Use Instead |
|-----------|---------------|-------------|
| Install/uninstall/switch plugin | Graceful restart (send `/exit`, re-launch `claude` in same session) | NEVER hibernate+wake |
| Update settings (task, model, tags, args) | No restart needed | Direct API/CLI update |
| Change role plugin | Uninstall old, install new, graceful restart | NEVER hibernate+wake |
| Rename agent | `tmux rename-session` (preserves session) | NEVER delete+recreate |

**Only `hibernate` and `delete --confirm` may destroy the tmux session.** Hibernate is intentional offline (session killed, data preserved). Delete is permanent removal (backup created first).

## Quick Reference

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

## USE CASES

### 1. List all online agents

See which agents are currently running.

```bash
aimaestro-agent.sh list --status online
```

Other status filters: `offline`, `hibernated`, `all` (default).

Output formats: `--format table` (default), `--format json`, `--format names`, `--json`, `-q` (quiet, names only).

**API:**
```bash
curl http://localhost:23000/api/agents
```

---

### 2. Create a new agent with a working directory

Provision a new agent and start its tmux session.

```bash
aimaestro-agent.sh create my-api --dir /Users/dev/projects/my-api
```

With a task description and tags:
```bash
aimaestro-agent.sh create backend-service \
  --dir /Users/dev/projects/backend \
  --task "Implement user authentication with JWT" \
  --tags "api,auth,security"
```

With extra program arguments passed to `claude`:
```bash
aimaestro-agent.sh create debug-agent --dir /Users/dev/projects/debug -- --verbose --debug
```

**`--dir` is required.** Additional options: `-p/--program`, `-m/--model`, `--no-session`, `--no-folder`, `--force-folder`.

**API:**
```bash
curl -X POST http://localhost:23000/api/agents \
  -H "Content-Type: application/json" \
  -d '{"name":"my-api","workingDirectory":"/Users/dev/projects/my-api"}'
```

---

### 3. Show agent details (persona, title, role, sessions)

Inspect a specific agent's full configuration.

```bash
aimaestro-agent.sh show my-api
```

JSON output: `--format json`.

Shows: agent ID, persona name (label), title (governance level), role (plugin specialization), working directory, model, tags, task, session status, installed plugins, and skills.

**API:**
```bash
curl http://localhost:23000/api/agents/{id}
```

---

### 4. Update agent properties (task, model, tags, args)

Change an agent's task, model, tags, or program arguments without restarting.

```bash
# Update task description
aimaestro-agent.sh update backend-api --task "Focus on payment integration"

# Add a tag
aimaestro-agent.sh update backend-api --add-tag "critical"

# Replace all tags
aimaestro-agent.sh update backend-api --tags "api,payments,v2"

# Remove a tag
aimaestro-agent.sh update backend-api --remove-tag "deprecated"

# Update program arguments
aimaestro-agent.sh update backend-api --args "--continue --chrome"

# Update AI model
aimaestro-agent.sh update backend-api --model opus
```

Options: `-t/--task`, `-m/--model`, `--tags`, `--add-tag`, `--remove-tag`, `--args`.

**API (supports additional fields: label, name, workingDirectory, avatar, role, team):**
```bash
curl -X PATCH http://localhost:23000/api/agents/{id} \
  -H "Content-Type: application/json" \
  -d '{"label":"Peter Bot","taskDescription":"Focus on payments"}'
```

---

### 5. Rename an agent

Change an agent's identity name. Optionally rename the tmux session and agent folder.

```bash
aimaestro-agent.sh rename old-name new-name
```

With automatic session and folder rename:
```bash
aimaestro-agent.sh rename old-name new-name --rename-session --rename-folder -y
```

**API:**
```bash
curl -X PATCH http://localhost:23000/api/agents/{id} \
  -H "Content-Type: application/json" \
  -d '{"name":"new-name"}'
```

---

### 6. Delete an agent

Permanently remove an agent. Requires explicit confirmation.

```bash
aimaestro-agent.sh delete my-api --confirm
```

Preserve agent folder or data:
```bash
aimaestro-agent.sh delete my-api --confirm --keep-folder --keep-data
```

**API (soft-delete by default, add `?hard=true` for permanent):**
```bash
curl -X DELETE http://localhost:23000/api/agents/{id}
curl -X DELETE "http://localhost:23000/api/agents/{id}?hard=true"
```

---

### 7. Hibernate an agent

Suspend an agent by killing its tmux session. Agent data (registry, memory, plugins) is preserved. The agent can be woken later.

```bash
aimaestro-agent.sh hibernate my-api
```

**API:**
```bash
curl -X POST http://localhost:23000/api/agents/{id}/hibernate
```

---

### 8. Wake an agent and optionally attach to it

Restore a hibernated agent by creating a new tmux session and launching `claude`.

```bash
aimaestro-agent.sh wake my-api
```

Wake and immediately attach to the tmux session:
```bash
aimaestro-agent.sh wake my-api --attach
```

**API:**
```bash
curl -X POST http://localhost:23000/api/agents/{id}/wake
```

---

### 9. Restart an agent (graceful)

Hibernate then immediately wake. Useful when configuration changes require a session restart.

```bash
aimaestro-agent.sh restart my-api
```

With custom wait time between hibernate and wake:
```bash
aimaestro-agent.sh restart my-api --wait 5
```

Default wait: 3 seconds. Cannot restart the session you are currently attached to.

---

### 10. Export an agent to a file

Create a portable agent export containing configuration, metadata, and settings.

```bash
aimaestro-agent.sh export my-api
```

Custom output path:
```bash
aimaestro-agent.sh export my-api -o /tmp/my-api-backup.agent.json
```

Default output: `<agent>.agent.json` in the current directory.

**API:**
```bash
curl http://localhost:23000/api/agents/{id}/export -o agent-backup.json
```

---

### 11. Import an agent from a file

Restore an agent from a previously exported file.

```bash
aimaestro-agent.sh import my-api.agent.json
```

Override name or directory during import:
```bash
aimaestro-agent.sh import backup.agent.json --name new-agent --dir /Users/dev/projects/new
```

**API:**
```bash
curl -X POST http://localhost:23000/api/agents/import \
  -H "Content-Type: application/json" \
  -d @agent-backup.json
```

---

### 12. List agent's installed skills

See all skills registered for an agent.

```bash
aimaestro-agent.sh skill list my-api
```

**API:**
```bash
curl http://localhost:23000/api/agents/{id}/skills
```

---

### 13. Install a skill on an agent

Add a skill from a file or directory.

```bash
# Install from a .skill file
aimaestro-agent.sh skill install my-api ./my-skill.skill

# Install from a directory with project scope
aimaestro-agent.sh skill install my-api ./path/to/skill-folder --scope project

# Install with a custom name
aimaestro-agent.sh skill install my-api ./debug-skill --scope local --name debug-helper
```

Scopes: `user` (default, `~/.claude/skills/`), `project` (`.claude/skills/`), `local` (project-local).

---

### 14. Uninstall a skill from an agent

Remove a skill by name.

```bash
aimaestro-agent.sh skill uninstall my-api debug-helper
```

With explicit scope:
```bash
aimaestro-agent.sh skill uninstall my-api debug-helper --scope project
```

---

### 15. Add/remove skills in agent registry

Manage the agent's skill registry (metadata tracking) without filesystem changes.

```bash
# Add a skill to the registry
aimaestro-agent.sh skill add my-api custom-skill --type custom --path /path/to/skill

# Remove from registry
aimaestro-agent.sh skill remove my-api custom-skill
```

---

## Normal Plugins vs Role Plugins

Claude Code has two kinds of plugins. Understanding the difference is essential.

### Normal Plugins

A **normal plugin** is any Claude Code plugin that adds functionality: skills, commands, hooks, rules, MCP servers, LSP servers, or output styles. It can have **any combination** of these elements.

**Detection:** A directory is a plugin if it contains any of:
`.claude-plugin/plugin.json`, `skills/`, `agents/`, `commands/`, `hooks/`, `rules/`, `.mcp.json`, `.lsp.json`, `output-styles/`

**Scope:** Installed with `--scope user` (all agents) or `--scope local` (one agent's project).

**Examples:** grepika, rechecker-plugin, claude-plugins-validation, llm-externalizer

### Role Plugins

A **role plugin** is a specialized normal plugin that defines an agent's **job specialization** (its Role). It bundles the persona, skills, hooks, rules, and configurations needed for a specific role like "architect" or "programmer".

**Role plugins are normal plugins with extra structure.** They must pass the **quad-match rule** (all 4 required):

| # | Rule | Example |
|---|------|---------|
| 1 | `plugin.json` name matches plugin directory name | `"name": "architect-agent"` |
| 2 | `<plugin-name>.agent.toml` exists at plugin root | `architect-agent.agent.toml` |
| 3 | `[agent].name` in TOML matches plugin name | `name = "architect-agent"` |
| 4 | `agents/<plugin-name>-main-agent.md` exists | `agents/architect-agent-main-agent.md` |

**Scope:** Always installed with `--scope local` in the agent's project directory.

**Key differences from normal plugins:**

| Aspect | Normal Plugin | Role Plugin |
|--------|--------------|-------------|
| Purpose | Add features (MCP, skills, hooks, etc.) | Define agent job specialization |
| Scope | User or local | Always local |
| Per agent | Multiple allowed | One at a time |
| Has .agent.toml | No | Yes (required) |
| Has main agent .md | Optional | Required |
| Switching | Install/uninstall freely | Uninstall old, install new, restart |
| Created by | Anyone | Haephestos or manually |
| Stored in | Any marketplace | `~/agents/role-plugins/` marketplace |

**An agent can have one role plugin AND many normal plugins simultaneously.** The role plugin defines what the agent IS; normal plugins add what the agent CAN DO.

---

### 16. List agent's installed plugins

See all Claude Code plugins installed for an agent.

```bash
aimaestro-agent.sh plugin list my-api
```

**API:**
```bash
curl http://localhost:23000/api/agents/{id}/local-plugins
```

---

### 17. Install a plugin on an agent

Install a Claude Code plugin. Triggers a graceful restart by default.

```bash
aimaestro-agent.sh plugin install my-api my-plugin
```

With scope and no restart:
```bash
aimaestro-agent.sh plugin install my-api my-plugin --scope local --no-restart
```

Scopes: `user` (default), `project`, `local`.

---

### 18. Uninstall a plugin from an agent

Remove a Claude Code plugin.

```bash
aimaestro-agent.sh plugin uninstall my-api my-plugin
```

Force uninstall (skip confirmation):
```bash
aimaestro-agent.sh plugin uninstall my-api my-plugin --force
```

---

### 19. Enable or disable a plugin

Toggle a plugin on or off without uninstalling it.

```bash
aimaestro-agent.sh plugin enable my-api my-plugin
aimaestro-agent.sh plugin disable my-api my-plugin
```

**Per-project plugin control (local scope):**

Plugins are installed at user level, but can be enabled or disabled per project using `--scope local`:

```bash
# Disable a user-level plugin only in this project
claude plugin disable plugin-name@marketplace-name --scope local

# Enable a plugin locally even if disabled at user level
claude plugin enable plugin-name@marketplace-name --scope local
```

The `plugin-name@marketplace-name` format is required. Find the correct key with:
```bash
claude plugin list
```

**Important**: There is NO way to selectively enable/disable user-level standalone elements (skills, agents, rules, commands) per project. Only plugins support per-project enable/disable. For standalone elements, the only override mechanism is placing a local element with the same name in `.claude/` — it will shadow the user-level one.

---

### 20. Update, reload, validate, or clean plugins

```bash
# Update a plugin to the latest version
aimaestro-agent.sh plugin update my-api my-plugin

# Reinstall a plugin (uninstall + install)
aimaestro-agent.sh plugin reinstall my-api my-plugin

# Load a plugin for the current session only (not persisted)
aimaestro-agent.sh plugin load my-api /path/to/plugin

# Validate a plugin's structure
aimaestro-agent.sh plugin validate my-api /path/to/plugin

# Clean stale plugin cache
aimaestro-agent.sh plugin clean my-api
aimaestro-agent.sh plugin clean my-api --dry-run
```

---

### 21. Manage plugin marketplaces

Add, remove, list, or update plugin marketplace sources.

```bash
# List marketplaces for an agent
aimaestro-agent.sh plugin marketplace list my-api

# Add a marketplace from a GitHub repo
aimaestro-agent.sh plugin marketplace add my-api owner/repo

# Add from a specific branch or tag
aimaestro-agent.sh plugin marketplace add my-api https://github.com/o/r.git#v1.0.0

# Remove a marketplace
aimaestro-agent.sh plugin marketplace remove my-api my-marketplace --force

# Update all or a specific marketplace
aimaestro-agent.sh plugin marketplace update my-api
aimaestro-agent.sh plugin marketplace update my-api my-marketplace
```

Source formats: `owner/repo`, `github:owner/repo`, HTTPS/SSH Git URLs, `#branch`, local directory paths.

---

## Claude Code Configuration Reference (Single Source of Truth)

### Scope System

Claude Code uses three scopes for elements and configuration. Higher scopes override lower ones.

| Scope | Meaning | Who can see it |
|-------|---------|----------------|
| `local` (default) | Private to you in the current project | Only you, only in this project |
| `project` | Shared with the team via version control | Everyone working on this project |
| `user` | Available to you across all projects | Only you, in all projects |

**Precedence**: local > project > user. A local element with the same name as a user element overrides it.

### Configuration File Locations

| File | What it stores | Managed by |
|------|---------------|------------|
| `~/.claude.json` | User-scoped MCP servers (top-level `mcpServers`), local-scoped MCP servers (under `projects[path].mcpServers`), plugin data, agent defaults | `claude mcp` CLI for MCP; Claude Code internals for the rest |
| `~/.claude/settings.json` | User-scoped settings (shared by all your projects) | `claude config` or direct edit |
| `.claude/settings.local.json` | Local-scoped settings (private to you in this project) | `claude config` or direct edit |
| `.claude/settings.json` | Project-scoped settings (shared via VCS) | `claude config` or direct edit |
| `.mcp.json` (project root) | Project-scoped MCP servers (shared via VCS) | `claude mcp add --scope project` |
| `~/.claude/skills/` | User-scoped standalone skills | Manual file management |
| `~/.claude/agents/` | User-scoped standalone agent definitions | Manual file management |
| `~/.claude/rules/` | User-scoped standalone rules | Manual file management |
| `~/.claude/commands/` | User-scoped standalone commands | Manual file management |
| `.claude/skills/` | Local-scoped standalone skills | Manual file management |
| `.claude/agents/` | Local-scoped standalone agent definitions | Manual file management |
| `.claude/rules/` | Local-scoped standalone rules | Manual file management |
| `.claude/commands/` | Local-scoped standalone commands | Manual file management |

**IMPORTANT**: Never edit `~/.claude.json` directly. Use the appropriate CLI commands.

### Element Types and Where They Live

| Element | Can be standalone? | Can be in plugins? | Managed by |
|---------|-------------------|-------------------|------------|
| Skills | YES (folder with SKILL.md) | YES | File operations (create/delete folder) |
| Agents | YES (.md file) | YES | File operations (create/delete .md) |
| Rules | YES (.md file) | YES | File operations (create/delete .md) |
| Commands | YES (.md file) | YES | File operations (create/delete .md) |
| Hooks | YES (in settings.json) | YES (hooks/hooks.json) | Settings edit or `/hooks` menu |
| MCP Servers | YES (via `claude mcp add`) | YES (.mcp.json in plugin) | `claude mcp` CLI only |
| LSP Servers | **NO — only inside plugins** | YES (.lsp.json in plugin) | Plugin install/uninstall |
| Output Styles | YES (file) | YES | File operations |
| Plugins | N/A | N/A | `claude plugin` CLI |
| Marketplaces | N/A | N/A | `claude plugin marketplace` CLI |

### Element Internal Structure

**Skills** — Each skill is a folder containing a `SKILL.md` file with optional YAML frontmatter:
```
skills/my-skill/SKILL.md
```
Frontmatter fields (all optional): `description`, `name`, `version`, `author`, `tags`, `globs`, and any custom fields. All frontmatter fields are extracted and displayed in the UI.

**Agents** — Each agent is a `.md` file in the agents/ directory with optional YAML frontmatter:
```
agents/my-agent.md
```
Frontmatter fields: `name`, `description`, `model`, and any custom fields.

**Rules** — Each rule is a `.md` file in the rules/ directory:
```
rules/my-rule.md
```
The first non-heading, non-empty line is used as a preview/description.

**Commands** — Each command is a `.md` file in the commands/ directory:
```
commands/my-command.md
```
Triggered with `/<filename>` (without .md extension). Frontmatter field `description` is used in UI.

**Hooks** — Defined in `hooks/hooks.json` (inside plugins) or in `settings.json` / `settings.local.json` (standalone). Each hook has:
- `event`: The trigger event type (e.g. `PreToolUse`, `PostToolUse`, `Stop`)
- `matcher`: Pattern to match (e.g. tool name, `*` for all)
- `command`: Shell command to execute
- `type`: `"prompt"` for prompt-type hooks (inject text into conversation) or omitted for command hooks
- `sync`: `true` for blocking (waits for result), `false`/omitted for async

Hook naming convention (auto-generated for display):
```
{event}_{type}_{scriptName}_{matcher}_{sync|async}_{pluginName}_hook_{N}
```
Example: `PreToolUse_command_tldr-read-enforcer_Read_async_my-plugin_hook_1`

**MCP Servers** — Defined via `claude mcp add` CLI (stored in `~/.claude.json`) or bundled in plugin `.mcp.json`. Each server has:
- `type`: `"stdio"`, `"http"`, or `"sse"`
- `command` + `args` (for stdio) or `url` (for http/sse)
- `env`: Environment variables
- `headers`: HTTP headers (for http/sse)
- `${CLAUDE_PLUGIN_ROOT}` variable resolved to plugin install directory in plugin `.mcp.json`

**LSP Servers** — Only in plugin `.lsp.json` files. Each server has:
- `command`: Server executable
- `extensionToLanguage`: Map of file extensions to language IDs
- Languages derived from `extensionToLanguage` values

**Output Styles** — Markdown files in the `output-styles/` directory that modify Claude Code's system prompt:
```
output-styles/my-style.md
```
Standalone: `~/.claude/output-styles/` (user) or `.claude/output-styles/` (project/local).
Frontmatter fields: `name`, `description`, `keep-coding-instructions` (boolean, default false).
When `keep-coding-instructions` is false, coding-specific instructions are removed from the system prompt.
Active style set via `outputStyle` field in settings or `/config` menu.

### Plugin Structure

A Claude Code plugin is a directory containing at minimum `.claude-plugin/plugin.json`. Detection criteria:
```
plugin-dir/
  .claude-plugin/
    plugin.json          # REQUIRED — manifest with name, version, description
    marketplace.json     # Optional — marketplace metadata
  skills/                # Optional — bundled skills (each subfolder with SKILL.md)
  agents/                # Optional — bundled agent .md files
  commands/              # Optional — bundled command .md files
  hooks/
    hooks.json           # Optional — bundled hooks
  rules/                 # Optional — bundled rule .md files
  .mcp.json              # Optional — bundled MCP servers
  .lsp.json              # Optional — bundled LSP servers
  output-styles/         # Optional — bundled output styles
```

Plugins are installed at user level (even with `--scope local`). The `--scope local` flag for plugins controls enable/disable state per project, NOT install location.

### 22. Manage MCP servers

MCP (Model Context Protocol) servers give Claude access to external tools, databases, and APIs.

**CRITICAL RULE**: Always use `claude mcp` CLI to add/remove/modify MCP servers. Never edit `~/.claude.json` directly. Reading `~/.claude.json` for display purposes is acceptable.

**Add a local-scoped MCP server (default — private to you in this project):**
```bash
# stdio transport (local process)
claude mcp add --scope local --transport stdio <name> -- <command> [args...]
claude mcp add --scope local --transport stdio airtable -- npx -y airtable-mcp-server

# HTTP transport (remote server)
claude mcp add --scope local --transport http <name> <url>
claude mcp add --scope local --transport http notion https://mcp.notion.com/mcp

# SSE transport (deprecated, use HTTP instead)
claude mcp add --scope local --transport sse <name> <url>

# With environment variables
claude mcp add --scope local --transport stdio --env API_KEY=xxx myserver -- npx my-mcp-server

# With authentication header
claude mcp add --scope local --transport http --header "Authorization: Bearer token" myapi https://api.example.com/mcp
```

**Add a user-scoped MCP server (available across all your projects):**
```bash
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp/
```

**Add a project-scoped MCP server (shared via .mcp.json in VCS):**
```bash
claude mcp add --scope project --transport http shared-api https://api.company.com/mcp
```

**List all configured MCP servers:**
```bash
claude mcp list
```

**Get details for a specific server:**
```bash
claude mcp get <name>
```

**Remove an MCP server:**
```bash
claude mcp remove <name>
```

**Add from JSON configuration:**
```bash
claude mcp add-json <name> '{"type":"http","url":"https://api.example.com/mcp"}'
claude mcp add-json <name> '{"type":"stdio","command":"npx","args":["-y","my-server"]}'
```

**Authenticate with OAuth (remote servers):**
```
/mcp
```
Then follow the browser login flow.

**MCP storage locations (read-only reference):**
- User-scoped: `~/.claude.json` → top-level `mcpServers`
- Local-scoped: `~/.claude.json` → `projects[projectPath].mcpServers`
- Project-scoped: `.mcp.json` at project root
- Plugin-bundled: `.mcp.json` at plugin root (managed by plugin install/uninstall)

**Plugin-bundled MCP servers** start automatically when the plugin is enabled. Use `/reload-plugins` if you enable/disable a plugin during a session.

---

### 23. LSP servers (plugin-only)

LSP (Language Server Protocol) servers provide language intelligence (autocomplete, diagnostics, go-to-definition).

**LSP servers ONLY exist inside plugins.** There are no standalone LSP servers. The `.lsp.json` file can only be at a plugin root, never outside a plugin.

To add LSP support: install a plugin that bundles a `.lsp.json` configuration.
To remove LSP support: uninstall or disable the plugin that provides it.

```bash
# Install a plugin that provides LSP
aimaestro-agent.sh plugin install my-api lsp-plugin-name

# Disable it (LSP stops)
aimaestro-agent.sh plugin disable my-api lsp-plugin-name

# Enable it (LSP resumes)
aimaestro-agent.sh plugin enable my-api lsp-plugin-name
```

---

### 24. Manage standalone elements (skills, agents, rules, commands)

Standalone elements are installed directly in `.claude/` folders, not via plugins.

**Skills** — folder with SKILL.md:
```bash
# User-scoped (all projects)
mkdir -p ~/.claude/skills/my-skill && cat > ~/.claude/skills/my-skill/SKILL.md << 'EOF'
---
description: My custom skill
---
# My Skill
Instructions here...
EOF

# Local-scoped (this project only)
mkdir -p .claude/skills/my-skill && cat > .claude/skills/my-skill/SKILL.md << 'EOF'
---
description: My local skill
---
# My Local Skill
Instructions here...
EOF

# Remove a skill
rm -rf ~/.claude/skills/my-skill      # user-scoped
rm -rf .claude/skills/my-skill        # local-scoped
```

**Agents** — .md files:
```bash
# User-scoped
cat > ~/.claude/agents/my-agent.md << 'EOF'
---
name: my-agent
description: Custom agent persona
---
You are a specialized agent...
EOF

# Remove
rm ~/.claude/agents/my-agent.md
```

**Rules** — .md files:
```bash
# User-scoped
cat > ~/.claude/rules/my-rule.md << 'EOF'
# My Rule
Always follow this convention...
EOF

# Remove
rm ~/.claude/rules/my-rule.md
```

**Commands** — .md files (trigger with /command-name):
```bash
# User-scoped
cat > ~/.claude/commands/my-command.md << 'EOF'
---
description: My custom command
---
Execute this when the user runs /my-command...
EOF

# Remove
rm ~/.claude/commands/my-command.md
```

**Override precedence**: A local element with the same name as a user-level element always takes priority. There is no way to selectively disable user-level standalone elements per project.

---

### 25. Manage agent sessions

Interact with the agent's tmux session directly.

```bash
# Add a new session window
aimaestro-agent.sh session add my-api

# Remove a session window
aimaestro-agent.sh session remove my-api --index 1

# Remove all session windows
aimaestro-agent.sh session remove my-api --all

# Execute a command in the agent's session
aimaestro-agent.sh session exec my-api "git status"
```

To attach to an agent's tmux session from your terminal:
```bash
tmux attach-session -t my-api
```

---

### 26. Troubleshooting: agent not responding

**Agent not found in list:**
```bash
aimaestro-agent.sh list                      # See all registered agents
tmux list-sessions                           # Check tmux sessions directly
```

**CLI script not found:**
```bash
which aimaestro-agent.sh                     # Should be in ~/.local/bin
echo $PATH | tr ':' '\n' | grep local       # Verify ~/.local/bin is in PATH
```

**AI Maestro API not running:**
```bash
curl http://localhost:23000/api/hosts/identity   # Check API health
pm2 status ai-maestro                            # Check PM2 process
pm2 restart ai-maestro                           # Restart if needed
```

**Agent stuck or unresponsive:**
```bash
aimaestro-agent.sh restart my-api            # Graceful restart
```

**Plugin not loading after install:**
```bash
aimaestro-agent.sh plugin list my-api        # Verify plugin appears
aimaestro-agent.sh plugin validate my-api /path/to/plugin   # Check plugin structure
aimaestro-agent.sh restart my-api            # Restart to reload plugins
```

---

## Requirements

- macOS or Linux
- Bash 4.0+
- tmux 3.0+
- jq
- curl
- AI Maestro running on `http://localhost:23000`

**Installation:**
```bash
./install-agent-cli.sh
```

For detailed output formats, error codes, and architecture, see [references/REFERENCE.md](./references/REFERENCE.md).
