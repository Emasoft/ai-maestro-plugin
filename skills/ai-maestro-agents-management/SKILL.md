---
name: ai-maestro-agents-management
user-invocable: false
description: "Manage AI agent lifecycle via CLI. Use when creating, listing, deleting, or configuring agents. Trigger with /ai-maestro-agents-management.. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-agent.sh:*), Bash(curl:*), Bash(jq:*), Bash(tmux:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "3.1.0"
---

## Overview

Manage AI agents through the `aimaestro-agent.sh` CLI and the AI Maestro REST API. Covers the full agent lifecycle: creation, configuration, hibernation, plugin/skill management, and import/export. For inter-agent messaging, use the `agent-messaging` skill instead.

## Prerequisites

- AI Maestro running on `http://localhost:23000`
- `aimaestro-agent.sh` installed in `~/.local/bin/`
- tmux 3.0+, jq, curl, Bash 4.0+

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

- [Full CLI & API Reference](references/REFERENCE.md) — All commands, options, examples, troubleshooting
  - CLI Quick Reference table
  - All 25 use cases with examples
  - Plugin vs Role Plugin comparison
  - Claude Code configuration reference
  - Script architecture
  - Troubleshooting and error messages
