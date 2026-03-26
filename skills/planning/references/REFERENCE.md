# Planning Skill Reference

## Table of Contents
- [Core Principle](#core-principle)
- [The 3-File Pattern](#the-3-file-pattern)
- [Output Directory Resolution](#output-directory-resolution)
- [The 6 Rules](#the-6-rules)
- [The 3-Strike Protocol](#the-3-strike-protocol)
- [When to Read vs Write](#when-to-read-vs-write)
- [The 5-Question Reboot](#the-5-question-reboot)
- [When to Use This Skill](#when-to-use-this-skill)
- [Anti-Patterns](#anti-patterns)
- [Integration with Memory Skill](#integration-with-memory-skill)
- [Templates](#templates)
- [Detailed Example Workflow](#detailed-example-workflow)
- [Troubleshooting](#troubleshooting)

---

## Core Principle

```
Context Window = RAM (volatile, limited, fast)
Filesystem = Disk (persistent, unlimited, explicit read required)

Anything important gets written to disk.
```

This skill solves the **execution problem** -- losing focus during complex tasks:

| Problem | Symptom | This Skill Fixes It |
|---------|---------|---------------------|
| Goal drift | Forgot original objective after 50 tool calls | Re-read plan before decisions |
| Lost progress | Can't remember what phase I'm in | Phase tracking in task_plan.md |
| Repeated errors | Make same mistake twice | Error log prevents repetition |
| Session loss | Can't resume after /clear | Planning files persist on disk |

**Note:** This is different from the Memory skill (which solves recall of past conversations). Planning solves staying focused NOW.

---

## The 3-File Pattern

Create these files in the output directory (not the project root or the skill directory):

| File | Purpose | Update When |
|------|---------|-------------|
| `task_plan.md` | Goals, phases, decisions, errors | After each phase |
| `findings.md` | Research, discoveries, resources | During research |
| `progress.md` | Session log, test results | Throughout session |

---

## Output Directory Resolution

Planning output files should be written to:

1. The directory specified by `AIMAESTRO_PLANNING_DIR` environment variable (if set)
2. Otherwise, `docs_dev/` in the current project root
3. Create the directory if it does not exist

Do NOT write planning files to the project root.

---

## The 6 Rules

### Rule 1: Create Plan First

**NEVER start a complex task without creating task_plan.md.**

Before writing any code or making any changes:
1. Create task_plan.md with clear goal
2. Break work into phases
3. List key questions to answer

### Rule 2: Read Before Decide

Before any major decision, re-read the plan:

```bash
cat "${AIMAESTRO_PLANNING_DIR:-docs_dev}/task_plan.md" | head -50
```

This refreshes your goals in the context window, preventing drift.

### Rule 3: Update After Act

After completing any phase:
- Mark phase as `[x]` complete
- Update status section
- Log any errors encountered
- Note files created/modified

### Rule 4: The 2-Action Rule

After every 2 search/view/browse operations, **immediately** save key findings to findings.md.

Visual content (screenshots, PDFs, browser results) doesn't persist in context. Write it down NOW.

### Rule 5: Log ALL Errors

Every error goes in task_plan.md:

```markdown
## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| FileNotFoundError | 1 | Created missing config |
| API timeout | 2 | Added retry with backoff |
```

This prevents repeating the same mistakes.

### Rule 6: Never Repeat Failures

```
if action_failed:
    next_action != same_action
```

After a failure, CHANGE your approach. Don't retry the exact same thing.

---

## The 3-Strike Protocol

**Attempt 1: Diagnose & Fix**
- Read error carefully
- Identify root cause
- Apply targeted fix

**Attempt 2: Alternative Approach**
- Same error? Try different method
- Consider different tools/libraries
- NEVER repeat exact failing action

**Attempt 3: Broader Rethink**
- Question assumptions
- Search for similar issues
- Update task plan with learnings

**After 3 Failures: Escalate**
- Explain all approaches tried
- Share specific error messages
- Ask user for guidance

---

## When to Read vs Write

| Situation | Action | Why |
|-----------|--------|-----|
| Just wrote a file | DON'T read | Content is in context |
| Viewed image/PDF | Write findings NOW | Visual content doesn't persist |
| Browser returned data | Write to findings.md | Screenshots don't persist |
| Starting new phase | Read task_plan.md | Re-orient from plan |
| Error occurred | Read relevant file | Need current state |
| Resuming after gap | Read ALL planning files | Recover context |

---

## The 5-Question Reboot

Lost? Answer these questions:

| Question | Find Answer In |
|----------|----------------|
| Where am I? | Current phase in task_plan.md |
| Where am I going? | Remaining phases in task_plan.md |
| What's the goal? | Goal section in task_plan.md |
| What have I learned? | findings.md |
| What have I done? | progress.md |

---

## When to Use This Skill

**USE for:**
- Multi-step tasks (3+ steps)
- Research projects
- Building features
- Tasks requiring >5 tool calls
- Anything needing organization

**SKIP for:**
- Simple questions
- Single-file edits
- Quick lookups
- Trivial changes

---

## Anti-Patterns

| DON'T | DO Instead |
|-------|------------|
| Use TodoWrite for complex tasks | Create task_plan.md file |
| State goals once and forget | Re-read plan before decisions |
| Hide errors and retry | Document errors in plan |
| Stuff everything in context | Store large content in files |
| Start executing immediately | Create plan FIRST |
| Repeat failed actions | Track attempts, change approach |

---

## Integration with Memory Skill

Planning and Memory solve **different problems**:

| Skill | Problem | Timescale |
|-------|---------|-----------|
| **Memory** | "What did we discuss last week?" | Days/weeks/months |
| **Planning** | "What am I supposed to do next?" | Minutes/hours |

Use BOTH for complex work:
1. **Memory** - Search for past decisions and context
2. **Planning** - Stay focused during execution

---

## Templates

Templates are in the skill's `templates/` directory:

- `task_plan.md` - Phase and progress tracking
- `findings.md` - Research and discoveries
- `progress.md` - Session logging

**Note:** The template path depends on how the skill was installed:
- **User scope** (global): `~/.claude/skills/planning/templates/`
- **Plugin scope**: `<plugin-cache>/skills/planning/templates/`
- **Project scope** (local): `<project>/.claude/skills/planning/templates/`

Copy to output directory and customize.

---

## Detailed Example Workflow

```
User: "Build a new authentication system"

1. CREATE PLAN
   - Copy templates to docs_dev/
   - Define goal: "Implement JWT authentication"
   - Break into phases: Research, Design, Implement, Test, Document

2. EXECUTE PHASE 1 (Research)
   - Search memory: memory-search.sh "authentication"
   - Search docs: docs-search.sh "auth patterns"
   - Write findings to findings.md
   - Mark Phase 1 complete in task_plan.md

3. EXECUTE PHASE 2 (Design)
   - READ task_plan.md (refresh goals)
   - READ findings.md (recall research)
   - Design approach, document decisions
   - Mark Phase 2 complete

4. CONTINUE...
   - Always read plan before major decisions
   - Always update after completing phases
   - Always log errors
```

---

## Troubleshooting

**Templates not found:**
```bash
ls ~/.claude/skills/planning/templates/
```
If missing, reinstall the skill or copy from AI Maestro plugin.

**Forgot the goal:**
```bash
cat "${AIMAESTRO_PLANNING_DIR:-docs_dev}/task_plan.md" | head -20
```

**Lost track of progress:**
```bash
grep -E "^\s*-\s*\[" "${AIMAESTRO_PLANNING_DIR:-docs_dev}/task_plan.md"
```
Shows all checkboxes and their status.
