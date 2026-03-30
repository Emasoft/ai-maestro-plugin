# AI Maestro Plugin

<!--BADGES-START-->
<!--BADGES-END-->

Built from plugin.manifest.json with 5 sources.

**Skills:** 11 | **Commands:** 12 | **Scripts:** 69

Built at: 2026-03-30T00:00:00Z

See the [main repo](https://github.com/23blocks-OS/ai-maestro-plugins) for source files and build instructions.

## Skills

| Skill | Description |
|-------|-------------|
| `ai-maestro-agents-management` | Agent lifecycle management |
| `debug-hooks` | Hook debugging utilities |
| `docs-search` | Documentation search |
| `graph-query` | Code graph querying |
| `mcp-discovery` | MCP server discovery |
| `memory-search` | Conversation memory search |
| `planning` | Task planning with persistent files |
| `team-governance` | Team governance and COS management |
| `team-kanban` | Team kanban boards and tasks |
| `agent-messaging` | AMP inter-agent messaging (send, receive, reply, attachments) |
| `agent-identity` | AID agent identity (Ed25519 keys, proof of possession, tokens) |

## AMP Commands (Agent Messaging Protocol)

12 slash commands for inter-agent communication:

| Command | Description |
|---------|-------------|
| `/amp-init` | Initialize agent identity and messaging |
| `/amp-identity` | Quick identity check for context recovery |
| `/amp-status` | Show messaging status and registrations |
| `/amp-inbox` | Check message inbox |
| `/amp-read` | Read a specific message |
| `/amp-send` | Send a message to another agent |
| `/amp-reply` | Reply to a message |
| `/amp-delete` | Delete a message |
| `/amp-register` | Register with an external AMP provider |
| `/amp-fetch` | Fetch messages from external providers |
| `/amp-download` | Download attachments from a message |
| `/amp-statusline` | Install AMP status line for Claude Code |

## AMP Scripts

14 shell scripts installed to PATH for messaging operations:

`amp-init.sh`, `amp-identity.sh`, `amp-status.sh`, `amp-inbox.sh`, `amp-read.sh`, `amp-send.sh`, `amp-reply.sh`, `amp-delete.sh`, `amp-register.sh`, `amp-fetch.sh`, `amp-download.sh`, `amp-statusline.sh`, `amp-helper.sh`, `amp-security.sh`

## AID Scripts (Agent Identity)

5 shell scripts for agent identity management:

| Script | Description |
|--------|-------------|
| `aid-init.sh` | Initialize Ed25519 agent identity |
| `aid-register.sh` | Register identity with a provider |
| `aid-status.sh` | Show identity status |
| `aid-token.sh` | Generate/exchange identity tokens |
| `aid-helper.sh` | Shared helper functions for AID scripts |

## License

MIT
