# TRDD Approval Tiers, the proposal→planned lifecycle, and baseline-ruleset governance

**Scope:** This rule governs (A) where a TRDD lives during its life, (B)
**who must approve** a TRDD before it may be executed, and (C) the
standard GitHub-ruleset baseline every AI Maestro repo carries. It
applies to **every** AI Maestro agent in **every** project — MANAGER,
ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER, CHIEF-OF-STAFF,
AUTONOMOUS, MAINTAINER, and any specialist agent.

It is a **unifying layer** over three existing rules — it does not
replace them:
- `~/.claude/rules/trdd-design-tasks.md` — the TRDD file format, the v2
  `column:` pipeline, NPT/EHT, the STATE block.
- `~/.claude/rules/manager-approval-defaults.md` — the EXEMPT vs
  NON-EXEMPT operation lists and the approval-request flow.
- `~/.claude/rules/prrd-design-rules.md` — GOLDEN/SILVER rules and the
  PRRD proposal queue.

When this rule and one of those agree, follow either. When this rule
adds a constraint (proposal folder, approval tier, baseline-deviation
gate), this rule governs.

---

## TRDD lifecycle — at a glance

```text
        ┌───────────────────────────────────────────────────────────────┐
        │  design/  ⇅  GitHub repo  =  SOLE SOURCE OF TRUTH              │
        │  every clone PULLS before acting and PUSHES after each change   │
        └───────────────────────────────────────────────────────────────┘

  idea / request
       │
       │  Tier 0 (own scope · NPT/EHT) ── author directly as `planned` ──┐
       │                                                                 │
       ▼   needs approval                                                ▼
 ┌───────────────────┐   approve                                ┌────────────────────────┐
 │ design/proposals/ │   (T1 COS · T2 MANAGER · T3 USER)         │  design/tasks/         │
 │  column: proposal │ ───────────────────────────────────────▶ │  = OPEN WORK           │
 │   (PENDING)       │                                          │                        │
 └───────────────────┘                                          │  planned→todo→dispatch │
       │                                                        │  →dev→testing→ai_review│
       │ refuse  (NEVER approved)                               │  →human_review         │
       ▼                                                        │  →complete→publish|deploy
 ┌───────────────────┐                                          │                        │
 │ design/refused/   │                                          │  • blocked  (lists its │
 │  column: refused  │                                          │    blocked-by:)        │
 └───────────────────┘                                          │  • failed → RETRY      │
                                                                │    (stays OPEN, never  │
                                                                │     archived)          │
                                                                └───────────┬────────────┘
                                                                            │ terminal-DONE
                                                                            │ (was approved)
                                                                            ▼
                                                          ┌──────────────────────────────┐
                                                          │  design/archived/            │
                                                          │  completed · cancelled ·     │
                                                          │  superseded                  │
                                                          └──────────────────────────────┘

  OPEN TRDD  = any file in design/tasks/  (INCLUDING `blocked` and `failed`).
  refused/   = proposals NEVER approved.   archived/ = ONCE-approved, now terminal.
  `failed` is OPEN and retryable — fix the cause (often via other TRDDs), retry;
  it is NEVER moved to archived. Giving up on a failed TRDD = cancel → archived.
```

---

## Project identity + canonical TRDD citation

**Every AI Maestro project has a unique `project-id`** — a stable,
**repo-independent** identifier. A project may span **more than one**
GitHub repo, so a repo URL is NOT a reliable project key. The
`project-id` is registered with AI Maestro and recorded in the project's
PRRD frontmatter (`project-id:`); it is what scopes a cross-project TRDD
search to exactly one project.

**Canonical TRDD citation** (what `findtrdd` resolves):

| Form | Meaning |
|---|---|
| `TRDD-<8hex>` | **canonical** — the 8 hex are the first 8 of the TRDD's UUIDv4. Collision-free in practice, so this ALONE uniquely identifies ONE TRDD in the whole database. |
| `#<8hex>` | casual short form (chat / commit messages) |
| `<project-id>:TRDD-<8hex>` | **project-scoped** — tells `findtrdd --project <project-id>` to look only inside that project (faster, explicit locality for multi-project queries) |

`findtrdd` accepts the bare 8-hex (global lookup — always resolves to
exactly one TRDD because the hash is unique) OR a `--project <project-id>`
scope (single-project lookup). The space in `TRDD-<8hex>` citations stays
greppable: `grep -rn "TRDD-9a8aba94" .` finds every reference.

