---
name: agent-messaging
user-invocable: false
description: "Use when sending or receiving inter-agent messages via AMP. Trigger with /amp-send, /amp-inbox, /amp-read. Loaded by ai-maestro-plugin"
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

## Communication Rules

AMP messaging is governed by a title-based directed graph. Not all agents can message all others. Subagents **cannot send messages**. See [detailed-guide](reference/detailed-guide.md) for the full adjacency matrix and routing rules.

**Key rules:**
- **MANAGER and COS**: full access to all titles
- **ORCHESTRATOR**: can reach COS, ARCHITECT, INTEGRATOR, MEMBER — NOT MANAGER
- **Workers** (ARCHITECT, INTEGRATOR, MEMBER): can only reach COS and ORCHESTRATOR
- **AUTONOMOUS**: can reach MANAGER, COS, and other AUTONOMOUS agents
- Blocked routes return HTTP 403 with routing suggestion

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

Agent ID resolution: `AMP_DIR` env var > `--id` flag > `CLAUDE_AGENT_ID` > auto-select. Addresses: `alice` (local) or `alice@acme.crabmail.ai` (external, requires registration).

## Output

- `amp-inbox.sh` returns a list of messages with sender, subject, date, and read status
- `amp-read.sh` returns the full message content and marks it as read
- `amp-send.sh` returns a confirmation with the message ID
- `amp-identity.sh` returns agent name, UUID, tenant, and key fingerprint

## Examples

```bash
amp-send.sh frontend-dev "Code review" "Please review PR #42"
amp-inbox.sh          # List unread
amp-read.sh msg_abc   # Read specific message
```

## Error Handling

Run `amp-init.sh --auto` if not initialized. Run `amp-fetch.sh` if messages not arriving. See detailed guide for full troubleshooting.

## Resources

- Detailed guide: [detailed-guide](reference/detailed-guide.md)
  - Agent Identification (`--id`)
  - Identity Check (Run First)
  - Installation
  - Address Formats
  - Full Commands Reference
  - User Authorization for External Providers
  - Message Types
  - Priority Levels
  - Attachment Security
  - Local Storage
  - Security
  - Communication Graph (Title-Based Directed Graph)
  - Extended Workflow Examples
  - Protocol Reference
- Protocol specification: https://agentmessaging.org
- GitHub: https://github.com/agentmessaging/protocol
