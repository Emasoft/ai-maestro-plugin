---
name: ama-trdd-update
description: "Edit an existing TRDD's body or non-column frontmatter as work proceeds — bump updated:, append implementation-commits/ci-runs/test results, write the STATE block, add review notes or post-mortems, set labels/priority/severity. Only the TRDD's current-owner edits its body; coordination fields (column, assignee) are moved by their owners. Use when recording progress on a task you own — NOT for column moves (/ama-trdd-transition) and NOT for a terminal frozen TRDD. Trigger with /ama-trdd-update, 'update the TRDD', or 'record the commit on TRDD X'. Authoring is /ama-trdd-write, finding /ama-trdd-find."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(date:*), Bash(git:*), Bash(findtrdd.py:*), Bash(resolve_pillar_scripts.sh:*), Read, Write, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-trdd-update — edit an existing TRDD

## Overview

`ama-trdd-update` edits a TRDD that already exists — its prose body and its
runtime-evidence / metadata frontmatter fields — as work proceeds. It does NOT
move the `column:` (that is `ama-trdd-transition`, which enforces who-can-move-
what) and it does NOT mutate a TRDD that has reached a terminal column.

## Permission (this skill's matrix row)

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| **edit TRDD body / metadata** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (own) | ✅ | ✅ |

Editing rules (self-check):

- **Body** — only the TRDD's `current-owner:` mutates the body. If you are not
  the owner, either take a documented write-lock (set `current-owner:` to your
  session, recorded) or hand off to the owner.
- **Coordination fields** (`column:`, `assignee:`) are NOT edited here — MANAGER
  / ORCHESTRATOR move those, and column moves go through `ama-trdd-transition`.
- **Runtime-evidence fields** (`implementation-commits:`, `ci-runs:`,
  `last-test-result:`, `test-failures:`, `feature-branch:`) are write-only logs
  the assignee / test-runner / INTEGRATOR append — exempt, no approval.
- **Terminal TRDDs** (`completed` / `failed` / `superseded` / `published` /
  `live`) — body is FROZEN. Only `updated:` and (for `superseded`) the
  `superseded-by:` field may change. New work = a new TRDD (`ama-trdd-write`).

**Always bump `updated:`** on EVERY edit (not just column changes), to a fresh
`date +%Y-%m-%dT%H:%M:%S%z` — the kanban "last touched" sort depends on it.

## Prerequisites

- The project has a `design/` tree (PRRD at `design/requirements/PRRD.md` and/or
  TRDDs under `design/tasks/`) holding the TRDD to edit. Bootstrap with
  `bootstrap_design.py` / `get-prrd.py --init` if absent.
- Python 3.10+ on PATH. The pillar scripts live at
  `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` and are resolved at runtime via
  `resolve_pillar_scripts.sh` (works from the core plugin OR any role plugin).
- You know your governance ROLE (MANAGER / ORCH / ARCH / INT / COS / MEMBER /
  AUTONOMOUS / MAINTAINER) — this skill's permission matrix is keyed on it.

## Instructions

1. Find the TRDD (re-read it before editing — never trust stale memory):

   ```bash
   DIR="$(sh "$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/resolve_pillar_scripts.sh")" || exit 1
   python3 "$DIR/findtrdd.py" 9a8aba94      # land on the file
   ```

2. Re-read the file, confirm it is NOT terminal, then Edit:
   - Append a SHA to `implementation-commits:` as code lands.
   - Write `last-test-result:` / `last-test-at:` / bump `test-failures:`.
   - Add review notes / a failure post-mortem to the body.
   - Keep / refresh the `## ⏵ STATE — READ THIS FIRST ON RESUME` block as the
     single source of truth (mandatory once the TRDD spans >1 session).
   - **Bump `updated:`** to a fresh ISO datetime.

3. Validate the frontmatter still satisfies the grep-first invariants, then
   commit by name:

   ```bash
   python3 "$DIR/findtrdd.py" --validate "$FN"
   git add "$FN" && git commit -m "docs(trdd): update TRDD-<short> — <what changed>"
   ```

## Output

The edited, re-validated, committed TRDD. A one-line summary of what changed.

## Examples

<example>
The PR for TRDD-9a8aba94 merged; record the SHA.
→ find the file, append the SHA to `implementation-commits:`, bump `updated:`, commit.
</example>

<example>
A multi-session TRDD needs its STATE block refreshed before handoff.
→ re-read the TRDD, rewrite the `## ⏵ STATE` block with current state + NEXT ACTION + superseded facts, bump `updated:`.
</example>

## Scope

Edits an existing, non-terminal TRDD's body + evidence/metadata fields. NOT
column moves (`ama-trdd-transition`), NOT authoring (`ama-trdd-write`), NOT
terminal-body edits (frozen).

## Error Handling

On non-zero exit the message is on STDERR; the agent adjusts. Exit 2 = a
precondition failed (PRRD/TRDD missing — run the bootstrap / `--init`); exit 3 =
rule/TRDD not found (check the id/number). If `resolve_pillar_scripts.sh` exits
1, the ai-maestro-plugin base is not installed — set
`$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base. This skill never mutates on
a partial failure.

## Resources

- `${CLAUDE_PLUGIN_ROOT}/rules/trdd-design-tasks.md` — canonical TRDD v2 format + the STATE-block + terminal-freeze rules (auto-installed each session).
- [../ama-trdd-transition/references/trdd-frontmatter-schema.md](../ama-trdd-transition/references/trdd-frontmatter-schema.md) — which fields are mutable, their types/defaults, the grep-first invariants.
  > Contents · Schema invariants (grep-friendliness) · Field schema · 1. Identity (mandatory on every TRDD) · 2. Ownership · 3. Classification · 4. Relationships · 5. Delivery · 6. Verification requirements · 7. Impact · 8. Runtime evidence · 9. Audit-flow · 10. External · Type forms · Schema extension · Validation · Migration from v1 · Anti-patterns
- `/ama-trdd-transition` — the gated column-move skill.
- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md) — findtrdd.py + --validate usage.
  > Contents · resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
