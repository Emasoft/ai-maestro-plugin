# Exempt operations — MANAGER-approval bypass list

**Scope:** This document defines which TRDD-related operations are
EXEMPT from MANAGER approval (an agent may perform them directly) and
which are NON-EXEMPT (the agent MUST request MANAGER approval before
performing them).

**Default:** MANAGER approval is required for every significant step
in the development process. The lists below define explicit
EXEMPTIONS. **Anything not on the exempt list is non-exempt.**

**Conservative principle:** When unsure whether a transition is exempt,
the agent MUST treat it as non-exempt and request MANAGER approval.
Better safe than sorry.

**R15 alignment:** Every command from agent to agent is documented in
the TRDD body (R15.1). Approval-request AMP messages carry only the
TRDD-id and a one-line request — the TRDD itself is the canonical
record (R15.4). MANAGER is exempt from the written-form requirement
(R15.6) — MANAGER's approval reply may be direct AMP.

## Contents

- EXEMPT operations (no MANAGER approval required)
- NON-EXEMPT operations (MANAGER approval REQUIRED)
- Approval-request AMP message template
- MANAGER's approval / rejection reply
- Recording the decision
- Crisis cross-reference
- R15 compatibility notes
- When to revise this list

## EXEMPT operations (no MANAGER approval required)

The agent performs the operation, updates the TRDD frontmatter and
body, and AMP-broadcasts the status change up the chain for visibility
(not for approval).

### A. Mechanical column transitions (judgment-free)

| Transition | Trigger | Owner |
|---|---|---|
| `dispatch → dev` | ORCH sets `assignee:` after match-making | ORCHESTRATOR |
| `dev → testing` | Assignee signals "code ready for tests" | MEMBER (assignee) |
| `testing → ai_review` | All `test-requirements:` + `audit-requirements:` PASSED | test runner / MEMBER |
| `testing → dev` (FAIL) | Any required test FAILED — increments `test-failures:` | test runner / MEMBER |
| `ai_review → dev` (REJECTED) | AI reviewer found issues — review notes added to body | AI reviewer / INT |
| `live → live_auditing` (soak entry) | `soak-duration:` defined; starting soak window | INTEGRATOR |
| `live_auditing (soak) → live` | Soak window elapsed clean | INTEGRATOR |

### B. TRDD intake and authoring (always-documented operations)

| Operation | Owner | Notes |
|---|---|---|
| Author new proto-TRDD → `backburner` from user input | AMAMA | Always documented in body |
| Author new proto-TRDD → `backburner` from agent report | AMAMA / INT | "Convert agent report to TRDD" — exempt |
| Author new audit TRDD → `live_auditing` from GitHub bug report / sentry alert / log irregularity | INT / AUTO | "Triage bug report" — exempt; `audit-trigger:` records source |
| Add NPT/EHT children during design | ARCHITECT | Within design-column scope |
| Set `labels:`, `priority:` (initial), `severity:`, `effort:` | any owner | Adjusting metadata |
| Set / change `assignee:` within team | ORCHESTRATOR | Within-team coordination |

### C. Read-only / informational operations

| Operation | Owner | Notes |
|---|---|---|
| Query PRRD (`get-prrd.py`, `findprrd.py`) | any agent | Read-only |
| Find TRDDs (`findtrdd.py`) | any agent | Read-only |
| Render kanban (`kanban.py`) | any agent | Read-only |
| Cite PRRD rules in TRDD `relevant-rules:` or body | any agent | Citation does not mutate the PRRD |
| File a PRRD proposal (`prrd-edit.py propose`) | any agent | Proposals are non-binding — they request MANAGER review but don't mutate the PRRD |
| Launch ai_review on a PR (REVIEW REQUEST only, NOT merge) | INTEGRATOR | Review request is informational; the merge decision is non-exempt |
| Launch CI runs | INTEGRATOR / MEMBER | Informational; results record in `ci-runs:` |
| Investigate live_auditing — collect `audit-evidence:` | INTEGRATOR / AUTONOMOUS | Evidence collection is informational |

### D. Within-team coordination

