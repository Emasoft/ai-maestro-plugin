# Agent Messaging Protocol (AMP) — Detailed Guide

## Table of Contents

- [Agent Identification (`--id`)](#agent-identification---id)
- [Identity Check (Run First)](#identity-check-run-first)
- [Installation](#installation)
- [Address Formats](#address-formats)
- [Full Commands Reference](#full-commands-reference)
- [User Authorization for External Providers](#user-authorization-for-external-providers)
- [Message Types](#message-types)
- [Priority Levels](#priority-levels)
- [Attachment Security](#attachment-security)
- [Local Storage](#local-storage)
- [Security](#security)
- [Communication Graph (Title-Based Directed Graph)](#communication-graph-title-based-directed-graph)
- [Extended Workflow Examples](#extended-workflow-examples)
- [Protocol Reference](#protocol-reference)

## Agent Identification (`--id`)

Every command (except `amp-init.sh`) accepts `--id <uuid>` to specify which agent you're operating as. The UUID comes from the agent's `config.json` (`agent.id` field).

```bash
# Operate as a specific agent
amp-inbox.sh --id 6bbdaeb8-8a85-4d0b-8f8c-3c217486eae8
amp-send.sh --id <uuid> alice "Hello" "Hi there"
```

**Resolution order** (first match wins):

1. `AMP_DIR` env var (AI Maestro sets this)
2. `--id <uuid>` argument
3. `CLAUDE_AGENT_ID` env var
4. `CLAUDE_AGENT_NAME` env var / tmux session
5. Single agent auto-select (if only one agent exists)

If multiple agents exist and none of the above resolve, the CLI lists available agents with UUIDs.

## Identity Check (Run First)

**Before using any messaging commands, ALWAYS verify your identity:**

```bash
amp-identity.sh
# Or with explicit agent:
amp-identity.sh --id <uuid>
```

If you see "Not initialized", run:

```bash
amp-init.sh --auto
```

This identity check is essential because:

- Your AMP identity persists across sessions
- After context reset, you need to rediscover who you are
- Each agent has its own isolated AMP directory with identity, keys, and messages

**Identity file location:** `${AMP_DIR}/IDENTITY.md` (per-agent, auto-resolved)

## Installation

### For Claude Code (plugin)

```bash
git clone https://github.com/agentmessaging/claude-plugin.git ~/.claude/plugins/agent-messaging
```

### For any AI agent (skills.sh)

```bash
npx skills add agentmessaging/claude-plugin
```

### Manual (any agent)

Scripts are installed to `~/.local/bin/` by `install-messaging.sh`. They are available on PATH after installation.

## Address Formats

**Local addresses** (work within your AI Maestro mesh):

- `alice` expands to `alice@<your-org>.aimaestro.local`
- `bob@acme.aimaestro.local` for explicit local delivery

**External addresses** (require registration):

- `alice@acme.crabmail.ai` via Crabmail provider
- `backend-api@23blocks.otherprovider.com` via other providers

## Full Commands Reference

All commands are bash scripts installed at `~/.local/bin/`.

### amp-init.sh — Initialize Agent

```bash
amp-init.sh --auto                          # Auto-detect name from environment
amp-init.sh --name my-agent                 # Specify name
amp-init.sh --name my-agent --tenant myteam # Override tenant
```

### amp-identity.sh — Check Identity

```bash
amp-identity.sh                     # Human-readable output
amp-identity.sh --json              # JSON output for parsing
amp-identity.sh --id <uuid> --json  # Check specific agent's identity
```

### amp-status.sh — Show Status

```bash
amp-status.sh                   # Full status with registrations
amp-status.sh --id <uuid>       # Status for specific agent
```

### amp-inbox.sh — Check Inbox

```bash
amp-inbox.sh                    # Show unread messages
amp-inbox.sh --all              # Show all messages
amp-inbox.sh --id <uuid> --all  # Specific agent's inbox
```

### amp-read.sh — Read a Message

```bash
amp-read.sh <message-id>                # Read and mark as read
amp-read.sh <message-id> --no-mark-read # Read without marking
```

### amp-send.sh — Send a Message

```bash
amp-send.sh <recipient> "<subject>" "<message>"
amp-send.sh <recipient> "<subject>" "<message>" --priority urgent
amp-send.sh <recipient> "<subject>" "<message>" --type request
amp-send.sh <recipient> "<subject>" "<message>" --context '{"pr": 42}'
amp-send.sh <recipient> "<subject>" "<message>" --attach /path/to/file.pdf
```

### amp-reply.sh — Reply to a Message

```bash
amp-reply.sh <message-id> "<reply-message>"
```

### amp-download.sh — Download Attachments

```bash
amp-download.sh <message-id> --all              # Download all attachments
amp-download.sh <message-id> <attachment-id>     # Download specific attachment
amp-download.sh <message-id> --all --dest ~/tmp  # Custom destination
```

### amp-delete.sh — Delete a Message

```bash
amp-delete.sh <message-id>          # With confirmation
amp-delete.sh <message-id> --force  # Without confirmation
```

### amp-register.sh — Register with External Provider

```bash
amp-register.sh --provider crabmail.ai --user-key uk_your_key_here
amp-register.sh -p crabmail.ai -k uk_xxx -n my-agent
```

### amp-fetch.sh — Fetch from External Providers

```bash
amp-fetch.sh                          # Fetch from all registered providers
amp-fetch.sh --provider crabmail.ai   # Fetch from specific provider
```

## User Authorization for External Providers

**You MUST ask the user for their User Key before registering with external providers.**

User Keys are sensitive credentials tied to the user's account and billing. They:

- Should NEVER be stored, cached, or logged by the agent
- Must be provided explicitly by the user for each registration
- Start with `uk_` prefix

**Flow:**

1. Explain what's needed: "To register with [provider], I'll need your User Key."
2. Wait for the user to provide the key.
3. Use it immediately via `amp-register.sh` and don't store it.

**Security rules:**

- Never ask for passwords — only User Keys (`uk_` format)
- Never store credentials — use immediately, then discard
- Never assume authorization — always ask explicitly

## Message Types

Canonical enum (`lib/types/amp-message.ts`): exactly seven values. Callers passing anything else get server-side validation errors.

| Type | Use Case |
|------|----------|
| `notification` | General information (default) |
| `request` | Asking for something |
| `response` | Reply to a request |
| `task` | Assigned work item |
| `status` | Status update |
| `alert` | Important notice |
| `update` | Progress or data update |

## Priority Levels

| Priority | When to Use |
|----------|-------------|
| `urgent` | Requires immediate attention |
| `high` | Important, respond soon |
| `normal` | Standard (default) |
| `low` | When convenient |

## Attachment Security

- Attachments with `scan_status: "suspicious"` require human approval before downloading
- Attachments with `scan_status: "rejected"` must never be downloaded
- SHA-256 digest verification is performed automatically by the download script

## Local Storage

Each agent has its own isolated AMP directory:

```
~/.agent-messaging/agents/<agent-name>/
├── IDENTITY.md          # Human-readable identity
├── config.json          # Agent configuration
├── keys/
│   ├── private.pem      # Private key (never shared)
│   └── public.pem       # Public key
├── messages/
│   ├── inbox/<sender>/msg_*.json
│   └── sent/<recipient>/msg_*.json
├── attachments/<msg-id>/
└── registrations/
```

The `AMP_DIR` environment variable points to the agent's directory and is auto-resolved.

## Security

- **Ed25519 signatures** — messages are cryptographically signed
- **Key revocation** — compromised keys are revoked and propagated across federation
- **Communication ACLs** — allowlist-based policies control who agents can message
- **Quarantine** — suspicious messages held for human review with risk scoring
- **Private keys stay local** — never sent to providers
- **Per-agent identity** — each agent has a unique keypair

## Communication Graph (Title-Based Directed Graph, R6 v2)

AMP enforces a directed communication graph based on governance titles. Each node is a title (plus the HUMAN user); each edge is either `Y` (allowed) or `1` (reply-only). Blank = forbidden. The server calls `lib/communication-graph.ts::validateMessageRoute()` before every delivery and returns HTTP 403 `title_communication_forbidden` on a forbidden edge.

### Graph Nodes

| Node | Description |
|------|-------------|
| `HUMAN` (H) | The end user — first-class graph node with full `Y` outbound; inbound from agents is `1` (team titles) or `Y` (governance titles) |
| `MANAGER` | Full `Y` access — sole bridge between team layer and governance layer |
| `CHIEF-OF-STAFF` (COS) | Team gateway — `Y` to MANAGER + peer COS + team roles; `1` to HUMAN; blank to MAINTAINER + AUTONOMOUS |
| `ORCHESTRATOR` | Task coordinator — `Y` to COS + ARCHITECT + INTEGRATOR + MEMBER; `1` to HUMAN |
| `ARCHITECT` | Design lead — `Y` to COS + ORCHESTRATOR; `1` to HUMAN |
| `INTEGRATOR` | Integration specialist — `Y` to COS + ORCHESTRATOR; `1` to HUMAN |
| `MEMBER` | Team member — `Y` to COS + ORCHESTRATOR; `1` to HUMAN |
| `MAINTAINER` | Governance-layer maintainer — `Y` to MANAGER + HUMAN only |
| `AUTONOMOUS` | Independent agent — `Y` to MANAGER + peer AUTONOMOUS + HUMAN |

Subagents (spawned task helpers without their own Claude Code instance) are **not nodes** — they cannot send messages at all.

### Edge Types

- `Y` — allow unconditionally.
- `1` — reply-only. Sender MUST pass `options.inReplyToMessageId` referencing an inbound H→agent message. AMP marks the original `replied=true` on successful delivery, so a second reply to the same inbound id is refused (one-reply-per-inbound invariant).
- blank — deny.

### Directed Edges (Allowed Connections)

```
HUMAN         → HUMAN, MANAGER, COS, ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER, MAINTAINER, AUTONOMOUS       (Y all)
MANAGER       → HUMAN, MANAGER, COS, ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER, MAINTAINER, AUTONOMOUS       (Y all)
COS           → MANAGER, COS, ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER  (Y); HUMAN (1); MAINTAINER/AUTONOMOUS (blank)
ORCHESTRATOR  → COS, ARCHITECT, INTEGRATOR, MEMBER                          (Y); HUMAN (1); all others (blank)
ARCHITECT     → COS, ORCHESTRATOR                                            (Y); HUMAN (1); all others (blank)
INTEGRATOR    → COS, ORCHESTRATOR                                            (Y); HUMAN (1); all others (blank)
MEMBER        → COS, ORCHESTRATOR                                            (Y); HUMAN (1); all others (blank)
MAINTAINER    → MANAGER, HUMAN                                               (Y); all others (blank)
AUTONOMOUS    → MANAGER, AUTONOMOUS, HUMAN                                   (Y); all others (blank)
```

### Adjacency Matrix (v2)

`Y` = allowed, `1` = reply-only, blank = forbidden.

| Sender \ Recipient | HUMAN | MANAGER | COS | ORCH | ARCH | INT | MEM | MAINT | AUTO |
|---------------------|:-----:|:-------:|:---:|:----:|:----:|:---:|:---:|:-----:|:----:|
| **HUMAN**           |   Y   |    Y    |  Y  |  Y   |  Y   |  Y  |  Y  |   Y   |  Y   |
| **MANAGER**         |   Y   |    Y    |  Y  |  Y   |  Y   |  Y  |  Y  |   Y   |  Y   |
| **COS**             |   1   |    Y    |  Y  |  Y   |  Y   |  Y  |  Y  |       |      |
| **ORCHESTRATOR**    |   1   |         |  Y  |      |  Y   |  Y  |  Y  |       |      |
| **ARCHITECT**       |   1   |         |  Y  |  Y   |      |     |     |       |      |
| **INTEGRATOR**      |   1   |         |  Y  |  Y   |      |     |     |       |      |
| **MEMBER**          |   1   |         |  Y  |  Y   |      |     |     |       |      |
| **MAINTAINER**      |   Y   |    Y    |     |      |      |     |     |       |      |
| **AUTONOMOUS**      |   Y   |    Y    |     |      |      |     |     |       |  Y   |

### Rules R6.1 – R6.10

| ID | Rule |
|----|------|
| **R6.1** | Communication is defined by the matrix above. Edge types: `Y` allow, `1` reply-only, blank deny. Unlisted pairs are denied. |
| **R6.2** | MANAGER has full `Y` access — sole bridge between team layer (COS + team roles) and governance layer (MAINTAINER, AUTONOMOUS). |
| **R6.3** | CHIEF-OF-STAFF is strictly the team gateway — `Y` to MANAGER + peer COS + team roles; `1` to HUMAN; blank to MAINTAINER + AUTONOMOUS. |
| **R6.4** | ORCHESTRATOR — `Y` to COS + ARCHITECT + INTEGRATOR + MEMBER; `1` to HUMAN; blank elsewhere. |
| **R6.5** | ARCHITECT / INTEGRATOR / MEMBER — `Y` to COS + ORCHESTRATOR; `1` to HUMAN; blank elsewhere. |
| **R6.5a** | AUTONOMOUS — `Y` to MANAGER + peer AUTONOMOUS + HUMAN; blank to COS + team roles + MAINTAINER. |
| **R6.5b** | MAINTAINER — `Y` to MANAGER + HUMAN; blank to COS + team roles + AUTONOMOUS + peer MAINTAINER. |
| **R6.6** | HUMAN has full `Y` outbound to every node including self. Inbound to H from team titles is `1` (reply-only). Inbound to H from governance titles is `Y`. Agents SHOULD NOT proactively initiate user contact even when persona-permitted — `1` is the hard server-enforced floor, persona is the soft floor. |
| **R6.7** | Blocked messages MUST return HTTP 403 with a routing suggestion. Cross-layer routes go through MANAGER (not COS). |
| **R6.8** | Three enforcement layers: (1) server `validateMessageRoute()`, (2) role-plugin main-agent `.md` listing recipients, (3) sub-agents forbidden from AMP entirely. |
| **R6.9** | Sub-agents have no AMP identity, cannot authenticate, communicate only with their spawning main-agent. |
| **R6.10** | Reply-only enforcement requires `options.inReplyToMessageId` referencing an inbound H→agent message. AMP inbox marks original `replied=true` on delivery, refusing a second reply. |

### Routing Suggestions (When Blocked)

Cross-layer routes (team ↔ governance) go **through MANAGER** — COS no longer reaches MAINTAINER or AUTONOMOUS.

| Sender Title | Blocked Recipient | Routing Suggestion |
|-------------|-------------------|-------------------|
| COS | MAINTAINER | Route through MANAGER |
| COS | AUTONOMOUS | Route through MANAGER |
| ORCHESTRATOR | MANAGER | Route through COS |
| ORCHESTRATOR | ORCHESTRATOR | Route through CHIEF-OF-STAFF for cross-team coordination |
| ORCHESTRATOR | MAINTAINER | Route through COS → MANAGER |
| ORCHESTRATOR | AUTONOMOUS | Route through COS → MANAGER |
| ARCHITECT / INTEGRATOR / MEMBER | MANAGER | Route through COS |
| ARCHITECT / INTEGRATOR / MEMBER | Other workers | Route through ORCHESTRATOR or COS |
| ARCHITECT / INTEGRATOR / MEMBER | MAINTAINER | Route through COS → MANAGER |
| ARCHITECT / INTEGRATOR / MEMBER | AUTONOMOUS | Route through COS → MANAGER |
| MAINTAINER | COS / ORCH / ARCH / INT / MEM / AUTONOMOUS / peer MAINTAINER | Route through MANAGER |
| AUTONOMOUS | COS / ORCH / ARCH / INT / MEM / MAINTAINER | Route through MANAGER |
| Team title (COS/ORCH/ARCH/INT/MEM) | HUMAN (no prior inbound) | Wait for the user to message first; then reply with `inReplyToMessageId` |

### Error Response Format

```json
{
  "error": "title_communication_forbidden",
  "status": 403,
  "message": "ARCHITECT cannot message MAINTAINER directly",
  "suggestion": "Route through COS → MANAGER"
}
```

## Extended Workflow Examples

### Code Review Request

```
User: Ask frontend-dev to review PR #42

Agent executes:
amp-send.sh frontend-dev "Code review request" \
  "Please review PR #42 - OAuth implementation" \
  --type request \
  --context '{"repo": "agents-web", "pr": 42}'
```

### Task Handoff

```
User: Hand off the database work to backend-db

Agent executes:
amp-send.sh backend-db "Task handoff: Database migration" \
  "I've completed the schema design. Please implement the migrations." \
  --type task \
  --priority high
```

## Protocol Reference

Full specification: <https://agentmessaging.org>
GitHub: <https://github.com/agentmessaging/protocol>
