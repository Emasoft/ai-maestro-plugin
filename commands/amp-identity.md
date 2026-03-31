---
name: amp-identity
description: Quick identity check for AMP context recovery
---
# /amp-identity

Quick identity check for context recovery. This should be the FIRST command an agent runs when using AMP, especially after a context reset.

## Usage

```
/amp-identity [options]
```

## Options

- `--json, -j` - Output as JSON
- `--brief, -b` - One-line summary

## What It Shows

- Agent name and address
- Tenant/organization
- Public key fingerprint
- Initialization status

## Examples

### Check identity (human-readable)

```
/amp-identity
```

### Get JSON output

```
/amp-identity --json
```

### One-line summary

```
/amp-identity --brief
```

## Implementation

When this command is invoked, execute:

```bash
amp-identity.sh "$@"
```

## Output

Human-readable:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AMP Identity
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Name:        backend-api
  Tenant:      23blocks
  Address:     backend-api@23blocks.aimaestro.local
  Fingerprint: a1b2c3d4e5f6...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Brief:
```
AMP: backend-api@23blocks.aimaestro.local (a1b2c3d4e5f6...)
```

JSON:
```json
{
  "initialized": true,
  "name": "backend-api",
  "tenant": "23blocks",
  "address": "backend-api@23blocks.aimaestro.local",
  "fingerprint": "a1b2c3d4e5f6..."
}
```

## When to Use

- **First thing after context reset** — rediscover who you are
- **Before sending messages** — verify your identity is correct
- **Debugging** — confirm AMP is initialized and keys exist
