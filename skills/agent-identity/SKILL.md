---
name: agent-identity
description: "Use when managing agent identity — Ed25519 keys, proof of possession, OAuth token exchange. Trigger with /amp-identity, 'create agent identity', 'get API token'."
license: MIT
compatibility: Requires curl, jq, openssl (3.x for Ed25519), and base64 CLI tools. macOS and Linux supported.
metadata:
  version: "0.3.0"
  homepage: "https://agentids.org"
  repository: "https://github.com/agentmessaging/agent-identity"
---

# Agent Identity (AID) Protocol

## Overview

Authenticate AI agents with auth servers using the Agent Identity (AID) protocol. AID uses Ed25519 cryptographic identity documents and proof of possession to obtain scoped JWT tokens via OAuth 2.0 token exchange. It is self-contained and works independently without other protocols.

## Prerequisites

Copy this checklist and track your progress:

- [x] `curl`, `jq`, `openssl` (3.x with Ed25519 support), and `base64` on PATH
- [x] AID scripts installed to `~/.local/bin/` (via `install-messaging.sh` or manual install)
- [ ] For registration: an admin JWT token and auth server URL
- [ ] For token exchange: a prior registration with the auth server

## Instructions

1. Initialize identity (one-time): `aid-init.sh --auto` — creates Ed25519 keypair at `~/.agent-messaging/agents/<name>/`
2. Register with auth server (one-time): `aid-register.sh --auth <url> --token <JWT> --role-id 2`
3. Get a JWT token: `TOKEN=$(aid-token.sh --auth <url> --quiet)` then use in API calls
4. Check status

```bash
aid-status.sh          # Human-readable
aid-status.sh --json   # JSON output
```

For full command reference, flags, and parameters, see [detailed-guide](reference/detailed-guide.md).

## Output

- `aid-init.sh` — creates Ed25519 keypair and identity document in `~/.agent-messaging/agents/<name>/`
- `aid-register.sh` — stores registration details locally for future token exchanges
- `aid-token.sh` — returns a JWT access token (string or JSON); cached until expiry
- `aid-status.sh` — displays identity info, registrations, and token cache status

## Error Handling

| Problem | Solution |
|---------|----------|
| "Agent identity not initialized" | Run `aid-init.sh --auto` |
| "Not registered" | Run `aid-register.sh` with auth server details |
| "Proof expired" | Clock skew >5 minutes; sync system clock |
| "Invalid signature" | Re-init with `aid-init.sh --auto --force` and re-register |
| "Agent suspended" | Contact admin for reactivation |
| "403 on token exchange" | Run `aid-status.sh` to check registration state |

For the full troubleshooting table, see [detailed-guide](reference/detailed-guide.md).

## Examples

**Initialize and register a new agent:**
```bash
aid-init.sh --auto
aid-register.sh --auth https://auth.23blocks.com/acme --token $ADMIN_JWT --role-id 2
```

**Get a scoped token for file access:**
```bash
TOKEN=$(aid-token.sh --auth https://auth.23blocks.com/acme --scope "files:read files:write" --quiet)
```

**Natural language mappings:**
- "Initialize my identity" -> `aid-init.sh --auto`
- "Get me an API token" -> `aid-token.sh --auth <url>`
- "Check my registrations" -> `aid-status.sh`

## Resources

- Detailed command reference: [detailed-guide](reference/detailed-guide.md)
- Protocol specification: https://agentids.org
- GitHub repository: https://github.com/agentmessaging/agent-identity
- Interoperability: AID shares `~/.agent-messaging/agents/` with AMP if both installed
