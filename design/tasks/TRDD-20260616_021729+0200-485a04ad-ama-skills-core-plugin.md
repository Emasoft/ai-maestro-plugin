---
trdd-id: 485a04ad-e2df-4393-81d3-70e9cbe0686b
title: Build the granular governance-enforcing ama-* pillar skills in the core plugin (Build #8 Phase A)
column: published
created: 2026-06-16T02:17:29+0200
updated: 2026-06-16T05:43:02+0200
current-owner: general-purpose
assignee: general-purpose
priority: 1
severity: HIGH
effort: L
task-type: infra
parent-trdd: TRDD-f5883dcc
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: publish
target-branch: main
review-requirements: [human-review]
impacts: [public-api]
implementation-commits: [306c7e8]
published-version: 2.7.9
published-at: 2026-06-16T02:44:14+0200
external-refs: ["github.com/Emasoft/ai-maestro-plugin"]
---

# TRDD-485a04ad — Granular governance-enforcing `ama-*` pillar skills (Build #8 Phase A)

## ⏵ STATE — READ THIS FIRST ON RESUME — 2026-06-16

This is **Phase A** of Build #8 (parent design TRDD-f5883dcc). **Phase B**
(the 4 governance rules bundled in `rules/` + SessionStart auto-install) is
ALREADY committed at HEAD c409431. Phase A is built ON TOP; one publish carries
both as `v2.7.9`.

### NEXT ACTION
Build the `ama-*` skills, retire `prrd-trdd-kanban`, CPV `--strict` clean,
commit (stage by name), `publish.py --patch` → v2.7.9, `gh run watch` Release.

### Load-bearing facts / gotchas
- Scripts live at `scripts/prrd-trdd/` and are resolved at runtime via
  `scripts/prrd-trdd/resolve_pillar_scripts.sh` (works from any plugin).
- The HARD enforcement backstop is `prrd_lib.caller_is_manager()` (reads
  `$AID_AUTH` against the AI Maestro server, or `AMAMA_PRRD_TRUST=1` / `--user`).
  It gates `prrd-edit.py` (direct add/revise/delete; promote/demote USER-only)
  and `amama_proposal_approvals.py` (approve/refuse/archive).
- There is **NO `caller_role()`** — non-MANAGER role distinctions (ORCH vs ARCH
  vs MEMBER, read-only-kanban roles, etc.) are NOT script-enforced. Per the
  decided enforcement model, those are enforced by **skill-instruction**: each
  skill states its matrix row and tells the agent to self-check role × op-tier
  and ROUTE/refuse. A `caller_role()` follow-up is noted below (do NOT block).
- The 4 governance rules now live in `rules/` (Phase B). References must POINT
  there, never re-duplicate the rule text.
- `reports/` + `reports_dev/` already gitignored (`.gitignore` lines 33-34).

### SUPERSEDED — do NOT carry forward
- The per-plugin `prrd-trdd-kanban` skill is being RETIRED in this TRDD; its 10
  `references/*.md` are folded into the `ama-*` skills as shared references.

## Plan (Phase A)

1. **STEP 0** — this TRDD (done).
2. **STEP 1** — create ~10 granular `ama-*` skills under `skills/`:
   - Script-wrapping: `ama-prrd-get` (get-prrd.py), `ama-prrd-find` (findprrd.py),
     `ama-prrd-edit` (prrd-edit.py — SILVER-gated), `ama-prrd-propose`
     (prrd-edit.py propose), `ama-kanban-render` (kanban.py — read),
     `ama-proposal-approvals` (amama_proposal_approvals.py — MANAGER/COS-gated),
     `ama-trdd-find` (findtrdd.py).
   - Guidance: `ama-trdd-write`, `ama-trdd-update`, `ama-trdd-transition`
     (column moves enforcing the matrix).
3. **STEP 2** — retire `skills/prrd-trdd-kanban/`; fold its 10 references into
   the `ama-*` skills as shared references (one source; the 4 governance rules
   point to `rules/`, not re-duplicated).
4. **STEP 3** — CPV `--strict` clean; commit (stage by name; `Agent:` trailer);
   `publish.py --patch` → v2.7.9; `gh run watch` Release.

## Enforcement model (DECIDED — do NOT redesign)

Scripts are the HARD backstop (`caller_is_manager()` via `$AID_AUTH`). Each
skill: (a) states its matrix row, (b) instructs the agent to self-check
role × op-tier and ROUTE/refuse (e.g. `ama-prrd-edit`: non-MANAGER on SILVER →
route to `ama-prrd-propose`; `ama-kanban-render` is read-only by construction;
`ama-proposal-approvals` is MANAGER/COS only), (c) invokes the script.
`disallowed-tools` drops write tools where a skill should be read-only.

## Governance-permission matrix (from the four rules)

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| read kanban/TRDD/PRRD | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| author proto-TRDD | ✅ | ✅ | ✅ | ✅ | ✅ | via COS | ✅ | ✅ |
| TRDD column transition | ✅ | dispatch | design | release | relay | signal-only | ✅ | ✅ |
| edit SILVER PRRD | ✅ | propose | propose | propose | relay | propose-via-COS | propose | propose |
| edit GOLDEN PRRD | ❌ USER-only | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| approve TRDD (tier) | T2/T3 | T1 | T0 | T0 | T1 | T0 | →USER | →MGR |

## Follow-up noted (do NOT block this build)

- `caller_role()` in `prrd_lib.py` — a future server-backed hard check that
  resolves the caller's full governance role (not just MANAGER yes/no). Until it
  exists, non-MANAGER role distinctions are enforced by skill-instruction only.

## Acceptance criteria
- ~10 `ama-*` skills in the core plugin; each states its matrix row + routes/refuses.
- `prrd-trdd-kanban` retired; its references folded (no duplicated rule text;
  governance rules point to `rules/`).
- CPV `--strict` clean. Published v2.7.9 (carries Phase B).

## Approval log

- 2026-06-16T05:43:02+0200 — `column: dev → published` (bookkeeping). All
  acceptance criteria met and the work shipped in **v2.7.9** (8 assets, Release
  green, published 2026-06-16T02:44:14+0200, impl commit `306c7e8`). This records
  the already-executed, user-authorized publish — NOT a newly-initiated release —
  so the kanban reflects shipped reality. The column had been left stale at `dev`
  after the publish; the janitor `[trdd-reminder]` surfaced it. Parent
  TRDD-f5883dcc (#8) stays open for its gated follow-up (rule-installer
  overwrite-on-bump, awaiting MANAGER's rule-ownership confirmation).
