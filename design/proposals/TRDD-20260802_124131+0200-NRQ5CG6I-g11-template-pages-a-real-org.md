---
trdd-id: NRQ5CG6I
title: PRRD G1.1's mandated self-ID line pages a real third-party GitHub organization
column: proposal
created: 2026-08-02T12:41:31+0200
updated: 2026-08-02T12:41:31+0200
current-owner: core-session
task-type: security
min-approval-requirement: user
relevant-rules: [1]
npt: []
eht: []
---

# G1.1's template literal `@owner` pages a real GitHub organization

## Why this is a PROPOSAL and not a fix

**G1.1 is GOLDEN.** Per `~/.claude/rules/prrd-design-rules.md`, a golden rule is set by the
USER and immutable to everyone else — *"not even the MANAGER may edit, add, delete, promote,
or demote a golden rule. An agent that thinks one is wrong files a **proposal** and waits for
the user."* So this card exists instead of a commit. **Do not "just fix" it** — the fix is one
line and the temptation to apply it is exactly what the golden tier exists to prevent.

## The defect

`design/requirements/PRRD.md:30` mandates that every agent writing to GitHub open with:

```text
_Posted by the Claude developing **<plugin-or-role>** (via the shared @owner gh auth)._
```

`@owner` is written **un-backticked**, so GitHub linkifies it. **`@owner` is a real GitHub
Organization** (verified: `gh api users/owner` → `login: owner, type: Organization`). Every
agent that pastes the template verbatim — rather than substituting the real handle — **pages
an unrelated third party**.

This is not hypothetical. Measured 2026-08-02:

| when | where | who |
|---|---|---|
| `05:51:22Z` | [ai-maestro-janitor#106 comment](https://github.com/Emasoft/ai-maestro-janitor/issues/106#issuecomment-5155760825) | the **ai-maestro-autonomous-agent** Claude, line reading `(via the shared @owner gh auth)` verbatim |

**CORE hosts the rule, so CORE hosts the cause.** Every plugin in the fleet inherits G1.1.

## Second-order: the substituted form pages the OWNER on every post

Substituting correctly gives `@Emasoft` — still un-backticked, so every compliant comment
mentions the owner and notifies them. **7 of this session's own comments did exactly that.**
Not a stranger, but unrequested noise, and the USER's directive (2026-08-02) was explicitly to
restrict this communication.

## Proposed change (USER decides; three options, all one line)

Backticks are the minimal fix: **GitHub does not linkify inside a code span**, so a backticked
handle renders visibly but pages nobody.

| # | G1.1's recommended line becomes | pages |
|---|---|---|
| A | ``(via the shared `@owner` gh auth)`` — backticked, handle still substituted | nobody |
| B | ``(via the shared `@Emasoft` gh auth)`` — backticked **and** pre-substituted, removing the substitution step agents get wrong | nobody |
| C | `(via the shared Emasoft gh auth)` — no `@` at all; survives any renderer that ignores code spans | nobody |

**Recommendation: B.** It fixes both failures at once — the stranger-page *and* the
owner-page — and it deletes the step that actually failed. The agent that broke this did not
misunderstand the rule; it copied a template containing a placeholder that is itself a valid
username. A template whose literal form is harmful will keep being pasted literally.

## Scope of the change if approved

- `design/requirements/PRRD.md:30` — the G1.1 text, **version bump `G1.1` → `G1.2`** (editing
  the text bumps the version; the number and tier are unchanged).
- `skills/team-governance/references/GOVERNANCE-RULES.md:1230` — the second shipped site
  carrying the same literal (2 total in CORE; verified by grep).
- Fleet notification so other plugins stop pasting the old form — **held**, because it means a
  GitHub write and the USER objected to exactly that while away.

## Acceptance

- [ ] USER picks A, B, or C (or rejects)
- [ ] Both CORE sites updated; `grep -rn '@owner' design/ skills/ commands/` returns only
      backticked or `@`-free forms
- [ ] Version bumped to `G1.2`, and every `PRRD G1.1` citation in the repo re-pinned
- [ ] An executable guard fails on any shipped file teaching a **bare** `@handle` that resolves
      to a real account — **NOT written yet on purpose**: it would flag `PRRD.md:30` and be born
      red, and a permanently-red gate gets suppressed within a week. It lands *with* the fix.
- [ ] Decide whether to notify `ai-maestro-autonomous-agent` (a GitHub write — USER's call)

## Notes

- `tj/commander.js` appeared in this account's 24h activity and was checked: a `WatchEvent`
  (a **star**), not a comment. Stars page nobody. It is NOT part of this defect.
- The audit that found this also cleared this session: 27 comments, 2 repos, both
  Emasoft-owned, `@Emasoft` the only mention. The stranger-page came from another agent.
