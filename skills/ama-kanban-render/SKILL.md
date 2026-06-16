---
name: ama-kanban-render
description: "Render the project's design/spec kanban board as a READ-ONLY view over the TRDD pile (the TRDD files under design/ ARE the board) — the full board, just the RED (blocked) column with priority ranking, one column, grouped by assignee, or as JSON; also drift-check. Allowed for every role. Use when you want to see what work exists and what column each TRDD is in before acting, or to check what's blocked. Trigger with /ama-kanban-render, 'show the kanban', or 'what's blocked'. The board is READ-ONLY here; column moves are done via /ama-trdd-transition."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(kanban.py:*), Bash(resolve_pillar_scripts.sh:*), Read, Grep, Glob"
disallowed-tools: "Edit, Write, NotebookEdit"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-kanban-render — render the board (READ-ONLY)

## Overview

`ama-kanban-render` renders the design/spec kanban as a VIEW over the TRDD files
under `design/` — the TRDDs ARE the board, `kanban.py` only reads them. This
skill is read-only **by construction**: its `disallowed-tools` drop Edit / Write
/ NotebookEdit, so it cannot mutate a TRDD even by accident. Column moves are a
separate, gated operation (`ama-trdd-transition`).

## Permission (this skill's matrix row)

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| **read/render kanban** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Rendering is allowed for **every** role — including the read-only roles. Nobody
mutates a TRDD through this skill (see `ama-trdd-transition` for moves, which
enforce the transition matrix).

## Recall before acting

Render the board (and recall related TRDDs) BEFORE starting work — "what already
exists, what column is it in, what's blocking the red lane?". The blocked (RED)
column is the chief source of delays; `--red` surfaces it with its priority
ranking.

## Prerequisites

- The project has a `design/` tree (PRRD at `design/requirements/PRRD.md` and/or
  TRDDs under `design/tasks/`) — the TRDD files ARE the board this skill renders.
  Bootstrap with `bootstrap_design.py` / `get-prrd.py --init` if absent.
- Python 3.10+ on PATH. The pillar scripts live at
  `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` and are resolved at runtime via
  `resolve_pillar_scripts.sh` (works from the core plugin OR any role plugin).
- You know your governance ROLE (MANAGER / ORCH / ARCH / INT / COS / MEMBER /
  AUTONOMOUS / MAINTAINER) — this skill's permission matrix is keyed on it.

## Instructions

1. Resolve the pillar-scripts directory:

   ```bash
   DIR="$(sh "$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/resolve_pillar_scripts.sh")" || exit 1
   ```

2. Render (NEVER mutates a TRDD):

   ```bash
   python3 "$DIR/kanban.py"                  # full board, compact
   python3 "$DIR/kanban.py" --view wide      # wide layout
   python3 "$DIR/kanban.py" --red            # blocked column + priority ranking
   python3 "$DIR/kanban.py" --column dev     # just one column
   python3 "$DIR/kanban.py" --group-by assignee
   python3 "$DIR/kanban.py" --check-drift    # drift signals (stale updated:, etc.)
   python3 "$DIR/kanban.py" --json           # machine-readable
   ```

## Output

The rendered board (or JSON) on STDOUT; errors on STDERR; exit 0 on success.

## Examples

<example>
User: what's blocked right now?
→ resolve DIR, `kanban.py --red` → the RED column with each TRDD's blockers + priority.
</example>

<example>
User: show me everything in testing
→ `kanban.py --column testing`.
</example>

## Scope

READ-ONLY (enforced by `disallowed-tools`). To MOVE a TRDD between columns use
`ama-trdd-transition` (which enforces who-can-move-what). To find a specific TRDD
use `ama-trdd-find`.

## Error Handling

On non-zero exit the message is on STDERR; the agent adjusts. Exit 2 = a
precondition failed (PRRD/TRDD missing — run the bootstrap / `--init`); exit 3 =
rule/TRDD not found (check the id/number). If `resolve_pillar_scripts.sh` exits
1, the ai-maestro-plugin base is not installed — set
`$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base. This skill never mutates on
a partial failure.

## Resources

- [../ama-trdd-transition/references/column-transitions.md](../ama-trdd-transition/references/column-transitions.md) — the transition matrix + red-column auto-priority ranking + drift signals.
  > Contents · Reading the table · Master matrix · Pre-PR gate (dialog loop c) · INTEGRATOR owns the `→ complete` flip · Reverse moves NOT in the matrix · EHT gate for `complete` · Drift signals · Red column auto-priority ranking · AMP routing — who hears about each transition · Authority enforcement
- `/ama-trdd-transition` — the gated column-move skill.
- `/ama-trdd-find` — find a specific TRDD by id/column/assignee.
- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md) — full kanban.py usage + exit codes.
  > Contents · resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
