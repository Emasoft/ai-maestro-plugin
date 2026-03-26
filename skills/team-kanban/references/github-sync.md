# GitHub Projects v2 Integration

AI Maestro kanban is a live browser of GitHub Projects v2. There is no sync — GitHub IS the source of truth. All task CRUD operations proxy through the GitHub GraphQL API.

## Prerequisites

- `gh` CLI installed and authenticated: `gh auth status`
- AI Maestro running on `http://localhost:23000`
- `kanban-sync.py` installed at `~/.local/bin/`
- A GitHub Project (v2) with a **Status** single-select field

## Setup

### Link a Team to a GitHub Project

```bash
kanban-sync.py link <team-id> <owner/repo> <project-number>
```

| Argument | Description |
|----------|-------------|
| `team-id` | AI Maestro team UUID |
| `owner/repo` | GitHub repo (e.g., `23blocks-OS/ai-maestro`) |
| `project-number` | Project number from the GitHub URL |

**What happens:**
1. Verifies the team exists in AI Maestro
2. Verifies the GitHub Project exists and has a Status field
3. Sets `githubProject` on the team (`{ owner, repo, number }`)
4. From this point, all task API calls go through GitHub

### Unlink a Team

```bash
kanban-sync.py unlink <team-id>
```

Removes the link. Tasks stay in GitHub but are no longer visible in AI Maestro kanban.

### Show Status

```bash
kanban-sync.py status <team-id>
kanban-sync.py list  # All teams
```

## How It Works

### Read Flow (GET /api/teams/{id}/tasks)

```
UI polls every 5s → API route → teams-service → github-project.ts
  → gh api graphql (query project items) → parse → return Task[]
  → server-side 10s cache avoids redundant GitHub calls
```

### Write Flow (POST/PUT/DELETE)

```
UI action → API route → teams-service → github-project.ts
  → gh issue create / gh api graphql (mutation) → GitHub
  → invalidate task cache → next GET fetches fresh data
```

### Column Config (GET/PUT /api/teams/{id}/kanban-config)

Columns = GitHub Project Status field options. No local storage.
- GET: reads Status field options via GraphQL
- PUT: updates Status field options via `updateProjectV2Field` mutation

## Field Mapping

| AI Maestro Task Field | GitHub Equivalent | Notes |
|-----------------------|-------------------|-------|
| `id` | Project item node_id (`PVTI_...`) | Used as task identifier |
| `subject` | Issue title | |
| `description` | Issue body | |
| `status` | Status field (single-select) | Column ID = lowercased, underscored option name |
| `priority` | Priority field (single-select) | 0=Critical, 1=High, 2=Medium, 3=Low. Fallback: `priority:*` label |
| `assigneeAgentId` | `assign:*` label or issue assignee | `assign:agent-name` label preferred, GitHub assignee as fallback |
| `labels` | Issue labels | Excluding parsed prefixed labels (type:, assign:, blocked-by:, etc.) |
| `taskType` | `type:*` label or bare type label | `type:bug` preferred, bare `bug` as fallback |
| `externalRef` | Issue URL | Auto-populated |
| `externalProjectRef` | Project item node_id | Same as `id` (PVTI_...) |
| `blockedBy` | `blocked-by:*`/`depends:*` labels + body refs | Parses `blocked-by:#42`, `depends:#13`, "Blocked by #N" in body |
| `previousStatus` | `status:blocked-from:*` label | Saved column before moving to blocked |
| `prUrl` | Linked PR (timeline events) | First connected/cross-referenced PR URL |
| `acceptanceCriteria` | Issue body `## Acceptance Criteria` | Lines under that heading parsed as checklist |
| `handoffDoc` | Issue body `handoff:` or `handoff-doc:` line | Path/URL to handoff document |
| `createdAt` | Issue `createdAt` | Real GitHub timestamp |
| `updatedAt` | Issue `updatedAt` | Real GitHub timestamp |
| `completedAt` | Issue `closedAt` | Set when issue is closed |
| `startedAt` | Derived from status | Set to `updatedAt` when status is `in_progress` |

### Label Taxonomy (AMOA Convention)

Labels with recognized prefixes are parsed into Task fields:

| Prefix | Task Field | Example |
|--------|-----------|---------|
| `type:` | `taskType` | `type:bug`, `type:feature`, `type:epic` |
| `assign:` | `assigneeAgentId` | `assign:backend-programmer` |
| `priority:` | `priority` (fallback) | `priority:high`, `priority:p1` |
| `blocked-by:` | `blockedBy` | `blocked-by:#42` |
| `depends:` | `blockedBy` | `depends:#13` |
| `status:blocked-from:` | `previousStatus` | `status:blocked-from:in_progress` |
| `blocked` (bare) | triggers `previousStatus` save | |

All other labels (including `status:*`, `component:*`, `effort:*`, `platform:*`, `toolchain:*`, `review:*`) are preserved in the `labels` array for display.

### Custom Project Fields

Additional single-select and text fields in the GitHub Project (beyond Status and Priority) are read and available through the field values. Examples: Agent, Platform, Effort, Component.

### Dependency Resolution

`resolveTaskDeps()` converts `blockedBy` references (which may be issue numbers like `#42`) into actual task IDs by matching against `externalRef` URLs. It also computes:
- `blocks[]` — reverse dependency (which tasks does this one block)
- `isBlocked` — true if any dependency is not in a completed status

## Status Column ID Conversion

GitHub Status option names are converted to column IDs:
- `"In Progress"` → `in_progress`
- `"To Do"` → `to_do`
- `"AI Review"` → `ai_review`
- `"Done"` → `done`

Rule: lowercase, replace non-alphanumeric with `_`, trim leading/trailing `_`.

## Caching

| What | TTL | Notes |
|------|-----|-------|
| Project metadata (field IDs, options) | 1 hour | Rarely changes |
| Task list | 10 seconds | UI polls every 5s |
| Writes | Bypass + invalidate | Next read fetches fresh |

## Rate Limits

GitHub authenticated API: 5000 requests/hour.
With 10s cache + 5s UI polling: ~360 requests/hour per active team.
Multiple browser tabs share the server-side cache.

## Error Handling

| HTTP Status | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Invalid request (bad status value, etc.) |
| 502 | GitHub API returned an error |
| 503 | `gh` CLI not installed or not authenticated |
| 504 | GitHub API timeout |

## API Examples

After linking, the standard task API works exactly the same:

```bash
TEAM="<team-id>"

# List tasks (fetched live from GitHub Project)
curl -s "http://localhost:23000/api/teams/$TEAM/tasks" | jq '.tasks'

# Create task (creates GitHub issue + adds to project)
curl -s -X POST "http://localhost:23000/api/teams/$TEAM/tasks" \
  -H "Content-Type: application/json" \
  -d '{"subject": "Fix login bug", "status": "to_do", "priority": 1}' | jq .

# Move task (updates Status field on GitHub Project)
curl -s -X PUT "http://localhost:23000/api/teams/$TEAM/tasks/<item-id>" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}' | jq .

# Get kanban columns (from GitHub Project Status field)
curl -s "http://localhost:23000/api/teams/$TEAM/kanban-config" | jq .
```

## Legacy: kanban-sync.sh

The old `kanban-sync.sh` script (bash) still exists for backward compatibility. It does basic issue-level sync (pull issues, push completed status) but does NOT use GitHub Projects v2. For full project integration, use the `kanban-sync.py` link approach instead.
