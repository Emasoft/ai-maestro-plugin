# Kanban API Reference

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
