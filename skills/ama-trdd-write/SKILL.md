---
name: ama-trdd-write
description: "Author a new TRDD task-design document under design/ with correct v2 frontmatter — uuid + timestamps, the right zone (tasks/ for a Tier-0 task written directly as 'planned'; proposals/ for a Tier-1/2/3 task needing approval), and a self-contained body. Allowed for every role (MEMBER via COS). Use when a non-trivial task, feature, or decision must be captured as a tracked spec, or a report's decision becomes a TRDD. Trigger with /ama-trdd-write, 'write a TRDD for X', or 'capture this as a task spec'. Finding is /ama-trdd-find, editing /ama-trdd-update, column moves /ama-trdd-transition."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(date:*), Bash(git:*), Bash(resolve_pillar_scripts.sh:*), Read, Write, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-trdd-write — author a new TRDD

## Overview

`ama-trdd-write` creates a new TRDD: it generates the identity (uuid +
timestamps), chooses the correct `design/` zone, and writes a v2-compliant
frontmatter + a self-contained body. A TRDD is the tracked, git-committed spec
for one atomic non-trivial task; trivial in-session todos do NOT need one.

## Permission (this skill's matrix row)

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| **author proto-TRDD** | ✅ | ✅ | ✅ | ✅ | ✅ | via COS | ✅ | ✅ |

Authoring is broadly allowed; a MEMBER routes intake through its COS (R6 v3).
**The zone you write into is decided by the approval tier** (self-classify):

- **Tier 0 (default)** — a DERIVED task (an NPT/EHT of work you already own) or a
  task fully inside your own scope, reversible & local, no baseline deviation →
  author directly in `design/tasks/` with `column: planned`. Proceed immediately.
- **Tier 1 / 2 / 3** — affects other team members (1, COS) / crosses team or
  project boundaries, enters the release pipeline, changes SILVER governance (2,
  MANAGER) / changes GOLDEN governance or is irreversible/owner-facing (3, USER)
  → author in `design/proposals/` with `column: proposal` and `approval-tier: N`;
  then keep working — approval is asynchronous (`ama-proposal-approvals` drains it).

**When unsure which tier, escalate one tier — conservative beats sorry.** Use the
objective tier-floor table in the approval-tiers reference.

## Prerequisites

- The project has a `design/` tree (PRRD at `design/requirements/PRRD.md` and/or
  TRDDs under `design/tasks/`); this skill bootstraps the four zones if absent.
  Bootstrap with `bootstrap_design.py` / `get-prrd.py --init` if absent.
- Python 3.10+ on PATH. The pillar scripts live at
  `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` and are resolved at runtime via
  `resolve_pillar_scripts.sh` (works from the core plugin OR any role plugin).
- You know your governance ROLE (MANAGER / ORCH / ARCH / INT / COS / MEMBER /
  AUTONOMOUS / MAINTAINER) — this skill's permission matrix is keyed on it.

## Instructions

1. Bootstrap the four `design/` zones if absent (idempotent):

   ```bash
   DIR="$(sh "$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/resolve_pillar_scripts.sh")" || exit 1
   python3 "$DIR/bootstrap_design.py"
   ```

2. Generate identity + timestamps and the filename (note: `$UID` is reserved by
   zsh — use `$SHORT`):

   ```bash
   TRDD_UUID=$(python3 -c "import uuid; print(uuid.uuid4())")
   SHORT=${TRDD_UUID:0:8}
   TS=$(date +%Y%m%d_%H%M%S%z)        # filename timestamp (compact, Windows-safe)
   ISO=$(date +%Y-%m-%dT%H:%M:%S%z)   # frontmatter datetime (ISO 8601 + TZ)
   ZONE=tasks                         # 'tasks' for Tier 0; 'proposals' for Tier 1/2/3
   FN="design/$ZONE/TRDD-$TS-$SHORT-<short-slug>.md"
   ```

3. Write the frontmatter + body (canonical skeleton in the scripts-usage
   reference). Mandatory fields: `trdd-id`, `title` (no colon), `column`
   (`planned` for Tier 0 in tasks/, `proposal` for proposals/), `created`,
   `updated` (same ISO in both). For a proposal add `approval-tier: N` and end
   the body with an empty `## Approval log` placeholder. Keep the body
   **self-contained** (a cross-team implementer shares none of your context).
   Add a `## ⏵ STATE` head block if the TRDD will span more than one session.

4. Create a todo-list entry carrying the `TRDD-<8hex>` reference, then commit by
   name (NEVER `git add -A`):

   ```bash
   git add "$FN" && git commit -m "docs: add TRDD-$SHORT — <summary>"
   ```

## Output

A new TRDD file in the correct zone, git-committed, plus the TRDD id + commit
hash to report to the user.

## Examples

<example>
A MEMBER must add an e2e test for an already-approved feature (a DERIVED EHT).
→ Tier 0: author directly in design/tasks/ as `column: planned`, parent-trdd set, commit, proceed.
</example>

<example>
An agent wants to change the release pipeline.
→ Tier 2: author in design/proposals/ with `approval-tier: 2`, then keep working;
  the MANAGER approves it later via /ama-proposal-approvals.
</example>

## Scope

Authors a NEW TRDD (Tier 0 → tasks/; Tier 1/2/3 → proposals/). Does not approve
proposals (`ama-proposal-approvals`), edit an existing TRDD (`ama-trdd-update`),
or move columns (`ama-trdd-transition`).

## Error Handling

On non-zero exit the message is on STDERR; the agent adjusts. Exit 2 = a
precondition failed (PRRD/TRDD missing — run the bootstrap / `--init`); exit 3 =
rule/TRDD not found (check the id/number). If `resolve_pillar_scripts.sh` exits
1, the ai-maestro-plugin base is not installed — set
`$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base. This skill never mutates on
a partial failure.

## Resources

- `${CLAUDE_PLUGIN_ROOT}/rules/trdd-design-tasks.md` — canonical TRDD v2 format, filename, STATE block, the report→TRDD rule (auto-installed each session).
- [../ama-trdd-transition/references/trdd-frontmatter-schema.md](../ama-trdd-transition/references/trdd-frontmatter-schema.md) — field-by-field frontmatter schema.
  > Contents · Schema invariants (grep-friendliness) · Field schema · 1. Identity (mandatory on every TRDD) · 2. Ownership · 3. Classification · 4. Relationships · 5. Delivery · 6. Verification requirements · 7. Impact · 8. Runtime evidence · 9. Audit-flow · 10. External · Type forms · Schema extension · Validation · Migration from v1 · Anti-patterns
- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md) — the canonical TRDD skeleton + bootstrap_design.py + per-role examples.
  > Contents · resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
- [../ama-trdd-transition/references/approval-tiers-and-zones.md](../ama-trdd-transition/references/approval-tiers-and-zones.md) — the four zones + tier ladder + the objective tier-floor (which zone to write into).
  > Contents · A. The four design zones · B. The `proposal → planned` lifecycle · C. The four-tier approval ladder · The objective tier-floor (mechanical, greppable) · Asynchronous enforcement (never block) · D. Single-writer-per-domain (collision avoidance) · Batch approval syntax (the fast path)
