---
version: "3.9.1"
date: 2026-05-06
branch: feature/phase6-jsonl-rebase-test
changelog:
  - "3.9.1: Codified the canonical agent-address format (R6.11–R6.14). Single ID string per host, wire format `<agent-id>@<host>` or `<host>:<agent-id>`, with bare `<agent-id>` defaulting to the writer's host. Persona name may alias the agent-id when no collision exists on the target host (R6.12); on collision, the API returns 409 `disambiguation_required`. The legacy 3-level hierarchical addressing (`team/sub/name`) is now formally deprecated for messaging — it survives only as the sidebar's visual tag organization. R6.14 mandates UI + persona-prompt migration across this repo and the 8 role-plugin repos."
  - "3.9.0: Expanded R21 to be the SINGLE COMPLETE source for All-In-One pipeline architecture (IRON). Folded in every AIO rule that previously lived only in the `make-all-in-one` skill: the 3 absolute rules (one-function-per-operation, helpers-must-be-pure, auth-inside-not-outside), the full gate architecture (G00-G99 / EXE / PG01-PG99 numbering, atomic gates, error-reporting by gate code), pre-gate / post-gate canonical sequences, the variant-specific `[VariantName]` bracket convention, the idempotency-gate pattern, the protected-resource four-layer defense, the result contract, the caller contract, the anti-pattern table, and the consolidation procedure. The user's 2026-05-06 composition directive remains verbatim at the top of R21 as load-bearing. With this expansion, GOVERNANCE-RULES.md is the canonical source for governance + AIO + communication rules; only scenario rules stay separate (`tests/scenarios/SCENARIOS_TESTS_RULES.md`) because they depend on per-user tooling choices (browser stack, headless vs visible, etc.)."
  - "3.8.0: Added R21 (All-In-One Pipeline Composition). Codifies the IRON rule that AIO API functions MUST call other AIOs internally when they need to perform a task another AIO already covers — never duplicate logic, never bypass gates with primitive helpers. Names matter: ChangePlugin is an agent-scoped configuration AIO (install/uninstall/enable/disable/update FOR THAT AGENT or user-scope target); UninstallPlugin (cross-agent) is the plugin-scoped AIO that cascades through ChangePlugin per agent; UninstallMarketplace cascades through UninstallPlugin per plugin. Without the cascade, agents are left with dangling enabledPlugins keys pointing at deleted marketplaces — they break. Driven by an audit that found ChangeMarketplace's remove path skipped agent cleanup and G11b in ChangePlugin called updateAgent directly instead of dispatching through ChangeCLIArgs."
  - "3.7.2: Source-vs-install-target clarification (2026-04-20). Added R20.29 and a new 'CRITICAL — source vs install target' block to the R20 intro making explicit that the 3 AI Maestro local-marketplace containers under `~/agents/{role,custom,core}-plugins/` are SOURCE STORAGE only. A plugin LIVES at its install target (the client's own plugin cache) reached via the client's own install protocol — regardless of whether the source was a GitHub URL, a local folder, a remote marketplace, or one of the 3 AI Maestro locals. AI Maestro only WRITES into local sources when it is the author or converter of the plugin. Driven by SCEN-026 authoring feedback."
  - "3.7.1: Drift-remediation pass (2026-04-16). Bumped version to match R20.25 / R20.27 / R20.28 body tags that were already labeled v3.7.1. Fixed R20.28 title count (Six → Five — enumeration has exactly five patterns). Added SCEN-023 and SCEN-024 to §0.8. Removed stale pointer to non-existent `app/api/agents/[id]/title/route.ts` (title changes dispatch via `PATCH /api/agents/[id]` per element-management-service). Clarified Overview wording: one remote marketplace + two local containers (+ one core container for non-Claude clients)."
  - "3.7.0: Added R9.13 (role-plugin mandatory for every agent, including AUTONOMOUS), R11.12 (role-plugin mandatory at every boundary), Invariant 8 rewritten. Added new §0 'Canonical source + copies' index and new §TERMINOLOGY (TITLE / ROLE / PERSONA three-layer model). AUTONOMOUS now resolves to the mandatory ai-maestro-autonomous-agent role-plugin."
  - "3.6.0: R20 revised — custom-plugins/ and role-plugins/ are CONTAINERS, not marketplaces. Each container holds one marketplace-<client>/ subfolder per client format (marketplace-claude/, marketplace-codex/, marketplace-openrouter/, ...). Each client-marketplace has its own schema per that client's spec. The .abstract/ IR hub lives at the container level and feeds all per-client marketplaces."
  - "3.5.0: Added R20 (Marketplace Governance) — three default marketplaces, source path format (./<plugin>), .abstract IR storage, core-plugin auto-update, converted-plugin re-emission on source update"
  - "3.4.0: R17 expanded with protection (R17.B), auto-update (R17.C), trust auto-accept (R17.D); R9 clarified AUTONOMOUS vs team agent behavior"
  - "3.3.0: Added R17 (Mandatory Core Plugin Installation)"
  - "3.2.0: Added R16 (Password Never Shared with Agents)"
  - "3.1.0: Added R13 (Role Boundaries), R14 (Team Resilience), R15 (Written Orders & GitHub Trail)"
  - "3.0.0: Added R12 (Minimum Team Composition), PHOTOSTORY scenario rule, moved to docs/ for git tracking"
  - "2.0.0: Added R9 (Manager Requirement), R10 (Agent Lifecycle), R11 (Title-Plugin Binding), communication graph, groups"
  - "1.0.0: Initial governance rules (R1-R8, invariants, permission matrix)"
---

## Table of contents

- §0. Canonical source + copies
- §TERMINOLOGY. Three-layer agent model (TITLE / ROLE / PERSONA)
- Overview
- R1. Teams and Groups
- R2. Team Name Rules
- R3. Role Hierarchy Rules
- R4. Agent Membership Rules
- R5. Transfer Rules
- R6. Messaging Rules (Communication Graph)
- R7. UI Robustness Rules
- R8. Data Integrity Rules
- R9. Manager Requirement
- R10. Agent Lifecycle Governance
- R11. Title-Plugin Binding
- R12. Minimum Team Composition (CRITICAL)
- R13. Role Boundaries (No Overstepping)
- R14. Team Resilience (Auto-Recovery)
- R15. Written Orders & GitHub Trail
- R16. Password Never Shared with Agents (CRITICAL)
- R17. Mandatory Core Plugin Installation (CRITICAL)
- R18. Plugin Continuity on Client Change (CRITICAL)
- R19. MAINTAINER Title
- R20. Marketplace Governance
- Invariants (Must Never Be Violated)
- R21. All-In-One Pipeline Architecture (CRITICAL — IRON)
- Role-Based Permission Matrix

---

> **Bundled mirror — read this first**
>
> This file is a verbatim copy of the canonical governance rules. The single
> source of truth lives in the `Emasoft/ai-maestro` fork:
>
> - Canonical path: `docs/GOVERNANCE-RULES.md`
> - Stable raw URLs (byte-identical at the sync point):
>   `https://raw.githubusercontent.com/Emasoft/ai-maestro/governance-rules/docs/GOVERNANCE-RULES.md`
>   `https://raw.githubusercontent.com/Emasoft/ai-maestro/feature/phase6-jsonl-rebase-test/docs/GOVERNANCE-RULES.md`
> - Synced from commit: `a17c01a4` (governance-rules / phase6-jsonl-rebase-test)
> - Bundled in `ai-maestro-plugin` on: 2026-05-08
> - Bundled-doc version: see the `version:` field in the YAML frontmatter
>   above (3.9.1 at the time of this sync).
>
> Treat this file as **read-only** in this repo. To update:
>
> 1. Edit the canonical file in `Emasoft/ai-maestro` first (bump `version:`,
>    append a changelog entry).
> 2. Walk the §0 cross-reference index in this very file — every mirror, role-plugin
>    persona, enforcement code, API route, UI component, scenario test, and
>    validation script must be updated in the same commit.
> 3. Re-sync this bundled copy: `cp <canonical> skills/team-governance/references/GOVERNANCE-RULES.md`
>    then refresh the four bullets at the top of this banner (URLs, commit hash,
>    sync date, bundled-doc version).
> 4. Republish `ai-maestro-plugin` so running agents pick up the new rules via
>    `claude plugin update` — agents read this file via the `team-governance` skill.
>
> If you find yourself disagreeing with this bundled copy: STOP, fetch the
> canonical, and trust that one. This bundle exists for offline/airgapped
> agent reading — it is never authoritative against the canonical.

---

# Team Governance — Design Rules & Requirements

**Source:** Extracted from user instructions, audit reports, and logical inference

---

## §0. Canonical source + copies (READ THIS BEFORE EDITING)

**`docs/GOVERNANCE-RULES.md` is the canonical source of truth for every governance rule in the AI Maestro ecosystem.** Every time a rule is added, renamed, renumbered, rewritten, or deleted, **every file listed below** must be updated in the same commit. Leaving any entry stale produces drift — agents that still obey an old rule because their plugin persona was never refreshed, validation scripts that block legitimate operations because they still check an old gate, etc.

The list is maintained here (not in a separate `GOVERNANCE-COPIES.md`) so it is impossible to read the rules without seeing the index. Update this list whenever a new copy is added.

### 0.1 — Canonical source

| Path | Role | Update strategy |
|---|---|---|
| `docs/GOVERNANCE-RULES.md` | **CANONICAL** — single source of truth | Edit first. Bump the `version:` field in YAML frontmatter. Append a changelog entry. |

### 0.2 — Documentation mirrors (in this repo)

These files paraphrase or link to the rules. Keep them in sync with the canonical file. Never let them contradict §1-§20 below.

| Path | What it contains | Update strategy |
|---|---|---|
| `README.md` → "Understanding AI Maestro Terms" | TITLE / ROLE / PERSONA terminology + 8-title list | Edit whenever §TERMINOLOGY or §R3 changes |
| `CLAUDE.md` → "Agent Terminology (TITLE / ROLE / PERSONA) — READ FIRST" | Same as README but for assistant sessions | Edit whenever §TERMINOLOGY changes |
| `CLAUDE.md` → various rule mentions (R9, R17, R18, R19, R20) | Scattered cross-references | Search for rule IDs and update text |
| `design/tasks/TRDD-*.md` | Task design docs that quote rules | Only edit the specific TRDD; rule IDs must match |
| `tests/scenarios/SCENARIOS_TESTS_RULES.md` | Scenario test rules (separate from governance, but adjacent) | Edit only if a new scenario rule is added — do NOT copy governance rule text here |

### 0.3 — Role-plugin main-agent personas (shipped as plugins in the marketplace)

Every role-plugin's `agents/<name>-main-agent.md` embeds the subset of governance rules the agent in question must obey. **When a rule changes, every relevant plugin must be republished** (bumped version, new commit, marketplace manifest updated) so agents running the old version get the update via `claude plugin update`. Never edit the cache at `~/.claude/plugins/cache/` — always edit the plugin's own GitHub repo and republish via `scripts/publish.py`.

| Role-plugin | Repo | Rules the persona embeds | Update trigger |
|---|---|---|---|
| `ai-maestro-assistant-manager-agent` | `Emasoft/ai-maestro-assistant-manager-agent` | R3 (MANAGER singleton), R9, R10, R15, R16, R20.2, comm graph | Any change to MANAGER privileges |
| `ai-maestro-chief-of-staff` | `Emasoft/ai-maestro-chief-of-staff` | R3, R5 (COS per team), R9, R10, R12, R13, R15, comm graph | Any change to COS privileges or team-lifecycle rules |
| `ai-maestro-architect-agent` | `Emasoft/ai-maestro-architect-agent` | R3, R6, R13 role-boundaries, comm graph | Any change to ARCHITECT boundaries |
| `ai-maestro-orchestrator-agent` | `Emasoft/ai-maestro-orchestrator-agent` | R3, R6, R13, R15 written orders, comm graph | Any change to ORCHESTRATOR routing or kanban rules |
| `ai-maestro-integrator-agent` | `Emasoft/ai-maestro-integrator-agent` | R3, R6, R13, comm graph | Any change to INTEGRATOR boundaries |
| `ai-maestro-programmer-agent` | `Emasoft/ai-maestro-programmer-agent` | R3, R6, R13, R15, comm graph (MEMBER subset) | Any change to MEMBER boundaries |
| `ai-maestro-maintainer-agent` | `Emasoft/ai-maestro-maintainer-agent` | R3, R9, R19 (MAINTAINER), R20.2, comm graph | Any change to MAINTAINER rules |
| `ai-maestro-autonomous-agent` | `Emasoft/ai-maestro-autonomous-agent` | R3, R9.13, R11.3, R11.12, comm graph (AUTONOMOUS subset), workspace isolation | Any change to AUTONOMOUS boundaries |

### 0.4 — Skills in `ai-maestro-plugin` (the core plugin — shipped to every agent)

The core plugin embeds cross-cutting rules that every agent must know — not just the ones for its own title.

| Skill path (inside `Emasoft/ai-maestro-plugin`) | Rules it teaches | Update trigger |
|---|---|---|
| `skills/team-governance/SKILL.md` | R1-R15 summary, title permissions matrix, COS lifecycle | Any change to R1-R15 |
| `skills/agent-messaging/SKILL.md` | R6 (communication graph), AMP routing rules | Any change to R6 or the comm graph |
| `skills/agent-identity/SKILL.md` | R14 (identity), R16 (password secrecy) | Any change to AID / password rules |
| `skills/team-kanban/SKILL.md` | R15 (written orders), kanban workflow | Any change to R15 or kanban rules |

### 0.5 — Enforcement code (TypeScript services)

These files enforce the rules at runtime. When a rule changes, **update the gate logic here in the same commit** — not in a follow-up PR, otherwise the server and the docs disagree for however long the follow-up takes.

| Path | What it enforces | Must be updated when |
|---|---|---|
| `services/element-management-service.ts` | `ChangeTitle` (23 gates), `ChangeTeam`, `ChangeClient`, `ChangePlugin`, `CreateAgent` | Any rule changes the conditions for title assignment, plugin install, or team membership |
| `services/governance-service.ts` | Team governance, MANAGER/COS checks, password validation, governance-request lifecycle | R3, R4, R5, R9, R10, R16 changes |
| `lib/communication-graph.ts` | R6 comm graph (directed adjacency matrix) | Any change to R6 |
| `lib/ecosystem-constants.ts` | `TITLE_PLUGIN_MAP`, `ROLE_PLUGIN_*`, `PREDEFINED_ROLE_PLUGIN_NAMES`, `PLUGIN_COMPATIBLE_TITLES` | R11 / R20.4 default changes, new predefined role-plugin |
| `lib/team-registry.ts` | `blockAllTeams`, `unblockAllTeams`, `isAgentInAnyTeam` | R9 cascade changes |
| `lib/agent-auth.ts` | Auth bridge, MANAGER/COS gate checks | R9, R10 auth changes |
| `lib/sudo-fetch.ts` + `security-registry.json` | Strict-route list, sudo-mode gate | Any new strict operation |
| `server.mjs` (startup tasks) | MANAGER detection, team blocking on boot | R9 cascade |

### 0.6 — API routes that re-implement rule checks

| Path | What it checks | Must be updated when |
|---|---|---|
| `app/api/agents/route.ts` (POST/GET) | CreateAgent delegation; auth + title validation | R3, R9, R11 |
| `app/api/agents/[id]/route.ts` (PATCH/DELETE) | Title change dispatcher (delegates to `ChangeTitle` in element-management-service), auth gate, sudo-mode gate for strict operations | R3, R9, R10, R11 |
| `app/api/agents/[id]/wake/route.ts` | R10 wake permission matrix | R10 |
| `app/api/agents/[id]/hibernate/route.ts` | R10 hibernate permission matrix | R10 |
| `app/api/teams/route.ts` + `app/api/teams/[id]/route.ts` | R1, R2, R3 team CRUD + block/unblock | R1, R2, R3, R9 |
| `app/api/governance/password/route.ts` | R16 password handling | R16 |
| `app/api/governance/requests/*` | R4 governance request lifecycle | R4 |

