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

Creates and manages 3 persistent markdown files (task_plan.md, findings.md, progress.md) that keep you focused during complex task execution. Solves the execution problem: goal drift, lost progress, and repeated errors by externalizing state to disk. Different from Memory skill (past recall) -- Planning keeps you focused NOW.

## Prerequisites

- Bash shell access for `mkdir` and `cat` commands
- Write access to project's `docs_dev/` directory (or `AIMAESTRO_PLANNING_DIR`)
- Templates available in skill's `templates/` directory

## Instructions

1. **Determine output directory**: Use `AIMAESTRO_PLANNING_DIR` env var if set, otherwise `docs_dev/` in project root. Create it if missing:
   ```bash
   PLAN_DIR="${AIMAESTRO_PLANNING_DIR:-docs_dev}"
   mkdir -p "$PLAN_DIR"
   ```

2. **Copy templates** to output directory:
   ```bash
   cat <skill-path>/templates/task_plan.md > "$PLAN_DIR/task_plan.md"
   cat <skill-path>/templates/findings.md > "$PLAN_DIR/findings.md"
   cat <skill-path>/templates/progress.md > "$PLAN_DIR/progress.md"
   ```

3. **Edit task_plan.md**: Define your goal, break work into phases, list key questions.

4. **Execute phases**: For each phase:
   - Re-read task_plan.md before major decisions (prevents drift)
   - After every 2 search/browse operations, save findings to findings.md
   - Mark phases `[x]` complete, log errors with attempt number and resolution
   - Update progress.md with session activity

5. **On failure**: Follow the 3-Strike Protocol -- diagnose, try alternative, rethink, then escalate after 3 failures. Never repeat the exact same failing action.

6. **On resumption**: Read ALL 3 planning files to recover context after /clear or session gap.

## Output

Three markdown files in the output directory:

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `task_plan.md` | Goals, phases, decisions, error log | After each phase |
| `findings.md` | Research discoveries, resources | During research |
| `progress.md` | Session log, test results | Throughout session |

## Error Handling

- **Templates not found**: Check skill installation with `ls <skill-path>/templates/`
- **Output dir not writable**: Verify permissions or set `AIMAESTRO_PLANNING_DIR` to writable path
- **Lost track of goal**: Run `cat "$PLAN_DIR/task_plan.md" | head -20`
- **Lost track of progress**: Run `grep -E "^\s*-\s*\[" "$PLAN_DIR/task_plan.md"` to see checkboxes
- **3 consecutive failures on same step**: Stop, document all attempts, escalate to user

## Examples

```
/planning "Build JWT authentication system"
```

Expected: Creates 3 files in docs_dev/, task_plan.md populated with goal "Build JWT authentication system" broken into phases (Research, Design, Implement, Test, Document).

```
/planning "Migrate database from Postgres to SQLite"
```

Expected: Creates planning files, goal set, phases defined for migration workflow.

## Checklist

Copy this checklist and track your progress:
- [ ] Determine output directory (env var or docs_dev/)
- [ ] Create output directory if missing
- [ ] Copy 3 template files to output directory
- [ ] Edit task_plan.md with specific goal and phases
- [ ] Execute Phase 1, update findings.md and progress.md
- [ ] Mark Phase 1 complete, log any errors
- [ ] Re-read task_plan.md before starting Phase 2
- [ ] Continue through all phases
- [ ] Final review: all phases marked complete

## Resources

- [Detailed Reference](references/REFERENCE.md) - Full planning methodology
  - The 6 Rules (Create Plan First, Read Before Decide, Update After Act, 2-Action Rule, Log Errors, Never Repeat Failures)
  - The 3-Strike Protocol for handling failures
  - When to Read vs Write decision table
  - The 5-Question Reboot for getting unstuck
  - Anti-patterns and integration with Memory skill
  - Troubleshooting guide
