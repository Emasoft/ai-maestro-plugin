# Team Governance Reference

## Table of Contents
- [Governance API Endpoints](#governance-api-endpoints)
- [Team Management](#team-management)
- [Agent Assignment](#agent-assignment)
- [Chief-of-Staff Assignment](#chief-of-staff-assignment)
- [Team Broadcast Messaging](#team-broadcast-messaging)
- [Permission Matrix](#permission-matrix)
- [Team Messaging Rules](#team-messaging-rules)
- [Error Codes](#error-codes)
- [Troubleshooting](#troubleshooting)

---

## Governance API Endpoints

Base URL: `${AIMAESTRO_API:-http://localhost:23000}`

All authenticated operations require `X-Agent-Id: <your-agent-id>` header.

| Operation | Method | Endpoint | Auth Required |
|-----------|--------|----------|---------------|
| Check own governance role | GET | `/api/governance` | None |
| List all teams | GET | `/api/teams` | None |
| Get team details | GET | `/api/teams/{id}` | None |
| Create team | POST | `/api/teams` | MANAGER for closed teams |
| Update team | PUT | `/api/teams/{id}` | MANAGER or COS |
| Delete team | DELETE | `/api/teams/{id}` | MANAGER |
| Assign/remove COS | POST | `/api/teams/{id}/chief-of-staff` | MANAGER + password |

---

## Team Management

### Check Your Governance Role (Run First)

```bash
curl -s "http://localhost:23000/api/governance" | jq .
```

Returns your agent's governance permissions. **If not MANAGER or COS, STOP** -- governance operations require elevated privileges.

### List All Teams

```bash
curl -s "http://localhost:23000/api/teams" | jq .
```

### Create a Team (MANAGER Only)

All teams are closed (isolated messaging with COS gateway). For lightweight unstructured agent collections, use Groups instead (`/api/groups`).

```bash
curl -s -X POST "http://localhost:23000/api/teams" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"name": "security-team", "type": "closed"}' | jq .
```

```bash
# With COS — auto-assigns COS title and auto-installs ai-maestro-chief-of-staff role-plugin
curl -s -X POST "http://localhost:23000/api/teams" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <manager-agent-id>" \
  -d '{"name": "security-team", "type": "closed", "chiefOfStaffId": "<cos-agent-id>"}' | jq .
```

**Auto-COS chain:** When `chiefOfStaffId` is provided, the `ai-maestro-chief-of-staff` role-plugin is automatically installed on the designated COS agent (`--scope local`). If no `chiefOfStaffId` is provided, the response includes `needsChiefOfStaff: true` — a COS must be assigned separately via `POST /api/teams/{id}/chief-of-staff`.

### Delete a Closed Team (MANAGER Only)

```bash
curl -s -X DELETE "http://localhost:23000/api/teams/<team-id>" \
  -H "X-Agent-Id: <your-agent-id>" | jq .
```

### Change Team Type (MANAGER Only)

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"type": "closed"}' | jq .
```

All teams are closed. Use Groups (`/api/groups`) for open agent collections.

---

## Agent Assignment

### Assign Agent to Closed Team (MANAGER or COS of that team)

```bash
# Get current members first
CURRENT=$(curl -s "http://localhost:23000/api/teams/<team-id>" | jq -r '.agentIds | join(",")')

# Add new agent to the list
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentIds": ["existing-agent-1", "existing-agent-2", "new-agent-id"]}' | jq .
```

### Remove Agent from Closed Team

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<team-id>" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentIds": ["remaining-agent-1", "remaining-agent-2"]}' | jq .
```

### Transfer Agent Cross-Team (MANAGER Only)

Assign agent to the new team -- old membership is automatically removed.

```bash
curl -s -X PUT "http://localhost:23000/api/teams/<new-team-id>" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentIds": ["current-members...", "transferred-agent-id"]}' | jq .
```

---

## Chief-of-Staff Assignment

COS is a trusted agent managing day-to-day team operations for the MANAGER. Only a MANAGER can assign/remove COS. Requires governance password from the user.

### Assign COS

```bash
curl -s -X POST "http://localhost:23000/api/teams/<team-id>/chief-of-staff" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentId": "<cos-agent-id>", "password": "<governance-password>"}' | jq .
```

### Remove COS

```bash
curl -s -X POST "http://localhost:23000/api/teams/<team-id>/chief-of-staff" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: <your-agent-id>" \
  -d '{"agentId": null, "password": "<governance-password>"}' | jq .
```

**Never store, cache, or log the governance password.** Ask the user each time.

**Role-plugin auto-install:** Assigning a COS automatically installs the `ai-maestro-chief-of-staff` role-plugin on the COS agent with `--scope local`. Similarly, assigning the MANAGER title auto-installs `ai-maestro-assistant-manager-agent`. These are non-blocking — title assignment succeeds even if plugin install fails.

---

## Team Broadcast Messaging

Use AMP to broadcast to all agents in a team. COS broadcasts to own team; MANAGER to any team.

### Broadcast to a Team

```bash
TEAM_ID="<team-uuid>"
AGENTS=$(curl -s "http://localhost:23000/api/teams/$TEAM_ID" | jq -r '.agentIds[]')
for AGENT_ID in $AGENTS; do
  AGENT_NAME=$(curl -s "http://localhost:23000/api/agents/$AGENT_ID" | jq -r '.agent.name')
  amp-send "$AGENT_NAME" "Team Update" "Your message here"
done
```

### Broadcast with Priority

```bash
TEAM_ID="<team-uuid>"
AGENTS=$(curl -s "http://localhost:23000/api/teams/$TEAM_ID" | jq -r '.agentIds[]')
for AGENT_ID in $AGENTS; do
  AGENT_NAME=$(curl -s "http://localhost:23000/api/agents/$AGENT_ID" | jq -r '.agent.name')
  amp-send "$AGENT_NAME" "Urgent: Team Update" "Your urgent message here" --priority urgent
done
```

---

## Permission Matrix

| Action | Normal Agent | COS (own team) | COS (other team) | MANAGER |
|--------|:------------:|:--------------:|:-----------------:|:-------:|
| Create team | No | No | No | Yes |
| Delete team | No | No | No | Yes |
| Assign agent (own team) | No | Yes | No | Yes |
| Remove agent (own team) | No | Yes | No | Yes |
| Assign agent (other team) | No | No | No | Yes |
| Remove agent (other team) | No | No | No | Yes |
| Assign COS | No | No | No | Yes |
| Broadcast own team | No | Yes | No | Yes |
| Broadcast any team | No | No | No | Yes |
| Message via AMP | Title-restricted | Team + COS + MANAGER | Team + COS + MANAGER | Unrestricted |

**Note:** AMP messaging between agents is governed by the title-based communication graph (see below). Normal agents (ARCHITECT, INTEGRATOR, MEMBER) can only reach COS and ORCHESTRATOR.

**Membership constraints:**
- A COS agent can lead **one closed team only** — cannot be COS of multiple teams simultaneously.
- A normal agent can belong to at most **one team** at any time.
- MANAGER can belong to **unlimited** teams.

---

## Team Messaging Rules

AMP messaging is governed by a **title-based directed communication graph**. Each governance title defines which other titles the agent can message directly. Connections not in the graph are blocked with HTTP 403 and a routing suggestion.

**Subagents** (spawned task helpers without their own Claude Code instance) **cannot send messages at all** — they are not nodes in the graph.

### Communication Graph — Adjacency Matrix

| Sender \ Recipient | MANAGER | COS | ORCHESTRATOR | ARCHITECT | INTEGRATOR | MEMBER | AUTONOMOUS |
|---------------------|:-------:|:---:|:------------:|:---------:|:----------:|:------:|:----------:|
| **MANAGER**         |    Y    |  Y  |      Y       |     Y     |     Y      |   Y    |     Y      |
| **CHIEF-OF-STAFF**  |    Y    |  Y  |      Y       |     Y     |     Y      |   Y    |     Y      |
| **ORCHESTRATOR**    |         |  Y  |              |     Y     |     Y      |   Y    |            |
| **ARCHITECT**       |         |  Y  |      Y       |           |            |        |            |
| **INTEGRATOR**      |         |  Y  |      Y       |           |            |        |            |
| **MEMBER**          |         |  Y  |      Y       |           |            |        |            |
| **AUTONOMOUS**      |    Y    |  Y  |              |           |            |        |     Y      |

### Key Rules

- **MANAGER and COS** can message anyone (full access row in the matrix).
- **ORCHESTRATOR** can message COS and team workers (ARCHITECT, INTEGRATOR, MEMBER) but **NOT** MANAGER.
- **Workers** (ARCHITECT, INTEGRATOR, MEMBER) can **ONLY** message COS and ORCHESTRATOR.
- **AUTONOMOUS** can message MANAGER, COS, and other AUTONOMOUS agents.
- If a connection is missing, the message is blocked with HTTP 403. The error response includes a `suggestion` field with a routing path.

### Routing Suggestions (When Blocked)

| Sender Title | Blocked Recipient | Routing Suggestion |
|-------------|-------------------|-------------------|
| ORCHESTRATOR | MANAGER | Route through COS |
| ORCHESTRATOR | AUTONOMOUS | Route through COS or MANAGER |
| ARCHITECT / INTEGRATOR / MEMBER | MANAGER | Route through COS |
| ARCHITECT / INTEGRATOR / MEMBER | Other workers | Route through ORCHESTRATOR or COS |
| ARCHITECT / INTEGRATOR / MEMBER | AUTONOMOUS | Route through COS or MANAGER |
| AUTONOMOUS | ORCHESTRATOR / workers | Route through MANAGER or COS |

### Contacting a Closed Team from Outside

Go through the team's Chief-of-Staff:

1. Find COS ID: `curl -s "${AIMAESTRO_API:-http://localhost:23000}/api/teams/<team-id>" | jq -r '.chiefOfStaffId'`
2. Resolve COS name: `curl -s "${AIMAESTRO_API:-http://localhost:23000}/api/agents/<cos-id>" | jq -r '.agent.name'`
3. Send message to the COS, who relays to team members

---

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 403 | `message_blocked` | No permission to message agents in a closed team you don't belong to |
| 403 | `title_communication_forbidden` | Sender's governance title cannot message recipient's title (see communication graph) |
| 403 | `access_denied_closed_team` | Governance op on closed team without MANAGER or COS role |
| 400 | `agent_already_in_closed_team` | Agent is in another closed team; use cross-team transfer |
| 401 | `invalid_governance_password` | Incorrect governance password for COS assignment/removal |
| 404 | `team_not_found` | Team ID does not exist |
| 400 | `invalid_team_type` | Invalid team configuration |

---

## Troubleshooting

### "Access denied" on team operations
Verify role: `curl -s "http://localhost:23000/api/governance" | jq .` -- must be MANAGER or COS of target team.

### "Agent already in closed team"
Agent can only belong to one closed team. Use MANAGER cross-team transfer.

### "Invalid governance password"
Ask user to re-provide password. Passwords are never stored or cached.

### COS cannot manage other teams
COS authority is scoped to assigned team only. Cross-team ops require MANAGER.
