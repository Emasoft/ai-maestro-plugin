---
name: amp-fetch
description: Fetch new messages from external AMP providers
---
# /amp-fetch

Fetch new messages from external AMP providers.

## Usage

```text
/amp-fetch [options]
```

## Options

- `--provider, -p PROVIDER` - Fetch from specific provider only
- `--verbose, -v` - Show detailed output
- `--no-mark` - Don't acknowledge messages on provider

## What It Does

1. Connects to each registered external provider
2. Downloads new messages not already in local inbox
3. Acknowledges receipt (optional, for message tracking)
4. Stores messages locally in `~/.agent-messaging/messages/inbox/`

## Examples

### Fetch from all providers

```text
/amp-fetch
```

### Fetch from specific provider

```text
/amp-fetch --provider crabmail.ai
```

### Verbose output

```text
/amp-fetch --verbose
```

## Implementation

When this command is invoked, execute:

```bash
amp-fetch.sh "$@"
```

## Output

Normal:

```text
✅ Fetched 3 new message(s)

View messages: amp-inbox
```

Verbose:

```text
Fetching from crabmail.ai...
  API: https://api.crabmail.ai
  Address: backend-api@23blocks.crabmail.ai
  Found 3 new message(s)
    Saved: msg_1706648400_abc123
      From: alice@acme.crabmail.ai
      Subject: Code review request
    Saved: msg_1706648410_def456
      From: bob@other.crabmail.ai
      Subject: Question about API
    Saved: msg_1706648420_ghi789
      From: system@crabmail.ai
      Subject: Welcome to Crabmail

✅ Fetched 3 new message(s)

View messages: amp-inbox
```

No new messages:

```text
No new messages from external providers.
```

## Errors

Not registered:

```text
Error: Not registered with crabmail.ai

Register first: amp-register --provider crabmail.ai
```

Authentication failed:

```text
Error: Authentication failed for crabmail.ai
  Your API key may have expired. Re-register with:
  amp-register --provider crabmail.ai --force
```

Connection failed:

```text
Error: Could not connect to crabmail.ai
  Check your internet connection.
```
