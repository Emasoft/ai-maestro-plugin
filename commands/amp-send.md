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
- `message` - Message body

## Options

- `--type, -t TYPE` - Message type: request, response, notification, alert,
  task, status, update (default: notification). The canonical
  `lib/types/amp-message.ts` enum has exactly these seven values;
  any other value is rejected by the server.
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

### Urgent alert

```text
/amp-send ops@company.crabmail.ai \
  "Security alert" "Unusual login activity detected" \
  --type alert --priority urgent
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

Canonical `MessageType` enum (`lib/types/amp-message.ts`) — exactly seven values:

| Type           | Use Case                       |
|----------------|--------------------------------|
| `notification` | General information (default)  |
| `request`      | Asking for something           |
| `response`     | Replying to a request          |
| `task`         | Assigning work                 |
| `status`       | Progress update                |
| `update`       | Progress or data update        |
| `alert`        | Important notification         |

## Priority Levels

| Priority | When to Use                    |
|----------|--------------------------------|
| `urgent` | Requires immediate attention   |
| `high`   | Important, respond soon        |
| `normal` | Standard priority (default)    |
| `low`    | When convenient                |
