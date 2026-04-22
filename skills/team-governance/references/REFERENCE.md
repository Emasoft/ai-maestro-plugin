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

**Note:** AMP messaging between agents is governed by the title-based communication graph (R6 v2, see below). Normal agents (ARCHITECT, INTEGRATOR, MEMBER) can only reach COS and ORCHESTRATOR directly; they can only reply to the user via the `1` (reply-only) edge.

**Membership constraints:**

- A COS agent can lead **one closed team only** — cannot be COS of multiple teams simultaneously.
- A normal agent can belong to at most **one team** at any time.
- MANAGER can belong to **unlimited** teams.

---

## Team Messaging Rules

AMP messaging is governed by the **R6 v2 title-based directed communication graph**. Two edge types: `Y` (allow) and `1` (reply-only — sender MUST pass `options.inReplyToMessageId` referencing an inbound H→agent message; AMP marks the inbound `replied=true` on delivery, so one reply per inbound). Blank = deny. The server enforces this before every delivery in `lib/communication-graph.ts::validateMessageRoute()` and returns HTTP 403 `title_communication_forbidden` on a forbidden edge.

**Subagents** (spawned task helpers without their own Claude Code instance) **cannot send messages at all** — they are not nodes in the graph.

This section mirrors `docs/GOVERNANCE-RULES.md` §R6 (rules R6.1–R6.10) in the `Emasoft/ai-maestro` server repo. Do not drift — the server's `lib/communication-graph.ts` is the canonical source.

### Communication Graph — Adjacency Matrix (v2)

`Y` = allowed, `1` = reply-only, blank = forbidden.

| Sender \ Recipient | HUMAN | MANAGER | COS | ORCH | ARCH | INT | MEM | MAINT | AUTO |
|---------------------|:-----:|:-------:|:---:|:----:|:----:|:---:|:---:|:-----:|:----:|
| **HUMAN**           |   Y   |    Y    |  Y  |  Y   |  Y   |  Y  |  Y  |   Y   |  Y   |
| **MANAGER**         |   Y   |    Y    |  Y  |  Y   |  Y   |  Y  |  Y  |   Y   |  Y   |
| **COS**             |   1   |    Y    |  Y  |  Y   |  Y   |  Y  |  Y  |       |      |
| **ORCHESTRATOR**    |   1   |         |  Y  |      |  Y   |  Y  |  Y  |       |      |
| **ARCHITECT**       |   1   |         |  Y  |  Y   |      |     |     |       |      |
| **INTEGRATOR**      |   1   |         |  Y  |  Y   |      |     |     |       |      |
| **MEMBER**          |   1   |         |  Y  |  Y   |      |     |     |       |      |
| **MAINTAINER**      |   Y   |    Y    |     |      |      |     |     |       |      |
| **AUTONOMOUS**      |   Y   |    Y    |     |      |      |     |     |       |  Y   |

### Rules R6.1 – R6.10

