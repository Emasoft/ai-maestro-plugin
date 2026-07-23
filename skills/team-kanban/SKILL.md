---
name: team-kanban
user-invocable: false
description: "Manage team kanban boards and tasks. Use when creating, moving, filtering, getting, or editing tasks. Trigger with /team-kanban. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(amp-kanban-list.sh:*), Bash(amp-kanban-get.sh:*), Bash(amp-kanban-create-task.sh:*), Bash(amp-kanban-move.sh:*), Bash(amp-kanban-edit.sh:*), Bash(amp-kanban-archive.sh:*), Bash(aimaestro-teams.sh:*), Bash(jq:*), Bash(kanban-sync.py:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.1.1"
---

<!-- Decoupled per MANAGER core#11 (TRDD-90c8ad35): task/board examples call the frozen `amp-kanban-*` CLIs (list/get/create-task/move/edit/archive) + `aimaestro-teams.sh kanban-config`, which resolve the API base + agent identity internally, never the server `/api/*` directly. `amp-kanban-get.sh` and `amp-kanban-edit.sh` (issue #23) close most of the former non-status-field residuals — `edit` is the general verb, every field the task PUT accepts. Bulk team `stats` is permanently client-side (`jq` aggregation) per MANAGER verdict ai-maestro#64 — no verb is pending. GitHub-sync (`kanban-sync.py`, `gh`) is OUT OF SCOPE — keep. -->

## Overview

Manage team kanban boards and tasks via the frozen `amp-kanban-*` CLIs + `aimaestro-teams.sh kanban-config`. Create, filter, get, move, edit, archive tasks; configure columns; sync with GitHub Projects v2.

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

