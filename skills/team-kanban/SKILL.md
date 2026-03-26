---
name: team-kanban
description: >-
  Manage team kanban boards and tasks — create/update/filter tasks, configure
  kanban columns, track dependencies, compute velocity, and sync with GitHub
  project boards. Use when agents say "create task", "move task", "show kanban",
  "configure columns", "sync with GitHub", "what's blocked", "team velocity".
allowed-tools: Bash
metadata:
  author: 23blocks
  version: "1.0"
---

# Team Kanban Management

Manage kanban boards, tasks, and GitHub project sync using the AI Maestro API.

---

## Auth Headers

All task/kanban endpoints require authentication:

```bash
AUTH="-H 'Authorization: Bearer <api-key>' -H 'X-Agent-Id: <your-agent-uuid>'"
```

If running as the system owner (no agents configured), omit auth headers.

---

## Quick Reference

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List tasks | GET | `/api/teams/{id}/tasks` |
| Create task | POST | `/api/teams/{id}/tasks` |
| Update task | PUT | `/api/teams/{id}/tasks/{taskId}` |
| Delete task | DELETE | `/api/teams/{id}/tasks/{taskId}` |
| Get kanban config | GET | `/api/teams/{id}/kanban-config` |
| Set kanban config | PUT | `/api/teams/{id}/kanban-config` |
| Bulk team stats | GET | `/api/teams/stats` |

---

## Task Lifecycle

### Create a Task

```bash
curl -s -X POST "http://localhost:23000/api/teams/<team-id>/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Implement auth middleware",
    "description": "Add JWT validation to all API routes",
    "status": "backlog",
    "priority": 1,
    "assigneeAgentId": "<agent-uuid>",
    "labels": ["backend", "security"],
    "taskType": "feature"
  }' | jq .
```

### List Tasks (with Filters)

```bash
# All tasks (API returns { tasks: [...] } — unwrap with .tasks)
curl -s "http://localhost:23000/api/teams/<team-id>/tasks" | jq '.tasks'

# Filter by status
curl -s "http://localhost:23000/api/teams/<team-id>/tasks?status=in_progress" | jq '.tasks'

# Filter by assignee
curl -s "http://localhost:23000/api/teams/<team-id>/tasks?assignee=<agent-uuid>" | jq '.tasks'

# Filter by label
curl -s "http://localhost:23000/api/teams/<team-id>/tasks?label=backend" | jq '.tasks'

# Filter by task type
curl -s "http://localhost:23000/api/teams/<team-id>/tasks?taskType=bug" | jq '.tasks'
```

### Move Task (Update Status)

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>/tasks/<task-id>" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}' | jq .
```

Status must match a column ID in the team's kanban config. Default columns: `backlog`, `pending`, `in_progress`, `review`, `completed`.

### Assign/Unassign Task

```bash
# Assign
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>/tasks/<task-id>" \
  -H "Content-Type: application/json" \
  -d '{"assigneeAgentId": "<agent-uuid>"}' | jq .

# Unassign
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>/tasks/<task-id>" \
  -H "Content-Type: application/json" \
  -d '{"assigneeAgentId": null}' | jq .
```

### Delete Task

```bash
curl -s -X DELETE "http://localhost:23000/api/teams/<team-id>/tasks/<task-id>" | jq .
```

---

## Task Dependencies

Tasks can block other tasks via `blockedBy` (array of task IDs).

### Set Dependencies

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>/tasks/<task-id>" \
  -H "Content-Type: application/json" \
  -d '{"blockedBy": ["<blocking-task-id-1>", "<blocking-task-id-2>"]}' | jq .
```

### Check What's Blocked

```bash
# List returns tasks with resolved deps: isBlocked (bool) and blocks (array)
curl -s "http://localhost:23000/api/teams/<team-id>/tasks" | \
  jq '[.tasks[] | select(.isBlocked == true) | {id, subject, blockedBy}]'
```

### Clear Dependencies

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>/tasks/<task-id>" \
  -H "Content-Type: application/json" \
  -d '{"blockedBy": []}' | jq .
```

Circular dependencies are rejected by the API.

---

## Kanban Configuration

### Get Current Columns

```bash
curl -s "http://localhost:23000/api/teams/<team-id>/kanban-config" | jq .
```

Returns: `{ columns: [{ id, label, color, icon? }, ...] }`

### Default Columns

| id | label | color | icon |
|----|-------|-------|------|
| `backlog` | Backlog | bg-gray-500 | Archive |
| `pending` | To Do | bg-gray-400 | Circle |
| `in_progress` | In Progress | bg-blue-400 | PlayCircle |
| `review` | Review | bg-amber-400 | Eye |
| `completed` | Done | bg-emerald-400 | CheckCircle2 |

### Customize Columns

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>/kanban-config" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": [
      {"id": "backlog", "label": "Backlog", "color": "bg-gray-500", "icon": "Archive"},
      {"id": "todo", "label": "TODO", "color": "bg-gray-400", "icon": "Circle"},
      {"id": "in_progress", "label": "In Progress", "color": "bg-blue-400", "icon": "PlayCircle"},
      {"id": "ai_review", "label": "AI Review", "color": "bg-purple-400", "icon": "SearchCheck"},
      {"id": "human_review", "label": "Human Review", "color": "bg-amber-400", "icon": "Eye"},
      {"id": "testing", "label": "Testing", "color": "bg-cyan-400", "icon": "FlaskConical"},
      {"id": "completed", "label": "Done", "color": "bg-emerald-400", "icon": "CheckCircle2"}
    ]
  }' | jq .
```

