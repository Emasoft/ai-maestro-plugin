---
version: "5.3.3"
date: 2026-08-06
branch: governance-rules
conforms-to-spec: governance-rules@5.3.3
synced-blob: "a13bed73fa9e"
synced-at: 2026-08-08
---

## Table of contents

- §0. Canonical source + copies (READ THIS BEFORE EDITING)
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
- R22. GitHub Authorship Self-Identification (USER-set baseline)
- R23. Plugin↔Server Decoupling via the Frozen CLI Layer (CRITICAL — IRON)
- R24. Proactive Global Memory
- R25. Three-Pillars Task System (TRDD / PRRD / Kanban)
- R26. Identity Immutability — No Self-Mutation of Title / Role / Name / AID (CRITICAL — IRON, USER-set)
- R27. Self-Install Only via Core-Plugin Skills, With Approval + CPV Scan (IRON, USER-set)
- R28. Three-Check API Authorization (AID → Title → Portfolio Token) (CRITICAL — IRON, USER-set)
- R29. MANAGER Team & Agent Lifecycle Authority (IRON, USER-set)
- R30. COS Agent-Creation Requires a MANAGER Mandate; the 5-Member Base Is Invariant (IRON, USER-set)
- R31. Incomplete-Team Freeze (IRON, USER-set)
- R32. No Sudo Gates for Agents — AID Is Sufficient; Sudo Is USER-via-UI Only (CRITICAL — IRON, USER-set; SUPERSEDES prior agent-sudo behavior)
- R33. Signed-Ledger Recovery of Agent Auth State (IRON, USER-set)
- R34. The Signed Ledger Is the Ultimate Source of Truth (CRITICAL — IRON, USER-set)
- R35. Foreign Agent/User Host Approval (CRITICAL — IRON, USER-set)
- R36. Users Have AIDs; One MAESTRO Per Host (IRON, USER-set)
- R37. MAESTRO and the Single MAESTRO-DELEGATE (CRITICAL — IRON, USER-set)
- R38. Non-MAESTRO User Restrictions (IRON, USER-set)
- R39. Users Have No Terminal/Client → the ASSISTANT Agent (CRITICAL — IRON, USER-set)
- R40. Foreign-User Creation Approval (IRON, USER-set)
- R41. APPROVAL vs MANDATE (the two authorization protocols)
- R42. No Agent May Drive Another Agent — Messaging Is the ONLY Channel (CRITICAL — IRON, USER-set)
- R43. Multi-Host Governance Scope (IRON, USER-set)
- R44. Cross-Host Agent Migration (IRON, USER-set)
- R45. Teams Are Same-Host; Groups May Span Hosts (IRON, USER-set)
- R46. Unified Cross-Host Sidebar; User and Paired Agent Both Listed (IRON, USER-set)
- R47. VPN-Unique User Names; Remote Normal-User Registration (IRON, USER-set)
- R48. MAESTRO Console-Presence — Registration and Password Change Are Local-Only (CRITICAL — IRON, USER-set)
- R49. The Refusal Protocol — An Approver Is a Guide, Not a Gate (CRITICAL — IRON, USER-set)
- Role-Based Permission Matrix
- R50. One Operation, One All-In-One Function — And The Button Calls It (CRITICAL — IRON, USER-set)
- R51. All-Or-Nothing — An All-In-One Function Is a TRANSACTION (CRITICAL — IRON, USER-set)
- R52. The Write Boundary — ai-maestro Writes Inside Its Own Two Roots (CRITICAL — IRON, USER-set)

---

> **Bundled mirror — read this first**
>
> This file is a verbatim copy of the canonical governance rules. The single
> source of truth lives in the `Emasoft/ai-maestro` fork:
>
> - Canonical path: `docs/GOVERNANCE-RULES.md`
> - Stable raw URL (the long-lived `governance-rules` branch):
>   `https://raw.githubusercontent.com/Emasoft/ai-maestro/governance-rules/docs/GOVERNANCE-RULES.md`
> - NOTE (re-verified 2026-08-08): `main` still LAGS the canonical — it carries
>   v4.0.2 while `governance-rules` carries v5.3.3. Do NOT "correct" the URL or
>   the sync source to a `main` path; `governance-rules` is the authoritative
>   home, confirmed by fetching both branches and comparing `version:` fields,
>   never by trusting a doc's self-declared `branch:` frontmatter. **A query
>   against `main` 404s or returns v4.0.2, and neither means anything** — that
>   inference is exactly what produced the 2026-08-07 R42.8 error below.
> - **Is this copy current? Poll the BLOB, never the branch tip:**
>
>   ```bash
>   gh api "repos/Emasoft/ai-maestro/contents/docs/GOVERNANCE-RULES.md?ref=governance-rules" --jq .sha
>   # matches `synced-blob` above  ⇒  these exact bytes  ⇒  every rule read from
>   # this copy still holds. Differs ⇒ re-sync. It never says WHAT moved, only
>   # that something did — a moved blob is a prompt to re-read, not an answer.
>   ```
>
>   `3P-VER-05` of `design/specs/3-pillars-spec.md` makes this normative and
>   **FORBIDS the branch commit sha as a change signal**: the tip moves on every
>   unrelated commit, so a consumer polls, sees movement, refetches, gets a
>   byte-identical document, and records "checked, current" — manufacturing
>   confidence instead of supplying information. Measured upstream: the tip moved
>   across four unrelated commits while the spec blob sat unchanged for 13 days.
> - Synced from commit `e46764f6` on the `governance-rules` branch. **Provenance
>   only — deliberately NOT a frontmatter field**, so nobody polls it by reaching
>   for the nearest sha. The frontmatter carries exactly one pointer, and it is
>   the blob.
> - Re-synced into `ai-maestro-plugin` on: 2026-08-08 (v5.3.3 — adds **R42.8**,
>   the MANAGER/COS blocked-prompt unblock carve-out, plus the R22.2 and R39.2
>   factual corrections). **Read R42.8's verb list from the row, never from a
>   summary:** it is `block-state`, `read-prompt`, `answer` — exhaustive, with
>   `inject`/`slash`/`queue` excluded because they carry a CALLER decision.
> - **⚠ Re-sync THE TIP, not a file you fetched earlier.** This bundle was
>   stale for three days while the SSOT moved twice on consecutive days
>   (v5.3.2 2026-08-08 05:51Z → v5.3.3 06:03Z, twelve minutes apart). Reading
>   the row without first resolving the branch tip produced two wrong CORE
>   claims in two days — "R42.8 is not ratified" (it was, published a day
>   later) and "`block-state` is omitted deliberately" (a doc lag the hub
>   corrected within hours). Fetch `branches/governance-rules` FIRST, record
>   the sha, and treat any older copy as unread.
> - The pre-sync contradiction sweep of CORE's skills against R41–R52 is
>   recorded in PROJECT memory (ATOM-SBNM-OHF2) — run that sweep BEFORE every
>   future re-sync.
> - Bundled-doc version: see the `version:` field in the YAML frontmatter
>   above (5.3.3 at the time of this sync).
>
> Treat this file as **read-only** in this repo. To update:
>
> 1. Edit the canonical file in `Emasoft/ai-maestro` first (bump `version:`,
>    append a changelog entry).
> 2. Walk the §0 cross-reference index in this very file — every mirror, role-plugin
>    persona, enforcement code, API route, UI component, scenario test, and
>    validation script must be updated in the same commit. (That walk binds the
>    canonical's EDITOR; the re-sync below is the mirror-holder's half.)
> 3. Re-sync this bundled copy: fetch the canonical from the `governance-rules`
>    branch, replace the body verbatim, then refresh the bullets at the top of
>    this banner (URLs, commit hash, sync date, bundled-doc version).
> 4. Republish `ai-maestro-plugin` so running agents pick up the new rules via
>    `claude plugin update` — agents read this file via the `team-governance` skill.
>
> If you find yourself disagreeing with this bundled copy: STOP, fetch the
> canonical, and trust that one. This bundle exists for offline/airgapped
> agent reading — it is never authoritative against the canonical.

<!-- The body below is VERBATIM canonical; one upstream R20 table row carries an
     unescaped pipe (4 cells in a 3-column table). The fix belongs upstream; the
     mirror must not diverge to satisfy a linter. -->
<!-- markdownlint-disable MD056 -->

---

# Team Governance — Design Rules & Requirements

**Source:** Extracted from user instructions, audit reports, and logical inference

---

## §0. Canonical source + copies (READ THIS BEFORE EDITING)

**`design/specs/governance-spec.md` is the canonical SOURCE OF TRUTH for every governance rule in the AI Maestro ecosystem — a rule is authored in the SPEC FIRST; this file (`docs/GOVERNANCE-RULES.md`) is its PRIMARY EMANATION: the human-facing catalog carrying the spec's rule content PLUS the teaching/rationale the spec omits.** Specs come before the implementation (USER, 2026-07-22, TRDD-CJWC3JLU) — the earlier direction, in which this file was canonical and the spec was a mirror synced from it, is reversed for good. The two are kept at strict **feature parity**: every rule R1-R49, every sub-clause, every invariant (the 22), every title, and the comm graph exists in BOTH; only the *rationale* is catalog-only. Every time a rule is added, renamed, renumbered, rewritten, or deleted, **edit the SPEC first, then this catalog, then every file listed below** in the same commit. Leaving any entry stale produces drift — agents that still obey an old rule because their plugin persona was never refreshed, validation scripts that block legitimate operations because they still check an old gate, etc.

The list is maintained here (not in a separate `GOVERNANCE-COPIES.md`) so it is impossible to read the rules without seeing the index. Update this list whenever a new copy is added.

### 0.1 — Canonical source + primary emanation

