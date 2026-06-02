---
name: prrd-trdd-kanban
description: "Universal PRRD / TRDD / Kanban workflow skill. Use when reading or mutating project rules (PRRD), authoring/finding/editing task design documents (TRDDs), or rendering the kanban board. Trigger with /prrd-trdd-kanban or whenever a project under design/ needs structured task or rule operations."
allowed-tools: "Bash(python3:*), Bash(get-prrd.py:*), Bash(prrd-edit.py:*), Bash(findprrd.py:*), Bash(findtrdd.py:*), Bash(kanban.py:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

## Overview

This is the **universal** PRRD / TRDD / Kanban skill, bundled with the
ai-maestro-plugin (umbrella) so every role-plugin (AMAMA, ORCH, ARCH,
INT, MEM, COS, AUTO, MAINT) inherits it. Each role-plugin layers a
role-specific skill (`<prefix>-prrd-trdd-kanban`) on top, describing
the columns and transitions that role owns. THIS skill describes the
mechanics common to all roles.

The three ingredients of the workflow:

- **PRRD** — single authoritative rules document at
  `<project-root>/design/requirements/PRRD.md`. MANAGER-mutable for
  silver rules, USER-only for golden rules. Citation form
  `PRRD G64.134` (full version always, G/S is an informative
  annotation).
- **TRDD** — atomic task design documents at
  `<project-root>/design/tasks/TRDD-<timestamp>-<uid8>-<slug>.md`. Each
  TRDD has rich YAML frontmatter and a markdown body. Short reference:
  `TRDD-9a8aba94` or `#9a8aba94`.
- **Kanban** — 17 columns rendered as a view over the TRDD pile (NOT a
  separate file; the TRDDs ARE the kanban). Special focus on the
  **blocked column** (RED) — the fundamental source of delays, owned
  by ORCHESTRATOR.

## Prerequisites

- Project tree has `design/requirements/PRRD.md` and
  `design/tasks/TRDD-*.md` (or be ready to bootstrap them).
- Python 3.10+ available on PATH.
- Scripts shipped at `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/`.
  Convenience symlinks usually live at `~/.local/bin/`.

## Instructions

Use the tools below. Every script accepts `--help`.

### Reading PRRD rules

```bash
# Latest version of rule 70
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/get-prrd.py 70

# Specific version
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/get-prrd.py 70.3

# Formatted citation
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/get-prrd.py --cite 70.3

# List all silver rules
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/get-prrd.py --list --kind silver

# JSON for tooling
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/get-prrd.py --json 70.3
```

The letter (G/S) in a reference is IGNORED on input. Rules are
identified by number alone. The letter is for the human reader.

### Mutating PRRD (MANAGER-only for direct mutation)

```bash
# MANAGER adds a silver rule
prrd-edit.py add silver "Use AID auth for all API calls"

# MANAGER revises a silver rule (bumps version)
prrd-edit.py revise 70 "new rule text"

# MANAGER deletes a silver rule (number retires forever)
prrd-edit.py delete 70

# USER promotes silver to golden
prrd-edit.py --user promote 70

# USER demotes golden to silver
prrd-edit.py --user demote 70

# Any agent files a proposal
prrd-edit.py propose silver "proposed text" --target 70 \
            --proposed-by my-session --routed-via cos-myteam
```

`--user` bypasses the MANAGER auth check (use when working solo without
AI Maestro). Non-MANAGER attempts to mutate without `--user` are
refused; agents must `propose` instead.

### Finding TRDDs

```bash
# By short UUID prefix
findtrdd.py 9a8aba94

# Filter by column
findtrdd.py --column blocked

# Filter by assignee
findtrdd.py --assignee alice

# Reverse-dep: what's blocked by this TRDD
findtrdd.py --blocked-by 9a8aba94

# Citation-aware: which TRDDs cite PRRD rule 64
findtrdd.py --relevant-rule 64

# SQL-ish where clause
findtrdd.py --where "column=dev AND priority<3"

# Free-text search
findtrdd.py --grep "auth"

# Compact table view
findtrdd.py --format table

# Validate a single TRDD
findtrdd.py --validate design/tasks/TRDD-...md
```

### Kanban view

```bash
# Full board (compact)
kanban.py

# Wide view with more detail per card
kanban.py --view wide

# Just the red (blocked) column with priority ranking
kanban.py --red

# Only one column
kanban.py --column dev

# Group by assignee
kanban.py --group-by assignee

# Show drift signals (block-down, block-up, eht-gate, etc.)
kanban.py --check-drift

# JSON for tooling
kanban.py --json
```

The kanban renderer is **read-only**. It NEVER mutates a TRDD. Column
moves are performed by editing the TRDD's `column:` frontmatter field
(per [column-transitions.md](references/column-transitions.md)).

### Authoring a new TRDD

Manually with an editor, OR via the canonical skeleton:

```bash
# Generate UUID + timestamp
UID=$(python3 -c "import uuid; print(uuid.uuid4())")
SHORT=${UID:0:8}
TS=$(date +%Y%m%d_%H%M%S%z)
ISO=$(date +%Y-%m-%dT%H:%M:%S%z)
FN="design/tasks/TRDD-$TS-$SHORT-<short-slug>.md"

cat > "$FN" <<EOF
---
trdd-id: $UID
title: <one-line title>
column: backburner
created: $ISO
updated: $ISO
current-owner: <session-name>
task-type: feature
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
target-branch: main
test-requirements: []
runtime-targets: [macos]
impacts: []
attempts: 0
test-failures: 0
last-test-result: not-run
implementation-commits: []
ci-runs: []
---

# <title>

<prose body>
EOF
```

