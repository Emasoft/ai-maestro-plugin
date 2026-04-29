# TRDD-b02f376b — Tamper-proof title verification for the directory guard hook (MANAGER user-scope writes)

**TRDD ID:** `b02f376b-85d8-4f7d-a303-26e9050c4cb1`
**Filename:** `design/tasks/TRDD-b02f376b-85d8-4f7d-a303-26e9050c4cb1-manager-user-scope-writes.md`
**Tracked in:** `Emasoft/ai-maestro-plugins` → `ai-maestro-plugin/` (this repo, `design/tasks/` is git-tracked)
**Status:** Not started — awaiting AI Maestro core API support
**Owners:** AI Maestro core API agent (server) + ai-maestro-plugin maintainer (hook)
**Affects:** `scripts/directory-guard.cjs` (this plugin), `aimaestro-agent.sh` CLI behavior, AI Maestro server

---

## 1. Summary

The plugin's `directory-guard.cjs` PreToolUse hook currently sandboxes every Claude Code agent to its own work directory plus a small allowlist (`/tmp`, AMP messaging, per-agent Claude Code project state). This is correct for ordinary agents, but it breaks the **MANAGER** governance role: a MANAGER must be able to install **skills, agents, commands, rules, MCP servers, plugins** (and the like) at **user scope** (`~/.claude/...`) on behalf of other agents, using the AI Maestro CLI. The hook must allow those writes — but **only for verified MANAGER agents**, and the verification cannot rely on environment variables (they are agent-spoofable).

This TRDD requests an AI Maestro server-side capability that lets the directory-guard hook verify the calling agent's governance title via the agent's existing Ed25519 AID identity (the same identity AMP already uses), so the hook can grant MANAGER-only user-scope write permission without trusting any env var.

## 2. Background

### 2.1 Current directory-guard sandbox

The hook (`ai-maestro-plugin/scripts/directory-guard.cjs`) fires on every `Write`, `Edit`, `NotebookEdit`, and `Bash` tool call. It uses `AGENT_WORK_DIR` (env var) as the trusted source for the agent's sandbox root and allowlists:

1. `$AGENT_WORK_DIR/**` — agent's own project (covers project + local element scopes)
2. `/tmp/**` and `/private/tmp/**`
3. `$AGENT_WORK_DIR/.claude/**` — explicit alias for #1
4. `~/.agent-messaging/agents/<basename(AGENT_WORK_DIR)>/**` — AMP messaging
5. `~/.claude/projects/<encoded(AGENT_WORK_DIR)>/**` — Claude Code per-project state (auto-memory, transcripts, todos). Encoding: every non-`[A-Za-z0-9-]` char in the absolute path becomes `-`. Each agent only matches its own slot.

Rule #5 was just added (this session) to fix the auto-memory bug where Claude Code's built-in memory system writes to `~/.claude/projects/<encoded>/memory/<name>.md` — every agent needs that.

For Bash, the hook scans the command for write-capable patterns (`>`, `tee`, `cp`, `mv`, `curl -o`, `python -c "...open(...)"`, `dd of=`, `sed -i`, `rm`, `chmod`, `ln -s`, etc.) and calls `isAllowedPath()` on each detected target.

### 2.2 Why the env-var approach is insufficient

The first design considered was: AI Maestro sets `AGENT_TITLE=MANAGER` at agent launch; the hook reads it and unlocks user-scope writes. **This is rejected**:

- An agent can `export AGENT_TITLE=MANAGER` (in any spawned shell) before issuing the Write. The hook would see "MANAGER" in `process.env` and allow the write.
- Even though the hook process is short-lived per tool call, env vars propagate from the shell that spawns it; a compromised or malicious agent owns that shell.
- This is a privilege-escalation primitive: a MEMBER agent could install an arbitrary user-scope skill/plugin globally, which is read-and-loaded by every future Claude Code session on the host.

