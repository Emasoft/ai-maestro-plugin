---
name: ama-trdd-transition
description: "Move a TRDD between kanban columns (the 14-stage pipeline plus blocked/failed) — enforcing the transition matrix: who may trigger each move, the frontmatter side-effects it requires, and the AMP broadcast it sends. Each move is role-gated (ORCH dispatches, ARCH designs, INTEGRATOR owns the ->complete flip, assignee signals dev->testing, MEMBER is signal-only). Use when advancing a task through the pipeline. Trigger with /ama-trdd-transition, 'move TRDD X to testing', 'dispatch this task', or 'mark it blocked'. Authoring is /ama-trdd-write, editing /ama-trdd-update, rendering /ama-kanban-render."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(date:*), Bash(git:*), Bash(findtrdd.py:*), Bash(kanban.py:*), Bash(resolve_pillar_scripts.sh:*), Read, Write, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-trdd-transition — move a TRDD between columns (matrix-enforced)

## Overview

`ama-trdd-transition` performs a column move by editing a TRDD's `column:` field
(plus the move's mandatory frontmatter side-effects) and sending the move's AMP
broadcast. The set of legal moves, their movers, side-effects, and broadcasts is
the **transition matrix** — this skill is the choke-point that enforces it. A
column move is a TRDD edit, not a script; `kanban.py` only renders, never moves.

This skill is also the **references hub** for the whole TRDD/Kanban pillar — the
shared mechanics references (column-transitions, approval-tiers-and-zones,
dialog-loops, cos-delegation, exempt-operations, frontmatter-schema,
scripts-usage, pillar-scripts-delivery) live in this skill's `references/` and
the other `ama-*` skills link to them here. The four governance RULES themselves
live in `${CLAUDE_PLUGIN_ROOT}/rules/` (auto-installed each session) — referenced,
never duplicated.

## Permission (this skill's matrix row) — SELF-CHECK WHICH MOVE YOU MAY MAKE

| TRDD column transition | who may trigger it |
|---|---|
| → `todo` (from backburner) | MANAGER |
| `todo` → `design` | ORCHESTRATOR (delegates to ARCH) |
| `design` → `dispatch` / split→`superseded` | ARCHITECT |
| `dispatch` → `dev` (assign) | ORCHESTRATOR |
| `dev` → `testing` | the assignee (MEMBER/INT/AUTO) — **after the pre-PR gate clears with ORCH** |
| `testing` → `ai_review` / `dev` (fail) | the test runner (assignee triggers) |
| `ai_review` → `human_review` / `dev` | the AI reviewer |
| → `complete` (from ai_review/human_review) | **INTEGRATOR** — INT owns the `→ complete` flip; nobody self-marks complete |
| `complete` → `publish` / `deploy` | INTEGRATOR (NON-EXEMPT — needs MANAGER approval) |
| `publish` → `published` / `deploy` → `live` | INTEGRATOR after RELEASER/DEPLOYER returns |
| `<any working>` → `blocked` / `blocked` → restore | the TRDD's owner |
| `<any>` → `failed` | MANAGER or USER (NON-EXEMPT) |

Condensed role view (from the four rules):

| | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| TRDD column transition | ✅ any | dispatch | design | release+`→complete` | relay | signal-only | ✅ | ✅ |

**MEMBER is signal-only** — a MEMBER asks ORCH/INT to move the column (e.g.
signals "code ready"), it does not flip coordination columns itself. **Release
transitions** (`complete → publish|deploy`, `→ published`, `→ live`) and
**abandonment** (`→ failed`) are NON-EXEMPT — request MANAGER approval first
(record it in the TRDD `## Approval log`). When unsure whether a move is exempt,
treat it as non-exempt and request approval.

## Prerequisites

- The project has a `design/` tree (PRRD at `design/requirements/PRRD.md` and/or
  TRDDs under `design/tasks/`) with the TRDD you intend to move. Bootstrap with
  `bootstrap_design.py` / `get-prrd.py --init` if absent.
- Python 3.10+ on PATH. The pillar scripts live at
  `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` and are resolved at runtime via
  `resolve_pillar_scripts.sh` (works from the core plugin OR any role plugin).
- You know your governance ROLE (MANAGER / ORCH / ARCH / INT / COS / MEMBER /
  AUTONOMOUS / MAINTAINER) — this skill's permission matrix is keyed on it.

## Instructions

1. Render the board + find the TRDD (re-read before editing):

   ```bash
   DIR="$(sh "$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/resolve_pillar_scripts.sh")" || exit 1
   python3 "$DIR/kanban.py" --column dev      # see the lane you're moving from
   python3 "$DIR/findtrdd.py" 9a8aba94        # land on the file
   ```

2. Look up the move in the transition matrix
   ([references/column-transitions.md](references/column-transitions.md)): confirm
   YOUR role is the matrix Mover for this exact From→To, and read its mandatory
   frontmatter side-effects + AMP broadcast.

3. If your role is NOT the Mover, or the move is NON-EXEMPT and unapproved —
   STOP. Route it: ask the matrix Mover (e.g. ORCH for dispatch, INT for
   `→ complete`), or request MANAGER approval for a release/abandon move.

4. Edit the TRDD: change `column:`, apply ALL the move's side-effects (e.g.
   `assignee:`, `feature-branch:`, `last-test-result:`, `pre-block-column:`,
   `implementation-commits:`), bump `updated:`. For `blocked`, set
   `pre-block-column:` and a non-empty `blocked-by:`; on unblock, restore it.

