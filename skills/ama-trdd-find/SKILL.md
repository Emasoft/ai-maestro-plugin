---
name: ama-trdd-find
description: "Find TRDD task-design documents under design/ — by 8-char id (TRDD-9a8aba94), column, assignee, blocked-by, cited PRRD rule, a SQL-ish --where filter, or free-text; also --validate a TRDD's frontmatter. Read-only, allowed for every role. Use when locating a task spec before working on it, resuming a TRDD from a todo-list id, or auditing the backlog. Trigger with /ama-trdd-find, 'find the TRDD for X', or 'which TRDDs are blocked'. Authoring is /ama-trdd-write, editing /ama-trdd-update, column moves /ama-trdd-transition."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(findtrdd.py:*), Bash(resolve_pillar_scripts.sh:*), Read, Grep, Glob"
disallowed-tools: "Edit, Write, NotebookEdit"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-trdd-find — find TRDDs (READ-ONLY)

## Overview

`ama-trdd-find` locates TRDD files in `design/` by id, column, assignee,
blocked-by, cited rule, a `--where` filter, or free-text — and validates a
TRDD's frontmatter. Read-only by construction (`disallowed-tools` drop Edit /
Write), so it can search but never mutate.

## Permission (this skill's matrix row)

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| **find/read TRDD** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Finding is allowed for **every** role — no gate.

## Prerequisites

- The project has a `design/` tree (PRRD at `design/requirements/PRRD.md` and/or
  TRDDs under `design/tasks/`) to search. Bootstrap with `bootstrap_design.py` /
  `get-prrd.py --init` if absent.
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

2. Find:

   ```bash
   python3 "$DIR/findtrdd.py" 9a8aba94                # by 8-char UUID prefix (the canonical short ref)
   python3 "$DIR/findtrdd.py" --column blocked        # by column
   python3 "$DIR/findtrdd.py" --assignee alice        # by assignee session name
   python3 "$DIR/findtrdd.py" --blocked-by 9a8aba94   # reverse-dep: all TRDDs this one blocks
   python3 "$DIR/findtrdd.py" --relevant-rule 64      # all TRDDs that cite PRRD rule 64
   python3 "$DIR/findtrdd.py" --where "column=dev AND priority<3"
   python3 "$DIR/findtrdd.py" --grep "auth"           # regex over title + body
   python3 "$DIR/findtrdd.py" --format table          # paths | json | table
   python3 "$DIR/findtrdd.py" --validate design/tasks/TRDD-9a8aba94-*.md   # frontmatter check
   ```

   Resolving a TRDD from a todo-list reference: the todo entry carries
   `TRDD-<8hex>`; pass the bare 8 hex to `findtrdd.py` to land on the file.

## Output

Matching TRDD paths / table / JSON on STDOUT; errors on STDERR; exit 0 on
success. `--validate` exits non-zero if the frontmatter violates the schema.

## Examples

<example>
User: resume the task TRDD-9a8aba94 from my todo list
→ resolve DIR, `findtrdd.py 9a8aba94` → the file path; read it top-down (STATE block first).
</example>

<example>
User: what would changing rule 27 affect?
→ `findtrdd.py --relevant-rule 27` → every TRDD that cites rule 27.
</example>

## Scope

READ-ONLY (enforced by `disallowed-tools`). Author a TRDD: `ama-trdd-write`.
Edit a TRDD's body/fields: `ama-trdd-update`. Move columns: `ama-trdd-transition`.

## Error Handling

On non-zero exit the message is on STDERR; the agent adjusts. Exit 2 = a
precondition failed (PRRD/TRDD missing — run the bootstrap / `--init`); exit 3 =
rule/TRDD not found (check the id/number). If `resolve_pillar_scripts.sh` exits
1, the ai-maestro-plugin base is not installed — set
`$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base. This skill never mutates on
a partial failure.

## Resources

- `${CLAUDE_PLUGIN_ROOT}/rules/trdd-design-tasks.md` — canonical TRDD v2 format + the 8-char hash ref syntax + grep cheat-sheet (auto-installed each session).
- [../ama-trdd-transition/references/trdd-frontmatter-schema.md](../ama-trdd-transition/references/trdd-frontmatter-schema.md) — field-by-field schema (what `--validate` checks).
  > Contents · Schema invariants (grep-friendliness) · Field schema · 1. Identity (mandatory on every TRDD) · 2. Ownership · 3. Classification · 4. Relationships · 5. Delivery · 6. Verification requirements · 7. Impact · 8. Runtime evidence · 9. Audit-flow · 10. External · Type forms · Schema extension · Validation · Migration from v1 · Anti-patterns
- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md) — full findtrdd.py usage + exit codes.
  > Contents · resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
