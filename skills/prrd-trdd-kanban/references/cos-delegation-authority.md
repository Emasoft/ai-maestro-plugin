# CHIEF-OF-STAFF delegation authority

**Scope:** Defines which decisions a CHIEF-OF-STAFF (COS) may make **by
itself** within its team, versus which it MUST **escalate to the
MANAGER**. This is the filter that makes the COS a real gatekeeper —
absorbing routine team load — instead of an unfiltered relay that
forwards everything upstream (which nullifies the reason the COS
exists).

## The two-tier model

Governance R6 forces every team-internal agent (ORCHESTRATOR,
ARCHITECT, INTEGRATOR, MEMBER) to write ONLY to its COS — for
approvals, problem reports, status, clarifications. The COS then
classifies each inbound request into exactly one of two tiers:

| Tier | COS action |
|------|-----------|
| **COS-AUTONOMOUS** | COS decides/acts within the team. Nothing goes upstream. The COS may log the decision in the relevant TRDD's `## Team log` section. |
| **COS-ESCALATE** | COS forwards a single consolidated approval-request to the MANAGER and relays the MANAGER's verdict back down. |

**This filter is presence-independent.** The COS classifies the same
way whether or not the user is at the keyboard. User presence is a
**MANAGER-tier** concern, applied AFTER the COS escalates (see
"How escalation composes with presence" below). The COS never reads
user-presence itself.

## How escalation composes with presence (the full chain)

```
team agent (ORCH/ARCH/INT/MEM) has a decision/request
  └─ writes to COS (R6: only COS)
       └─ COS classifies:
            • COS-AUTONOMOUS → COS decides, done. No upstream.
            • COS-ESCALATE   → COS forwards ONE consolidated request to MANAGER
                                └─ MANAGER applies its EXISTING flow:
                                     1. amama-presence-tracker.get_state()
                                     2. hard-floor? → always escalate to USER (or defer if absent)
                                     3. golden-rule change? → ALWAYS USER, regardless of presence
                                     4. else amama-autonomous-fallback.decide():
                                          - USER present (active)      → escalate to USER
                                          - USER away/monitoring/dnd   → reversibility-matrix verdict
                                                                          (approve REVERSIBLE/COMPENSABLE
                                                                           autonomously, defer ONE-WAY-DOOR)
                                          - USER unknown               → refuse autonomous action
```

The COS layer is NEW (this document). The MANAGER layer already exists:
`exempt-operations.md`, `amama-presence-tracker`,
`amama-autonomous-fallback`, the reversibility matrix, and the
hard-floor list. The COS feeds into that unchanged.

## COS-AUTONOMOUS — the COS decides, no upstream

The unifying principle: a decision is COS-autonomous when ALL of these
hold:
1. **Team-internal in scope** — affects only this team's members /
   TRDDs, no other team.
2. **Within already-granted authority** — the team and its task scope
   were already approved by the MANAGER/USER when the team was created
   and the work was dispatched; this decision operates inside that grant.
3. **No cost, no irreversibility, no governance change** — it does not
   incur budget, is reversible, and does not touch PRRD rules,
   governance titles, or a ratified baseline.
4. **Not in the MANAGER hard-floor** and **not NON-EXEMPT** per
   `exempt-operations.md`.

### Category CA-A — Intra-team task coordination

| Decision | Notes |
|---|---|
| Assign / re-assign a TRDD to a member **within this team** | ORCH normally does this; COS does it when acting as coordinator or ORCH is absent |
| Sequence / prioritize the team's own backlog | Within the team's dispatched scope |
| Ping a member for status; chase a stalled member | Routine |
| Relay information between two members of the same team | The COS is the team's switchboard |
| Acknowledge a member's status report | No upstream needed |
| Answer a member's scope-clarification question | ONLY if the answer is already determined by the TRDD body, acceptance criteria, or PRRD. If it requires a NEW decision, escalate. |

### Category CA-B — Approving EXEMPT-tier operations

