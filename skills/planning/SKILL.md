---
name: planning
description: "Persistent markdown planning files for complex tasks. Use when starting multi-step tasks needing 5+ tool calls. Trigger with /planning."
allowed-tools: "Bash(mkdir:*), Bash(cat:*), Bash(grep:*), Bash(ls:*), Read, Write, Edit, Glob, Grep"
metadata:
  author: "Emasoft"
  version: "2.0.0"
  user-invocable: "true"
---

## Overview

Creates and manages 3 persistent markdown files (task_plan.md, findings.md, progress.md) that keep you focused during complex tasks. Solves goal drift, lost progress, and repeated errors by externalizing state to disk.

## Prerequisites

- Bash shell access
- Write access to project's `docs_dev/` directory (or `AIMAESTRO_PLANNING_DIR`)
- Templates in skill's `templates/` directory

## Instructions

1. **Set output directory**:
   ```bash
   PLAN_DIR="${AIMAESTRO_PLANNING_DIR:-docs_dev}" && mkdir -p "$PLAN_DIR"
   ```

2. **Copy templates**:
   ```bash
   cat <skill-path>/templates/task_plan.md > "$PLAN_DIR/task_plan.md"
   cat <skill-path>/templates/findings.md > "$PLAN_DIR/findings.md"
   cat <skill-path>/templates/progress.md > "$PLAN_DIR/progress.md"
   ```

3. **Edit task_plan.md** — define goal, break into phases, list key questions.

4. **Execute phases** — for each phase:
   - Re-read task_plan.md before major decisions (prevents drift)
   - Save findings to findings.md every 2 search operations
   - Mark phases `[x]` complete, log errors with attempt number

5. **On failure** — 3-Strike Protocol: diagnose, try alternative, rethink, escalate after 3 failures.

6. **On resumption** — read ALL 3 files to recover context after session gap.

## Output

- `task_plan.md`: Goals, phases, decisions (update after each phase)
- `findings.md`: Research discoveries (update during research)
- `progress.md`: Session log, test results (update throughout session)

## Error Handling

- **Templates not found**: Check `ls <skill-path>/templates/`
- **Dir not writable**: Set `AIMAESTRO_PLANNING_DIR` to writable path
- **Lost track**: Check task_plan.md checkboxes:
  ```bash
  grep -E "^\s*-\s*\[" "$PLAN_DIR/task_plan.md"
  ```
- **3 consecutive failures**: Stop, document all attempts, escalate to user

## Examples

```
/planning "Build JWT authentication system"
```
Creates 3 files in docs_dev/, task_plan.md populated with goal broken into phases.

```
/planning "Migrate database from Postgres to SQLite"
```
Creates planning files with migration-specific phases.

## Checklist

Copy this checklist and track your progress:

- [ ] Create output directory
- [ ] Copy 3 template files
- [ ] Edit task_plan.md with goal and phases
- [ ] Execute phases, updating findings.md and progress.md
- [ ] Mark phases complete, log errors
- [ ] Re-read task_plan.md before each new phase
- [ ] Final review: all phases complete

## Resources

- [Detailed Reference](references/REFERENCE.md) - The 6 Rules, 3-Strike Protocol, When to Read vs Write, 5-Question Reboot, Anti-patterns, Memory skill integration