`AGENT_WORK_DIR` is still trusted because spoofing it can only **shrink** the sandbox in practice (the agent reads the env var to learn its own dir; spoofing it to expand the sandbox does work, but that's a separate hardening problem and is not what this TRDD is solving).

### 2.3 Existing AID identity

AMP messaging already gives every agent an Ed25519 keypair via `amp-init.sh --auto`. The skill `agent-messaging` confirms:

> Send and receive cryptographically signed messages between AI agents using the Agent Messaging Protocol (AMP). [...] Ed25519 signatures.

So the trust root we want to leverage already exists. The directory-guard hook just needs a way to verify the holder of that key has the MANAGER title — without the agent being able to lie about it.

## 3. Problem

A MANAGER must run these AI Maestro CLI commands successfully (taken verbatim from `skills/ai-maestro-agents-management/references/REFERENCE.md`):

| # | Command (default scope is `user` unless noted) | Section in skill |
|---|------------------------------------------------|------------------|
| 1 | `aimaestro-agent.sh skill install <agent> <path-to-skill>` | §13 Install Skill |
| 2 | `aimaestro-agent.sh skill uninstall <agent> <skill>` | §14 Uninstall Skill |
| 3 | `aimaestro-agent.sh plugin install <agent> <plugin>` | §17 Install Plugin |
| 4 | `aimaestro-agent.sh plugin uninstall <agent> <plugin>` | §18 Uninstall Plugin |
| 5 | `aimaestro-agent.sh plugin enable / disable <agent> <plugin>` | §19 |
| 6 | `aimaestro-agent.sh plugin update / reinstall / load / validate / clean <agent> <plugin>` | §20 |
| 7 | `aimaestro-agent.sh plugin marketplace add / remove / update <agent> <source>` | §21 Manage Marketplaces |
| 8 | `claude mcp add --scope user --transport ... <name> ...` | §22 MCP Servers |
| 9 | `claude plugin install <name> --scope user` | §17 / role-plugin install |
| 10 | `claude plugin enable / disable <plugin>@<marketplace> --scope user` | §19 |

When **scope = user**, these commands write to `~/.claude/...`:

| Element | User-scope path |
|---------|-----------------|
| Skill | `~/.claude/skills/<name>/` |
| Agent | `~/.claude/agents/<name>.md` |
| Command | `~/.claude/commands/<name>.md` |
| Rule | `~/.claude/rules/<name>.md` |
| MCP server | `~/.claude.json` (top-level; CLI-only, never edited directly) |
| Plugin | `~/.claude/plugins/cache/<marketplace>/<plugin>/...` and `~/.claude/settings.json` |
| Output style | `~/.claude/output-styles/<name>.md` |
| Hook | `~/.claude/hooks/...` (via plugin, typically) |
| Settings | `~/.claude/settings.json`, `~/.claude/settings.local.json` |

Today, **all** of those writes are blocked by the directory guard for **every** title, including MANAGER. The CLI itself runs (the bash analyzer doesn't see write patterns in `bash aimaestro-agent.sh skill install ...`), but as soon as the agent or CLI script does anything visible to the hook — a `Write` tool call to `~/.claude/skills/foo/SKILL.md`, or a `cp my-skill.md ~/.claude/skills/...` — the guard refuses.

`scope=project` and `scope=local` already work for MANAGER and every other title because both land inside `<agent-work-dir>/.claude/` (rule #1 above).

## 4. Goals / non-goals

**In scope**

- Provide a tamper-proof way for the directory-guard hook to learn the calling agent's governance title.
- Define which `~/.claude/**` paths a verified MANAGER may write to.
- Keep the hook fast (≤ 3 s timeout, fires on every Write/Edit/Bash).
- Preserve cross-agent isolation: MANAGER may install user-scope elements but **must not** be able to read/write another agent's per-project state under `~/.claude/projects/<other-encoded>/` (memories, transcripts).

**Out of scope**

- Tightening `AGENT_WORK_DIR` against agent spoofing — separate hardening, separate TRDD.
- Granting AUTONOMOUS, MAINTAINER, CHIEF-OF-STAFF additional paths. They install at project/local scope, which already works (writes go to their own work dir, or are dispatched via `aimaestro-agent.sh` — whose internal writes are invisible to the hook because PreToolUse only sees Claude's top-level tool calls, not shell-spawned child processes).
- Any change to AMP transport or to `amp-*.sh` CLI semantics.
- New permissions for non-AI-Maestro hosts (multi-tenant, federation, etc.).

## 5. Threat model

| Adversary | Capability | What this TRDD must prevent |
|-----------|------------|------------------------------|
| Compromised MEMBER agent | Read/write own work dir, run shell, set env vars | Cannot trick the hook into allowing user-scope writes by spoofing title or AID identity |
| Compromised MANAGER agent | All of the above + legitimate MANAGER privs | Cannot escalate beyond user-scope element/config writes (still cannot tamper with another agent's `~/.claude/projects/<other>/`) |
| Stolen AID private key | Sign as that agent | Lifetime is bounded — server can revoke title; cached tokens have TTL ≤ a few minutes |
| AI Maestro server compromise | Issue any title | Out of scope; AI Maestro is the trust root |

Required property: **a non-MANAGER agent cannot, by any local action, cause the hook to authorize a user-scope write.** This rules out env vars, file flags, hostname checks, CWD checks, and anything else the agent can write.

## 6. Proposed designs (two options — server agent picks one)

### Option A — Per-call signed challenge

1. Server adds endpoint `POST /api/governance/title-attestation`.
2. Hook on each fire:
   - Reads the agent's AID Ed25519 keypair from disk (path TBD, likely `~/.agent-messaging/agents/<basename(AGENT_WORK_DIR)>/identity.json` or similar — please confirm).
   - Calls `GET /api/governance/nonce` → server returns a fresh 16-byte nonce.
   - Signs the nonce with the agent's private key.
   - Calls `POST /api/governance/title-attestation` with `{aid_pubkey, nonce, signature}`.
   - Server verifies (public-key + nonce-replay), returns `{title: "MANAGER" | ...}`.
3. Hook caches the result for the lifetime of the current tool call only (no persistence).

**Pros:** Always-fresh — title revocation propagates immediately.
**Cons:** Two HTTP round-trips per Write/Edit/Bash. With a 3 s hook timeout that is tight if the server is busy. Hard outage for the agent if AI Maestro is down (everything blocks until cache TTL clears).

### Option B — Pre-issued signed title token (recommended)

1. When AI Maestro assigns a title (e.g. via the existing `POST /api/governance/manager` flow referenced in the agents-management skill §"Auto-install triggers"), the server **also writes** a short-lived signed attestation file to a path the agent already controls — proposal: `~/.agent-messaging/agents/<name>/title-attestation.json`.

   Token contents (minimum):
   ```json
   {
     "aid_pubkey": "ed25519:base64...",
     "agent_name": "my-api",
     "title": "MANAGER",
     "issued_at": 1714388400,
     "expires_at": 1714389300,
     "server_signature": "ed25519:base64..."
   }
   ```
   `server_signature` covers the SHA-256 of the canonical JSON of all other fields. The server's public key is fetched once by the hook from `GET /api/governance/server-pubkey` (cached on disk; rotated only when the server rotates).

2. Server refreshes the file on a cadence ≤ TTL/2 — proposed TTL = 15 min, refresh every 5 min — and re-issues on title change. Refresh can be:
   - **Push:** `aimaestro-agent.sh` daemon writes the file from a tick task.
   - **Pull:** Agent's existing AMP refresh / Claude Code SessionStart hook calls `GET /api/governance/title-token` → server signs and returns; agent writes the file.
   - **Hybrid:** Push by default; agent can force-refresh on demand.

3. Hook on each fire:
   - Reads `~/.agent-messaging/agents/<basename(AGENT_WORK_DIR)>/title-attestation.json`.
   - Verifies the server signature against the pinned server pubkey.
   - Verifies `expires_at > now` and `agent_name == basename(AGENT_WORK_DIR)`.
   - Verifies `aid_pubkey` matches the local agent's public key (so a stolen token from agent A cannot be dropped into agent B's directory).
   - If valid AND `title == "MANAGER"`, allow user-scope writes; otherwise fall through to existing rules.

**Pros:** Zero network in the hot path. Survives ai-maestro outages within TTL. Fast (sub-millisecond verification). The same file can also be read by other future hooks/scripts that need to know the title.
**Cons:** Stale up to TTL — title revocation has up to 15 min lag. Mitigation: server can also drop a `revoked` marker file on demand, hook checks for it before honoring the token.

### Recommendation

**Option B**, with TTL = 15 min and refresh = 5 min. The hook is on the hot path (every Write/Edit/Bash), and the cost of a 15-min revocation lag is acceptable for the user-scope install use case (these are not security-critical real-time decisions; they're plugin/skill installs).

If Option B is chosen, the AI Maestro core API agent owns:

- `GET /api/governance/server-pubkey` (read-only, cacheable).
- The token-issuing/refresh job — runs server-side, writes to the agent's home directory either directly (server runs as the same user) or via a per-agent push channel.
- `POST /api/governance/title-token/refresh` — explicit-refresh endpoint, AMP-authenticated, used by `amp-*` CLI on demand.
- A `~/.agent-messaging/agents/<name>/title-revoked` flag the server drops to invalidate the token before TTL.

## 7. Directory guard plugin changes (after the API exists)

This is what `scripts/directory-guard.cjs` will do **after** AI Maestro ships the chosen design. Sketch only — implementation lives in this plugin.

Add a 6th allowlist branch in `isAllowedPath()`:

```js
// 6. MANAGER-only: user-scope element/config installs.
//    Title verified via signed attestation file (Option B).
//    NEVER from env vars or CWD.
if (isVerifiedManagerTitle(agentWorkDir) && isManagerUserScopePath(resolvedPath)) {
  return true;
}
```

`isVerifiedManagerTitle()` must:
- Read `~/.agent-messaging/agents/<basename(agentWorkDir)>/title-attestation.json`.
- Verify Ed25519 server signature (using `crypto` from Node stdlib).
- Verify expiry, agent name, pubkey binding.
- Return `false` on any verification failure (fail-closed).
- Cache the verification result in-process for the lifetime of the current Node invocation only — the hook is a fresh Node process per tool call, so no cross-call cache.

`isManagerUserScopePath()` allows (proposed final list):

```
~/.claude/skills/**
~/.claude/agents/**
~/.claude/commands/**
~/.claude/rules/**
~/.claude/output-styles/**
~/.claude/hooks/**
~/.claude/plugins/**
~/.claude/mcp_servers/**     (if AI Maestro stores MCP defs as files; otherwise N/A — see §3 row 5)
~/.claude/settings.json
~/.claude/settings.local.json
~/.claude.json               (top-level Claude Code config; CLI writes MCP entries here)
```

Explicitly **not** in the MANAGER allowlist:

- `~/.claude/projects/**` — per-agent isolation must hold. A MANAGER cannot tamper with another agent's memories/transcripts.
- `~/.claude/cache/**` (if it exists) — opaque cache, no install reason to write it.
- Anything outside `~/.claude/`.

Also: bash analyzer detects 12 write patterns (redirect, tee, cp, mv, curl -o, wget -O, python -c, node -e, install, dd, sed -i, rm, chmod, chown, ln -s) and runs `isAllowedPath()` on each target — so the same allowlist transparently covers `cp my-skill.md ~/.claude/skills/foo/SKILL.md` and equivalent shell-form writes, no separate code path needed.

## 8. Acceptance criteria

A future PR closes this TRDD only when **all** of the following hold:

### 8.1 Server (AI Maestro core)

- [ ] Endpoint(s) for the chosen design exist and are documented.
- [ ] Title-issuing flow is wired to the existing governance assignment endpoints (`POST /api/governance/manager`, `POST /api/teams/{id}/chief-of-staff`, etc.).
- [ ] Token revocation (or per-call attestation freshness, for Option A) is testable.
- [ ] Server pubkey is exposed and pinnable.

### 8.2 Hook (this plugin, `scripts/directory-guard.cjs`)

- [ ] When the calling agent has a valid MANAGER attestation, the following all succeed:

  ```bash
  # Direct shell-form writes (bash analyzer path)
  cp my-skill.md ~/.claude/skills/foo/SKILL.md
  cp my-plugin/ ~/.claude/plugins/cache/local/my-plugin/ -r

  # Tool-form writes (Write/Edit path)
  Write file_path=~/.claude/agents/my-agent.md
  Write file_path=~/.claude/commands/my-cmd.md
  Edit file_path=~/.claude/settings.json
  ```

- [ ] When the calling agent has no attestation, an expired attestation, an invalid signature, or a non-MANAGER title, **all of the above are denied** with the existing fail-closed message.
- [ ] Project-scope and local-scope writes (`<agent-dir>/.claude/...`) continue to work for **every** agent.
- [ ] `~/.claude/projects/<other-agent-encoded>/` writes are **denied** even for MANAGER.
- [ ] `~/.claude/projects/<own-encoded>/` writes (auto-memory, the bug fixed earlier this session) continue to work.
- [ ] Hook latency p99 ≤ 250 ms with valid attestation cached on disk (Option B).
- [ ] Hook never makes a network call in the steady state under Option B.

### 8.3 CLI integration

- [ ] All 10 commands listed in §3 succeed when run from a verified MANAGER agent.
- [ ] All 10 commands fail (with the directory-guard's existing deny message) when run from a non-MANAGER agent against `--scope user`.
- [ ] `--scope project` and `--scope local` variants of every command in §3 continue to succeed for any agent.

## 9. Open questions for the API agent

1. **Endpoint shape** — Confirm or correct the endpoint names proposed in §6 (`/api/governance/title-attestation`, `/api/governance/server-pubkey`, `/api/governance/title-token/refresh`). The agents-management skill already references `/api/governance` and `POST /api/governance/manager`; the new endpoints should fit the same prefix.
2. **AID key location** — What is the canonical on-disk path of an agent's Ed25519 private key today? `amp-identity.sh` reports it; the hook needs the same path. Best guess: `~/.agent-messaging/agents/<name>/identity.json`. Please confirm and document.
3. **Server signing key** — Where does the AI Maestro server's signing key live? Is it already exposed for AMP, or is this a new key?
4. **Revocation propagation** — For Option B, is a flag-file revocation acceptable, or do you want a websocket / SSE push channel? Flag-file is simpler and matches the "agent reads from local disk" pattern already used by AMP.
5. **MCP user-scope path** — `claude mcp add --scope user` writes to `~/.claude.json` (top-level), not to `~/.claude/`. The directory guard needs to allowlist that exact file for MANAGER. Confirm this is the only top-level-of-`~` file that should be MANAGER-writable.
6. **Custom role-plugin marketplace** — `~/agents/role-plugins/` is mentioned in the skill (§"Custom role-plugins"). When MANAGER auto-installs role-plugins (via `POST /api/governance/manager` triggering `claude plugin install --scope local`), does the resulting cache write land under `~/.claude/plugins/cache/...` or under `~/agents/role-plugins/`? The latter would also need to be MANAGER-writable.

## 10. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Token theft from a MANAGER's home dir | TTL ≤ 15 min; revocation flag; pubkey-binding ties token to specific AID |
| Server signing key compromise | Same blast radius as AI Maestro itself; out of scope for this TRDD |
| Hook bug allows user-scope writes for non-MANAGER | Fail-closed on every verification failure; unit tests for every negative case (already a pattern in `directory-guard.cjs`) |
| Replay of an old token after title revocation | Revocation flag + expiry + per-call mtime check |
| AI Maestro server outage | Option B keeps working until TTL; users can extend TTL temporarily by editing the token TTL config knob (server-side only) |
| Confusion with `AGENT_WORK_DIR` trust model | Document explicitly in the hook docstring that AID > env var, and that AGENT_WORK_DIR remains an env-var trust point until separately hardened |

## 11. Test plan sketch

Unit tests in this plugin (extend the inline harness already used for the auto-memory bug fix):

```js
// Negative: no attestation → user-scope write blocked
['no attestation, MANAGER user-scope path',
 '/Users/x/agents/manager-1', '/Users/x/.claude/skills/foo/SKILL.md', 'deny']

// Negative: expired
// Negative: signature invalid
// Negative: pubkey mismatch (token from agent A in agent B's dir)
// Negative: title=MEMBER attestation, MANAGER user-scope path
// Positive: valid MANAGER attestation, all 10 user-scope path types
// Positive: MANAGER attestation, project-scope path → still allowed (rule #1)
// Negative: MANAGER attestation, ~/.claude/projects/<other>/ → still denied
```

Server-side: standard governance assignment tests already exist; extend with token-issuance assertions.

End-to-end: a CI scenario boots a MANAGER agent, runs all 10 commands from §3, verifies they succeed; boots a MEMBER agent, runs the same commands, verifies they fail with the directory-guard deny message.

## 12. Cross-references

- Directory guard implementation: `ai-maestro-plugin/scripts/directory-guard.cjs`
- Hook registration: `ai-maestro-plugin/hooks/hooks.json` (PreToolUse on `Write|Edit|NotebookEdit|Bash`, 3 s timeout)
- CLI grammar source of truth: `ai-maestro-plugin/skills/ai-maestro-agents-management/references/REFERENCE.md` §12–§22
- Governance graph & titles: `ai-maestro-plugin/skills/team-governance/SKILL.md` and its references
- AMP identity / AID: `ai-maestro-plugin/skills/agent-messaging/SKILL.md`
- Auto-memory bug fix (rule #5 in §2.1): committed earlier in this session — see `git log -- scripts/directory-guard.cjs` for the patch
