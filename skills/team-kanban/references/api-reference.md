# Kanban API Reference

## Table of Contents

- [Endpoints](#endpoints)
  - [GET /api/teams/{id}/tasks](#get-apiteamsidtasks)
  - [POST /api/teams/{id}/tasks](#post-apiteamsidtasks)
  - [PUT /api/teams/{id}/tasks/{taskId}](#put-apiteamsidtaskstaskid)
  - [DELETE /api/teams/{id}/tasks/{taskId}](#delete-apiteamsidtaskstaskid)
  - [GET /api/teams/{id}/kanban-config](#get-apiteamsidkanban-config)
  - [PUT /api/teams/{id}/kanban-config](#put-apiteamsidkanban-config)
  - [GET /api/teams/stats](#get-apiteamsstats)
- [Task Lifecycle Examples](#task-lifecycle-examples)
- [Task Dependencies](#task-dependencies)
- [Kanban Configuration](#kanban-configuration)
- [Velocity and Distribution](#velocity-and-distribution)
- [Extended Task Fields](#extended-task-fields)
- [Error Codes](#error-codes)
- [Task Storage](#task-storage)
- [Available Tailwind Colors](#available-tailwind-colors)
- [Available Lucide Icons](#available-lucide-icons)

---

## Endpoints

### GET /api/teams/{id}/tasks

List all tasks for a team with resolved dependency information.

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter by status (must match a kanban column ID) |
| `assignee` | string | Filter by assignee agent UUID |
| `label` | string | Filter by label |
| `taskType` | string | Filter by task type |

**Response:** Array of TaskWithDeps objects.

Each task includes derived fields:

- `blocks` — array of task IDs that this task blocks
- `isBlocked` — boolean, true if any blockedBy task is not completed
- `assigneeName` — display name of the assigned agent (resolved from registry)

---

### POST /api/teams/{id}/tasks

Create a new task.

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subject` | string | Yes | Task title |
| `description` | string | No | Detailed description |
| `status` | string | No | Initial status (default: first column, usually `backlog`) |
| `priority` | number | No | Priority (lower = higher priority) |
| `assigneeAgentId` | string | No | Agent UUID to assign |
| `blockedBy` | string[] | No | Array of task IDs that block this task |
| `labels` | string[] | No | Categorization labels |
| `taskType` | string | No | Type: `feature`, `bug`, `chore`, `spike`, etc. |
| `externalRef` | string | No | External issue URL (e.g., GitHub issue) |
| `externalProjectRef` | string | No | External project URL |
| `acceptanceCriteria` | string[] | No | Definition of done items |
| `handoffDoc` | string | No | Handoff documentation |
| `prUrl` | string | No | Associated pull request URL |

**Response:** Created task object with generated `id`, `createdAt`, `updatedAt`.

---

### PUT /api/teams/{id}/tasks/{taskId}

Update an existing task. All fields optional — only provided fields are changed.

**Body:** Same fields as POST (all optional), plus:

| Field | Type | Description |
|-------|------|-------------|
| `previousStatus` | string | Record previous status (for undo tracking) |
| `reviewResult` | string | Review outcome notes |

**Validation:**

- `status` must match a column ID in the team's kanban config
- `blockedBy` must not create circular dependencies
- `priority` must be a finite number
- `assigneeAgentId` can be `null` to explicitly unassign

**Response:** Updated task object.

---

### DELETE /api/teams/{id}/tasks/{taskId}

Delete a task permanently.

**Response:** `{ "ok": true }`

---

### GET /api/teams/{id}/kanban-config

Get the team's kanban column configuration.

**Response:**

```json
{
  "columns": [
    { "id": "backlog", "label": "Backlog", "color": "bg-gray-500", "icon": "Archive" },
    { "id": "pending", "label": "To Do", "color": "bg-gray-400", "icon": "Circle" },
    ...
  ]
}
```

If no custom config is set, returns the 5 default columns.

---

### PUT /api/teams/{id}/kanban-config

Set custom kanban columns for a team.

**Body:**

```json
{
  "columns": [
    { "id": "<status-key>", "label": "<Display Name>", "color": "<tailwind-class>" },
    ...
  ]
}
```

**Column fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Column key, used as task status value |
| `label` | string | Yes | Display name shown in UI |
| `color` | string | Yes | Tailwind dot-color class (e.g., `bg-blue-400`) |
| `icon` | string | No | Lucide icon name (e.g., `PlayCircle`, `Eye`) |

**Response:** `{ "columns": [...] }` — the saved configuration.

---

### GET /api/teams/stats

Bulk stats for all teams (eliminates N+1 fetch pattern).

**Response:**

```json
{
  "<teamId>": { "taskCount": 12, "docCount": 3 },
  "<teamId>": { "taskCount": 5, "docCount": 0 }
}
```

---

## Task Storage

Tasks are stored per-team in JSON files:

```
~/.aimaestro/teams/tasks-{teamId}.json
```

Format: `{ "version": 1, "tasks": [...] }`

Writes are atomic (temp file + rename). The UI polls every 5 seconds for multi-tab sync.

---

## Available Tailwind Colors

For kanban column `color` field, use any Tailwind dot-color:

```
bg-gray-400  bg-gray-500  bg-red-400   bg-red-500
bg-orange-400  bg-amber-400  bg-yellow-400  bg-lime-400
bg-green-400  bg-emerald-400  bg-teal-400  bg-cyan-400
bg-sky-400  bg-blue-400  bg-indigo-400  bg-violet-400
bg-purple-400  bg-fuchsia-400  bg-pink-400  bg-rose-400
```

---

## Available Lucide Icons

For kanban column `icon` field, common choices:

```
Archive  Circle  PlayCircle  Eye  CheckCircle2
Clock  AlertTriangle  Bug  Wrench  FlaskConical
SearchCheck  Rocket  Pause  XCircle  Star
GitPullRequest  Code  Shield  Zap  Target
```

---

## Task Lifecycle Examples

### Auth Headers

All task/kanban endpoints require authentication:

```bash
AUTH="-H 'Authorization: Bearer <api-key>' -H 'X-Agent-Id: <your-agent-uuid>'"
```

If running as the system owner (no agents configured), omit auth headers.

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

## Velocity and Distribution

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