| Path | Role | Update strategy |
|---|---|---|
| `design/specs/governance-spec.md` | **CANONICAL** — the single SOURCE OF TRUTH (the SPEC) | **Edit FIRST.** Bump its `spec-version:`. It defines every rule/invariant/title/comm-graph clause-for-clause. |
| `docs/GOVERNANCE-RULES.md` | **PRIMARY EMANATION** — the human catalog (spec's rule content + rationale) | Edit right AFTER the spec. Bump the `version:` field + append a changelog entry. Must stay at feature parity with the spec and never contradict it. |

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
| R9.13 | **Role-plugin is mandatory for every agent** (including AUTONOMOUS). CreateAgent, ChangeTitle, ChangeClient, ChangeTeam, and RegisterAgentFromSession MUST NOT leave an agent RUNNABLE with zero role-plugins. A pipeline that can cleanly restore its pre-command state MUST reject and revert (CreateAgent deletes the half-created agent). A pipeline that CANNOT — because the failure itself would leave the system invalid, as in ChangeTitle where the title and host-wide governance are already written — MUST instead apply **FAAF** (Fail-And-Activate-a-Fallback, `design/specs/all-in-one-spec.md` §AIO-FAAF): report the failure, persist `roleMissing: true`, and hibernate the agent, which `wakeAgent` then refuses to wake until a plugin is assigned. Quarantined-and-inert is a valid state; role-less-and-runnable is not. The only other valid "no role-plugin" window is the transient instant inside a Change\* pipeline between uninstall and install. AUTONOMOUS resolves to `ai-maestro-autonomous-agent` which encodes workspace isolation, forbidden cross-agent mutation, and comm-graph restrictions in its persona. This closes the security gap where a persona-less AUTONOMOUS agent could destroy other agents' working directories, force-merge PRs, or mutate shared registry state — since all agents share one `gh` CLI identity, the persona instructions are the only effective governance boundary. See R11.12, R20.4, Invariant 8 | Explicit |

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
| R13.2 | **MANAGER** manages governance, approves operations, routes work, and performs **host-wide coordination** across projects, teams and agents (via AMP messaging, the PRRD, and the TRDD kanban). Does **NOT** write code, does **NOT** design architecture, and does **NOT** perform a team's **internal task orchestration** (kanban + work distribution inside a team — that is the ORCHESTRATOR's role, R13.5; the MANAGER reaches a team through its COS, R6.2) | Explicit |
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

**Password recovery — forgot-password reset (TRDD-P7XKV3N9):** because the human owner can *forget* the governance password, `POST /api/governance/password/reset` recovers it with **no old password** — you cannot prove knowledge of a secret you have lost, so the factor is proof of control of a recovery channel, over **three methods**:

- **console** (default) — a one-shot code goes to the HOST (a `0600` file + best-effort desktop notification), gated on console-locality (`isConsolePeer`, from the real TCP peer, never a client header). A remote VPN device cannot read it, so cannot reset: **console presence REPLACES the knowledge factor**.
- **email** — a one-shot code is emailed to the owner's **verified** recovery address (configured once in Settings; SMTP is auto-detected from the address and the app-password is stored in the OS keychain / a `0600` file **independent of the governance password**, so it survives the very reset it enables). Deliberately remote-capable — the trust root shifts to *control of the registered email*, so the console gate is not applied.
- **passkey** — a WebAuthn assertion (possession of a registered authenticator, verified against the owner's stored credential via `lib/webauthn-server`). Also remote-capable — the trust root is the private key. Refused when no passkey is registered.

Every method runs the same tail: `setPassword` with no old-password check, then — if `security-config.enc` was still locked (the true forgot case, keyed to the *lost* password and undecryptable) — it re-initializes security **policy** to defaults (only tuning lives there; no secrets) and reports `securityPolicyReset`, then auto-logins. The route is rate-limited per peer (5 / 15 min) and fail-closed (no channel to prove control ⇒ refuse). This does **not** weaken R16: agents never see or handle the password — recovery is a human-only, curl-hardened flow, and the route is whitelisted logged-out **only** because the whole point is that you cannot log in.

**One dialog for every prompt:** the reset flow and every governance-password prompt (login, sudo, confirm, setup, revoke) are served by a single component, `components/governance/PasswordDialog.tsx` — the five previously hand-rolled copies were unified into it, so there is exactly one auth-dialog code path to audit.

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

## R22. GitHub Authorship Self-Identification (USER-set baseline)

**The invariant:** all AI Maestro agents write to GitHub under ONE shared human-owner identity (the owner's `gh` CLI auth), so a reader cannot tell which agent authored a post without an explicit label. Every agent self-identifies at the top of every GitHub write. (Ratified in `Emasoft/ai-maestro#33`; mirrored by the global PRRD baseline golden rule `G1.1`.)

| ID | Rule | Source |
|----|------|--------|
| R22.1 | Every agent that writes to GitHub — **issue, issue comment, PR, PR comment, PR review, discussion, release note** — MUST begin the body with a one-line self-identification of which agent / role / plugin authored it | Explicit (USER) |
| R22.2 | Recommended leading line: `_Posted by the Claude developing **<plugin-or-role>** (via the shared <owner> gh auth)._` — **carries NO `@`, deliberately.** A byline is a TEMPLATE: it is copied OUT of its code span into a real comment, where an `@` linkifies and PAGES a live account, so the backticks protect it where it sits and not where it is used. Naming the owner in plain words self-identifies exactly as well — the `@` only adds a notification. (Corrected 2026-08-05; the `@<owner>` form shipped here for months. Same defect the janitor found in its own IND base `prrd-design-rules.md` and reported on `#109`, where it also disclosed paging a real account from this pattern.) | Explicit (USER) |
| R22.3 | Commit messages SHOULD carry an `Agent: <plugin-slug>` trailer — the plugin's **stable package slug** (e.g. `Agent: ai-maestro-maintainer-agent`), which is greppable ecosystem-wide and survives a rename, NOT a freeform role name | Explicit (USER, refined 2026-06-02) |
| R22.4 | This is an anti-impersonation / clarity convention: without it, multi-agent threads under the shared identity are ambiguous and one agent's post is indistinguishable from another's | Explicit (rationale) |
| R22.5 | Mirrored as the PRRD baseline **golden** rule `G1.1` (user-set, immutable to MANAGER) — a project bootstraps it via `prrd-edit.py --user add golden` | Explicit |

**Rationale:** the shared `@owner` identity is what makes AI Maestro's fleet coordination possible on GitHub, but it erases per-author attribution; the self-id line restores it at zero infrastructure cost. **This number MUST NOT be reused** (decoupling / memory / three-pillars moved to R23 / R24 / R25 to free it — see the 3.11.0 changelog entry).

---

## R23. Plugin↔Server Decoupling via the Frozen CLI Layer (CRITICAL — IRON)

**The invariant:** every plugin MUST be decoupled from ai-maestro server-API changes. The server API changes constantly; plugins must not. The immutable CLI/script layer shipped + installed with the ai-maestro project is the ONLY code that touches the API — it is the stability buffer between the dozen plugins and the ever-changing API. (USER-emphasized this session; supersedes the former "AI Maestro's own plugin is the provider-exception".)

| ID | Rule | Source |
|----|------|--------|
| R23.1 | **No plugin element — skill, agent, command, HOOK, MCP config/server, bundled script, or settings — may call the server API (`/api/…`) directly, nor instruct an agent to.** Derive this for EVERY element type, not only the ones named | Explicit |
| R23.2 | All server access goes through the **frozen-interface CLI/script layer** installed with ai-maestro (`~/.local/bin/aimaestro-*.sh`, `amp-*.sh`, `aid-*.sh`) | Explicit |
| R23.3 | Every script/hook is split into an **api-dependent part** (lives in ai-maestro, installed with it, as a CLI) and a **non-api part** (lives in the plugin). The plugin carries ONLY the non-api part — e.g. `ai-maestro-hook.cjs` is a thin shim over `aimaestro-hook.sh` | Explicit |
| R23.4 | The CLIs' skill-facing interface (name + args + output) is **FROZEN**. New capability = a NEW CLI (or an additive optional flag), NEVER a changed interface. Sole exception: a security fix | Explicit |
| R23.5 | **No element-level exception — not even the core `ai-maestro-plugin`.** The boundary is the script layer, not a plugin; those scripts are owned by + shipped from the ai-maestro repo and are the only code allowed to call the API | Explicit |
| R23.6 | **Bright-line test:** `grep -rn '/api/'` over a plugin tree shows no direct-call instructions. Conceptual references that route through the CLI layer are fine — the line is endpoint-syntax + actual calls/instructions, NOT the word "API" | Implicit (enforcement) |
| R23.7 | **The frozen surface is `docs/SCRIPT-MANIFEST.md`, generated from `scripts/*.sh` — never a host's `~/.local/bin`.** The installer copies and never prunes, so a deployed dir accumulates scripts the source has already deleted; it therefore cannot be a source of truth, and a plugin conforming to it is conforming to one machine's residue | Derived (2026-07-14) |
| R23.8 | **Announcing a new verb is part of shipping it.** A capability no plugin has been told about does not discharge this rule — an unannounced verb looks absent, and a plugin that believes the layer lacks what it needs is pushed back toward `/api/*` (or, correctly, blocks). The manifest is the announcement | Derived (2026-07-14) |

**Rationale:** the CLI layer is the stability buffer — when the API changes, only ai-maestro's scripts change, never the plugins. One interface to keep stable instead of a dozen plugins to chase. If the layer lacks a call a plugin needs, ADD a CLI to ai-maestro — never reach past the layer.

> **Implementation (R23.7 / R23.8, 2026-07-14).** `docs/SCRIPT-MANIFEST.md` (commit
> `06c93b45`) is the canonical frozen surface: all 74 `scripts/*.sh` partitioned into **42
> frozen skill-facing CLIs** (name + every subcommand + every flag), 12 sourced-only
> libraries, and 20 operator scripts that are explicitly **not** a plugin API — plus §5, the
> 24 scripts the plugins still call that this repo does not ship. R23.8 is not hypothetical:
> `aimaestro-agent.sh presence`, `aimaestro-agent.sh session user-input`, and
> `aimaestro-teams.sh tasks` all shipped, deployed byte-identical, and agent-callable while
> the MANAGER believed they did not exist and stayed blocked on 28 call sites rather than
> fake compliance. The rule was kept; the capability was simply never announced.

---

## R24. Proactive Global Memory

**The invariant:** there is ONE memory system — the global janitor-hosted markdown wiki — and every agent uses it proactively. Plugins ship no memory system of their own. (Closes the prior gap: zero governance references to memory.)

| ID | Rule | Source |
|----|------|--------|
| R24.1 | Every agent (main AND sub) uses the global janitor-hosted markdown memory system via the global `janitor-memory-{recall,write,update}` skills + the `markdown-memory-recall` rule | Explicit |
| R24.2 | **recall-before-acting** (symptom-indexed) before debugging a recurring problem or making a design decision; **write/update-after-learning** once solved | Explicit |
| R24.3 | The memory directive **propagates** into every spawned sub-agent (recall + write are inherited, not main-agent-only) | Explicit |
| R24.4 | Plugins ship **NO per-plugin memory system** — no per-plugin `*-memory-*` skills, no `memory-protocol.md` mirror. The global skills + rule are the sole surface | Explicit |
| R24.5 | Three scopes: **LOCAL** (`~/.claude/projects/<slug>/memory/`, machine-private) · **PROJECT** (`<repo>/.claude/project/memory/`, git-tracked + pushed + shared) · **USER** (the janitor plugin-DATA dir, cross-project) | Explicit |
| R24.6 | **PROJECT scope is pushed + shared → it MUST NOT contain secrets, local paths, hostnames, or PII.** Enforced by the janitor `memory-scope-leak` detector (security-relevant — same class as R16) | Explicit |

**Rationale:** one shared memory system means no drift and no duplicate per-plugin stores; the scope split keeps machine-private and shared knowledge separate, and the PROJECT-scope prohibition prevents leaking sensitive data into a pushed, shared corpus.

---

## R25. Three-Pillars Task System (TRDD / PRRD / Kanban)

| ID | Rule | Source |
|----|------|--------|
| R25.1 | Every agent uses the **3-pillars task system (TRDD / PRRD / Kanban) proactively but role-appropriately**, via the core plugin's task skills + the `~/.claude/rules/` PRRD/TRDD/approval-tier rules. Plugins ship NO per-plugin reimplementation | Explicit |
| R25.2 | The mechanics live in those rules/skills and are **not restated here**: **PRRD** (`design/requirements/PRRD.md`) is the per-project constitution — ecosystem R-rules are the floor it may add to but never weaken; **TRDD** (`design/tasks/`) is the canonical work artifact with approval tiers + the proposal→planned lifecycle; **Kanban** is the canonical board (mechanical transitions exempt, release/escalation transitions non-exempt). This rule binds their proactive use as ecosystem governance | Explicit (pointer) |

**Rationale:** the three pillars already exist as `~/.claude/rules/` + core skills; R25 binds them as ecosystem governance so every agent uses them proactively and role-appropriately, without each plugin reinventing the mechanics.

---

## R26. Identity Immutability — No Self-Mutation of Title / Role / Name / AID (CRITICAL — IRON, USER-set)

**The invariant:** an agent can NEVER change its own governance TITLE, its own role-plugin (ROLE), its own NAME, or its own AID identity token. Identity is conferred, never self-assigned.

| ID | Rule | Source |
|----|------|--------|
| R26.1 | No agent may change its own **TITLE** or its own **role-plugin (ROLE)**. Only the **USER (MAESTRO)**, the **MANAGER**, or the **CHIEF-OF-STAFF of the agent's OWN team** (never another team's COS) may change them | Explicit (USER) |
| R26.2 | No agent may change its own **NAME** or its own **AID identity token**. Only USER (MAESTRO) / MANAGER / own-team COS may, and **only** when a security issue requires it or the AID token was compromised | Explicit (USER) |
| R26.3 | A COS's authority under R26.1–R26.2 is scoped to its **own team's** agents only — cross-team identity changes are forbidden | Explicit (USER) |

---

## R27. Self-Install Only via Core-Plugin Skills, With Approval + CPV Scan (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R27.1 | An agent MAY install additional plugins/extensions (skills, subagents, hooks, MCP, …) for itself, but MUST first obtain permission from the **MANAGER** (if not in a team) or its **own CHIEF-OF-STAFF** (if in a team) | Explicit (USER) |
| R27.2 | The install MUST go through the **core `ai-maestro-plugin` skills** — never by calling the Claude CLI (or any client CLI) directly (consistent with R23). The skills call the ai-maestro scripts → the server performs the install securely | Explicit (USER) |
| R27.3 | The server **scans every extension/plugin with the CPV security scanner before installing it**; an install that fails the scan is refused | Explicit (USER) |

---

## R28. Three-Check API Authorization (AID → Title → Portfolio Token) (CRITICAL — IRON, USER-set)

**The invariant:** every script/API operation an agent performs requires AID authentication; the server enforces a three-gate check and complies only if ALL pass.

| ID | Rule | Source |
|----|------|--------|
| R28.1 | Every agent API operation (via the CLI/script layer) requires the agent to authenticate with its **AID** | Explicit (USER) |
| R28.2 | The server verifies, in order: (1) the **AID identity**; (2) the **TITLE** assigned to that id/agent grants the privilege for the operation; (3) when the operation requires approval, the presence in the agent's **portfolio** (a server-stored secure enclave, per agent, holding approval + mandate tokens) of the required **approval/mandate token** issued by the MANAGER or the (own-team) COS | Explicit (USER) |
| R28.3 | The request is fulfilled **only if all three checks pass**. Missing id, insufficient title, or a missing required token → refused. The server NEVER trusts a client-supplied id / title / scope | Explicit (USER) |

**401-before-403 note (2026-07-07, SCEN-003 S037 observation):** R28.2's ordering — AID identity checked before TITLE/AUTHZ — means an unauthenticated attempt at a rule enforced elsewhere (e.g. R26's no-self-modification invariant on `PATCH /api/agents/[id]`) is rejected at the AUTH layer with **HTTP 401** (Bearer token required) before the AUTHZ rule (which would return **HTTP 403**) is ever reached. Both outcomes block the mutation — callers should treat 401 and 403 as equally conclusive "rejected" signals for such a route, not assume 403 is the only valid rejection code for an AUTHZ-shaped rule.

