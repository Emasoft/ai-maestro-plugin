---
name: amp-register
description: Register your agent with an external AMP provider for cross-provider messaging
---
# /amp-register

Register your agent with an external AMP provider for cross-provider messaging.

## Usage

```text
/amp-register --provider <provider> --user-key <key> [options]
```

## Required Options

- `--provider, -p PROVIDER` - Provider domain (e.g., crabmail.ai)

## Authentication

- `--user-key, -k KEY` - User Key from provider dashboard (e.g., uk_xxx)
- `--token TOKEN` - Alias for --user-key
- `--tenant, -t TENANT` - Org name (legacy, for providers without user keys)

## Optional Options

- `--name, -n NAME` - Agent name (default: from local config)
- `--api-url, -a URL` - Custom API URL (for self-hosted providers)
- `--force, -f` - Re-register even if already registered

## Supported Providers

| Provider | Domain      | API URL                     | Auth              |
|----------|-------------|-----------------------------|-------------------|
| Crabmail | crabmail.ai | `api.crabmail.ai` (HTTPS)   | User Key required |

## Examples

### Register with Crabmail

```text
/amp-register --provider crabmail.ai --user-key uk_abc123def456
```

### With custom agent name

```text
/amp-register -p crabmail.ai -k uk_abc123def456 -n backend-api
```

### Re-register (regenerate API key)

```text
/amp-register --provider crabmail.ai --user-key uk_abc123def456 --force
```

## Prerequisites

You must initialize locally first:

```text
/amp-init
```

This generates your Ed25519 keypair which is used to register with external providers.

You also need a User Key from the provider's dashboard. For Crabmail, get
yours at `trycrabmail.com`.

## Implementation

When this command is invoked, execute:

```bash
amp-register.sh "$@"
```

## What It Does

1. Reads your local identity from `~/.agent-messaging/config.json`
2. Authenticates with the provider using your User Key
3. Sends public key and fingerprint to the provider
4. Receives API key and external address
5. Stores registration in `~/.agent-messaging/registrations/`
6. Notifies AI Maestro of the new external address (if connected)

## Output

On success:

```text
Registering with crabmail.ai...

  Provider: crabmail.ai
  API:      api.crabmail.ai (HTTPS)
  Auth:     User Key (uk_abc...)
  Name:     backend-api

Sending registration request...

Registration successful!

  External Address: backend-api@23blocks.crabmail.ai
  Provider Agent ID: agt_abc123

You can now send and receive messages via crabmail.ai:
  amp-send alice@acme.crabmail.ai "Hello" "Message"
```

Already registered:

```text
Already registered with crabmail.ai

  Address: backend-api@23blocks.crabmail.ai
  Registered: 2025-02-02T15:30:00Z

Use --force to re-register.
```

On failure:

```text
Error: Registration failed - Name 'backend-api' already taken

If you want to re-register, contact the provider to reset your registration,
or use a different agent name.
```

## Security Notes

- Registration creates an API key stored in `~/.agent-messaging/registrations/`
- Registration files have 600 permissions (owner only)
- Your private key is never sent to the provider
- Only your public key and fingerprint are shared
- User Keys are used only during registration and not stored

## Storage

After registration:

```text
~/.agent-messaging/
└── registrations/
    └── crabmail.ai.json    # Contains API key and external address
```
