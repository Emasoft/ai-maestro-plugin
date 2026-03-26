---
name: team-kanban
description: "Manage team kanban boards and tasks. Use when creating, moving, or filtering tasks. Trigger with /team-kanban."
allowed-tools: "Bash(curl:*), Bash(jq:*), Bash(kanban-sync.py:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Manage team kanban boards and tasks via the AI Maestro API. Supports creating, updating, filtering, and deleting tasks; configuring kanban columns; tracking dependencies and blocked tasks; computing velocity/distribution metrics; and syncing with GitHub Projects v2.

## Prerequisites

- AI Maestro running on `http://localhost:23000`
- `jq` installed for JSON processing
- For GitHub sync: `gh` CLI authenticated (`gh auth status`) and `kanban-sync.py` at `~/.local/bin/`

## Instructions

1. **Identify the team ID** — use `curl -s http://localhost:23000/api/teams | jq .` to list teams
2. **Create a task** — POST to `/api/teams/{id}/tasks` with subject, status, priority, labels, assignee
3. **List/filter tasks** — GET `/api/teams/{id}/tasks` with optional query params: `status`, `assignee`, `label`, `taskType`
4. **Move a task** — PUT `/api/teams/{id}/tasks/{taskId}` with `{"status": "<column-id>"}`
5. **Set dependencies** — PUT with `{"blockedBy": ["<task-id>"]}`; check blocked tasks with jq filter on `isBlocked`
6. **Configure columns** — GET/PUT `/api/teams/{id}/kanban-config` to read or customize kanban columns
7. **Compute velocity** — use jq to group tasks by status or assignee from the task list response
8. **Link GitHub Project** — run `kanban-sync.py link <team-id> <owner/repo> <project-number>` for live GitHub integration

### Quick API Reference

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List tasks | GET | `/api/teams/{id}/tasks` |
| Create task | POST | `/api/teams/{id}/tasks` |
| Update task | PUT | `/api/teams/{id}/tasks/{taskId}` |
| Delete task | DELETE | `/api/teams/{id}/tasks/{taskId}` |
| Kanban config | GET/PUT | `/api/teams/{id}/kanban-config` |
| Bulk stats | GET | `/api/teams/stats` |

### Auth Headers

Closed-team endpoints require:
```bash
-H 'Authorization: Bearer <api-key>' -H 'X-Agent-Id: <agent-uuid>'
```
Omit for system owner (no agents configured).

### Default Kanban Columns

`backlog` | `pending` | `in_progress` | `review` | `completed`

Status values in task create/update must match a column ID.

## Output

- Task list: `{ "tasks": [...] }` with resolved `isBlocked`, `blocks[]`, `assigneeName`
- Single task: task object with `id`, `subject`, `status`, `priority`, timestamps
- Kanban config: `{ "columns": [{ id, label, color, icon? }] }`
- Bulk stats: `{ "<teamId>": { taskCount, docCount } }`

## Error Handling

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | `Invalid status` | Status must match a kanban column ID |
| 400 | `Circular dependency` | blockedBy creates a cycle |
| 403 | `Access denied` | Agent not a team member |
| 404 | `Team/Task not found` | Invalid ID |
| 502/503 | GitHub errors | Check `gh auth status` |

## Examples

```
/team-kanban create a task "Fix login bug" with priority 1 in team abc-123
```
Expected: Creates task via POST, returns task object with generated ID.

```
/team-kanban show blocked tasks in team abc-123
```
Expected: Lists tasks where `isBlocked == true` with their blockers.

```
/team-kanban link team abc-123 to GitHub project 23blocks-OS/ai-maestro #5
```
Expected: Runs `kanban-sync.py link` to connect team to GitHub Projects v2.

## Checklist

Copy this checklist and track your progress:
- [ ] Identified correct team ID
- [ ] Verified auth headers (if closed team)
- [ ] Created/updated tasks with valid status column IDs
- [ ] Set task dependencies without circular refs
- [ ] Verified blocked tasks resolve correctly
- [ ] Configured kanban columns if custom workflow needed
- [ ] Linked GitHub Project if external sync required

## Resources

- [API Reference](references/api-reference.md) — Full endpoint docs, task lifecycle examples, dependency management, column config, velocity queries, extended fields, error codes
  - Endpoints (GET/POST/PUT/DELETE for tasks, kanban-config, stats)
  - Task Lifecycle Examples (create, list, filter, move, assign, delete)
  - Task Dependencies (set, check blocked, clear)
  - Kanban Configuration (default columns, customize)
  - Velocity and Distribution (per-status, per-agent, date range, bulk stats)
  - Extended Task Fields (externalRef, acceptanceCriteria, prUrl, etc.)
  - Error Codes
- [GitHub Sync Reference](references/github-sync.md) — GitHub Projects v2 integration, field mapping, label taxonomy, caching
  - Setup (link, unlink, status)
  - How It Works (read/write flow, column config)
  - Field Mapping (AI Maestro to GitHub equivalents)
  - Label Taxonomy (AMOA Convention)
  - Status Column ID Conversion
  - Caching and Rate Limits