Each column needs: `id` (used as task status value), `label` (display name), `color` (Tailwind class). `icon` is optional (Lucide icon name).

After updating columns, existing tasks with statuses not in the new config cannot be moved until their status is updated to a valid column ID.

---

## Velocity & Distribution

### Tasks Per Status (Team Velocity Snapshot)

```bash
curl -s "http://localhost:23000/api/teams/<team-id>/tasks" | \
  jq '.tasks | group_by(.status) | map({status: .[0].status, count: length})'
```

### Tasks Per Agent (Load Distribution)

```bash
curl -s "http://localhost:23000/api/teams/<team-id>/tasks" | \
  jq '.tasks | group_by(.assigneeAgentId) | map({agent: .[0].assigneeAgentId, assigneeName: .[0].assigneeName, count: length, in_progress: [.[] | select(.status == "in_progress")] | length})'
```

### Completed in Date Range

```bash
curl -s "http://localhost:23000/api/teams/<team-id>/tasks?status=completed" | \
  jq --arg since "2026-03-01" '[.tasks[] | select(.completedAt >= $since)] | length'
```

### Bulk Stats (All Teams)

```bash
curl -s "http://localhost:23000/api/teams/stats" | jq .
# Returns: { "<teamId>": { taskCount: N, docCount: N }, ... }
```

---

## GitHub Project Integration

AI Maestro kanban acts as a **browser** (GUI) of GitHub Projects v2. GitHub is the sole source of truth. Each team is linked to a specific GitHub repo and project board.

### Architecture

When a team has a `githubProject` link configured:
- **Every task read** queries GitHub Projects v2 via GraphQL
- **Every task write** (create, update, delete) mutates GitHub directly
- **Kanban columns** are derived from the GitHub Project's Status field options
- **No local task storage** — GitHub is the only source of truth
- Results are cached 10 seconds server-side to avoid excessive API calls

### Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- AI Maestro running on localhost:23000
- A GitHub Project (v2) with a "Status" single-select field

### Link a Team to a GitHub Project

```bash
kanban-sync.py link <team-id> <owner/repo> <project-number>
# Example: kanban-sync.py link abc-123 23blocks-OS/ai-maestro 5
```

This verifies the project exists, shows its columns, and sets the `githubProject` field on the team. From that point, all kanban operations go through GitHub.

### Unlink a Team

```bash
kanban-sync.py unlink <team-id>
```

Removes the GitHub Project link. Tasks remain in GitHub but are no longer visible in AI Maestro. The team reverts to local file-based storage (empty).

### Show Link Status

```bash
kanban-sync.py status <team-id>
# Shows: GitHub project link, columns, connection status
```

### List All Teams

```bash
kanban-sync.py list
# Shows all teams with their GitHub Project link status
```

### How Tasks Map to GitHub

| AI Maestro | GitHub | Notes |
|-----------|--------|-------|
| Task subject | Issue title | |
| Task description | Issue body | |
| Task status | Project Status field | Column ID = lowercased, underscored |
| Task priority | Project Priority field | Fallback: `priority:*` label |
| Task assignee | `assign:*` label / Issue assignee | Label preferred, GitHub assignee fallback |
| Task labels | Issue labels | Excluding parsed prefix labels |
| Task ID | Project item node ID (PVTI_...) | |
| `taskType` | `type:*` label or bare label | `type:bug`, `type:feature`, etc. |
| `externalRef` | Issue URL | |
| `blockedBy` | `blocked-by:*`/`depends:*` labels + body | Parses issue # references |
| `previousStatus` | `status:blocked-from:*` label | For blocked→restore flow |
| `prUrl` | Linked PR (timeline events) | First connected PR URL |
| `acceptanceCriteria` | `## Acceptance Criteria` in body | Checklist items parsed |
| `handoffDoc` | `handoff:` line in body | |
| `createdAt`/`updatedAt` | Issue timestamps | Real GitHub timestamps |
| `completedAt` | Issue `closedAt` | |

### Kanban Columns = GitHub Status Field

Columns are NOT stored locally. They ARE the GitHub Project's Status field options. When you customize columns via the AI Maestro API, it updates the GitHub Project's Status field directly.

See [GitHub Sync Reference](references/github-sync.md) for more details.

---

## Extended Task Fields

Tasks support fields for workflow tracking beyond basic status:

| Field | Type | Purpose |
|-------|------|---------|
| `externalRef` | string | Link to external issue (GitHub issue URL) |
| `externalProjectRef` | string | Link to external project (GitHub project URL) |
| `acceptanceCriteria` | string[] | Definition of done checklist |
| `handoffDoc` | string | Handoff documentation for next assignee |
| `prUrl` | string | Pull request URL |
| `reviewResult` | string | Review outcome notes |
| `previousStatus` | string | Status before current (for undo) |

### Link PR to Task

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>/tasks/<task-id>" \
  -H "Content-Type: application/json" \
  -d '{"prUrl": "https://github.com/org/repo/pull/42", "status": "review"}' | jq .
```

---

## Error Codes

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | `Invalid status` | Status must match a kanban column ID |
| 400 | `Circular dependency` | blockedBy would create a cycle |
| 400 | `priority must be a finite number` | Priority must be a number |
| 403 | `Access denied` | Agent not a member of closed team |
| 404 | `Team not found` | Invalid team ID |
| 404 | `Task not found` | Invalid task ID |

---

## Resources

- [API Reference](references/api-reference.md) — full endpoint documentation
- [GitHub Sync Reference](references/github-sync.md) — sync procedures, label mapping, advanced options