| Operation | Owner | Notes |
|---|---|---|
| ARCH design-column work: 1→N split or N→1 group | ARCHITECT | Within design-column scope |
| ARCH sets `task-type:`, `test-requirements:`, `audit-requirements:`, `review-requirements:`, `release-via:` during design | ARCHITECT | Initial design authoring |
| ARCH sets `runtime-targets:`, `impacts:`, `fixtures:`, `required-credentials:` during design | ARCHITECT | Design metadata |
| ORCH bumps `priority:` of red-column blockers | ORCHESTRATOR | Red-column priority management |
| ORCH re-assigns a TRDD between MEMBERs within the same team | ORCHESTRATOR | Within-team reassignment |
| COS routes proposals and relays AMP messages | COS | Mechanical relay; the proposal itself is non-binding |

### E. Runtime evidence (write-only logging)

| Operation | Owner | Notes |
|---|---|---|
| Append `implementation-commits:` SHAs as code lands | MEMBER (assignee) | Backtracking field |
| Write `last-test-result:`, `last-test-at:`, `test-failures:` | test runner | Test outcomes |
| Add review notes / failure post-mortems to TRDD body | reviewer | Body content |
| Write `ci-runs:` URLs | INTEGRATOR | CI references |
| Set `feature-branch:` when starting work | MEMBER (assignee) | Branch tracking |
| Append to `audit-evidence:` during live_auditing investigation | INTEGRATOR / AUTONOMOUS | Evidence log |

### F. GitHub-repo hardening — apply the ratified baseline as-is

These operations are EXEMPT only when they apply the **ratified
unified baseline** without deviation. Any deviation (loosening a rule,
adding a bypass actor, downgrading a check, disabling a ruleset) is
NON-EXEMPT and requires MANAGER approval.

| Operation | Owner | Reference |
|---|---|---|
| Apply baseline branch rulesets (no-force/no-delete/linear + PR/checks split) | INTEGRATOR / MAINTAINER (via `workflow-protect-branch`) / janitor (Tier 1 + Tier 2) | Ratified baseline |
| SHA-pin third-party GitHub Actions | INTEGRATOR / MAINTAINER (via `workflow-pin-actions`) | Standard hardening |
| Lint config files (JSON/YAML/TOML/.env/Dockerfile) | INTEGRATOR / MAINTAINER (via `maintainer-config-lint`) | Drift detection |
| Run secret scans on the working tree + git history | INTEGRATOR / MAINTAINER (via `maintainer-secrets-scan`) | TruffleHog with public-info allowlist |
| Apply workflow bootstrap / safe-fix patterns | INTEGRATOR / MAINTAINER (via `workflow-bootstrap`, `workflow-fix-safe`) | Standard CI scaffolding |
| Restore drifted branch rules back to the ratified baseline | INTEGRATOR / MAINTAINER | Idempotent re-apply |
| Run janitor supply-chain watcher | janitor (no main agent — applies as-is) | Dependency monitoring |
| Run janitor credential-window audit | janitor (no main agent — applies as-is) | Stale token detection |
| Run janitor fork-PR cache audit | janitor (no main agent — applies as-is) | Cache poisoning detection |

**The ratified baseline (RATIFIED 2026-06-02)** is the `baseline-*`
pair, agreed byte-identical by both plugins via:

- janitor: <https://github.com/Emasoft/ai-maestro-janitor/issues/14>
- maintainer: <https://github.com/Emasoft/ai-maestro-maintainer-agent/issues/7>

The two ratified rulesets (both `target: branch`, `enforcement: active`,
condition `ref_name.include: ["~DEFAULT_BRANCH"]`):

- **`baseline-history-protect`** — `bypass_actors: []` (nobody, incl.
  admin). Rules: `deletion`, `non_fast_forward`,
  `required_linear_history`.
- **`baseline-pr-and-checks`** — `bypass_actors:
  [{actor_id:5, actor_type:RepositoryRole, bypass_mode:always}]`
  (admin direct-push for `publish.py`; outside PRs still gated). Rules:
  `pull_request` (`required_approving_review_count:1`,
  `dismiss_stale_reviews_on_push:true`,
  `require_code_owner_review:false`,
  `require_last_push_approval:false`,
  `required_review_thread_resolution:true`) and
  `required_status_checks` (`strict_required_status_checks_policy:true`,
  CI job ids auto-detected at apply time).