To **know all TRDDs in all open projects**, the MANAGER iterates the
registered `project-id`s and reads each project's `design/` from its
**GitHub SSOT** (the canonical copy), never a possibly-stale local clone.

---

## Part A — Two folders: `design/proposals/` and `design/tasks/`

A TRDD lives in exactly one of two folders, by lifecycle state:

| Folder | Lifecycle state (`column:`) | Meaning |
|---|---|---|
| `design/proposals/` | `proposal` | Authored, awaiting approval. **NOT** authorized to execute. |
| `design/tasks/` | `planned` (then every downstream `column:` — `todo`, `dispatch`, `dev`, `testing`, …) | Approved/authorized. In the execution pipeline. |
| `design/refused/` | `refused` | A **proposal that was NEVER approved** — declined at the proposal gate. Kept (per RULE 0 never deleted) as an audit record. |
| `design/archived/` | `completed` · `cancelled` · `superseded` | **Once-approved** TRDDs that reached a terminal-DONE state — finished, withdrawn, or replaced. Kept (never deleted). **`failed` is NOT here** — it stays in `design/tasks/` (retryable). |

**Lineage rule (which terminal folder?):** the dividing line is *was it
ever approved?* A proposal the approver **declines** never entered the
pipeline → it goes to **`design/refused/`**. A TRDD that **was approved**
(reached `design/tasks/`) and later finishes, is cancelled, or is
superseded → it goes to **`design/archived/`**. Only once-approved TRDDs
can land in `design/archived/`; only never-approved proposals land in
`design/refused/`.

`proposal`, `planned`, `refused`, `cancelled`, `completed`, and
`superseded` are **overlay values of the v2 `column:` field** (TRDD v2
has no separate `status:` field — the state machine is `column:`).
`proposal` precedes `planned`; `planned` is the approved-entry column
from which the owner advances the TRDD through the normal v2 flow
(`todo` → `dispatch` → `dev` → …).

**Three terminal-archive states live in `design/archived/`:**
`completed` (work finished / shipped), `cancelled` (withdrawn — the work
is no longer wanted), and `superseded` (replaced by other TRDD(s)).
**`refused`** is the separate proposal-stage rejection and lives in
`design/refused/`.

**`failed` is NOT terminal and is NOT archived.** A failed TRDD stays in
`design/tasks/` with `column: failed`; failure is a *retryable* state —
the owner fixes the cause (often by running other TRDDs) and retries
until it succeeds. Only an explicit decision to give up converts
`failed` → `cancelled` (→ `design/archived/`). There is no "archive as
failed".

### Lifecycle

1. **A TRDD that needs approval** (see Part B) is authored in
   `design/proposals/` with `column: proposal` in its frontmatter.
   While it sits there it is a request, not a commitment — nobody is
   expected to execute it. (Full field list: **Creation procedure** below.)
2. **On approval** by the authority Part B requires, the approver:
   - sets `column: planned`,
   - records the approval in the TRDD body `## Approval log`
     (who approved, when, one-line rationale),
   - **moves the file** with `git mv design/proposals/TRDD-….md
     design/tasks/TRDD-….md` (preserves history),
   - bumps `updated:`.
   The TRDD then flows through the normal v2 pipeline. (Step-by-step:
   **Promotion protocol** below.)
3. **On refusal**, the approver sets `column: refused`, records the
   one-line reason in `## Approval log`, and `git mv`s the file into
   `design/refused/` (never deletes it). (Step-by-step:
   **Refusal protocol** below.)
4. **An agent MAY author a TRDD directly in `design/tasks/` with
   `column: planned`** — skipping the proposal stage entirely — **only
   when the task is within that agent's independent authority (Tier 0
   below).** This is the common case for **DERIVED TASKS**: the
   necessary prerequisites (NPT) and effect-handling tasks (EHT) an
   agent must create and execute to deliver an already-approved task.
   It also covers a genuinely independent, in-scope task the agent
   needs to do its job. Agents are **expected** to continuously plan
   and execute their own Tier-0 work this way without waiting on
   anyone.

The design/ folders are therefore an **accurate live index** with three
zones:

