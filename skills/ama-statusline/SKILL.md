---
name: ama-statusline
user-invocable: false
description: "Read the fleet's 5h/7d rate-limit windows at ZERO API cost via the frozen aimaestro-statusline.sh CLI — the windows arrive free in Claude Code's statusline payload, so get/list hand them back without spending a call on the usage endpoint. Use when checking remaining budget before a batch, finding which session is closest to a cap, or reading the fleet roll-up. Trigger with 'how much rate-limit is left across the fleet', 'which session is nearest its 5h cap', 'read the statusline feed'. Does NOT carry model-scoped weekly windows, severity, or is_active — those stay endpoint-only. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-statusline.sh:*), Bash(aid-auth.sh:*), Bash(jq:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-statusline — free rate-limit windows from the statusline feed

## Overview

`ama-statusline` wraps the frozen `aimaestro-statusline.sh` CLI — **the only thing
in the ecosystem that knows the statusline endpoints.** Claude Code pipes a
statusline payload on every turn, and that payload already contains the 5-hour and
7-day rate-limit windows. This CLI stores and serves them, so an agent can read
remaining budget **without spending an API call** on `/api/oauth/usage`.

Per the decoupling invariant no plugin, skill, hook or agent may curl the AI
Maestro API directly. This script is the immutable CLI in front of it: new
capability arrives as a new subcommand or a new optional flag, never as a changed
contract.

## What is and is NOT in this feed

**In:** the 5h and 7d window readings, per session, plus a fleet roll-up.

**Not in — and do not expect them here:** the model-scoped weekly windows,
`severity`, and `is_active`. Those remain endpoint-only. Reading their absence as
"the fleet is fine" is the mistake this section exists to prevent: the feed is
silent about them, not reassuring about them.

## Auth is asymmetric — and `ingest` deliberately needs none

| verb | credential |
|---|---|
| `get` / `list` | ordinary fleet reads — agent callers export `AID_AUTH`; a human uses the dashboard session cookie |
| `ingest` | **none.** The route is console-only, because Claude Code runs the user's statusline in a plain terminal with neither cookie nor token |

That `ingest` is uncredentialed is a deliberate consequence of where statuslines
run, not an oversight to "harden".

## Prerequisites

- AI Maestro running; `aimaestro-statusline.sh` on `PATH` (installed by
  `install-messaging.sh`).
- For `get`/`list` as an agent: `export AID_AUTH="$(aid-auth.sh)"`.
- `jq` for parsing.

## Instructions

1. **Fleet roll-up — the tightest window across live sessions.** This is the one
   to read before committing to a batch, because the binding constraint is
   whichever session is closest to a cap, not the average:

   ```bash
   aimaestro-statusline.sh list | jq '.'
   ```

2. **One session's last observation**, with its age:

   ```bash
   aimaestro-statusline.sh get "$SESSION_ID"
   ```

   **Check the age.** A stale observation is a reading from a session that has
   stopped reporting — it describes the past, and treating it as current is how a
   dead session looks healthy.

3. `ingest` is what `aimaestro-statusline-capture.sh` forks, detached. Agents do
   not normally call it by hand; it exists for the capture path.

### Quick CLI Reference

| Subcommand | Args | Auth |
|---|---|---|
| `list` | — | `AID_AUTH` / cookie |
| `get <sessionId>` | session id | `AID_AUTH` / cookie |
| `ingest` | `[--file PATH]`, else JSON on stdin | none (console-only route) |

## Output

JSON on STDOUT. `list` returns the fleet roll-up (tightest 5h/7d); `get` returns
the last stored observation plus its age.

## Error Handling

| Symptom | Likely cause |
|---|---|
| auth failure on `get`/`list` | `AID_AUTH` not exported and no dashboard cookie |
| `get` returns nothing for a real session | that session has not reported a statusline payload yet |
| the reading looks frozen | check the age field — the session may have stopped reporting |
| looking for `severity` / `is_active` / weekly model windows | not in this feed by design — use the usage endpoint |

## Examples

<example>
Decide whether a long batch fits before starting it.
→ `aimaestro-statusline.sh list | jq '.'` — read the TIGHTEST window, since that
session is the one that will hit a cap first.
</example>

<example>
A session looks idle; is it actually reporting?
→ `aimaestro-statusline.sh get "$SESSION_ID"` and read the AGE, not just the
percentages.
</example>

## Scope

The statusline-derived window feed. The caller's OWN window health plus
self-resume is `ama-continuity`; agent lifecycle is `ai-maestro-agents-management`.

## Use also

- `Skill(skill: "ama-continuity")` — the caller's own window health and the
  `next_action` recommendation, plus self-resume.
- `Skill(skill: "agent-identity")` — where `AID_AUTH` comes from.
