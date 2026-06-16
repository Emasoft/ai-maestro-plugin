# TRDD v2 format — pointer to the canonical rule

## Contents

- Why this is a pointer, not a copy
- What lives WHERE (so you don't go looking in the wrong file)

> **Single source of truth.** The full TRDD v2 specification — filename format,
> the complete `column:` enum (the 14-stage kanban + `blocked` + the
> proposal-lifecycle overlay `proposal`/`planned`/`refused`/`cancelled`/
> `superseded`), NPT vs EHT semantics, the 8-char hash reference syntax, the
> STATE head block, and the v1→v2 migration — lives in the **bundled canonical
> rule** and is NOT duplicated here:
>
> **`${CLAUDE_PLUGIN_ROOT}/rules/trdd-design-tasks.md`**
>
> That same file is auto-installed to `~/.claude/rules/trdd-design-tasks.md` at
> session start, so every agent already has the full text in context. Read the
> bundled rule for anything this page references.

## Why this is a pointer, not a copy

The four governance rules (`trdd-design-tasks`, `prrd-design-rules`,
`trdd-approval-tiers`, `manager-approval-defaults`) are bundled ONCE in
`${CLAUDE_PLUGIN_ROOT}/rules/` and auto-installed every session. Re-pasting the
rule text into a skill reference would create a second copy that drifts. So this
reference is a thin redirect: it exists only so the relative links from the
co-located mechanics references (`column-transitions.md`,
`approval-tiers-and-zones.md`, `trdd-frontmatter-schema.md`) resolve to a real
file, while the authoritative text stays in one place.

## What lives WHERE (so you don't go looking in the wrong file)

| You want… | Read |
|---|---|
| The full TRDD v2 spec / column enum / NPT-EHT / STATE block | `${CLAUDE_PLUGIN_ROOT}/rules/trdd-design-tasks.md` (canonical) |
| The field-by-field frontmatter schema (types, defaults, validation) | [trdd-frontmatter-schema.md](trdd-frontmatter-schema.md) |
| Who can move a TRDD column X→Y + side effects + AMP | [column-transitions.md](column-transitions.md) |
| The 4 design zones + `proposal → planned` lifecycle + tier ladder | [approval-tiers-and-zones.md](approval-tiers-and-zones.md) |
| The EXEMPT / NON-EXEMPT operation lists + approval-request template | [exempt-operations.md](exempt-operations.md) |
| GOLDEN / SILVER rule format + citation grammar | `${CLAUDE_PLUGIN_ROOT}/rules/prrd-design-rules.md` (canonical) |
