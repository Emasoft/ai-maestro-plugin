---
trdd-id: 90c8ad35-f7c9-4576-8ad4-2b72a82d047a
title: Decouple the core plugin from the ai-maestro server API — repoint /api/* to the frozen CLI layer
column: blocked
created: 2026-06-17T00:28:54+0200
updated: 2026-06-17T00:36:58+0200
pre-block-column: dev
current-owner: ai-maestro-plugin
assignee: ai-maestro-plugin
priority: 1
severity: HIGH
effort: M
task-type: refactor
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
must-pass-tests-before-merge: true
review-requirements: [human-review]
impacts: [public-api, ci-pipeline]
implementation-commits: []
external-refs: ["github.com/Emasoft/ai-maestro-plugin/issues/11", "github.com/Emasoft/ai-maestro/issues/36", "github.com/Emasoft/ai-maestro-assistant-manager-agent/issues/16", "github.com/Emasoft/ai-maestro-chief-of-staff/issues/20"]
---

# TRDD-90c8ad35 — Decouple core plugin from server `/api/*` → frozen CLI layer

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-17

MANAGER directive **core#11** (cites USER 2026-06-15, ABSOLUTE/exception-free,
PRE-AUTHORIZED — "execute, don't wait"). No ai-maestro plugin may call the
server `/api/*` directly. Each API-touching **script AND hook** splits:
api-part → a CLI verb that lands in the `ai-maestro` project (NOT mine to
build — ai-maestro#36); non-api part stays here. This plugin calls ONLY the
frozen CLI. **GitHub API (`gh`, `api.github.com`) is OUT OF SCOPE — keep it.**

### NEXT ACTION (BLOCKED on ai-maestro#36 deploy — external)
All committable code work is DONE (Phases 1-3 below). The TRDD is now **blocked**
on **ai-maestro#36** landing the frozen verbs (`aimaestro-agent.sh resolve --cwd`,
the session-activity + send-command verbs, `aid-governance`/`aid-whoami`). When #36
deploys: (1) flip each `DECOUPLE-BLOCKED ai-maestro#36` tag → the real CLI call,
(2) re-verify `grep -rn '/api/'` shows zero real call sites, (3) publish (MANAGER
verify-acks). Also pending: MANAGER ruling on whether skill-doc `curl /api/…`
examples are in-scope (asked on #11). `blocked-by` is the EXTERNAL issue
ai-maestro#36 (not a local TRDD), so the frontmatter list stays empty by
construction; restore to `pre-block-column: dev` when #36 deploys.

### DONE (2026-06-17, commit-not-publish)
- **Phase 1** ✅ `prrd_lib.py` `/api/governance` (caller_is_manager) tagged
  DECOUPLE-BLOCKED (aid-* verbs MISSING). py_compile clean. commit.
- **Phase 2** ✅ `ai-maestro-hook.cjs` — all 3 functions tagged DECOUPLE-BLOCKED
  (resolve-by-cwd + session-activity + send-command verbs all absent; comment-only
  change → runtime byte-identical; `node --check` + Stop smoke-test pass). commit.
- **Phase 3** ✅ verified: the ONLY executable `/api/` (ai-maestro server) call
  sites are those 2 files (6 in the hook + 1 in prrd_lib), ALL DECOUPLE-BLOCKED-
  tagged + functional. Zero untagged real call sites. GitHub API untouched.

### Load-bearing facts / gotchas
- **commit-not-publish** until ai-maestro#36 deploys the missing verbs — the
  verbs must EXIST before a plugin that calls them is published. MANAGER
  verify-acks on publish.
- **FROZEN-interface invariant (assistant-manager#16, from the ai-maestro
  scripts owner):** every installed CLI script's interface (name/args/output)
  is immutable; plugins must NEVER patch installed scripts — script-side
  changes route through the `ai-maestro` repo. I edit MY files to *call* the
  CLI; I do not touch `~/.local/bin/*`.
- **CLI availability verified 2026-06-17 (this machine):** `aimaestro-agent.sh`,
  `amp-inbox`, `amp-send`, `amp-read`, `amp-reply` EXIST. `aid-whoami`,
  `aid-governance`, `aimaestro-teams`, `aimaestro-governance` MISSING (land via
  #36 → DECOUPLE-BLOCKED meanwhile).
- Server is currently HTTP 401 / down, so the hook's existing `/api/` fetches
  are already no-ops right now → the repoint is behavior-preserving in this
  state and only changes behavior when the server is up (where matching the
  frozen CLI interface is what matters).
- `ai-maestro-hook.cjs` is LOAD-BEARING — it runs on every Notification / Stop /
  SessionStart / Subagent* / Compact event fleet-wide (session tracking + AMP
  inbox notification). A broken edit degrades the whole fleet's session
  tracking. Re-verify it parses + runs (node --check) after every edit.
- `# DECOUPLE-BLOCKED ai-maestro#36` is the greppable tag for a call left
  functional because its frozen verb doesn't exist yet; it flips to the CLI
  once the verb lands.

### SUPERSEDED — do NOT carry forward
- (none yet)

### Durable artifacts to read before acting
- core#11 (the directive), COS#20 (worked example + repoint-queue pattern),
  assistant-manager#16 (FROZEN invariant + rollout status), ai-maestro#36
  (the frozen-verb build list).

## Real `/api/*` call sites (discovery 2026-06-17, ai-maestro server only; GitHub excluded)

| File:line | Call | Target CLI verb | Status |
|---|---|---|---|
| `scripts/ai-maestro-hook.cjs:63,155,197` | `GET /api/agents` | `aimaestro-agent.sh list` | verb EXISTS → repoint (Phase 2) |
| `scripts/ai-maestro-hook.cjs:222` | `GET /api/messages?...box=inbox&status=unread` | `amp-inbox` | verb EXISTS → repoint (Phase 2) |
| `scripts/ai-maestro-hook.cjs:84` | `POST /api/sessions/activity/update` | `aimaestro-agent.sh session …`? | verify source; else DECOUPLE-BLOCKED |
| `scripts/ai-maestro-hook.cjs:171` | `POST /api/sessions/{name}/command` | `aimaestro-agent.sh session …`? | verify source; else DECOUPLE-BLOCKED |
| `scripts/prrd-trdd/prrd_lib.py:608` | `{api}/api/governance` (caller_is_manager) | `aid-governance`/`aid-whoami` | verb MISSING → DECOUPLE-BLOCKED #36 |

**Docs/specs (excluded from the real-call-site end-state, per #11):** TRDD bodies
under `design/`, and the instructional `curl .../api/...` examples in skill docs
(`skills/team-kanban/`, `team-governance/`, `memory-search/`, `graph-query/`,
`mcp-discovery/`, `network-security/`, `ama-trdd-transition/`). OPEN QUESTION for
the MANAGER: do skill-doc curl examples that *teach the agent to hit the server*
count as "real call sites" to repoint to CLI verbs, or are they "docs" and
excluded? The directive says docs excluded; but "the plugin must not embed
endpoint knowledge" suggests the SKILL.md guidance should eventually teach the
CLI verb. Defer doc-repoint to a follow-up pending that ruling — do NOT block the
code-repoint on it.

## Plan (phased; commit-not-publish each)

1. **STEP 0** — this TRDD (done). Reply to #11 with scope + CLI-availability +
   the skill-doc open question.
2. **Phase 1 (safe, do first)** — `prrd_lib.py:608`: add `# DECOUPLE-BLOCKED
   ai-maestro#36` immediately above the `/api/governance` call (target CLIs
   missing). Leave the call functional. `node`/`py` syntax check. Commit.
3. **Phase 2 (hook repoint)** — read `aimaestro-agent.sh` + `amp-inbox` source
   for frozen interfaces. Repoint the 3 `/api/agents` reads + the `/api/messages`
   read; for the 2 `/api/sessions/*` writes, repoint if a frozen
   `aimaestro-agent.sh session` verb covers them, else tag DECOUPLE-BLOCKED.
   `node --check scripts/ai-maestro-hook.cjs` after each edit; smoke-run the
   hook with a fixture event. Commit.
4. **Phase 3 (verify)** — `grep -rn '/api/'` shows only docs + DECOUPLE-BLOCKED
   tags (zero untagged real call sites). Update this STATE block. Reply #11.
5. **Hold at commit-not-publish** until ai-maestro#36 lands the missing verbs;
   then flip the DECOUPLE-BLOCKED tags to the CLI and publish (MANAGER verify-ack).

## Acceptance criteria
- Zero UNTAGGED real `/api/*` (ai-maestro server) call sites in executable code.
- Every still-functional server call carries `# DECOUPLE-BLOCKED ai-maestro#36`.
- No installed CLI script (`~/.local/bin/*`) was edited (FROZEN invariant).
- GitHub API calls untouched.
- `ai-maestro-hook.cjs` still `node --check`-clean and runs on a fixture event.
- commit-not-publish observed until #36 deploy.

## Approval log
- 2026-06-17T00:28:54+0200 — Authored under MANAGER core#11 standing
  pre-authorization (cites USER 2026-06-15, ABSOLUTE + "execute, don't wait").
  Tier: directive is Tier-2/3 by nature but PRE-AUTHORIZED + commit-not-publish
  (no outward-facing act until the gated publish, which the MANAGER verify-acks).
  Authored directly in design/tasks/ per that pre-authorization.