Applying this `baseline-*` pair as-is is EXEMPT. The legacy names
(`janitor-baseline`, `default-branch-no-force-no-delete`,
`default-branch-required-checks`) are superseded — re-applying the
ratified pair deletes the orphaned legacy rulesets by name.

**Non-exempt for this category** (require MANAGER approval):

- Adding / removing a `bypass_actor` from a ratified ruleset.
- Loosening a rule's parameters (e.g. lowering
  `required_approving_review_count`).
- Disabling required status checks.
- Switching enforcement from `active` to `evaluate` or `disabled`.
- Adding a new ruleset that affects the default branch.
- Granting a new admin role on the repo.
- Modifying secrets / tokens / OIDC bindings.

## NON-EXEMPT operations (MANAGER approval REQUIRED)

The agent composes an approval-request AMP message (template below),
sends it via COS to MANAGER, waits for MANAGER's "approved" reply,
THEN performs the transition.

For AUTONOMOUS: the chain short-circuits to USER for these operations
(AUTONOMOUS reaches USER per R6.6).

### X. PRRD mutations (already enforced via $AID_AUTH)

| Operation | Required authority |
|---|---|
| `prrd-edit.py add silver` | MANAGER (or `--user`) |
| `prrd-edit.py revise N` of silver rule | MANAGER (or `--user`) |
| `prrd-edit.py delete N` of silver rule | MANAGER (or `--user`) |
| `prrd-edit.py add golden` | USER ONLY (`--user`) |
| `prrd-edit.py revise N` of golden rule | USER ONLY (`--user`) |
| `prrd-edit.py delete N` of golden rule | USER ONLY (`--user`) |
| `prrd-edit.py promote N` (S → G) | USER ONLY |
| `prrd-edit.py demote N` (G → S) | USER ONLY |

These are enforced by `caller_is_manager()` in `prrd_lib.py`.

### Y. Release and production-touching transitions