- `design/proposals/` (excluding `refused/`) — *pending a decision*.
- `design/tasks/` — **OPEN work**: authorized and not yet terminal —
  every column from `planned` through `dev`/`testing`/`blocked`/**`failed`**.
- `design/archived/` + `design/refused/` — *decided / terminal*
  (`completed`/`cancelled`/`superseded`, and `refused`).

An **OPEN TRDD is exactly one that lives in `design/tasks/`** — the
canonical definition the MANAGER uses to report open work. Keeping the
zones accurate is why every decision (approve / refuse / complete /
cancel / supersede) **`git mv`s** the file into the right zone, so a
decided TRDD never lingers among the open ones. **Failed TRDDs are open**
— they stay in `design/tasks/` and are retried, never archived.

**Grandfathering:** TRDDs already in `design/tasks/` before this rule
existed are treated as `planned` (already authorized). Do **not** move
them to `design/proposals/`.

### Creation procedure (authoring a proposal)

A proposal is a normal v2 TRDD that happens to start at `column:
proposal` and live in `design/proposals/`. To author one:

1. Generate identity + timestamps (same as any TRDD):
   ```bash
   TID=$(python3 -c "import uuid; print(uuid.uuid4())"); SHORT=${TID:0:8}
   TS=$(date +%Y%m%d_%H%M%S%z); ISO=$(date +%Y-%m-%dT%H:%M:%S%z)
   ```
2. Write `design/proposals/TRDD-$TS-$SHORT-<slug>.md` with frontmatter:
   - `trdd-id: $TID`, `title:` (no colon), `column: proposal`,
     `created: $ISO`, `updated: $ISO`, `current-owner:`, `task-type:`.
   - **`approval-tier: N`** — the tier (0/1/2/3 from Part B) this
     proposal needs. This is what makes the proposal's required
     authority greppable and lets the listing tool show it. A Tier-0
     task does **not** belong here (author it directly in
     `design/tasks/`); proposals are Tier 1/2/3 by definition.
   - Relationships (`parent-trdd:`, `npt:`, `eht:`, `relevant-rules:`)
     and `external-refs:` as applicable.
3. Body: fully **self-contained** (a cross-project proposal's
   implementer shares none of the author's context — write the WHY,
   the exact changes, acceptance criteria, and verification steps).
   Add a STATE block if it will span sessions, and end with an empty
   `## Approval log` placeholder so the approver has a home for the
   decision line.
4. Commit it (`docs: add proposal TRDD-$SHORT — <summary>`).

### Promotion protocol (approve: `proposal` → `planned`)

Performed by the authority Part B requires (USER / MANAGER / COS), or
in batch by the `amama-proposal-approvals` skill. Per proposal:

1. Confirm the approver holds the proposal's `approval-tier:` authority
   (a Tier-3 proposal needs USER; a Tier-2 needs MANAGER; etc.).
2. Edit frontmatter: `column: proposal` → `column: planned`; bump
   `updated:` to a fresh `date +%Y-%m-%dT%H:%M:%S%z`.
3. Append to `## Approval log`:
   `- <ISO> — APPROVED by <approver> (tier <N>). <one-line rationale>.`
4. `git mv design/proposals/TRDD-….md design/tasks/TRDD-….md`.
5. Commit (`docs: approve TRDD-<short> → planned`). The owner then
   advances it through the normal v2 pipeline (`planned` → `todo` → …).

### Refusal protocol (refuse / deny)

Never delete a refused proposal (RULE 0 — it is the audit trail). Per
refused proposal:

1. Edit frontmatter: `column: proposal` → `column: refused`; bump
   `updated:`.
2. Append to `## Approval log`:
   `- <ISO> — REFUSED by <approver> (tier <N>). <one-line reason>.`
3. `git mv` the file into `design/refused/` (create the
   folder if absent). It leaves the pending index but stays in-repo.
4. Commit (`docs: refuse TRDD-<short> → refused`).

A refused proposal is terminal — re-attempting the idea means authoring
a **new** proposal (which may cite the refused one in `supersedes:` /
the body).

### Archival protocol (complete / cancel / supersede → `design/archived/`)

A TRDD leaves the OPEN zone (`design/tasks/`) for `design/archived/`
when it reaches a **terminal-DONE** state — one of three:

| State | `column:` | When |
|---|---|---|
| **completed** | `completed` | the work is finished / shipped (its release-via terminal reached: internal `complete`, tool `published`, or service `live` past soak) |
| **cancelled** | `cancelled` | the work is **withdrawn** — no longer wanted (applies to a proposal OR a planned task) |
| **superseded** | `superseded` | the TRDD is **replaced** by other TRDD(s) (record them in `superseded-by:`) |

Per archived TRDD (never delete it — RULE 0):

1. Edit frontmatter: `column:` → `column: <completed|cancelled|superseded>`;
   bump `updated:` (set `superseded-by:` when superseding).
2. Append to `## Approval log`:
   `- <ISO> — <COMPLETED|CANCELLED|SUPERSEDED> by <approver>. <one-line reason>.`
3. `git mv` the file into `design/archived/` (create the folder if
   absent), wherever it currently lives (`design/proposals/` or
   `design/tasks/`).
4. Commit (`docs: archive TRDD-<short> → <state>`).

**Never archive a `failed` TRDD.** `failed` is a *retryable* in-progress
state, not a terminal one — it stays in `design/tasks/` (it remains
OPEN) and is retried until it succeeds. Giving up on a failed TRDD is an
explicit **cancel** (`failed` → `cancelled` → `design/archived/`); it is
never silently archived as "failed".

(`amama_proposal_approvals.py archive --state <completed|cancelled|superseded>
--id <short-or-full-id> …`, with `cancel` as an alias for `--state
cancelled`, operationalizes this.)

### Batch approval syntax (the fast user/MANAGER path)

Reviewing proposals one-by-one does not scale. The canonical fast path
(operationalized by the **`amama-proposal-approvals`** skill in the
MANAGER plugin) is:

1. **List** — the tool prints every proposal in `design/proposals/`
   (excluding `refused/`) as a numbered, one-line-each table (number,
   8-char id, tier, title) sorted by `created:`, and records a manifest
   mapping each **number → stable `trdd-id`** for the current listing.
2. **Decide** — the approver replies with one of:
   - `approved: 4,6,22,14,2` — approve **exactly** those numbers
     (promote → `planned` → `design/tasks/`). **Every unlisted proposal
     stays PENDING** — `approved:` never refuses anything by omission.
   - `refused: 48,7,8,5` — refuse **exactly** those numbers (→
     `refused/`) **and APPROVE every other proposal in the listing.**
     This is the bulk path for when approvals outnumber refusals: list
     only the few to deny, and the rest are approved by complement.
   - Both lines together (`approved: …` *and* `refused: …`) — treat
     both as **explicit** lists: approve the approved set, refuse the
     refused set, and leave everything else **PENDING** (the presence
     of an explicit `approved:` line disables the refuse-mode
     complement-approve).
3. Numbers resolve against the **most recent listing's manifest** (by
   stable `trdd-id`, not array position), so a proposal that already
   moved is reported and skipped rather than mis-targeted. If no fresh
   manifest exists, the tool re-lists first and asks the approver to
   re-issue the decision against the new numbering.

The asymmetry is deliberate: `approved:` is the **conservative**
explicit-approve verb (safe default; silence = still pending), while
`refused:` is the **bulk** approve-the-rest verb (use only when you
have reviewed the whole list and want everything except the named few).

---

## Part B — Approval classification: who must approve before `planned`

**THE DEFAULT IS TIER 0 (agent-independent).** An agent escalates to a
higher tier **only** when a trigger in that tier fires. **When unsure
which tier applies, escalate one tier — conservative beats sorry.**

### Tier 0 — Agent-independent — DEFAULT, no approval
Author directly in `design/tasks/` as `planned`. Permitted when **all**
hold:
- The task is a **DERIVED TASK** (NPT/EHT of a task the agent already
  owns) **or** an independent task **fully inside the agent's own
  assignment scope**.
- It does **not** deviate from any standard baseline (GitHub rulesets
  per Part C, canonical pipeline, lint/test gates, …).
- It does **not** touch another team's or another project's source
  tree, public API, releases, or production.
- It does **not** change governance (PRRD rules, approval rules,
  personas, baselines) and incurs no cost/risk beyond the agent's
  mandate.
- It is reversible and local.

This is exactly the **EXEMPT** set in
`manager-approval-defaults.md` (mechanical column transitions, TRDD
intake/authoring, within-team coordination, read-only queries, runtime
evidence logging, applying the ratified baseline as-is).

### Tier 1 — CHIEF-OF-STAFF approval — team-internal coordination
Required when the task:
- affects **other members of the same team**, reprioritizes team work,
  or creates team-internal dependencies; or
- is proposed by a team-internal agent (ORCH/ARCH/INT/MEMBER) and
  reaches **beyond its own slice but stays inside the team**.

Per R6 v3, **COS is the sole entry point into a team** — the proposal
routes through the team's CHIEF-OF-STAFF. COS may approve and promote
(`proposal → planned`, move the file) **without** escalating, UNLESS a
Tier-2/3 trigger also fires — then COS forwards to MANAGER.

### Tier 2 — MANAGER approval — cross-team / governance / release / baseline-deviation
Required when the task:
- **deviates from a standard baseline, or adds/loosens/removes a rule
  relative to the baseline** — e.g. a special GitHub-ruleset exception,
  an extra branch rule, a new bypass actor, a downgraded required check
  (see Part C); or
- crosses **team or project** boundaries; or
- enters the **release pipeline** (publish/deploy to production) — the
  NON-EXEMPT release transitions; or
- changes a **SILVER PRRD rule**, a persona, or other governance; or
- is **architectural / first-of-kind / high-blast-radius**.

These are the **NON-EXEMPT** operations in
`manager-approval-defaults.md`, minus the USER-only items. The agent
files the TRDD in `design/proposals/` and routes an approval request to
MANAGER (team-internal agents via their COS). MANAGER approves →
promotes → moves to `design/tasks/`.

### Tier 3 — USER approval — golden / highest-stakes / owner-facing
Required when the task:
- changes a **GOLDEN PRRD rule**, or promotes/demotes a rule between
  golden and silver; or
- is anything **MANAGER itself cannot authorize** (the USER-only items
  in `manager-approval-defaults.md` §X — golden edits, promote/demote);
  or
- is **irreversible, public-facing at the owner-identity level, or
  otherwise highest-stakes** (first production deploy of a new service,
  a breaking public-API change, anything touching shared credentials /
  the owner GitHub identity).

MANAGER escalates to USER and relays the decision back down the chain.

### Routing summary
- Team-internal agents (ORCH/ARCH/INT/MEMBER) route **all** proposals
  through their **COS** (R6 v3). COS handles Tier 1; forwards Tier 2/3
  to MANAGER.
- AUTONOMOUS and MAINTAINER propose **directly to MANAGER**
  (governance-layer peers).
- MANAGER handles Tier 2; forwards Tier 3 to USER.
- USER is the only approver for Tier 3.

---

## Part D — Asynchronous enforcement: self-classify fast, audit lazily

Approval must **never** be a bottleneck and **never** force a synchronous
interrupt. An agent is busy and often steered by the USER; the MANAGER
serves ALL agents and ALL projects on its host; a COS serves one team.
None of them can stop to review every TRDD the instant it is created.
The model below keeps agents at full speed while still catching the
under-classification an efficiency-oriented agent is tempted to do.

### D1. Never block; enqueue and drain on idle

- **Tier 0** → author in `design/tasks/` as `planned` and **proceed
  immediately**. No wait, ever. This is the overwhelming majority of work
  (all derived NPT/EHT and in-scope tasks). Agents are *expected* to
  create as many Tier-0 derived TRDDs as the work needs.
- **Tier 1/2/3** → author in `design/proposals/`, then **keep working on
  other things**. The agent does NOT spin-wait on the approver. The
  proposal sits in a **queue** the approver drains when not busy with
  more urgent matters (the janitor heartbeat is a natural idle cadence).
  Time is never a constraint — a proposal may wait minutes or days; the
  agent picks it up once approved.
- The approver processes the queue **by priority** (sensitive/urgent
  first), not in creation order, and **never** as a per-creation
  interrupt.

### D2. Self-classify for speed — but it is AUDITED, not trusted

The agent sets its own `approval-tier:` so it never waits on a human to
*classify*. That speed is bought with an explicit anti-gaming contract:

- An agent that **deliberately under-classifies** a TRDD (flags a
  sensitive change Tier 0 to dodge the queue) commits a **governance
  violation** — worse than the wait it avoided. The agent's local
  judgment is NOT a substitute for the MANAGER's: only the MANAGER has
  the cross-project, user-priority, whole-picture view.
- Because the high tiers are defined by **objective, greppable signals**
  (below), misclassification is **mechanically detectable** — so it is
  caught, just not instantly.

### D3. The objective tier-floor (mechanical, not subjective)

A TRDD's **minimum** tier is computed from what it actually touches —
signals a script can check, so the watchdog needs no subjective call:

| Objective signal in the TRDD's content / proposed diff | Tier floor |
|---|---|
| GOLDEN PRRD rule edit · shared credentials / owner identity · irreversible destructive op · first production deploy of a new service · breaking public-API change | **3 (USER)** |
| `.github/` workflows or rulesets · baseline-ruleset deviation · another project's source (cross-repo) · SILVER PRRD / persona / governance file · `release-via: publish\|deploy` to production | **2 (MANAGER)** |
| affects other members of the same team / cross-member coordination | **1 (COS)** |
| everything else (in-scope dev, NPT/EHT, docs, local refactor) | **0** |

Keep the floors **narrow and objective** — approval is required *rarely*,
only for truly sensitive, detectable categories. The narrower and more
objective they are, the less incentive to cheat and the more reliably the
watchdog detects under-classification.

### D4. The classification watchdog (lazy, not per-creation)

A **TRDD approval watchdog** runs **periodically on idle** (janitor
heartbeat cadence / MANAGER idle sweep) — **never** on every creation:

1. For each TRDD in `design/tasks/` + `design/proposals/`, compute the
   D3 objective floor from its content + proposed diff.
2. Compare the **declared** `approval-tier:` to the floor:
   - **declared ≥ floor** → fine.
   - **declared < floor (UNDER-CLASSIFIED)** → for an *unambiguous*
     objective signal, **auto-correct**: raise `approval-tier:` to the
     floor, and if it was already in `design/tasks/` as `planned`, **move
     it back to `design/proposals/`** (un-authorize it) and stop any
     dependent execution; log it in the TRDD `## Approval log` and the
     watchdog report. For an *ambiguous* case, **flag** it for the
     MANAGER queue rather than auto-moving.
3. The watchdog writes a report the MANAGER drains at leisure; it does
   not interrupt anyone.

This is the safety net that makes D2 trustworthy: agents go fast by
self-classifying, and the (rare) sensitive TRDD that was mis-flagged is
caught asynchronously and corrected — without forcing the MANAGER to
review every TRDD the moment it is born.

### D5. The two levers, used together

The USER posed "watchdog **or** relax the classifiers" — the answer is
**both**, because they reinforce each other:

- **Relax + objectify** (D3): make approval rare and its triggers
  mechanical → fewer chances and less incentive to cheat, and cheating
  becomes detectable.
- **Watchdog** (D4): audit the now-rare high-tier classifications
  lazily → catch the residual under-classification without per-creation
  review.

Relaxing alone trusts agents too much on the sensitive few; a watchdog
alone over-burdens detection on a too-large surface. Together: agents
are free, sensitive work is still gated, and no one is interrupted.

### D6. Emergency enforcement (MANAGER can raise the bar instantly)

The lazy default (D4) is wrong for an active threat. When something
urgent appears — a security threat, a discovered vulnerability/CVE, a
deprecated/forbidden API — the MANAGER can declare a **temporary
emergency rule** that **raises** the required approval for a *matching
category* of TRDDs, effective **immediately** and **proactively** (the
watchdog enforces it in real time for that category, not on the idle
sweep). From the moment it is declared, any TRDD touching the emergency
area MUST be submitted for approval and can **never be self-approved**,
until the MANAGER lifts it.

**Shape of an emergency rule** (git-tracked SSOT —
`design/requirements/emergency-rules.yaml` — and/or the AI Maestro
server registry):

```yaml
- id: cve-2026-xxxx-libfoo
  declared: 2026-06-05T19:00:00+0200
  declared-by: MANAGER
  reason: "CVE-2026-XXXX in libfoo — every TRDD touching libfoo is MANAGER-gated"
  match:                       # CHEAP, script-only predicates (the narrowing)
    paths:    ["**/libfoo/**"]
    keywords: ["libfoo", "CVE-2026-XXXX"]
    deps:     ["libfoo"]
  min-tier: 2                  # raise matches to >= Tier 2
  no-self-approve: true
  mode: realtime              # proactive for THIS category only
  expires: 2026-06-12T19:00:00+0200   # TTL — see below
  status: active              # active | expired | lifted
```

**Token discipline (mandatory — the USER's constraint).** Real-time
scanning of *all* TRDDs would burn tokens. So an emergency rule is
enforced in two cheap stages, escalating cost only as the surface
shrinks:

1. **Script pre-filter (zero-LLM):** the `match` predicates are pure
   path-glob / keyword-grep / dependency checks. They run on every
   TRDD create/change and reduce the whole corpus to the **handful of
   suspects** that actually touch the emergency area. Heuristics give no
   certainty, but they shrink the investigation area massively — that is
   their job.
2. **LLM confirm only on the suspects:** the (few) matched TRDDs get the
   expensive check — raise their `approval-tier:` to `min-tier`, enforce
   `no-self-approve` (if a match was self-approved into `design/tasks/`,
   move it back to `design/proposals/` and halt dependent execution),
   and LLM-confirm ambiguous matches. The non-matches never cost a
   token.

**Auto-expiry so a forgotten emergency can't drain tokens.** Every
emergency rule carries `expires:`. The watchdog **auto-lifts** an
expired rule (back to the lazy default) and the MANAGER's idle sweep
**reminds** about any still-active emergency ("rule X active N days —
still needed?"). The MANAGER MUST lift it when the situation stabilizes;
the TTL is the backstop if they forget. Real-time enforcement only ever
applies to the narrow matched category, never the whole corpus.

---

## Part C — Standard baseline GitHub rulesets (the always-on floor)

Every AI Maestro repository carries a **standard baseline** of GitHub
branch rulesets: the ratified pair
**`baseline-history-protect`** (no-bypass: `deletion`,
`non_fast_forward`, `required_linear_history`) +
**`baseline-pr-and-checks`** (admin-bypass for `publish.py`:
`pull_request` 1-approval + `required_status_checks`). The canonical
definition lives in `manager-approval-defaults.md` §F.

**The ai-maestro-janitor automatically enforces this baseline.** If an
agent forgets to set it (or a repo drifts off it), the janitor
re-applies the ratified pair unprompted. Applying the baseline **as-is**
is a **Tier-0** operation — no approval needed; the janitor does it
without being asked.

**Any deviation is Tier 2 (MANAGER permission required BEFORE it is
applied):**
- adding a special exception or an extra rule not in the baseline,
- loosening, downgrading, or removing a baseline rule or check,
- adding or removing a bypass actor,
- switching enforcement from `active` to `evaluate`/`disabled`,
- any per-repo ruleset that differs from the ratified baseline.

No agent may unilaterally weaken, extend, or diverge from the baseline.
If a repo genuinely needs a non-baseline rule, the agent files a
**proposal** TRDD describing the exception and routes it to MANAGER
(team-internal via COS). MANAGER weighs it; if it touches a GOLDEN rule
or the shared identity, MANAGER forwards to USER (Tier 3).

---

## Why this exists

- **Autonomy without chaos.** Agents must plan and execute their own
  Tier-0 work continuously (DERIVED TASKS) — waiting on approval for
  every step would stall everything. The tiers draw the exact line
  between "just do it" and "ask first."
- **One clear escalation ladder.** Tier 0 → COS → MANAGER → USER maps
  directly onto the EXEMPT/NON-EXEMPT lists and the GOLDEN/SILVER split,
  so there is a single, greppable answer to "who signs off on this?"
- **Proposals are visible and revertible.** A `proposal` in
  `design/proposals/` is a tracked, reviewable request; promotion to
  `design/tasks/` via `git mv` records the decision in history.
- **The baseline is a floor, not a suggestion.** The janitor guarantees
  every repo has it; the MANAGER gate guarantees nobody quietly drills a
  hole in it.

## Anti-patterns

- Authoring a Tier-2/Tier-3 task directly in `design/tasks/` as
  `planned` to skip approval. The folder is determined by the tier, not
  by convenience.
- A team-internal agent routing a proposal straight to MANAGER instead
  of through its COS (violates R6 v3).
- "It's just a small ruleset tweak" applied without MANAGER sign-off —
  baseline deviations are Tier 2 regardless of size.
- Moving a grandfathered `design/tasks/` TRDD back into
  `design/proposals/`.
- Leaving an approved proposal in `design/proposals/` after approval —
  it MUST be `git mv`-ed to `design/tasks/` so the two folders stay an
  accurate index of "pending vs authorized".