### 0.7 — UI components that display or enforce rules

| Path | What it shows/enforces | Update trigger |
|---|---|---|
| `components/agent-profile/RoleTab.tsx` | N:1 compatibility UI (locked label vs dropdown), R11 title-plugin binding | Any R11 change |
| `components/AgentCreationWizard.tsx` | Title picker, role-plugin picker, R9/R11/R19 requirements | Any R9, R11, R19 change |
| `components/TitleAssignmentDialog.tsx` | Governance password gate, title change flow | R3, R16 changes |
| `components/sidebar/TeamListView.tsx` | Team delete dialog, R1/R9 blocking behavior | R1, R9 changes |

### 0.8 — Scenario test specs (`tests/scenarios/SCEN-*.scen.md`)

When a rule changes, any scenario that exercises the old behavior must be rewritten. Scenarios that test governance:

| Scenario | Rules tested | Update trigger |
|---|---|---|
| `SCEN-001_title-change-lifecycle.scen.md` | R3, R9, R11 | R3, R9, R11 |
| `SCEN-002_team-create-delete.scen.md` | R1, R2, R9 | R1, R2, R9 |
| `SCEN-005_manager-gate-team-lifecycle.scen.md` | R3, R9 MANAGER gate cascade | R3, R9 |
| `SCEN-010_cos-lifecycle.scen.md` | R5 COS immutability | R5 |
| `SCEN-011_agent-session-control.scen.md` | R10 lifecycle governance | R10 |
| `SCEN-018_maintainer-lifecycle.scen.md` | R19 MAINTAINER | R19 |
| `SCEN-019_marketplace-and-plugin-lifecycle.scen.md` | R20 marketplace | R20 |
| `SCEN-020_core-plugins-unchangeable.scen.md` | R17 core plugin | R17 |
| `SCEN-021_user-local-scope-isolation.scen.md` | R20.20 scope isolation | R20.20 |
| `SCEN-022_manager-autonomous-config-ops.scen.md` | R9, R9.13, R11 (MANAGER creates AUTONOMOUS) | R9, R11 |
| `SCEN-023_r17-exhaustive-surface-audit.scen.md` | R17 exhaustive surface audit (cannot-uninstall, cannot-disable, all UI surfaces) | R17 |
| `SCEN-024_delete-team-revert-cos.scen.md` | DeleteTeam COS revert behavior, R5 COS-immutability edge cases | R1, R3, R5 |

### 0.9 — Validation scripts and linters

| Path | What it validates | Update trigger |
|---|---|---|
| `scripts/publish.py` (in each role-plugin repo) | Quad-match identity, `.agent.toml` schema, CPV strict | Role-plugin TOML schema changes |
| `scripts/validate-governance.sh` (if present) | Runtime governance check | Any rule change affecting runtime enforcement |
| `tests/scenarios/scripts/dev-browser-helpers/aim-helpers.sh` | UI helper functions used by scenarios | UI governance flow changes |

### 0.10 — Update protocol

When you change a rule:

1. **Edit `docs/GOVERNANCE-RULES.md` first.** Bump the `version:` field. Append a changelog entry with the rule ID that changed.
2. **Walk through §0.2 - §0.9 above.** For every entry that applies, read the referenced file and update the text/code/test so it matches the new rule.
3. **Update this §0 index** if you added a new copy location.
4. **Commit all affected files together** — not a separate PR per category. The canonical file and every mirror must be atomic.
5. **Republish affected role-plugins** via `scripts/publish.py` in each plugin's own GitHub repo. The publish pipeline bumps the plugin version, updates the marketplace manifest, and triggers `claude plugin update` on running agents.
6. **Run the affected SCEN-NNN scenarios** to verify the rule change is coherent end-to-end before claiming it works.

If you catch yourself thinking "I'll fix the other copies later", STOP — that is how drift starts. Fix them now, or revert the canonical change and come back when you have the time to do it properly.

---

## §TERMINOLOGY. Three-layer agent model (TITLE / ROLE / PERSONA)

Every AI Maestro agent has **three orthogonal layers**. Keeping them distinct is essential — they are mutated by different pipelines, displayed in different UI tabs, and governed by different rules.

| Layer | Answers | Example |
|---|---|---|
| **TITLE** | *What is it allowed to do?* — the governance class (permissions) | `MEMBER` |
| **ROLE** | *What does it know how to do?* — the role-plugin main agent loaded from a marketplace | `ai-maestro-programmer-agent:programmer-main-agent@Emasoft/ai-maestro-plugins` |
| **PERSONA** | *Which specific running instance?* — identity (name, AID, avatar, workdir) | `peter-bot, <aid>, ~/avatars/peter.jpg, ~/agents/peter-bot/` |

### §TERMINOLOGY.1 — TITLE (governance class)

The TITLE determines what an agent is authorized to do within the governance system. The eight valid titles are listed in R3. TITLE is the access-control role, not the behaviour. Changing a TITLE runs the `ChangeTitle` pipeline (23 gates) and requires the governance password or MANAGER/COS authorization per R3 and R16. In the code: `agent.governanceTitle` (lowercase kebab).

### §TERMINOLOGY.2 — ROLE (role-plugin main agent)

The ROLE is the **role-plugin main agent** the PERSONA is currently running. It is referenced in fully-qualified form:

```
<plugin-name>:<main-agent-name>@<marketplace>
```

The `@<marketplace>` suffix mirrors Claude Code's standard plugin syntax (`plugin@marketplace`); the `:<main-agent>` segment selects which main-agent `.md` file inside the plugin is loaded by `claude --agent <main-agent>`. A role-plugin is **any normal Claude Code plugin** that additionally contains:

1. A `<name>.agent.toml` file at the plugin root with two mandatory extra fields: `compatible-titles` (array of governance titles the plugin is designed for) and `compatible-clients` (array of CLI clients like `claude-code`, `codex`).
2. A main-agent `.md` file whose persona text carries the governance rules that agent must follow — inline, via `skills:` references, or via rule-file links. This persona is the actual security boundary: every agent on a host shares a single `gh` CLI identity, so only the persona text restrains destructive actions.

Storage location, install pipeline, `TITLE_PLUGIN_MAP` membership, and the Haephestos authoring tool are **NOT** defining properties of a role-plugin. Any plugin matching the two conditions above is a valid role-plugin regardless of where it lives or how it was authored. AI Maestro ships two default role-plugin marketplaces (`Emasoft/ai-maestro-plugins` remote, `ai-maestro-local-roles-marketplace` local at `~/agents/role-plugins/marketplace/`), but role-plugin folders can live anywhere as long as a registered marketplace manifest's `source` field points at them.

Changing a ROLE runs `ChangePlugin` with the `rolePluginSwap` flag, or is triggered automatically by `ChangeTitle` Gates 15/16 when the new TITLE requires a different plugin. In the code: `agent.rolePlugin` + `config.rolePlugin.name`.

### §TERMINOLOGY.3 — PERSONA (running instance)

The PERSONA is the concrete running agent. Four attributes together identify a specific Claude Code tmux session:

1. **Name** — a unique kebab identifier (e.g. `peter-bot`, `sammy`). Case-insensitive on input; lowercase internally; capitalized for display.
2. **AID** — the Agent Identity Ed25519 key pair used for AMP signing and cross-host authentication. Provisioned once per PERSONA; stored at `~/.agent-messaging/agents/<name>/keys/`.
3. **Avatar** — image file displayed on the sidebar card.
4. **Workdir** — project folder at `~/agents/<name>/` where Claude Code runs. All `--scope local` plugins live here, and this is the only location outside `/tmp` where the PERSONA may write.

PERSONA is the only layer with 1:1 cardinality to a running tmux session. TITLE and ROLE are swappable on a live PERSONA without destroying identity, AID, avatar, or workdir.

In the code: `agent.name` + `agent.label` + `agent.aid` + `agent.workingDirectory` + `agent.avatarPath` together form the PERSONA.

### §TERMINOLOGY.4 — Relationships and invariants

- **TITLE and ROLE are orthogonal but constrained by `compatible-titles`.** `ChangeTitle` rejects assigning a ROLE whose `.agent.toml` does not include the new TITLE — the plugin was designed (skills, instructions, governance text) for those specific titles, and installing it in an incompatible title breaks that design contract.
- **N:1 compatibility** — multiple ROLEs can satisfy one TITLE. The Agent Profile → Role tab shows a dropdown when ≥2 role-plugins declare the same title in their `compatible-titles`, and a locked label when exactly one does. One ROLE may also be compatible with multiple TITLEs.
- **R9.13 mandatoriness** — every persisted agent MUST carry exactly one ROLE. CreateAgent / ChangeTitle HARD REJECT any desired state that would leave an agent with zero role-plugins.
- **AUTONOMOUS resolves to `ai-maestro-autonomous-agent`** — no title is ever "no plugin". See R11.3 and R11.12.

### §TERMINOLOGY.5 — Writing conventions

- Use **TITLE** when discussing permissions, governance, the communication graph, or approval flows.
- Use **ROLE** when discussing behaviour, skills, main-agent persona text, or available tools.
- Use **PERSONA** when identifying a specific agent (the one in the sidebar card, at that workdir, with that AID).
- Do not use "role" as a synonym for "title". The 2026-03-20 rename made `TitleBadge` / `TitleAssignmentDialog` authoritative in the codebase.
- When the user says "change the agent's role", clarify whether they mean swap the role-plugin (ROLE) or re-assign the governance level (TITLE) — these are different pipelines.

### §TERMINOLOGY.6 — OOP analogy

If it helps communicating the model to a new contributor:

- **TITLE** = access-control role (permission level)
- **ROLE** = class definition (behaviour + skills + instructions)
- **PERSONA** = instance (state + identity)

---

## Overview

AI Maestro implements a team governance model with eight governance titles
(MANAGER, CHIEF-OF-STAFF, ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER,
AUTONOMOUS, MAINTAINER), teams (isolated messaging + ACL), groups
(lightweight broadcast collections), one remote marketplace plus two
local plugin containers (role-plugins + custom-plugins) and — for
non-Claude clients only — a third local core-plugins container (R20),
and an identity layer where every privileged action is backed by a
cryptographically-signed AID token. Teams require a MANAGER to
function. Groups are unstructured collections with no governance.
MAINTAINERs live at the host level bound to a GitHub repo and never
join a team.

---

## R1. Teams and Groups

| ID | Rule | Source |
|----|------|--------|
| R1.1 | **Teams** have isolated messaging, ACL, governance titles, and a COS. Former "closed teams" | Explicit |
| R1.2 | **Groups** are lightweight agent collections for broadcast messaging. No governance, no COS, no kanban. Former "open teams" | Explicit |
| R1.3 | Every team **SHOULD** have a COS assigned — the COS manages membership and external communication | Explicit |
| R1.4 | Teams require a **MANAGER** to exist on the host before they can be created | Explicit |
| R1.5 | Teams without a MANAGER are **blocked** (`team.blocked = true`) — all operations frozen | Explicit |
| R1.6 | Groups have no governance constraints — any agent can subscribe/unsubscribe freely | Explicit |

**Rationale:** The COS is the team's operational leader. The MANAGER is the host-wide governance authority. Without either, the team cannot function safely. Groups exist for lightweight coordination without governance overhead.

---

## R2. Team Name Rules

| ID | Rule | Source |
|----|------|--------|
| R2.1 | Team names must be unique (case-insensitive comparison) — no two teams can share the same name | Explicit |
| R2.2 | Duplicate name check must be enforced both server-side (API rejects with 409) and client-side (UI shows inline error before POST) | Implicit (both creation surfaces exist) |
| R2.3 | Renaming a team via update must also check uniqueness against all other teams (excluding the team being renamed) | Implicit (rename is an update operation) |

---

## R3. Role Hierarchy Rules

| ID | Rule | Source |
|----|------|--------|
| R3.1 | Eight governance titles exist: **MANAGER** (global singleton), **CHIEF-OF-STAFF** (per team), **ORCHESTRATOR** (per team), **ARCHITECT**, **INTEGRATOR**, **MEMBER** (default team title), **AUTONOMOUS** (no team), **MAINTAINER** (no team, bound to a GitHub repo) | Explicit |
| R3.2 | Only ONE agent can be MANAGER at any given time (singleton constraint) | Explicit |
| R3.3 | COS is a per-team title — each team has exactly one COS | Explicit |
| R3.4 | An agent can be COS of only **ONE** team at any time | Explicit |
| R3.5 | All role changes (assign/remove MANAGER, assign/remove COS) require the governance password | Explicit |
| R3.6 | MANAGER has full authority over all teams: can add/remove agents, assign COS, approve transfers, create/delete teams, message anyone | Explicit |
| R3.7 | COS is responsible for **external communication** of their team — they are the contact point for outside agents | Explicit |
| R3.8 | COS decides the **staff composition** (add/remove agents) of their team — this is why they are called "chief-of-staff" | Explicit |
| R3.9 | MANAGER can do everything COS can, but **usually delegates** to the COS | Explicit |
| R3.10 | Typical workflow: MANAGER creates a team, assigns a COS, and lets the COS manage the team from there | Explicit |
| R3.11 | Reassigning MANAGER to a new agent immediately revokes the role from the old agent (only one MANAGER exists) | Implicit (singleton) |
| R3.12 | COS changes (assign/remove) on a team must **NOT** be possible via the generic `PUT /api/teams/[id]` endpoint — only via the dedicated `POST /api/teams/[id]/chief-of-staff` endpoint which requires the governance password | Implicit (prevents bypass of password protection) |

---

## R4. Agent Membership Rules

| ID | Rule | Source |
|----|------|--------|
| R4.1 | Non-MANAGER agents can be in at most **ONE team** at any given time (single-team membership) | Explicit |
| R4.2 | Any agent can subscribe to **unlimited groups** simultaneously (groups have no governance) | Explicit |
| R4.3 | **MANAGER** and **MAINTAINER** are not in any team — both operate at the host level | Explicit |
| R4.4 | When an agent joins a team, it is auto-assigned the **MEMBER** title and the programmer plugin | Explicit |
| R4.5 | An agent cannot be added to a team they are already a member of (no duplicate membership in `agentIds`) | Explicit |
| R4.6 | COS **must** be a member of the team they lead (present in `agentIds[]`) — they manage the team staff and the message filter relies on `agentIds` for same-team communication | Implicit (logical necessity) |
| R4.7 | Removing a COS from a team's `agentIds` while they remain `chiefOfStaffId` is **forbidden** — COS title can only be removed by deleting the team | Implicit (COS immutability invariant) |
| R4.8 | The UI must **always show team memberships** when selecting agents for any operation (add to team, remove from team, transfer, team creation agent selection) | Explicit |
| R4.9 | Agent existence must be validated when adding to a team — `agentIds` must reference agents that actually exist in the registry | Implicit (referential integrity) |

---

## R5. Transfer Rules

| ID | Rule | Source |
|----|------|--------|
| R5.1 | Moving a normal agent **FROM** a team requires a transfer request (approval workflow) — the agent cannot simply leave | Explicit (implemented) |
| R5.2 | Only MANAGER or COS can **create** transfer requests | Explicit (enforced) |
| R5.3 | Only the source team's COS or MANAGER can **approve/reject** transfers | Explicit (enforced) |
| R5.4 | COS **cannot be transferred out** of their own team — COS title is immutable to team lifecycle | Implicit (COS immutability invariant) |
| R5.5 | **Destination team must exist** at the time the transfer request is created | Implicit (referential integrity) |
| R5.6 | Source and destination teams must be **different** (no self-transfer) | Implicit (nonsensical operation) |
| R5.7 | On transfer approval, the **single-team constraint** (R4.1) must be checked: verify the agent is not already in another team | Implicit (logical consequence) |
| R5.8 | Duplicate pending transfer requests (same agent + same source + same destination) must be prevented | Explicit (enforced) |

---

## R6. Messaging Rules (Communication Graph)

All teams are closed. Messaging between agents is governed by a title-based directed communication graph. Missing connections are forbidden.

### Canonical address format (2026-05-06 update)

