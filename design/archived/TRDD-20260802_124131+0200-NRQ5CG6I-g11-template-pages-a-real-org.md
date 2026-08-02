---
trdd-id: NRQ5CG6I
title: PRRD G1.1's mandated self-ID line pages a real third-party GitHub organization
column: complete
created: 2026-08-02T12:41:31+0200
updated: 2026-08-02T13:02:00+0200
current-owner: core-session
task-type: security
min-approval-requirement: user
approved: true
relevant-rules: [1]
implementation-commits: [acbea84]
npt: []
eht: []
---

## Approval log

- 2026-08-02 — **APPROVED by USER** (min-approval-requirement: user). Directive, verbatim:
  *"when writing in github issues and comments never use the `@<name>` syntax outside of a
  code block, since it triggers paging of other users! Someone paged a `@manager` user and a
  `@janitor` user by error!"* — the USER stated the governing rule, which both authorizes the
  golden-rule edit and settles the A/B/C choice in favour of backticking. Executed in
  `acbea84`: G1.1 → **G1.2**, handle pre-substituted and backticked, prohibition written into
  the rule, all 7 citations re-pinned, executable guard added.

## Resolution — what shipped

Two handles beyond the two this card originally found were also being paged
(`@manager`, `@janitor`, reported by the USER). **All six AI Maestro role names resolve to
real GitHub accounts** — `@manager`/`@janitor` are Users, `@owner`/`@role`/`@core`/
`@orchestrator` are Organizations — so the exposure was the whole role vocabulary, not two
placeholders.

`tests/test_no_bare_github_mentions.py` makes it executable, and **caught its own author
within minutes**: writing the warning into `team-governance/SKILL.md` I typed an illustrative
bare `@manager` in prose. Knowing the rule is demonstrably not sufficient.

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

This is not hypothetical, and it is **ACTIVE — it fired again while this card was being
written.** Measured 2026-08-02:

| when | handle | resolves to | where |
|---|---|---|---|
| `05:51:22Z` | `@owner` | **REAL Organization** | [janitor#106 comment](https://github.com/Emasoft/ai-maestro-janitor/issues/106#issuecomment-5155760825) — **ai-maestro-autonomous-agent**, `(via the shared @owner gh auth)` verbatim |
| `10:41:37Z` | `@role` | **REAL Organization "ROLE"** | [plugin#36 comment](https://github.com/Emasoft/ai-maestro-plugin/issues/36#issuecomment-5157261596) — another agent, minutes after the USER complained |

**ONE golden line is the source of BOTH.** `PRRD.md:30` carries the `@owner` self-ID template
*and* the `Agent: <role>` commit-trailer guidance; grep confirms it is the only site in CORE
for either. Verified with `gh api users/<h>`:

```
@owner              REAL — owner (Organization)
@role               REAL — ROLE  (Organization)
@gmail              REAL — gmail (User)          <- via `fmuaddib@gmail.com` in comment bodies
@ai-maestro-plugins does not exist (safe)
```

**CORE hosts the rule, so CORE hosts the cause.** Every plugin in the fleet inherits G1.1, and
the two pages above came from two *different* agents — so this is a class defect, not one
agent misbehaving. **The rate is roughly one third-party page per few hours of fleet activity.**

## Why a placeholder that is a valid username is the actual bug

`<plugin-or-role>` is safe: the angle brackets make it obviously a slot, and no agent posts it
literally. `@owner` and `@role` are unsafe for the opposite reason — they *look* like finished
text, so an agent reasonably copies them as-is. **A template is only safe if its literal form
is harmless**, because literal pasting is the expected failure mode, not an aberration.

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

**The `Agent: <role>` trailer needs the same treatment** — it is on the same line and produced
the `@role` page. Written as `` `Agent: <role>` `` (backticked) it cannot linkify either.

**Recommendation: B + backtick the trailer.** It fixes all three failures at once — the
stranger-pages (`@owner`, `@role`) *and* the owner-page (`@Emasoft`) — and it deletes the
substitution step that actually failed. Neither agent misunderstood the rule; each copied a
template whose placeholder is itself a valid GitHub account. **A template whose literal form
is harmful will keep being pasted literally**, so the fix has to be in the template, not in
the agents.

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
