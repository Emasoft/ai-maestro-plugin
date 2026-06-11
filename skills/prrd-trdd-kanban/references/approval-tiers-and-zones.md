# Approval tiers + the 4-zone design folders + the `proposal` lifecycle

This is the CANONICAL bundled definition of (A) the four `design/` zones a TRDD
moves through, (B) the `proposal → planned` approval lifecycle, and (C) the
four-tier approval ladder that decides WHO must approve a TRDD before it may be
executed. Role plugins defer to this file. It is a unifying layer over
[exempt-operations.md](exempt-operations.md) (the EXEMPT/NON-EXEMPT lists),
[trdd-design-tasks.md](trdd-design-tasks.md) (the `column:` pipeline), and
[prrd-design-rules.md](prrd-design-rules.md) (GOLDEN/SILVER).

## Contents

- A. The four design zones
- B. The `proposal → planned` lifecycle
- C. The four-tier approval ladder
- D. Single-writer-per-domain (collision avoidance)
- Batch approval syntax (the fast path)

## A. The four design zones

A TRDD lives in exactly one of four folders, by lifecycle state:

| Folder | `column:` overlay | Meaning |
|---|---|---|
| `design/proposals/` | `proposal` | Authored, awaiting approval. NOT authorized to execute. |
| `design/tasks/` | `planned` then every downstream column (`todo`…`dev`…`blocked`…`failed`) | Approved/authorized. The OPEN-work zone. |
| `design/refused/` | `refused` | A proposal that was NEVER approved — declined at the gate. Kept (audit trail). |
| `design/archived/` | `completed` · `cancelled` · `superseded` | Once-approved TRDDs that reached a terminal-DONE state. Kept. |

**An OPEN TRDD is exactly one that lives in `design/tasks/`** — INCLUDING
`blocked` and `failed`. `failed` is a *retryable* state: it stays in
`design/tasks/`, never archived. Giving up on a failed TRDD is an explicit
`cancel` (`failed → cancelled → design/archived/`).

**Lineage rule (which terminal folder):** *was it ever approved?* A proposal the
approver declines → `design/refused/`. A TRDD that was approved (reached
`design/tasks/`) and later finishes/withdraws/is-replaced → `design/archived/`.

Every decision (`approve`/`refuse`/`complete`/`cancel`/`supersede`) `git mv`s the
file into the right zone so the four folders stay an accurate live index. Never
delete a TRDD (RULE 0) — move it.

Bootstrap the four zones with the helper:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/bootstrap_design.py [project-root]`.
**Grandfathering:** TRDDs already in `design/tasks/` before zones existed are
treated as `planned` — do NOT move them to `proposals/`.

## B. The `proposal → planned` lifecycle

```text
 design/proposals/      approve (tier authority signs off)      design/tasks/
   column: proposal  ───────────────────────────────────────►   column: planned
        │                                                        (then todo→dev→…)
        │ refuse                                  complete/cancel/supersede
        ▼                                                              ▼
 design/refused/                                              design/archived/
```

- **Author a proposal:** a normal TRDD that starts `column: proposal` in
  `design/proposals/`, carrying `approval-tier: N` (the tier it needs). Body is
  fully self-contained + an empty `## Approval log` placeholder.
- **Promote (approve):** set `column: planned`, append an `## Approval log` line
  (`<ISO> — APPROVED by <approver> (tier N). <rationale>.`),
  `git mv design/proposals/… design/tasks/…`, bump `updated:`.
- **Refuse:** set `column: refused`, log the reason, `git mv … design/refused/`.
- **Archive:** set `column: completed|cancelled|superseded`, log it,
  `git mv … design/archived/`.

The `amama_proposal_approvals.py` script operationalizes all four moves
(`list`/`approve`/`refuse`/`archive`) — see
[scripts-usage.md](scripts-usage.md).

## C. The four-tier approval ladder

