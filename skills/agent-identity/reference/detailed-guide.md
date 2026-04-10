# Agent Identity (AID) Protocol — Detailed Guide

## Table of Contents

- [Installation](#installation)
- [Commands Reference](#commands-reference)
- [How AID Authentication Works](#how-aid-authentication-works)
- [Security](#security)
- [Interoperability](#interoperability)
- [Agent Lifecycle](#agent-lifecycle)
- [Token Introspection](#token-introspection)
- [Troubleshooting](#troubleshooting)
- [Protocol Reference](#protocol-reference)

Full reference for the Agent Identity protocol: Ed25519 identity documents,
proof of possession, OAuth 2.0 token exchange, and scoped JWT tokens.

## Installation

### For Claude Code (skill)

```bash
npx skills add agentmessaging/agent-identity
```

### Quick Install

```bash
INSTALL_URL="https://raw.githubusercontent.com/\
agentmessaging/agent-identity/main/install.sh"
curl -fsSL "$INSTALL_URL" | bash
```

### Manual

```bash
git clone https://github.com/agentmessaging/agent-identity.git ~/agent-identity
export PATH="$HOME/agent-identity/scripts:$PATH"
```

## Commands Reference

### aid-init.sh — Initialize Agent Identity

Create an Ed25519 keypair and identity for this agent.

```bash
aid-init.sh --auto              # Auto-detect name from environment
aid-init.sh --name my-agent     # Specify agent name
aid-init.sh --name my-agent --force  # Overwrite existing
```

**Parameters:**

- `--auto` — Auto-detect agent name from environment
- `--name, -n` — Specify agent name
- `--force, -f` — Overwrite existing identity

### aid-register.sh — Register with Auth Server

One-time registration linking the agent's Ed25519 identity to a tenant
with a specific role.

```bash
aid-register.sh --auth https://auth.23blocks.com/acme \
  --token <ADMIN_JWT> --role-id 2
```

**Parameters:**

- `--auth, -a` — Auth server URL (required)
- `--token, -t` — Admin JWT for authorization (required)
- `--role-id, -r` — Role ID to assign (required)
- `--api-key, -k` — API key (X-Api-Key header)
- `--name, -n` — Display name (default: agent name)
- `--description, -d` — Agent description
- `--lifetime, -l` — Token lifetime in seconds (default: 3600)

**What it does:**

1. Reads the agent's Ed25519 public key and identity
2. POSTs the registration to the server's agent registration endpoint
3. Stores the registration locally for future token exchanges

### aid-token.sh — Exchange Identity for JWT Token

Performs the OAuth 2.0 token exchange using `grant_type=urn:aid:agent-identity`.

```bash
# Get a token (uses cache if valid)
aid-token.sh --auth https://auth.23blocks.com/acme

# Get just the token string (for scripting)
TOKEN=$(aid-token.sh --auth https://auth.23blocks.com/acme --quiet)

# Get a token with specific scopes
aid-token.sh --auth https://auth.23blocks.com/acme --scope "files:read files:write"
```

**Parameters:**

- `--auth, -a` — Auth server URL (required)
- `--scope, -s` — Space-separated scopes (optional)
- `--json, -j` — Output as JSON
- `--quiet, -q` — Output only the token string
- `--no-cache` — Skip token cache

**What it does:**

1. Builds a fresh Agent Identity Document with current timestamp
2. Creates a Proof of Possession
   (`aid-token-exchange\n{timestamp}\n{auth_issuer}`)
3. Signs the proof with the agent's Ed25519 private key
4. POSTs to the OAuth token endpoint with
   `grant_type=urn:aid:agent-identity`
5. Returns the JWT access token (cached for reuse)

### aid-status.sh — Check Identity & Registration Status

```bash
aid-status.sh          # Human-readable output
aid-status.sh --json   # JSON output
```

## How AID Authentication Works

### Step 1: Agent Identity Document

A signed JSON document proving the agent's identity:

```json
{
  "aid_version": "1.0",
  "address": "support-agent@default.local",
  "alias": "support-agent",
  "public_key": "-----BEGIN PUBLIC KEY-----\n...",
  "key_algorithm": "Ed25519",
  "fingerprint": "SHA256:abc123...",
  "issued_at": "2026-03-23T00:00:00Z",
  "expires_at": "2026-09-23T00:00:00Z",
  "signature": "base64-ed25519-signature"
}
```

### Step 2: Proof of Possession

The agent signs a challenge proving it holds the private key:

```text
aid-token-exchange\n{timestamp}\n{auth_server_url}
```

### Step 3: Token Exchange

```text
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn%3Aaid%3Aagent-identity
&agent_identity={base64url-identity-document}
&proof={base64url-signed-proof}
```

### Step 4: Use the JWT

The server returns a standard OAuth 2.0 response with an RS256 JWT access
token. Use it with any API that validates JWTs via the auth server's JWKS
endpoint.

## Security

- **Self-contained** — no external protocol dependencies
- **Ed25519 signatures** — identity documents are cryptographically signed
- **Proof of possession** — agents prove key ownership at every token exchange
- **Human-controlled access** — admin creates roles and registers agents
- **Short-lived tokens** — JWTs expire quickly, limiting blast radius
- **No shared secrets** — private keys never leave the agent
- **Scoped access** — tokens carry only the permissions the agent's role allows

## Interoperability

AID shares the `~/.agent-messaging/agents/` directory with
[AMP](https://agentmessaging.org) if both are installed. One identity
serves both protocols. Neither requires the other.

## Agent Lifecycle

Agents have 4 lifecycle states controlled by the admin:

| Status      | Can get tokens? | Introspection                             |
|-------------|-----------------|-------------------------------------------|
| `pending`   | No              | `active: false`                           |
| `active`    | Yes             | `active: true`                            |
| `suspended` | No (403)        | `active: false, reason: agent_suspended`  |
| `deleted`   | No              | `active: false, reason: agent_not_found`  |

Admin commands:

- Suspend: `POST /agent_registrations/:id/suspend`
- Reactivate: `POST /agent_registrations/:id/reactivate`

## Token Introspection

Target APIs can verify agent tokens in real-time:

```text
POST /:tenant/oauth/introspect
token=eyJhbGciOiJSUz...
```

Returns `active: true/false` with agent details. Useful for detecting
suspended agents before their token expires.

## Troubleshooting

| Problem                          | Solution                                  |
|----------------------------------|-------------------------------------------|
| "Agent identity not initialized" | Run `aid-init.sh --auto`                  |
| "Not registered"                 | Run `aid-register.sh` with auth details   |
| "Proof expired"                  | Clock skew > 5 min; sync system clock     |
| "Invalid signature"              | Corrupted identity; re-init + re-register |
| "Fingerprint mismatch"           | Key changed since registration; re-reg    |
| "Scope not allowed"              | Request only granted scopes               |
| "Agent suspended"                | Admin suspended; contact for reactivation |
| "403 on token exchange"          | May be suspended; run `aid-status`        |

## Protocol Reference

- Full specification: <https://agentids.org>
- GitHub: <https://github.com/agentmessaging/agent-identity>