5. Send the move's AMP broadcast (per the matrix), then commit by name:

   ```bash
   git add "$FN" && git commit -m "docs(trdd): TRDD-<short> <FROM> -> <TO>"
   ```

## The dialog loops (governance preconditions on the work columns)

The work columns (`dev` → `testing` → `ai_review`) are wrapped by three dialog
loops ([references/dialog-loops.md](references/dialog-loops.md)) that prevent
wasted tokens: the **comprehension handshake** (ORCH ⇄ MEMBER before `dev`), the
**in-dev issue dialog** (never silently improvise around a design flaw), and the
**pre-PR gate** (clear "done — PR now?" with ORCH before `dev → testing` / before
notifying INT). The `→ complete` flip is INTEGRATOR's after it validates the
merged PR satisfies the TRDD.

## Output

The TRDD moved to its new column with all side-effects applied, the AMP
broadcast sent, the file re-validated and committed. A one-line move summary.

## Examples

<example>
ORCH assigns a designed TRDD to a member.
→ matrix row `dispatch → dev`, Mover=ORCH: set `assignee:`, `feature-branch:`, bump `updated:`, AMP the assignee via COS, commit.
</example>

<example>
A MEMBER finished coding and wants to move to testing.
→ MEMBER is signal-only: first clear the pre-PR gate with ORCH, THEN (as assignee) flip `dev → testing` recording the commit SHAs — but the move into `complete` is INT's, not the member's.
</example>

<example>
INTEGRATOR wants to publish a completed TRDD.
→ `complete → publish` is NON-EXEMPT: request MANAGER approval, log it in `## Approval log`, then move + spawn RELEASER.
</example>

## Scope

Moves a TRDD's `column:` per the matrix (role-gated; release/abandon moves
MANAGER-gated). Authoring is `ama-trdd-write`; non-column edits are
`ama-trdd-update`; proposal-zone moves (`proposals/`↔`tasks/`/`refused/`/
`archived/`) are `ama-proposal-approvals`; rendering is `ama-kanban-render`.

## Error Handling

