# TRDD-9e80e484-221a-4b2c-a252-b5820af4ea19 — Sibling-skill prose-pointer weakness

**TRDD ID:** `9e80e484-221a-4b2c-a252-b5820af4ea19`
**Filename:** `design/tasks/TRDD-9e80e484-221a-4b2c-a252-b5820af4ea19-sibling-skill-prose-pointer-weakness.md`
**Tracked in:** this repo (design/tasks/ is git-tracked)
**Source audit:** `reports/v258-pre-publish-audit/skeptical-review.md` (SR-002)
**Severity:** FIX_BEFORE_NEXT (UX / discoverability — non-blocking, deferred to v2.5.9)
**Status:** Not started
**Filed:** 2026-05-08

## Problem

Earlier governance commits (a903ed3) collapsed sibling cross-links from
explicit `Skill(...)` invocations to prose pointers ("see the
team-governance skill"), to fit the 5000-char SKILL.md ceiling. Prose
pointers are not parseable by the skill-loading mechanism — they're a
docs convention, not an automatic link.

A user pasting an agent-identity skill into a fresh session won't see
agent-messaging recommended unless they happen to read the prose. The
collapsed cross-links create a navigation gap that the 5000-char limit
forced.

## Design

### Approach A — Inline `Use also:` line at bottom of each governance SKILL.md

Each of agent-identity, agent-messaging, ai-maestro-agents-management,
team-governance, team-kanban gets a one-line footer:

```
Use also: `Skill(skill: "agent-messaging")`, `Skill(skill: "team-governance")`.
```

Cost: ~80-120 chars per skill. team-governance has 24 chars of slack,
so this requires reclaiming budget elsewhere first (compress Resources
TOC per A11.6).

### Approach B — Move cross-link table to references/skill-graph.md

Create a single file at `references/skill-graph.md` with a table of all
governance-tier skills and their relationships. Each SKILL.md adds one
prose pointer: "Sibling skills: see `[skill-graph](../references/skill-graph.md)`."
(The pointer is shown as inline code here because the target file is
proposed by this approach and does not exist yet.)

Cost: ~30-50 chars per skill (cheaper). Con: indirection — the LLM
auto-loader reads SKILL.md, sees the prose pointer, and may not follow
the link to skill-graph.md without explicit instruction.

### Approach C — Hybrid

`team-governance/SKILL.md` (highest stakes, tightest budget) gets
Approach B. The other four (which have more slack) get Approach A.

## Recommendation

**Approach C.** team-governance has 24 chars of slack and competing
demands (TRDD-9f10ed97 wants to expand Examples, which already needs
TOC compression). The other four have plenty of room for inline
`Use also:` footers.

## Acceptance criteria

- [ ] team-governance/SKILL.md keeps a prose-pointer plus a link to
  `references/skill-graph.md` (which lists all governance siblings)
- [ ] agent-identity, agent-messaging, ai-maestro-agents-management,
  team-kanban each have a `Use also:` footer with at least 2
  `Skill(skill: "...")` examples
- [ ] All 5 SKILL.md files remain within the 5000-char CPV ceiling
- [ ] CPV strict PASS

## Dependencies

- **Loosely related: TRDD-9f10ed97-…** (team-governance Examples
  expansion). Both want to compress the team-governance Resources TOC.
  Land them in the same release to avoid two passes over the same file.

## Out of scope

- Auto-generating the `Use also:` footer from a manifest (would force a
  build step on every SKILL.md edit; not worth it for 5 files)
- Adding sibling-pointer footers to non-governance skills (debug-hooks,
  docs-search, etc. — those don't form a tight cross-skill graph the
  way governance does)
