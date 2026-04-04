---
name: network-security
user-invocable: false
description: "Network security model, Tailscale VPN access, IP filtering, and remote device connectivity. Use when configuring remote access or debugging connectivity.. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(tailscale:*), Bash(curl:*), Bash(ping:*), Bash(lsof:*), Bash(ifconfig:*), Bash(nc:*), Read, Grep"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# Network Security

## Overview

AI Maestro uses a dual-bind server with TCP-level IP filtering. The server binds to `::` (all interfaces) when Tailscale is detected, but only allows connections from localhost and Tailscale VPN IPs. All other connections (LAN, public internet) are dropped at the TCP level before any HTTP/WebSocket processing.

Tailscale VPN is **required** for any remote access. Without it, the server falls back to `127.0.0.1`-only binding.

## Prerequisites

- Tailscale installed and running on the host machine
- All remote devices signed into the same Tailscale account (same tailnet)
- Port 23000 allowed in firewall (Linux: `sudo ufw allow 23000/tcp`)

Copy this checklist and track your progress:

- [ ] Tailscale installed and running (`tailscale status`)
- [ ] Host Tailscale IP found (`tailscale ip -4`)
- [ ] Remote device connected to tailnet
- [ ] Port 23000 accessible on host

## Instructions

1. **Install Tailscale** on the host (see prerequisites table in [reference](references/REFERENCE.md))
2. **Find your host's Tailscale IPv4**: `tailscale ip -4` — this is the `100.x.x.x` address
3. **Connect remote device** to the same Tailscale account
4. **Access the dashboard** from any tailnet device: `http://<tailscale-ip>:23000`
5. **For mobile (iOS/iPadOS/Android)**: use the raw IPv4 address — MagicDNS hostnames (`*.ts.net`) may not resolve on mobile
6. **Diagnose connection issues**: check the troubleshooting table in [reference](references/REFERENCE.md)

## Output

- Server startup logs show `[Tailscale]` messages indicating bind mode and detected IP
- `tailscale status` shows all tailnet devices and their IPs
- `lsof -i :23000 -P | grep LISTEN` shows what address the server is bound to

## Error Handling

| Symptom | Cause | Fix |
|---------|-------|-----|
| Remote device can't connect | Orphaned VPN extension or firewall | Check `systemextensionsctl list`, check `ufw`/`iptables` |
| Mobile: "server not found" | MagicDNS not resolving | Use raw IPv4: `http://100.x.x.x:23000` |
| LAN IP works (shouldn't) | IP filter not loaded | Check PM2 logs for `[Tailscale]` messages; restart |
| Connection timeout | Tailscale not connected | Open Tailscale app, verify "Connected" status |

If Tailscale is not running, the server silently falls back to localhost-only binding.

## Examples

```bash
# Find Tailscale IP on host machine
tailscale ip -4
# Returns: 100.x.x.x

# Test connectivity from host
curl -s -o /dev/null -w "%{http_code}" "http://$(tailscale ip -4):23000/api/sessions"
# Expected: 200

# Check server is listening on correct address
lsof -i :23000 -P | grep LISTEN
```

## Resources

- [Network Security Reference](references/REFERENCE.md)
  - IP Filter Implementation
  - Tailscale CGNAT Range Detail
  - Server Bind Modes
  - Port 23000
  - WebSocket Security
  - AMP Message Security
