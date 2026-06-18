---
name: team-governance
user-invocable: false
description: "Use when managing teams or governance titles. Trigger with /team-governance. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-governance.sh:*), Bash(aimaestro-teams.sh:*), Bash(aimaestro-agent.sh:*), Bash(jq:*), Bash(amp-send:*), Bash(amp-inbox:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

<!-- Decoupled per MANAGER core#11 (TRDD-90c8ad35): every example below calls the frozen `aimaestro-governance.sh` / `aimaestro-teams.sh` / `aimaestro-agent.sh` CLIs (which resolve the API base + agent identity internally), never the server `/api/*` directly. AMP (`amp-send`/`amp-inbox`) already uses the CLI. The one residual — assigning a COS to an EXISTING team — has no frozen verb yet and is marked DECOUPLE-BLOCKED inline (set the COS at create time via `--cos`). -->

## Overview

Manage teams, assign agents, assign Chief-of-Staff titles, and handle broadcasts via the frozen `aimaestro-governance.sh` / `aimaestro-teams.sh` CLIs. All teams are closed (isolated messaging with COS gateway). For lightweight agent collections, use Groups. Requires MANAGER or CHIEF-OF-STAFF title.

**Communication graph (R6 v3, 2026-05-04):** AMP follows a title-based directed graph; HUMAN is a first-class node. v3 made **COS the SOLE gateway** for in-team agents — MANAGER no longer reaches ORCH/ARCH/INT/MEM directly. Blocked routes return HTTP 403 `title_communication_forbidden`. See R6 + matrix in the [reference](references/REFERENCE.md#team-messaging-rules) and the bundled rules.

**Minimum team composition (R12, CRITICAL):** every team has ≥5 agents — 1 COS + 1 ARCHITECT + 1 ORCHESTRATOR + 1 INTEGRATOR + 1 MEMBER. MANAGER enforces R12.6 on team creation.

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
   - **Delete team**: `aimaestro-teams.sh delete <team-id> --password <pw>` (MANAGER only)
   - **Add / remove agent**: `aimaestro-teams.sh add-agent|remove-agent <team-id> <agent>`

3. **Create a closed team** (the CLI sends your agent identity — no manual header):

   ```bash
   aimaestro-teams.sh create --name my-team --type closed | jq .
   ```

4. **COS assignment** — ask the user for the governance password (never cache it):
   - **At create time** (supported): `aimaestro-teams.sh create --name my-team --type closed --cos <cos-agent-id> --password <pw>`
   <!-- DECOUPLE-BLOCKED ai-maestro#36: assigning a COS to an ALREADY-EXISTING team (was `POST /api/teams/{id}/chief-of-staff`) has no frozen-CLI verb yet — `aimaestro-teams.sh update` exposes no `--cos`. Pending a follow-up verb (same gov-password residual class flagged on ai-maestro#36). Until then: set the COS at create time via `--cos` above, or have the MANAGER assign it through their own tooling. Do NOT call `/api/*` directly (core#11). -->

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
| 401 | Invalid governance password |
| 404 | Team not found |

## Examples

`/team-governance create a closed team` — see REFERENCE.md for full flows.

## Checklist

Copy this checklist and track your progress:

- [ ] Verified governance role via `aimaestro-governance.sh whoami`
- [ ] Confirmed MANAGER or COS title
- [ ] Obtained governance password from user (if COS assignment)
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
  - Role-Based Permission Matrix
