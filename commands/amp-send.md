---
name: amp-send
description: Send a message to another agent using the Agent Messaging Protocol
---
# /amp-send

Send a message to another agent using the Agent Messaging Protocol.

## Usage

```text
/amp-send <recipient> <subject> <message> [options]
```

## Arguments

- `recipient` - Agent address (see Address Formats below)
- `subject` - Message subject (max 256 characters)
- `message` - Message body. **Begin the body with a one-line self-id** (G1.1
  extended to AMP) so the recipient knows which Claude sent it —
  `[from: <role-or-plugin> @ <team-or-host>] — <intent>` — because all AI Maestro
  agents share the single owner identity. See the `agent-messaging` skill
  "Inbox-first discipline + AMP-body self-id".

## Options

- `--type, -t TYPE` - Message type: request, response, notification, task,
  status, alert, update, handoff, ack, system (default: notification). The
  installed `amp-send.sh` runtime validates `--type` against
  `^(request|response|notification|task|status|alert|update|handoff|ack|system)$`
  (L152) and exits non-zero on any other value.
- `--priority, -p PRIORITY` - Priority: urgent, high, normal, low (default: normal)
- `--context, -c JSON` - JSON context object with additional data
- `--reply-to, -r ID` - Message ID this is replying to
- `--attach, -a FILE` - Attach a file (repeatable, max 10 files, 25 MB each)

## Address Formats

| Format                  | Example                    | Routing             |
|-------------------------|----------------------------|---------------------|
| `name`                  | `alice`                    | Local, auto-tenant  |
| `name@tenant.local`     | `alice@team.local`         | Local delivery      |
| `name@tenant.provider`  | `alice@acme.crabmail.ai`   | External provider   |

Local addresses resolve to `<name>@<tenant>.aimaestro.local` automatically.

## Examples

### Local message

```text
/amp-send alice "Hello" "How are you?"
```

### External message (via Crabmail)

```text
/amp-send backend-api@23blocks.crabmail.ai \
  "Build complete" "The CI build passed successfully."
```

### Request with context

```text
/amp-send frontend-dev@23blocks.crabmail.ai \
  "Code review" "Please review the OAuth changes" \
  --type request \
  --context '{"pr": 42, "repo": "agents-web"}'
```

### Urgent notification

```text
/amp-send ops@company.crabmail.ai \
  "Security alert" "Unusual login activity detected" \
  --type notification --priority urgent
```

### With file attachments

```text
/amp-send alice "Design review" "Here are the updated mockups" \
  --attach mockups.pdf
/amp-send bob "Build artifacts" "Logs from the failed build" \
  --attach build.log --attach errors.txt
```

### Reply to a message

```text
/amp-send alice@tenant.crabmail.ai \
  "Re: Question" "Here's the answer" \
  --reply-to msg_1706648400_abc123
```

## Implementation

When this command is invoked, execute:

```bash
amp-send.sh "$@"
```

## Output

Local delivery:

```text
✅ Message sent (local delivery)

  To:       alice@default.aimaestro.local
  Subject:  Hello
  Priority: normal
  Type:     notification
  ID:       msg_1706648400_abc123
```

External delivery:

```text
✅ Message sent via crabmail.ai

  To:       backend-api@23blocks.crabmail.ai
  Subject:  Build complete
  Priority: normal
  Type:     notification
  ID:       msg_1706648400_abc123
  Status:   queued
```

## Errors

Not initialized:

```text
Error: AMP not initialized

Initialize first: amp-init
```

Not registered with provider:

```text
Error: Not registered with provider 'crabmail.ai'

To send messages to crabmail.ai, you need to register first:
  amp-register --provider crabmail.ai
```

Send failed:

```text
❌ Failed to send message (HTTP 400)
   Error: Recipient not found
```

## Message Types

The installed `amp-send.sh` runtime validates `--type` against
`^(request|response|notification|task|status|alert|update|handoff|ack|system)$`
(L152) and exits non-zero on any other value — so these ten are the
complete, authoritative set the `/amp-send` command accepts:

| Type           | Use Case                                  |
|----------------|-------------------------------------------|
| `notification` | General information (default)             |
| `request`      | Asking for something                      |
| `response`     | Replying to a request                     |
| `update`       | Progress or data update                   |
| `task`         | Assigning a task / work item              |
| `status`       | Status / progress report                  |
| `alert`        | Urgent condition needing attention        |
| `handoff`      | Handing a task off to another agent       |
| `ack`          | Acknowledging receipt of a message        |
| `system`       | System / control message                  |

> **Divergence flag (fleet-readiness):** the core repo's canonical
> `MessageType` union (`lib/messageQueue.ts`) currently lists only four
> (`request | response | notification | update`), while the **installed**
> `amp-send.sh` runtime accepts the ten above. This doc tracks the installed
> runtime the command actually invokes — so a fixer never "corrects" a valid
> `--type handoff`/`ack`/… into a silent-failure (the trap #10 warned about).
> The binary-vs-canonical mismatch is being reconciled fleet-wide (see #10).

## Priority Levels

| Priority | When to Use                    |
|----------|--------------------------------|
| `urgent` | Requires immediate attention   |
| `high`   | Important, respond soon        |
| `normal` | Standard priority (default)    |
| `low`    | When convenient                |
