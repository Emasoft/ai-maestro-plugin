# MCP Discovery Reference

## Table of Contents
- [Plugin-Based Discovery (mcp-discover.sh)](#plugin-based-discovery-mcp-discoversh)
- [Output Formats](#output-formats)
- [Advanced Methods](#advanced-methods)
- [Remote/Standalone Discovery (mcp_discovery.py)](#remotestandalone-discovery-mcp_discoverypy)
- [AI Maestro API Discovery](#ai-maestro-api-discovery)
- [UI Discovery](#ui-discovery)
- [Finding the Server Name](#finding-the-server-name)
- [Technical Notes](#technical-notes)

---

## Plugin-Based Discovery (mcp-discover.sh)

Discover tools from installed Claude Code plugins using the `mcp-discover.sh` script.

### Basic Usage

```bash
# Discover tools from a named plugin
mcp-discover.sh --plugin <plugin-name> <server-name>

# Example: chromedev-tools plugin
mcp-discover.sh --plugin chromedev-tools cdt
```

### Output Formats

```bash
# JSON (default)
mcp-discover.sh --plugin <plugin-name> <server-name>

# Human-readable text
mcp-discover.sh --plugin <plugin-name> <server-name> --format text

# LLM-optimized format (for passing to another LLM)
mcp-discover.sh --plugin <plugin-name> <server-name> --format llm
```

### From a Specific .mcp.json File

```bash
mcp-discover.sh /path/to/.mcp.json <server-name>
```

### Raw Server Response

For debugging, get the exact protocol response:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --raw
```

## Advanced Methods

### Call a Specific Tool

Execute a tool directly on the MCP server:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> \
  --method tools/call \
  --tool-name <tool-name> \
  --tool-arg key=value
```

Example -- list Chrome pages:
```bash
mcp-discover.sh --plugin chromedev-tools cdt \
  --method tools/call \
  --tool-name list_pages
```

### List Server Resources

See what resources (files, data) the server exposes:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --method resources/list
```

### List Server Prompts

See predefined prompts the server offers:

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --method prompts/list
```

### Custom Timeout

For slow-starting servers (e.g. npx downloads):

```bash
mcp-discover.sh --plugin <plugin-name> <server-name> --timeout 60
```

Default timeout is 25 seconds.

## Remote/Standalone Discovery (mcp_discovery.py)

Discover tools WITHOUT installing a plugin, using `scripts_dev/mcp_discovery.py`.

### Remote HTTP/SSE MCP Server

```bash
uv run scripts_dev/mcp_discovery.py --url https://mcp.example.com/sse
```

With authentication:
```bash
uv run scripts_dev/mcp_discovery.py --url https://mcp.example.com/sse --bearer-token sk-abc123
```

### NPX Package (Before Installing)

```bash
uv run scripts_dev/mcp_discovery.py --transport stdio -- npx -y <package-name>
```

Examples:
```bash
# Check chrome-devtools-mcp tools
uv run scripts_dev/mcp_discovery.py --transport stdio -- npx -y chrome-devtools-mcp@latest --headless

# Check a Python MCP server
uv run scripts_dev/mcp_discovery.py --transport stdio -- uvx mcp-server-sqlite --db-path /tmp/test.db
```

### Local Binary/Script

```bash
uv run scripts_dev/mcp_discovery.py --transport stdio -- /path/to/mcp-server --arg1 --arg2
```

Or with explicit command:
```bash
uv run scripts_dev/mcp_discovery.py --command node --command-arg /path/to/server.js
```

### GitHub Repo .mcp.json (Before Installing)

```bash
# Download just the .mcp.json
curl -sL "https://raw.githubusercontent.com/owner/repo/main/plugins/plugin-name/.mcp.json" > /tmp/check.json
# Discover tools from it
uv run scripts_dev/mcp_discovery.py /tmp/check.json <server-name> --json
```

### Custom Environment Variables

```bash
uv run scripts_dev/mcp_discovery.py --transport stdio \
  --env API_KEY=sk-123 \
  --env DB_HOST=localhost \
  -- node /path/to/server.js
```

### SSE Transport (Legacy Servers)

```bash
uv run scripts_dev/mcp_discovery.py --url https://mcp.example.com/events --transport sse
```

## AI Maestro API Discovery

For remote agents, route discovery through the AI Maestro server:

```bash
# Via mcp-discover.sh with --api flag
mcp-discover.sh --plugin <plugin-name> <server-name> --api

# Direct API call
curl -s -X POST http://localhost:23000/api/settings/mcp-discover \
  -H "Content-Type: application/json" \
  -d '{"configPath": "/path/to/.mcp.json", "serverName": "server-name"}'
```

## UI Discovery

1. Navigate to **Settings** > **Claude Plugins** > **Elements** tab
2. Filter by **MCP Servers**
3. Expand an MCP element
4. Click **"Discover Tools"**
5. Click **"Copy Tools List"** in the footer to copy to clipboard

## Finding the Server Name

The server name is the key in the `.mcp.json` file:

```bash
cat ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/.mcp.json | jq 'keys[]'
```

The `--plugin` flag in `mcp-discover.sh` searches the plugin cache automatically, so you only need the plugin name and server key.

## Technical Notes

- `${CLAUDE_PLUGIN_ROOT}` in `.mcp.json` is resolved automatically by the script
- The script starts the MCP server temporarily for discovery, then stops it
- Default timeout is 25 seconds (some servers need time to download via npx)
- JSON format returns: `{ tools, resources, prompts, serverInfo, capabilities }`
- The `--api` flag routes through the AI Maestro server (useful for remote agents)