**THE DEFAULT IS TIER 0.** Escalate only when a trigger fires. When unsure,
escalate one tier — conservative beats sorry. The `approval-tier:` frontmatter
field records the tier a TRDD needs (a Tier-0 task is authored directly in
`design/tasks/`; tiers 1/2/3 start as proposals).

| Tier | Approver | Author directly in `design/tasks/`? | Fires when the task… |
|---|---|---|---|
| **0** | none (agent-independent) — DEFAULT | YES, as `planned` | is a DERIVED task (NPT/EHT of work it owns) or fully in its own scope; no baseline deviation; reversible & local. = the EXEMPT set. |
| **1** | CHIEF-OF-STAFF | no — `design/proposals/` | affects other members of the SAME team / reprioritizes team work. COS is the sole team entry point (R6 v3). |
| **2** | MANAGER | no — `design/proposals/` | deviates from a standard baseline; crosses team/project boundaries; enters the release pipeline; changes a SILVER PRRD rule / persona / governance; architectural / high-blast-radius. = the NON-EXEMPT set minus USER-only. |
| **3** | USER | no — `design/proposals/` | changes a GOLDEN PRRD rule, promotes/demotes a rule, or is irreversible / owner-identity-facing / highest-stakes. |

**Routing:** team-internal agents (ORCH/ARCH/INT/MEMBER) route ALL proposals
through their COS (R6 v3); COS handles Tier 1, forwards 2/3 to MANAGER. AUTONOMOUS
and MAINTAINER propose directly to MANAGER. MANAGER handles Tier 2, forwards Tier
3 to USER.

### The objective tier-floor (mechanical, greppable)

A TRDD's MINIMUM tier is computed from what it touches — signals a script can
check, so under-classification is detectable, not trusted:

| Objective signal in the TRDD's content / proposed diff | Tier floor |
|---|---|
| GOLDEN rule edit · shared credentials / owner identity · irreversible destructive op · first production deploy · breaking public-API change | **3** |
| `.github/` rulesets-or-workflows · baseline deviation · another project's source · SILVER/persona/governance file · `release-via: publish\|deploy` to production | **2** |
| affects other same-team members | **1** |
| everything else (in-scope dev, NPT/EHT, docs, local refactor) | **0** |

### Asynchronous enforcement (never block)

- Tier 0 → author and proceed immediately. The overwhelming majority of work.
- Tier 1/2/3 → author the proposal, then KEEP WORKING on other things. The
  approver drains the proposal queue on idle, by priority — never as a
  per-creation interrupt.
- Self-classification is for SPEED but is AUDITED: a periodic watchdog compares
  each TRDD's declared `approval-tier:` to its objective floor and corrects
  under-classification (raises the tier, moves a wrongly-self-approved TRDD back
  to `proposals/`). Deliberate under-classification is a governance violation.

## D. Single-writer-per-domain (collision avoidance)

Every mutable surface (a file, a config key, a board column's state, a release
channel) has exactly ONE owner at a time, recorded by the TRDD's `current-owner:`
write-lock. A task needing a domain it does not own either delegates to the owner
or takes a documented claim. DERIVED tasks (NPT/EHT) inherit this: before an
NPT/EHT touches a surface, confirm no sibling derived task already owns it — two
EHTs editing the same file in parallel is the classic collision. The comprehension
handshake (loop a, item 2) is where ORCH cross-checks the MEMBER's named domains
against existing owners.

## Batch approval syntax (the fast path)

`amama_proposal_approvals.py list` prints every pending proposal as a numbered
one-line table. The approver replies with either:

- `approved: 4,6,22` — approve EXACTLY those (everything else stays pending). The
  conservative explicit-approve verb.
- `refused: 7,8` — refuse exactly those AND approve every OTHER listed proposal.
  The bulk approve-the-rest verb (use only after reviewing the whole list).

Numbers resolve against the most recent listing's stable `trdd-id` manifest.
