---
name: team-governance
user-invocable: false
description: "Use when managing teams or governance titles. Trigger with /team-governance. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-governance.sh:*), Bash(aimaestro-teams.sh:*), Bash(aimaestro-agent.sh:*), Bash(jq:*), Bash(amp-send:*), Bash(amp-inbox:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.1.0"
---

<!-- Decoupled per MANAGER core#11 (TRDD-90c8ad35): every example below calls the frozen `aimaestro-governance.sh` / `aimaestro-teams.sh` / `aimaestro-agent.sh` CLIs (which resolve the API base + agent identity internally), never the server `/api/*` directly. AMP (`amp-send`/`amp-inbox`) already uses the CLI. The one residual — assigning a COS to an EXISTING team — has no frozen verb yet and is marked DECOUPLE-BLOCKED inline (set the COS at create time via `--cos`). -->

## Overview

Manage teams, assign agents, assign Chief-of-Staff titles, and handle broadcasts via the frozen `aimaestro-governance.sh` / `aimaestro-teams.sh` CLIs. All teams are closed (isolated messaging with COS gateway). For lightweight agent collections, use Groups. Requires MANAGER or CHIEF-OF-STAFF title.

**Communication graph (R6 v3, 2026-05-04):** AMP follows a title-based directed graph; HUMAN is a first-class node. v3 made **COS the SOLE gateway** for in-team agents — MANAGER no longer reaches ORCH/ARCH/INT/MEM directly. Blocked routes return HTTP 403 `title_communication_forbidden`. See R6 + matrix in the [reference](references/REFERENCE.md#team-messaging-rules) and the bundled rules.

**Minimum team composition (R12, CRITICAL):** every team has ≥5 agents — 1 COS + 1 ARCHITECT + 1 ORCHESTRATOR + 1 INTEGRATOR + 1 MEMBER. MANAGER enforces R12.6 on team creation.

**Authorization model (R26–R40, security-first):** agents authenticate **only** by their **AID** — the `aimaestro-*` CLIs send it automatically. The server runs the **R28 three-check** (AID → derived TITLE → portfolio approval/mandate token) and never trusts a client-supplied id/title/scope; a skill **never asserts its own title**. Per **R32**, agents **never** face a sudo gate — AID + title + token IS the authorization; a governance/sudo **password is requested only of the USER, only via the UI** (R16), so a `--password` flag on a deployed CLI is a **USER/UI residual you surface to the user, never supply yourself**. Per **R29–R31**, the **MANAGER** creates/deletes teams (auto-creating the COS + the 5 base members) with **no user approval** (R9.11); a **COS** needs a MANAGER mandate to add extra MEMBER agents (the 5-member base is invariant); a team missing any base member is **frozen** (only its COS active) until complete. Identity is **conferred, never self-assigned** (R26). Full text in the [bundled rules](references/GOVERNANCE-RULES.md) R26–R40.

## Prerequisites

- AI Maestro running (the `aimaestro-*` CLIs resolve the API base + auth internally)
- The `aimaestro-governance.sh` / `aimaestro-teams.sh` / `aimaestro-agent.sh` CLIs on PATH; `jq` installed
- AMP scripts (`amp-send`, `amp-inbox`) for broadcasts
- Agent must have MANAGER or COS title

## Instructions

1. **Verify role** before any operation:

   ```bash
   aimaestro-governance.sh whoami | jq .
   ```

   If not MANAGER or COS, STOP and inform the user.

2. **Operations** (each CLI resolves the API base + your agent identity internally):
   - **List teams**: `aimaestro-teams.sh list`
   - **Show team**: `aimaestro-teams.sh show <team-id>`
   - **Create team**: `aimaestro-teams.sh create --name <name> --type closed [--cos <agent-id>]` (closed requires MANAGER)
   - **Update team**: `aimaestro-teams.sh update <team-id> [--name|--description|--agents|--orchestrator]`
   - **Delete team**: `aimaestro-teams.sh delete <team-id>` (MANAGER only — authenticates by AID per R29/R32; do **not** supply a password. The deployed CLI's `--password` flag is a USER/UI residual, not for agents.)
   - **Add / remove agent**: `aimaestro-teams.sh add-agent|remove-agent <team-id> <agent>`

3. **Create a closed team** (the CLI sends your agent identity — no manual header):

   ```bash
   aimaestro-teams.sh create --name my-team --type closed | jq .
   ```

4. **COS assignment (R29/R32)** — the MANAGER assigns the COS; this needs **no user approval and no agent password** (the MANAGER authenticates by AID — R9.11). Per R29 the MANAGER creating a team auto-creates its COS + 5 base members:
   - **At create time** (supported): `aimaestro-teams.sh create --name my-team --type closed --cos <cos-agent-id>` — assigns the COS title + auto-installs `ai-maestro-chief-of-staff`.
   <!-- DECOUPLE-BLOCKED ai-maestro#36: assigning a COS to an ALREADY-EXISTING team (was `POST /api/teams/{id}/chief-of-staff`) has no frozen-CLI verb yet — `aimaestro-teams.sh update` exposes no `--cos`. Pending a follow-up verb. Until then: set the COS at create time via `--cos` above, or have the MANAGER assign it through their own tooling. Do NOT call `/api/*` directly (core#11). The deployed CLI's `--password` flag is a USER/UI residual (R32.3), never supplied by agents. -->

5. **Broadcasts** — message all team agents via AMP:

   ```bash
   # Resolve the team + each agent's name through the frozen CLIs, then AMP.
   AGENTS=$(aimaestro-teams.sh show <team-id> | jq -r '.agentIds[]')
   for AID in $AGENTS; do
     NAME=$(aimaestro-agent.sh show "$AID" | jq -r '.agent.name')
     amp-send "$NAME" "Subject" "Message"
   done
   ```

6. **Respect messaging isolation** for closed teams. See reference for full rules.

## Output

- JSON response with team data, agent lists, or error details
- Broadcast confirmation per agent messaged

## Error Handling

| HTTP | Meaning |
|------|---------|
| 403 | Not MANAGER/COS, or closed team isolation blocks messaging |
| 400 | Bad input (invalid type, agent in another closed team) |
| 401 | Sudo/governance password rejected — a **USER/UI** path (R32.2); agents authenticate by AID and should never hit this |
| 404 | Team not found |

## Examples

`/team-governance create a closed team` — see REFERENCE.md for full flows.

## Checklist

Copy this checklist and track your progress:

- [ ] Verified governance role via `aimaestro-governance.sh whoami`
- [ ] Confirmed MANAGER or COS title
- [ ] Authenticated by AID only — supplied NO password (R32; the server runs the R28 three-check)
- [ ] Executed the frozen-CLI command (`aimaestro-teams.sh` / `aimaestro-governance.sh`)
- [ ] Verified response; sent broadcasts if applicable

## Resources

- [Detailed Reference](references/REFERENCE.md)
  - Governance API Endpoints
  - Team Management
  - Agent Assignment
  - Chief-of-Staff Assignment
  - Team Broadcast Messaging
  - Permission Matrix
  - Team Messaging Rules
  - Error Codes
  - Troubleshooting
- [Canonical Governance Rules (bundled mirror)](references/GOVERNANCE-RULES.md)
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
  - R22. GitHub Authorship Self-Identification (RESERVED — see issue #33)
  - R23. Plugin↔Server Decoupling via the Frozen CLI Layer (CRITICAL — IRON)
  - R24. Proactive Global Memory
  - R25. Three-Pillars Task System (TRDD / PRRD / Kanban)
  - R26. Identity Immutability — No Self-Mutation of Title / Role / Name / AID (CRITICAL — IRON)
  - R27. Self-Install Only via Core-Plugin Skills, With Approval + CPV Scan (IRON)
  - R28. Three-Check API Authorization (AID → Title → Portfolio Token) (CRITICAL — IRON)
  - R29. MANAGER Team & Agent Lifecycle Authority (IRON)
  - R30. COS Agent-Creation Requires a MANAGER Mandate; the 5-Member Base Is Invariant (IRON)
  - R31. Incomplete-Team Freeze (IRON)
  - R32. No Sudo Gates for Agents — AID Is Sufficient; Sudo Is USER-via-UI Only (CRITICAL — IRON)
  - R33. Signed-Ledger Recovery of Agent Auth State (IRON)
  - R34. The Signed Ledger Is the Ultimate Source of Truth (CRITICAL — IRON)
  - R35. Foreign Agent/User Host Approval (CRITICAL — IRON)
  - R36. Users Have AIDs; One MAESTRO Per Host (IRON)
  - R37. MAESTRO and the Single MAESTRO-DELEGATE (CRITICAL — IRON)
  - R38. Non-MAESTRO User Restrictions (IRON)
  - R39. Users Have No Terminal/Client → the ASSISTANT Agent (CRITICAL — IRON)
  - R40. Foreign-User Creation Approval (IRON)
  - Role-Based Permission Matrix
