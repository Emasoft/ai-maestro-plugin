# TRDD: Task Requirement Design Documents (v2)

**Rule:** Every non-trivial feature spec, backlog item, or deferred-work
design note MUST be saved as a **Task Requirement Design Document (TRDD)**
in `<project-root>/design/tasks/`. TRDDs are git-tracked artifacts of the
project. Every TRDD is a single `.md` file with a YAML frontmatter that
captures all the structured state (column, ownership, dependencies, test
requirements, deploy/publish target, commit hashes, …) and a body that
captures the prose. The frontmatter is **grep-first**; tools never need
to parse anything else to answer ordinary questions about a TRDD.

This is **v2** of the TRDD rule. It supersedes v1
(`status:`-based enum + minimal frontmatter). v1 TRDDs continue to work
through the migration path in [Migration from v1](#migration-from-v1);
new TRDDs use v2.

## What's new in v2

- **`column:` replaces `status:`**. The 14-stage kanban pipeline +
  `blocked` is the canonical state machine.
- **NPT and EHT relationships** — every TRDD can spawn Necessary
  Prerequisite Task children (`npt:`) and Effects Handling Task children
  (`eht:`), in addition to traditional `blocked-by:`.
- **8-char hash reference syntax** — `TRDD-9a8aba94` or `#9a8aba94` is
  the canonical short form.
- **Full delivery / verification / impact metadata** — `release-via:`,
  `test-requirements:`, `audit-requirements:`, `review-requirements:`,
  `runtime-targets:`, `impacts:`, etc.
- **Design-column 1→N split / N→1 group semantics** — ARCHITECT can
  decompose a proto-TRDD into many full TRDDs (or merge several).
- **Per-rule PRRD citations** — `relevant-rules:` in frontmatter pins
  the PRRD rule numbers a TRDD must comply with.
- **Backtracking — `implementation-commits:`** — the SHAs that landed
  this TRDD's code, so a bug discovered later can be traced to the TRDD
  that introduced it.

## Location

**Canonical path:** `<project-root>/design/tasks/TRDD-<YYYYMMDD_HHMMSS±HHMM>-<uid-first-8>-<slug>.md`

- `design/tasks/` lives at the project root and is committed to the repo.
- It MUST NOT be in the project's `.gitignore` — fix the gitignore if it is.
- TRDDs are NEVER saved in `docs_dev/` (gitignored) or `~/.claude/`
  (not project-scoped).

If `design/` or `design/tasks/` does not exist, create with `mkdir -p`.

## Filename format

```
design/tasks/TRDD-<YYYYMMDD_HHMMSS±HHMM>-<uid-first-8>-<slug>.md
```

Three components separated by `-`:

- `<YYYYMMDD_HHMMSS±HHMM>` — **creation timestamp**, compact form (no
  `:` in the offset → Windows-safe filesystem), local time + GMT delta.
  Generate via `date +%Y%m%d_%H%M%S%z`.
- `<uid-first-8>` — first 8 hex chars of the canonical RFC 4122 UUID.
  Used as the **canonical short reference** in messages, commits, and
  citations (`TRDD-9a8aba94` or `#9a8aba94`).
- `<slug>` — kebab-case summary (2-4 words).

Generate the UUID:

```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

Example filename:

```
design/tasks/TRDD-20260602_115300+0200-a58a02c4-maintainer-title.md
```

## Frontmatter — the v2 spec

Every TRDD frontmatter is **grep-first**. The invariants:

1. **One field per line.** No multi-line strings, no folded scalars
   (`>`, `|`), no nested mappings.
2. **Lists are flow-style.** `[a, b, c]` — not block style.
3. **Enum values are bare kebab-case.** `not-started`, `in-progress`,
   `blocked`, `deploy`, `live`, etc. — never quoted, never capitalised.
4. **Titles never contain colons.** Use em-dash `—` or hyphen.
5. **Dates are ISO 8601 + local TZ offset.** Format
   `%Y-%m-%dT%H:%M:%S%z` (e.g. `2026-06-02T11:53:00+0200`). Generate via
   `date +%Y-%m-%dT%H:%M:%S%z`.
6. **No trailing whitespace, no trailing comments** on data lines.

### Full schema (organised by purpose)

```yaml
---
# ─────────── 1. IDENTITY (mandatory)
trdd-id: <full RFC 4122 UUID>            # canonical id
title: <single line, ≤80 chars, no colons>
column: backburner                       # kanban state (see "Column enum" below)
created: 2026-06-02T11:53:00+0200        # ISO 8601 + local TZ
updated: 2026-06-02T11:53:00+0200        # bump on EVERY edit

# ─────────── 2. OWNERSHIP
current-owner: amama                     # session name with write-lock on body
assignee: cos-myteam                     # who is responsible for execution
priority: 3                              # 0 = highest, 9 = lowest
severity: LOW                            # CRITICAL | HIGH | MEDIUM | LOW | NIT
effort: M                                # S | M | L | XL — rough size estimate
labels: [auth, refactor]                 # free-form tags

# ─────────── 3. CLASSIFICATION
task-type: bugfix                        # feature | bugfix | refactor | docs | infra | security | artifact | spike | audit
artifact-kinds: []                       # only when task-type=artifact; e.g. [icon, sound, html]

# ─────────── 4. RELATIONSHIPS (flow-style — grep `^npt:` returns one line per TRDD with full list)
parent-trdd: null                        # the TRDD that spawned this one
npt: [TRDD-9a8aba94, TRDD-7e80e484]      # Necessary Prerequisite Tasks
eht: [TRDD-71a2239a]                     # Effects Handling Tasks
blocked-by: [TRDD-9a8aba94]              # runtime blockers (subset of npt while in-flight)
supersedes: []                           # TRDDs this one replaces
superseded-by: []                        # populated when column=superseded
pre-block-column: null                   # column to restore to when blockers clear
relevant-rules: [3, 27, 64.134]          # PRRD rule numbers; bare = latest version, n.v = pinned

# ─────────── 5. DELIVERY
release-via: publish                     # publish | deploy | none
delivery: pull-request                   # pull-request | direct-push
target-branch: main
feature-branch: null                     # null until created
merge-strategy: squash                   # squash | merge | rebase
must-pass-tests-before-merge: true
publish-target: null                     # marketplace / registry name — when release-via=publish
publish-channel: null                    # stable | beta | nightly — when release-via=publish
deploy-target: null                      # staging | production | dev-server | <custom> — when release-via=deploy
soak-duration: null                      # e.g. "24h" — time TRDD lives in live_auditing after deploy

# ─────────── 6. VERIFICATION REQUIREMENTS
test-requirements: [unit, integration]   # subset of: unit | integration | e2e | dev-browser-headless | performance | lint | typecheck
audit-requirements: []                   # subset of: security-scan | adversarial-scan | dependency-audit | license-check | accessibility
review-requirements: [human-review]      # subset of: human-review | human-evaluation | code-review | design-review
fixtures: [sample-pdf]                   # named fixtures the test suite needs
required-credentials: [github-pat]       # required user-supplied secrets
runtime-targets: [macos, linux]          # platforms/envs this must pass on; "docker" if container required
docker-image: null                       # only when "docker" is in runtime-targets

# ─────────── 7. IMPACT
impacts: [install-script, dependencies]  # subset of: install-script | dependencies | config-schema | migration | public-api | ci-pipeline
migration-direction: null                # forward | backward | both — when migration in impacts

# ─────────── 8. RUNTIME EVIDENCE (mutated as work proceeds)
attempts: 0                              # implementation attempts
test-failures: 0                         # cumulative failure count
last-test-result: not-run                # not-run | pass | fail | partial
last-test-at: null
implementation-commits: []               # SHAs where this TRDD's code landed — primary backtracking field
pr-url: null
ci-runs: []                              # CI run URLs/IDs
published-version: null                  # populated when column reaches published; e.g. "2.10.1"
published-at: null                       # ISO timestamp when published
live-since: null                         # ISO timestamp when deployed live

# ─────────── 9. AUDIT-FLOW (only when task-type=audit)
audit-trigger: null                      # alert | sentry | log | scheduled | manual | user-report
audit-target: null                       # which deployed component is under audit
audit-evidence: []                       # links/paths to logs, sentry events, screenshots
audit-conclusion: null                   # null while investigating | benign | issue-confirmed

# ─────────── 10. EXTERNAL (optional, free-form)
external-refs: []                        # e.g. ["github.com/.../issues/42", "jira:PROJ-123"]
---
```

### Minimal TRDD (most fields use defaults)

```yaml
---
trdd-id: 7e80e484-221a-4b2c-a252-b5820af4ea19
title: Add e2e test for password reset flow
column: backburner
created: 2026-06-02T11:53:00+0200
updated: 2026-06-02T11:53:00+0200
current-owner: amama
task-type: feature
parent-trdd: TRDD-9a8aba94
test-requirements: [e2e, dev-browser-headless]
relevant-rules: [3]
---
```

A trivial TRDD uses 6-10 fields. A complex one uses 25+. Absent fields
take documented defaults. **Schema is open** — new fields can be added
without breaking old TRDDs.

## Column enum (the 14-stage kanban + blocked)

`column:` replaces v1's `status:`. Values (in lifecycle order):

| Group | Column | TRDD lives here when… |
|---|---|---|
| **ENTRY** | `backburner` | proto-TRDD parking lot |
| | `todo` | promoted by MANAGER, awaiting design |
| | `live_auditing` (entry mode) | investigation task (audit-trigger set) |
| **DESIGN** | `design` | ARCHITECT shapes proto → full TRDD; may 1→N split or N→1 group |
| | `dispatch` | full TRDD designed; awaiting `assignee:` assignment |
| **WORK** | `dev` | assignee implementing (new code OR fixes — same column) |
| | `testing` | tests + audits running; failures bounce back to `dev` |
| | `ai_review` | code review by AI agents |
| | `human_review` | human eyes required (`review-requirements:` includes `human-review`) |
| **READY** | `complete` | requirements met + tested; not yet shipped |
| **SHIP (tools)** | `publish` | actively publishing tool / package |
| | `published` | terminal: users can install the version with this TRDD's work |
| **SHIP (services)** | `deploy` | actively deploying service |
| | `live` | terminal: real traffic reaches this TRDD's code |
| **OPERATE** | `live_auditing` (soak mode) | post-deploy monitoring window |
| **EXCEPTIONS** | `blocked` 🔴 | RED — `blocked-by:` is non-empty |
| | `failed` | terminal: abandoned with post-mortem |
| | `superseded` | terminal: replaced by split/group children |

**Pipeline flows by `release-via:`:**

```
release-via: publish (tool TRDDs):
  backburner → todo → design → dispatch → dev → testing → ai_review
    → (human_review) → complete → publish → published

release-via: deploy (service TRDDs):
  backburner → todo → design → dispatch → dev → testing → ai_review
    → (human_review) → complete → deploy → live → (live_auditing soak) → live

release-via: none (internal TRDDs):
  backburner → todo → design → dispatch → dev → testing → ai_review
    → (human_review) → complete

audit TRDD (task-type: audit):
  live_auditing (entry) → done|complete (if benign)
  OR
  live_auditing → dev → testing → ai_review → ... → deploy → live (if issue-confirmed)
```

`blocked` is **orthogonal** — any working column can divert to `blocked`
when `blocked-by:` becomes non-empty, and the TRDD restores to its
`pre-block-column:` when blockers clear.

## Design-column 1→N split / N→1 group semantics

The `design` column is unique: ARCHITECT can take ONE input and produce
MANY outputs (split), or take MANY inputs and produce ONE output (group).

**Split (1 → N)** — a complex proto-TRDD becomes N parallel tasks:

- `T_parent.column` → `superseded`
- `T_parent.superseded-by` ← `[T_child1, T_child2, T_child3]`
- Each `T_childN`:
  - `parent-trdd: T_parent`
  - `supersedes: [T_parent]`
  - `column: dispatch` (or `design` if further design is needed)
  - All other frontmatter authored fresh

**Group (N → 1)** — several proto-TRDDs are merged into one larger task:

- Each input `T_in_n.column` → `superseded`
- Each `T_in_n.superseded-by` ← `[T_combined]`
- `T_combined`:
  - `supersedes: [T_in_1, T_in_2, T_in_3]`
  - `parent-trdd: null` (or first input's parent)
  - `column: dispatch`
  - Frontmatter merged thoughtfully (test-requirements, impacts, etc. → union)

## NPT vs EHT semantics

Both are children spawned BY a TRDD; they differ in WHY:

- **`npt:` — Necessary Prerequisite Tasks** — these must complete
  BEFORE the parent can proceed past `dev`. They're typically `blocked-by:`
  references while in-flight.
  Example: "Refactor auth module" depends on "Update auth schema first".
- **`eht:` — Effects Handling Tasks** — these handle the CONSEQUENCES
  of the parent's work. They are **post-conditions**, not preconditions —
  the parent can land its code, but it can't reach `complete` until its
  EHTs are also closed.
  Example: "Refactor auth module" needs EHTs "Update all callers of
  authenticate()", "Update auth-related docs", "Re-test downstream
  consumers".

A parent's transition to `complete` is gated on:

```
(column == ai_review or human_review)  ─ tests + reviews passed
  AND  all eht children are in terminal column (complete | published | live | superseded)
```

## The 8-char hash reference syntax

Every TRDD has a canonical short form derived from the first 8 hex chars
of its UUID:

| Form | Meaning |
|---|---|
| `TRDD-9a8aba94` | Full short reference — canonical in commits, PR comments, AMP messages |
| `#9a8aba94` | Casual short form — appropriate in chat / Slack-like contexts |
| `9a8aba94` | Bare prefix — accepted by `findtrdd.py` as input |

Tools resolving the short form scan filenames for the
`TRDD-<TS>-<uid-first-8>-<slug>.md` pattern; the 8-char prefix is
collision-free in practice (UUIDv4 first-8 has 2^32 = 4 billion values).
If a collision is ever detected, the tool widens to 12 chars and warns.

## STATE head section (mandatory once a TRDD spans >1 session)

Carried over from v1. A TRDD that grows across sessions becomes an
append-only chronological log. Reading it top-down hits the OLDEST
(often SUPERSEDED) facts first — and a compaction summary can carry
those stale facts forward as if current. To stay summary-proof, every
TRDD that spans more than one session MUST carry a **STATE head block**
immediately after the title, before the first body section:

```markdown
## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — <date>
```

It is the SINGLE SOURCE OF TRUTH, kept current on every edit, and
contains:

- **Current state** of each component (done / broken / pending).
- **NEXT ACTION** — the one concrete next step, runnable as written.
- **Load-bearing facts / gotchas** the work depends on.
- **SUPERSEDED — do NOT carry forward** — an explicit list of stale facts.
- **Durable artifacts to read before acting** — paths to reports/specs
  holding the evidence behind the plan.

The STATE block is body content, not frontmatter — its purpose is to
catch a model who reads the body before the frontmatter (which still
happens with current Read-tool behavior).

## Reports are evidence; decisions become TRDDs

Carried over from v1. A **report** (audit, research synthesis, option
benchmark) presents DATA. It lives under `reports/` — gitignored and
ephemeral. The moment a report leads to a DECISION, that decision MUST
be written into a TRDD — a NEW TRDD, or by EXTENDING an existing TRDD's
STATE block / plan steps.

## Todo list cross-reference

Every TaskCreate entry that references a TRDD MUST include the UUID (or
at least the `TRDD-<first-8>` prefix) in its subject or description:

```
"Implement MAINTAINER governance title (TRDD-a58a02c4)"
```

From a todo list entry, you can grep `design/tasks/` for the prefix and
land directly on the spec file.

## Workflow

### Authoring a TRDD (from any column)

1. Generate a UUID:

   ```bash
   UID=$(python3 -c "import uuid; print(uuid.uuid4())")
   SHORT=${UID:0:8}
   ```
2. Capture timestamps:

   ```bash
   TS=$(date +%Y%m%d_%H%M%S%z)
   ISO=$(date +%Y-%m-%dT%H:%M:%S%z)
   ```
3. Ensure `design/tasks/` exists; verify `design/` is NOT in `.gitignore`.
4. Create the TRDD at `design/tasks/TRDD-$TS-$SHORT-<slug>.md` with the
   mandatory frontmatter; initialise `column: backburner` (or
   `live_auditing` for audit TRDDs), `trdd-id: $UID`, same ISO datetime
   in BOTH `created:` and `updated:`. Write the prose.
5. Create a TaskCreate entry referencing the TRDD.
6. Stage and commit:

   ```bash
   git add "design/tasks/TRDD-$TS-$SHORT-<slug>.md"
   git commit -m "docs: add TRDD-$SHORT — <short description>"
   ```
7. Tell the user the TRDD ID + commit hash.

### Transitioning a TRDD between columns

The full transition matrix lives in
[references/column-transitions.md](references/column-transitions.md).
Quick reference:

| Transition | Who can trigger | Side effects |
|---|---|---|
| `backburner → todo` | MANAGER | none |
| `todo → design` | ORCHESTRATOR | assigns ARCHITECT via AMP |
| `design → dispatch` | ARCHITECT | full frontmatter authored; may 1→N split |
| `dispatch → dev` | ORCHESTRATOR | sets `assignee:` |
| `dev → testing` | assignee | signal "code ready for tests" |
| `testing → ai_review` | test runner | `last-test-result: pass`; `last-test-at:` set |
| `testing → dev` (failure) | test runner | `test-failures:` += 1; post-mortem added |
| `ai_review → human_review` | AI reviewer | only when `review-requirements:` includes human-review |
| `ai_review|human_review → complete` | reviewer | all reviews passed |
| `complete → publish|deploy` | INTEGRATOR | spawns RELEASER / DEPLOYER subagent |
| `publish → published` | RELEASER (via INTEGRATOR) | `published-version:`, `published-at:` set |
| `deploy → live` | DEPLOYER (via INTEGRATOR) | `live-since:` set |
| `live → live_auditing` (soak) | INTEGRATOR | optional; only when `soak-duration:` set |
| `<any working> → blocked` | owner | `blocked-by:` becomes non-empty; `pre-block-column:` set |
| `blocked → <pre-block-column>` | owner | `blocked-by:` empties; restore previous column |
| `<any> → failed` | MANAGER or USER | after `attempts >= threshold` or USER decision |
| `<any> → superseded` | ARCHITECT (during split) | `superseded-by:` populated |

### Mutating a TRDD

- **Body** — only the TRDD's `current-owner:` mutates the body.
- **`column:`, `assignee:`** — MANAGER, ORCHESTRATOR may mutate
  regardless of `current-owner:` (these are coordination fields).
- **`updated:`** — bump on EVERY mutation, not just status changes.
- **Frontmatter format** — every edit re-runs the greppability invariants
  check (one field per line, flow-style lists, bare kebab-case enums).

### Resuming work on a TRDD in a later session

1. Grep `design/tasks/` for the UUID prefix from the todo list:

   ```bash
   ls design/tasks/TRDD-*-9a8aba94-*
   ```
2. Read the TRDD top-to-bottom — STATE block FIRST.
3. Verify the STATE block agrees with the frontmatter `column:`. If they
   disagree, the STATE block wins (newer hand-edits beat structured fields).
4. Update the TRDD's frontmatter `column:` field as work progresses. On
   EVERY edit, bump `updated:` to current ISO datetime.
5. When complete (or terminal), keep the TRDD as historical reference.
   Do NOT delete — it's the audit trail mapping a backlog UUID back to
   the commits that shipped it.

## Migration from v1

v1 TRDDs use `status:` (6 values) and a sparser frontmatter. They keep
working through automatic mapping:

| v1 `status:` | v2 `column:` (mapping) |
|---|---|
| `not-started` | `backburner` (default) — or `todo`/`dispatch` if context indicates |
| `in-progress` | `dev` (default) — or `design`/`testing`/etc. if context indicates |
| `completed` | `complete` (NOT `published`/`live` — those are runtime states beyond v1) |
| `failed` | `failed` |
| `blocked` | `blocked` |
| `superseded` | `superseded` |

Tools (`findtrdd.py`, kanban renderer) accept both. A TRDD with
`status:` but no `column:` is treated as v1 and the mapping is applied
read-only.

**On next edit** of a v1 TRDD, the agent should:

1. Replace `status:` with `column:` using the table above.
2. Add absent v2 fields where their values are known:
   - `current-owner:`, `assignee:`, `priority:` from context
   - `task-type:` based on what the TRDD does
   - `release-via:` (default `none` — promote to `publish`/`deploy` if it ships)
   - `test-requirements:`, `audit-requirements:`, etc. (default `[]`)
3. Commit as a normal TRDD edit with `chore(trdd): migrate <short> to
   v2 frontmatter` message.

Do NOT auto-migrate v1 TRDDs en masse — incremental migration on next
touch is the right cadence.

## Grep cheat-sheet (extended)

```bash
# Every TRDD's column in one go (UID-prefixed)
grep -H "^column:" design/tasks/*.md

# All currently in-blocked TRDDs (the RED column)
grep -l "^column: blocked$" design/tasks/*.md

# All TRDDs in WORK group (dev/testing/ai_review/human_review)
grep -lE "^column: (dev|testing|ai_review|human_review)$" design/tasks/*.md

# All TRDDs assigned to a specific agent
grep -l "^assignee: cos-myteam$" design/tasks/*.md

# All TRDDs that cite PRRD rule 64
grep -lE "^relevant-rules:.*\\b64\\b" design/tasks/*.md

# All TRDDs that cite PRRD rule 64 in body (any version)
grep -rlE "PRRD [GS]64(\\.|\\b)" design/tasks/

# All TRDDs blocked by a specific TRDD prefix
grep -l "^blocked-by:.*TRDD-9a8aba94" design/tasks/*.md

# All TRDDs that landed commit abc1234
grep -l "^implementation-commits:.*abc1234" design/tasks/*.md

# All audit TRDDs whose conclusion is "issue-confirmed"
grep -l "^audit-conclusion: issue-confirmed$" design/tasks/*.md

# All TRDDs whose tests have failed ≥3 times
awk '/^test-failures: [3-9]|^test-failures: [0-9][0-9]/' design/tasks/*.md

# Last 5 TRDDs touched, chronologically (most-recent last)
grep -H "^updated:" design/tasks/*.md | sort -t: -k2 | tail -5

# Every TRDD's title in one shot
grep -H "^title:" design/tasks/*.md

# Find a TRDD by partial UID (first 8 chars)
ls design/tasks/TRDD-*-9a8aba94-*.md

# Find a TRDD by full UUID (grep frontmatter)
grep -l "^trdd-id: 9a8aba94-b5d7-4d48-b05f-bdbd72295a13" design/tasks/*.md

# Find a TRDD by content keyword
grep -rl "<keyword>" design/tasks/

# All tool TRDDs not yet published
grep -lE "^release-via: publish$" design/tasks/*.md | xargs grep -L "^column: published$"

# All service TRDDs not yet live
grep -lE "^release-via: deploy$" design/tasks/*.md | xargs grep -L "^column: live$"
```

For richer queries (e.g. "which TRDDs are blocked by a TRDD that is
itself blocked?") prefer `findtrdd.py --where ...` over chained `grep`.

## Why this exists

- **Searchability.** UUID prefix in filename + todo list lets you jump
  from backlog entry to full spec in one grep.
- **Persistence.** `design/tasks/` is git-tracked; survives branch
  switches, clean clones, and `rm -rf docs_dev/`.
- **Reviewability.** PRs that touch a TRDD get reviewed alongside the
  code, catching stale specs before they cause drift.
- **Discoverability.** New contributors (or future you) can see the
  full feature backlog without access to private session notes.
- **Uniqueness.** Date-based filenames collide when multiple specs are
  created the same day; UUIDs never collide.
- **Backtracking** — `implementation-commits:` lets a bug from any time
  trace back to the TRDD that introduced the code.
- **Compliance is greppable.** "Which TRDDs comply with rule 64?" →
  `grep -lE '^relevant-rules:.*\\b64\\b'`. One command, no API.

## Anti-patterns

- **Putting multiple decisions in one TRDD.** Each TRDD is one atomic
  task. If you're tempted to "and also do X" in a TRDD, that's an NPT
  or EHT child, or a separate TRDD entirely.
- **Editing a `completed` / `failed` / `superseded` / `published` /
  `live` TRDD's body.** Those are terminal columns. New work = new TRDD.
  Only `updated:` and (for `superseded`) the `superseded-by:` field may
  be touched.
- **Skipping the STATE block on multi-session TRDDs.** The grep-cheat
  finds your TRDD but the model reading it without the STATE block can
  surface stale facts as if current.
- **Citing rules without their numbers.** "Should follow the
  installation conventions" is unverifiable; "should follow `PRRD G3.1`"
  is checkable.
- **Mutating `column:` without bumping `updated:`.** The kanban view
  relies on `updated:` for "last touched" sorting; stale `updated:` makes
  the board misleading.
- **Marking a TRDD `complete` while its EHTs are open.** EHTs are
  post-conditions; the parent's transition to `complete` must wait.

## Does NOT apply to

- **Session handoff files** — `docs_dev/YYYY-MM-DD-handoff-*.md` is
  still fine for session state not committed.
- **Scenario test files** — use `tests/scenarios/SCEN-NNN_*.scen.md`
  with sequential numbers, tracked in the scenarios folder.
- **Proposal reports** — `tests/scenarios/reports/*_<timestamp>.md`.
- **Trivial TODOs** that will be done in the current session — just use
  TaskCreate, no TRDD needed.
- **Inline code comments / TODOs** — those are fine where they are.

TRDDs are specifically for **non-trivial design tasks** that will be
picked up later and need to survive as tracked artifacts of the project.
