---
name: team-governance
user-invocable: false
description: "Use when managing teams or governance titles. Trigger with /team-governance. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(curl:*), Bash(jq:*), Bash(amp-send:*), Bash(amp-inbox:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Manage teams, assign agents, assign Chief-of-Staff titles, and handle broadcasts via the AI Maestro governance API. All teams are closed (isolated messaging with COS gateway). For lightweight agent collections, use Groups. Requires MANAGER or CHIEF-OF-STAFF title.

**Communication graph (R6 v3, 2026-05-04):** AMP follows a title-based directed graph; HUMAN is a first-class node. v3 made **COS the SOLE gateway** for in-team agents — MANAGER no longer reaches ORCH/ARCH/INT/MEM directly. Blocked routes return HTTP 403 `title_communication_forbidden`. See R6 + matrix in the [reference](references/REFERENCE.md#team-messaging-rules) and the bundled rules.

**Minimum team composition (R12, CRITICAL):** every team has ≥5 agents — 1 COS + 1 ARCHITECT + 1 ORCHESTRATOR + 1 INTEGRATOR + 1 MEMBER. MANAGER enforces R12.6 on team creation.

## Prerequisites

- AI Maestro at `${AIMAESTRO_API:-http://localhost:23000}`
- `curl(1)` and `jq` installed
- AMP scripts (`amp-send`, `amp-inbox`) for broadcasts
- Agent must have MANAGER or COS title

## Instructions

1. **Verify role** before any operation:

   ```bash
   curl -s "http://localhost:23000/api/governance" | jq .
   ```

   If not MANAGER or COS, STOP and inform the user.

2. **API operations**:
   - **List teams**: `GET /api/teams`
   - **Create team**: `POST /api/teams` (closed requires MANAGER + `X-Agent-Id` header)
   - **Update team**: `PUT /api/teams/{id}`
   - **Delete team**: `DELETE /api/teams/{id}` (MANAGER only)
   - **Assign COS**: `POST /api/teams/{id}/chief-of-staff` (MANAGER + governance password)

3. **Auth header** for protected operations:

   ```bash
   curl -s -X POST "http://localhost:23000/api/teams" \
     -H "Content-Type: application/json" \
     -H "X-Agent-Id: <your-agent-id>" \
     -d '{"name":"my-team","type":"closed"}' | jq .
   ```

4. **COS assignment** — ask user for governance password (never cache it):

   ```bash
   curl -s -X POST "http://localhost:23000/api/teams/<id>/chief-of-staff" \
     -H "Content-Type: application/json" -H "X-Agent-Id: <id>" \
     -d '{"agentId":"<cos-id>","password":"<pw>"}' | jq .
   ```

5. **Broadcasts** — message all team agents via AMP:

   ```bash
   # Fetch to a temp file, then parse — keeps each API response inspectable.
   TEAM_FILE="$(mktemp)"
   curl -s "http://localhost:23000/api/teams/<id>" -o "$TEAM_FILE"
   AGENTS=$(jq -r '.agentIds[]' "$TEAM_FILE")
   for AID in $AGENTS; do
     AGENT_FILE="$(mktemp)"
     curl -s "http://localhost:23000/api/agents/$AID" -o "$AGENT_FILE"
     NAME=$(jq -r '.agent.name' "$AGENT_FILE")
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

- [ ] Verified governance role via `/api/governance`
- [ ] Confirmed MANAGER or COS title
- [ ] Obtained governance password from user (if COS assignment)
- [ ] Executed API call with correct headers
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