| Transition | Why non-exempt |
|---|---|
| `complete → publish` | Entering the release pipeline; affects observable artifact state |
| `complete → deploy` | Entering the release pipeline; affects production state |
| `publish → published` (on RELEASER success) | Confirms artifact is live to users |
| `deploy → live` (on DEPLOYER success) | Confirms service is live to users |
| `live_auditing (entry) → dev` | Audit confirmed an issue; entering fix flow requires alignment |
| `<any> → failed` | Abandoning a TRDD; permanent decision |
| `<any non-design> → superseded` | Force-supersede (ARCH's design split is exempt; force-supersede is not) |

### Z. Escalation gates

| Transition | Why non-exempt |
|---|---|
| `ai_review → human_review` | Escalating to USER; MANAGER relays per R6.6 / R6.10 |
| `human_review → complete` | USER decision; MANAGER relays the verdict |
| `human_review → dev` | USER decision; MANAGER relays the verdict |
| Approving / merging a PR | Always requires MANAGER + USER for sensitive PRs |

### W. Cross-team / cross-project operations

| Operation | Why non-exempt |
|---|---|
| Reassigning a TRDD across teams | Affects multiple team's workloads |
| Creating / disbanding teams | MANAGER-only per R9, R10, R12 (already enforced) |
| Changing a TRDD's `parent-trdd:` after authoring | Modifies the TRDD lineage |

### V. Architectural / first-of-kind operations

| Operation | Why non-exempt |
|---|---|
| First push to `main` on a new feature branch | Per K3 crisis in autonomous-fallback — force-escalation |
| Marking a TRDD as a breaking change (`impacts:` includes `public-api` AND release-mode is publish/deploy) | High blast radius |
| Initial deployment of a new service to production | First-of-kind deploy |

## Approval-request AMP message template

When a non-exempt transition is needed, the agent sends to MANAGER
(via COS for team-internal agents per R6 v3):

```text
Subject: APPROVAL REQUEST — TRDD-<id8> transition <FROM> → <TO>
Type: approval_request
Priority: <normal | urgent based on TRDD priority>
Body:
  TRDD: design/tasks/TRDD-<id8>-...md
  Current column: <FROM>
  Requested transition: <FROM> → <TO>
  Rationale (1-line): <why this transition now>
  Impact (1-line): <what changes when approved>
  Reversible: <yes | no | compensable>
  
  Standing by for MANAGER reply.
```

**Per R15.4**: the message carries only the TRDD reference — the body
of the TRDD is the canonical record. MANAGER reads the TRDD directly.

## MANAGER's approval / rejection reply

**Per R15.6, MANAGER is exempt** from the written-form requirement.
MANAGER may reply with direct AMP:

- **Approved**: `"approved: TRDD-<id8> may transition <FROM> → <TO>"`.
  The requesting agent performs the transition.
- **Rejected**: `"rejected: TRDD-<id8> — <one-line rationale>"`.
  The agent records the rejection in the TRDD body's
  `## MANAGER decisions` section and does NOT perform the transition.
- **Defer**: `"defer: TRDD-<id8> — <reason>"`. The TRDD stays put;
  the agent re-requests later.
- **Escalate to USER** (for sensitive transitions): MANAGER relays
  the request to USER; the chain continues per the standard approval
  flow.

If MANAGER does NOT reply within the project's approval timeout
(default 24h for normal-priority, 1h for urgent-priority), the agent
escalates to USER directly per the AUTONOMOUS fallback rules.

## Recording the decision

Every non-exempt transition's outcome MUST be recorded in the TRDD
body in a section called `## Approval log` (creating it on first
write):

```markdown
## Approval log

- 2026-06-02T11:30:00+0200 — Requested `complete → deploy` (target: production).
  MANAGER reply: APPROVED at 11:33. Rationale: tests passed; EHTs terminal.
- 2026-06-03T09:15:00+0200 — Requested `deploy → live` (after DEPLOYER success).
  MANAGER reply: APPROVED at 09:17. `live-since: 2026-06-03T09:18:00+0200`.
```

This is the durable audit trail — git-tracked, greppable, and
discoverable via `findtrdd.py --grep "MANAGER reply: APPROVED"`.

## Crisis cross-reference

| Risk | How this rule mitigates it |
|---|---|
| Agent makes a deploy without MANAGER awareness | `complete → deploy` is non-exempt; MANAGER must approve |
| Agent merges a PR without USER awareness | Merge is non-exempt; MANAGER relays to USER for sensitive PRs |
| Agent silently abandons a TRDD | `<any> → failed` is non-exempt; MANAGER reviews abandonment |
| Agent escalates routine work to MANAGER, causing review fatigue | Category A/B/C/D/E exempt — routine work doesn't escalate |
| Agent is uncertain whether a transition is exempt | Conservative default: treat as non-exempt |
| MANAGER misses the request | Timeout escalates to USER (autonomous fallback) |
| Agent forges an "APPROVED" reply | Approval log is git-tracked; MANAGER can audit at any time |

## R15 compatibility notes

- Every exempt transition's documentation lives in the TRDD body
  (R15.1 satisfied by the TRDD).
- Every non-exempt approval-request is documented in the
  `## Approval log` section (R15.1 satisfied).
- AMP messages carry only the TRDD-id and a one-line summary (R15.4
  satisfied).
- MANAGER's approval replies use direct AMP (R15.6 exemption).
- The TRDD pile in `design/tasks/` IS the permanent audit log (R15.5
  satisfied — and arguably more queryable than GitHub issues alone).

## When to revise this list

- A new column or new transition is added to the workflow → review
  whether it should be exempt.
- A non-exempt operation becomes routine enough that MANAGER approval
  is creating friction → MANAGER files a PRRD proposal to make it
  exempt (silver rule).
- A previously-exempt operation surfaces unanticipated risk → MANAGER
  proposes to make it non-exempt.

The exempt list is a SILVER PRRD rule by default (silver = MANAGER
can revise) — MANAGER can adjust the list as patterns emerge. The
**principle** that "MANAGER approval is the default and the exempt
list defines the bypass" is a GOLDEN PRRD rule and can only be
changed by USER.