On non-zero exit the message is on STDERR; the agent adjusts. Exit 2 = a
precondition failed (PRRD/TRDD missing — run the bootstrap / `--init`); exit 3 =
rule/TRDD not found (check the id/number). If `resolve_pillar_scripts.sh` exits
1, the ai-maestro-plugin base is not installed — set
`$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base. This skill never mutates on
a partial failure.

## Resources

- [references/column-transitions.md](references/column-transitions.md) — the full transition matrix (mover, trigger, side-effects, AMP) + red-column priority + drift signals.
  > Contents · Reading the table · Master matrix · Pre-PR gate (dialog loop c) · INTEGRATOR owns the `→ complete` flip · Reverse moves NOT in the matrix · EHT gate for `complete` · Drift signals · Red column auto-priority ranking · AMP routing — who hears about each transition · Authority enforcement
- [references/approval-tiers-and-zones.md](references/approval-tiers-and-zones.md) — the four design zones + `proposal → planned` lifecycle + Tier 0/1/2/3 ladder + objective tier-floor.
  > Contents · A. The four design zones · B. The `proposal → planned` lifecycle · C. The four-tier approval ladder · The objective tier-floor (mechanical, greppable) · Asynchronous enforcement (never block) · D. Single-writer-per-domain (collision avoidance) · Batch approval syntax (the fast path)
- [references/exempt-operations.md](references/exempt-operations.md) — EXEMPT vs NON-EXEMPT transitions + approval-request template + `## Approval log` format.
  > Contents · EXEMPT operations (no MANAGER approval required) · A. Mechanical column transitions (judgment-free) · B. TRDD intake and authoring · C. Read-only / informational operations · D. Within-team coordination · E. Runtime evidence (write-only logging) · F. GitHub-repo hardening — apply the ratified baseline as-is · NON-EXEMPT operations (MANAGER approval REQUIRED) · X. PRRD mutations · Y. Release and production-touching transitions · Z. Escalation gates · W. Cross-team / cross-project operations · V. Architectural / first-of-kind operations · Approval-request AMP message template · MANAGER's approval / rejection reply · Recording the decision · Approval log · Crisis cross-reference · R15 compatibility notes · When to revise this list
- [references/dialog-loops.md](references/dialog-loops.md) — the three dialog loops + INTEGRATOR-owns-`complete`.
  > Contents · Loop (a) — Task-comprehension handshake (BEFORE coding starts) · Loop (b) — In-dev issue dialog (DURING coding, any time) · Loop (c) — Pre-PR gate (BEFORE the PR opens) · Ownership rule — INTEGRATOR owns the column → `completed` flip · Why this exists
- [references/cos-delegation-authority.md](references/cos-delegation-authority.md) — COS two-tier filter + escalation/presence chain.
  > Contents · The two-tier model · How escalation composes with presence (the full chain) · COS-AUTONOMOUS — the COS decides, no upstream · Category CA-A — Intra-team task coordination · Category CA-B — Approving EXEMPT-tier operations · Category CA-C — Team health & lifecycle · Category CA-D — Information & triage · COS-ESCALATE — forward to MANAGER · Category CE-X — MANAGER hard-floor · Category CE-Y — NON-EXEMPT operations · Category CE-Z — Resource / composition changes · Category CE-W — Governance / PRRD / baseline · Category CE-V — Cross-team · Category CE-U — Unresolvable in-team · Category CE-T — Conservative default · Consolidation — the COS batches, it doesn't flood · The COS escalation message (to MANAGER) · User-presence — where it lives, and the janitor fallback · Why this exists · Relationship to exempt-operations.md
- [references/trdd-frontmatter-schema.md](references/trdd-frontmatter-schema.md) — field-by-field frontmatter schema (the side-effect fields).
  > Contents · Schema invariants (grep-friendliness) · Field schema · 1. Identity (mandatory on every TRDD) · 2. Ownership · 3. Classification · 4. Relationships · 5. Delivery · 6. Verification requirements · 7. Impact · 8. Runtime evidence · 9. Audit-flow · 10. External · Type forms · Schema extension · Validation · Migration from v1 · Anti-patterns
- [references/scripts-usage.md](references/scripts-usage.md) — full pillar-script usage + TRDD skeleton + exit codes + per-role examples.
  > Contents · resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
- [references/pillar-scripts-delivery.md](references/pillar-scripts-delivery.md) — cross-plugin script resolution.
  > Contents · Two supported delivery models · Why a resolver, not a hard-coded path
- `${CLAUDE_PLUGIN_ROOT}/rules/trdd-design-tasks.md`, `${CLAUDE_PLUGIN_ROOT}/rules/trdd-approval-tiers.md`, `${CLAUDE_PLUGIN_ROOT}/rules/manager-approval-defaults.md`, `${CLAUDE_PLUGIN_ROOT}/rules/prrd-design-rules.md` — the four canonical governance rules (auto-installed to `~/.claude/rules/` each session; referenced, never duplicated).
