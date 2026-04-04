# Network Security Reference

## Table of Contents
- [IP Filter Implementation](#ip-filter-implementation)
- [Tailscale CGNAT Range Detail](#tailscale-cgnat-range-detail)
- [Server Bind Modes](#server-bind-modes)
- [Port 23000](#port-23000)
- [WebSocket Security](#websocket-security)
- [AMP Message Security](#amp-message-security)

---

## IP Filter Implementation

The `isAllowedSource()` function in `server.mjs`:

```javascript
function isAllowedSource(remoteAddress) {
  if (!remoteAddress) return false
  const ip = remoteAddress.replace(/^::ffff:/, '') // Strip IPv4-mapped IPv6 prefix
  if (ip === '127.0.0.1' || ip === '::1' || ip === 'localhost') return true
  if (/^100\./.test(ip)) return true           // Tailscale CGNAT (100.64.0.0/10)
  if (/^fd7a:115c:a1e0:/.test(ip)) return true // Tailscale IPv6 ULA
  return false
}
```

### Why these ranges?

| Range | RFC | Owner | Why safe |
|-------|-----|-------|----------|
| `100.64.0.0/10` | RFC 6598 | CGNAT shared space | Tailscale exclusively uses this range within tailnets; not routable on the public internet |
| `fd7a:115c:a1e0::/48` | RFC 4193 | Tailscale ULA | Unique Local Address — Tailscale's specific prefix; not globally routable |
| `127.0.0.0/8` | RFC 1122 | Loopback | Local machine only |
| `::1/128` | RFC 4291 | IPv6 loopback | Local machine only |

### Why `::ffff:` stripping?

When an IPv4 client connects to an IPv6-bound server (`::` bind), Node.js reports the address as `::ffff:192.168.1.100` (IPv4-mapped IPv6). The `replace(/^::ffff:/, '')` strips this prefix so the filter can match raw IPv4 patterns.

## Tailscale CGNAT Range Detail

Tailscale assigns addresses from `100.64.0.0/10` (the CGNAT shared address space). This is a /10 block — addresses `100.64.0.0` through `100.127.255.255`. Our filter uses `/^100\./` which matches `100.0.0.0/8` — slightly broader but still not publicly routable. The extra range `100.0.0.0-100.63.255.255` is unassigned IANA space that no ISP or service uses.

## Server Bind Modes

| Tailscale | HOSTNAME env | Bind address | Security |
|-----------|-------------|--------------|----------|
| Detected | Not set | `::` (dual-stack) + IP filter | Localhost + Tailscale only |
| Detected | `127.0.0.1` | `::` + IP filter | Same (HOSTNAME is overridden) |
| Detected | `0.0.0.0` | `0.0.0.0` + IP filter | Same (filter still active) |
| Not detected | Not set | `127.0.0.1` | Localhost only |
| Not detected | `0.0.0.0` | `0.0.0.0` (NO filter!) | All interfaces — INSECURE |

**Warning:** Setting `HOSTNAME=0.0.0.0` without Tailscale installed bypasses the IP filter entirely. The filter is only activated when Tailscale is detected.

## Port 23000

AI Maestro uses port 23000 (configured in PM2). This port is:
- Not a well-known port (no conflicts with standard services)
- Must be allowed in Tailscale ACLs (default ACLs allow all ports between tailnet devices)
- Blocked by `isAllowedSource()` for non-Tailscale IPs even when listening on `0.0.0.0`

## WebSocket Security

Terminal WebSocket connections (`/term?name=<session>&host=<hostId>`) go through the same TCP-level IP filter. A connection from a non-allowed IP is destroyed before the WebSocket upgrade happens.

For remote host terminal access (proxied via `handleRemoteWorker`):
1. Client connects to local server (must pass IP filter)
2. Local server opens a WebSocket to the remote host's Tailscale IP
3. Remote host's IP filter allows the connection (both hosts are in the same tailnet)
4. Bidirectional proxy established

## AMP Message Security

AMP (Agent Messaging Protocol) messages between hosts use HTTP POST to `/api/v1/route`. These requests:
1. Must come from a Tailscale IP (IP filter)
2. Must include a valid Bearer token (AMP API key)
3. Are signed with Ed25519 host keys for governance operations

An attacker outside the Tailscale VPN cannot send AMP messages because they cannot reach port 23000.