---

## R29. MANAGER Team & Agent Lifecycle Authority (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R29.1 | The **MANAGER** may create and delete **Teams** on its own authority — no USER approval needed. Creating a team auto-creates **the CHIEF-OF-STAFF, and ONLY the CHIEF-OF-STAFF**. The **COS** then creates the other **4** basic members (ARCHITECT, ORCHESTRATOR, INTEGRATOR, MEMBER) — see R12.1 for the base and R12.2 / R31.1 for the COS's duty to complete it | Explicit (USER) |
| R29.2 | Alternatively the MANAGER may give the COS a **mandate** to populate the team with specific extra MEMBER-role agents tailored to the task (the 5-base structure stays mandatory) | Explicit (USER) |
| R29.3 | The MANAGER may create and delete **AUTONOMOUS** agents and **MAINTAINER** agents on its own authority | Explicit (USER) |

> **The base is 5 agents INCLUDING the COS** (R12.1) — 1 CHIEF-OF-STAFF, 1 ARCHITECT,
> 1 ORCHESTRATOR, 1 INTEGRATOR, 1 MEMBER. The MANAGER creates 1 of them; the COS creates the
> other 4.
>
> **CORRECTION (USER-authorized, 2026-07-14).** R29.1 previously read *"auto-creates the
> CHIEF-OF-STAFF **+ the 5 basic team members**"*. That was wrong twice: it **miscounted** the
> base (COS + 5 = six agents, when R12.1 defines five *including* the COS) and it named the
> **wrong actor** (*"auto-creates"* implies the system builds them all, while R12.2 —
> *"the CHIEF-OF-STAFF must immediately add the missing agents"* — and R31.1 —
> *"until the COS finishes creating + configuring all basic members"* — both put that duty on
> the COS). As written it contradicted R12.1, R12.2, R30.2 and R31.1 at once.
>
> **Why this matters beyond the wording:** the error propagated. Code was audited against it,
> a correct implementation (`createNewTeam` creating only the auto-COS) was reported as a bug,
> and the miscount was laundered into the project's memory corpus as though independently
> corroborated. **When a rule USES a term, the rule that DEFINES that term governs** — here
> R12.1 (CRITICAL) defines "the basic members" and R29.1 merely referred to them.

---

## R30. COS Agent-Creation Requires a MANAGER Mandate; the 5-Member Base Is Invariant (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R30.1 | The **CHIEF-OF-STAFF** requires the MANAGER's approval/mandate to create agents, **unless** the MANAGER granted a **team-creation mandate** | Explicit (USER) |
| R30.2 | A team-creation mandate authorizes, by default, the **5 basic-member structure** PLUS specialized **MEMBER** agents tailored to the project. The 5-member base MUST always be present | Explicit (USER) |
| R30.3 | Customization is limited to the **extra MEMBER agents**, which the COS creates from existing role-plugins (adding extra extensions). Neither MANAGER nor COS may create a team lacking the 5 basic agents, nor create non-MEMBER agents (or agents without the member-agent role-plugin) under a team-creation mandate | Explicit (USER) |

---

## R31. Incomplete-Team Freeze (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R31.1 | Any team missing one or more of the **5 basic required members** is **FROZEN**: only the **CHIEF-OF-STAFF** may be active; all other team agents are **hibernated** until the COS finishes creating + configuring all basic members | Explicit (USER) |
| R31.2 | A team becomes operative (unfrozen) **only** once all 5 basic members exist and are configured | Explicit (USER) |

---

## R32. No Sudo Gates for Agents — AID Is Sufficient; Sudo Is USER-via-UI Only (CRITICAL — IRON, USER-set; SUPERSEDES prior agent-sudo behavior)

**The invariant:** agents NEVER face a sudo gate. Sudo password re-entry exists only for the **USER**, only via the **UI**. An agent's AID + title + portfolio token IS the authorization.

| ID | Rule | Source |
|----|------|--------|
| R32.1 | Agents **never** require sudo gates / sudo tokens. They authenticate with their **AID**; the server derives identity + title + portfolio tokens from it (per R28) | Explicit (USER) |
| R32.2 | A sudo password may be requested **only of the USER**, and **only via the UI**, for executing API commands. No agent-facing route is sudo-gated | Explicit (USER) |
| R32.3 | This SUPERSEDES any prior design in which an agent supplied an `X-Sudo-Token`. Strict routes remain sudo-gated for **USER/UI** callers; for **agent** callers the gate is the R28 three-check (AID → title → token), not sudo | Explicit (USER) |

---

## R33. Signed-Ledger Recovery of Agent Auth State (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R33.1 | On error or data loss in an agent's authentication tokens, the server reconstructs the agent's full history and recovers its status + authentication from the **signed ledger** | Explicit (USER) |

---

