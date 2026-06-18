---
trdd-id: fabb5c42-c17a-4deb-b09a-6102765f1c4d
title: Propagate governance R26-R40 into core-plugin persona + skills + docs + SCEN
column: dev
created: 2026-06-18T20:52:01+0200
updated: 2026-06-18T21:24:09+0200
current-owner: ai-maestro-plugin
assignee: ai-maestro-plugin
priority: 2
severity: MEDIUM
effort: L
task-type: feature
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
test-requirements: [lint]
impacts: []
implementation-commits: []
external-refs: ["github.com/Emasoft/ai-maestro-plugin/issues/12", "github.com/Emasoft/ai-maestro/issues/37"]
---

# TRDD-fabb5c42 — Propagate governance R26-R40 into the core plugin (persona + skills + docs + SCEN)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-18

MANAGER directive (Emasoft/ai-maestro-plugin **#12**, opened 2026-06-18 by the
Claude developing ai-maestro-assistant-manager-agent). Fleet governance landed:
`GOVERNANCE-RULES.md v4.0.1`, rules **R26-R40** (USER's refined-v2 wording + the
propagation task on **Emasoft/ai-maestro#37**). Every role-plugin persona must
internalize R26-R40. **Reference implementation = AMAMA (MANAGER plugin)
ai-maestro-assistant-manager-agent v2.12.0** (CPV `--strict` clean, tests 15/15:
reconciled persona + skills + docs + `tests/scenarios/governance-scenarios.md`).
Mirror that here. **Execute on next wake; reply on #37 or #12 when done.**

THIS plugin's emphasis (it is the CORE / substrate): its **self-install skills are
the R27 ENFORCEMENT POINT** — agents install ONLY through these skills (which call
the server + CPV-scan). The whole fleet's R26-R40 compliance rests on this plugin.

### NEXT ACTION (start here)
1. **Read canonical rules** — `docs/GOVERNANCE-RULES.md` on the `governance-rules`
   branch of Emasoft/ai-maestro (R26-R40 full text) + ai-maestro#37 (per-plugin
   matrix + refined-v2 wording). Fetch via `gh api` (don't trust the possibly-stale
   bundled mirror at skills/team-governance/references/GOVERNANCE-RULES.md).
2. **Study the AMAMA v2.12.0 reference** — how it reconciled persona + skills + docs
   + governance-scenarios.md (follow-the-reference, match the shape).
3. **Inventory OLD-model statements to REVERSE** in this plugin's persona + skills
   + docs (grep candidates): "COS assignment is USER-only", "MANAGER recommends COS"
   / "needsChiefOfStaff", any agent using a sudo / governance `--password`, team
   create/delete needing user approval, COS-assignment semantics.