> **Recall first (proactive memory).** Before acting on a recurring problem, a design decision, or a repeated alert, recall prior lessons FIRST: `/janitor-memory-recall <symptom>` (shared wiki memory — index by the *symptom* / your words, not the fix's jargon) and `/memory-search <query>` (past discussion). See the proactive memory contract in the plugin `CLAUDE.md`.

## Prerequisites

- AI Maestro running (the `amp-kanban-*` / `aimaestro-teams.sh` CLIs resolve the API base + auth internally)
- The `amp-kanban-*` + `aimaestro-teams.sh` CLIs on PATH; `jq` installed
- For GitHub sync: `gh` CLI authenticated, `kanban-sync.py` at `~/.local/bin/`

## Instructions

> **Approval requirements.** Task creation and board operations (create/move/archive/configure) on a team you belong to are **`min-approval-requirement: none` (in-scope)** — no proposal needed; act directly. Anything that escalates beyond your slice (creating a team, cross-team work) follows the `ama-proposal-approvals` skill and the ai-maestro approval overlay (`.claude/rules/aimaestro-trdd-approval.md`).

1. **Identify team**: `aimaestro-teams.sh list | jq .`
2. **Create task**: `amp-kanban-create-task.sh "<title>" [--status S] [--priority N] [--labels "a,b"] [--assignee <id>]`
3. **List/filter**: `amp-kanban-list.sh [--status X] [--assignee Y] [--label Z]`
4. **Get one task**: `amp-kanban-get.sh <task-id>` — full task object, not just the fields `list` filters return.
5. **Move task (status only)**: `amp-kanban-move.sh <task-id> <status>`
6. **Edit task (any field)**: `amp-kanban-edit.sh <task-id> --set priority=1 --set assigneeAgentId=<uuid>` or `--set-json blockedBy='["<id>"]'` — the general verb; every field the task PUT accepts, repeatable per call.
7. **Archive/delete task**: `amp-kanban-archive.sh <task-id>`
8. **Configure columns**: `aimaestro-teams.sh kanban-config <team-id> --get | --set <columns-json>`
9. **GitHub sync**: `kanban-sync.py link <team-id> <owner/repo> <project-number>` (out of #11 scope — keep)
   <!-- Bulk team metrics across all teams (was `GET /api/teams/stats`) will NEVER get a frozen-CLI verb — MANAGER verdict ai-maestro#64: an all-teams roll-up is a dashboard concern, not an agent verb. Permanent pattern: list with `amp-kanban-list.sh` per team and aggregate client-side with `jq` (see the Velocity and Distribution reference). Do NOT call `/api/*` directly (core#11). -->

   When the sync posts to GitHub (issue, PR comment, project-item note), per PRRD G1.1 begin the body with a one-line self-identification of the authoring agent, since all agents share the one owner identity.

### Quick CLI Reference

| Operation | CLI command |
|-----------|-------------|
| List / filter tasks | `amp-kanban-list.sh [--status\|--assignee\|--label\|--task-type]` |
| Get one task | `amp-kanban-get.sh <task-id>` |
| Create task | `amp-kanban-create-task.sh "<title>" [--status\|--priority\|--labels\|--assignee]` |
| Move task (status) | `amp-kanban-move.sh <task-id> <status>` |
| Edit task (any field) | `amp-kanban-edit.sh <task-id> (--set k=v \| --set-json k=<json>)...` |
| Archive / delete task | `amp-kanban-archive.sh <task-id>` |
| Kanban config | `aimaestro-teams.sh kanban-config <team-id> --get\|--set <json>` |

Each CLI auto-detects the team from your agent registration (pass `--team <id>` to override).

### Authentication

The `amp-kanban-*` / `aimaestro-teams.sh` CLIs resolve your agent identity + bearer token internally — no `Authorization` / `X-Agent-Id` headers to set by hand. Pass `--id <uuid>` only to act as a specific agent.

### Columns

Columns are **per-team configurable** — `status` must match a column id in that team's
kanban config, so read the team's real config before moving a card rather than assuming
a vocabulary (`aimaestro-teams.sh kanban-config <team-id>`).

The **ratified vocabulary is the 17 columns** — 14 lifecycle:

`backburner` → `todo` → `design` → `dispatch` → `dev` → `testing` → `ai_review` →
`human_review` → `complete` → `publish` → `published` → `deploy` → `live` → `live_auditing`

plus 3 orthogonal/terminal: `blocked`, `failed`, `superseded`.

The legacy five (`backlog`/`pending`/`in_progress`/`review`/`completed`) are **obsolete**
and must not be taught as the target vocabulary — but a team whose config was never
migrated may still serve them, which is exactly why you read the config instead of
assuming. Configure a team onto the ratified set with `kanban-config --set` (see
[api-reference](references/api-reference.md)).

### Write-gate enforcement — not every move is yours to make

The server **refuses** some moves. This is enforced at the write endpoint, so a move you are
not entitled to make fails with `403` rather than silently succeeding:

- **GATE 1 — governed transitions need a MANAGER (by AID) or the human owner.** That covers
  moving a card *into* `human_review`, `complete`, `publish`, `deploy`, `published`, `live`,
  `failed`, or `superseded`; moving it *backward into* `dev` from `human_review` or
  `live_auditing`; and writing the release-evidence fields `publishedVersion` / `liveSince`.
- **GATE 2 — self-review ban.** You may not render a verdict on a card **you are assigned to**
  — writing `reviewResult`, or moving it out of `ai_review`/`human_review` into `complete`.
  Any *other* agent, of any title, may.
- **Everything else is a free member move**: `backburner`, `todo`, `design`, `dispatch`,
  `dev` (forward), `testing`, `ai_review`, `blocked`, `live_auditing`.

**Caveat — teams on a custom column configuration.** The gate matches literal column strings,
so this guarantee holds only for columns whose names match the ratified 17-column set; a
renamed governed column is not yet gated (tracked in TRDD-LY442MKH). A default-board team
needs no qualifier.

**Enforcement vs. process.** The write gate distinguishes only *MANAGER-by-AID / owner* from
*everyone else*, plus the self-review ban. The finer per-title routing (`todo→design` =
ORCHESTRATOR, `design→dispatch` = ARCHITECT, `dispatch→dev` = ORCHESTRATOR sets the assignee,
…) is the **organizational contract agents follow — it is NOT mechanically enforced**. Do not
rely on the server to refuse a contract violation it does not gate; see the
ai-maestro DEP overlay `.claude/rules/aimaestro-trdd-approval.md` (Part B) for the
routing itself.

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
| 403 | Governed transition refused (GATE 1) | Move into a governed column, backward into `dev` from `human_review`/`live_auditing`, or a write to `publishedVersion`/`liveSince` — needs a MANAGER (by AID) or the human owner. **Not** a membership problem; do not go debug membership |
| 403 | Self-review refused (GATE 2) | You are the card's assignee — another agent must render the verdict |
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
    - Get task
    - Create task
    - Move task (status)
    - Edit task (any field)
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

## Use also

- `Skill(skill: "team-governance")` — the teams and titles the board's tasks belong to.
- `Skill(skill: "agent-messaging")` — notify agents about task changes (AMP).