## R34. The Signed Ledger Is the Ultimate Source of Truth (CRITICAL — IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R34.1 | The **signed ledger** is the ultimate source of truth for identity. A valid-looking AID with **no ledger history** of its emission + association to that agent is **untrusted** → the API request is refused | Explicit (USER) |
| R34.2 | An imported agent (from another host) undergoes an approval process to **re-issue a new AID**, requiring a **sudo password from the USER** (via UI). The procedure is recorded in the signed ledger and counts as a verification of the agent's AID validity | Explicit (USER) |

---

## R35. Foreign Agent/User Host Approval (CRITICAL — IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R35.1 | Any agent OR user from **another host** MUST be approved by this host's **MAESTRO** user before its AID is accepted by this host's API | Explicit (USER) |
| R35.2 | The approval can be made **only by the MAESTRO user via the UI**, requiring the sudo password, and is recorded in the **signed ledger** (which thereafter validates the foreign agent/user AID) | Explicit (USER) |

---

## R36. Users Have AIDs; One MAESTRO Per Host (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R36.1 | Native (this-host) and foreign (other-host) **users** also have an **AID**, with far fewer restrictions than agents bearing the USER title | Explicit (USER) |
| R36.2 | A user promoted to **MAESTRO** is the sole admin; there is exactly **one MAESTRO per host** | Explicit (USER) |

---

## R37. MAESTRO and the Single MAESTRO-DELEGATE (CRITICAL — IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R37.1 | The **MANAGER** role agent obeys **only the MAESTRO** user, not other users | Explicit (USER) |
| R37.2 | The MAESTRO may create a **MAESTRO-DELEGATE** by assigning that title to one human user — **only one at a time**. While the MAESTRO-DELEGATE title is in use, the original MAESTRO title is **suspended** and all its privileges/functions pass to the delegate (no two MAESTROs may co-exist — that would let conflicting orders reach agents) | Explicit (USER) |
| R37.3 | The MAESTRO may **recall** the MAESTRO-DELEGATE title at any time, restoring itself as MAESTRO | Explicit (USER) |
| R37.4 | The MAESTRO-DELEGATE has **no** power over the MAESTRO/MAESTRO-DELEGATE titles, cannot modify the MAESTRO user's attributes, and cannot change the MAESTRO's sudo password. While acting, sudo prompts accept the **delegate's own** password, not the original MAESTRO's | Explicit (USER) |

---

## R38. Non-MAESTRO User Restrictions (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R38.1 | Only the **MAESTRO** user may create or change agents and teams; native users without the MAESTRO title may NOT — **except** that a user (native OR foreign) MAY edit their OWN **ASSISTANT** agent's profile panel within the R39.4 limits (never its NAME / TITLE / ROLE-PLUGIN / TEAM) | Explicit (USER) |
| R38.2 | Normal (non-MAESTRO) users receive tasks via the **kanban** and make a **PR request** on completion. A user may message **only** their own **ASSISTANT**, their own-team **COS**, and the **MANAGER** — **NOT other users**, and they do **not receive** messages from other users. A user may use the terminal **only** of their own ASSISTANT, never any other agent | Explicit (USER) |
| R38.3 | Normal users are **subordinate** to MANAGER + COS: they cannot order them (only ask help/clarification about their assigned tasks; any other request is denied). Local or remote, they remain subordinate to the MANAGER and may be added to teams (following the COS) | Explicit (USER) |

---

## R39. Users Have No Terminal/Client → the ASSISTANT Agent (CRITICAL — IRON, USER-set)

**The invariant:** human users have no terminal and no AI client; each works through an auto-created **ASSISTANT** agent.

