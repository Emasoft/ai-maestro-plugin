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

- `--type, -t TYPE` - Message type: request, response, notification, update
  (default: notification). The `amp-send.sh` runtime validates `--type`
  against exactly these four values
  (`^(request|response|notification|update)$`) and exits non-zero on any
  other value, so passing `task`/`status`/`alert`/etc. fails the send.
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

The `amp-send.sh` runtime accepts exactly four values — it validates
`--type` against `^(request|response|notification|update)$` (and the
canonical `MessageType` union in the core repo's `lib/messageQueue.ts`
matches: `'request' | 'response' | 'notification' | 'update'`). Any
other value is rejected before the send, so the table below is the
complete, authoritative set:

| Type           | Use Case                       |
|----------------|--------------------------------|
| `notification` | General information (default)  |
| `request`      | Asking for something           |
| `response`     | Replying to a request          |
| `update`       | Progress or data update        |

## Priority Levels

| Priority | When to Use                    |
|----------|--------------------------------|
| `urgent` | Requires immediate attention   |
| `high`   | Important, respond soon        |
| `normal` | Standard priority (default)    |
| `low`    | When convenient                |