Anything already **EXEMPT** in `exempt-operations.md` (mechanical
kanban transitions, TRDD intake/triage, read-only ops, within-team
coordination, runtime-evidence logging, applying the ratified
GitHub-hardening baseline as-is). A member asking "may I move this
TRDD dev→testing?" gets a COS "yes — that's exempt" with no upstream.
The COS does not manufacture approval gates the MANAGER model doesn't
require.

### Category CA-C — Team health & lifecycle within approved composition

| Decision | Notes |
|---|---|
| Wake / hibernate a member that is **already part of the approved team** (R12 composition) | COS has this power for its OWN team per the persona's lifecycle rules |
| Restart a crashed / stuck member | Recovery, not expansion |
| Re-dispatch a TRDD that bounced from testing→dev | Mechanical |
| Health-check pings, liveness probes | Routine |

### Category CA-D — Information & triage

| Decision | Notes |
|---|---|
| Produce an intra-team status summary | Read-only |
| First-line triage of a reported problem | COS attempts in-team resolution FIRST (reassign, clarify, unblock via another member) before escalating |
| Decide a problem is resolved within the team | If the fix used only COS-autonomous actions |

## COS-ESCALATE — forward to MANAGER

The unifying principle: escalate when the decision crosses the team
boundary, incurs cost, changes governance/PRRD/baseline, is in the
hard-floor, is NON-EXEMPT, or the COS is simply unsure.

### Category CE-X — MANAGER hard-floor (ALWAYS up)

The seven hard-floor categories from
`amama-amcos-coordination/references/delegation-rules.md`:
production deployments, security-sensitive changes, data deletion,
external communications, budget commitments, breaking changes, access
changes. The COS NEVER decides these itself — not even when the user
is absent (the MANAGER decides, and even the MANAGER escalates these
to the user when present).

### Category CE-Y — NON-EXEMPT operations

Anything NON-EXEMPT in `exempt-operations.md`: entering the release
pipeline (`complete→publish`/`complete→deploy`), confirming
`published`/`live`, escalating a TRDD to `human_review`, merging any
PR, moving a TRDD to a terminal column (`failed`/`superseded`),
first-push-to-main, breaking-change attributes.

### Category CE-Z — Resource / composition changes

| Decision | Why up |
|---|---|
| Add a NEW member beyond the approved team composition | Resource + budget implication; team composition was a MANAGER/USER grant |
| Request a new tool, credential, or budget for the team | Cost / access |
| Disband the team or remove an approved member | Lifecycle decision above the COS's grant |

### Category CE-W — Governance / PRRD / baseline

| Decision | Why up |
|---|---|
| Any PRRD rule change (a member proposes add/revise/delete/promote/demote) | MANAGER owns silver; USER owns golden. COS only relays the proposal (filing it is exempt; deciding it is not). |
| Any deviation from a ratified baseline (e.g. the `baseline-*` branch ruleset) | NON-EXEMPT per `exempt-operations.md` §F |
| Any governance-title change request | Governance layer |

### Category CE-V — Cross-team

Anything involving another team, another team's members, or a
shared/host-level resource. The COS's authority is bounded to its own
team; cross-team coordination transits the MANAGER (R6.2 — the MANAGER
is the sole cross-layer / cross-team bridge).

### Category CE-U — Unresolvable in-team

| Decision | Why up |
|---|---|
| A member dispute the COS cannot settle | Needs a higher arbiter |
| A TRDD past the project's `test-failures` threshold | Re-design / re-scope decision |
| A member explicitly requests MANAGER or USER attention | Honor the request — escalate |
| Repeated blockers the COS cannot clear within the team | Red-column escalation |

### Category CE-T — Conservative default