Every agent (and every human user) is addressed by a **single unique ID string** per host. The legacy three-level hierarchical addressing (`first/second/third/agent-name` style) is **deprecated** — that format only ever applied to the sidebar's *visual* tag organization and was never load-bearing for messaging. Use the formats below for ALL new code, persona prompts, message bodies, and orchestration directives.

The canonical wire format is one of:

```
<agent-id>@<host>      ← preferred for cross-host messaging
<host>:<agent-id>      ← equivalent alternate; pick whichever reads more
                          naturally in the surrounding sentence
<agent-id>             ← short form; resolves to the writer's host
                          (the sender's home host)
```

When the writer is the human user, the writer's host is the dashboard's local host (the box the user is logged into). When the writer is an agent, the writer's host is the agent's `hostId` value as recorded in the registry.

The **persona name** may substitute for the agent-id whenever the substitution is unambiguous on the target host — i.e. there is no other agent on that host whose name (or label) collides with this persona name. When a collision exists, the persona name MUST be replaced by the agent-id (or the address rejected at the API layer with HTTP 409 + a `disambiguation_required` code).

**Examples:**

| Format | Resolves to |
|---|---|
| `peter-bot@mac.lan` | the agent named `peter-bot` on host `mac.lan` |
| `mac.lan:peter-bot` | same as above, alternate spelling |
| `peter-bot` (in a message authored by an agent on `mac.lan`) | `peter-bot@mac.lan` |
| `peter-bot` (in a message authored by a user logged into `mac.lan`) | `peter-bot@mac.lan` |
| `Peter Parker` (persona-name alias, no collision on mac.lan) | resolved to `peter-bot@mac.lan` |
| `Peter Parker` (collision: two agents have label "Peter Parker") | rejected — the writer must use the agent-id |
| `H` / `human:user@host` | the human user (single H node per host, no agent-id) |

**What this replaces:** any persona prompt, doc, or orchestration rule that asks an agent to address peers using a hierarchical path like `team-x/sub-y/agent-z` is OUT OF DATE. Replace with the bare `agent-id` or the `agent-id@host` form. The 3-level sidebar visual organization (R7 family) is unaffected — it remains purely a UX feature, not an addressing scheme.

**Adjacency matrix.** Cell values:

- **`Y`** — sender may freely initiate a message to recipient.
- blank — sender is **forbidden** from sending to recipient (API returns HTTP 403 with routing suggestion).
- **`1`** — sender may send EXACTLY ONE reply to recipient if the recipient previously messaged the sender. Without a prior inbound message from the recipient, this edge is equivalent to blank. Used only for team-agent edges to the human user (`C/O/R/I/E -> H`). MAINTAINER and AUTONOMOUS have full `Y` edges to H.

**2026-04-22 v2 update** — the HUMAN USER (**H**) is now a first-class node in the graph. H has unconditional outbound access to every node (including other humans). Inbound to H from team agents (COS, ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER) is `1` — reply-only. Inbound to H from governance-layer titles (MANAGER, MAINTAINER, AUTONOMOUS) is `Y` — they may initiate messages to the user.

**2026-05-04 v3 update** — MANAGER → in-team-non-COS edges (ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER) flipped from `Y` to blank. Real-world test on 2026-05-03 showed great confusion when MANAGER bypassed COS to issue directives directly to team agents — COS or ORCHESTRATOR ended up uninformed or issued contradictory instructions on the same task. **The CHIEF-OF-STAFF is now the SOLE inbound and outbound gateway for closed-team agents.** MANAGER still freely reaches COS, peer MANAGERs, MAINTAINER (out-of-team), AUTONOMOUS (out-of-team), and the HUMAN user. The user (HUMAN) remains exempt — full `Y` to every node, can do everything.

| Sender \ Recipient | HUMAN | MANAGER | COS | ORCHESTRATOR | ARCHITECT | INTEGRATOR | MEMBER | MAINTAINER | AUTONOMOUS |
|---------------------|:-----:|:-------:|:---:|:------------:|:---------:|:----------:|:------:|:----------:|:----------:|
| **HUMAN**           |   Y   |    Y    |  Y  |      Y       |     Y     |     Y      |   Y    |     Y      |     Y      |
| **MANAGER**         |   Y   |    Y    |  Y  |              |           |            |        |     Y      |     Y      |
| **CHIEF-OF-STAFF**  |   1   |    Y    |  Y  |      Y       |     Y     |     Y      |   Y    |            |            |
| **ORCHESTRATOR**    |   1   |         |  Y  |              |     Y     |     Y      |   Y    |            |            |
| **ARCHITECT**       |   1   |         |  Y  |      Y       |           |            |        |            |            |
| **INTEGRATOR**      |   1   |         |  Y  |      Y       |           |            |        |            |            |
| **MEMBER**          |   1   |         |  Y  |      Y       |           |            |        |            |            |
| **MAINTAINER**      |   Y   |    Y    |     |              |           |            |        |            |            |
| **AUTONOMOUS**      |   Y   |    Y    |     |              |           |            |        |            |     Y      |

| ID | Rule | Source |
|----|------|--------|
| R6.1 | Communication rules are defined by the directed graph above — each (sender, recipient) pair must be explicitly listed with its edge type (`Y` = allow, `1` = reply-only, blank = deny). | Explicit |
| R6.2 | **MANAGER** can freely message: COS (the sole team gateway), peer MANAGERs, MAINTAINER, AUTONOMOUS, and the HUMAN user. **MANAGER cannot directly contact in-team non-COS agents** (ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER) — must route through COS. The 2026-05-03 field test showed MANAGER's direct in-team directives caused confusion (COS/ORCHESTRATOR uninformed or contradicting); v3 of the graph (2026-05-04) corrects this. | Explicit |
| R6.3 | **CHIEF-OF-STAFF** is the SOLE inbound and outbound team gateway — every directive from MANAGER fans into the team through COS, and every team-internal escalation fans out through COS. COS can message MANAGER, COS peers, and the team roles (ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER). Cannot initiate messages to MAINTAINER, AUTONOMOUS, or the human user (H-edge is reply-only). | Explicit |
| R6.4 | **ORCHESTRATOR** can message COS, ARCHITECT, INTEGRATOR, MEMBER. Cannot initiate to MANAGER, MAINTAINER, AUTONOMOUS, or the human user (H-edge is reply-only). | Explicit |
| R6.5 | **ARCHITECT**, **INTEGRATOR**, **MEMBER** can only freely message COS and ORCHESTRATOR. H-edge is reply-only (may answer a user message once; cannot initiate). | Explicit |
| R6.5a | **AUTONOMOUS** can freely message MANAGER, other AUTONOMOUS agents, AND the human user. Cannot reach COS, team roles, or MAINTAINER. The H-edge is `Y` (not reply-only) — AUTONOMOUS operates outside teams and may initiate user-directed messages. | Explicit |
| R6.5b | **MAINTAINER** can freely message MANAGER and the human user. Cannot reach COS, team roles, AUTONOMOUS, or peer MAINTAINERs. The H-edge is `Y` (not reply-only) — MAINTAINERs need to surface repo-scoped concerns directly to the user when MANAGER routing would add latency. | Explicit |
| R6.6 | The **human user (H)** is a first-class node with unconditional outbound `Y` to every other node INCLUDING other humans (H -> H is `Y` for user-to-user messaging). Inbound to H from team titles is `1` (reply-only: team agents cannot proactively initiate but may reply once to an inbound user message). Inbound to H from governance titles (M/T/A) is `Y`. Agents are additionally persona-discouraged from proactively initiating user contact — the reply-only rule is the hard floor; the persona sets the soft floor. | Explicit |
| R6.7 | When a message is blocked, the error must include a **routing suggestion**. The routing-suggestion table in `lib/communication-graph.ts` is authoritative. Under the 2026-04-22 tightening, almost every cross-layer route goes through MANAGER (not COS). | Explicit |
| R6.8 | **Three layers of enforcement**: (1) API server validates sender/recipient titles before delivery via `validateMessageRoute()`, (2) Role-plugin main-agent .md files list allowed/reply-only recipients, (3) Sub-agents are forbidden from using AMP messaging entirely. | Explicit |
| R6.9 | Sub-agents have no AMP identity and cannot authenticate — they communicate only with their spawning main-agent. | Explicit |
| R6.10 | **Reply-only enforcement** (`1` edges): the sender MUST pass `inReplyToMessageId` when targeting a reply-only recipient. Today the graph layer only requires the field to be a truthy string; it does NOT load the referenced message, verify its sender/recipient pair, or prevent multiple replies to the same id. The "one reply per inbound message" invariant (AMP inbox sets `replied=true` on the original and rejects subsequent attempts) is planned but not yet implemented — tracked in `design/tasks/TRDD-80557822-comm-graph-downstream-sync.md`. The advisory check is latent in production because no flow currently routes messages to the human user; it becomes load-bearing the moment Phase 2 maestro auth wires H as an AMP recipient. | Explicit (enforcement partial; see TRDD-80557822) |
| R6.11 | **Canonical address format** (2026-05-06): every agent is addressed by ONE unique id string per host. The wire format is `<agent-id>@<host>` (preferred) or `<host>:<agent-id>` (alternate). The bare `<agent-id>` resolves to the writer's host. Hierarchical/3-level addressing (`team/sub/name`) is deprecated for messaging — that pattern was only ever used by the sidebar's visual tag organization and never by the message router. | Explicit |
| R6.12 | **Persona-name alias**: an agent's persona name (registry `label` field) MAY substitute for `<agent-id>` whenever the substitution is unambiguous on the target host (no other agent on that host has a name or label that collides). On collision, the address MUST use `<agent-id>` and the API returns HTTP 409 `disambiguation_required` if a persona-name alias is sent. | Explicit |
| R6.13 | **Default-host resolution**: when the host is omitted from an address, it defaults to the writer's host. For agents, that is `agent.hostId` from the registry. For human users, that is the dashboard host the user is logged into. Cross-host messaging therefore REQUIRES the explicit `@<host>` (or `<host>:`) suffix; an agent on host A cannot accidentally reach an agent on host B by typing a bare id. | Explicit |
| R6.14 | **UI and persona drift**: every UI tooltip, onboarding-guide step, agent persona prompt, role-plugin instruction, and orchestration rule that references the deprecated 3-level addressing format MUST be migrated to R6.11–R6.13 wording. The deprecation is permanent — no flag toggles, no compatibility shim. The migration is tracked across this repo (UI text + docs) and the 8 role-plugin repos under `Emasoft/ai-maestro-*` (persona prompts). | Explicit |

Full spec: `docs_dev/2026-04-03-communication-graph.md`

---

## R7. UI Robustness Rules

| ID | Rule | Source |
|----|------|--------|
| R7.1 | **Prevent accidental multiple operations** from fast repeated clicks — all mutating buttons must have `submitting` guards | Explicit |
| R7.2 | Show **loading spinners** for all async operations (API calls, data fetching) | Explicit |
| R7.3 | Show **error messages** for all failures — no silent failures allowed | Explicit |
| R7.4 | Handle all **edge cases** and possible errors gracefully | Explicit |
| R7.5 | No **infinite loops** or **blocking operations** in the UI | Explicit |
| R7.6 | Show **role badges** (MANAGER: amber/gold, COS: indigo) next to agent names throughout the UI | Implicit |
| R7.7 | Show **blocked badge** on teams when no MANAGER exists | Implicit |
| R7.8 | **Resolve COS UUID** to human-readable agent name everywhere it is displayed — never show raw UUIDs to users | Implicit (UX requirement) |
| R7.9 | When governance data is loading, show **loading state** — do not show stale/default "normal" role which would be misleading | Implicit |

---

## R8. Data Integrity Rules

| ID | Rule | Source |
|----|------|--------|
| R8.1 | All write operations on teams use **file locking** (`withLock`) to prevent corruption from concurrent writes | Implemented |
| R8.2 | `chiefOfStaffId` and `type` changes must **NOT** be accepted in the generic team update (`PUT /api/teams/[id]`) — must use dedicated password-protected endpoints | Implicit (prevents governance bypass) |
| R8.3 | Team deletion should **clean up related transfers** (cancel pending transfer requests involving the deleted team) | Implicit (referential integrity) |
| R8.4 | `Agent.team` free-text field is **display-only** — it is NOT connected to `Team.id` in the governance system, membership is tracked solely via `Team.agentIds[]` | Documented |

---

## R9. Manager Requirement

The MANAGER is the host-wide governance authority. Without a MANAGER, teams cannot function — but AUTONOMOUS agents operate normally. The key distinction:

