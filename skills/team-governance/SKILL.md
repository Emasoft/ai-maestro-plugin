---
name: team-governance
description: "Manage team governance: create/delete teams, assign agents, set COS roles. Use when managing teams or roles. Trigger with /team-governance."
allowed-tools: "Bash(curl:*), Bash(jq:*), Bash(amp-send:*), Bash(amp-inbox:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Manage teams, assign agents, set team types (open/closed), assign Chief-of-Staff roles, and handle team broadcasts using the AI Maestro governance API. Only agents with MANAGER or CHIEF-OF-STAFF title can perform governance operations.

## Prerequisites

- AI Maestro running at `${AIMAESTRO_API:-http://localhost:23000}`
- `curl` and `jq` installed
- AMP scripts installed (`amp-send`, `amp-inbox`) for team broadcasts
- Agent must have MANAGER or COS title (verify first)

## Instructions

1. **Verify your governance role** before any operation:
   ```bash
   curl -s "http://localhost:23000/api/governance" | jq .
   ```
   If not MANAGER or COS, STOP and inform the user.

2. **Choose the operation** from the governance API:
   - **List teams**: `GET /api/teams`
   - **Create team**: `POST /api/teams` (closed requires MANAGER + `X-Agent-Id` header)
   - **Update team**: `PUT /api/teams/{id}` (change type, assign/remove agents)
   - **Delete team**: `DELETE /api/teams/{id}` (MANAGER only)
   - **Assign COS**: `POST /api/teams/{id}/chief-of-staff` (MANAGER + governance password)

3. **For authenticated operations**, include the `X-Agent-Id` header:
   ```bash
   curl -s -X POST "http://localhost:23000/api/teams" \
     -H "Content-Type: application/json" \
     -H "X-Agent-Id: <your-agent-id>" \
     -d '{"name": "my-team", "type": "closed"}' | jq .
   ```

4. **For COS assignment**, ask the user for the governance password (never store/cache it):
   ```bash
   curl -s -X POST "http://localhost:23000/api/teams/<team-id>/chief-of-staff" \
     -H "Content-Type: application/json" \
     -H "X-Agent-Id: <your-agent-id>" \
     -d '{"agentId": "<cos-id>", "password": "<password>"}' | jq .
   ```

5. **For team broadcasts**, use AMP to message all team agents:
   ```bash
   AGENTS=$(curl -s "http://localhost:23000/api/teams/<id>" | jq -r '.agentIds[]')
   for AID in $AGENTS; do
     NAME=$(curl -s "http://localhost:23000/api/agents/$AID" | jq -r '.name')
     amp-send "$NAME" "Subject" "Message"
   done
   ```

6. **Respect messaging isolation** for closed teams. See reference for the full messaging rules and permission matrix.

## Output

- JSON response from each API call with team data, agent lists, or error details
- Broadcast confirmation per agent messaged

## Error Handling

| HTTP Status | Meaning |
|-------------|---------|
| 403 | No permission (not MANAGER/COS, or messaging blocked by closed team isolation) |
| 400 | Invalid input (bad team type, agent already in another closed team) |
| 401 | Invalid governance password |
| 404 | Team not found |

On `agent_already_in_closed_team`, use MANAGER cross-team transfer instead of direct assignment.

## Examples

```
/team-governance create a closed team called "security-core"
```
Expected: Team created with type "closed", returns team ID and metadata.

```
/team-governance assign agent backend-dev to security-core
```
Expected: Agent added to team's agentIds array, confirmed via API response.

```
/team-governance broadcast "Deploy at 3pm" to security-core
```
Expected: AMP message sent to each team member individually.

## Checklist

Copy this checklist and track your progress:
- [ ] Verified governance role via `/api/governance`
- [ ] Confirmed MANAGER or COS title for target team
- [ ] Obtained governance password from user (if COS assignment)
- [ ] Executed governance API call with correct headers
- [ ] Verified API response for success
- [ ] Sent broadcast messages (if applicable)

## Resources

- [Detailed Reference](references/REFERENCE.md) - Full governance API/CLI reference
  - Governance API endpoints table
  - Team management (create, update, delete)
  - Agent assignment and cross-team transfer
  - Chief-of-Staff assignment/removal
  - Team broadcast messaging patterns
  - Full permission matrix (13 actions x 4 roles)
  - Messaging isolation rules for closed teams
  - Error codes and troubleshooting
