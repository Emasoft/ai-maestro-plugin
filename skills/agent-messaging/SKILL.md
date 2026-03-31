---
name: agent-messaging
user-invocable: "false"
description: "Use when sending or receiving inter-agent messages via AMP protocol. Trigger with /amp-send, /amp-inbox, /amp-read, or 'check my messages', 'send a message to'."
license: Apache-2.0
compatibility: Requires curl, jq, openssl, and base64 CLI tools. macOS and Linux supported.
metadata:
  version: "0.1.2"
  homepage: "https://agentmessaging.org"
  repository: "https://github.com/agentmessaging/claude-plugin"
---

# Agent Messaging Protocol (AMP)

## Overview

Send and receive cryptographically signed messages between AI agents using the Agent Messaging Protocol (AMP). Supports local messaging within an AI Maestro mesh, federation across external providers, file attachments, and Ed25519 signatures. Works with any AI agent that can execute shell commands.

## Prerequisites

Copy this checklist and track your progress:

- [x] AMP scripts installed to `~/.local/bin/` (via `install-messaging.sh`)
- [x] Agent identity initialized (`amp-init.sh --auto`)
- [x] CLI tools: `curl`, `jq`, `openssl`, `base64`

## Instructions

1. Check identity (run first after context reset): `amp-identity.sh`
2. Initialize if needed (first time only): `amp-init.sh --auto`
3. Send a message: `amp-send.sh <recipient> "<subject>" "<message>"`
4. Check inbox: `amp-inbox.sh`
5. Read a message: `amp-read.sh <message-id>`
6. Reply to a message: `amp-reply.sh <message-id> "<reply>"`

### Core Commands

| Command | Purpose |
|---------|---------|
| `amp-identity.sh` | Verify current agent identity |
| `amp-init.sh --auto` | Initialize agent identity |
| `amp-inbox.sh` | List unread messages |
| `amp-read.sh <id>` | Read a specific message |
| `amp-send.sh <to> <subj> <msg>` | Send a message |
| `amp-reply.sh <id> <msg>` | Reply to a message |
| `amp-delete.sh <id>` | Delete a message |
| `amp-download.sh <id> --all` | Download attachments |
| `amp-fetch.sh` | Fetch from external providers |

### Agent Identification

Commands accept `--id <uuid>` to specify which agent to operate as. Resolution order: `AMP_DIR` env var, `--id` flag, `CLAUDE_AGENT_ID`, `CLAUDE_AGENT_NAME`, single-agent auto-select.

### Addresses

- Local: `alice` or `bob@acme.aimaestro.local`
- External: `alice@acme.crabmail.ai` (requires registration via `amp-register.sh`)

For full command reference, options, and advanced usage, see [detailed-guide](reference/detailed-guide.md).

## Output

- `amp-inbox.sh` returns a list of messages with sender, subject, date, and read status
- `amp-read.sh` returns the full message content and marks it as read
- `amp-send.sh` returns a confirmation with the message ID
- `amp-identity.sh` returns agent name, UUID, tenant, and key fingerprint

## Error Handling

| Problem | Solution |
|---------|----------|
| "AMP not initialized" | Run `amp-init.sh --auto` |
| "Not registered with provider" | Run `amp-register.sh --provider <url> --user-key <key>` |
| "Authentication failed" | Get a new User Key from the provider dashboard |
| "Agent not found" | Verify address format: `name@tenant.provider` |
| Messages not arriving | Run `amp-fetch.sh` to pull from external providers |

## Examples

### Send a code review request

```bash
amp-send.sh frontend-dev "Code review request" \
  "Please review PR #42 - OAuth implementation" \
  --type request --context '{"pr": 42}'
```

### Check inbox and read messages

```bash
amp-inbox.sh          # List unread
amp-read.sh msg_abc   # Read specific message
```

### Hand off a task with priority

```bash
amp-send.sh backend-db "Task handoff: DB migration" \
  "Schema design complete. Please implement migrations." \
  --type handoff --priority high
```

## Resources

- Detailed guide: [detailed-guide](reference/detailed-guide.md)
- Protocol specification: https://agentmessaging.org
- GitHub: https://github.com/agentmessaging/protocol
