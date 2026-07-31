---
trdd-id: 5TJDVWAP
title: Claude Code v2.1.170 → v2.1.191 changelog ecosystem-sync review
column: complete
created: 2026-06-25T19:37:09+0200
updated: 2026-06-25T19:37:09+0200
current-owner: null
assignee: null
priority: 4
severity: LOW
effort: S
task-type: audit
parent-trdd: null
relevant-rules: []
release-via: none
test-requirements: []
audit-requirements: []
review-requirements: []
impacts: []
audit-trigger: user-report
audit-target: ai-maestro-plugin (skills, commands, hooks, plugin.json)
audit-conclusion: benign
external-refs: ["https://code.claude.com/docs/en/changelog.md"]
---

# TRDD-5TJDVWAP — Claude Code v2.1.170 → v2.1.191 changelog ecosystem-sync review

**Tracked in:** this repo (design/tasks/ is git-tracked)
**Trigger:** USER — "big changes to Claude Code impacting the whole plugins/extensions
ecosystem; read all updates since v2.1.170 → v2.1.191 and update the plugin accordingly."
**Source:** https://code.claude.com/docs/en/changelog.md (fetched 2026-06-25)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-25

- **Outcome:** the changelog v2.1.170→v2.1.191 requires **NO source edit** to this
  plugin. Every ecosystem-impacting item was checked against the actual source
  (skills/, commands/, hooks/hooks.json, .claude-plugin/plugin.json, rules/, CLAUDE.md)
  and found **not-applicable**. Recorded as a clean audit, not a code change.
- **NEXT ACTION:** none (audit complete). 2 informational/integration items noted below
  for future awareness — no edit needed now.
- This is the recurring "changelog-sync" chore; the prior instance was the completed
  task #38 (an earlier version range). This TRDD is the v2.1.170→191 delta record so a
  future session does NOT re-derive the analysis.

## Method (facts, not assumptions)

Fetched the changelog and extracted every entry in [2.1.170, 2.1.191]. Filtered the
TUI/model-picker/background-session/MCP-reliability noise from the items that can affect
**plugin authoring** (skills, agents, commands, hooks, MCP specs, settings/permission
rules, plugin.json, marketplace, model IDs). Each candidate was grepped against the
real source before any conclusion.

## Verification matrix — ecosystem-impacting items vs this plugin

| Changelog item (version) | Could affect a plugin? | This plugin? | Verdict |
|---|---|---|---|
| `TeamCreate`/`TeamDelete` tools **removed**; `team_name` Agent param **ignored**; teams implicit via Agent `name` (2.1.178) | Yes — for plugins using CC agent-teams | `rg TeamCreate\|TeamDelete\|team_name` over skills/commands/hooks/rules/CLAUDE.md = **0 hits**. The plugin's "teams" are the **AI-Maestro server governance** concept (`aimaestro-teams.sh create/delete`, closed teams + COS + role-plugins), NOT the CC Agent-tool teams. | **Not affected** |
| Comma-separated hook matchers (`"Bash,PowerShell"`) silently never fired (fixed 2.1.191) | Yes — for hooks.json comma matchers | hooks.json uses **pipe** matchers exclusively (`"Bash\|Write\|Edit\|NotebookEdit"`, `"idle_prompt\|permission_prompt"`). Zero comma matchers. | **Not affected** |
| Skill frontmatter keys accept kebab/snake/camel case; malformed YAML now loads with **empty** metadata (2.1.186) | Yes — malformed frontmatter silently loses name/desc/triggers | All 23 skills have well-formed frontmatter with `name:` + `description:` (checked every `skills/*/SKILL.md`); 0 malformed. Case-tolerance is permissive (no required change). | **Not affected** |
| `/review <pr>` → `/code-review medium` engine (2.1.186) | Only if plugin ships a `/review` wrapper | No `/review` command shipped (the one "review" hit is the word in a governance self-id rule). | **Not affected** |
| Hook `if` Read/Edit/Write path patterns + `WebFetch(domain:*.x)` / mid-pattern wildcard permission rules fixed (2.1.176 / 2.1.172) | Only if plugin ships settings.json permission rules / hook `if` conditions | No settings.json shipped; hooks.json uses no `if` conditions. | **Not affected** |
| MCP server-level specs in `disallowedTools` now honored; nested `.claude/skills` `<dir>:<name>` clash naming (2.1.178) | Only if plugin uses disallowedTools / nested skills | No `disallowedTools`/`allowedTools` in source; skills are flat under `skills/`. | **Not affected** |
| Fable 5 `[1m]` suffix normalization; model-picker / `availableModels` fixes (2.1.170–2.1.176) | Only if plugin hardcodes model IDs | No hardcoded `claude-*` model IDs in skills/commands/rules/docs. CLAUDE.md model knowledge already current. plugin.json declares no `model:`. | **Not affected** |
| Sub-agents can spawn sub-agents, 5 levels deep (2.1.172) | Capability, not a breaking change | Informational — the janitor subconscious agent + spark fan-outs benefit; no edit. | **Not affected** |

## Informational / integration notes (no edit required now)

1. **v2.1.183 — auto-mode now natively blocks destructive git** (`git reset --hard`,
   `git checkout -- .`, `git clean -fd`, `git stash drop`, unrequested `git commit --amend`,
   `terraform/pulumi/cdk destroy`). This **backstops** the plugin's `directory-guard.cjs`
   defense-in-depth posture rather than conflicting with it — the guard remains the
   plugin-side sandbox; CC's classifier is now a second layer. No change.
2. **v2.1.183 — scheduled-task / webhook-trigger deliveries are now classified as task
   notifications and can NOT approve a pending action or set the session title in auto
   mode.** This independently **confirms the janitor heartbeat-cron security model**
   (a heartbeat delivery is not user authorization — RULE 1.5/1.6 and the marker
   security rule). No change; reinforces existing design.
3. **v2.1.178 — new `Tool(param:value)` permission syntax** (e.g. `Agent(model:opus)` to
   block Opus subagents, `*` wildcard). A genuinely new capability. Not adopted: the
   plugin ships no settings.json permission rules and its governance skills cover the
   AI-Maestro server layer, not CC permission-rule authoring. Candidate for a future
   doc note only if a CC-permissions skill is ever added.

## Conclusion

Changelog v2.1.170→v2.1.191 reviewed in full; **no plugin source change is warranted**.
Manufacturing edits to "match" a changelog whose breaking items don't touch this plugin
would violate the "only what is strictly necessary" mandate. The audit is the
deliverable. The 3 informational items are captured for future awareness.
