# Column transition matrix

**Scope:** Formal contract for who can move a TRDD from column X to
column Y, what frontmatter mutations the transition triggers, and what
AMP messages the move broadcasts. This is the machine-readable
specification consumed by `kanban.py` and by per-role skills.

## Reading the table

- **From / To** are `column:` enum values from
  [trdd-design-tasks.md](trdd-design-tasks.md#column-enum-the-14-stage-kanban--blocked).
- **Mover** is the role (governance title) authorised to trigger the
  transition. AMAMA = MANAGER. COS = CHIEF-OF-STAFF. ORCH =
  ORCHESTRATOR. ARCH = ARCHITECT. INT = INTEGRATOR. MEM = MEMBER
  (assignee). AUTO = AUTONOMOUS. MAINT = MAINTAINER. USER = the human.
- **Trigger** is the event or condition that allows the move.
- **Frontmatter side effects** are the fields the mover MUST update
  atomically with the column change.
- **AMP broadcast** is the message (if any) the mover sends after the move.

## Master matrix

| # | From | To | Mover | Trigger | Frontmatter side effects | AMP broadcast |
|---|---|---|---|---|---|---|
| 1 | (new) | `backburner` | AMAMA, AUTO | TRDD authored from user input | Initialize all mandatory frontmatter; `column: backburner` | AMP → ORCH: "new TRDD in backburner: TRDD-<id>" |
| 2 | `backburner` | `todo` | AMAMA | MANAGER decides this is next-up | bump `updated:` | AMP → COS: "TRDD-<id> promoted to todo; please claim via ORCH" |
| 3 | `todo` | `design` | ORCH | ORCH delegates to ARCH | `assignee: <arch-session>` (temp during design); bump `updated:` | AMP → ARCH (via COS): "TRDD-<id> needs design" |
| 4 | `design` | `dispatch` | ARCH | ARCH finished full TRDD (no split) | full frontmatter; `assignee: null`; bump `updated:` | AMP → ORCH (via COS): "TRDD-<id> designed; ready for dispatch" |
| 5 | `design` | `superseded` | ARCH | ARCH 1→N split (or N→1 group) | `superseded-by: [...new children...]`; bump `updated:` | AMP → ORCH (via COS): "TRDD-<id> split into <N>: <ids>" |
| 5b | (new) | `dispatch` | ARCH | ARCH emits new child TRDDs from split | each child: `parent-trdd: <T_parent>`, `supersedes: [<T_parent>]`, `column: dispatch` | (covered by #5's broadcast) |
| 6 | `dispatch` | `dev` | ORCH | ORCH assigns to an agent | `assignee: <session>`; bump `updated:`; `feature-branch:` if `delivery: pull-request` | AMP → assignee (via COS): "TRDD-<id> assigned; please implement" |
| 7 | `dev` | `testing` | assignee (MEM/INT/AUTO) | assignee signals "code ready for tests" | bump `updated:`; record commit SHAs in `implementation-commits:` | AMP → ORCH (via COS): "TRDD-<id> code ready; running tests" |
| 8 | `testing` | `ai_review` | test runner (assignee triggers) | All `test-requirements:` + `audit-requirements:` PASSED | `last-test-result: pass`; `last-test-at:`; bump `updated:` | AMP → AI-reviewer: "TRDD-<id> awaiting AI review" |
| 9 | `testing` | `dev` | test runner | Any required test FAILED | `last-test-result: fail`; `last-test-at:`; `test-failures: +=1`; append failure post-mortem to body; bump `updated:` | AMP → assignee (via COS): "TRDD-<id> test failed; please fix" |
| 10 | `testing` | `failed` | ORCH or AMAMA | `test-failures >= project-threshold` (default 5) | `column: failed`; body grows "## Abandonment post-mortem" section | AMP → AMAMA → USER: "TRDD-<id> abandoned after <N> test failures" |
| 11 | `ai_review` | `human_review` | AI reviewer | `review-requirements:` includes `human-review` or `human-evaluation`; AI review passed | bump `updated:`; review notes in body | AMP → AMAMA → USER: "TRDD-<id> needs human review" |
| 12 | `ai_review` | `complete` | AI reviewer | `review-requirements:` does NOT include any `human-*`; AI review passed | bump `updated:`; gate on EHTs (see below) | AMP → ORCH (via COS): "TRDD-<id> reviews complete; ready to ship" |
| 13 | `ai_review` | `dev` | AI reviewer | AI review FOUND ISSUES | bump `updated:`; review notes in body | AMP → assignee (via COS): "TRDD-<id> review found issues" |
| 14 | `human_review` | `complete` | USER (via AMAMA) | USER approves | bump `updated:`; gate on EHTs | AMP → ORCH (via COS): "TRDD-<id> human-approved" |
| 15 | `human_review` | `dev` | USER (via AMAMA) | USER requests changes | bump `updated:`; USER notes in body | AMP → assignee (via COS): "TRDD-<id> needs changes per USER feedback" |
| 16 | `complete` | `publish` | INT | `release-via: publish` AND all EHTs terminal | bump `updated:` | AMP → INT: "spawn RELEASER subagent for TRDD-<id>" |
| 17 | `complete` | `deploy` | INT | `release-via: deploy` AND all EHTs terminal | bump `updated:` | AMP → INT: "spawn DEPLOYER subagent for TRDD-<id>" |
| 18 | `complete` | (terminal) | — | `release-via: none` AND all EHTs terminal | (no further moves; TRDD remains in `complete`) | (none) |
| 19 | `publish` | `published` | INT (after RELEASER returns success) | RELEASER subagent returned success | `published-version: <semver>`; `published-at: <iso>`; bump `updated:` | AMP → ORCH → COS → AMAMA: "TRDD-<id> published as <version>" |
| 20 | `publish` | `failed` | INT (after RELEASER returns failure) | RELEASER subagent returned hard-fail | body: "## Publish failure post-mortem"; bump `updated:` | AMP → AMAMA → USER: "TRDD-<id> publish FAILED; investigate" |
| 21 | `deploy` | `live` | INT (after DEPLOYER returns success) | DEPLOYER subagent returned success | `live-since: <iso>`; bump `updated:` | AMP → ORCH → COS → AMAMA: "TRDD-<id> live on <deploy-target>" |
| 22 | `deploy` | `failed` | INT (after DEPLOYER returns failure) | DEPLOYER subagent returned hard-fail | body: "## Deploy failure post-mortem"; bump `updated:` | AMP → AMAMA → USER: "TRDD-<id> deploy FAILED; investigate" |
| 23 | `live` | `live_auditing` | INT | `soak-duration:` is set; entering soak window | bump `updated:` | (none; ambient monitoring) |
| 24 | `live_auditing` (soak) | `live` | INT | soak window elapsed with no alerts | bump `updated:` | AMP → ORCH: "TRDD-<id> soak complete" |
| 25 | (new) | `live_auditing` (entry) | INT or AUTO | New investigation task born (alert, sentry, log irregularity, user-report) | `task-type: audit`; `audit-trigger:`, `audit-target:`, `audit-evidence:`; `column: live_auditing` | AMP → ORCH: "TRDD-<id> investigation started: <audit-target>" |
| 26 | `live_auditing` (entry) | `complete` | INT | `audit-conclusion: benign` | `audit-conclusion: benign`; bump `updated:` | AMP → ORCH: "TRDD-<id> audit benign" |
| 27 | `live_auditing` (entry) | `dev` | INT | `audit-conclusion: issue-confirmed` | `audit-conclusion: issue-confirmed`; body grows "## Fix plan"; bump `updated:` | AMP → ORCH (via COS): "TRDD-<id> audit found issue; needs fix" |
| 28 | `<any working>` | `blocked` | owner of TRDD | `blocked-by:` becomes non-empty | `pre-block-column: <previous>`; bump `updated:` | AMP → ORCH: "TRDD-<id> blocked by: <ids>" |
| 29 | `blocked` | `<pre-block-column>` | owner of TRDD | `blocked-by:` empties | restore `column: <pre-block-column>`; `pre-block-column: null`; bump `updated:` | AMP → ORCH: "TRDD-<id> unblocked; resumed" |
| 30 | `<any non-terminal>` | `failed` | AMAMA or USER | USER decides to abandon | body: "## Abandonment decision" + rationale; bump `updated:` | AMP → ORCH (via COS): "TRDD-<id> abandoned per USER decision" |
| 31 | `<any non-terminal>` | `superseded` | ARCH | ARCH retroactively splits or groups | `superseded-by:` populated | AMP → ORCH (via COS): "TRDD-<id> superseded" |

## Reverse moves NOT in the matrix

- **Cannot** move from a terminal column (`published`, `live`,
  `complete-with-no-release`, `failed`, `superseded`) back to any
  earlier column. Terminals are absorptive. New work = new TRDD.
- **Cannot** skip the design column for non-trivial TRDDs. If you find
  yourself wanting to move `todo → dispatch` without ARCH involvement,
  the TRDD is either trivial (use TaskCreate, not a TRDD) OR you're
  cutting corners.

## EHT gate for `complete`

A TRDD with `eht:` (Effects Handling Task children) cannot enter
`complete` until **all** EHTs are in a terminal column. The gate is
checked by the mover transitioning into `complete`:

```python
def can_enter_complete(trdd):
    for eht_ref in trdd.eht:
        eht = load_trdd(eht_ref)
        if eht.column not in ("complete", "published", "live", "superseded"):
            return False, f"EHT {eht_ref} not terminal (currently {eht.column})"
    return True, None
```

If the gate fails, the transition is refused. The owner adds the
blocking EHT to `blocked-by:` AND the TRDD moves to `blocked`. When the
EHT resolves, the gate retries.

## Drift signals

The kanban renderer flags:

- `blocked-by != []` AND `column != blocked` → **drift-block-down** —
  TRDD has blockers but isn't parked. Owner forgot to move it.
- `blocked-by == []` AND `column == blocked` → **drift-block-up** —
  blockers cleared but nobody moved it back.
- `column == complete` AND any `eht:` member NOT in terminal column →
  **drift-eht-gate** — `complete` reached prematurely.
- `column == published` AND `published-version: null` →
  **drift-publish-missing** — published without recording version.
- `column == live` AND `live-since: null` → **drift-live-missing** —
  live without timestamp.
- `column in [publish, deploy]` AND `last-test-result != pass` →
  **drift-ship-untested** — shipping without passing tests.
- `release-via: deploy` AND `deploy-target: null` →
  **drift-deploy-target-missing**.
- `release-via: publish` AND `publish-target: null` →
  **drift-publish-target-missing**.

Drift signals are surfaced by `kanban.py --check-drift` and by the
INTEGRATOR / ORCHESTRATOR skills on every column-transition attempt.

## Red column auto-priority ranking

`kanban.py` computes the "unblocks-most" ranking on every render of the
blocked column:

```python
def red_column_priority(all_trdds):
    blocked = [t for t in all_trdds if t.blocked_by]
    blocker_ids = set()
    for t in blocked:
        blocker_ids.update(t.blocked_by)
    ranking = []
    for bid in blocker_ids:
        unblocks = sum(1 for t in blocked if bid in t.blocked_by)
        blocker = load_trdd(bid)
        ranking.append({
            "trdd": blocker,
            "unblocks_count": unblocks,
            "currently_in": blocker.column,
            "assignee": blocker.assignee,
        })
    ranking.sort(key=lambda r: r["unblocks_count"], reverse=True)
    return ranking
```

Output (top of the blocked column on every render):

```
🔓 BLOCK-CLEARING PRIORITY (orchestrator: bump these)
  TRDD-9a8aba94  unblocks 3 TRDDs   currently in dev,    assignee: alice
  TRDD-71a2239a  unblocks 1 TRDD    currently in design, assignee: bob
```

ORCHESTRATOR reads this ranking AT LEAST once per work session and
bumps `priority:` on the top entries.

## AMP routing — who hears about each transition

R6 v3 enforces MANAGER → CHIEF-OF-STAFF → team-internal (ORCH/ARCH/INT/MEM)
routing. Transition broadcasts respect this. Example for transition #6
(`dispatch → dev`):

- ORCHESTRATOR is in-team.
- ORCH wants to message the assignee (also in-team).
- ORCH → assignee directly (both same-team peer, R6 permits).
- ORCH → COS: "I just assigned TRDD-<id> to <session>". COS aggregates
  status.
- COS → MANAGER: rolled into the next status batch (or sent immediately
  if AMAMA queried).

The AMP broadcasts in the matrix above use this layered convention. The
exact `amp-send` invocation is documented in each per-role skill.

## Authority enforcement

The kanban scripts MAY be invoked by any agent (read-only ops like
`findtrdd.py` are universal). Mutations are checked against the
`Mover` column above:

```bash
kanban-move TRDD-9a8aba94 dev
```

This checks `$AID_AUTH` against the AI Maestro server, resolves the
caller's governance title, and refuses if the title is not authorised
for the requested move. Refusal message includes the matrix row number
so the agent can look up who CAN make the move.

For solo / autonomous projects (no AI Maestro server), `--user` skips
the auth check and trusts the local user.
