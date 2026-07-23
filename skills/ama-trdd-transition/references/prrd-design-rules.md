# PRRD format — pointer to the canonical rule

## Contents

- Why this is a pointer, not a copy
- The one fact every `ama-prrd-*` skill enforces

> **Single source of truth.** The full PRRD specification — the GOLDEN (USER-only)
> vs SILVER (MANAGER-mutable) split, the `<letter><number>.<version>` rule
> identity, promote/demote semantics, the `PRRD G64.134` citation grammar, the
> proposal queue, and the mutation-authority table — lives in the **bundled
> canonical rule** and is NOT duplicated here:
>
> **`~/.claude/rules/prrd-design-rules.md`**
>
> That same file is shipped globally by the ai-maestro-janitor (IND base) at
> session start, so every agent already has the full text in context.

## Why this is a pointer, not a copy

The governance rules live at their canonical homes (janitor IND bases in
`~/.claude/rules/`, ai-maestro DEP overlays in each agent workdir's
`.claude/rules/`); re-pasting the rule text here would create a
second copy that drifts. This reference exists only so the relative links from
co-located mechanics references resolve to a real file, while the authoritative
text stays in one place.

## The one fact every `ama-prrd-*` skill enforces

- **GOLDEN rules are USER-only.** No agent — not even MANAGER — may edit, add,
  delete, promote, or demote a GOLDEN rule. Agents `propose` instead.
- **SILVER rules are MANAGER-mutable.** MANAGER edits directly; every other role
  `propose`s (team-internal agents route via their COS).
- Both facts are enforced at the script layer by
  `prrd_lib.caller_is_manager()` (and the USER-only check on promote/demote).
  The `ama-prrd-edit` skill refuses a non-MANAGER SILVER edit and routes to
  `ama-prrd-propose`; GOLDEN edits are refused for everyone but the USER.

See `~/.claude/rules/prrd-design-rules.md` for the complete model.
