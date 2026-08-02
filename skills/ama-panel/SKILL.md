---
name: ama-panel
user-invocable: false
description: "Drive an agent's HTML dashboard side panel via the frozen aimaestro-panel.sh CLI — push HTML or a live URL, open/close/refresh the panel, check how many dashboard clients are connected, and drain feedback events the panel's HTML posted back. Use when an agent wants to render a status view, a form, or a live page in its own dashboard panel. Trigger with 'show this in my side panel', 'push this HTML to my panel', 'check if anyone is watching my panel', 'read panel feedback'. CRITICAL gotcha: 'delivered: 0' from open/set means the content was DROPPED, not queued — always check status first when delivery matters. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-panel.sh:*), Bash(jq:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-panel — drive an agent's HTML dashboard side panel

## Overview

`ama-panel` wraps the frozen `aimaestro-panel.sh` CLI (Tier A, §2.1 of
`SCRIPT-MANIFEST.md`): the surface an agent uses to render content — HTML or
a live URL — into its own dashboard side panel, and to read back feedback
the rendered page posts. It never talks to the AI Maestro API directly; the
CLI resolves the API base and the caller's identity internally.

## THE GOTCHA — read this before relying on any `set` / `open` result

**`delivered: N` on `open`/`set` is a live-channel count, not a queue
depth.** Unlike `ama-session`'s `queue`, the panel is a **live surface** —
there is no server-side hold-and-drain for it. **`delivered: 0` means the
content was DROPPED**, not "waiting for someone to look" — it means no
dashboard client currently has that agent's panel open. If delivery
actually matters (the panel is carrying something the user needs to see,
not just a nice-to-have), **check `status` first**:

```bash
aimaestro-panel.sh status <agent>
```

`status` reports the number of connected dashboard clients and the pending
feedback-event count. If it reports zero clients, `set`/`open` will report
`delivered: 0` and you should not treat the push as having reached anyone.

## Authorization

Per `TRDD-D3RP7KQZ`: an agent drives its **own** panel by default. Targeting
**another** agent's panel requires MANAGER (any agent) or CHIEF-OF-STAFF
(agents of its own team). **Strict verbs** (agent: AID + title; human: fresh
sudo-token): `open`, `close`, `refresh`, `set`. **Non-strict**: `status`,
`feedback`.

## Security constraints on pushed content

- Pushed HTML renders in a **sandboxed `iframe srcdoc`** — no
  `allow-same-origin`, so it cannot read the dashboard's own cookies/storage.
- A live `--url` renders **with** `allow-same-origin` (it's a real page you
  are choosing to trust), and only `https:`/`http:` schemes are accepted —
  `javascript:`, `file:`, and `data:` URLs are rejected with a 400.
- HTML content is capped at **2 MB**.

## Prerequisites

- AI Maestro running; `aimaestro-panel.sh` on `PATH` (installed by
  `install-messaging.sh`; re-run it if missing).
- The CLI resolves your agent identity + bearer token internally.
- `jq` for parsing JSON output.

## Instructions

1. Decide what you're rendering: static HTML (`--html` inline or
   `--html-file <path>`) or a live page (`--url`).
2. If delivery matters, check who's watching first:

   ```bash
   aimaestro-panel.sh status <agent>
   ```

3. Push the content and open the panel:

   ```bash
   aimaestro-panel.sh set <agent> --html-file /tmp/status.html
   aimaestro-panel.sh open <agent>
   ```

   Or push a live URL:

   ```bash
   aimaestro-panel.sh set <agent> --url "https://example.com/live-status"
   ```

4. **Check the `delivered` count in the response.** `0` means dropped — the
   panel wasn't open anywhere. If the content is important, `open` the
   panel first (or tell the user to open their dashboard) and re-`set`.
5. `refresh <agent>` to re-render after pushing new content without
   toggling open/close. `close <agent>` when done.
6. Drain any feedback the pushed HTML posted back (e.g. a form submit inside
   the `iframe`):

   ```bash
   aimaestro-panel.sh feedback <agent>
   ```

   `feedback` **drains** — it reads and clears in one call; a second call
   returns nothing new until more feedback arrives.

### Quick CLI Reference

| Subcommand | Flags | Verb class |
|---|---|---|
| `open <agent>` | `--url <https-url>` | **strict** |
| `close <agent>` | — | **strict** |
| `refresh <agent>` | — | **strict** |
| `set <agent>` | exactly one of `--html-file <path>` \| `--html "<html>"` \| `--url <https-url>` | **strict** |
| `status <agent>` | — | non-strict |
| `feedback <agent>` | — | non-strict, drains (read + clear) |

## Output

JSON on STDOUT (pipe to `jq`). `set`/`open` return `{ "delivered": N, ... }`.
`status` returns the connected-client count and pending-feedback count.
`feedback` returns the drained events (empty array if none).

## Error Handling

| Symptom | Likely cause |
|---|---|
| `delivered: 0` | no dashboard client has this agent's panel open — check `status`, ask the user to open it, or accept the push was a no-op |
| 400 on `--url` | scheme is not `https:`/`http:`, or the URL was `javascript:`/`file:`/`data:` |
| 400 on `--html`/`--html-file` | content exceeds the 2 MB cap |
| 403 targeting another agent | you are not MANAGER, and not that agent's own-team COS |
| `feedback` returns empty every time | either nothing has been submitted yet, or it was already drained by a prior call |

## Examples

<example>
Push a status page and confirm it actually reached someone.
→ `aimaestro-panel.sh status <agent>` (check client count) → if non-zero,
`aimaestro-panel.sh set <agent> --html-file status.html` → confirm
`delivered` in the response is non-zero.
</example>

<example>
Render a live external dashboard instead of static HTML.
→ `aimaestro-panel.sh set <agent> --url "https://example.com/dashboard"`
(rejected 400 if the scheme isn't `https:`/`http:`).
</example>

<example>
Read back a form the panel's HTML posted.
→ `aimaestro-panel.sh feedback <agent>` — remember this drains; the same
events won't show up on a second call.
</example>

## Scope

Drives an agent's **own** dashboard panel, or another agent's when the
caller is MANAGER (any) / COS (own team). Terminal/state control is
`ama-session`. Server-mediated TRDD search/read is `ama-trdd-server`.

## Resources

- `.claude/rules/aimaestro-manager-approval-defaults.md` — the
  EXEMPT/NON-EXEMPT split this skill's strict/non-strict verbs mirror
  (the ai-maestro DEP overlay, seeded into every agent workdir).

## Use also

- `Skill(skill: "ama-session")` — drive the agent's terminal/state; the
  companion self-drive surface to this one.
- `Skill(skill: "team-governance")` — the titles (MANAGER/COS/…) this
  skill's cross-agent targeting rule is keyed on.
