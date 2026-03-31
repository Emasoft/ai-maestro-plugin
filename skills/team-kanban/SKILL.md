---
name: team-kanban
user-invocable: "false"
description: "Manage team kanban boards and tasks. Use when creating, moving, or filtering tasks. Trigger with /team-kanban."
allowed-tools: "Bash(curl:*), Bash(jq:*), Bash(kanban-sync.py:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Manage team kanban boards and tasks via the AI Maestro API. Create, update, filter, delete tasks; configure columns; track dependencies; compute metrics; sync with GitHub Projects v2.

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

Closed-team endpoints require: `-H 'Authorization: Bearer <key>' -H 'X-Agent-Id: <uuid>'`

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
/team-kanban link team abc-123 to GitHub project 23blocks-OS/ai-maestro #5
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

- [API Reference](references/api-reference.md) — Endpoints, Task Lifecycle, Dependencies, Column Config, Velocity, Extended Fields, Error Codes
- [GitHub Sync Reference](references/github-sync.md) — Setup, Field Mapping, Label Taxonomy, Caching
