---
name: agent-repo-workflow
user-invocable: false
description: "Use when an agent needs to clone or create repos, branch, open PRs, list project repos/team members, or report task done/blocked to its orchestrator via AMP. Trigger with 'clone the project repo', 'open a PR for this task', 'list my team's repos', 'report this task blocked to my orchestrator'. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(amp-*:*), Bash(jq:*), Bash(git:*), Read, Grep, Glob"
license: Apache-2.0
compatibility: Requires git, gh, and jq CLI tools, plus the installed amp-* scripts on PATH. macOS and Linux supported.
metadata:
  author: "Emasoft"
  version: "0.1.0"
---

# Agent Repository Workflow

## Overview

The development work-loop for an AI Maestro agent, driven entirely by the
frozen `amp-*` CLIs. A team member that has been dispatched a coding task runs
the same arc every time: get a repository (clone an existing one or create a
new one) → cut a working branch → do the work → open a pull request → report
back to the orchestrator that the task is done, or blocked. The repo/branch/PR
steps wrap `git` + `gh`; the project-discovery steps (`amp-project-info.sh`,
`amp-project-repos.sh`, `amp-team-members.sh`, `amp-list-local-repos.sh`) and
the reporting steps (`amp-task-done.sh`, `amp-task-blocked.sh`) talk to the AI
Maestro server and the team's AMP mesh, so the orchestrator always knows where
the work stands.

> **Recall first (proactive memory).** Before acting on a recurring problem, a design decision, or a repeated alert, recall prior lessons FIRST: `/janitor-memory-recall <symptom>` (shared wiki memory — index by the *symptom* / your words, not the fix's jargon) and `/memory-search <query>` (past discussion). See the proactive memory contract in the plugin `CLAUDE.md`.

## Prerequisites

Copy this checklist and track your progress:

- [ ] `amp-*` scripts installed to `~/.local/bin/` and on `PATH`
- [ ] Agent identity initialized (`amp-identity.sh` resolves; see the `agent-messaging` skill)
- [ ] CLI tools: `git`, `gh` (authenticated), `jq`
- [ ] AI Maestro server reachable (`AIMAESTRO_API`, default `http://localhost:23000`)
- [ ] Know your task's target repo + branch convention (ask the orchestrator if unset)

## Instructions

Run the work-loop in this order. Most steps accept `--id <uuid>` to act as a
specific agent; when omitted the agent identity is auto-resolved from config.

1. **Survey the project.** See what repos and teammates exist before starting:
   `amp-project-info.sh`, then `amp-project-repos.sh` and `amp-team-members.sh`.
2. **Get a repository.** Either clone an existing one
   (`amp-clone-repo.sh <url> [<localName>]`) or create a new one
   (`amp-create-repo.sh <name> [--org <org>] [--private] [--description "..."]`).
3. **List what you already have locally** if unsure where a clone landed:
   `amp-list-local-repos.sh`.
4. **Cut a working branch** off the base:
   `amp-create-branch.sh <repo-path> <branch-name>` (creates and pushes it).
5. **Do the work** — edit code, commit on the branch (normal `git`).
6. **Open the pull request:**
   `amp-submit-pr.sh <repo-path> <title> [--body "..."] [--base main]`.
7. **Report the outcome to the orchestrator** via AMP:
   - success → `amp-task-done.sh <message> [--id <agent-uuid>]`
   - blocked → `amp-task-blocked.sh <reason> [--id <agent-uuid>]` (high priority).

### Command reference

| Command (args from `# Usage:`) | Purpose |
|--------------------------------|---------|
| `amp-clone-repo.sh <url> [<localName>]` | Clone a repository into the agent's work directory |
| `amp-create-repo.sh <name> [--org <org>] [--private] [--description "..."]` | Create a GitHub repo (gh CLI) and register it with the team |
| `amp-create-branch.sh <repo-path> <branch-name>` | Create a branch and push it to origin |
| `amp-submit-pr.sh <repo-path> <title> [--body "..."] [--base main]` | Push the current branch and open a pull request |
| `amp-list-local-repos.sh` | List git repos in the agent's work directory (JSON) |
| `amp-project-info.sh [--team <teamId>] [--id <agentUUID>]` | Show team and project info for the current agent |
| `amp-project-repos.sh [--team <teamId>] [--id <agentUUID>]` | List repositories for a team's project |
| `amp-team-members.sh [--team <teamId>] [--id <agentUUID>]` | List team members with title and status |
| `amp-task-done.sh <message> [--id <agent-uuid>]` | Report task completion to the orchestrator (kanban `complete`) |
| `amp-task-blocked.sh <reason> [--id <agent-uuid>]` | Report a blocking issue to the orchestrator (kanban `blocked`) |

Every read/query script also accepts `--id <uuid>` to operate as a named agent;
the `--team <teamId>` flag is auto-detected from the agent registry when omitted.

## Output

- `amp-project-info.sh` / `amp-project-repos.sh` / `amp-team-members.sh` return
  the team's project, repos, and members (auto-detecting the team from your
  agent registry when `--team` is omitted).
- `amp-list-local-repos.sh` outputs repo metadata as JSON.
- `amp-clone-repo.sh` clones into the agent work directory; `amp-create-repo.sh`
  prints the new repo and registers it with the team.
- `amp-create-branch.sh` confirms the branch was created and pushed.
- `amp-submit-pr.sh` creates the PR and prints its URL.
- `amp-task-done.sh` / `amp-task-blocked.sh` send an AMP message to the
  orchestrator and confirm with a message ID.

## Error Handling

- **Identity not resolving** — verify `amp-identity.sh` first; initialize per the
  `agent-messaging` skill (`amp-init.sh --auto`). All these scripts resolve the
  agent ID from `--id` > `CLAUDE_AGENT_ID` > config.
- **`amp-create-branch.sh` errors "not a git repository"** — the `<repo-path>`
  has no `.git`; clone first or pass the correct path.
- **`amp-create-repo.sh` / `amp-submit-pr.sh` fail** — ensure `gh` is installed
  and authenticated (`gh auth status`).
- **Project/team queries return empty** — pass `--team <teamId>` explicitly if
  auto-detection from the agent registry yields nothing, and confirm the AI
  Maestro server (`AIMAESTRO_API`) is reachable.
- **PR has nothing to compare** — make sure the branch was pushed
  (`amp-create-branch.sh`) and has commits ahead of `--base`.

## Examples

```bash
# 1. Survey the project, then clone the repo the task targets.
amp-project-info.sh
amp-project-repos.sh
amp-clone-repo.sh https://github.com/org/repo.git
```

```bash
# 2. Start fresh: create a private repo with a description, then branch it.
amp-create-repo.sh my-new-repo --org myorg --private --description "A cool project"
amp-create-branch.sh /path/to/repo feature/new-api
```

```bash
# 3. Open a PR off a non-default base branch.
amp-submit-pr.sh . "Fix auth bug" --body "Fixes #42" --base develop
```

```bash
# 4. Report the outcome to the orchestrator.
amp-task-done.sh "API refactor complete, all tests pass"
amp-task-blocked.sh "Cannot access staging DB, credentials expired"
```

## Use also

- `Skill(skill: "agent-messaging")` — AMP inter-agent messaging (the transport
  `amp-task-done.sh` / `amp-task-blocked.sh` send over; inbox and reply flow).
- `Skill(skill: "team-kanban")` — the team task board where done/blocked land as
  column moves.
