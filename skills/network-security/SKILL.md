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

AI Maestro uses a dual-bind server with TCP-level IP filtering. The server binds to `::` (all interfaces, dual-stack IPv4+IPv6) when Tailscale is detected, but only allows connections from localhost and Tailscale VPN IPs. All other connections (LAN, public internet) are dropped at the TCP level before any HTTP/WebSocket processing.

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

## Prerequisites

### Install Tailscale

| Platform | Install |
|----------|---------|
| **macOS** | Download from https://tailscale.com/download or `brew install --cask tailscale` |
| **Linux (Debian/Ubuntu)** | `curl -fsSL https://tailscale.com/install.sh \| sh` then `sudo tailscale up` |
| **Linux (other)** | See https://tailscale.com/kb/1031/install-linux |
| **Windows WSL** | Install Tailscale on Windows host (not inside WSL). WSL inherits the tailnet. |
| **iOS/iPadOS** | App Store: search "Tailscale", install, sign in with same account |
| **Android** | Play Store: search "Tailscale", install, sign in with same account |

All devices must be signed into the **same Tailscale account** (same tailnet).

### Verify Tailscale is Running

```bash
tailscale status
```

This shows all devices in your tailnet with their Tailscale IPs.

## Remote Access (iPad, Phone, Laptop)

Access the dashboard from any device in the same Tailscale VPN:

```
http://<YOUR-TAILSCALE-IP>:23000
```

### Finding Your Host's Tailscale IP

```bash
# On the machine running AI Maestro:
tailscale ip -4    # IPv4 (e.g., 100.x.x.x)
tailscale ip -6    # IPv6 (e.g., fd7a:115c:a1e0::xxxx:xxxx)
tailscale status   # Full status with all devices and IPs
```

The Tailscale IPv4 address (starting with `100.`) is the most reliable. Use it in the browser on your remote device.

### Platform-Specific Notes

**macOS host:**
- If you previously had ProtonVPN (or similar VPN) installed and uninstalled, an orphaned network extension may block incoming connections. Fix: reinstall the VPN app, disable it, reboot.
- Check for orphaned extensions: `systemextensionsctl list 2>&1 | grep -v tailscale`

**Linux host:**
- Ensure the firewall allows port 23000: `sudo ufw allow 23000/tcp` (UFW) or `sudo firewall-cmd --add-port=23000/tcp --permanent` (firewalld)
- If using `iptables`, add: `iptables -A INPUT -s 100.64.0.0/10 -p tcp --dport 23000 -j ACCEPT`

**Windows WSL host:**
- AI Maestro runs inside WSL but Tailscale runs on Windows
- The Tailscale IP is assigned to the Windows host, not WSL
- WSL port forwarding may be needed: `netsh interface portproxy add v4tov4 listenport=23000 listenaddress=0.0.0.0 connectport=23000 connectaddress=127.0.0.1`

**iOS/iPadOS client:**
- MagicDNS hostnames (`*.ts.net`) may NOT resolve — use the raw IPv4 address instead
- Bookmark `http://<tailscale-ip>:23000` or add to Home Screen for quick access
- Tailscale must be connected (check the Tailscale app shows "Connected")

**Android client:**
- Same as iOS: use raw IPv4 if MagicDNS doesn't resolve
- Tailscale app must show "Connected"

## Known Limitations

### MagicDNS Does Not Work Reliably on Mobile
- `http://<hostname>.tail*.ts.net:23000` may NOT resolve from iPad/iPhone/Android
- Short form `http://<hostname>:23000` may also fail
- Root cause: mobile Tailscale apps don't always inject their DNS resolver
- **Workaround**: always use the raw Tailscale IPv4 address (`100.x.x.x`)
- The IPv4 address is stable — it doesn't change unless the device is removed from the tailnet

### Tailscale IPv6 Untested from Mobile
- The IPv6 ULA address (`fd7a:...`) is assigned and the IP filter allows it
- macOS Tailscale cannot loopback IPv6 to itself (only works from remote devices)
- Mobile browsers may not support IPv6 literal URLs (`http://[fd7a:...]:23000`)
- Use IPv4 (`100.x.x.x`) as the reliable path

### HTTPS Not Available by Default
- WireGuard already encrypts all Tailscale tunnel traffic end-to-end
- HTTPS on top requires enabling certificates in the Tailscale admin console (one-time manual step at https://login.tailscale.com/admin/dns)
- `tailscale serve` was tested but breaks Next.js static file serving — not used
- Current access is HTTP over WireGuard (encrypted tunnel, unencrypted localhost last-mile)

### No Human User Authentication (Phase 2)
- Any device in the tailnet can access the full dashboard without login
- Acceptable for single-user tailnets; risky for shared tailnets
- Phase 2 will add maestro credentials (username + password per host)
- Design: `docs_dev/2026-04-02-maestro-auth-design.md`

## Diagnostics

### Check if Tailscale is running
```bash
tailscale status
```

### Check what the server is listening on
```bash
# macOS / Linux:
lsof -i :23000 -P | grep LISTEN
# Windows WSL:
ss -tlnp | grep 23000
```

### Test connectivity from the host itself
```bash
# Should return 200 (allowed):
curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:23000/api/sessions"
curl -s -o /dev/null -w "%{http_code}" "http://$(tailscale ip -4):23000/api/sessions"

# Should return 000 or connection refused (blocked):
# macOS:
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://$(ipconfig getifaddr en0):23000/api/sessions"
# Linux:
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://$(hostname -I | awk '{print $1}'):23000/api/sessions"
```

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| White/blank page on localhost | PM2 serving stale build | `pm2 restart ai-maestro` after `yarn build` |
| Remote device can't connect at all | Orphaned VPN extension or firewall | Check `systemextensionsctl list`, check `ufw`/`iptables`/Windows Firewall |
| Mobile: "server not found" | MagicDNS not resolving | Use raw IPv4: `http://100.x.x.x:23000` |
| 404 on Tailscale IP | `tailscale serve` HTTP proxy active | `tailscale serve reset` (not needed with direct bind) |
| LAN IP works (shouldn't) | IP filter not loaded | Check PM2 logs for `[Tailscale]` messages; restart |
| Connection timeout | Tailscale not connected on remote device | Open Tailscale app, verify "Connected" status |

## Error Handling

If Tailscale is not installed or not running, the server silently falls back to `127.0.0.1`-only binding. No error, no crash — just localhost access only. Check PM2 logs for startup messages.

## Key Files

- `server.mjs` — `isAllowedSource()` IP filter + Tailscale IP detection + TCP connection filter
- `scripts/setup-tailscale-serve.sh` — Tailscale serve config script (available but not used in current architecture)
- `docs_dev/2026-04-02-maestro-auth-design.md` — Phase 2 maestro auth design
- `docs_dev/2026-04-02-remote-host-deep-audit.md` — Full security audit
