---
name: mcp-discovery
description: >-
  Discover tools, resources, and prompts from any MCP server. List available
  tools before using them, inspect server capabilities, call tools directly,
  and get server metadata. Use when working with MCP servers, debugging MCP
  connections, or exploring what tools a server provides.
version: 1.0.0
user_invocable: false
allowed_tools:
  - Bash
  - Read
tags:
  - mcp
  - tools
  - discovery
  - server
  - plugins
---

# MCP Server Discovery

Discover and inspect MCP servers installed via Claude Code plugins.

## Use Cases

### 1. List all tools from a plugin's MCP server

When you need to know what tools an MCP server provides:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name>
```

Example:
```bash
mcp-discover.sh --plugin chromedev-tools cdt
```

### 2. List tools in human-readable format

When you want a readable summary instead of JSON:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --format text
```

### 3. List tools in LLM-optimized format

When you need the output formatted for another LLM to process:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --format llm
```

### 4. Discover tools from a specific .mcp.json file

When you have the config path directly:

```bash
mcp-discover.sh /path/to/.mcp.json <server-name>
```

### 5. Get raw server response (unprocessed)

When you need the exact protocol response for debugging:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --raw
```

### 6. Call a specific tool on the server

When you want to execute a tool directly:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> \
  --method tools/call \
  --tool-name <tool-name> \
  --tool-arg key=value
```

Example — list Chrome pages:
```bash
mcp-discover.sh --plugin chromedev-tools cdt \
  --method tools/call \
  --tool-name list_pages
```

### 7. List server resources

When you want to see what resources (files, data) the server exposes:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --method resources/list
```

### 8. List server prompts

When you want to see predefined prompts the server offers:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --method prompts/list
```

### 9. Use the AI Maestro API (for remote agents)

When the agent is on a different host than the MCP server:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --api
```

Or call the API directly:
```bash
curl -s -X POST http://localhost:23000/api/settings/mcp-discover \
  -H "Content-Type: application/json" \
  -d '{"configPath": "/path/to/.mcp.json", "serverName": "server-name"}'
```

### 10. Set a custom timeout

When the MCP server is slow to start (e.g. downloads dependencies via npx):

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --timeout 60
```

### 11. Discover tools from the UI

Navigate to Settings → Claude Plugins → Elements tab → filter by MCP Servers → expand an MCP element → click "Discover Tools".

### 12. Copy the tools list to clipboard

After discovering tools in the UI, click the "Copy Tools List" button in the footer of the tools panel.

## Discovering tools WITHOUT installing the plugin

### 13. Discover tools from a remote HTTP/SSE MCP server

When the MCP server is hosted remotely (no plugin needed):

```bash
uv run scripts_dev/mcp_discovery.py --url https://mcp.example.com/sse
```

With authentication:
```bash
uv run scripts_dev/mcp_discovery.py --url https://mcp.example.com/sse --bearer-token sk-abc123
```

### 14. Discover tools from an npx package (without installing the plugin)

When you want to check what tools an npm-based MCP server provides before installing:

```bash
uv run scripts_dev/mcp_discovery.py --transport stdio -- npx -y <package-name>
```

Example — check chrome-devtools-mcp tools:
```bash
uv run scripts_dev/mcp_discovery.py --transport stdio -- npx -y chrome-devtools-mcp@latest --headless
```

Example — check a Python MCP server:
```bash
uv run scripts_dev/mcp_discovery.py --transport stdio -- uvx mcp-server-sqlite --db-path /tmp/test.db
```

### 15. Discover tools from a local binary/script (not yet in a plugin)

When you have an MCP server binary or script but it's not in a plugin yet:

```bash
uv run scripts_dev/mcp_discovery.py --transport stdio -- /path/to/mcp-server --arg1 --arg2
```

Or with explicit command and args:
```bash
uv run scripts_dev/mcp_discovery.py --command node --command-arg /path/to/server.js
```

### 16. Discover tools from a GitHub repo's .mcp.json (before installing)

When you want to check a plugin's MCP tools before adding the marketplace:

```bash
# Download just the .mcp.json
curl -sL "https://raw.githubusercontent.com/owner/repo/main/plugins/plugin-name/.mcp.json" > /tmp/check.json
# Discover tools from it
uv run scripts_dev/mcp_discovery.py /tmp/check.json <server-name> --json
```

### 17. Discover tools with custom environment variables

When the MCP server needs specific env vars to start:

```bash
uv run scripts_dev/mcp_discovery.py --transport stdio \
  --env API_KEY=sk-123 \
  --env DB_HOST=localhost \
  -- node /path/to/server.js
```

### 18. Discover tools with SSE transport (legacy servers)

Some older MCP servers use Server-Sent Events instead of Streamable HTTP:

```bash
uv run scripts_dev/mcp_discovery.py --url https://mcp.example.com/events --transport sse
```

## Finding the server name

The server name is the key in the `.mcp.json` file. To find it:

```bash
cat ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/.mcp.json | jq 'keys[]'
```

Or use `--plugin` which searches the plugin cache automatically.

## Notes

- `${CLAUDE_PLUGIN_ROOT}` in `.mcp.json` is resolved automatically
- The script starts the MCP server temporarily for discovery, then stops it
- Default timeout is 25 seconds (some servers need time to download via npx)
- JSON format returns: `{ tools, resources, prompts, serverInfo, capabilities }`
- The `--api` flag routes through the AI Maestro server (useful for remote agents)