| ID | Rule |
|----|------|
| **R6.1** | Communication is defined by the matrix above. Edge types: `Y` allow, `1` reply-only, blank deny. Unlisted pairs are denied. |
| **R6.2** | MANAGER has full `Y` access — sole bridge between team layer (COS + team roles) and governance layer (MAINTAINER, AUTONOMOUS). |
| **R6.3** | CHIEF-OF-STAFF is strictly the team gateway — `Y` to MANAGER + peer COS + team roles; `1` to HUMAN; blank to MAINTAINER + AUTONOMOUS. |
| **R6.4** | ORCHESTRATOR — `Y` to COS + ARCHITECT + INTEGRATOR + MEMBER; `1` to HUMAN; blank elsewhere. |
| **R6.5** | ARCHITECT / INTEGRATOR / MEMBER — `Y` to COS + ORCHESTRATOR; `1` to HUMAN; blank elsewhere. |
| **R6.5a** | AUTONOMOUS — `Y` to MANAGER + peer AUTONOMOUS + HUMAN; blank to COS + team roles + MAINTAINER. |
| **R6.5b** | MAINTAINER — `Y` to MANAGER + HUMAN; blank to COS + team roles + AUTONOMOUS + peer MAINTAINER. |
| **R6.6** | HUMAN has full `Y` outbound to every node including self. Inbound to H from team titles is `1` (reply-only). Inbound to H from governance titles is `Y`. Agents SHOULD NOT proactively initiate user contact even when persona-permitted — `1` is the hard server-enforced floor, persona is the soft floor. |
| **R6.7** | Blocked messages MUST return HTTP 403 with a routing suggestion. Cross-layer routes go through MANAGER (not COS). |
| **R6.8** | Three enforcement layers: (1) server `validateMessageRoute()`, (2) role-plugin main-agent `.md` listing recipients, (3) sub-agents forbidden from AMP entirely. |
| **R6.9** | Sub-agents have no AMP identity, cannot authenticate, communicate only with their spawning main-agent. |
| **R6.10** | Reply-only enforcement requires `options.inReplyToMessageId` referencing an inbound H→agent message. AMP inbox marks original `replied=true` on delivery, refusing a second reply. |

### Key Rules

- **MANAGER** has full `Y` access — the sole cross-layer bridge between team layer (COS + team roles) and governance layer (MAINTAINER, AUTONOMOUS).
- **CHIEF-OF-STAFF** is the team gateway only: `Y` to MANAGER + peer COS + team roles; `1` (reply-only) to HUMAN; **blank to MAINTAINER and AUTONOMOUS** (COS no longer reaches the governance layer — route via MANAGER).
- **ORCHESTRATOR** can message COS and team workers (ARCHITECT, INTEGRATOR, MEMBER) but **NOT** MANAGER directly; `1` to HUMAN.
- **Workers** (ARCHITECT, INTEGRATOR, MEMBER) can **ONLY** message COS and ORCHESTRATOR; `1` to HUMAN.
- **MAINTAINER** reaches MANAGER + HUMAN only.
- **AUTONOMOUS** reaches MANAGER + peer AUTONOMOUS + HUMAN only.
- **Team titles (COS / ORCH / ARCH / INT / MEM) MUST NOT proactively initiate user contact** — only reply to a prior user message via the `1` edge, which consumes the one-reply-per-inbound quota.
- Blocked connections return HTTP 403 `title_communication_forbidden` with a `suggestion` routing path. Cross-layer routes go **through MANAGER**, not COS.

### Routing Suggestions (When Blocked)

| Sender Title | Blocked Recipient | Routing Suggestion |
|-------------|-------------------|-------------------|
| COS | MAINTAINER | Route through MANAGER |
| COS | AUTONOMOUS | Route through MANAGER |
| ORCHESTRATOR | MANAGER | Route through COS |
| ORCHESTRATOR | MAINTAINER | Route through COS → MANAGER |
| ORCHESTRATOR | AUTONOMOUS | Route through COS → MANAGER |
| ARCHITECT / INTEGRATOR / MEMBER | MANAGER | Route through COS |
| ARCHITECT / INTEGRATOR / MEMBER | Other workers | Route through ORCHESTRATOR or COS |
| ARCHITECT / INTEGRATOR / MEMBER | MAINTAINER | Route through COS → MANAGER |
| ARCHITECT / INTEGRATOR / MEMBER | AUTONOMOUS | Route through COS → MANAGER |
| MAINTAINER | COS / ORCH / workers / AUTONOMOUS / peer MAINTAINER | Route through MANAGER |
| AUTONOMOUS | COS / ORCH / workers / MAINTAINER | Route through MANAGER |
| Team title (COS/ORCH/ARCH/INT/MEM) | HUMAN (no prior inbound) | Wait for the user to message first; then reply with `inReplyToMessageId` |

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
