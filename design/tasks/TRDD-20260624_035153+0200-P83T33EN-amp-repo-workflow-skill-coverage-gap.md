---
trdd-id: P83T33EN
title: Close the script↔skill coverage gap — new agent-repo-workflow skill for the uncovered AMP work-loop scripts
column: complete
created: 2026-06-24T03:51:53+0200
updated: 2026-06-24T03:58:13+0200
current-owner: ai-maestro-plugin
implementation-commits: [a401719]
assignee: ai-maestro-plugin
priority: 2
severity: HIGH
effort: M
task-type: feature
labels: [coverage, skills, amp, fleet-readiness]
relevant-rules: []
release-via: publish
test-requirements: [lint]
review-requirements: []
impacts: []
external-refs: ["Emasoft/ai-maestro#35", "Emasoft/ai-maestro-plugin (this repo)"]
---

# TRDD-P83T33EN — Close the script↔skill coverage gap (agent-repo-workflow skill)

## Problem (verified, not assumed)

The USER's directive: "the core plugin's skills must cover all the scripts
functionalities of ai-maestro." A fact-based audit (deployed `~/.local/bin`
skill-facing surface vs `grep` of every `skills/*/SKILL.md` reference) found a
real, significant gap. The plugin covers messaging (`agent-messaging` →
`amp-{send,inbox,read,reply,…}`), kanban (`team-kanban` → `amp-kanban-*`),
identity (`agent-identity` → `aid-*`), and the frozen governance/agent CLIs
(`team-governance`, `ai-maestro-agents-management` → `aimaestro-*.sh`). But an
entire **agent development work-loop** is deployed and agent-facing yet covered
by NO skill (each confirmed a CLI by its `# Usage:` header, not an internal lib):

| Script | Purpose |
|---|---|
| `amp-clone-repo.sh` | Clone a repo into the agent's work dir (`--id <uuid> <git-url>`) |
| `amp-create-repo.sh` | Create a GitHub repo + register with the team (`<name> [--org] [--private] [--description] [--team]`) |
| `amp-create-branch.sh` | Create + push a new git branch |
| `amp-submit-pr.sh` | Open a PR from the current branch (`<repo-path> <title> [--body] [--base]`) |
| `amp-list-local-repos.sh` | List git repos in the agent's work dir |
| `amp-project-info.sh` | Show team + project info |
| `amp-project-repos.sh` | List project repositories |
| `amp-task-done.sh` | Report task completion to the Orchestrator (`<message> [--id]`) |
| `amp-task-blocked.sh` | Report a blocking issue to the Orchestrator |
| `amp-team-members.sh` | List team members with details (`[--team] [--id]`) |

Plus one stray AMP command (`amp-register.sh` — register with an external
provider) that belongs in the existing `agent-messaging` command reference.
`amp-security.sh` / `amp-helper.sh` are internal libs (correctly NOT skill-faced).

## Why this matters

An agent that loads the core plugin can message and run kanban, but has NO
documented way to clone the repo it was assigned, branch, open a PR, or report
done/blocked to its orchestrator — the core loop of doing actual work. The
scripts exist and are frozen-contract (ai-maestro#35); only the skill coverage
is missing.

## Design

Two changes, minimal + cohesive (no bloat):

1. **NEW skill `skills/agent-repo-workflow/SKILL.md`** — covers the 10 work-loop
   scripts as one coherent capability: *clone/create repo → branch → work →
   submit PR → report done/blocked*, plus the repo/project/team context queries.
   CPV-compliant: frontmatter (`user-invocable: false`, `allowed-tools:
   "Bash(amp-*:*), Bash(jq:*), Read, Grep, Glob"`), Overview, the recall-first
   blockquote (core#14 house style), Prerequisites, Instructions (the work-loop
   order), a command-reference table, Examples, Error Handling, Resources, and a
   `## Use also` footer to agent-messaging + team-kanban.
2. **EXTEND `skills/agent-messaging/SKILL.md`** — add `amp-register.sh` to the
   command reference (external-provider registration; it already documents
   `amp-fetch.sh` for external providers).

Each script's frozen CLI contract is read from its `# Usage:` header in
`~/.local/bin/<script>` (source of truth on this host; reconcile with the
canonical frozen manifest requested on ai-maestro#35 when it lands).

## Acceptance criteria

- [ ] `skills/agent-repo-workflow/SKILL.md` exists, CPV-strict clean, documents
      all 10 work-loop scripts with accurate args from their `# Usage:` headers
- [ ] `agent-messaging` command reference includes `amp-register.sh`
- [ ] README skill list (if any) updated to include the new skill
- [ ] No skill references a non-existent / renamed script
- [ ] CPV `--strict` PASS at publish (publish.py G3)

## Coordination

- ai-maestro#35 (script↔skill sync): this closes the plugin-side gap for the
  AMP work-loop family. Posting the concrete uncovered list there + noting the
  new skill; will reconcile against the canonical frozen manifest when provided.

## Out of scope

- Internal libs (`amp-security.sh`, `amp-helper.sh`, `agent-*.sh`, `aid-helper.sh`).
- The frozen-CLI verb core#11 waits on (separate, ai-maestro#45).
- Rebuilding the messaging/kanban/identity skills (already cover their families).
