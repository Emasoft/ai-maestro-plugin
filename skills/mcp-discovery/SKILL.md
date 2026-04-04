---
name: mcp-discovery
user-invocable: false
description: "Discover MCP server tools, resources, and prompts without installing plugins. Use when exploring MCP servers or debugging connections. Trigger with /mcp-discovery.. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(mcp-discover.sh:*), Bash(jq:*), Bash(curl:*), Bash(uv:*), Bash(cat:*), Read, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Discover and inspect tools, resources, and prompts from any MCP server. Works with installed plugins (via `mcp-discover.sh`) and standalone/remote servers (via `mcp_discovery.py`).

## Prerequisites

- `mcp-discover.sh` at `~/.local/bin/` (included with AI Maestro plugin)
- `jq` for JSON processing
- For standalone discovery: `uv` and `scripts_dev/mcp_discovery.py`

## Instructions

1. **For installed plugins** — use `mcp-discover.sh`:
   ```bash
   mcp-discover.sh --plugin <plugin-name> <server-name>
   mcp-discover.sh --plugin <plugin-name> <server-name> --format text
   mcp-discover.sh --plugin <plugin-name> <server-name> --format llm
   ```

2. **For standalone/remote servers** — use `mcp_discovery.py`:
   ```bash
   uv run scripts_dev/mcp_discovery.py --url https://mcp.example.com/sse
   uv run scripts_dev/mcp_discovery.py --transport stdio -- npx -y <package>
   ```

3. **Find server name** if unknown:
   ```bash
   jq 'keys[]' < ~/.claude/plugins/cache/<marketplace>/<plugin>/<ver>/.mcp.json
   ```

4. **Advanced** — call tools, list resources/prompts:
   ```bash
   mcp-discover.sh --plugin <name> <server> --method tools/call --tool-name <t> --tool-arg k=v
   mcp-discover.sh --plugin <name> <server> --method resources/list
   ```

5. **Remote agents** — route through API: `mcp-discover.sh --plugin <name> <server> --api`

## Output

- **JSON** (default): `{ tools, resources, prompts, serverInfo, capabilities }`
- **Text**: Human-readable summary
- **LLM**: Optimized for passing to another LLM
- **Raw** (`--raw`): Exact protocol response

## Error Handling

- **Timeout**: Increase with `--timeout 60` (default 25s)
- **Server not found**: Verify plugin name and server key via `jq 'keys[]'` on `.mcp.json`
- **Connection refused**: Check URL and auth token for remote servers
- **Missing tools**: Try `--raw` to see raw capabilities

## Examples

```bash
/mcp-discovery
mcp-discover.sh --plugin chromedev-tools cdt --format text
```
Expected: list of tool names with descriptions.

```bash
uv run scripts_dev/mcp_discovery.py --transport stdio -- npx -y chrome-devtools-mcp@latest
```
Expected: JSON with tools array.

## Checklist

Copy this checklist and track your progress:

- [ ] Identify target (installed plugin or standalone/remote)
- [ ] Run discovery command
- [ ] Review discovered tools
- [ ] Test specific tool calls if needed

## Resources

- [Detailed Reference](references/REFERENCE.md) - Plugin-based discovery, Output formats, Advanced methods, Remote/standalone discovery, AI Maestro API and UI discovery