- **AUTONOMOUS agents**: Always fully operational. Can be created, woken, hibernated, and used regardless of whether a MANAGER exists. They appear in the dashboard at all times.
- **Team agents** (any agent in a team's `agentIds[]`): Require a MANAGER on the host. When no MANAGER exists, team agents are forcefully hibernated and cannot be woken until a MANAGER is assigned.

**All agents always appear in the dashboard sidebar** (ACTIVE/ALL/HIBER tabs) regardless of MANAGER status. The MANAGER gate only controls whether team agents can be **woken** — it never hides agents from the UI or removes them from the registry.

### Manager Blocking Protocol

When no MANAGER exists (at startup or after MANAGER removal), this cascade executes:

1. All teams are marked `blocked: true` in `teams.json`
2. All agents belonging to blocked teams have their tmux sessions killed (forcefully hibernated)
3. The wake API rejects wake requests for team agents with HTTP 403: "Cannot wake team agent: no MANAGER exists"
4. AUTONOMOUS agents are **completely unaffected** — they keep running, can be woken, hibernated, created, and deleted normally
5. Team CRUD operations (add/remove agents, create/delete teams) are rejected with HTTP 400

When a MANAGER is assigned (via title change), the reverse cascade runs:

1. All teams are marked `blocked: false`
2. Agents remain hibernated — the MANAGER or user must wake them manually
3. All team operations are re-enabled

| ID | Rule | Source |
|----|------|--------|
| R9.1 | A MANAGER agent **MUST** exist on the host before any team can be created | Explicit |
| R9.2 | If no MANAGER exists, all existing teams are **blocked** (`team.blocked = true`) | Explicit |
| R9.3 | When teams are blocked, no agents can be added to or removed from them | Explicit |
| R9.4 | When teams are blocked, all agents belonging to those teams are **forcefully hibernated** (tmux sessions killed) | Explicit |
| R9.5 | **AUTONOMOUS agents are completely unaffected by team blocking** — they can be created, woken, hibernated, deleted, and used normally even when no MANAGER exists. The MANAGER gate applies exclusively to team agents | Explicit |
| R9.6 | When a MANAGER is assigned (title change), all teams are **unblocked** (`team.blocked = false`) | Explicit |
| R9.7 | Unblocking does **NOT** auto-wake agents — agents remain hibernated until manually woken by the user or the MANAGER | Explicit |
| R9.8 | If a MANAGER is deleted or their title is removed, the blocking cascade triggers immediately (same as startup without MANAGER) | Explicit |
| R9.9 | At server startup, if no MANAGER is detected, team blocking + agent hibernation runs as a startup task | Explicit |
| R9.10 | When attempting to delete the MANAGER agent, the Delete Agent dialog MUST show a clear warning: "This agent holds the MANAGER title. Removing it will block all team operations." The system auto-demotes the MANAGER to AUTONOMOUS before proceeding with deletion | Explicit |
| R9.11 | The MANAGER agent may create teams via the API using AID authentication. The governance password is NOT required for MANAGER-initiated team creation — the server validates the MANAGER's AID session secret (mst_* token) and grants team-creation privileges based on the MANAGER governance title | Explicit |
| R9.12 | **All agents always appear in the dashboard** (sidebar ACTIVE/ALL/HIBER tabs) regardless of MANAGER status. The MANAGER gate controls wake permissions, not visibility. The registry is the source of truth for the agent list — it is never filtered by governance state | Explicit |
| R9.13 | **Role-plugin is mandatory for every agent** (including AUTONOMOUS). CreateAgent, ChangeTitle, ChangeClient, ChangeTeam, and RegisterAgentFromSession MUST reject any desired state that would leave an agent with zero role-plugins. The only valid "no role-plugin" window is the transient instant inside a Change\* pipeline between uninstall and install — the agent is never persisted in that state. AUTONOMOUS resolves to `ai-maestro-autonomous-agent` which encodes workspace isolation, forbidden cross-agent mutation, and comm-graph restrictions in its persona. This closes the security gap where a persona-less AUTONOMOUS agent could destroy other agents' working directories, force-merge PRs, or mutate shared registry state — since all agents share one `gh` CLI identity, the persona instructions are the only effective governance boundary. See R11.12, R20.4, Invariant 8 | Explicit |

**Rationale:** Without a MANAGER, no governance authority exists to oversee teams. Blocking prevents unsupervised team operations and ensures the system is in a safe state until governance is restored. AUTONOMOUS agents are independent by definition — they have no team, no COS, and no governance chain that requires a MANAGER. Restricting them would break the fundamental principle that AUTONOMOUS agents operate outside the team governance model.

---

## R10. Agent Lifecycle Governance

| ID | Rule | Source |
|----|------|--------|
| R10.1 | Only the **user** (web UI, no auth headers) or the **MANAGER** agent can wake ANY agent | Explicit |
| R10.2 | Only the **user** or the **MANAGER** agent can hibernate ANY agent | Explicit |
| R10.3 | The **CHIEF-OF-STAFF** can wake or hibernate agents that belong to **their own team only** | Explicit |
| R10.4 | All other agents (MEMBER, ORCHESTRATOR, ARCHITECT, INTEGRATOR, AUTONOMOUS) **cannot** wake or hibernate any agent | Explicit |
| R10.5 | Team agents cannot be woken if no MANAGER exists on the host (even by the user — assign MANAGER first) | Explicit |
| R10.6 | The restart endpoint follows the same governance rules as the wake endpoint | Explicit |
| R10.7 | When deleting a team with "Delete Agents Too", the system SHOULD warn if any agents were created before the team and offer to keep them as AUTONOMOUS instead of deleting them | Recommended |

**Enforcement points:**
- `POST /api/agents/[id]/wake` — checks auth headers, validates caller is user/MANAGER/COS-of-team
- `POST /api/agents/[id]/hibernate` — same checks
- `POST /api/sessions/[id]/restart` — checks if target agent is in a team without MANAGER

---

## R11. Title-Plugin Binding

| ID | Rule | Source |
|----|------|--------|
| R11.1 | Every governance title (including MEMBER and AUTONOMOUS) has a corresponding default role-plugin. **There is NO "no role-plugin" state for a persisted agent** — every agent MUST carry exactly one role-plugin at rest | Explicit |
| R11.2 | MEMBER title installs `ai-maestro-programmer-agent` via ChangeTitle pipeline | Explicit |
| R11.3 | AUTONOMOUS title installs `ai-maestro-autonomous-agent` — the mandatory role-plugin for no-team agents. Its persona enforces workspace isolation, forbids cross-agent mutation, and encodes the AMP communication-graph restrictions. ChangeTitle('autonomous') swaps whatever role-plugin the agent currently has for `ai-maestro-autonomous-agent` | Explicit |
| R11.4 | When an agent joins a team, ChangeTeam calls ChangeTitle('member') which auto-installs the programmer plugin | Explicit |
| R11.5 | When an agent leaves a team, ChangeTeam calls ChangeTitle('autonomous') which uninstalls the team role-plugin and installs `ai-maestro-autonomous-agent` in its place | Explicit |
| R11.12 | **Role-plugin is mandatory at every boundary.** CreateAgent, ChangeTitle, ChangeClient, ChangeTeam, and RegisterAgentFromSession **MUST** reject any desired-state that would leave an agent with zero role-plugins. The only legitimate "no role-plugin" window is the transient instant inside an AIO pipeline between uninstall and install — the agent is never persisted in that state. This is R9.13 as reflected in R11. | Explicit |
| R11.6 | The N:1 compatibility model allows multiple plugins to serve one title — the UI shows a dropdown when 2+ plugins are compatible | Explicit |
| R11.7 | Role-plugins are identified by the **fourfold identity rule**: (1) `plugin.json` `name` is the canonical identity, (2) folder name must equal it, (3) `<name>.agent.toml` must exist with `[agent].name` matching, (4) `agents/<name>-main-agent.md` must exist with frontmatter `name: <name>-main-agent`. All 4 must match or the plugin is rejected | Explicit |
| R11.8 | The target client of a role-plugin is determined ONLY by the `compatible-clients` field in `.agent.toml`, never by the plugin name | Explicit |
| R11.9 | When converting a role-plugin to another client format, the converter preserves the original name, updates `compatible-clients` in `.agent.toml` to the target client, enforces fourfold identity, and stores in `~/agents/role-plugins/`. The converter NEVER overwrites an existing role-plugin folder | Explicit |
| R11.10 | Ordinary (non-role) plugins get a `-<client>` suffix when converted (e.g., `my-plugin-codex`) and are stored in `~/agents/custom-plugins/<client>/` with the `ai-maestro-local-custom-marketplace` | Explicit |
| R11.11 | The `ai-maestro-local-roles-marketplace` contains ALL local role-plugins regardless of their target client. The `ai-maestro-local-custom-marketplace` contains converted ordinary plugins | Explicit |

**Title → Default Plugin mapping:**

| Title | Default Role-Plugin |
|-------|-------------------|
| MANAGER | ai-maestro-assistant-manager-agent |
| CHIEF-OF-STAFF | ai-maestro-chief-of-staff |
| ORCHESTRATOR | ai-maestro-orchestrator-agent |
| ARCHITECT | ai-maestro-architect-agent |
| INTEGRATOR | ai-maestro-integrator-agent |
| MEMBER | ai-maestro-programmer-agent |
| MAINTAINER | ai-maestro-maintainer-agent |
| AUTONOMOUS | ai-maestro-autonomous-agent |

---

## R12. Minimum Team Composition (CRITICAL)

| ID | Rule | Source |
|----|------|--------|
| R12.1 | Every team **MUST** contain a minimum of 5 agents with these titles: **1 CHIEF-OF-STAFF**, **1 ARCHITECT**, **1 ORCHESTRATOR**, **1 INTEGRATOR**, **1 MEMBER** (programmer role-plugin) | Explicit |
| R12.2 | A team lacking any of the 5 required titles is a **NON-FUNCTIONAL TEAM** — the CHIEF-OF-STAFF must immediately add the missing agents | Explicit |
| R12.3 | Each role-plugin is designed for **one role only** — an agent cannot simultaneously serve as COS and ARCHITECT, or any other title combination | Explicit |
| R12.4 | Additional agents with the **MEMBER** title can be added at the judgment of the CHIEF-OF-STAFF, using the programmer role-plugin or any role-plugin compatible with the MEMBER title | Explicit |
| R12.5 | The CHIEF-OF-STAFF decides team composition based on the **design requirements document** received from the MANAGER | Explicit |
| R12.6 | The **MANAGER** must enforce R12.1 when creating teams — a team creation task must always produce at least 5 agents | Explicit |

**Example of a well-composed team (10 agents):**

| # | Title | Role-Plugin | Purpose |
|---|-------|-------------|---------|
| 1 | CHIEF-OF-STAFF | ai-maestro-chief-of-staff | Team operations, staffing, external comms |
| 2 | ARCHITECT | ai-maestro-architect-agent | System design, data models, architecture |
| 3 | ORCHESTRATOR | ai-maestro-orchestrator-agent | Task coordination, workflow management |
| 4 | INTEGRATOR | ai-maestro-integrator-agent | Integration, CI/CD, deployment |
| 5 | MEMBER | ai-maestro-programmer-agent | Core implementation |
| 6 | MEMBER | database-expert (custom) | Database design and optimization |
| 7 | MEMBER | react-native-programmer (custom) | Mobile frontend |
| 8 | MEMBER | figma-designer (custom) | UI/UX design |
| 9 | MEMBER | ai-ocr-expert (custom) | OCR/ML features |
| 10 | MEMBER | ios-debug-expert (custom) | Platform-specific debugging |

**Rationale:** Each title has a unique role-plugin providing specialized skills, guidance, and constraints. A team missing any core title cannot function because no other agent has the skills to fill that gap. The MEMBER title is the only one that supports multiple agents with different specializations, allowing teams to scale horizontally for implementation capacity.

---

## R13. Role Boundaries (No Overstepping)

| ID | Rule | Source |
|----|------|--------|
| R13.1 | Each title agent **MUST operate strictly within its role-plugin's scope**. No agent may perform tasks assigned to another title's role-plugin | Explicit |
| R13.2 | **MANAGER** manages governance, approves operations, routes work. Does NOT write code, design architecture, or coordinate tasks | Explicit |
| R13.3 | **CHIEF-OF-STAFF** manages team staffing, agent lifecycle, external comms. Does NOT design, implement, or integrate | Explicit |
| R13.4 | **ARCHITECT** designs system architecture, data models, APIs. Does NOT implement code, manage agents, or run CI/CD | Explicit |
| R13.5 | **ORCHESTRATOR** coordinates tasks, manages kanban, distributes work. Does NOT design architecture or write code | Explicit |
| R13.6 | **INTEGRATOR** handles code review, quality gates, CI/CD, merging. Does NOT design architecture or write features | Explicit |
| R13.7 | **MEMBER** (programmer) implements features, fixes bugs, writes tests. Does NOT design architecture, manage agents, or run CI/CD pipelines | Explicit |
| R13.8 | An agent that **detects it is being asked to overstep** its role MUST refuse and route the request to the correct title via AMP messaging through the ORCHESTRATOR or COS | Explicit |
| R13.9 | The role-plugin provides the **skills, guidance, and constraints** for its title. An agent without its role-plugin installed CANNOT perform that role's functions | Explicit |

**Rationale:** Role separation ensures quality — each title agent has specialized skills and constraints. Overstepping produces inferior work because the agent lacks the specialized guidance, and creates confusion in the governance chain.

---

## R14. Team Resilience (Auto-Recovery)

| ID | Rule | Source |
|----|------|--------|
| R14.1 | If any of the 5 required title agents (COS, ARCHITECT, ORCHESTRATOR, INTEGRATOR, MEMBER) is **accidentally deleted**, the CHIEF-OF-STAFF must **immediately recreate** the missing agent | Explicit |
| R14.2 | Without all 5 basic title agents, the team is **NON-FUNCTIONAL** — no work can proceed until the missing agent is recreated | Explicit |
| R14.3 | The COS must check team composition **at startup** (when woken) and after any agent deletion event | Explicit |
| R14.4 | If the **COS itself is deleted**, the MANAGER must recreate a COS for the team or delete the team | Explicit |
| R14.5 | The recreated agent must be assigned the **same title and default role-plugin** as the deleted one | Explicit |
| R14.6 | The COS **logs the incident** (deleted agent name, title, timestamp, recreation details) in the team's record-keeping files | Explicit |

**Rationale:** Agent deletion can happen by accident (UI misclick, cleanup scripts, bugs). The team must self-heal to remain functional.

---

## R15. Written Orders & GitHub Trail

| ID | Rule | Source |
|----|------|--------|
| R15.1 | Every command from one agent to another **MUST be accompanied by a written .md file** using a template from the sender's role-plugin | Explicit |
| R15.2 | Every report back from an agent **MUST be a written .md file** using a template from the reporter's role-plugin | Explicit |
| R15.3 | Attachments (design docs, code reviews, task specs, reports) **MUST be published on GitHub** as issue comments or new issues — not sent via AMP messaging | Explicit |
| R15.4 | AMP messages carry **only the GitHub issue/comment URL** pointing to the attachment — never the file content itself | Explicit |
| R15.5 | The GitHub issue trail serves as the **permanent audit log** of all orders, decisions, and deliverables | Explicit |
| R15.6 | The **MANAGER is the only agent exempt** from R15.1-R15.4 — the MANAGER may send direct instructions via AMP without GitHub issues | Explicit |
| R15.7 | Each role-plugin **MUST include message templates** in its `shared/` or `references/` directory for: work requests, status reports, approval requests, handoff documents | Explicit |

**Rationale:** AMP messaging has size limits and no persistent storage. GitHub issues provide permanent, searchable, linkable records. This creates a complete paper trail of all governance actions and prevents information loss when agent conversations are compacted or sessions end.

---

## R16. Password Never Shared with Agents (CRITICAL)

| ID | Rule | Source |
|----|------|--------|
| R16.1 | The governance password **MUST NEVER be given to any agent** in a task instruction, prompt, or AMP message | Explicit |
| R16.2 | Agents MUST NEVER use the user's governance password or session cookies. The server MUST reject any API request where an agent process attempts to authenticate using user credentials. Agent authentication is exclusively via AID session secrets (`$AID_AUTH` / `mst_*` tokens) | Explicit |
| R16.3 | When an agent needs to perform a password-protected operation (team creation, title change), the API call triggers a **UI popup** that the **user enters manually** | Explicit |
| R16.4 | The MANAGER agent requests the operation via API. If the API requires a password, the MANAGER must inform the user: "This operation requires your governance password. Please enter it in the UI popup." | Explicit |
| R16.5 | The user **physically types** the password in the browser dialog — the agent never sees, stores, or transmits the password | Explicit |
| R16.6 | Any agent that receives a governance password in its prompt MUST refuse to use it and ask the user to enter it via the UI instead | Explicit |
| R16.7 | Scenario tests are the **only exception** — test automation may pass the password via API for testing purposes. This exception does not apply to production agent workflows. | Explicit |

**Rationale:** The governance password exists specifically to prevent agents from performing dangerous operations without user approval. If agents can receive and use the password, the security boundary is meaningless — any compromised or misbehaving agent could create teams, change titles, or delete agents without user knowledge. The password must always require a human in the loop.

**Implementation:** When an agent's API call returns HTTP 403 with `"Governance password required"`, the AI Maestro dashboard should intercept this and show a password entry popup to the user. The user enters the password, which is sent to complete the operation. The agent never sees the password.

---

## R17. Mandatory Core Plugin Installation (CRITICAL)

| ID | Rule | Source |
|----|------|--------|
| R17.1 | Every agent registered in an AI Maestro host **MUST** have the `ai-maestro-plugin` installed with `--scope local` in its working directory. This is a non-negotiable prerequisite for the agent to participate in the AI Maestro ecosystem | Explicit |
| R17.2 | The installation command is: `claude plugin install ai-maestro-plugin@ai-maestro-plugins --scope local` executed from inside the agent's working directory (`~/agents/<name>/`) | Explicit |
| R17.3 | This installation **MUST** happen at agent registration time — whether the agent is created via the Agent Creation Wizard, imported from an existing tmux session, or created programmatically by the MANAGER or any other agent | Explicit |
| R17.4 | The `ai-maestro-plugin` provides the foundational skills (agent-messaging, agent-identity, team-governance, team-kanban, etc.), AMP slash commands, and hooks (session tracking, message notifications) that every agent needs to operate within AI Maestro | Explicit |
| R17.5 | An agent **without** the `ai-maestro-plugin` installed locally is **non-functional** within the AI Maestro ecosystem — it cannot receive messages, participate in governance, use AMP commands, or receive session notifications | Explicit |
| R17.6 | The `CreateAgent` pipeline (element-management-service) **MUST** include a gate that installs `ai-maestro-plugin@ai-maestro-plugins --scope local` in the agent's working directory as part of agent provisioning | Explicit |
| R17.7 | The `RegisterAgentFromSession` flow (importing existing tmux sessions) **MUST** install the plugin with local scope before the agent is considered fully registered | Explicit |
| R17.8 | The `--scope local` flag is mandatory because the plugin must be installed in the agent's own project directory (`settings.local.json`), not in the user's global settings. Each agent is an independent Claude Code instance with its own local configuration | Explicit |
| R17.9 | If the plugin installation fails (marketplace not registered, network error, plugin not found), the agent registration **MUST** still succeed but the agent **MUST** be flagged with `corePluginMissing: true` in the registry. The dashboard MUST show a warning badge on such agents | Explicit |
| R17.10 | The MANAGER and CHIEF-OF-STAFF **SHOULD** periodically verify that all agents in their scope have the core plugin installed. If an agent is missing it, the COS or MANAGER should trigger a reinstallation | Explicit |
| R17.11 | For **non-Claude clients** (Codex, OpenCode, Gemini, Kiro, etc.), the `ai-maestro-plugin` **MUST** be converted to the target client's native format before installation. The conversion uses AI Maestro's cross-client conversion pipeline: (1) generate the Universal Plugin IR from the Claude source plugin, (2) emit the client-specific plugin via the appropriate client adapter. The converted plugin is stored in `~/agents/custom-plugins/<client>/ai-maestro-plugin-<client>/` and registered in the `ai-maestro-local-custom-marketplace` | Explicit |
| R17.12 | The `CreateAgent` and `RegisterAgentFromSession` pipelines **MUST** detect the agent's client type (from `compatible-clients` in `.agent.toml` or the agent registry) and automatically perform the conversion if the client is not `claude-code`. The agent receives the converted plugin, not the Claude original | Explicit |
| R17.13 | The converted plugin **MUST** preserve all skills, commands, hooks, and AMP functionality that the target client supports. Features that cannot be mapped (e.g., Claude-specific hook events with no Codex equivalent) are documented in the conversion loss report but do not block the installation | Explicit |

### R17.B — Core Plugin Protection (Cannot Be Removed or Disabled)

| ID | Rule | Source |
|----|------|--------|
| R17.14 | The `ai-maestro-plugin` **CANNOT be uninstalled** from any agent, neither via the AI Maestro UI nor via the AI Maestro API. The `ChangePlugin` pipeline MUST reject uninstall requests for this plugin with an error citing R17 | Explicit |
| R17.15 | The `ai-maestro-plugin` **CANNOT be disabled** from any agent, neither via the AI Maestro UI nor via the AI Maestro API. The `ChangePlugin` / `InstallElement` pipeline MUST reject disable requests for this plugin. Re-enablement happens only inside an AIO pipeline (Wake R17 gate, InstallElement) — never from a background loop | Explicit |
| R17.16 | The dashboard UI **MUST NOT show an uninstall button** (X icon) on the `ai-maestro-plugin` in the Config tab's Plugins section. Instead, it MUST show a **"core"** label indicating the plugin is a protected system component | Explicit |
| R17.17 | The `ai-maestro-plugin` **MUST NOT be installed at user scope** (`--scope user`). It MUST only exist at local scope in each agent's working directory. If the AI Maestro server detects the plugin enabled at user scope (`~/.claude/settings.local.json`), it MUST disable it at user scope on startup. User-scope installation would make the plugin load in ALL Claude Code projects on the host, not just AI Maestro agents | Explicit |
| R17.18 | **The AI Maestro server MUST NOT run a startup audit or a periodic enforcement loop that mutates agent state.** Core-plugin compliance is the sole responsibility of the **AIO Change\* pipelines** — `InstallElement`, `CreateAgent`, `wakeAgent`, `createSession`, `ChangeTitle`, `ChangeClient`, etc. Every such pipeline ends with post-gates (PG01/PG02/PG05) that guarantee the agent is left in a valid state: `ai-maestro-plugin` installed with `--scope local`, role-plugin matching the agent's title (or none if AUTONOMOUS). A background loop is an anti-pattern: it operates on stale data and fights the AIO contract. If an agent is ever found in an invalid state, the defect is in the pipeline that mutated it last — fix the pipeline, never add a repair loop | Explicit |
| R17.18a | **The AI Maestro server MUST NOT auto-register tmux sessions** it discovers during `/api/sessions` or `/api/agents` polling. Unknown sessions (tmux session names not matching any entry in `~/.aimaestro/agents/registry.json`) are surfaced ONLY as read-only `unregisteredSessions` in the sidebar's "Dead Sessions" list, enriched via `lib/session-history.ts` for display. No agent record is created, no plugin is installed, no AMP identity is provisioned, no tmux environment is mutated — until the user **explicitly** clicks "Revive" or "Import", which then invokes the normal `CreateAgent` AIO pipeline. This applies to both standard tmux sockets and OpenClaw sockets | Explicit |

### R17.C — Core Plugin Auto-Update

| ID | Rule | Source |
|----|------|--------|
| R17.19 | When AI Maestro is updated (version bump via `bump-version.sh`), the update script **MUST** also update the `ai-maestro-plugin` from the `Emasoft/ai-maestro-plugins` marketplace. If the marketplace is not registered, the script MUST register it first | Explicit |
| R17.20 | The AI Maestro server **MUST ensure** that the `Emasoft/ai-maestro-plugins` marketplace is registered on every startup. If it was removed or never installed, the server re-registers it automatically | Explicit |
| R17.21 | The `wakeAgent` function **MUST check** for core plugin presence before launching the program. If missing, it attempts installation via `InstallElement` AIO. If the installation fails, `wakeAgent` **MUST reject the wake** with an error citing R17 — a titled agent without its core plugin is non-functional (no hooks, no state detection, no messaging, cannot be stopped/hibernated safely) and must never be launched. The legacy `corePluginMissing: true` flag remains only as a diagnostic marker, cleared by the next successful `InstallElement` | Explicit |

### R17.D — Directory Trust Auto-Accept

| ID | Rule | Source |
|----|------|--------|
| R17.22 | When Claude Code starts in a new agent directory for the first time, it shows a directory trust prompt ("Do you trust the files in this folder?"). The AI Maestro server **MUST automatically accept** this prompt by sending `Enter` to the tmux session (the "Yes, I trust this folder" option is pre-selected). This runs in the background after program launch, polling the pane for up to 8 seconds | Explicit |
| R17.23 | The trust auto-accept **MUST NOT block** the wake API response. It runs asynchronously after the tmux session and program are launched | Explicit |

**Rationale — Why This Is a Governance Rule, Not Just a Requirement:**

The `ai-maestro-plugin` is the **load-bearing infrastructure** of the entire AI Maestro system. Its hooks are the ONLY mechanism through which the server detects agent state transitions (active, idle, waiting for input, permission prompt, exited). Without these hooks, the following **cascading failure** occurs:

1. **Agent state detection fails** — the server cannot tell if an agent is active, idle, waiting for user input, or has exited the client. The 5-state activity model (Exited, Permission, Waiting, Active, Idle) goes completely dark.
2. **Session control commands fail** — without knowing agent state, the server cannot determine when it is safe to send `/exit`, restart commands, or approve permission prompts. The Stop, Restart, and Approve buttons become non-functional.
3. **Plugin and title changes fail** — changing a governance title or role-plugin requires restarting Claude Code (exit + relaunch) so the new plugin is loaded. If the restart command fails (because state detection is broken), the ChangeTitle and ChangePlugin pipelines stall permanently.
4. **Team operations fail** — since ChangeTitle is broken, agents cannot be assigned to teams, COS cannot be appointed, and the minimum team composition (R12) cannot be enforced.
5. **AMP messaging fails** — the plugin provides the session tracking hook that enables push notifications and the message notification banner. Without it, agents cannot receive messages, and the entire inter-agent communication system is down.
6. **Auto-continue fails** — the keep-alive mechanism that prevents idle agents from timing out depends on detecting the idle state via hooks.
7. **Governance becomes unenforceable** — the governance skills (team-governance, agent-messaging, agent-identity) that agents use to understand and follow governance rules are bundled in this plugin. Without them, agents have no knowledge of R1–R16.

In short: removing the `ai-maestro-plugin` from a single agent doesn't just break that agent — it breaks every operation that touches that agent, and since governance operations (title changes, team membership, transfers) are transitive, a single broken agent can stall operations across the entire host.

This is why R17 is a **governance rule with system-wide enforcement**, not a soft recommendation. The server MUST proactively detect and repair violations (re-enable disabled plugins, reinstall missing plugins, flag non-compliant agents) rather than waiting for the user to notice and fix them manually.

**Implementation:**

```bash
# Claude Code agents — direct install:
cd ~/agents/<agent-name>/
claude plugin install ai-maestro-plugin@ai-maestro-plugins --scope local

# Non-Claude agents (e.g., Codex) — convert first, then install:
# 1. The CreateAgent pipeline calls convertAndStorePlugin() with source=ai-maestro-plugin
# 2. This generates ~/agents/custom-plugins/codex/ai-maestro-plugin-codex/
# 3. The converted plugin is installed in the agent's working directory
```

This writes the plugin reference to `~/agents/<agent-name>/.claude/settings.local.json` (or the equivalent config file for the target client) under `enabledPlugins`, ensuring the agent loads it on every session start.

---

## R18. Plugin Continuity on Client Change (CRITICAL)

| ID | Rule | Source |
|----|------|--------|
| R18.1 | When an agent's AI client changes (via `ChangeClient`), the agent **MUST NEVER** be left without its previously installed plugins. Every plugin that was installed for the old client **MUST** be re-emitted in a format compatible with the new client | Explicit |
| R18.2 | The `ChangeClient` pipeline **MUST** enumerate all plugins currently installed in the agent's working directory (role-plugin + normal plugins, enabled and disabled) BEFORE uninstalling anything. This snapshot is the set of plugins that MUST be preserved | Explicit |
| R18.3 | For each plugin in the snapshot, `ChangeClient` **MUST** ensure a version compatible with the new client exists, using the following resolution order: **(a)** if a native version already exists in `~/agents/custom-plugins/<new-client>/<name>/` or the client's cache, use it; **(b)** else if a Universal Plugin IR exists in `~/agents/custom-plugins/.abstract/<name>/`, call `emitForClient(name, newClient)` to generate the new-client version from the IR; **(c)** else call `convertAndStorePlugin(name, oldClient, [newClient])` which parses the existing plugin, builds the Universal IR automatically, and then emits for the new client | Explicit |
| R18.3b | **Asymmetric conversion rule (CRITICAL):** Claude is the richest plugin format. Any conversion X→Claude is lossy (features not expressible in the reduced source format cannot be invented). When the target client is `claude`, `ChangeClient` **MUST** use the canonical Claude source (checked first in `~/.claude/plugins/cache/<marketplace>/<name>/<version>/`, then in `~/agents/role-plugins/<name>/` for role-plugins). If no canonical Claude source exists, `ChangeClient` **MUST refuse to perform a lossy X→Claude conversion** and abort with a clear error instructing the user to restore the Claude plugin cache | Explicit |
| R18.3c | **R18.3b implies:** a Universal IR built from a non-Claude source (e.g., from a prior Claude→Codex conversion) **MUST NOT** be reverse-emitted to Claude — doing so would silently lose features that the original Claude plugin had. The only legitimate path back to Claude is the canonical cache or a fresh install from the marketplace | Explicit |
| R18.3d | **General "prefer native" rule (CRITICAL):** `ChangeClient` **MUST NEVER** convert or emit a plugin if a native version already exists for the target client. The resolution order is strict: **(1)** client-native plugin cache (`~/.claude/plugins/cache/`, `~/.codex/plugins/cache/`, `~/.gemini/plugins/`, `~/.opencode/plugins/`, `~/.kiro/plugins/`), **(2)** local role-plugins marketplace (`~/agents/role-plugins/<name>/`) if the plugin's `.agent.toml` `compatible-clients` field includes the target client, **(3)** previously emitted custom-plugins (`~/agents/custom-plugins/<client>/<name>/` or `<name>-<client>/`), **(4)** emit from existing Universal IR only if no native version was found, **(5)** fresh conversion as absolute last resort. Skipping a native source in favor of conversion would silently degrade the plugin (conversion is lossy in every direction except claude→claude). Native sources — from GitHub marketplaces, from Haephestos-generated role-plugins, or from user installs — are always authoritative and must be used as-is | Explicit |
| R18.4 | Only AFTER all compatible versions are confirmed to exist may `ChangeClient` uninstall the old-client versions and install the new-client versions. If ANY plugin fails to convert, the entire `ChangeClient` operation **MUST abort** before touching the agent directory — no partial state is allowed | Explicit |
| R18.5 | The `ai-maestro-plugin` core plugin is subject to R18 in addition to R17: when the client changes, its converted version for the new client **MUST** be installed using the same conversion pipeline. R17's core plugin requirement is satisfied by the converted version | Explicit |
| R18.6 | Role-plugins (plugins with a quad-match `.agent.toml`) follow the same conversion pipeline as normal plugins, but the converted output preserves the original plugin name (no `-<client>` suffix) and is stored in `~/agents/role-plugins/<name>/`. The `.agent.toml`'s `compatible-clients` field is updated to include the new client | Explicit |
| R18.7 | The `ChangeClient` pipeline **MUST** set `restartNeeded = true` on success, because the client binary (claude / codex / gemini / etc.) must be relaunched for the new-client plugins to be loaded | Explicit |
| R18.8 | If a feature of the old plugin cannot be mapped to the new client (e.g., a Claude-specific hook event with no Codex equivalent), the conversion emits a loss report but the operation **MUST** still proceed. A plugin with reduced features is acceptable — an agent with no plugins is not | Explicit |
| R18.9 | The `ChangeClient` pipeline **MUST NOT** uninstall the role-plugin by calling `syncRolePlugin`, because `syncRolePlugin` uses the title-to-plugin map which assumes Claude. Instead, `ChangeClient` handles the role-plugin conversion explicitly as part of R18.3 | Explicit |
| R18.10 | After `ChangeClient` completes successfully, the agent's governance title (if any) **MUST NOT** change. The title → role-plugin binding (R11) remains satisfied by the converted role-plugin | Explicit |

**Rationale — Why This Is a Governance Rule:**

An agent's identity and capabilities are inseparable from its installed plugins. The governance title binding (R11), the mandatory core plugin (R17), and every skill or hook the agent relies on are all expressed through plugins. If `ChangeClient` removed plugins without re-installing them in the new client's format, the agent would lose its role (ARCHITECT becomes a plain shell), its governance capabilities (no team messaging, no title badge), and the core infrastructure (R17.5: "non-functional within the AI Maestro ecosystem"). This would violate the Title-plugin invariant, the Core-plugin-presence invariant, and — for titled agents — leave the team with a broken slot that the COS would have to recreate from scratch via R14.

The conversion infrastructure already exists (`convertAndStorePlugin`, `emitForClient`, the Universal Plugin IR pipeline, per-client adapters). R18 makes its use on client change **mandatory**, not optional.

---

## R19. MAINTAINER Title

| ID | Rule | Source |
|----|------|--------|
| R19.1 | MAINTAINER is a no-team governance title assigned to agents responsible for maintaining an external software project (typically a GitHub repository). Like AUTONOMOUS, a MAINTAINER is NOT a member of any team — it operates independently at the host level | Explicit |
| R19.2 | Every MAINTAINER agent MUST have a non-empty `githubRepo` attribute in the form `owner/repo`. The attribute is **immutable** once set — to change the repo, assign the MAINTAINER title to a different agent | Explicit |
| R19.3 | One MAINTAINER per repository on a given host. Assigning MAINTAINER to an agent when another active (non-deleted) MAINTAINER already owns the same `githubRepo` MUST be rejected with a uniqueness error | Explicit |
| R19.4 | A MAINTAINER's core workflow is: (a) poll GitHub issues every 5 minutes via `gh issue list`, (b) detect new unprocessed issues by diffing against a local ledger, (c) triage each new issue (bugs auto-triage; feature requests accepted only from the authorized `gh` user), (d) if valid, clone the repo, create a branch, edit files, run tests, commit, (e) bump the version and push to origin via `scripts/publish.py` | Explicit |
| R19.5 | The MAINTAINER uses the host's `gh` CLI authentication. No separate webhook secrets or listener ports are needed. The agent polls `gh issue list --repo <owner/repo> --state open --json number,title,author,labels,createdAt` and compares against `~/.aimaestro/maintainer/<agentId>/processed-issues.json` to detect new issues | Explicit |
| R19.6 | Feature requests and change proposals MUST only be accepted if the GitHub issue author matches the locally authenticated `gh` user (determined at runtime via `gh api user --jq .login`). Bug reports from any user are triaged normally. This prevents unauthorized users from directing the MAINTAINER to make arbitrary changes | Explicit |
| R19.7 | A MAINTAINER must NOT run destructive git operations on the repository beyond what the publish pipeline authorizes: force-push, history rewrite, tag deletion, branch deletion. All destructive operations require explicit MANAGER approval via an `approval-request` AMP message | Explicit |
| R19.8 | Before publishing any fix, a MAINTAINER MUST: (1) confirm the test suite passes, (2) confirm a version bump is actually required (not a doc-only change), (3) confirm R18 plugin continuity is satisfied for any bundled plugins in the target repo, (4) honor the repo's `pre-push` git hook if one exists | Explicit |
| R19.9 | MAINTAINERs can message: MANAGER, COS, AUTONOMOUS, other MAINTAINERs. They can be messaged by: MANAGER, COS, AUTONOMOUS, other MAINTAINERs, and the user. Team workers (architect/integrator/member/orchestrator) cannot contact MAINTAINERs directly — route through COS or MANAGER | Explicit |
| R19.10 | The MAINTAINER title is bound to the `ai-maestro-maintainer-agent` role-plugin (R11 binding). Per R17, the `ai-maestro-plugin` core plugin is also required | Explicit |
| R19.11 | A MAINTAINER agent can be hibernated safely — polling stops while hibernated, and unprocessed issues will be picked up on the next patrol cycle when woken. The processed-issues ledger persists across hibernation cycles | Explicit |

---

## R20. Marketplace Governance

These rules describe how AI Maestro organizes plugin marketplaces and their
contents. The key architectural distinction is between **containers** and
**marketplaces**:

- A **container** is a folder grouping multiple related marketplaces plus the
  shared universal IR hub (`.abstract/`). The two default containers are
  `~/agents/role-plugins/` and `~/agents/custom-plugins/`.
- A **marketplace** is a folder that follows a specific client's marketplace
  spec (manifest schema, source-path format, etc.) and is registered with
  that client's CLI. One container MAY hold many marketplaces — one per
  client format (Claude, Codex, OpenRouter, Gemini, …). Each is named
  `marketplace-<client>/` inside its container.

### CRITICAL — source vs install target (clarified 2026-04-20)

**The three AI Maestro local-marketplace containers
(`~/agents/{role,custom,core}-plugins/…`) are SOURCE STORAGE only. They
are publishing surfaces, NOT the installed location of any plugin.**

A plugin LIVES at its install target, which is ALWAYS the client's own
plugin cache (e.g. `~/.claude/plugins/cache/…`, `~/.codex/plugins/cache/…`),
reached via the client's own install protocol. This holds regardless of
where the plugin's source came from:

- a GitHub URL,
- a local folder,
- one of the 3 AI Maestro local marketplaces, OR
- a remote marketplace (`Emasoft/ai-maestro-plugins`, or any third-party).

In all 4 cases AI Maestro installs the plugin INTO the client by invoking
that client's protocol (for Claude: `claude plugin install`; for Codex:
the file-based edit of `~/.agents/plugins/marketplace.json` +
`~/.codex/config.toml`). AI Maestro only WRITES into
`~/agents/{role,custom,core}-plugins/…` when it is the author or converter
of the plugin — i.e. when there is no upstream source to install from
(Haephestos-generated customs, Claude→other-client conversions, core-plugin
emissions for non-Claude clients). In every other case the source folder
stays where the user pointed (GitHub, a local checkout, etc.) and AI
Maestro installs from there directly.