4. **Edit persona + skills + docs** to internalize R26-R40 behaviors. Per #12, focus:
   - **R27** self-install via the core plugin's skills ONLY (this plugin is the gate).
   - **R28** 3-check authz: skills carry the AID → server derives TITLE → checks the
     portfolio token. NEVER assert your own title.
   - **R32** agents NEVER sudo: AID + portfolio token; a deployed-CLI `--password` is
     a USER/UI residual you SURFACE to the MAESTRO, never perform.
   - **R29-R31** MANAGER creates/deletes teams + auto-COS + 5 base members +
     AUTONOMOUS/MAINTAINER (NO user approval); COS mandate + MEMBER-titled-on-the-
     member-plugin; freeze incomplete teams.
   - **R38/R39** the ASSISTANT title + role plugin; user↔agent messaging matrix.
   - **R26** immutable identity; **R33/R34** signed-ledger SoT; **R35/R36/R37/R40**
     foreign-host MAESTRO approval / obey active MAESTRO / MAESTRO-DELEGATE handoff.
   - **REVERSE** every place the persona states the OLD model (the #12 examples).
5. **Add `tests/scenarios/governance-scenarios.md`** (mirror AMAMA's).
6. **CPV `--strict` clean** (devitalize/remove FPs — never suppress; report FPs to CPV).
7. **Publish via the canonical pipeline (CPV agent)** — the #12 directive authorizes
   "publish via your canonical pipeline." Residual/blocked items stay tagged.
8. **Reply on #37 (or #12)** when shipped; this is the MANAGER #37 propagation task.

### Load-bearing facts / gotchas
- Canonical wording is on the ai-maestro `governance-rules` branch — the bundled
  `team-governance/references/GOVERNANCE-RULES.md` mirror may be an OLD version; the
  decouple work (TRDD-90c8ad35) treated that mirror as not-mine-to-edit (it mirrors
  the server repo). Confirm whether THIS task wants the bundled mirror updated too
  (it's a mirror of ai-maestro's canonical — likely synced separately).
- Publish is non-exempt, but #12 explicitly instructs to publish — treat as
  authorized (like #11's publish-ack); still report completion on #37/#12.
- Shell gotcha: `UID` is a reserved zsh/bash variable — use `TID` etc. for UUIDs.

### Canonical R26-R40 — READ 2026-06-18 (GOVERNANCE-RULES.md v4.0.1, ai-maestro `governance-rules` branch, doc lines 1211-1384). Implications for THIS plugin:
- **R26** identity immutable — persona: a title/role/name/AID is CONFERRED, never
  self-assigned; only USER(MAESTRO)/MANAGER/own-team-COS may change them (COS scoped
  to own team).
- **R27** self-install ONLY via the core-plugin skills, after MANAGER (no team) /
  own-COS (in team) approval, and the server CPV-scans every extension before
  install. ← THIS plugin's self-install skills are that gate; never the client CLI directly.
- **R28** every agent op authenticates with AID; the SERVER does the 3-check
  (AID → TITLE → portfolio approval/mandate token) and never trusts a client-supplied
  id/title/scope. Skills carry the AID; they must NOT assert their own title.
- **R29** MANAGER creates/deletes teams with NO user approval (auto-COS + 5 base
  members); may mandate the COS to add extra MEMBERs. **R30** COS needs a MANAGER
  mandate to create agents (team-creation mandate covers the 5-base + extra MEMBERs;
  5-base invariant, MEMBER-role only). **R31** a team missing any of the 5 base is
  FROZEN (only COS active; others hibernated) until complete.
  → **REVERSE** any "COS assignment is USER-only" / "MANAGER recommends COS" /
  team-create-needs-user-approval text.
- **R32** (SUPERSEDES X-Sudo-Token) agents NEVER face a sudo gate — AID+title+token
  IS the authorization; a sudo password is requested ONLY of the USER, ONLY via the
  UI. → drop any agent-facing sudo/`X-Sudo-Token` instruction; a deployed-CLI
  `--password` (e.g. governance password) is a USER/UI residual the agent SURFACES to
  the MAESTRO, never performs.
- **R33/R34** signed ledger = ultimate identity SoT (AID with no ledger history =
  untrusted/refused; imported-agent AID re-issue needs USER sudo via UI).
- **R35** foreign agent/user host needs this host's MAESTRO approval (UI+sudo, ledger-
  recorded). **R36** users have AIDs; exactly one MAESTRO per host. **R37** MANAGER
  obeys only the MAESTRO; single MAESTRO-DELEGATE (suspends MAESTRO while active).
- **R38** non-MAESTRO users: only MAESTRO creates/changes agents+teams; a user may
  message only their own ASSISTANT + own-team COS + MANAGER; subordinate to MANAGER+COS.
- **R39** users have NO terminal/client → an auto-created **ASSISTANT** agent running
  `ai-maestro-assistant-role-agent` (MANAGER-planning + AUTONOMOUS-programming, no
  agent/team-creation), no team, bound to the user (cascades on user delete), invisible
  to other agents, inherits the user's kanban tasks+permissions. **R40** foreign users
  need MAESTRO approval for every agent/team creation.
- **Permission matrix (doc 1367-1384):** R26-R40 govern where it differs; "Assign COS /
  Create/Delete team = MANAGER Yes (password)" — the (password) is the USER/UI sudo
  path, not an agent sudo (R32).
- Canonical cached at `/tmp/gov-rules-canonical.md` THIS session only (re-fetch via
  `gh api repos/Emasoft/ai-maestro/contents/docs/GOVERNANCE-RULES.md?ref=governance-rules`).

### Inventory + refined worklist (2026-06-18)
- **No `agents/` dir** — this CORE plugin has NO role persona. So "edit your persona"
  (templated in #12) maps here to **skills + docs + scenarios**, per #12's own
  emphasis ("your self-install skills are the R27 enforcement point").
- **Bundled mirror `skills/team-governance/references/GOVERNANCE-RULES.md` is v3.9.1
  and LACKS R26-R40** (canonical is v4.0.1, 1384 lines, R1-R40). → sync it to v4.0.1.
  CAUTION: the bundled file carries plugin-specific framing (§0 mirror-index, a
  plugin↔rule mapping table, server-file implementation pointers) — so MERGE
  (append R26-R40 + bump the embedded `version:` to 4.0.1 + refresh the changed
  R3/R6/R9/R12 wording) rather than blind-overwrite, OR verify canonical already
  contains those framing sections before replacing. Decide by diffing structure first.
- **team-governance SKILL.md + references/REFERENCE.md** carry OLD-model statements to
  reframe per R28/R32: e.g. mirror R3.5 "all role changes require the governance
  password", R3.12/R8.2 "password-protected endpoint". Reframe: **agents never sudo
  (R32)** — they auth by AID and the server does the R28 3-check; the governance
  password is a **USER/UI** path the agent **surfaces to the MAESTRO**, never performs.
  Confirm R29 (MANAGER creates teams, no user approval; auto-COS + 5 base) is stated,
  not "USER assigns COS". (Note R9.11 in the mirror already says MANAGER team-create
  needs no password / uses AID — consistent; keep.)
- **skills/ai-maestro-agents-management** — reflect R26 (identity immutable, conferred),
  R27 (self-install only via core-plugin skills + approval + CPV scan), R28 (AID
  3-check). Its agent create/update/delete docs already repointed to `aimaestro-agent.sh`
  in #11; now add the R26/R27/R28 governance framing.
- **NEW `tests/scenarios/governance-scenarios.md`** — mirror AMAMA v2.12.0's.
- The `ama-*` PRRD/TRDD/kanban governance skills are a DIFFERENT governance layer
  (3-pillars task system, not the server identity/lifecycle model) — their "USER-only"
  (golden-rule editing) is correct + out of R26-R40 scope; leave them.
### PROGRESS (2026-06-18T21:13)
- **Authoritative canonical RESOLVED:** `governance-rules` @ **v4.0.2** (commit
  `291758a4`, blob `ad6159e8`). NOT the `feature/phase6-jsonl-rebase-test` branch
  (that holds a STALE v3.9.1 — the v4.0.2 doc's own `branch:` front-matter field
  naming it is misleading editing metadata). `main` 404s (doc not yet merged
  there). v4.0.2 already folds the USER's authoritative **refined-v2** R38/R39
  wording (R38.2 user↔user messaging FORBIDDEN both ways; R39.7 ASSISTANT invisible
  but inherits the user's tasks+permissions). #37 confirms: MANAGER published AMAMA
  v2.12.0 (ref impl) + opened **9 per-plugin directives** (#12 is mine); cross-project
  rule restated there ("I edit only my own plugin directly; every other self-updates").
- **✅ ARTIFACT 1 DONE — bundled mirror synced** v3.9.1→v4.0.2 (commit `09393df`).
  Decision was **REPLACE** (verbatim canonical body + refreshed local wrapper:
  front-matter, regenerated TOC through R40, refreshed "Bundled mirror" banner),
  NOT append — the 3.x→4.x MAJOR bump reworded R1-R21, so appending R26-R40 onto
  stale R1-R21 would contradict. Verified: 1453 lines, R26-R40 at 1280-1427, single
  title/version, clean seam at line 97. `/tmp/canon-v402.md` + `/tmp/canon-body.md`
  + `/tmp/amama-gov-scen.md` (252 lines, 11 SCEN-G01..G11) cached THIS session.

- **✅ ARTIFACT 2 DONE — team-governance SKILL + REFERENCE reframed** (commit `a3057de`).
  Replaced the old agent-facing-password model with R28 (AID-auth + 3-check, never
  assert own title) / R32 (no agent sudo; password is USER/UI residual surfaced-not-
  supplied — dropped every agent-facing `--password` from CLI examples) / R29-R31
  (MANAGER lifecycle no-user-approval + auto-COS + 5-base invariant + freeze) / R26
  (identity conferred). Added an "Authorization model (R26-R40)" note to both files;
  reframed the 401 row + troubleshooting as USER/UI paths; extended SKILL.md Resources
  TOC through R40 (derived task — keeps the advertised rule list in sync with the
  synced mirror). SKILL.md v2.0.0→2.1.0. Verified: 0 `--password` in any command line.

- **✅ ARTIFACT 3 DONE — agents-management R26/R27/R28 framing** (commit `c397d59`).
  Added an "Authorization & identity (R26-R28)" note (identity conferred+immutable;
  self-install only via core-plugin skills + approval + CPV scan, THIS skill IS the
  R27 gate; AID 3-check, never assert own title) + extended the Resources governance
  pointer to R26/R27/R28. SKILL.md v3.1.0→3.2.0. **Derived fix:** cleaned an R23
  residual the #11 decouple missed — Troubleshooting "API not running" told the agent
  to `curl http://localhost:23000/api/...` directly → reframed to a CLI liveness check
  (`aimaestro-agent.sh list`); with that gone, dropped the now-dead `Bash(curl:*)`
  allowed-tool + `curl` prereq. Verified: 0 runnable curl/`/api` in the skill.

- **NEXT CONCRETE STEP (remaining artifacts):**
  (4) **NEW `tests/scenarios/governance-scenarios.md`** — mirror AMAMA's 11 SCENs
      (`/tmp/amama-gov-scen.md`), adapted to the CORE-plugin perspective (emphasize
      R27 self-install-gate, R28 skills-carry-AID-never-assert-title).
  (5) CPV `--strict` clean (devitalize/remove FPs — never suppress; report to CPV).
  (6) Publish via the canonical pipeline (CPV agent). (7) Reply #37/#12.

### Plan provenance
Issue #12 body (verbatim task) + ai-maestro#37 (canonical R26-R40 + per-plugin
matrix). AMAMA v2.12.0 is the worked example to mirror.
