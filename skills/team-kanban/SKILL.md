---
name: team-kanban
user-invocable: false
description: "Manage team kanban boards and tasks. Use when creating, moving, or filtering tasks. Trigger with /team-kanban. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(curl:*), Bash(jq:*), Bash(kanban-sync.py:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

<!-- DECOUPLE-BLOCKED ai-maestro#36: the `curl .../api/teams/...` task/board examples below will teach the `aimaestro-teams` CLI once ai-maestro#36 lands the verb (per core#11, TRDD-90c8ad35). Until then they stay functional against the server. GitHub-sync (`kanban-sync.py`, `gh`) is OUT OF SCOPE. -->

## Overview

Manage team kanban boards and tasks via the AI Maestro API. Create, update, filter, delete tasks; configure columns; track dependencies; compute metrics; sync with GitHub Projects v2.

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

- AI Maestro on `http://localhost:23000`
- `jq` installed
- For GitHub sync: `gh` CLI authenticated, `kanban-sync.py` at `~/.local/bin/`

## Instructions

1. **Identify team**: `curl -s http://localhost:23000/api/teams | jq .`
2. **Create task**: POST `/api/teams/{id}/tasks` with subject, status, priority, labels, assignee
3. **List/filter**: GET `/api/teams/{id}/tasks?status=X&assignee=Y&label=Z`
4. **Move task**: PUT `/api/teams/{id}/tasks/{taskId}` with `{"status":"<column-id>"}`
5. **Dependencies**: PUT with `{"blockedBy":["<id>"]}`, filter blocked tasks via `isBlocked`
6. **Configure columns**: GET/PUT `/api/teams/{id}/kanban-config`
7. **GitHub sync**: `kanban-sync.py link <team-id> <owner/repo> <project-number>`

### Quick API Reference

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List tasks | GET | `/api/teams/{id}/tasks` |
| Create task | POST | `/api/teams/{id}/tasks` |
| Update task | PUT | `/api/teams/{id}/tasks/{taskId}` |
| Delete task | DELETE | `/api/teams/{id}/tasks/{taskId}` |
| Kanban config | GET/PUT | `/api/teams/{id}/kanban-config` |

### Auth Headers

Closed-team endpoints require two headers: `Authorization` with value `Bearer <key>`, and `X-Agent-Id: <uuid>`.

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

- [ ] Identified correct team ID
- [ ] Verified auth headers (if closed team)
- [ ] Used valid status column IDs
- [ ] Set dependencies without circular refs
- [ ] Configured columns if custom workflow needed

## Resources

- [API Reference](references/api-reference.md)
  - Endpoints
  - GET /api/teams/{id}/tasks
  - POST /api/teams/{id}/tasks
  - PUT /api/teams/{id}/tasks/{taskId}
  - DELETE /api/teams/{id}/tasks/{taskId}
  - GET /api/teams/{id}/kanban-config
  - PUT /api/teams/{id}/kanban-config
  - GET /api/teams/stats
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
