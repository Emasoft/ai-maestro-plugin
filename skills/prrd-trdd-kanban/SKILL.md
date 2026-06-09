---
name: prrd-trdd-kanban
description: "Universal PRRD / TRDD / Kanban workflow skill. Use when reading or mutating project rules (PRRD), authoring/finding/editing task design documents (TRDDs), or rendering the kanban board. Trigger with /prrd-trdd-kanban or whenever a project under design/ needs structured task or rule operations."
allowed-tools: "Bash(python3:*), Bash(get-prrd.py:*), Bash(prrd-edit.py:*), Bash(findprrd.py:*), Bash(findtrdd.py:*), Bash(kanban.py:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.1.0"
---

## Overview

The **universal** PRRD / TRDD / Kanban skill, bundled with
ai-maestro-plugin so every role-plugin inherits it. Each role-plugin
layers a `<prefix>-prrd-trdd-kanban` skill on top; THIS skill is the
common mechanics. Three ingredients:

- **PRRD** — one authoritative rules doc at
  `design/requirements/PRRD.md`. Silver = MANAGER-mutable, golden =
  USER-only. Citation `PRRD G64.134` (lookup by bare number; G/S is
  annotation).
- **TRDD** — atomic task docs at
  `design/tasks/TRDD-<ts>-<uid8>-<slug>.md` (YAML frontmatter + body).
  Short ref `TRDD-9a8aba94`.
- **Kanban** — 17 columns rendered as a VIEW over the TRDD pile (the
  TRDDs ARE the kanban). The **blocked column** (RED) is the chief
  source of delays, owned by ORCHESTRATOR.

## Prerequisites

- Project has `design/requirements/PRRD.md` + `design/tasks/TRDD-*.md`
  (or be ready to bootstrap them via `get-prrd.py --init`).
- Python 3.10+ on PATH. Scripts at
  `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/`.

## Instructions

Five scripts do the work (full usage + examples:
[scripts-usage.md](references/scripts-usage.md)):

1. `get-prrd.py` — read a PRRD rule by number (`70`, `70.3`, `--cite`, `--list`, `--json`, `--init`).
2. `prrd-edit.py` — mutate PRRD: add/revise/delete/promote/demote/propose (MANAGER-only; `--user` for solo).
3. `findprrd.py` — search rules (`--kind`/`--grep`/`--cited-in`/`--unused`/`--count`).
4. `findtrdd.py` — find TRDDs by uuid/column/assignee/blocked-by/relevant-rule/grep/`--where`; `--validate`.
5. `kanban.py` — render the board (`--red`/`--column`/`--group-by`/`--check-drift`/`--json`); READ-ONLY.

Column moves are done by editing a TRDD's `column:` field, not a script
(see [column-transitions.md](references/column-transitions.md)). TRDD
skeleton: [scripts-usage.md](references/scripts-usage.md).

## Output

Each script writes results to STDOUT, errors to STDERR, exit 0 on
success. Exit-code table in [scripts-usage.md](references/scripts-usage.md).

## Error Handling

On non-zero exit, the message is on STDERR; the agent adjusts (`--user`
if solo, `propose` if not MANAGER, `--init` if PRRD missing). Full exit
table in [scripts-usage.md](references/scripts-usage.md).

## Examples

See [scripts-usage.md](references/scripts-usage.md) "Per-role quick
examples" for AMAMA / ORCH / ARCH / INT / MEM one-liners.

## MANAGER approval discipline

MANAGER approval is the DEFAULT for every significant step;
[exempt-operations.md](references/exempt-operations.md) lists the
EXEMPT categories, and the COS filters first via
[cos-delegation-authority.md](references/cos-delegation-authority.md).
Conservative default: unsure → non-exempt (request approval).

## GitHub authorship self-identification (PRRD G1 / governance R22)

All agents share the owner's single `gh` identity, so every agent
writing to GitHub MUST begin the body with a one-line self-id —
`_Posted by the Claude developing **<plugin-or-role>** (via the shared
@owner gh auth)._` — and commits SHOULD carry an `Agent: <plugin-slug>`
trailer. Golden rule `G1.1` in each PRRD; ecosystem governance R22.

## Resources

- [references/scripts-usage.md](references/scripts-usage.md) — full script usage + TRDD skeleton + exit codes + per-role examples
  > get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules
  > · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
- [references/prrd-design-rules.md](references/prrd-design-rules.md) — PRRD format, citation grammar, promote/demote, golden/silver, G1 baseline
  > Recommended baseline golden rule G1 — GitHub authorship self-identification · Location and shape · File anatomy
  > · Rule identity, versioning, and promote/demote · Citation grammar · Mutation rules · Proposal queue · Scripts · Cross-reference with TRDDs
  > · Mirror discipline (§0 pattern) · Bootstrap — projects without a PRRD · Grep cheat-sheet · Anti-patterns · Why this exists
  > · Does NOT apply to · Migration from no-PRRD projects
- [references/trdd-design-tasks.md](references/trdd-design-tasks.md) — TRDD v2 format, filename, column enum, NPT/EHT, STATE block, migration
  > The rule · What's new in v2 · Location · Filename format · Frontmatter — the v2 spec · Column enum (the 14-stage kanban + blocked)
  > · Design-column 1→N split / N→1 group semantics · NPT vs EHT semantics · The 8-char hash reference syntax
  > · STATE head section (mandatory once a TRDD spans >1 session) · Reports are evidence; decisions become TRDDs · Todo list cross-reference
  > · Workflow · Migration from v1 · Grep cheat-sheet (extended) · Why this exists · Anti-patterns · Does NOT apply to
- [references/trdd-frontmatter-schema.md](references/trdd-frontmatter-schema.md) — field-by-field frontmatter schema with types/defaults/validation
  > Schema invariants (grep-friendliness) · Field schema · Type forms · Schema extension · Validation · Migration from v1 · Anti-patterns
- [references/column-transitions.md](references/column-transitions.md) — transition matrix, AMP broadcasts, red-column priority, drift signals
  > Reading the table · Master matrix · Reverse moves NOT in the matrix · EHT gate for `complete` · Drift signals
  > · Red column auto-priority ranking · AMP routing — who hears about each transition · Authority enforcement
- [references/exempt-operations.md](references/exempt-operations.md) — MANAGER-approval default + EXEMPT categories + approval-request template + Approval log
  > EXEMPT operations (no MANAGER approval required) · NON-EXEMPT operations (MANAGER approval REQUIRED) · Approval-request AMP message template
  > · MANAGER's approval / rejection reply · Recording the decision · Crisis cross-reference · R15 compatibility notes · When to revise this list
- [references/cos-delegation-authority.md](references/cos-delegation-authority.md) — COS two-tier filter (autonomous vs escalate), consolidation, presence chain
  > The two-tier model · How escalation composes with presence (the full chain) · COS-AUTONOMOUS — the COS decides, no upstream
  > · COS-ESCALATE — forward to MANAGER · Consolidation — the COS batches, it doesn't flood · The COS escalation message (to MANAGER)
  > · User-presence — where it lives, and the janitor fallback · Why this exists · Relationship to exempt-operations.md
- `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` — the 5 scripts + `prrd_lib.py`

Role layers: `amama-` `amoa-` `amaa-` `amia-` `ampa-` `amcos-` `ai-maestro-autonomous-` `maintainer-prrd-trdd-kanban`.
