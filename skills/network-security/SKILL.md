---
name: network-security
user-invocable: false
description: "Network security model, Tailscale VPN access, IP filtering, and remote device connectivity. Use when configuring remote access or debugging connectivity."
allowed-tools: "Bash(tailscale:*), Bash(curl:*), Bash(ping:*), Bash(lsof:*), Bash(ifconfig:*), Bash(nc:*), Read, Grep"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

## Overview

AI Maestro uses a dual-bind server with TCP-level IP filtering. The server binds to `::` (all interfaces, dual-stack IPv4+IPv6) when Tailscale is detected, but only allows connections from localhost and Tailscale VPN IPs. All other connections (LAN, internet) are dropped at the TCP level before any HTTP/WebSocket processing.

Tailscale VPN is **required** for any remote access. Without Tailscale installed, the server falls back to `127.0.0.1`-only binding.

## How It Works

The server (`server.mjs`) auto-detects Tailscale at startup:
1. Runs `tailscale ip -4` to get the Tailscale IPv4 address
2. If found, binds to `::` (dual-stack) instead of `127.0.0.1`
3. Registers a TCP `connection` event filter that calls `isAllowedSource()`
4. Non-allowed source IPs get `socket.destroy()` — connection killed before HTTP

### Allowed Source IPs

| Range | Description |
|-------|-------------|
| `127.0.0.1` | IPv4 localhost |
| `::1` | IPv6 localhost |
| `100.0.0.0/8` | Tailscale CGNAT range (IPv4) |
| `fd7a:115c:a1e0::/48` | Tailscale ULA range (IPv6) |

Everything else is dropped.

## Remote Access (iPad, Phone, Laptop)

Access the dashboard from any device in the same Tailscale VPN:

```
http://<tailscale-ipv4>:23000
```

Example: `http://100.99.233.43:23000`

### Finding the Tailscale IP

```bash
tailscale ip -4    # IPv4 (e.g., 100.99.233.43)
tailscale ip -6    # IPv6 (e.g., fd7a:115c:a1e0::8137:e92b)
tailscale status   # Full status with all devices
```

## Known Limitations

### MagicDNS Does Not Work on iOS
- `http://<hostname>.tail*.ts.net:23000` does NOT resolve from iPad/iPhone
- Short form `http://<hostname>:23000` also does NOT resolve
- Root cause: iOS Tailscale app does not always inject its DNS resolver
- **Workaround**: always use the raw Tailscale IPv4 address
- The IPv4 address is stable (doesn't change unless the device is removed from the tailnet)

### Tailscale IPv6 Untested from Mobile
- The IPv6 ULA address (`fd7a:...`) is assigned and the IP filter allows it
- Cannot self-connect on macOS (Tailscale app doesn't loopback IPv6)
- Untested from iPad — Safari may not support IPv6 literal URLs in the address bar
- Use IPv4 (`100.x.x.x`) as the reliable path

### HTTPS Not Available by Default
- WireGuard already encrypts all Tailscale tunnel traffic
- HTTPS on top requires enabling certificates in the Tailscale admin console (one-time manual step)
- `tailscale serve` was tested but breaks Next.js static file serving — not used
- Current access is HTTP over WireGuard (encrypted tunnel, unencrypted last-mile on localhost)

### No Human User Authentication (Phase 2)
- Any device in the tailnet can access the full dashboard
- Phase 2 will add maestro credentials (username + password per host)
- Design: `docs_dev/2026-04-02-maestro-auth-design.md`

## Diagnostics

### Check if Tailscale is running
```bash
tailscale status
```

### Check what the server is listening on
```bash
lsof -i :23000 -P | grep LISTEN
```

### Test connectivity from another device
```bash
# From the target device (or simulate from the host):
curl -s -o /dev/null -w "%{http_code}" "http://<tailscale-ip>:23000/api/sessions"
```

### Check the IP filter is working
```bash
# Should return 200 (allowed):
curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:23000/api/sessions"
curl -s -o /dev/null -w "%{http_code}" "http://$(tailscale ip -4):23000/api/sessions"

# Should return 000 or connection refused (blocked):
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://$(ipconfig getifaddr en0):23000/api/sessions"
```

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| White page on localhost | PM2 serving stale build | `pm2 restart ai-maestro` after `yarn build` |
| iPad can't connect at all | Orphaned VPN extension (ProtonVPN, etc.) | Reinstall the VPN app, disable it, reboot |
| iPad: "server not found" | MagicDNS not resolving on iOS | Use raw IPv4: `http://100.x.x.x:23000` |
| 404 on Tailscale IP | `tailscale serve` HTTP proxy active | `tailscale serve reset` (not needed with direct bind) |
| LAN IP works (shouldn't) | IP filter not loaded | Check PM2 logs for Tailscale detection errors |

## Error Handling

If Tailscale is not installed or not running, the server silently falls back to `127.0.0.1`-only binding. No error, no crash — just localhost access only. Check PM2 logs for `[Tailscale]` entries.

## Key Files

- `server.mjs:89-104` — `isAllowedSource()` IP filter + Tailscale IP detection
- `server.mjs:1316-1323` — TCP connection filter on `::` bind
- `scripts/setup-tailscale-serve.sh` — Tailscale serve config script (available but not used in current architecture)
- `docs_dev/2026-04-02-maestro-auth-design.md` — Phase 2 maestro auth design
- `docs_dev/2026-04-02-remote-host-deep-audit.md` — Full security audit