Uninstall likewise operates on the client target only — the AI Maestro
local source, when one exists, is preserved so a later reinstall doesn't
require re-emission. **AI Maestro NEVER deletes from the 3 source
containers; removing a source folder is a manual user action, outside
AI Maestro's scope, exactly as it would be for an arbitrary external
folder the user pointed at during install.** See R20.31.

**Scope + UI semantics of install / uninstall (R20.30):** Every plugin
lives in exactly one scope on the target client — either LOCAL
(per-agent, scoped to a single agent's working directory) or USER
(global, visible to every agent on the same client). Not all clients
support local scope; the per-client adapter declares this capability.

The UI has two distinct surfaces for the two scopes, and they MUST NOT
overlap:

| UI surface | Scope shown | Uninstall semantics |
|---|---|---|
| Agent Profile → Config → Plugins section | LOCAL scope only (the plugins installed in THIS agent's workdir) | LOCAL uninstall for this agent only — other agents using the same plugin are unaffected |
| Settings → Plugins Explorer → `<client>` tab | USER scope only (the plugins installed globally on this client) | USER uninstall for this client — affects every agent on that client simultaneously |

An uninstall button NEVER touches the opposite scope, and NEVER touches
the AI Maestro source containers. Cross-scope invisibility is R20.20;
the scoped-uninstall semantics above are R20.30.

Each client's marketplace has its OWN manifest schema per that client's spec:

- **Claude Code** — manifest at `<marketplace>/.claude-plugin/marketplace.json`;
  `source` is a string like `"./my-plugin"`; registered via
  `claude plugin marketplace add <dir>`.
- **Codex** — manifest at `<marketplace>/marketplace.json` (root, no
  `.claude-plugin/` wrapper); `source` is an object
  `{ "source": "local", "path": "./my-plugin" }` plus required
  `policy.installation` + `policy.authentication` + `category` + `interface`
  fields. Registered via the Codex equivalent of Claude's `marketplace add`.

AI Maestro shells out to each client's CLI for install/uninstall/enable/disable
rather than re-implementing these operations.

| ID | Rule | Source |
|----|------|--------|
| R20.1 | AI Maestro ships with one online marketplace (**DEFAULT PLUGINS**: `github:Emasoft/ai-maestro-plugins`) and two offline **containers** for converted and custom plugins: (a) **ROLE PLUGINS CONTAINER** at `~/agents/role-plugins/`; (b) **CUSTOM PLUGINS CONTAINER** at `~/agents/custom-plugins/`. Each container holds one marketplace subfolder per client format AND the shared `.abstract/` universal IR hub (R20.8-R20.9). **Naming convention (R20.3 v3.7.0):** Claude marketplaces have no client prefix: `custom-marketplace/`, `roles-marketplace/`. All other clients use `<client>-custom-marketplace/`, `<client>-roles-marketplace/`. Claude plugin names have no suffix; non-Claude plugins are suffixed: `<name>-<client>`. Each per-client marketplace is registered separately with its own client CLI. | Explicit |
| R20.2 | Every agent MUST have the **CORE PLUGIN** — `ai-maestro-plugin@ai-maestro-plugins` — installed at `--scope local` (or the per-client equivalent) in its working directory. This mirrors R17 and is the core-plugin-presence invariant. | Explicit |
| R20.3 | On every UI interaction and every agent-initiated API call, the server MUST verify R20.2 is respected. Agents missing the core plugin MUST be forced to hibernate until they comply. This mirrors the enforcement loop described in R17 / core-plugin-presence invariant. | Explicit |
| R20.4 | Each agent MUST have installed at `--scope local` the default role-plugin for its governance title, OR any role-plugin whose `compatible-titles` (in its `.agent.toml`) includes that title. Defaults: **AUTONOMOUS** → `ai-maestro-autonomous-agent@ai-maestro-plugins` (or any other plugin declaring `compatible-titles=["AUTONOMOUS"]`); **MANAGER** → `ai-maestro-assistant-manager-agent@ai-maestro-plugins`; **MAINTAINER** → `ai-maestro-maintainer-agent@ai-maestro-plugins`; **CHIEF-OF-STAFF** → `ai-maestro-chief-of-staff@ai-maestro-plugins`; **ORCHESTRATOR** → `ai-maestro-orchestrator-agent@ai-maestro-plugins`; **ARCHITECT** → `ai-maestro-architect-agent@ai-maestro-plugins`; **INTEGRATOR** → `ai-maestro-integrator-agent@ai-maestro-plugins`; **MEMBER** → `ai-maestro-programmer-agent@ai-maestro-plugins`. **AUTONOMOUS is no longer "(none)"** — per R9.13 and R11.12 every agent MUST carry a role-plugin, and `ai-maestro-autonomous-agent` is the mandatory default that encodes workspace-isolation and cross-agent-mutation restrictions in its persona. | Explicit |
| R20.5 | The default role-plugin for a title MUST be installed automatically when the title is granted to an agent, unless the user (or a privileged caller) explicitly picks a different compatible role-plugin at assignment time. See ChangeTitle Gate 15. | Explicit |
| R20.6 | Agents whose client differs from Claude MUST have the converted version of the default role-plugin for their title installed automatically from the `marketplace-<client>/` folder of the appropriate container. If a native version exists in any registered marketplace (priority: client-native plugin cache → `marketplace-<client>/` inside the role-plugins container → `marketplace-<client>/` inside the custom-plugins container), it MUST be preferred over re-conversion. | Explicit |
| R20.7 | Agents changing their client (`ChangeClient`) MUST have every currently-installed plugin re-emitted into the target client's format and installed from the target container's `marketplace-<client>/` folder — unless a compatible native version for the new client already exists in any registered marketplace, in which case the native version MUST be used. See R18 for the full plugin-continuity pipeline. | Explicit |
| R20.8 | The **universal intermediate representation** of a converted *ordinary* plugin MUST be stored at `~/agents/custom-plugins/.abstract/<plugin-name>/plugin-universal-ir.yaml`. This is the IR hub used by `emitForClient` to re-emit the plugin for any target client without going back to the original source. `.abstract/` lives at the CONTAINER level, shared across every `marketplace-<client>/` folder inside that container. | Explicit |
| R20.9 | The **universal intermediate representation** of a converted *role-plugin* MUST be stored at `~/agents/role-plugins/.abstract/<plugin-name>/plugin-universal-ir.yaml`, paralleling R20.8 but isolated so role-plugin IR never bleeds into the ordinary-plugin namespace. Same container-level shared-hub semantics. | Explicit |
| R20.10 | AI Maestro MUST detect any update to the CORE plugin and apply it immediately with the exact command `claude plugin update ai-maestro-plugin@ai-maestro-plugins` (for Claude clients). For agents on other clients, the server MUST re-convert the new Claude version into every target client format and re-install it at `--scope local` in each affected agent's working directory, updating the corresponding `marketplace-<client>/` entry in the custom-plugins container. This enforces the **core-plugin-currency invariant**. | Explicit |
| R20.11 | AI Maestro MUST check for updates on every non-core plugin from the DEFAULT marketplace AND from every `marketplace-<client>/` inside the role-plugins and custom-plugins containers. When any marketplace reports a newer version, the server MUST notify the affected agents (via AMP or UI badge) and expose an idempotent API command that the agent (or user) can invoke to update the plugin. | Explicit |
| R20.12 | Plugins emitted from the universal IR as conversions of an original plugin MUST detect when the original plugin is updated and re-emit the converted version into every `marketplace-<client>/` that currently contains an emitted copy, bumping the version number. The re-emitted plugin MUST be registered in each target marketplace manifest (using that client's schema) so that R20.11 picks up the update and propagates it to the agents that have it installed. | Explicit |
| R20.13 | Agent names and agent UUIDs MUST be unique host-wide. Name collisions MUST be resolved at creation time (wizard rejects; API returns 409). Cross-host uniqueness is handled by agent-host address format (`<name>@<host>`). | Explicit |
| R20.14 | Each AI Maestro host MUST maintain a registry of agent identities and UUIDs that any other AI Maestro host on the Tailscale mesh can consult freely (read-only). This supports cross-host AMP routing and mesh-level identity lookups without any secret exposure. | Explicit |
| R20.15 | To exercise any privileged action that its title allows, an agent MUST prove its identity with an AID-signed token (see R14, AID identity rules) and present it to the AI Maestro API it wants to call. The server rejects any privileged call lacking a valid AID token — the token type (Bearer `aim_tk_*`, session secret `mst_*`, or AMP key `amp_live_sk_*`) determines the auth path but identity verification is non-negotiable. | Explicit |
| R20.16 | The identity authority for a given agent is either an AMP third-party provider OR the AI Maestro server that spawned the agent session. Agents registered against a local AI Maestro host get their identity certified by that host; agents federated from external providers get their identity certified by the remote provider. See the AMP messaging rules for the full delegation chain. | Explicit |
| R20.17 | Role-plugins MUST be identified by their profile file `<plugin-name>.agent.toml` at the plugin root AND by passing the **fourfold-identity validation check**: (1) `plugin.json` (or the per-client equivalent) `name` equals the plugin folder name; (2) the folder contains `<name>.agent.toml`; (3) `[agent].name` inside the TOML equals `<name>`; (4) `agents/<name>-main-agent.md` (or the per-client equivalent) exists with frontmatter `name: <name>-main-agent`. The per-client "equivalent files" are defined in each client's marketplace spec (e.g. Codex uses `.codex-plugin/plugin.toml` instead of `.claude-plugin/plugin.json`, and agents/main-agent markdown is normalized by the converter). Files failing any of these four checks are NOT role-plugins and MUST NOT be treated as such by any Change* pipeline. | Explicit |
| R20.18 | Every per-client marketplace MUST conform to its client's published marketplace spec — the AI Maestro converter is forbidden from inventing fields or bending a schema. Concretely: (a) **Claude** marketplaces MUST put the manifest at `<marketplace>/.claude-plugin/marketplace.json` and use `source: "./<name>"` as a plain string; (b) **Codex** marketplaces MUST put the manifest at `<marketplace>/marketplace.json` (root, no subfolder) and use `source: { "source": "local", "path": "./<name>" }` as an object plus the mandatory `policy`, `category`, and top-level `interface` fields from the Codex spec; (c) Every relative `source.path` or `source` string MUST start with `./` and MUST resolve to a plugin folder located inside the same `marketplace-<client>/` root — no `../` traversal, no absolute paths, no cross-client path leakage. When a new client (OpenRouter, Gemini, Kiro, …) publishes its marketplace spec, the generator MUST be extended with a dedicated emitter for that schema rather than reusing an existing client's code. | Explicit |
| R20.19 | An agent MAY have additional optional plugins installed at `--scope local` beyond the required CORE (R20.2) and TITLE role-plugin (R20.4), selected from any registered marketplace via the Agent Profile → Config → Marketplaces view. Optional plugins are NOT subject to the auto-reinstall enforcement loop of R20.3 — only CORE and TITLE role-plugin are mandatory. | Explicit |
| R20.20 | Scope isolation: plugins installed at `--scope user` via Settings → Plugins Explorer MUST NOT appear in any agent's local plugin list, and plugins installed at `--scope local` via Agent Profile → Config MUST NOT appear in the user-scope listing. Enable/disable state is per-scope and completely independent. SCEN-021 verifies this invariant end-to-end. | Explicit |
| R20.21 | The converter + validator pipeline MUST treat per-client marketplace folders (Claude: `custom-marketplace/` / `roles-marketplace/`; others: `<client>-custom-marketplace/` / `<client>-roles-marketplace/`) as independent marketplaces, each registered separately with its target client's CLI. When the server registers or refreshes marketplaces at startup, it MUST iterate over every per-client marketplace folder inside both containers and call the matching client's `<cli> plugin marketplace add|update` — never assume a single container-wide marketplace, and never mix two clients' plugins inside the same marketplace folder. | Explicit |
| R20.22 | The universal IR hubs (`.abstract/` at container level, R20.8 + R20.9) are shared across ALL per-client marketplaces within their container. Re-emitting a plugin for a new client MUST read the IR from the container's `.abstract/<name>/plugin-universal-ir.yaml` and write the emitted plugin into the correct per-client marketplace subfolder of the same container. The IR MUST NOT be duplicated into per-client subdirectories. | Explicit |
| R20.23 | **Multi-client plugin duplication (v3.7.0):** If a role-plugin's `.agent.toml` declares `compatible-clients` with multiple clients, the plugin MUST be stored as a **separate emitted copy** inside EACH compatible client's marketplace directory. Each copy's `.agent.toml` retains the FULL `compatible-clients` list (so any consumer can see what other clients the plugin supports); only the emitted code, manifest format, and folder name differ per client. The shared `.abstract/` IR is the single source of truth; each marketplace copy is an independently emitted artifact. A plugin is NEVER shared by symlink or reference across marketplace directories — each client's CLI must be able to install from its own marketplace without cross-client path resolution. For **custom plugins** (which do NOT have `.agent.toml`), the target client is determined by the name suffix: `<name>-codex` → codex, `<name>-gemini` → gemini, `<name>` (no suffix) → claude. Custom plugins converted for multiple clients are likewise duplicated, one per marketplace. | Explicit |
| R20.24 | **Role-plugin vs custom-plugin distinction (v3.7.0):** The presence of a `<name>.agent.toml` file at the plugin root is the SOLE marker that distinguishes a role-plugin from a custom (ordinary) plugin. Custom plugins MUST NOT contain `.agent.toml` files. The converter MUST only write `.agent.toml` (via `writeConvertedAgentProfile`) for role-plugins, never for custom plugins. Client detection for custom plugins relies on the name suffix convention, not on any TOML field. | Explicit |
| R20.25 | **Core-plugins container (v3.7.1, clarified 2026-04-16):** A third container at `~/agents/core-plugins/` holds the converted versions of the `ai-maestro-plugin` (the CORE plugin) for non-Claude clients ONLY. Structure: `.abstract/ai-maestro-plugin/` (shared IR), `<client>-core-marketplace/ai-maestro-plugin-<client>/` (per-client emitted copy). **Claude does NOT use this container AT ALL** — Claude installs the core plugin from the remote `Emasoft/ai-maestro-plugins` marketplace and there is NO `~/agents/core-plugins/core-marketplace/` directory, NO local Claude core manifest, and NO Claude CLI marketplace registration for the core-plugins container. Non-Claude clients install the core plugin via their respective per-client adapter (`lib/client-plugin-adapters/<client>-adapter.ts`) which copies files directly from `<client>-core-marketplace/ai-maestro-plugin-<client>/` into the agent's working directory — there is no marketplace registration for core-plugins on any client side. When the remote core plugin updates, the server MUST re-emit into every `<client>-core-marketplace/` that exists (R20.10 + R20.12). | Explicit |
| R20.26 | **NO-RENAMING-RULE-FOR-PLUGINS (v3.7.0):** Plugin names (both folder name and manifest name) are **immutable** once created. No AI Maestro API, UI action, or script/skill may rename an existing plugin. Names MUST be treated as permanent identifiers. Conversion behavior: (a) The converter computes the target name (Claude: `<name>`, others: `<name>-<client>`) and checks whether a folder with that exact literal name exists in the target marketplace. Example: original `programmer-plugin` → codex target name is `programmer-plugin-codex`. (b) If `programmer-plugin-codex` already exists in the codex marketplace → **overwrite** (update in place). (c) If `programmer-plugin-codex` does NOT exist → **write new**, regardless of whether identical plugins exist under different names. No similarity check, no deduplication. (d) There is no plugin registry beyond the filesystem — "the DB is the filesystem". Plugin dirs and their manifests ARE the registry. No external database, no rename tracking, no deduplication index. | Explicit |
| R20.27 | **Manifest-name MUST equal folder-name (v3.7.1):** Every plugin's manifest `name` field MUST be exactly equal to the plugin's folder name. This rule applies to: (a) `.claude-plugin/plugin.json` for Claude plugins — `name === basename(folder)`; (b) `.codex-plugin/plugin.json` for Codex plugins — `name === basename(folder)` (which already includes the `-codex` suffix per R20.26); (c) any analogous manifest for future clients. The converter pipeline (`plugin-storage-service.ts::emitForClient`, `plugin-storage-service.ts::emitPluginToDir`) MUST rewrite the manifest `name` to match the target folder name whenever the target folder name differs from the source name (i.e. any non-Claude target). For role-plugins the fourfold-identity rule (R20.17) extends this to THREE additional checks: `<name>.agent.toml` filename, `[agent].name` inside the toml, and `agents/<name>-main-agent.md` frontmatter — ALL must match the folder name. The canonical marketplace `source` path (R20.18) is derived from the folder name, so a mismatch between folder and manifest breaks marketplace discovery. Validators and installers MUST reject any plugin whose folder name ≠ manifest name. | Explicit |
| R20.28 | **Five canonical local marketplace folder patterns (v3.7.1):** The ONLY valid local marketplace folder names under `~/agents/` are exactly these five patterns. No other folder is ever registered as a marketplace, and no additional pattern is ever invented: (1) `~/agents/role-plugins/roles-marketplace/` — Claude role-plugins. (2) `~/agents/role-plugins/<client>-roles-marketplace/` — per-client role-plugins for codex, gemini, kiro, opencode. (3) `~/agents/custom-plugins/custom-marketplace/` — Claude custom (ordinary) plugins. (4) `~/agents/custom-plugins/<client>-custom-marketplace/` — per-client custom plugins. (5) `~/agents/core-plugins/<client>-core-marketplace/` — per-client converted core plugin (Claude is absent by R20.25). The installer MUST create every folder pattern that is applicable for the installed clients and MUST write a valid manifest inside each — even if the plugins array is currently empty. Filesystem-only per-client marketplaces (non-Claude) use a flat `marketplace.json` at the root of the marketplace folder; Claude marketplaces use `.claude-plugin/marketplace.json` at the CONTAINER level (not the per-client marketplace) per Claude's spec. | Explicit |
| R20.29 | **Source-vs-install-target invariant (v3.7.2, 2026-04-20):** The three AI Maestro local-marketplace containers under `~/agents/{role,custom,core}-plugins/` are SOURCE STORAGE / publishing surfaces, NOT the installed location of any plugin. A plugin LIVES at its install target — the client's own plugin cache (`~/.claude/plugins/cache/…`, `~/.codex/plugins/cache/…`, etc.) — reached via that client's own install protocol (`claude plugin install` for Claude; file-based edits to `~/.agents/plugins/marketplace.json` + `~/.codex/config.toml` for Codex). This invariant holds regardless of the plugin's SOURCE: whether the source is (a) a GitHub URL, (b) a local folder, (c) one of the 3 AI Maestro local marketplaces, or (d) a remote marketplace like `Emasoft/ai-maestro-plugins`, the install step ALWAYS invokes the client's own protocol to write into the client's target state. AI Maestro only WRITES into the local source containers when it is the author or converter of the plugin (Haephestos-generated customs, Claude→non-Claude conversions, core-plugin emissions for non-Claude clients); in every other case the plugin's source stays where the user pointed. Uninstall operates on the client target only — the AI Maestro source, when one exists, is preserved across uninstall/reinstall cycles so later reinstalls do not require re-emission. **The 3 local source containers behave exactly like any external folder a user might point at during install: AI Maestro never deletes from them. Removing a source folder is a manual user action, outside AI Maestro's scope.** Tested by SCEN-026 Phase 1 S008 (source + target layers both asserted independently) and Phase 2 S012 (source folders preserved after target swap). | Explicit |
| R20.30 | **Scope semantics of install + uninstall (v3.7.2, 2026-04-20):** Every plugin install uses the client's own protocol and lands in exactly one scope — either LOCAL (per-agent, scoped to a single agent's working directory) or USER (global, visible to every agent on the same client). Not all clients support local scope; the installer MUST check the client's capability via the per-client adapter before offering local-scope install. Uninstall NEVER touches the AI Maestro source marketplaces; it calls the client's uninstall protocol at the scope where the plugin is installed: (a) LOCAL scope uninstall removes the plugin for ONE agent only — other agents that have the same plugin installed locally are completely unaffected; (b) USER scope uninstall removes the plugin from EVERY agent on that client simultaneously. An agent's "Config → Plugins" list MUST show only LOCAL-scope plugins installed in that agent's workdir, and the uninstall button in that list MUST perform a LOCAL-scope uninstall scoped to that agent alone. The global "Settings → Plugins Explorer → <client>" tab MUST show only USER-scope plugins installed for that client, and its uninstall button MUST perform a USER-scope uninstall. Cross-scope invisibility is R20.20; this rule adds the matching uninstall semantics. | Explicit |
| R20.31 | **Local source folders are user-owned (v3.7.2, 2026-04-20):** The 3 local-source containers `~/agents/role-plugins/`, `~/agents/custom-plugins/`, `~/agents/core-plugins/` and every per-client marketplace folder inside them are USER-OWNED storage. AI Maestro WRITES into them only when authoring a plugin (Haephestos), converting a plugin (cross-client emitter), or emitting the core plugin for a non-Claude client; AI Maestro NEVER DELETES a plugin folder from them. Even when every install referencing a given source has been uninstalled from every client, the source folder remains on disk as a reusable publishing artifact. Removing a source folder is explicitly the user's responsibility — the same way an arbitrary folder on the user's machine (pointed at during a "Install from folder" flow) would be the user's responsibility to clean up. AI Maestro's uninstall button never reaches into these folders. | Explicit |

---

## Invariants (Must Never Be Violated)

These are hard invariants that the system must maintain at all times:

1. **COS-membership invariant**: `team.chiefOfStaffId === agentId` implies `team.agentIds.includes(agentId)`
2. **Singleton-MANAGER invariant**: At most one agent has `managerId === agentId` globally
3. **Single-team invariant**: A non-MANAGER agent appears in `agentIds` of at most one team
4. **Name-uniqueness invariant**: No two teams have the same name (case-insensitive)
5. **COS-immutability invariant**: COS title can only be removed by deleting the team (not by title reassignment)
6. **Manager-team invariant**: Teams cannot exist in an active (non-blocked) state without a MANAGER on the host
7. **Team-agent-lifecycle invariant**: Team agents cannot be woken while teams are blocked (no MANAGER)
8. **Title-plugin invariant**: Every agent (INCLUDING AUTONOMOUS) has exactly one role-plugin installed matching their title. Agents without a role-plugin cannot exist at rest — the only transient "no role-plugin" window is the instant inside a Change* pipeline between uninstall and install, and the agent is never persisted in that state (see R9.13, R11.12)
9. **Minimum-composition invariant**: Every team must have at least 5 agents covering all 5 required titles (COS, ARCHITECT, ORCHESTRATOR, INTEGRATOR, MEMBER)
10. **Role-boundary invariant**: No agent may perform tasks outside its title's role-plugin scope
11. **Team-resilience invariant**: Deleted core title agents must be immediately recreated by COS (or MANAGER for COS)
12. **Written-orders invariant**: All inter-agent commands and reports must be written .md files with GitHub issue attachments (MANAGER exempt)
13. **Password-secrecy invariant**: The governance password must never be transmitted to, stored by, or used by any agent — only the human user may enter it
14. **Core-plugin-presence invariant**: Every agent registered in the AI Maestro host must have `ai-maestro-plugin@ai-maestro-plugins` installed with `--scope local` in its working directory
15. **Core-plugin-protection invariant**: The `ai-maestro-plugin` cannot be uninstalled, disabled, or moved to user scope on any agent — it is a permanent, enabled, local-scope fixture
16. **Core-plugin-currency invariant**: The `ai-maestro-plugin` must be updated from the marketplace whenever AI Maestro itself is updated
17. **Plugin-continuity invariant**: When an agent's client changes, every plugin that was installed for the old client must be re-emitted and re-installed in a format compatible with the new client — no agent may ever be left without its plugins as a side effect of `ChangeClient`
18. **MAINTAINER-repo-uniqueness invariant**: At any time, at most one active (non-deleted) agent has a given `githubRepo` value. Two MAINTAINERs cannot maintain the same repository on the same host
19. **Marketplace-source-path invariant** (R20.18): every `source` field in a per-client marketplace manifest starts with `./`, resolves to an existing folder inside the same `marketplace-<client>/` root, and conforms to that client's marketplace spec (Claude string `"./x"` vs Codex object `{source:"local", path:"./x"}`)
20. **IR-storage-location invariant** (R20.8 + R20.9 + R20.22): converted-plugin universal IR lives at the CONTAINER level — `~/agents/custom-plugins/.abstract/<name>/` for ordinary plugins and `~/agents/role-plugins/.abstract/<name>/` for role-plugins — NEVER inside any `marketplace-<client>/` subfolder and NEVER duplicated per client
21. **Scope-isolation invariant** (R20.20): user-scope and local-scope plugin lists are disjoint — no plugin install at one scope ever appears in the listing or affects the enable-state of the other scope
22. **Container-marketplace separation invariant** (R20.1 + R20.21): `~/agents/role-plugins/` and `~/agents/custom-plugins/` are CONTAINERS, not marketplaces. A container holds zero or more `marketplace-<client>/` subfolders plus the shared `.abstract/` IR hub. The container folder itself is NEVER registered with any client CLI as a marketplace — only the individual `marketplace-<client>/` subfolders are

---

## R21. All-In-One Pipeline Architecture (CRITICAL — IRON)

This section is the **single, complete source** for the AIO architecture. Every rule that previously lived only in the `make-all-in-one` skill is folded in here, plus the user's 2026-05-06 composition directive at the top. Use this — not the skill — as the authoritative reference.

**The user's verbatim directive (2026-05-06) — load-bearing wording, do not paraphrase:**

> macro all-in-one api functions must handle the details via other all-in-one function. for example uninstall marketplace must handle internally the uninstall of all its plugins from all the agents or global scope) before actually uninstalling the marketplace, otherwise the agents will break. this meame that internally they must call the all-in-one function of the sgent, like change-plugin, and it must internally calls the all-in-ones of uninstalling plugins, changing-title, change-team, etc. since all those things are affected (change-plugin all-in-one must also directly take care of enable-disable a plugin in the agent, a task that does not have a dedicated all-in-one since it is part of change-plugin api command of any agent). in other words: you must remember the other all-in-one rule: all-in-one api commands must call internally other all-in-one commands when they need to do something, since they cannot duplicate the functionality internally ("only one way to do one thing, one single piece of code to debug in the whole codebase" is the rule). So for example if the all-in-one api command to change title is called, internally it must call the others all-in-one commands to do the changes to the agent plugins. beware of the names: the aio change-plugin is actually an api function about an agent configuration, not about plugins. uninstalling a plugin completely from all agents instead is a consequence of calling uninstall-plugin, a api function that is about plugins, not about agents. and it is needed by the aio uninstall-marketplace.

### R21.0 — What an AIO function is

An all-in-one (AIO) function is a **single pipeline function** that represents the **only way** to perform a specific sensitive operation in the codebase. It consists of a deterministic, linear sequence of numbered gates: pre-execution gates validate whether the operation is allowed and safe, the execution performs the mutation, and post-execution gates repair any state the operation may have broken. The guarantee: **no matter when, from where, or from whom the function is called, it ALWAYS leaves the system in a valid state consistent with the project's rules.**

### R21.1 — One Function Per Operation (Rule 1)

For every sensitive mutation (create, delete, update, transfer, assign, revoke, etc.), there exists EXACTLY ONE AIO function. No other code path performs the same mutation. If code elsewhere needs this operation, it calls the AIO function — it never duplicates the logic. **Thin wrappers are forbidden**; they create a second entry point that may drift from the real pipeline. Aliases like `installPluginLocally` that wrap `ChangePlugin(action='install', scope='local')` are deprecated and must be removed.

### R21.2 — Helpers Must Be Pure (Rule 2)

Helper functions may perform read-only checks, lookups, or transformations only. Any function that writes to storage, modifies state, calls external services, or produces side effects MUST be an AIO function with the full gate pipeline. **A helper that mutates is a backdoor that bypasses all safety gates.** This includes shell-outs to CLIs that mutate state — those must be encapsulated inside an AIO, not invoked from a helper.

### R21.3 — Authorization Inside, Not Outside (Rule 3)

Callers verify identity only (who is the requester?). All authorization decisions (is this requester allowed to do this specific operation on this specific target?) happen inside the AIO function at Gate 0 (`gate0Auth`). No caller duplicates authorization checks — the AIO function is the single authority. Routes call `authenticateFromRequest` for identity, then immediately delegate to the AIO. No identity-based fork in the route layer.

### R21.4 — AIO Composition (the 2026-05-06 directive, codified)

When an AIO needs to perform a task that an existing AIO already covers, it MUST call that AIO. It MUST NOT re-implement the underlying primitive (`updateAgent`, `loadJsonSafe`, `claude plugin update`, `tmux send-keys`, …) directly. **"Only one way to do one thing, one single piece of code to debug in the whole codebase."** Inlining a cascaded mutation in a post-gate is forbidden — call the other AIO function so its full gate pipeline runs.

### R21.5 — Naming convention is part of the rule

Names mislead unless interpreted carefully:

| AIO name | Scope | Purpose |
|---|---|---|
| `ChangePlugin` | one agent (or user-scope) | Configures a SINGLE target's plugin set. Actions: install / uninstall / enable / disable / update FOR THAT TARGET. NOT a global plugin operation. |
| `UninstallPlugin` (plugin-scoped, cross-agent) | the plugin everywhere | Removes a plugin from every agent and from user-scope. Cascades through `ChangePlugin` per (target, scope). |
| `UpdatePlugin` (plugin-scoped, cross-agent) | the plugin everywhere | Updates a plugin in every agent and user-scope where it is installed. Cascades through `ChangePlugin(action='update')`. |
| `InstallPlugin` (plugin-scoped) | a target list | Installs a plugin into one or more targets. Cascades through `ChangePlugin(action='install')`. |
| `UninstallMarketplace` (= `DeleteMarketplace`) | marketplace-wide | Cascades through `UninstallPlugin` per plugin in the marketplace, THEN removes the marketplace itself. |
| `InstallMarketplace` (= `CreateMarketplace`) | marketplace-wide | Registers the marketplace; does NOT auto-install plugins (that is the user's explicit action). |
| `UpdateMarketplace` | marketplace-wide | Refreshes the marketplace's manifest + cache. Does NOT auto-update plugins. |
| `CheckPluginUpdates` | plugin-scoped | Detects which plugins have new versions available. Read-only. |
| `CheckMarketplaceUpdates` | marketplace-wide | Detects whether a marketplace has new plugin versions or new plugins available. Read-only. |

The "Change*" prefix means "change the configuration of one entity" (one agent, one user-scope config). The "Install*Plugin / Uninstall*Plugin / Update*Plugin" verbs (no "Change" prefix) mean "operate on a plugin across every place it is installed". The "InstallMarketplace / UninstallMarketplace / UpdateMarketplace" verbs operate on marketplaces and, when destructive, cascade through the plugin-scoped verbs. `enable` / `disable` is NOT a separate AIO — it is an action inside `ChangePlugin`'s action enum.

### R21.6 — Mandatory cascade chains

The destructive cascade chain is non-negotiable:

```
UninstallMarketplace(name)
  └─ for each plugin in the marketplace:
       UninstallPlugin(plugin, marketplace)        # cross-agent AIO
        └─ for each agent that has this plugin:
             ChangePlugin(agentId, action='uninstall')  # per-agent AIO
              └─ may trigger ChangeTitle / ChangeTeam if invariants require
       (then user-scope uninstall via ChangePlugin(null, scope='user'))
  └─ then remove the marketplace itself (CLI + cache + settings)
```

A `UninstallMarketplace` that skips the cascade leaves agents with dangling `<plugin>@<deleted-marketplace>` keys in their `settings.local.json` — those keys reference a marketplace that no longer exists, the next `claude` launch fails, and the agent **breaks**. Identical reasoning applies to `UninstallPlugin` skipping its `ChangePlugin` per-agent cascade.

`ChangeTitle` cascades into `ChangePlugin(rolePluginSwap=true)` for role-plugin transitions and into `ChangeTeam` for team-membership changes — never into direct `settings.local.json` or `teams.json` writes.

### R21.7 — Cross-cutting six API surface

The user-facing API exposes EXACTLY six plugin/marketplace operations:

| API | AIO it calls |
|---|---|
| 1. Check plugin updates | `CheckPluginUpdates` |
| 2. Install plugin | `InstallPlugin` |
| 3. Update plugin | `UpdatePlugin` |
| 4. Check marketplace updates | `CheckMarketplaceUpdates` |
| 5. Install marketplace | `InstallMarketplace` (= `CreateMarketplace`) |
| 6. Update marketplace | `UpdateMarketplace` |

Uninstall is reachable through the same surfaces (each Install* AIO has a matching `Uninstall*` cousin reached via DELETE / `action='uninstall'`). New endpoints scattered around the codebase that mutate plugin or marketplace state outside these six pipelines are forbidden.

### R21.8 — Settings-management endpoints are not plugin operations

Endpoints that read or write *settings* about plugin/marketplace policy (e.g. `GET/PATCH /api/settings/auto-update`, `POST /api/settings/auto-update/run`) are NOT plugin operations and do NOT count against the six. They are configuration endpoints for the policy that drives the AIOs above. The "Run now" trigger calls into the AIOs but does not introduce a parallel mutation path.

### R21.9 — Gate Architecture: numbering and naming

Every AIO uses this exact gate numbering — no shortcuts:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `G00`–`G99` | Pre-execution gate (validates ONE condition) | `G06: Path traversal rejected` |
| `EXE` | Execution (the mutation itself — unique, not a gate) | `EXE: Record written to database` |
| `PG01`–`PG99` | Post-execution gate (repairs ONE invariant) | `PG04: Dependent entity repaired via UpdateDependency()` |

The execution step uses `EXE:`, not a numbered gate, because it is unique and fundamentally different from validation/repair gates. There is exactly one execution per pipeline.

### R21.10 — Atomic Gates (one check per gate)

Each gate checks EXACTLY ONE condition. If a gate validates name format AND scope AND target existence, split it into three gates. Composite conditions (NOT/AND/OR/XOR) inside a single check are allowed, but multiple distinct checks are not. This ensures:
- The operations log pinpoints the exact failure
- Each gate can be tested independently
- Gate numbers are stable references in documentation and error messages

**Wrong:** `G00: Validate inputs — name, scope, target all valid`
**Right:** `G00: Validate name format / G01: Validate scope / G02: Validate target exists`

### R21.11 — Pre-Execution Gates (canonical sequence)

| Gate | Purpose |
|------|---------|
| G00 | Authorization (`gate0Auth`) |
| G01–Gk | Validate each input field (one gate per field) |
| Gk+1 | Resolve context (lookup target entity from registry) |
| Gk+2 | Validate resolved context |
| ... | Path/security checks (no traversal, allowed roots) |
| ... | Directory/resource exists (or create) |
| ... | Protected resource guard (e.g. R17 core plugin) |
| ... | Permission/role guard (e.g. R3 MANAGER singleton) |
| ... | Idempotency check (skip EXE if already in desired state, BUT post-gates still run) |
| ... | Dependency check (parent entity exists, marketplace registered, ...) |
| ... | Status check (system not busy / not hibernated / not reindexing / ...) |
| Gk+m | Variant detection + variant-specific gates (see R21.14) |

### R21.12 — Execution

The actual mutation — the smallest possible core operation. Write to database, modify a file, call an external API, kill a process, etc. Everything before this is validation; everything after is state repair. Tagged with `EXE:` in the operations log. **Never assigned a `G##` number.**

### R21.13 — Post-Execution Gates

Post-gates ALWAYS run, even when the idempotency gate skipped execution — stale flags or inconsistencies may still need repair.

| Gate | Purpose |
|------|---------|
| PG01 | Verify action took effect (read-back check) |
| PG02 | Update flags/metadata in registry (e.g. `corePluginMissing`) |
| PG03 | Scope consistency (deduplicate if resource exists at two levels) |
| PG04 | Dependent entity repair → call another AIO function |
| PG05 | Protected resource defense in depth → recursive AIO call if guard was bypassed |
| PG06 | Composition integrity (parent group still meets minimum requirements?) |
| PG07 | Duplicate detection (same resource at two scope levels?) |
| PG08 | Restart/notification (set `restartNeeded`, broadcast WebSocket event, ...) |

For every field the execution mutates, ask: **"What invariants in the rest of the system depend on this field?"** For each dependency, add a post-gate that either repairs the invariant or logs a warning for manual intervention. The post-gate must use other AIO functions for cascading mutations — it does not inline the logic (R21.4).

### R21.14 — Variant-Specific Gates (`[VariantName]` brackets)

When the system supports multiple variants of the same operation (different clients, different platforms, different formats), operations that behave differently per variant MUST use **separate sequential gates per variant** rather than a single gate with if/else branches.

```
G11: Detect client type
G12: [Claude]  Install plugin via Claude CLI
G13: [Codex]   Convert plugin to Codex format, then install
G14: [Gemini]  Convert plugin to Gemini format, then install
```

Each variant-specific gate:
- Is prefixed with the variant name in brackets: `[Claude]`, `[Codex]`, etc.
- Runs ONLY if the detected variant matches; other variant gates are skipped with a log entry
- Contains the complete logic for that variant — no shared mutable state between variant gates
- Can call variant-specific helper functions or other AIO functions

### R21.15 — Idempotency Gate

Every AIO SHOULD include an idempotency gate (typically G09) that checks if the desired state is already achieved. If so, the execution is skipped but **post-gates still run** (to repair any stale flags or inconsistencies). This prevents wasted work and avoids duplicate-action errors while still ensuring post-gate invariants are maintained.

### R21.16 — Protected Resource Pattern (four layers)

Resources that must NEVER be removed or disabled (e.g. R17 core plugin, R9 MANAGER singleton, R20.10 marketplace required for core plugin) are defended at FOUR layers:

1. **Pre-gate guard**: a dedicated pre-gate rejects remove/disable for the protected resource. Primary defense.
2. **Post-gate defense-in-depth**: a post-gate checks if the protected resource was somehow removed despite the pre-gate. If so, restores it via recursive AIO call.
3. **Startup enforcement**: a periodic server-side check audits all entities for the protected resource's presence; flags missing and attempts repair.
4. **UI protection**: the UI hides the remove/disable button for protected resources, showing a "core" / "required" / "system" badge instead.

All four layers reinforce each other — removing any one layer should not compromise the invariant.

### R21.17 — Result contract

Every AIO function returns this exact shape:

```ts
{
  success: boolean         // Did the full pipeline complete?
  error?: string           // Human-readable reason if failed (includes gate number)
  operations: string[]     // Ordered log of every gate's outcome
  // ... domain-specific fields (entity ID, timestamps, restartNeeded, ...)
}
```

The `operations` array is the debug trail. On failure, the last entry shows exactly where and why:

```
["G00: Name 'user-42' valid",
 "G05: DENIED — 'user-42' is a protected system account. Cannot delete."]
```

### R21.18 — Caller contract

Code that calls an AIO function MUST:
1. Provide identity/auth context (`authContext`) so Gate 0 can decide
2. Trust the result — if `success=true`, all invariants hold; if `success=false`, nothing was mutated
3. NEVER perform additional state mutations after the call — post-gates already handled everything

Code that calls an AIO function MUST NOT:
1. Duplicate gate checks before calling (the AIO checks everything)
2. Perform cleanup after the call (post-gates did it)
3. Catch and suppress errors (they indicate invariant violations that must be visible)
4. Exist as a second path for the same operation (R21.1 violation)

### R21.19 — Anti-Patterns (forbidden)

When asked to write code, refuse these patterns. They violate the AIO architecture:

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|---------------|------------------|
| "Create a helper that also writes X" | Helpers must be pure; writes bypass gates | Make it an AIO function with gates (R21.2) |
| "Add a shortcut function that calls the AIO with defaults" | Two paths = one will drift | Callers call the AIO directly (R21.1) |
| "Check authorization in the route AND in the function" | Duplicate checks = inconsistent rules | Auth only inside the AIO pipeline (R21.3) |
| "Add the cleanup logic after the AIO call in the caller" | Callers must not do post-mutation work | Add it as a post-gate in the AIO (R21.18) |
| "Skip the post-gates for performance" | Invalid state is never acceptable | Every post-gate runs, every time (R21.13) |
| "Put all validations in one gate" | Non-atomic gates hide which check failed | One check per gate — split (R21.10) |
| "Use a G## number for the execution step" | Execution is not a gate — it's the mutation | Use `EXE:` prefix (R21.9) |
| "Handle multiple variants in the same if/else block" | Variant logic gets tangled and untestable | Separate variant-specific gates (R21.14) |
| "Inline the cascaded mutation in the post-gate" | Bypasses the cascaded operation's own gates | Call the other AIO function (R21.4) |
| "Shell out to a CLI tool that does what the AIO does" | Bypasses the full gate pipeline | Call the AIO directly (R21.4) |
| "Add a `fetch('localhost/api/...')` loopback call" | HTTP loopback is fragile, adds latency, loses auth | Import and call the service function directly (R21.4) |
| "Manually bump a registry flag from a route handler" | Routes do identity, not state mutation | Move the flag bump into a post-gate (R21.13) |

### R21.20 — Consolidation procedure (scattered → AIO)

When multiple functions perform the same operation with slight variations:

1. **Catalog** all functions that perform the operation (grep for the raw mutation)
2. **Union** all their checks into one gate sequence (no check is lost)
3. **Union** all their cleanup steps into post-gates (no cleanup is lost)
4. **Create** the AIO function with the complete gate pipeline
5. **Replace** all callers to use the AIO function directly
6. **Delete** all the old scattered functions — no wrappers, no aliases, no compatibility shims
7. **Verify** no code path bypasses the AIO function (grep for the raw mutation — should hit only the AIO)

### R21.21 — Audit checklist (every PR touching an AIO)

Every PR that touches `services/element-management-service.ts` or any file declaring an AIO must answer:
1. Does this AIO call other AIOs for cross-cutting work, or does it duplicate primitive code? (R21.4)
2. If it removes a plugin/marketplace, does the cascade reach every agent that has the plugin? (R21.6)
3. Does it call any `loadJsonSafe`/`saveJsonSafe`/`updateAgent` directly when an AIO would have done the job? (R21.2)
4. Are gates atomic (one check each) and numbered consecutively? (R21.10)
5. Does each variant get its own `[VariantName]` gate, or is the if/else still tangled? (R21.14)
6. Do post-gates run even when the idempotency gate skipped execution? (R21.13, R21.15)

A PR that fails any of those is a R21 violation and must be refactored before merge.

### R21.22 — Operations that need an AIO

An operation needs an AIO function if ANY of these are true:
- It writes to persistent storage (database, file, registry)
- It modifies system state (processes, sessions, permissions)
- It has authorization requirements (not everyone can do it)
- Its failure could leave the system in an inconsistent state
- Multiple places in the code currently perform it (consolidation needed)
- It has cleanup side effects (cascading deletes, reference updates)

Read-only operations (queries, lookups, calculations) do NOT need AIO functions and SHOULD remain pure helpers (R21.2).

---

**Note on the `make-all-in-one` skill.** The skill at `~/.claude/skills/make-all-in-one/` predates this section. With v3.9.0 the skill is no longer the canonical source — this R21 section is. The skill remains useful as an authoring tutorial (the step-by-step process, the "create or consolidate" workflow), but the load-bearing rules that govern compliance live HERE. If the two ever drift, this section wins.

---

## Role-Based Permission Matrix

| Action | MEMBER | COS (own team) | ORCHESTRATOR | ARCHITECT / INTEGRATOR | MANAGER | AUTONOMOUS |
|--------|--------|----------------|--------------|----------------------|---------|------------|
| Join team | Via MANAGER/COS | Via MANAGER | Via MANAGER/COS | Via MANAGER/COS | N/A (host-level) | Via MANAGER/COS |
| Leave team | No (transfer) | No (COS locked) | No (transfer) | No (transfer) | N/A | No (transfer) |
| Add agent to own team | No | Yes | No | No | Yes | No |
| Remove agent from own team | No | Yes | No | No | Yes | No |
| Assign COS | No | No | No | No | Yes (password) | No |
| Create team | No | No | No | No | Yes (password) | No |
| Delete team | No | No | No | No | Yes (password) | No |
| Create transfer request | No | Yes (own team) | No | No | Yes | No |
| Approve/reject transfer | No | Yes (own team) | No | No | Yes | No |
| Wake agent | No | Own team only | No | No | Any agent | No |
| Hibernate agent | No | Own team only | No | No | Any agent | No |
| Message (see R6 graph) | COS + ORCH | All titles | COS+ARCH+INTEG+MEM | COS + ORCH | All titles | MGR+COS+AUTO |
