---
name: ama-trdd-write
user-invocable: true
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
**The zone you write into is decided by `min-approval-requirement:`** — the TITLE
that must approve the card (self-classify). The ladder:

```
none  <  orchestrator  <  chief-of-staff  <  manager  <  user
```

- **`none` (default, and what an ABSENT field means)** — a DERIVED task (an NPT/EHT
  of work you already own) or a task fully inside your own scope, reversible &
  local, no baseline deviation → author directly in `design/tasks/` with
  `column: planned`. Proceed immediately.
- **Any higher rung** → author in `design/proposals/` with `column: proposal` and
  `min-approval-requirement: <title>`; then keep working — approval is asynchronous
  (`ama-proposal-approvals` drains it).

**When unsure which rung, escalate one — conservative beats sorry.** Do NOT
reproduce the floor here: read the objective requirement-floor table in the
**ai-maestro DEP overlay `.claude/rules/aimaestro-trdd-approval.md`, §D3** (seeded
into every agent workdir), which is its single canonical home. A floor restated in
a skill is a floor that goes stale.

> **Never write a number.** `approval-tier: N` is retired. Read a legacy card as
> `0→none, 1→chief-of-staff, 2→manager, 3→user` and rewrite it to the title;
> `orchestrator` has no number. `maestro` is a deprecated read-alias for `user`.

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
   # The id IS 8-char UPPERCASE base36 (A-Z0-9) — it is the canonical identifier.
   # There is NO UUID: `trdd-id:` carries this same value, not a longer form.
   # -iname, NOT -name: legacy LOWERCASE ids exist and can NEVER be renamed (they are
   # cited in immutable commit subjects), so a case-sensitive check would report a
   # case-folding id as free and the write would silently overwrite that card.
   # This is permanent, not a migration aid — never "simplify" it back to -name.
   while :; do
     TID=$(LC_ALL=C tr -dc 'A-Z0-9' < /dev/urandom | head -c 8)
     find design ~/.claude/projects/*/design -iname "TRDD-*-${TID}-*.md" 2>/dev/null \
       | grep -q . || break      # grep -q, never `ls <glob>`: an unmatched glob can
   done                          # make ls list the cwd and exit 0 -> infinite loop
   TS=$(date +%Y%m%d_%H%M%S%z)        # filename timestamp (compact, Windows-safe)
   ISO=$(date +%Y-%m-%dT%H:%M:%S%z)   # frontmatter datetime (ISO 8601 + TZ)
   ZONE=tasks                         # 'tasks' for `none`; 'proposals' for any higher rung
   FN="design/$ZONE/TRDD-$TS-$TID-<short-slug>.md"
   ```

3. Write the frontmatter + body (canonical skeleton in the scripts-usage
   reference). Mandatory fields: `trdd-id`, `title` (no colon), `column`
   (`planned` for a `none` card in tasks/, `proposal` for proposals/), `created`,
   `updated` (same ISO in both). For a proposal add
   `min-approval-requirement: <title>` and end
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
→ `manager`: author in design/proposals/ with `min-approval-requirement: manager`,
  then keep working;
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

- `~/.claude/rules/trdd-design-tasks.md` — canonical TRDD v2 format, filename, STATE block, the report→TRDD rule (shipped globally by the ai-maestro-janitor (IND base)).
- [../ama-trdd-transition/references/trdd-frontmatter-schema.md](../ama-trdd-transition/references/trdd-frontmatter-schema.md) — field-by-field frontmatter schema.
  > Contents · Schema invariants (grep-friendliness) · Field schema · 1. Identity (mandatory on every TRDD) · 2. Ownership · 3. Classification · 4. Relationships · 5. Delivery · 6. Verification requirements · 7. Impact · 8. Runtime evidence · 9. Audit-flow · 10. External · Type forms · Schema extension · Validation · Migration from v1 · Anti-patterns
- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md) — the canonical TRDD skeleton + bootstrap_design.py + per-role examples.
  > Contents · resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
- [../ama-trdd-transition/references/approval-tiers-and-zones.md](../ama-trdd-transition/references/approval-tiers-and-zones.md) — the four zones + the `min-approval-requirement:` ladder + the objective requirement-floor (which zone to write into).
  > Contents · A. The four design zones · B. The `proposal → planned` lifecycle · C. The `min-approval-requirement:` field (rung semantics defer to the DEP overlay) · D. Single-writer-per-domain (collision avoidance) · Batch approval syntax (the fast path)
