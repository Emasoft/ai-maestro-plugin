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
Code (Phases 1-3) DONE. **Phase 4 (doc wave) is now ACTIVE** per the MANAGER's
ruling (#11, 2026-06-16): executable skill-`curl /api/…` IS in scope; inert refs
exempt. Do Phase 4 now (commit-not-publish), then HOLD the whole TRDD blocked on
**ai-maestro#36** for the tag→CLI flip + publish. When #36 deploys: flip every
`DECOUPLE-BLOCKED ai-maestro#36` tag → the real CLI call, re-verify grep, publish
(MANAGER verify-acks). `blocked-by` is the EXTERNAL ai-maestro#36 (not a local
TRDD) → frontmatter list stays empty; restore to `pre-block-column: dev` on deploy.

**Session-verb request SENT (#11):** verified `agent-session.sh cmd_session` only
`tmux attach`es → asked MANAGER to add `session activity-update` + `session command`
to the #36 build list (+ confirmed the hook also needs `resolve --cwd`, already on
#36). Hook flips once #36 ships resolve--cwd + those 2 session verbs.

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

## Phase 4 — skill-doc wave (MANAGER ruling #11, 2026-06-16; the tracked tail)

Line: **executable** agent-facing `curl /api/…` in a SKILL = in scope (the agent
RUNS it at skill-load → plugin calls the API). **Inert** refs exempt: response-shape
samples, "is the server up" health-probes the agent isn't told to act on, changelog
mentions, test fixtures. Judge each by "is the agent meant to RUN this against the
server?".

Per-skill (verb-availability decides repoint-now vs tag-blocked):
- `/api/agents` → `aimaestro-agent.sh list` (NOW) · `/api/messages` → `amp-inbox` (NOW).
- `team-kanban` → `aimaestro-teams` (#36 → tag) · `team-governance` → `aimaestro-governance`
  (#36 → tag) · `ama-trdd-transition` presence ref → its #36 verb (tag).
- `graph-query`/`memory-search` health-probe `curl …/identity|/subconscious/status`:
  classify (probe vs instruction) — likely EXEMPT health-checks; `mcp-discovery`
  `POST /api/settings/mcp-discover` → assess for a verb or tag.
- `network-security` `/api/v1/route` = protocol DOC describing AMP transport, not an
  instruction → EXEMPT.

Skill docs are NOT executable code, so a broken edit can't crash anything; still
commit-not-publish. Code wave already done — this does not block it.

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
- 2026-06-17T00:37+0200 — Phases 1-3 (code) committed; replied #11 with the
  session-verb finding (cmd_session only tmux-attaches → requested `session
  activity-update` + `session command` added to #36). Column → blocked (ai-maestro#36).
- 2026-06-17T00:40+0200 — MANAGER ruled (#11): executable skill-`curl` IN SCOPE,
  inert EXEMPT; code-first, docs as tracked tail. Phase 4 (doc wave) added + made
  active. Still commit-not-publish; MANAGER verify-acks at the gated publish.
