---
name: team-kanban
user-invocable: false
description: "Manage team kanban boards and tasks. Use when creating, moving, or filtering tasks. Trigger with /team-kanban. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(amp-kanban-list.sh:*), Bash(amp-kanban-create-task.sh:*), Bash(amp-kanban-move.sh:*), Bash(amp-kanban-archive.sh:*), Bash(aimaestro-teams.sh:*), Bash(jq:*), Bash(kanban-sync.py:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

<!-- Decoupled per MANAGER core#11 (TRDD-90c8ad35): task/board examples call the frozen `amp-kanban-*` CLIs (list/create-task/move/archive) + `aimaestro-teams.sh kanban-config`, which resolve the API base + agent identity internally, never the server `/api/*` directly. Residuals with no frozen verb yet (non-status task edits — priority/blockedBy; team `stats`/metrics) are marked DECOUPLE-BLOCKED inline. GitHub-sync (`kanban-sync.py`, `gh`) is OUT OF SCOPE — keep. -->

## Overview

Manage team kanban boards and tasks via the frozen `amp-kanban-*` CLIs + `aimaestro-teams.sh kanban-config`. Create, filter, move, archive tasks; configure columns; sync with GitHub Projects v2.

**Single board — anti-split-brain (team-kanban vs the `ama-*` design board).** Two
kanban surfaces exist and are NOT interchangeable — each is the SINGLE writer of its own
domain, so there is no split brain. THIS skill is the **live team-coordination
board** (server-backed: who is assigned what, presence, real-time task state).
The `ama-kanban-render` / `ama-trdd-transition` skills render and move the
**design/spec board** where the TRDD files
under `design/` ARE the board and `column:` is the source of truth for
design-pipeline state. A team task references a TRDD by `TRDD-<id>` but never
overrides its `column:`. When they appear to disagree: the TRDD file wins for
pipeline state; this server board wins for live assignment/presence.

## Prerequisites

- AI Maestro running (the `amp-kanban-*` / `aimaestro-teams.sh` CLIs resolve the API base + auth internally)
- The `amp-kanban-*` + `aimaestro-teams.sh` CLIs on PATH; `jq` installed
- For GitHub sync: `gh` CLI authenticated, `kanban-sync.py` at `~/.local/bin/`

## Instructions

1. **Identify team**: `aimaestro-teams.sh list | jq .`
2. **Create task**: `amp-kanban-create-task.sh "<title>" [--status S] [--priority N] [--labels "a,b"] [--assignee <id>]`
3. **List/filter**: `amp-kanban-list.sh [--status X] [--assignee Y] [--label Z]`
4. **Move task**: `amp-kanban-move.sh <task-id> <status>`
5. **Archive/delete task**: `amp-kanban-archive.sh <task-id>`
6. **Configure columns**: `aimaestro-teams.sh kanban-config <team-id> --get | --set <columns-json>`
7. **GitHub sync**: `kanban-sync.py link <team-id> <owner/repo> <project-number>` (out of #11 scope — keep)
   <!-- DECOUPLE-BLOCKED ai-maestro#36: non-status task edits (priority / blockedBy dependencies, was `PUT /api/teams/{id}/tasks/{taskId}` with `{priority}`/`{blockedBy}`) and team metrics (was `GET /api/teams/stats`) have no frozen-CLI verb yet — pending a follow-up. `amp-kanban-move` handles status moves; `amp-kanban-create-task` sets initial priority/labels. Do NOT call `/api/*` directly (core#11). -->

### Quick CLI Reference

| Operation | CLI command |
|-----------|-------------|
| List / filter tasks | `amp-kanban-list.sh [--status\|--assignee\|--label\|--task-type]` |
| Create task | `amp-kanban-create-task.sh "<title>" [--status\|--priority\|--labels\|--assignee]` |
| Move task (status) | `amp-kanban-move.sh <task-id> <status>` |
| Archive / delete task | `amp-kanban-archive.sh <task-id>` |
| Kanban config | `aimaestro-teams.sh kanban-config <team-id> --get\|--set <json>` |

Each CLI auto-detects the team from your agent registration (pass `--team <id>` to override).

### Authentication

The `amp-kanban-*` / `aimaestro-teams.sh` CLIs resolve your agent identity + bearer token internally — no `Authorization` / `X-Agent-Id` headers to set by hand. Pass `--id <uuid>` only to act as a specific agent.

### Default Columns

`backlog` / `pending` / `in_progress` / `review` / `completed`

## Output

- Task list: `{"tasks":[...]}` with `isBlocked`, `blocks[]`, `assigneeName`
- Single task: object with id, subject, status, priority, timestamps
- Kanban config: `{"columns":[{id,label,color}]}`

## Error Handling

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | Invalid status | Must match a column ID |
| 400 | Circular dependency | blockedBy creates cycle |
| 403 | Access denied | Agent not team member |
| 404 | Not found | Invalid team/task ID |

## Examples

```
/team-kanban create a task "Fix login bug" with priority 1 in team abc-123
```

Creates task via POST, returns task object with generated ID.

```
/team-kanban show blocked tasks in team abc-123
```

Lists tasks where `isBlocked == true`.

```
/team-kanban link team abc-123 to GitHub project Emasoft/ai-maestro #5
```

Connects team to GitHub Projects v2.

## Checklist

Copy this checklist and track your progress:

- [ ] Identified correct team ID (`aimaestro-teams.sh list`)
- [ ] Confirmed agent identity (CLI resolves it; `--id <uuid>` to act as another agent)
- [ ] Used valid status column IDs
- [ ] Set dependencies without circular refs
- [ ] Configured columns if custom workflow needed

## Resources

- [API Reference](references/api-reference.md)
  - Operations
    - List tasks
    - Create task
    - Update task (status move + fields)
    - Archive / delete task
    - Get kanban config
    - Set kanban config
    - Team stats (residual)
  - Task Lifecycle Examples
  - Task Dependencies
  - Kanban Configuration
  - Velocity and Distribution
  - Extended Task Fields
  - Error Codes
  - Task Storage
  - Available Tailwind Colors
  - Available Lucide Icons
- [GitHub Sync Reference](references/github-sync.md)
  - Prerequisites
  - Setup
  - Link a Team to a GitHub Project
  - Unlink a Team
  - Show Status
  - How It Works
  - Field Mapping
  - Label Taxonomy (AMOA Convention)
  - Custom Project Fields
  - Dependency Resolution
  - Status Column ID Conversion
  - Caching
  - Rate Limits
  - Error Handling
  - API Examples
  - Legacy: kanban-sync.sh
- Canonical governance rules (R15 written-orders / GitHub trail, R12
  minimum team composition): see the `team-governance` skill, which
  bundles the canonical rules and embeds the full TOC.
