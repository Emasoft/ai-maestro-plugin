# Kanban API Reference

<!-- Decoupled per MANAGER core#11 (TRDD-90c8ad35): operations use the frozen `amp-kanban-*` CLIs (list/create-task/move/archive) + `aimaestro-teams.sh kanban-config`, which resolve the API base + agent identity internally, never the server `/api/*` directly. The field/response tables document what each CLI accepts and returns. Residuals with no frozen verb yet (re-assign/unassign an existing task, set/clear blockedBy dependencies, link prUrl / other non-status field edits, team `stats`) are marked DECOUPLE-BLOCKED inline, re-targeted to an ai-maestro follow-up. -->

## Table of Contents

- [Operations](#operations)
  - [List tasks](#list-tasks)
  - [Create task](#create-task)
  - [Update task (status move + fields)](#update-task-status-move--fields)
  - [Archive / delete task](#archive--delete-task)
  - [Get kanban config](#get-kanban-config)
  - [Set kanban config](#set-kanban-config)
  - [Team stats (residual)](#team-stats-residual)
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

## Operations

Each CLI auto-detects the team from your agent registration (pass `--team <id>` to
override) and resolves the API base + auth internally — no headers to set by hand.

### List tasks

CLI: `amp-kanban-list.sh [--status S] [--assignee A] [--label L] [--task-type T] [--team <id>]`

Lists all tasks for a team with resolved dependency information.

**Filters:**

| Flag | Type | Description |
|-------|------|-------------|
| `--status` | string | Filter by status (must match a kanban column ID) |
| `--assignee` | string | Filter by assignee agent UUID |
| `--label` | string | Filter by label |
| `--task-type` | string | Filter by task type |

**Response:** `{ "tasks": [...] }` — array of TaskWithDeps objects (unwrap with `jq '.tasks'`).

Each task includes derived fields:

- `blocks` — array of task IDs that this task blocks
- `isBlocked` — boolean, true if any blockedBy task is not completed
- `assigneeName` — display name of the assigned agent (resolved from registry)

---

### Create task

CLI: `amp-kanban-create-task.sh "<title>" [--description D] [--status S] [--priority N] [--assignee A] [--labels "a,b,c"] [--task-type T] [--team <id>]`

Creates a new task.

**Fields** (CLI flag → stored field):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subject` (positional title) | string | Yes | Task title |
| `description` (`--description`) | string | No | Detailed description |
| `status` (`--status`) | string | No | Initial status (default: first column, usually `backlog`) |
| `priority` (`--priority`) | number | No | Priority (lower = higher priority) |
| `assigneeAgentId` (`--assignee`) | string | No | Agent UUID to assign |
| `labels` (`--labels`) | string[] | No | Categorization labels (comma-separated) |
| `taskType` (`--task-type`) | string | No | Type: `feature`, `bug`, `chore`, `spike`, etc. |

Additional stored fields (`blockedBy`, `externalRef`, `externalProjectRef`,
`acceptanceCriteria`, `handoffDoc`, `prUrl`) are set at create time by the server
default or left empty; editing them on an existing task is a residual (see below).

**Response:** Created task object with generated `id`, `createdAt`, `updatedAt`.

---

### Update task (status move + fields)

Update an existing task. The **status move** is covered by the frozen CLI:

CLI: `amp-kanban-move.sh <task-id> <status> [--team <id>]`

<!-- DECOUPLE-BLOCKED ai-maestro#36: editing NON-status fields on an existing task — re-assign/unassign (`assigneeAgentId`), set/clear `blockedBy` dependencies, `priority`, `prUrl`, `reviewResult`, `previousStatus` (was `PUT /api/teams/{id}/tasks/{taskId}` with those fields) — has no frozen-CLI verb yet. `amp-kanban-move` only changes status; `amp-kanban-create-task` sets initial priority/labels/assignee. Pending a follow-up verb. Do NOT call `/api/*` directly (core#11). -->

**Validation** (enforced server-side):

- `status` must match a column ID in the team's kanban config
- `blockedBy` must not create circular dependencies
- `priority` must be a finite number
- `assigneeAgentId` can be `null` to explicitly unassign

**Response:** Updated task object.

---

### Archive / delete task

CLI: `amp-kanban-archive.sh <task-id> [--team <id>]`

Archives (removes) a task.

**Response:** `{ "ok": true }`

---

### Get kanban config

CLI: `aimaestro-teams.sh kanban-config <team-id> --get`

Gets the team's kanban column configuration.

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

### Set kanban config

CLI: `aimaestro-teams.sh kanban-config <team-id> --set '<columns-json>'` (or `--set-file <path>`)

Sets custom kanban columns for a team.

**Columns JSON:**

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

### Team stats (residual)

<!-- DECOUPLE-BLOCKED ai-maestro#36: bulk team stats (task/doc counts across all teams, was `GET /api/teams/stats`) has no frozen-CLI verb yet — pending a follow-up. For a single team's task counts, list with `amp-kanban-list.sh` and aggregate client-side with `jq` (see Velocity and Distribution). Do NOT call `/api/*` directly (core#11). -->

**Shape (when a verb lands):**

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

### Authentication

The `amp-kanban-*` / `aimaestro-teams.sh` CLIs resolve your agent identity + bearer
token internally — no `Authorization` / `X-Agent-Id` headers to set by hand. Pass
`--id <uuid>` only to act as a specific agent (UUID from `config.json`); omit it to
run as the auto-detected caller.

### Create a Task

```bash
amp-kanban-create-task.sh "Implement auth middleware" \
  --description "Add JWT validation to all API routes" \
  --status backlog \
  --priority 1 \
  --assignee <agent-uuid> \
  --labels "backend,security" \
  --task-type feature | jq .
```

### List Tasks (with Filters)

```bash
# All tasks (CLI returns { tasks: [...] } — unwrap with .tasks)
amp-kanban-list.sh | jq '.tasks'

# Filter by status
amp-kanban-list.sh --status in_progress | jq '.tasks'

# Filter by assignee
amp-kanban-list.sh --assignee <agent-uuid> | jq '.tasks'

# Filter by label
amp-kanban-list.sh --label backend | jq '.tasks'

# Filter by task type
amp-kanban-list.sh --task-type bug | jq '.tasks'
```

### Move Task (Update Status)

```bash
amp-kanban-move.sh <task-id> in_progress | jq .
```

Status must match a column ID in the team's kanban config. Default columns: `backlog`, `pending`, `in_progress`, `review`, `completed`.

### Assign/Unassign Task

Set the assignee **at create time** with `--assignee` (covered):

```bash
amp-kanban-create-task.sh "Review PR #42" --assignee <agent-uuid> --status review | jq .
```

<!-- DECOUPLE-BLOCKED ai-maestro#36: re-assigning or unassigning an EXISTING task (was `PUT /api/teams/{id}/tasks/{taskId}` with `{assigneeAgentId}` / `null`) has no frozen-CLI verb yet — pending a follow-up. Set the assignee at create time via `--assignee`, or wait for the verb. Do NOT call `/api/*` directly (core#11). -->

### Delete Task

```bash
amp-kanban-archive.sh <task-id> | jq .
```

---

## Task Dependencies

Tasks can block other tasks via `blockedBy` (array of task IDs).

### Set / Clear Dependencies

<!-- DECOUPLE-BLOCKED ai-maestro#36: setting or clearing `blockedBy` dependencies on a task (was `PUT /api/teams/{id}/tasks/{taskId}` with `{blockedBy: [...]}` / `[]`) has no frozen-CLI verb yet — pending a follow-up. Circular dependencies are rejected server-side. Do NOT call `/api/*` directly (core#11). -->

### Check What's Blocked

```bash
amp-kanban-list.sh | \
  jq '[.tasks[] | select(.isBlocked == true) | {id, subject, blockedBy}]'
```

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
aimaestro-teams.sh kanban-config <team-id> --set '[
  {"id": "backlog", "label": "Backlog", "color": "bg-gray-500", "icon": "Archive"},
  {"id": "todo", "label": "TODO", "color": "bg-gray-400", "icon": "Circle"},
  {"id": "in_progress", "label": "In Progress", "color": "bg-blue-400", "icon": "PlayCircle"},
  {"id": "ai_review", "label": "AI Review", "color": "bg-purple-400", "icon": "SearchCheck"},
  {"id": "human_review", "label": "Human Review", "color": "bg-amber-400", "icon": "Eye"},
  {"id": "testing", "label": "Testing", "color": "bg-cyan-400", "icon": "FlaskConical"},
  {"id": "completed", "label": "Done", "color": "bg-emerald-400", "icon": "CheckCircle2"}
]' | jq .
```

Each column needs: `id` (used as task status value), `label` (display name), `color` (Tailwind class). `icon` is optional (Lucide icon name). Tip: keep the column JSON in a file and use `aimaestro-teams.sh kanban-config <team-id> --set-file <path>`.

After updating columns, existing tasks with statuses not in the new config cannot be moved until their status is updated to a valid column ID.

---

## Velocity and Distribution

These read the task list with `amp-kanban-list.sh` and aggregate client-side with `jq`.

### Tasks Per Status (Team Velocity Snapshot)

```bash
amp-kanban-list.sh | \
  jq '.tasks | group_by(.status) | map({status: .[0].status, count: length})'
```

### Tasks Per Agent (Load Distribution)

```bash
amp-kanban-list.sh | \
  jq '.tasks | group_by(.assigneeAgentId) | map({agent: .[0].assigneeAgentId, assigneeName: .[0].assigneeName, count: length, in_progress: [.[] | select(.status == "in_progress")] | length})'
```

### Completed in Date Range

```bash
amp-kanban-list.sh --status completed | \
  jq --arg since "2026-03-01" '[.tasks[] | select(.completedAt >= $since)] | length'
```

### Bulk Stats (All Teams)

<!-- DECOUPLE-BLOCKED ai-maestro#36: bulk all-teams stats (was `GET /api/teams/stats`) has no frozen-CLI verb yet — pending a follow-up. For one team, use the per-status aggregation above. Do NOT call `/api/*` directly (core#11). -->

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

The **status move** part is covered (`amp-kanban-move.sh <task-id> review`).

<!-- DECOUPLE-BLOCKED ai-maestro#36: setting `prUrl` (and the other extended fields above) on an existing task (was `PUT /api/teams/{id}/tasks/{taskId}` with `{prUrl, ...}`) has no frozen-CLI verb yet — pending a follow-up. Move the status with `amp-kanban-move`; the prUrl/extended-field edit waits for the verb. Do NOT call `/api/*` directly (core#11). -->

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
