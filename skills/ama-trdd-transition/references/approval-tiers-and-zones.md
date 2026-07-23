# Approval tiers + the 4-zone design folders + the `proposal` lifecycle

This is the CANONICAL bundled definition of (A) the four `design/` zones a TRDD
moves through, (B) the `proposal → planned` approval lifecycle, and (C) the
`min-approval-requirement:` field whose ladder decides WHO must approve a TRDD
before it may be executed — with the authoritative **rung semantics deferred to
the ai-maestro DEP overlay** (approval authority is a DEP concern per the
3-pillars SPEC `3P-BND-02`, not CORE's to re-teach). Role plugins defer to this
file for the IND scaffolding. It is a unifying layer over
[exempt-operations.md](exempt-operations.md) (the EXEMPT/NON-EXEMPT lists),
[trdd-design-tasks.md](trdd-design-tasks.md) (the `column:` pipeline), and
[prrd-design-rules.md](prrd-design-rules.md) (GOLDEN/SILVER).

## Contents

- A. The four design zones
- B. The `proposal → planned` lifecycle
- C. The `min-approval-requirement:` field (rung semantics defer to the DEP overlay)
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
  `design/proposals/`, carrying `min-approval-requirement: <title>` (the TITLE it
  needs). Body is fully self-contained + an empty `## Approval log` placeholder.
- **Promote (approve):** set `column: planned`, append an `## Approval log` line
  (`<ISO> — APPROVED by <approver> (min-approval-requirement: <title>). <reason>`),
  `git mv design/proposals/… design/tasks/…`, bump `updated:`.
- **Refuse:** set `column: refused`, log the reason, `git mv … design/refused/`.
- **Archive:** set `column: completed|cancelled|superseded`, log it,
  `git mv … design/archived/`.

The `amama_proposal_approvals.py` script operationalizes all four moves
(`list`/`approve`/`refuse`/`archive`) — see
[scripts-usage.md](scripts-usage.md).

## C. The `min-approval-requirement:` field (rung semantics defer to the DEP overlay)

The `min-approval-requirement:` frontmatter field records the TITLE a TRDD needs
before it may execute, on the ladder
`none < orchestrator < chief-of-staff < manager < user`. **THE DEFAULT IS `none`** —
and that is also what an ABSENT field means: a `none` task is authored directly in
`design/tasks/` as `planned`; any higher rung starts as a proposal in
`design/proposals/`. When unsure, escalate one rung — conservative beats sorry.

> **`approval-tier: N` is RETIRED — never write a number.** DECODE a legacy card as
> `0→none, 1→chief-of-staff, 2→manager, 3→user` and rewrite it to the title.
> `orchestrator` has no number: a 4-value numeric field structurally cannot express
> it, which is exactly why the scheme was retired.

**The authoritative rung semantics live in the ai-maestro DEP overlay, not here.**
Per the 3-pillars SPEC `3P-BND-02`, `min-approval-requirement` / approval tiers /
mandate authority / COS routing are **DEP** — so WHO each title is, WHEN each rung
fires, the objective **requirement-floor** the watchdog audits against, and the COS
routing are defined once in `.claude/rules/aimaestro-trdd-approval.md` (Part B2),
seeded into every agent workdir. CORE does not re-teach them here — a second copy
would drift, which is exactly what the governance-rules retirement (core#35) removed.
The one IND base rule that holds even with no harness: the **USER** approves a
GOLDEN-PRRD-rule change or an irreversible / owner-identity-facing op; a project's own
Claude self-approves in-scope `none` work.

Enforcement is **asynchronous — never block**: author a `none` task and proceed; for
any higher rung author the proposal and KEEP WORKING while the approver drains the
queue on idle (never a per-creation interrupt). Self-classification is for SPEED but
is AUDITED by the overlay's watchdog, which raises an under-classified requirement and
moves a wrongly-self-approved TRDD back to `proposals/`.

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
