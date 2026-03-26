---
name: mcp-discovery
description: "Discover MCP server tools, resources, and prompts without installing plugins. Use when exploring MCP servers or debugging connections. Trigger with /mcp-discovery."
allowed-tools: "Bash(mcp-discover.sh:*), Bash(jq:*), Bash(curl:*), Bash(uv:*), Bash(cat:*), Read, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Discover and inspect tools, resources, and prompts from any MCP server. Works with installed Claude Code plugins (via `mcp-discover.sh`) and standalone/remote servers (via `mcp_discovery.py`). Supports JSON, text, and LLM-optimized output formats.

## Prerequisites

- `mcp-discover.sh` installed at `~/.local/bin/` (included with AI Maestro plugin)
- `jq` for JSON processing
- For standalone discovery: `uv` and `scripts_dev/mcp_discovery.py`
- For API discovery: AI Maestro server running on port 23000

## Instructions

1. **Identify the target**: Determine whether the MCP server is in an installed plugin or standalone/remote.

2. **For installed plugins** -- use `mcp-discover.sh`:
   ```bash
   # List all tools from a plugin's MCP server
   mcp-discover.sh --plugin <plugin-name> <server-name>

   # Human-readable output
   mcp-discover.sh --plugin <plugin-name> <server-name> --format text

   # LLM-optimized output
   mcp-discover.sh --plugin <plugin-name> <server-name> --format llm
   ```

3. **For standalone/remote servers** -- use `mcp_discovery.py`:
   ```bash
   # Remote HTTP/SSE server
   uv run scripts_dev/mcp_discovery.py --url https://mcp.example.com/sse

   # NPX package (before installing)
   uv run scripts_dev/mcp_discovery.py --transport stdio -- npx -y <package-name>

   # Local binary
   uv run scripts_dev/mcp_discovery.py --transport stdio -- /path/to/server
   ```

4. **Find server name** if unknown:
   ```bash
   cat ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/.mcp.json | jq 'keys[]'
   ```

5. **Advanced operations** (call tools, list resources/prompts):
   ```bash
   # Call a tool directly
   mcp-discover.sh --plugin <plugin-name> <server-name> \
     --method tools/call --tool-name <tool-name> --tool-arg key=value

   # List resources or prompts
   mcp-discover.sh --plugin <plugin-name> <server-name> --method resources/list
   mcp-discover.sh --plugin <plugin-name> <server-name> --method prompts/list
   ```

6. **For remote agents** -- route through AI Maestro API:
   ```bash
   mcp-discover.sh --plugin <plugin-name> <server-name> --api
   ```

## Output

- **JSON** (default): `{ tools, resources, prompts, serverInfo, capabilities }`
- **Text** (`--format text`): Human-readable summary with tool names and descriptions
- **LLM** (`--format llm`): Optimized for passing to another LLM
- **Raw** (`--raw`): Exact protocol response for debugging

## Error Handling

- **Server timeout**: Increase with `--timeout 60` (default 25s). NPX servers may need extra time.
- **Server not found**: Verify plugin name and server key with `jq 'keys[]'` on the `.mcp.json`.
- **Connection refused**: Ensure the MCP server is reachable. For remote, check URL and auth token.
- **Missing tools**: The server may not implement `tools/list`. Try `--raw` to see raw capabilities.

## Examples

```bash
# Discover chromedev-tools plugin tools
/mcp-discovery
mcp-discover.sh --plugin chromedev-tools cdt --format text
```

Expected: list of tool names with descriptions.

```bash
# Check an NPX MCP server before installing
uv run scripts_dev/mcp_discovery.py --transport stdio -- npx -y chrome-devtools-mcp@latest --headless
```

Expected: JSON with tools array.

```bash
# Discover via UI
# Settings > Claude Plugins > Elements > MCP Servers > Discover Tools
```

## Checklist

Copy this checklist and track your progress:
- [ ] Identify target (installed plugin or standalone/remote)
- [ ] Run discovery command with appropriate tool
- [ ] Review discovered tools list
- [ ] Test specific tool calls if needed
- [ ] Document discovered capabilities

## Resources

- [Detailed Reference](references/REFERENCE.md) - Full CLI reference and all discovery patterns
  - Plugin-based discovery (mcp-discover.sh)
  - Output formats (JSON, text, LLM)
  - Advanced methods (tool calls, resources, prompts)
  - Remote/standalone discovery (mcp_discovery.py)
  - AI Maestro API and UI discovery