The minimal mandatory fields are: `trdd-id`, `title`, `column`,
`created`, `updated`. All other fields take documented defaults from
[trdd-frontmatter-schema.md](references/trdd-frontmatter-schema.md).

## Output

- `get-prrd.py` — single rule text (or `--json` / `--cite` form)
- `prrd-edit.py` — one-line confirmation; optional mirror-sync warning
- `findprrd.py` — list of rules matching a filter
- `findtrdd.py` — list of file paths (or `--format table|json`)
- `kanban.py` — multi-column board (or `--json` for tooling)

All scripts write to STDOUT; errors to STDERR. Exit code 0 on success.

## Error Handling

| Exit code | Meaning |
|---|---|
| 0 | success |
| 1 | usage / generic error |
| 2 | file / state precondition failed (e.g. PRRD missing, file exists) |
| 3 | not found (rule, TRDD) |
| 4 | authority refused (e.g. MANAGER-only without `--user`) |

If a script fails, the message goes to STDERR. Agents read the message
and adjust (e.g. `--user` if running solo, file a proposal if not
MANAGER, etc.).

## Examples

```text
# AMAMA promotes a TRDD from backburner to todo
findtrdd.py 9a8aba94                    # find the file
# (edit frontmatter: column: todo, bump updated)

# ORCH checks the red column priority
kanban.py --red

# ARCHITECT looks up the rule a TRDD cites
get-prrd.py --cite 64.134

# INTEGRATOR validates a TRDD before deploying
findtrdd.py --validate design/tasks/TRDD-9a8aba94-*.md

# MEMBER files a proposal to revise rule S70
prrd-edit.py propose silver "new wording" --target 70 \
            --proposed-by member-frontend --routed-via cos-website
```

## MANAGER approval discipline

**MANAGER approval is the DEFAULT for every significant step.** The
[references/exempt-operations.md](references/exempt-operations.md)
document lists the EXEMPT categories (mechanical transitions, TRDD
intake/triage, read-only ops, within-team coordination, runtime
evidence). Anything NOT on the exempt list is non-exempt — the agent
MUST request MANAGER approval (via COS for team-internal agents) before
performing the transition. Conservative default: when unsure, treat
as non-exempt. See [exempt-operations.md](references/exempt-operations.md)
for the canonical list, approval-request AMP template, and the
`## Approval log` body-section format.

## GitHub authorship self-identification (PRRD G1 / governance R22)

All AI Maestro agents share the single human-owner GitHub identity
(the owner's `gh` CLI auth), so a comment from "the orchestrator"
and one from "the maintainer" both appear as the same `@owner`
account. To prevent confusion, **every agent that writes to GitHub
MUST begin the body with a one-line self-identification** of which
agent/role/plugin authored it. Recommended leading line:

```
_Posted by the Claude developing **<plugin-or-role>** (via the shared @owner gh auth)._
```

Applies to issues, issue comments, PRs, PR comments, PR reviews,
discussions, and release notes. Commit messages SHOULD carry an
`Agent: <plugin-slug>` trailer (the plugin's stable package slug,
e.g. `Agent: ai-maestro-maintainer-agent` — greppable ecosystem-wide
and rename-surviving). This is golden rule `G1.1` in each project's
PRRD and ecosystem governance rule R22.

## Resources

- [references/prrd-design-rules.md](references/prrd-design-rules.md) —
  authoritative PRRD format, citation grammar, promote/demote rules
- [references/trdd-design-tasks.md](references/trdd-design-tasks.md) —
  authoritative TRDD format (v2), filename rules, status enum, STATE
  block
- [references/column-transitions.md](references/column-transitions.md) —
  who can move what from where to where, AMP broadcasts per transition
- [references/trdd-frontmatter-schema.md](references/trdd-frontmatter-schema.md) —
  field-by-field frontmatter spec with types, defaults, validation
- [references/exempt-operations.md](references/exempt-operations.md) —
  MANAGER-approval default + EXEMPT category list (mechanical
  transitions, intake, read-only, within-team coordination, runtime
  evidence)
- [references/cos-delegation-authority.md](references/cos-delegation-authority.md) —
  COS two-tier filter (COS-AUTONOMOUS vs COS-ESCALATE): which team
  requests the COS decides itself vs forwards to MANAGER. The team-boundary
  filter that sits one layer below exempt-operations.md (the
  governance-boundary filter)
- `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` — the five canonical
  scripts (`get-prrd.py`, `prrd-edit.py`, `findprrd.py`, `findtrdd.py`,
  `kanban.py`) plus the shared library (`prrd_lib.py`)

For role-specific responsibilities, see the per-role layer skill:
`amama-prrd-trdd-kanban`, `amoa-prrd-trdd-kanban`,
`amaa-prrd-trdd-kanban`, `amia-prrd-trdd-kanban`,
`ampa-prrd-trdd-kanban`, `amcos-prrd-trdd-kanban`,
`ai-maestro-autonomous-prrd-trdd-kanban`, or
`maintainer-prrd-trdd-kanban`.
