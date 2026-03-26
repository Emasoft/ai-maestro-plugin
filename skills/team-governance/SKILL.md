---
name: team-governance
description: Manage team governance - create/delete teams, assign agents, set team type (open/closed), assign Chief-of-Staff roles. ONLY for agents with MANAGER or CHIEF-OF-STAFF role.
allowed-tools: Bash
metadata:
  author: 23blocks
  version: "1.0"
---

# Team Governance

Manage teams, assign agents, set team types, and assign Chief-of-Staff roles using the AI Maestro governance API.

---

## Role Check (Run First)

**Before using any governance commands, ALWAYS verify your role:**

```bash
curl -s "http://localhost:23000/api/governance" | jq .
```

This returns your agent's governance permissions, including which teams you manage or serve as Chief-of-Staff.

**If you are not a MANAGER or CHIEF-OF-STAFF of any team, STOP.** Inform the user that governance operations require elevated privileges. Only agents with MANAGER or CHIEF-OF-STAFF roles can use this skill.

---

## Team Management

| Operation | Method | Endpoint | Auth Required |
|-----------|--------|----------|---------------|
| List all teams | GET | `/api/teams` | None |
| Create open team | POST | `/api/teams` | None |
| Create closed team | POST | `/api/teams` | MANAGER (X-Agent-Id) |
| Delete closed team | DELETE | `/api/teams/{id}` | MANAGER (X-Agent-Id) |
| Change type open->closed | PUT | `/api/teams/{id}` | MANAGER (X-Agent-Id) |
| Change type closed->open | PUT | `/api/teams/{id}` | MANAGER (X-Agent-Id) |

### List All Teams

```bash
curl -s "http://localhost:23000/api/teams" | jq .
```

### Create an Open Team

Any agent can create an open team. Open teams allow any agent to join or leave freely.

```bash
curl -s -X POST "http://localhost:23000/api/teams" \
  -H "Content-Type: application/json" \
  -d '{"name": "frontend-squad", "type": "open"}' | jq .
```

### Create a Closed Team (MANAGER Only)

Closed teams require explicit assignment. Only a MANAGER can create them.

```bash
curl -s -X POST "http://localhost:23000/api/teams" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"name": "security-team", "type": "closed"}' | jq .
```

### Delete a Closed Team (MANAGER Only)

```bash
curl -s -X DELETE "http://localhost:23000/api/teams/<team-id>" \
  -H "X-Agent-Id: <your-agent-id>" | jq .
```

### Change Team Type: Open to Closed (MANAGER Only)

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"type": "closed"}' | jq .
```

### Change Team Type: Closed to Open (MANAGER Only)

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"type": "open"}' | jq .
```

---

## Agent Assignment

| Operation | Method | Endpoint | Auth Required |
|-----------|--------|----------|---------------|
| Assign agent to closed team | PUT | `/api/teams/{id}` | MANAGER or COS of that team (X-Agent-Id) |
| Remove agent from closed team | PUT | `/api/teams/{id}` | MANAGER or COS of that team (X-Agent-Id) |
| Transfer agent cross-team | PUT | `/api/teams/{id}` | MANAGER only (X-Agent-Id) |

### Assign an Agent to a Closed Team

Update the team's `agentIds` array to include the new agent. Only MANAGER or the Chief-of-Staff of that specific team can perform this operation.

```bash
# First, get current team members
CURRENT=$(curl -s "http://localhost:23000/api/teams/<team-id>" | jq -r '.agentIds | join(",")')

# Add new agent to the list
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentIds": ["existing-agent-1", "existing-agent-2", "new-agent-id"]}' | jq .
```

### Remove an Agent from a Closed Team

Update the team's `agentIds` array with the agent removed.

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentIds": ["remaining-agent-1", "remaining-agent-2"]}' | jq .
```

### Transfer an Agent Cross-Team (MANAGER Only)

Assign the agent to the new team. The old membership is automatically removed.

```bash
# Assign agent to the new team (removes from old team automatically)
curl -s -X PUT "http://localhost:23000/api/teams/<new-team-id>" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentIds": ["current-members...", "transferred-agent-id"]}' | jq .
```

---

## Chief-of-Staff Assignment (MANAGER Only)

The Chief-of-Staff (COS) is a trusted agent that can manage day-to-day team operations on behalf of the MANAGER. Only a MANAGER can assign or remove a COS. This operation requires the governance password, which must be provided by the user.

### Assign a Chief-of-Staff

```bash
curl -s -X POST "http://localhost:23000/api/teams/<team-id>/chief-of-staff" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentId": "<cos-agent-id>", "password": "<governance-password>"}' | jq .
```

### Remove a Chief-of-Staff

```bash
curl -s -X POST "http://localhost:23000/api/teams/<team-id>/chief-of-staff" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentId": null, "password": "<governance-password>"}' | jq .
```

**Important:** The governance password must be obtained from the user. Never store, cache, or log the password. Ask the user to provide it each time a COS assignment or removal is needed.

---

## Broadcast Messages

Use AMP messaging to broadcast messages to all agents in a team. The Chief-of-Staff can broadcast to their own team; MANAGER can broadcast to any team.

### Broadcast to a Team

```bash
TEAM_ID="<team-uuid>"
AGENTS=$(curl -s "http://localhost:23000/api/teams/$TEAM_ID" | jq -r '.agentIds[]')
for AGENT_ID in $AGENTS; do
  AGENT_NAME=$(curl -s "http://localhost:23000/api/agents/$AGENT_ID" | jq -r '.name')
  amp-send "$AGENT_NAME" "Team Update" "Your message here"
