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
- [references/prrd-design-rules.md](references/prrd-design-rules.md) — PRRD format, citation grammar, promote/demote, golden/silver, G1 baseline
- [references/trdd-design-tasks.md](references/trdd-design-tasks.md) — TRDD v2 format, filename, column enum, NPT/EHT, STATE block, migration
- [references/trdd-frontmatter-schema.md](references/trdd-frontmatter-schema.md) — field-by-field frontmatter schema with types/defaults/validation
- [references/column-transitions.md](references/column-transitions.md) — transition matrix, AMP broadcasts, red-column priority, drift signals
- [references/exempt-operations.md](references/exempt-operations.md) — MANAGER-approval default + EXEMPT categories + approval-request template + Approval log
- [references/cos-delegation-authority.md](references/cos-delegation-authority.md) — COS two-tier filter (autonomous vs escalate), consolidation, presence chain
- `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` — the 5 scripts + `prrd_lib.py`

Role layers: `amama-` `amoa-` `amaa-` `amia-` `ampa-` `amcos-` `ai-maestro-autonomous-` `maintainer-prrd-trdd-kanban`.