**When the COS is unsure which tier a request falls in, it ESCALATES.**
Better to surface one extra request to the MANAGER (who can quickly say
"that was COS-autonomous, handle it") than to make an out-of-scope
decision. The COS errs toward escalation; over time, recurring
escalations that the MANAGER keeps waving through become candidates for
a new COS-AUTONOMOUS entry (the MANAGER files a PRRD proposal to widen
the COS's grant — silver rule).

## Consolidation — the COS batches, it doesn't flood

A core part of the COS's load-absorbing value: when multiple team
members raise related COS-ESCALATE requests, the COS **consolidates
them into ONE MANAGER approval-request** rather than forwarding N
separate messages. Example: three members each report their sub-task
is ready to ship → the COS sends the MANAGER a single "team X has 3
TRDDs ready for release approval: [list]" rather than three pings. This
is the difference between a gatekeeper and a relay.

## The COS escalation message (to MANAGER)

When escalating, the COS sends the MANAGER an approval-request AMP
message (the same shape as `exempt-operations.md`'s template, but
team-consolidated):

```text
Subject: COS-ESCALATE — team <team> — <N> item(s) need MANAGER decision
Type: approval_request
Priority: <max priority across the batched items>
Body:
  Team: <team-name>
  Items (each: TRDD-id, requested action, COS-assessed category, reversibility):
    1. TRDD-<id8> — complete→deploy (CE-Y, COMPENSABLE) — member <x>
    2. TRDD-<id8> — add new member 'db-expert' (CE-Z) — ORCH request
  COS in-team triage already done: <what the COS resolved itself before escalating>
  Standing by for MANAGER verdict(s).
```

The MANAGER reads the referenced TRDDs directly (R15.4 — the message
carries refs, not bodies), applies its presence-aware flow, and
replies with per-item verdicts. The COS relays each verdict to the
originating member and records it in the TRDD `## Approval log`.

## User-presence — where it lives, and the janitor fallback

The COS does NOT read user presence. Presence is consumed one layer up,
by the MANAGER, via `amama-presence-tracker` (which reads the AI Maestro
server `GET /api/users/me/presence`, server-clock-anchored). When the
COS escalates, the MANAGER's existing flow decides escalate-to-USER vs
decide-autonomously based on that presence signal. Golden-rule changes
always reach the USER regardless of presence.

**Degradation fallback (janitor breadcrumb).** If the AI Maestro server
is unreachable, `amama-presence-tracker` currently returns `unknown`
(→ refuse autonomous action → everything escalates to the user, who may
be absent → stall). To harden this, the janitor SHOULD write a
user-presence breadcrumb the presence-tracker can read as a fallback:

- Path: `~/.aimaestro/state/user-presence.json`
- Shape: `{"last_user_input_epoch": <int>, "source": "janitor", "written_at_epoch": <int>}`
- Written by the janitor's `on-prompt-submit` hook (it already had a
  vestigial `last-activity.ts` write that no detector reads — repoint
  it here) and refreshed on each heartbeat.

`amama-presence-tracker`'s read order becomes:
1. AI Maestro server `/api/users/me/presence` (authoritative).
2. On server-unreachable → the janitor breadcrumb (degraded but better
   than `unknown`).
3. On neither → `unknown` (refuse autonomous action; safe default).

This is a coordination item with the janitor plugin (it owns the hook);
filed as a follow-up. The COS tier above does NOT depend on it — it's a
MANAGER-tier robustness improvement.

## Why this exists

- **Restores the COS's reason to exist.** Without a filter, the COS is
  an unfiltered relay and the MANAGER drowns — exactly the overload the
  COS was created to prevent.
- **Bounds COS authority cleanly.** The COS decides team-internal,
  reversible, in-scope, no-cost things; everything with cross-team /
  cost / governance / irreversibility implications goes up. The
  boundary is the team itself.
- **Composes with the existing MANAGER model.** The COS tier sits
  cleanly on top of `exempt-operations.md` + the presence-aware
  autonomous-fallback — no changes to those; the COS just decides what
  reaches the MANAGER at all.
- **Conservative by default.** Unsure → escalate. Recurring waved-through
  escalations widen the COS grant via a PRRD proposal, so the boundary
  self-tunes without ever defaulting to over-permission.

## Relationship to exempt-operations.md

| Layer | Question it answers | Document |
|---|---|---|
| COS tier | "Does this team request even reach the MANAGER?" | THIS file |
| MANAGER tier | "Does this reaching-the-MANAGER operation need USER sign-off, or can the MANAGER decide?" | `exempt-operations.md` |
| Presence | "Is the USER available to sign off right now?" | `amama-presence-tracker` + `amama-autonomous-fallback` |

Three nested filters: COS (team boundary) → MANAGER (governance
boundary) → presence (user availability). A request must pass through
each in turn.