done
```

### Broadcast with Priority

```bash
TEAM_ID="<team-uuid>"
AGENTS=$(curl -s "http://localhost:23000/api/teams/$TEAM_ID" | jq -r '.agentIds[]')
for AGENT_ID in $AGENTS; do
  AGENT_NAME=$(curl -s "http://localhost:23000/api/agents/$AGENT_ID" | jq -r '.name')
  amp-send "$AGENT_NAME" "Urgent: Team Update" "Your urgent message here" --priority urgent
done
```

---

## Permission Matrix

| Action | Normal Agent | COS (own team) | COS (other team) | MANAGER |
|--------|:------------:|:--------------:|:-----------------:|:-------:|
| Create open team | Yes | Yes | Yes | Yes |
| Create closed team | No | No | No | Yes |
| Delete open team | No | No | No | Yes |
| Delete closed team | No | No | No | Yes |
| Change team type | No | No | No | Yes |
| Assign agent (own team) | No | Yes | No | Yes |
| Remove agent (own team) | No | Yes | No | Yes |
| Assign agent (other team) | No | No | No | Yes |
| Remove agent (other team) | No | No | No | Yes |
| Assign COS | No | No | No | Yes |
| Broadcast own team | No | Yes | No | Yes |
| Broadcast any team | No | No | No | Yes |
| Message any agent (AMP) | Yes | Yes | Yes | Yes |

---

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 403 | `message_blocked` | Agent does not have permission to message agents in a closed team it does not belong to. |
| 403 | `access_denied_closed_team` | Agent attempted a governance operation on a closed team without MANAGER or COS role. |
| 400 | `agent_already_in_closed_team` | The agent is already a member of another closed team. Transfer is required instead of direct assignment. |
| 401 | `invalid_governance_password` | The governance password provided for COS assignment/removal is incorrect. |
| 404 | `team_not_found` | The specified team ID does not exist. |
| 400 | `invalid_team_type` | Team type must be "open" or "closed". |

---

## Team Messaging Rules

Closed teams have messaging isolation. Understanding these rules is essential for reliable agent communication.

### Who Can Message Whom

| Your Title | Who You Can Message |
|-----------|-------------------|
| **Open-world agent** (not in any closed team) | Any agent NOT in a closed team |
| **Closed team member** | Same-team members + your team's Chief-of-Staff |
| **Chief-of-Staff** | Own team members + MANAGER + other Chiefs-of-Staff |
| **MANAGER** | Anyone (unrestricted) |

### Key Restrictions
- You **CANNOT** message into a closed team from outside — the message will be rejected (403)
- You **CANNOT** message out of a closed team to non-team-members (except COS/MANAGER)

### Contacting a Closed Team from Outside

Go through the team's **Chief-of-Staff**:

1. Find the COS: `curl -s "${AIMAESTRO_API:-http://localhost:23000}/api/teams/<team-id>" | jq -r '.chiefOfStaffId'`
2. Resolve the COS name: `curl -s "${AIMAESTRO_API:-http://localhost:23000}/api/agents/<cos-id>" | jq -r '.agent.name'`
3. Send your message to the COS, who can relay it to team members

---

## Troubleshooting

### "Access denied" on team operations

Verify your role with `curl -s "http://localhost:23000/api/governance" | jq .` -- you must be MANAGER or COS of the target team.

### "Agent already in closed team"

An agent can only belong to one closed team at a time. Use the MANAGER cross-team transfer operation to move the agent.

### "Invalid governance password"

Ask the user to re-provide the governance password. Passwords are not stored or cached.

### COS cannot manage other teams

A Chief-of-Staff's authority is scoped to their assigned team only. Cross-team operations require MANAGER privileges.