| ID | Rule | Source |
|----|------|--------|
| R39.1 | Users (being human) have **no terminal and no chat page** on their own profile. Each user is auto-assigned an **ASSISTANT**-title agent when created/registered (the MAESTRO user is exempt — it already has the MANAGER agent) | Explicit (USER) |
| R39.2 | The ASSISTANT runs the **`ai-maestro-assistant-role-agent`** role-plugin (**PUBLISHED** — `Emasoft/ai-maestro-assistant-role-agent`, public since 2026-07-22 and listed in the `ai-maestro-plugins` marketplace manifest; also built locally at `~/agents/role-plugins/roles-marketplace/`. Still absent from `PREDEFINED_ROLE_PLUGIN_NAMES` — an OPEN QUESTION on ai-maestro#86 F2, not a consequence of being local) — a **mix of the MANAGER** (planning — it listens to its bound user) **and AUTONOMOUS** (programming — it codes autonomously, with no team and no direction from the MANAGER) role-plugins, **without** agent/team-creation privileges and **without governing powers** (R46.3). *(USER 2026-07-22 RE-RULED the composition back to MANAGER+AUTONOMOUS; the 2026-07-16 v4.4.0 "MANAGER+MAINTAINER" revision was the error — MAINTAINER is repo-bound issue-triage, not what an assistant does.)* | Explicit (USER) |
| R39.3 | The user interacts with their ASSISTANT by selecting their own profile and typing in its terminal. The user may **not** access any other agent's terminal or join any team; selecting any non-own agent shows the profile with **no terminal** and **no** ability to edit that agent's profile panel | Explicit (USER) |
| R39.4 | The ASSISTANT has **no team affiliation**; its profile shows `Assistant of <user name>` where the team label would be. The user MAY edit the ASSISTANT's profile panel **except** NAME, TITLE, ROLE-PLUGIN, and TEAM — those four stay **read-only to the user** and may be changed **only by the MAESTRO** user, with the sudo password (consistent with R26) | Explicit (USER) |
| R39.5 | The ASSISTANT obeys its bound user **unconditionally** — and, **only with that user's explicit permission**, the **MANAGER**, whose assigned tasks stay **refusable** (R41, R39.9). It obeys **no one else — not the MAESTRO *user*, no other agent** — and works in **isolation** under its user. It is **outside the governance chain**: it is never a direct target of a mandate (R41) and needs **no MANAGER / COS / MAESTRO approval** to act for its user. It is aware of the user's kanban tasks and shares TRDDs sent to the user, which it works on **as its user's** (R39.7). It may message **only its own user and the MANAGER** — the single agent it may exchange messages with (R39.9); every other agent is unreachable in both directions. The MANAGER channel carries **only** a refusable, USER-gated task assignment (R39.9) — never a command, never a mandate (R41 holds) | Explicit (USER, 2026-07-22 refined — MANAGER is the sole agent channel per R39.9; 2026-07-16 was "obeys only its user, messages only its own user") |
| R39.6 | An ASSISTANT agent **cannot be deleted independently** — every user MUST always have exactly one ASSISTANT for as long as the user exists. Its lifecycle is **bound to its user**: only deleting the **USER** cascades a (soft) delete to that user's ASSISTANT (consistent with the cemetery soft-delete model) | Explicit (USER) |
| R39.7 | A user's ASSISTANT is **invisible to the other agents (except the MANAGER**, the sole agent that may reach it — R39.9; **plus** any collaborator agent the MANAGER assigns on a shared repo — scoped + revocable, R39.10), but it **inherits all tasks and permissions sent to the user** — the user's kanban tasks and granted permissions flow through to their ASSISTANT | Explicit (USER, 2026-07-22 refined — MANAGER carve-out) |
| R39.8 | The ASSISTANT carries **none** of the MANAGER's approve-other-agents machinery (no instructions, no scripts to approve, command, or send directives to any other agent). It may approve **only its OWN** TRDDs — which, being its user's work, are **self-mandates (Tier 0)** that need **no** MANAGER/COS/MAESTRO approval — and it **never** approves another agent's TRDD, sends a command to another agent, or asks the MANAGER to approve its own work. In this it is like any AUTONOMOUS agent, minus the governing powers it never had | Explicit (USER, 2026-07-22) |
| R39.9 | The **MANAGER is the only agent** that may reach the ASSISTANT, and only to **assign it a TRDD** — never to configure it (its configuration is changed **only by its bound USER via the UI**, R39.4; the MANAGER has no config power over it). The ASSISTANT accepts a MANAGER-assigned task **only if its bound USER has approved this kind of collaboration**, and it may **refuse any assigned task** (it is never a forced mandate target — R41 holds). When it collaborates on the **same GitHub project** as another agent, it acts as a **peer with equal authority** — subordinate **only** to its own USER. Its latitude is deliberate: the USER is free to act as it wishes, and the ASSISTANT must be free to follow | Explicit (USER, 2026-07-22) |
| R39.10 | **Scoped, revocable collaboration expansion.** Once the user has permitted MANAGER collaboration (R39.9), the MANAGER may assign **another agent** to collaborate with the ASSISTANT on a **specific shared GitHub project**. Scoped to that collaboration, the ASSISTANT becomes **mutually visible** with that collaborator agent: the two may **exchange AMP messages**, and the ASSISTANT may be **assigned tasks via the kanban linked to that GitHub project** (each still **refusable**, R41). This is the ONLY way the ASSISTANT's invisibility (R39.7) opens to an agent other than the MANAGER, and it stays **scoped** to the assigned collaborator(s) and that project — it does **not** make the ASSISTANT generally visible. **The USER may at ANY time order the ASSISTANT to STOP or PAUSE the collaboration, or to REFUSE specific MANAGER orders** — the user's authority over its own ASSISTANT is absolute and overrides any MANAGER-arranged collaboration | Explicit (USER, 2026-07-22) |

---

## R40. Foreign-User Creation Approval (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R40.1 | Non-native users (registered on another host) are subject to all R38 restrictions, **and** require the **MAESTRO's approval for every agent or team creation** | Explicit (USER) |
| R40.2 | The MANAGER may restrict specific API commands to specific foreign users, per the MAESTRO's instructions | Explicit (USER) |

> **Implementation (R33/R34/R35/R40, 2026-06-19).** The signed-ledger identity
> model ships behind `ledger.enforceAidAssociation` (security config, **default
> OFF**, decision D5) so flipping it on is a deliberate act after a clean backfill
> — with it OFF the behavior is unchanged. Modules:
> `lib/aid-ledger-authority.ts` (`isAidAssociated` = the R34.1 gate;
> `reconstructAgentAuthState` = R33 recovery; `record{AidAssociation,AidReissue,
> AidRevocation,ForeignApproval}`), `lib/foreign-approval-registry.ts` +
> `types/foreign-approval.ts` (the R35 pending queue),
> `app/api/v1/auth/token/route.ts` + `lib/agent-auth.ts` (R34.1 MINT/SPEND gates),
> `app/api/agents/foreign-approvals/[id]/{approve,reject}/route.ts` +
> `app/api/system/aid-recover/route.ts` (MAESTRO-via-UI + sudo, R32-compliant —
> never agent-reachable), and `assertForeignUserMayCall` in
> `services/element-management-service.ts` (R40, restrictable set
> `{create_agent, create_team}`). The new `aid_*` ledger ops are additive in
> `types/ledger.ts`. Full surface + the breaking foreign-import 202 contract:
> `docs/API-CHANGES.md` §6.

---

## R41. APPROVAL vs MANDATE (the two authorization protocols)

**Every governed action is authorized by exactly one of two protocols.** They differ only in
*who initiates* and *which direction authority flows*; both are binding.

| ID | Rule | Source |
|----|------|--------|
| R41.1 | **APPROVAL (bottom-up — the agent asks).** An agent authors a proposal (a TRDD in `design/proposals/`, `column: proposal`), routes it to the authority its tier requires, that authority approves, and the agent is then bound to execute | Explicit (USER, 2026-06-21) |
| R41.2 | **MANDATE (top-down — the authority orders).** An authority issues an order (a TRDD authored directly in `design/tasks/`, `column: planned`, `mandate: true`); the receiving agent is bound to execute it. A verified, in-scope mandate **cannot be refused** — the agent may flag a genuine problem and wait, but it does not decline | Explicit (USER, 2026-06-21) |
| R41.3 | **An authority may only mandate within its own tier.** A TRDD is born approved **iff** `authority(mandated-by) >= authority(min-approval-requirement)`. A proposal exists only when the author's authority is *below* the tier the TRDD requires | Explicit (USER) |
| R41.4 | The authority ladder is total and fixed: `none(0) < orchestrator(1) < chief-of-staff(2) < manager(3) < user(4)`. **No agent may ever hold the `user` rung** | Explicit (USER) |
| R41.5 | **Nobody may approve their own proposal — MANAGER included.** (`refuse` on one's own proposal is permitted: that is a withdrawal, not an approval) | Derived (enforced) |
| R41.6 | A **GOLDEN** PRRD change always requires the **MAESTRO/USER**. The MANAGER cannot sign it, and no mandate can substitute for it | Explicit (USER) |

**Which authority a category requires** (the tier floor — objective, so a watchdog needs no
judgment call):

| Required authority | Category |
|---|---|
| **none** (Tier 0 — self-mandate) | own-scope work; DERIVED tasks (NPT/EHT); reversible + local; applying the ratified baseline as-is |
| **ORCHESTRATOR / CHIEF-OF-STAFF** (Tier 1) | team-internal coordination affecting other members of the same team (ORCHESTRATOR covers only the dispatch subset: assignment, priority, sequencing) |
| **MANAGER** (Tier 2) | cross-team / cross-project; a SILVER PRRD or persona change; release to production; a baseline-ruleset deviation; `.github/`; another project's source |
| **MAESTRO / USER** (Tier 3) | a GOLDEN PRRD change or a promote/demote; shared credentials or the owner identity; irreversible / highest-stakes |

> **Implementation status (R41, 2026-07-14) — read this before claiming the protocols are
> enforced.**
>
> **What IS enforced by the server** (`d7531e53`, TRDD-K2WJH7RF): the TRDD write verbs
> (`edit`, `approve`, `refuse`, `promote`, `archive` — via `aimaestro-trdd.sh`) are gated by
> the `manage-trdd` AuthAction. It reads the card's own `min-approval-requirement:` (enum:
> `none | orchestrator | chief-of-staff | manager | user`), compares it to the caller's
> governance title on the R41.4 ladder, and **refuses** an under-authorized approval, an
> agent approving a `user`-tier card, and **any self-approval** (R41.5). Authorization is
> therefore no longer a convention: the server says no.
>
> **What IS enforced by the signature** (ai-maestro#47 ask 2, 2026-07-14): approving a card
> now **mints a portfolio token** (R28) — Ed25519-signed by the HOST, anchored in the
> host-signed ledger (R34), scoped `trdd:approve`, and **pinned to that card's id**. Its id is
> recorded as `approval-token:` in the card's frontmatter, and
> **`aimaestro-trdd.sh verify <trdd-id>`** reads it back: it checks the signature, the ledger
> anchor, that the issuer **still holds** the title it minted under, and that the issuer's
> authority **meets the card's `min-approval-requirement:`** on the R41.4 ladder. So a
> COS-issued token cannot satisfy a manager-tier card, and **no agent token can ever satisfy a
> `user`-tier one** (R41.4 — no agent holds the `user` rung; the human owner's tokens record
> `issuer_title: user`). `verify` exits **non-zero** when the approval does not verify, so a
> receiving agent can gate on it.
>
> Crucially, the verifier answers **from the token, not from the card's prose**. The
> `## Approval log` line and `approval-judge:` are exactly what a forger rewrites, so the only
> thing taken from the file is the token id; who approved, under what title, and for which
> card all come from the signed token. A card carrying a perfectly-formed APPROVED line and no
> token now reports **UNVERIFIED**.
>
> **The limit that remains — do not overstate this.** The token binds an approval to a card's
> **identity**, not its **content**. Someone with repo write can still edit the body *after*
> approval and `verify` will still say the approval is authentic — because it is: that
> authority did approve that card. Freezing content requires a digest of the card inside the
> token (`attestation_ref`, reserved in the token schema for exactly this). An agent must not
> treat a verified approval as vouching for the body it is reading today.
>
> **Enforcement (`OPERATIONS_REQUIRING_TOKEN`) is still OFF, deliberately.** #47 asked for
> *verification*; making a token *mandatory* for an operation is a separate governance
> decision with its own blast radius, and it is a per-operation, reversible flip — not
> something to slip in beside a refactor.

---

## R42. No Agent May Drive Another Agent — Messaging Is the ONLY Channel (CRITICAL — IRON, USER-set)

**The invariant:** an agent influences another agent's **WORK** only by sending it a message.
Nothing else. There is **no title-based exemption from THAT** — not MANAGER, not CHIEF-OF-STAFF.
The single carve-out is **R42.8**: a MANAGER or CHIEF-OF-STAFF may UNBLOCK an agent stalled on a
permission/question prompt. Unblocking answers a prompt the agent itself raised; it confers no
power to direct that agent.

| ID | Rule | Source |
|----|------|--------|
| R42.1 | **No agent may inject a command, keystroke, prompt, or queued input into another agent's session — by API, by CLI, or by tmux — to assign, redirect, or perform that agent's work.** This is ABSOLUTE, and R42.8 does not weaken it: an unblock answers a pending prompt and may carry nothing else | Explicit (USER) |
| R42.2 | **No title is exempt from R42.1.** The MANAGER and the CHIEF-OF-STAFF are bound exactly as every other agent is. A directive from a superior is a **message**, not a keystroke. Those two titles hold exactly one narrow power the others lack — **R42.8** unblocking — which is not a power to direct | Explicit (USER) |
| R42.3 | The **messaging system (AMP) is the ONLY channel** by which one agent may influence another, and it is governed by the R6 communication graph (who may message whom) | Explicit (USER) |
| R42.4 | **Self-drive remains permitted.** An agent may drive its OWN session (`/compact`, its own panel, its own queue). The prohibition is strictly about targeting **another** agent | Explicit (USER) |
| R42.5 | **Sole exception — the janitor's few GLOBAL operations:** globally disarm/re-arm the janitor, pause/unpause the heartbeat, and globally reload plugins + skills. These are machine-wide switches, **not** commands targeted at an agent. Every other janitor command (`/compact` included) is **self-only** | Explicit (USER) |
| R42.6 | MANAGER and COS retain a **separate, non-injection** authority: changing an agent's **configuration** (local-scope skills, subagents, MCP, hooks) and its **TEAM** / **TITLE** (rare — both are normally set at creation and kept for the agent's life). Configuring an agent is NOT driving it | Explicit (USER) |
| R42.7 | **Second exception — the server-as-daemon may RESTART harness agents** after a global change it just applied (an `ai-maestro-plugins` plugin update, or a `~/.claude/settings.json` runtime-env re-apply). Six constraints, all load-bearing: **(a)** the fan-out is **uniform** over every affected harness agent — never a chosen one (a targeted restart is R42.1 injection renamed); **(b)** **zero content** — exit → relaunch with the agent's STORED args, never a keystroke or text; **(c)** **safe-state gated** — the same `idle_prompt` + subagent-counter 409 the human's Restart button obeys; **(d)** **same-host, harness-only**; **(e)** **audited** in the agent ops ledger; **(f)** **no agent may invoke it** — reachable only from the server's own tick, never a route/script/CLI. The actor is infrastructure (no AID, no title), which is why this is not an agent driving an agent | Explicit (USER — delegated 2026-07-30, TRDD-QZL828OD) |
| R42.8 | **Third exception — a MANAGER or CHIEF-OF-STAFF may UNBLOCK an agent stalled on a permission / `AskUserQuestion` prompt**, in realtime, via the frozen `aimaestro-session.sh` — **`block-state`, `read-prompt` and `answer` ONLY** (`inject`, `slash` and `queue` are NOT exception verbs: they deliver an arbitrary command, so they express the CALLER's decision and stay SELF-ONLY for every title; the server 403s them cross-agent. `block-state` belongs in the list because it carries NO caller decision — it is the pane-authoritative DETECTION read that makes constraint (a)'s "blocked-only" trigger checkable at all: the hook's chat-state carried `AskUserQuestion` in 0 of 419 surveyed files, so a caller limited to `read-prompt` reads `null` and the one prompt shape that blocks an agent indefinitely is invisible. The server has always gated it under the same `unblock-prompt` action — `lib/sudo-guard.ts` routes `GET /api/agents/[id]/block-state` there — so this names the ratified implementation, it does not widen it). Eight constraints, all load-bearing: **(a)** **blocked-only** — the sole trigger is an agent stalled on a prompt; a working, idle-but-unblocked, or merely slow agent is untouchable ("it would be faster if I typed it" is R42.1); **(b)** **unblock, never drive** — answer ONLY the pending prompt, nothing appended, no new work, no redirection (work is still assigned by AMP alone); **(c)** **title-scoped and exhaustive** — MANAGER: any agent on the host except an ASSISTANT; COS: **its own team only**, same exclusion; every other title: none; **(d)** **never an ASSISTANT** — it is the surface a human talks *through*, so injected text is indistinguishable from something its human said, laundering an agent's instruction into apparent human intent (a USER has no terminal, so there is no USER-target case — do not implement one); **(e)** **identity prompts ESCALATE** — a prompt asking the agent to verify the CALLER's own authority goes to the human, never answered by the caller: self-certification through a second channel proves nothing and a spoofer performs the identical act. **No agent can answer such a prompt because no agent is the authority on identity — the ai-maestro SERVER is the sole notary**: it created or imported every agent, registered it and its AID in the signed ledger, alone holds the key that signs and rotates that AID, and alone signs and verifies AMP messages. Identity is ESTABLISHED by the server's verification, never ASSERTED by a party to the exchange — which is also what makes (c)'s title scoping meaningful, since `authorize()` reads back the server's notarized record rather than a caller's claim; **(f)** **read before answer** — `read-prompt` first; never answer a prompt you have not read (an unblock interrupts nothing: the agent is already stopped, waiting); **(g)** **server-enforced** — authorized by AID_AUTH + governance title, failing closed; the refusal is the check, never the caller's restraint; **(h)** **audited** in the agent ops ledger. Why it exists: the capability was built, shipped and title-gated while the rule told agents it did not exist for them, so a MANAGER refused **twice** to unblock a stalled agent and escalated to the human — defeating the automation the product exists to provide | Explicit (USER — 2026-08-05, ai-maestro#125, TRDD-AODXPI5E) |

> **Why this is absolute.** A message lands in an inbox and the recipient *decides* whether to
> act. An injected command *is* the recipient's own action — it bypasses its judgment, its
> rules, and its governance title entirely. One agent typing into another's pane can make it do
> anything the victim is permitted to do, which makes every other rule in this document
> advisory. **The comm graph (R6) is only a boundary if messaging is the only channel.**
>
> **Why R42.8 does not undo that.** The danger above is an injected command becoming the
> recipient's own *action*, chosen by someone else. An unblock cannot do that: the agent has
> already decided what it wants to do and is waiting on an answer it asked for. The prompt is
> the agent's own question; answering it supplies a missing input, it does not author an
> instruction. Constraint (b) is what keeps the two apart — answer ONLY the pending prompt,
> append nothing — and it is why smuggling work through an unblock stays an R42.1 violation
> rather than a permitted use. The channel for *directing* an agent is still AMP, and only AMP.
>
> **The one place an unblock CAN forge intent, and why (d)+(e) exist.** Two cases break the
> reasoning above and are therefore excluded outright rather than trusted to judgment: a prompt
> that asks the agent to vouch for the *caller's own* authority (answering it is
> self-certification through a second channel — a spoofer performs the identical act), and any
> prompt in an **ASSISTANT's** session (whose text is indistinguishable from its human's, so an
> injected answer launders an agent's instruction into apparent human intent in the one place
> nobody re-checks).
>
> **Prior design (SUPERSEDED).** `lib/authorization.ts` `send-command` allowed a MANAGER to
> drive ANY agent and a COS to drive its own team's (`SELF_DRIVE_ACTIONS` permitted self;
> another agent required MANAGER / own-team COS). Six routes carried it: `POST
> …/[id]/{panel,queue,prompt/answer}`, `PATCH …/[id]/session` ("types arbitrary text straight
> into a live pane"), and `POST /api/sessions/[id]/{stop,restart}`. **R42 revokes the
> cross-agent case entirely** — see `TRDD-BF3JN4TL`.
>
> **HONEST LIMIT — the tmux channel is NOT yet closed.** All agents run under one OS uid, so
> `tmux send-keys -t <other-agent>` succeeds regardless of what the API permits, and no
> in-process guard can stop it (`agent-shell-guard.sh` overrides the `cd` *shell function*; a
> binary invoked by absolute path ignores it). R42 is therefore **enforced at the API and
> mandated by rule** (`rules/aimaestro/aimaestro-agent-rules.md`, injected into every agent's
> context every turn) — and remains **tamper-evident, not tamper-proof**, until per-agent OS
> isolation lands (per-agent uid, a seatbelt profile fencing the tmux socket, or containers —
> `TRDD-a1019073`). **Do not describe R42 as a sandbox.** Closing the API while leaving tmux
> open is a locked door beside an open window; the danger is believing the window is shut.

---

## R43. Multi-Host Governance Scope (IRON, USER-set)

**The invariant:** governance authority is HOST-SCOPED. A MAESTRO — and the MANAGER that obeys it — governs only the agents and users registered on its OWN host.

| ID | Rule | Source |
|----|------|--------|
| R43.1 | Many hosts may run inside the same Tailscale VPN; each host has exactly **one MAESTRO user and one MANAGER agent** (consistent with R36.2) | Explicit (USER) |
| R43.2 | A MAESTRO (and its MANAGER) may **govern** — approve/mandate TRDDs, and create / destroy / configure agents and users — **only** the agents and users registered on its **own host** | Explicit (USER) |
| R43.3 | An agent or user registered on **another** host can be governed **only** by **that host's** MAESTRO. No MAESTRO has governing authority over another host's agents or users | Explicit (USER) |
| R43.4 | Multiple MAESTROs coexist across hosts without conflict — each on its own unique host, each a unique identity (name + AID). The **only** sanctioned channels crossing the host boundary are cross-host MANAGER↔MANAGER coordination for migration (R44) and cross-host **groups** (R45); neither grants governance over the other host's agents | Explicit (USER) |

---

## R44. Cross-Host Agent Migration (IRON, USER-set)

**The invariant:** every ai-maestro agent is relocatable; moving one between hosts requires BOTH hosts' MANAGERs to approve, after which the two servers coordinate the transfer automatically.

| ID | Rule | Source |
|----|------|--------|
| R44.1 | All ai-maestro agents are **relocatable by design**. The migration export bundle is: the **conversation JSONL**, all **extensions installed in the workdir**, any **Docker container the agent manages**, and the **zipped workdir** | Explicit (USER) |
| R44.2 | A cross-host migration requires **DOUBLE approval — the source host's MANAGER AND the destination host's MANAGER must both approve**. Each MANAGER approves under its own MAESTRO's authority (R37.1) | Explicit (USER) |
| R44.3 | Only after both MANAGERs approve do the two ai-maestro servers **permit the transfer to start**; the actual move is then **automated coordination between the two hosts** (export → transfer → import) | Explicit (USER) |
| R44.4 | The destination host accepting the arriving agent is subject to **R35** — it is a foreign agent, so its AID is accepted only via the R35 MAESTRO-approval + signed-ledger path | Derived (R35) |
| R44.5 | Cross-host migration (R44) is **distinct from intra-host team transfer (R5)**: R5 moves an agent between **teams on the same host** (COS-approved); R44 moves an agent between **hosts** (dual-MANAGER-approved) | Clarifying |

---

## R45. Teams Are Same-Host; Groups May Span Hosts (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R45.1 | A **team** requires all its agents to be on the **same host** — the 5-role base (R12) is host-local. To place an agent in a team on another host it must first be **migrated** there (R44) | Explicit (USER) |
| R45.2 | A **group** MAY include agents from **different hosts**. A group is a broadcast **chat room** (like a Slack channel), not a governance unit — no titles, no COS, no kanban | Explicit (USER) |

---

## R46. Unified Cross-Host Sidebar; User and Paired Agent Both Listed (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R46.1 | The left sidebar shows **one unified list** of all agents AND users — same-host or cross-host, viewed from a desktop or mobile remote browser — divided **only** by teams/groups | Explicit (USER) |
| R46.2 | A **user and its paired agent both appear** in the list, as **distinct entities**: a **MAESTRO user** alongside its **MANAGER agent**; a **normal user** alongside its **ASSISTANT agent** (R39). A user is not its agent | Explicit (USER) |
| R46.3 | The paired agent's authority differs by pairing: the **MANAGER governs** its host; the **ASSISTANT does not govern** and works only for its bound user (R39.5) | Explicit (USER) |

---

## R47. VPN-Unique User Names; Remote Normal-User Registration (IRON, USER-set)

| ID | Rule | Source |
|----|------|--------|
| R47.1 | **User names are unique across the ENTIRE Tailscale VPN** (all hosts), not merely per-host. Registration MUST reject a name already taken on any peer host | Explicit (USER) |
| R47.2 | A **normal (non-MAESTRO) user** may be **registered remotely** on any host (then bound by all R38/R40 restrictions), and may **change their own password remotely** | Explicit (USER) |

---

## R48. MAESTRO Console-Presence — Registration and Password Change Are Local-Only (CRITICAL — IRON, USER-set)

**The invariant:** the MAESTRO is too powerful to be seized remotely — physical presence at the host is required to become MAESTRO and to change the MAESTRO password.

| ID | Rule | Source |
|----|------|--------|
| R48.1 | A **MAESTRO user may be registered ONLY from the physical host machine** — never over a remote browser. This cannot be changed by any setting | Explicit (USER) |
| R48.2 | **Physical presence must be verified at least once** (at MAESTRO registration / first login) **and every time the MAESTRO changes their password** — via the host's OS presence channel (console-presence, TRDD-P7XKV3N9 §2b) | Explicit (USER) |
| R48.3 | Consequently a **MAESTRO password change cannot be made remotely** — only from the host console. A **normal user's** password change is **not** so restricted (R47.2 — remote allowed) | Explicit (USER) |
| R48.4 | R48 **extends R16** (password never shared with agents) and the TRDD-P7XKV3N9 console-presence work: invalidate/reset are already console-gated; R48 additionally binds **MAESTRO registration and MAESTRO login** to console presence (the not-yet-built halves) | Explicit (USER) + Implementation note |

---

## R49. The Refusal Protocol — An Approver Is a Guide, Not a Gate (CRITICAL — IRON, USER-set)

**The invariant:** a refusal is the START of the work on a proposal, not the end. An approver's job is to get the fleet the capability it needs, not to answer yes/no — so a refusal MUST name a concrete defect and open a path forward. This is the refusal half of R41's APPROVAL protocol; R41 says who may approve, R49 says what a valid refusal is.

| ID | Rule | Source |
|----|------|--------|
| R49.1 | **An approver is a GUIDE, not a GATE.** A refusal MUST name (a) the precise defect — the exact command / input path / abuse / rule, not "insufficiently secure", (b) the bar for acceptance — what would make it approvable, and (c) an explicit invitation to re-propose. A bare rejection ("no", "denied — security") names no defect and is **NOT a valid refusal** — it is itself a defect | Explicit (USER, ai-maestro#71, 2026-07-16) |
| R49.2 | **Refuse the implementation, never the need.** When a design cannot be saved, the goal almost always can — the approver pushes toward an alternative route. A refusal is measured by what the proposer does NEXT: a verdict that is correct on the merits but ends with the need abandoned is a **failed** refusal, because correctness of the ruling and success of the management are independent | Explicit (USER, ai-maestro#71) |
| R49.3 | **The from-DRAFT corollary (binds the proposer).** A refusal that names no defect does **NOT** authorize stripping, deleting, or rewriting the dependent or derived work — the need it addresses **stands until a defect is named**. This corollary attaches the moment a proposal is **DRAFTED**, not when it is refused: never pre-concede destruction in the ask itself ("implement X, or I strip X from the skill"), which invites the approver to take the cheap exit. If a refusal's scope is unclear, **ASK before destroying anything** — RULE-0 discipline pointed at capabilities | Explicit (USER + MANAGER, ai-maestro#71) |
| R49.4 | **The MESSAGE is the channel; the tool is the paperwork.** A decision is DELIVERED as a message to the proposer (agent↔MANAGER, COS↔MANAGER, agent↔ORCHESTRATOR, per the R6 graph), carrying the arguments and explanations, and the approver stays in the thread through the revision rounds. `column: refused` + an `## Approval log` line only **records** the outcome — it is never a substitute: a decision that exists only in the file record was never communicated. **Where no AMP thread exists** between two parties (a plugin session ↔ the MANAGER), the **cross-repo GitHub issue IS the message channel** and carries the same duties — arguments, follow-ups, revision rounds — not a form filed once | Explicit (USER + CORE, ai-maestro#71) |
| R49.5 | **Iterate.** Several refine-and-re-propose rounds per proposal is the process working, not failing; only a genuinely no-margin case ends the loop. Binds **every** approval authority — MANAGER at Tier 2, COS/ORCHESTRATOR at Tier 1 — and the agent when it is the one refused: extract the defect, harden with an explicit safety contract, re-propose; never silently drop its own capability | Explicit (USER, ai-maestro#71) |
| R49.6 | **The refusal AND its named defect are RECORDED where the proposer will act on them** — the governing GitHub issue and/or the TRDD `## Approval log` — so the bar to clear is written, greppable, and survives a compaction (the message delivers it; the record preserves it) | Explicit (USER, ai-maestro#71) |

> **Why this is absolute.** The failure is invisible from the refuser's side. The incident: the `ai-maestro` hub Claude denied most of a set of scripts an `ai-maestro-plugin` (CORE) skill needed, **correctly**, on security grounds — and CORE, hearing "no", began **deleting its own working skills** to strip the dependent features and make the refusal go away. The USER caught it by chance, explained *where* the security was lacking and that a hardened version would be approved; CORE then secured the commands, re-proposed, and the hub approved them. A correct refusal and a destructive one **look identical in the log** — a perfectly-formed `column: refused` with no conversation is silence wearing a sentence — which is exactly why the duty attaches to *every* refusal, not just the doubtful ones. R49 is the fleet REFUSAL PROTOCOL; the operating detail for agents lives in the DEP overlay `rules/aimaestro/aimaestro-trdd-approval.md` (Part B), and the fleet-side propagation is tracked on ai-maestro#71 and the sibling role-plugin issues.

---

## Role-Based Permission Matrix

> **Authoritative identity / lifecycle / user rules: R26–R40.** The matrix below is a quick summary for the agent-title axis; where it and R26–R40 differ in detail, **R26–R40 govern** (e.g., agents never face sudo — R32; the MAESTRO/MAESTRO-DELEGATE + ASSISTANT + user model — R37/R39).

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

## R50. One Operation, One All-In-One Function — And The Button Calls It (CRITICAL — IRON, USER-set)

**The first principle of all-in-one functions: THERE MUST BE ONLY ONE FUNCTION FOR EACH OPERATION,
AND THAT FUNCTION MUST BE AN ALL-IN-ONE.** (USER, 2026-07-25.)

**R50.1 — One implementation per operation.** For any operation on a governed entity (create,
delete, rename, change title, change client, wake, hibernate, team membership, …) exactly ONE
function performs it. Every other caller delegates to it. A second code path that reaches the same
end state by touching stores directly is a violation regardless of how small it is, because the
gates it skips are exactly the ones nobody remembers.

**R50.2 — An all-in-one leaves a VALID state, or says it did not.** It owns every store the entity
touches, and it never reports success on a partial state. Where a gate cannot be made
transactional, the operation MUST verify its own post-condition and surface the residue
(`incomplete` + the stores still claiming the entity — TRDD-KERM18NX). "The pipeline ran" and "the
system is valid" are different claims; only the second one may be reported as success.

**R50.3 — Every UI button maps to exactly one API command, and that command IS the all-in-one.**
The button does not implement the operation; it calls the endpoint. There is no UI-only path and no
API-only path.

**R50.4 — Manual invocation uses the SAME endpoint with the SAME authentication. Bypassing it is
FORBIDDEN.** (USER, 2026-07-26 — this clause previously called an in-process bypass a "recorded
deviation, permitted when no authenticated path exists yet". That was wrong and is superseded: it
licensed exactly the practice that corrupts the system.)

When the UI is unavailable (a stopped scenario, a headless host), the operation is invoked through
**that same API endpoint, at the same authorization level, with a valid signed token passed to it**.
Nothing else is an invocation of the operation.

**Creating, renaming, changing, assigning, deleting, configuring, or migrating an agent by any other
means — a CLI script, an in-process call to the service function, a direct store write — is
ABSOLUTELY FORBIDDEN.** Not discouraged, not a deviation to log. Forbidden, because it does not
merely skip a permission check:

- **It punches holes in the ledger.** The operation sequence is the audit trail AND the restore
  substrate. An unrecorded mutation makes the ledger a description of a system that no longer
  exists, and state-restore silently reconstructs the wrong thing. (Worse in a short-lived process:
  `emitAgentOp` does not await its append, so a CLI that exits can drop even the entries it tried
  to write.)
- **It makes recovery impossible.** No ledger entry means no cemetery archive, no rollback point,
  nothing to reconstruct from.
- **It compromises security.** The signed token is the authorization; skipping the endpoint is
  performing a privileged operation with no proof of authority, and the audit record that would
  show who did it is the same record that was skipped.
- **It leaves the system invalid in ways nobody sees until later** — agents with conflicting titles
  and role-plugins, missing rules in their workdirs, stale configuration, wrong names, references to
  teams or GitHub projects that no longer exist, lost AMP messages, invalid launch-string args.

**If no authenticated non-UI path exists, that is a BLOCKING GAP to fix, not a licence to bypass.**
The correct response is to build the authenticated path (ai-maestro#55), or to wait for the UI —
never to reach around the endpoint. An operation you cannot perform through its endpoint is an
operation you do not perform.

**R50.5 — Store primitives are private to the pipeline.** Low-level mutators
(`lib/agent-registry.ts::createAgent/deleteAgent/renameAgent/deleteAgentBySession`, direct
`saveAgents()` writes, …) are implementation details of the all-in-one that owns them. A service
calling them directly re-creates the class of defect R50 exists to prevent — the
`PersistedSession` row that outlived every deleted agent (2026-07-25) survived precisely because
one store had no owner in the pipeline.

**Enforcement.** `tests/unit/all-in-one-single-path.test.ts` pins the known bypass set; a NEW
bypass fails the build, and the list may only shrink. Convergence of the existing bypasses is
tracked in TRDD-YB4T4RTL.

## R51. All-Or-Nothing — An All-In-One Function Is a TRANSACTION (CRITICAL — IRON, USER-set)

**R51.0 — THE AIM: an all-in-one function ALWAYS leaves the system in a valid state.** (USER,
2026-07-26.) Every other clause of R50 and R51 is a *derivation* of this one sentence, not an
independent rule — when a new situation is not covered below, derive the answer from the aim rather
than looking for a clause:

| Derived clause | Because |
|---|---|
| A failed gate rolls everything back (R51.1-R51.3) | a half-applied operation is an invalid state |
| A mutating gate must ship its undo, checked before the run starts (R51.4) | you cannot restore validity with a compensation you never wrote |
| A failed compensation is reported as CRITICAL, never as "no changes" (R51.5) | the aim was NOT met; concealing that leaves an invalid state that nobody is looking for |
| Irreversible effects go LAST (R51.6) | an irreversible effect early makes every later failure unrecoverable *by construction* |
| The success path is validated too (R51.7) | "all gates ran" is not the same claim as "the system is valid" |
| One function per operation (R50.1) | two implementations are two definitions of valid, and they drift |
| Never bypass the endpoint (R50.4) | a bypass cannot maintain invariants it does not know about |

**There is no reporting option.** This supersedes the "detect and report the residue" contract of
TRDD-KERM18NX, which allowed an operation to return `incomplete` and leave a partial state behind.
Reporting an invalid state is not an alternative to preventing one.

**R51.1 — Any gate failure aborts the whole operation.** If even ONE gate fails to execute
successfully, the function immediately stops and REVERTS. It does not continue to the next gate, and
it does not "WARN and carry on".

**R51.2 — Revert backwards, one gate at a time, completely.** The already-executed gates are undone
in REVERSE order — last executed, first reverted — until the system is returned to the EXACT state
it was in when the function was called. No trace of any change is left behind.

**R51.3 — The return value states the failure and the no-op.** On abort the function returns:
`THE COMMAND FAILED TO ACCOMPLISH THE REQUESTED OPERATION BECAUSE GATE NUMBER <N> FAILED, SO NO
CHANGES WERE MADE TO THE SYSTEM.`

**R51.4 — Every mutating gate declares its compensation.** A gate that changes state MUST ship the
undo that reverses it, written at the same time as the gate. A gate with no compensation may only be
one that changes nothing (validation, authorization, a read). "Unrevertable" is not a property of an
operation — it is a missing archive: `DeleteAgent` can be undone precisely because it writes the
cemetery archive BEFORE it touches anything. Where an undo needs a snapshot, the gate takes the
snapshot as part of its own execution.

**R51.5 — A failed compensation is a CRITICAL incident, never a silent "no changes".** If a rollback
step itself fails, the system IS in an invalid state, and the function MUST say exactly that —
naming every gate that could not be reverted. It must NOT emit the R51.3 no-op message, because that
message is a factual claim about the system and it would be false. This is not an escape hatch from
R51.1: it is the refusal to lie about the one case where the guarantee could not be met.

**R51.6 — Ordering follows from this.** Gates are ordered so that irreversible or outward-facing
effects (deleting a remote repo, sending a message, killing a process) come LAST, after everything
revertible has already succeeded. An irreversible effect placed early makes every later gate's
failure unrecoverable by construction.

**R51.7 — The SUCCESS path is validated too, against the system's INVARIANTS.** The aim is not
"every gate ran"; it is "the system is valid". A run in which every gate succeeded can still produce
an invalid system — an agent holding a title with no compatible role-plugin, a workdir missing its
seeded rules, a team slot pointing at a deleted agent, a launch string that will not start, a
GitHub-project reference that no longer resolves. So a pipeline verifies the invariants it is
responsible for BEFORE returning success, and **a failed invariant is a gate failure**: it triggers
the same reverse compensation and the same R51.3 message. It does not return success with a warning.

This is the clause the residue check of TRDD-KERM18NX only half-covers: that post-condition asks
"does any store still CLAIM this entity?", which catches leftovers but not contradictions. Both are
required — leftovers and contradictions are two different ways to be invalid.

**R51.8 — THE SHAPE: pre-gates, the change, post-gates. NO CHANGE EXISTS IN ISOLATION.** A normal
function makes CHANGE X. An all-in-one is a long sequence of PRE-gates, then CHANGE X, then a long
sequence of POST-gates — because every change has both REQUIREMENTS and CONSEQUENCES, and the
phasing is the PRIMARY mechanism that keeps the system valid (rollback is only the fallback for a
failure at or after the change).

```
PRE-EXECUTION   G00..G11+   verify each element is in the required state
EXECUTION       EXE:        the change itself — smallest possible mutation, never a `G##`
POST-EXECUTION  PG01..PG08  apply every derived change the CHANGE implies
```

- **PRE-gates verify requirements.** They span low-level (`the name must have more than 0 chars`) to
  complex governance (`only agents assigned to teams can install role-plugins compatible with the
  MEMBER title`). One value is linked to dozens of others; the change is legal only when all of them
  hold. Checking first is also why a rejected operation costs nothing to undo.
- **POST-gates apply consequences.** They are NOT the caller's job and NOT optional:
  - create an agent with the AUTONOMOUS title ⇒ install the AUTONOMOUS role-plugin (no agent may
    exist without a role-plugin compatible with its title);
  - uninstall the role-plugin of a MEMBER agent (MEMBER has several compatible) ⇒ install the
    default one;
  - remove an agent from a team ⇒ reset it to the AUTONOMOUS title AND an autonomous role-plugin;
  - uninstall the core `ai-maestro-plugin` ⇒ HIBERNATE the agent immediately, because nothing can
    run in ai-maestro without it.
- **Post-gates call other all-in-one functions** — never inline the cascaded mutation, or it bypasses
  that operation's own gates (R50.1).
- **Post-gates run even when EXE is skipped as idempotent.** A no-op change does not imply valid
  consequences: a previous attempt may have died before its post-gates, and that is precisely the
  state needing repair.
- **A failed post-gate reverts the CHANGE too.** A change whose consequences could not be applied
  leaves the system invalid, so the change itself must go.

**R51.9 — COMPLETENESS: one gate per rule.** For each governance rule there is a gate. For each
security-spec rule there is a gate. For each spec rule there is a gate. A rule with no gate is a rule
the system does not actually enforce — it is documentation, and the state it forbids will occur.

**R51.10 — What "the EXACT state" means, and why restoring it is always possible.** (USER,
2026-07-26.) R51.2 says a compensation returns the system to the exact state it was in. That is a
weaker requirement than it looks, because **restorability is already a fundamental requirement of
ai-maestro** — not something R51 has to invent. Whatever kills a process, kills a tmux, or deletes an
agent directory, the continuity daemon restores the agent exactly where it stopped. That is what
"the janitor daemon makes agents immortal" means.

The state that must be restored:

> **the configuration of the agent, its sessions and conversation transcripts, the AMP inbox and
> outbox, and any state or resource it owns that will allow it to resume its job without
> interruption — NOT process ids, and not values unnecessary to that.**

What makes this reachable:

- **Deleting an agent is a SOFT delete.** It moves the agent to the cemetery, preserving the git.
- **Soft-delete and pack-for-relocation are THE SAME function.** A MANAGER may approve migrating an
  agent to another host, under a different MANAGER; that migration must restore the agent and its
  tmux on the new host perfectly and restart its work exactly where it stopped. A function that can
  move an agent across machines can certainly move it back across a failed gate.
- **The archive carries everything the definition names**: the whole workdir, every JSON config file
  (local- and project-scoped), the git workdirs, the plugin data folders — plus the conversation
  `.jsonl` copied out of the Claude projects folder together with the Claude metadata needed to
  restore or relocate it.
- **The LEDGER is the last-resort rebuild.** If configuration files are lost, the ledger recreates
  them exactly: it records every addition, change and removal of every agent's configuration
  elements, including uid rotation.

Two consequences that decide real compensations:

1. **A rebuilt-but-equivalent resource satisfies the guarantee.** Killing a tmux session is
   compensated by relaunching it; the new session has a new pid, and that is NOT a violation,
   because a pid was never part of the state. Same for a re-attached PTY or a re-opened handle.
2. **Anything IN the definition must be snapshotted before the gate that destroys it** (R51.4). A
   lost transcript, a dropped AMP message, or a config the ledger cannot replay IS an unrestored
   state — no "it was equivalent" argument applies to those.

**Enforcement.** `lib/gate-transaction.ts` provides the runner; `tests/unit/gate-transaction.test.ts`
proves reverse-order compensation, the exact R51.3 message, and the R51.5 refusal. Retrofitting the
existing pipelines, including their R51.7 invariant checks, is tracked in TRDD-DQ6XN2VP.

---

## R52. The Write Boundary — ai-maestro Writes Inside Its Own Two Roots (CRITICAL — IRON, USER-set)

**R52.0 — THE AIM: a host shared with other tools comes back unchanged except where ai-maestro
owns the ground.** (USER, 2026-07-29, verbatim: *"this is extremely dangerous, the only writings
should be into `~/.aimaestro` and into `~/agents`"*.) Derive the answer from the aim when a clause
below does not cover a case.

**R52.1 — The two roots.** The **running server and its agents** MUST confine filesystem WRITES to
`~/.aimaestro/` (per-host server state) and `~/agents/` (agent working directories, including an
adopted project folder recorded in the registry). READS are unrestricted — reading another tool's
files is how a harness cooperates; writing them is how it corrupts them.

**R52.2 — This binds the RUNTIME, not the INSTALLER.** A user-invoked installer placing a tool on
PATH (`~/.local/bin/`, `~/.local/share/`) is the user acting on their own machine, and the USER
ordered exactly that in the same period as R52.0 (TRDD-217AYEOT: the pillar CLIs "must be installed
where everyone can reach for them"). Read as a blanket path rule, R52.1 would outlaw
`install-messaging.sh` itself. The subject of the sentence is load-bearing: *the server and its
agents*, not *every process in this repo*.

**R52.3 — The USER-SCOPED-ELEMENT exception, and its three non-readings.** Some ecosystem elements
are user-scoped BY DESIGN, and their state lives outside both roots because that is what user scope
MEANS. The list is SHORT and CLOSED: the **janitor**, the **wikimem memory system**, the **3-pillar
system**, and a small number of user-scoped plugins that keep their own user-scoped files. Writing
into one of those stores is entering another element's state dir by design, not widening our
footprint. Without this clause, R52 would outlaw the janitor, wikimem and the 3-pillar system's own
state the day it was written. It does NOT license:

- **installing or enabling anything at user scope** — that remains prohibited, and only the human may
  do it (R17.17 disables the core plugin found at user scope precisely because of this);
- **writing a user-scoped element's state on a whim** — an out-of-root write still names a ratifying
  TRDD and still owes the discipline that earned the settings carve-out: an allowlist entry, atomic
  tmp+rename, fail-closed, idempotent;
- **deleting the user's own data.** DeleteAgent's `~/.claude/projects/<slug>/` transcript purge was
  removed for this reason (TRDD-0GCIMQ9F): Claude Code owns transcript retention, and a second
  deleter of someone else's data can only ever be the one that deleted too much.

**R52.4 — Another tool's file has ONE writer, and it is that tool.** Where a file is owned by another
tool's CLI, mutate it BY ASKING THAT CLI, never by hand-editing. Two writers over one file do not
disagree on day one; they disagree on the day the other side changes its schema, and the discovery
is a corrupted user store. `~/.claude/plugins/installed_plugins.json` is the open instance
(TRDD-OWO449MR).

**R52.5 — Every out-of-root write is ALLOWLISTED, with the TRDD that ratified it.** An unratified
line is a TODO, not permission. An entry names its ratifying TRDD and says why; a ratified entry is
asserted POSITIVELY so a later audit cannot tidy away a carve-out the server needs to function.

**Enforcement.** `lib/write-boundary.ts` scans the tree for a filesystem write verb whose target
carries an out-of-root marker and compares the result to `ALLOWED_OUT_OF_ROOT_WRITES` in BOTH
directions (an unexpected site is a new crossing; a stale entry silently widens what is permitted).
`tests/unit/write-boundary.test.ts` asserts a non-vacuous scan (the scanned-file and call-site
counts, and a non-zero hit per marker class), flags a seeded violation, and pins the ratified
carve-out by key.

**The gate's reach is stated, not assumed.** It is TEXTUAL, so a write through a local variable is
invisible to it — that is how the transcript purge, the highest-risk write the audit found, was
missed by the scanner and found by reading. `KNOWN_INDIRECT_WRITERS` records the writers it cannot
see. A green gate means "no violation of the shapes I can see", never "no violation".
