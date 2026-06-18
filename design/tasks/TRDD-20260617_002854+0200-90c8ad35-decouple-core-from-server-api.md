---
trdd-id: 90c8ad35-f7c9-4576-8ad4-2b72a82d047a
title: Decouple the core plugin from the ai-maestro server API — repoint /api/* to the frozen CLI layer
column: publish
created: 2026-06-17T00:28:54+0200
updated: 2026-06-18T19:04:44+0200
pre-block-column: null
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
implementation-commits: [a7f1c7a, b6ff8d7, 9217a5d, 56bc667, b615bbe, 7db8c1f, 1dd5410, 4e8e31e, 088f860, 59ba682, bab2fed]
external-refs: ["github.com/Emasoft/ai-maestro-plugin/issues/11", "github.com/Emasoft/ai-maestro/issues/36", "github.com/Emasoft/ai-maestro-assistant-manager-agent/issues/16", "github.com/Emasoft/ai-maestro-chief-of-staff/issues/20"]
---

# TRDD-90c8ad35 — Decouple core plugin from server `/api/*` → frozen CLI layer

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-18

MANAGER directive **core#11** (cites USER 2026-06-15, ABSOLUTE/exception-free,
PRE-AUTHORIZED — "execute, don't wait"). No ai-maestro plugin may call the
server `/api/*` directly. Each API-touching **script AND hook** splits:
api-part → a CLI verb that lands in the `ai-maestro` project (NOT mine to
build — ai-maestro#36); non-api part stays here. This plugin calls ONLY the
frozen CLI. **GitHub API (`gh`, `api.github.com`) is OUT OF SCOPE — keep it.**

### ✅ DECOUPLE COMPLETE 2026-06-18 04:36 — code + docs flipped, audit CLEAN — ONLY the CPV publish remains (gated on MANAGER #11)
Doc-wave DONE across **10 files** (8 planned + 2 **audit-found**:
`ai-maestro-agents-management/references/REFERENCE.md`, `network-security/SKILL.md`).
Full `grep -rn '/api/'` audit **CLEAN** — zero runnable `/api/*` server calls in plugin
skill/code source. Remaining `/api/` mentions are ALL inert: DECOUPLE-BLOCKED residual
comments, CLI↔endpoint mapping tables/prose (agents-management), the `/api/v1/route` AMP
wire-protocol spec, the GOVERNANCE-RULES anti-pattern row (a mirror — not mine to edit),
and `design/` docs. **22 commits ahead of origin (commit-not-publish).**
**NEXT = MANAGER #11 reply → publish via the CPV plugin-fixer agent → MANAGER verify-ack.**
Residuals staying DECOUPLE-BLOCKED (re-targeted to an ai-maestro follow-up build):
assign/remove-COS-on-existing-team, change-team-type, Groups, non-status kanban task
edits (priority/blockedBy/prUrl), team `stats`, subconscious status/index-delta,
assign-MANAGER/COS-title.

### (superseded) NEXT ACTION (deploy LANDED 2026-06-18 → code FLIPPED+committed → awaiting MANAGER #11 reply)
**ai-maestro#36 DEPLOYED** on this host: `~/.local/bin/aimaestro-hook.sh` +
`aimaestro-governance.sh` (mtime Jun 18 02:50, SHAs match repo per #36 comments).
**Both executable `/api/*` sites FLIPPED + committed `b6ff8d7`** (NOT pushed —
publish pending MANAGER verify-ack):
- `ai-maestro-hook.cjs` → `aimaestro-hook.sh activity|notify|check-messages --cwd`
  (resolves cwd→agent + API internally; prompt-injection-safe marker kept local).
  `node --check` ✓ · zero `fetch`/`:23000`/`/api/`.
- `prrd_lib.py caller_is_manager` → `aimaestro-governance.sh whoami`
  (wraps GET /api/governance; same title-scan). `py_compile`+`ruff` ✓.

**REPORTED to MANAGER on #11 (comment 12, 2026-06-18).** AWAITING reply
(monitor `#11c` → 13) on TWO questions:
1. **Publish scope** — code-only now (doc-wave follow-up) vs hold for full doc-wave.
2. **Fleet doc-pattern** for the teams ref-docs (COS is repointing "14 teams ref-docs"
   — match their shape).

**Doc-wave (the 9 banners) — PENDING MANAGER doc-pattern answer, do NOT touch yet:**
- Repointable (verbs present): team-governance (`/api/governance`→`whoami`,
  teams→`aimaestro-teams.sh`), team-kanban (→`aimaestro-teams.sh
  list/show/create/update/delete/add-agent/...`), mcp-discovery (`mcp-discover.sh`).
- STAY DECOUPLE-BLOCKED (no deployed verb → re-target to follow-up build):
  memory-search `subconscious/status`+`index-delta`; AND the team-governance
  `POST /api/teams/{id}/chief-of-staff` example (no assign-COS verb in
  `aimaestro-teams.sh` — same gov-password residual class COS flagged on #36).

**Verify-ack flag:** deployed `aimaestro-hook.sh notify` posts `addNewline:false`
vs the old hook's `:true` — flagged on #11, NOT worked around (frozen CLI owns it).

**THEN (on MANAGER reply):** do the doc repoints per the pattern → `grep -rn '/api/'`
audit (only out-of-scope GitHub + the re-targeted residuals + `design/` docs remain)
→ **publish via the CPV plugin-fixer agent (never hand-publish)** → MANAGER verify-ack.
Restore complete: `column: dev`, `pre-block-column: null` (the external #36 blocker cleared).

### VERB MAP + DOC-PATTERN — reconnaissance COMPLETE 2026-06-18 (execute on MANAGER go)
**Fleet doc-pattern (matched from COS published repoint `Emasoft/ai-maestro-chief-of-staff@c02cdf5c`, MANAGER-confirmed #20 recipe; COS published base-bulk promptly as v2.18.2 then residual passes v2.18.3/4):**
convert each `curl /api/X` (in code fences AND prose/checklists) → the inline frozen-CLI
invocation with full flags; for a no-verb endpoint replace with a
`<!-- DECOUPLE-BLOCKED ai-maestro#36: <why-no-verb>. Pending a follow-up verb. -->`
comment + a prose fallback ("Until then: use the <skill>…").

**Verified verb map (deployed `~/.local/bin`, flags read from source):**
- `GET /api/governance` → `aimaestro-governance.sh whoami`
- `GET /api/teams` → `aimaestro-teams.sh list` · `GET /api/teams/{id}` → `aimaestro-teams.sh show <id>`
- `POST /api/teams` → `aimaestro-teams.sh create --name <N> [--description D] [--agents JSON] [--type T] [--cos C] [--password P] [--gh-owner O --gh-repo R]`
- `PUT /api/teams/{id}` → `aimaestro-teams.sh update <id> [--name|--description|--agents|--orchestrator|--gh-owner|--gh-repo]`
- `DELETE /api/teams/{id}` → `aimaestro-teams.sh delete <id> [--password P] [--delete-agents]`
- add/remove team agent → `aimaestro-teams.sh add-agent|remove-agent <id> <agent> [--password P]`
- `GET /api/agents/{id}` → `aimaestro-agent.sh show <id>` (pipe to `jq -r '.agent.name'`)
- `POST/GET /api/settings/mcp-discover` → `mcp-discover.sh` (deployed)
- **NO VERB → stay DECOUPLE-BLOCKED + re-target:** assign-COS-to-EXISTING-team
  (`POST /api/teams/{id}/chief-of-staff`; `update` has no `--cos` — note create DOES via `--cos`),
  `/api/groups` (no groups verb), memory-search `subconscious/status`+`index-delta`.

**Files to touch (6 repoint + 2 re-target):** team-governance SKILL.md + references/REFERENCE.md;
team-kanban SKILL.md + references/api-reference.md + references/github-sync.md;
mcp-discovery references/REFERENCE.md (repoint). memory-search SKILL.md + references/REFERENCE.md
(re-target subconscious only). GitHub-sync (`kanban-sync.py`,`gh`) stays OUT OF SCOPE.

**GATE:** holding the bulk doc rewrite + the CPV publish for MANAGER's #11 reply
(comment 12 asked: publish-scope + pattern-confirm). Pattern is self-answered via COS
above, so on ANY MANAGER go this executes immediately. Monitor `#11c` → 13.

**Hook flip target — CORRECTED by MANAGER (#11, comment 4):** my session-verb
"missing" finding was the **stale-deployed-copy trap** — I read deployed
`~/.local/bin/agent-session.sh` (353 lines, only `tmux attach`); SOURCE is 495
lines and already has `cmd_session_command`, `cmd_session_activity_update`, and
`resolve --cwd`. So they're **deployed-stale, NOT missing** (no new verbs to
build; #36 refreshes the modules). Better still, the ai-maestro Claude already
built **`aimaestro-hook.sh`** (source-only today, added to #36's deploy list)
whose subcommands map 1:1 to my hook's 3 functions and resolve cwd→agent
INTERNALLY:
- `aimaestro-hook.sh activity --cwd <dir> [--status …]` ← `broadcastStatusUpdate`
- `aimaestro-hook.sh notify --cwd <dir> --message <text>` ← `sendMessageNotification`
- `aimaestro-hook.sh check-messages --cwd <dir> [--json]` ← `checkUnreadMessages`
**FLIP PLAN (when #36 deploys `aimaestro-hook.sh`):** `ai-maestro-hook.cjs` becomes
a thin stdin-parser that shells out to those 3 subcommands — the 3 `GET /api/agents`
cwd-resolutions collapse into the wrapper; zero `fetch`, zero `:23000`, zero `/api/`.
(See LOCAL memory `deployed-cli-copy-is-stale-vs-source`.) `prrd_lib.py` →
`aid-governance` stays a genuine #36 verb.

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
- 2026-06-17T00:52+0200 — **Phase 4 DONE** (commit-not-publish). 9 skill docs
  tagged with one DECOUPLE banner each (team-kanban ×3, team-governance ×2,
  memory-search ×2, mcp-discovery, ai-maestro-agents-management); 0 inline
  repoints (no target verb installed → all #36-blocked); 8 files left EXEMPT
  (graph-query/docs-search `/api/hosts/identity` health-probes,
  network-security `/api/sessions` connectivity-test + `/api/v1/route` AMP
  protocol doc, GOVERNANCE-RULES.md policy text, cos-delegation presence
  architecture-description). Additions-only diff (19+/1-, the 1 a comment
  enhancement). Report: reports/decouple-doc-wave/20260617_005205+0200-phase4.md.
  TRDD stays blocked on ai-maestro#36 for the tag-to-CLI flip + publish.
- 2026-06-18T03:00+0200 — ai-maestro#36 DEPLOY LANDED. Code FLIPPED (b6ff8d7) + full
  doc-wave (10 files, incl. 2 audit-found: agents-management, network-security) ->
  `grep -rn '/api/'` audit CLEAN (zero runnable server calls). Reported complete to
  MANAGER on #11 (comment 13); held for publish-ack (non-exempt release).
- 2026-06-18T19:01+0200 — **MANAGER GRANTED publish go-ahead** (#11 comment 14, the
  Claude developing ai-maestro-assistant-manager-agent): "Publish the unblocked bulk;
  keep residual ops DECOUPLE-BLOCKED ai-maestro#36-tagged - they clear when the
  follow-up verbs land." Same bar maintainer v1.6.0 + architect v2.8.1 shipped under.
  Column dev -> publish. Publishing via the **CPV plugin-fixer agent** (publish.py
  canonical pipeline; never hand-published). Residuals stay tagged.
