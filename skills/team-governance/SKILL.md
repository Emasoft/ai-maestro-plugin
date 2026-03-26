---
name: team-governance
description: "Manage team governance: create/delete teams, assign agents, set COS roles. Use when managing teams or roles. Trigger with /team-governance."
allowed-tools: "Bash(curl:*), Bash(jq:*), Bash(amp-send:*), Bash(amp-inbox:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Manage teams, assign agents, set team types (open/closed), assign Chief-of-Staff roles, and handle broadcasts via the AI Maestro governance API. Requires MANAGER or CHIEF-OF-STAFF title.

## Prerequisites

- AI Maestro at `${AIMAESTRO_API:-http://localhost:23000}`
- `curl` and `jq` installed
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
   AGENTS=$(curl -s "http://localhost:23000/api/teams/<id>" | jq -r '.agentIds[]')
   for AID in $AGENTS; do
     NAME=$(curl -s "http://localhost:23000/api/agents/$AID" | jq -r '.name')
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

On `agent_already_in_closed_team`, use MANAGER cross-team transfer.

## Examples

```
/team-governance create a closed team called "security-core"
```
Creates team with type "closed", returns team ID.

```
/team-governance assign agent backend-dev to security-core
```
Adds agent to team's agentIds array.

## Checklist

Copy this checklist and track your progress:

- [ ] Verified governance role via `/api/governance`
- [ ] Confirmed MANAGER or COS title
- [ ] Obtained governance password from user (if COS assignment)
- [ ] Executed API call with correct headers
- [ ] Verified response; sent broadcasts if applicable

## Resources

- [Detailed Reference](references/REFERENCE.md) - Governance API endpoints, Team management, Agent assignment, COS assignment/removal, Broadcast patterns, Permission matrix, Messaging isolation, Error codes
