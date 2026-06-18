# Team Governance Reference

<!-- Decoupled per MANAGER core#11 (TRDD-90c8ad35): every example calls the frozen `aimaestro-governance.sh` / `aimaestro-teams.sh` / `aimaestro-agent.sh` CLIs (which resolve the API base + agent identity internally), never the server `/api/*` directly. Residuals with no frozen verb yet (assign-COS-to-existing-team, change-team-type, Groups) are marked DECOUPLE-BLOCKED inline, re-targeted to an ai-maestro follow-up. -->

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

## Governance CLI Commands

All operations go through the frozen CLIs (`aimaestro-governance.sh`,
`aimaestro-teams.sh`, `aimaestro-agent.sh`), which resolve the API base + your
agent identity internally — no base URL and no `X-Agent-Id` header to set by hand.

| Operation | CLI command | Auth Required |
|-----------|-------------|---------------|
| Check own governance role | `aimaestro-governance.sh whoami` | None |
| List all teams | `aimaestro-teams.sh list` | None |
| Get team details | `aimaestro-teams.sh show <team-id>` | None |
| Create team | `aimaestro-teams.sh create --name <n> --type closed [--cos <id>]` | MANAGER for closed teams |
| Update team | `aimaestro-teams.sh update <team-id> [--name\|--description\|--agents\|--orchestrator]` | MANAGER or COS |
| Delete team | `aimaestro-teams.sh delete <team-id> [--password <pw>]` | MANAGER |
| Add / remove agent | `aimaestro-teams.sh add-agent\|remove-agent <team-id> <agent>` | MANAGER or COS |
| Assign COS to existing team | _no frozen verb yet — DECOUPLE-BLOCKED #36 (set `--cos` at create)_ | MANAGER + password |

---

## Team Management

### Check Your Governance Role (Run First)

```bash
aimaestro-governance.sh whoami | jq .
```

Returns your agent's governance permissions. **If not MANAGER or COS, STOP** -- governance operations require elevated privileges.

### List All Teams

```bash
aimaestro-teams.sh list | jq .
```

### Create a Team (MANAGER Only)

All teams are closed (isolated messaging with COS gateway). For lightweight unstructured agent collections, use Groups instead. <!-- DECOUPLE-BLOCKED ai-maestro#36: Groups (was `/api/groups`) have no frozen-CLI verb yet — pending a follow-up. Do NOT call `/api/*` directly (core#11). -->

```bash
aimaestro-teams.sh create --name security-team --type closed | jq .
```

```bash
# With COS — auto-assigns the COS title and auto-installs ai-maestro-chief-of-staff (--scope local)
aimaestro-teams.sh create --name security-team --type closed --cos <cos-agent-id> | jq .
```

**Auto-COS chain:** When `--cos` is provided, the `ai-maestro-chief-of-staff` role-plugin is automatically installed on the designated COS agent (`--scope local`). If no `--cos` is provided, the team is created without a COS. <!-- DECOUPLE-BLOCKED ai-maestro#36: assigning a COS to an ALREADY-EXISTING team (was `POST /api/teams/{id}/chief-of-staff`) has no frozen verb yet (`aimaestro-teams.sh update` exposes no `--cos`); pending a follow-up. Until then set `--cos` at create time, or have the MANAGER assign via their own tooling. -->

### Delete a Closed Team (MANAGER Only)

```bash
aimaestro-teams.sh delete <team-id> --password <governance-password> | jq .
```

### Change Team Type (MANAGER Only)

All teams are closed by design; there is no open/closed toggle to set. <!-- DECOUPLE-BLOCKED ai-maestro#36: `aimaestro-teams.sh update` exposes no `--type` flag (was `PUT /api/teams/{id}` with `{type}`). Effectively a no-op since all teams are closed; pending a follow-up verb only if a type toggle is ever reintroduced. -->

---

## Agent Assignment

### Assign Agent to Closed Team (MANAGER or COS of that team)

```bash
# add-agent appends to the team's membership — no need to fetch + resend the full list.
aimaestro-teams.sh add-agent <team-id> <new-agent-id> | jq .
```

### Remove Agent from Closed Team

```bash
aimaestro-teams.sh remove-agent <team-id> <agent-id> | jq .
```

### Transfer Agent Cross-Team (MANAGER Only)

Add the agent to the new team -- old closed-team membership is automatically removed.

```bash
aimaestro-teams.sh add-agent <new-team-id> <transferred-agent-id> | jq .
```

---

## Chief-of-Staff Assignment

COS is a trusted agent managing day-to-day team operations for the MANAGER. Only a MANAGER can assign/remove COS. Requires governance password from the user.

### Assign COS

At **create time**, pass `--cos` (supported):

```bash
aimaestro-teams.sh create --name <team-name> --type closed --cos <cos-agent-id> --password <governance-password> | jq .
```

<!-- DECOUPLE-BLOCKED ai-maestro#36: assigning a COS to an ALREADY-EXISTING team (was `POST /api/teams/{id}/chief-of-staff`) has no frozen-CLI verb yet — `aimaestro-teams.sh update` exposes no `--cos`. Same gov-password residual class flagged on ai-maestro#36; pending a follow-up verb. Until then: set `--cos` at create, or the MANAGER assigns through their own tooling. Do NOT call `/api/*` directly (core#11). -->

### Remove COS

<!-- DECOUPLE-BLOCKED ai-maestro#36: removing a COS from a team (was `POST /api/teams/{id}/chief-of-staff` with `agentId:null`) has no frozen-CLI verb yet — pending the same follow-up as assign-COS. Do NOT call `/api/*` directly (core#11). -->

**Never store, cache, or log the governance password.** Ask the user each time.

**Role-plugin auto-install:** Assigning a COS automatically installs the `ai-maestro-chief-of-staff` role-plugin on the COS agent with `--scope local`. Similarly, assigning the MANAGER title auto-installs `ai-maestro-assistant-manager-agent`. These are non-blocking — title assignment succeeds even if plugin install fails.

---

## Team Broadcast Messaging

Use AMP to broadcast to all agents in a team. COS broadcasts to own team; MANAGER to any team.

### Broadcast to a Team

```bash
TEAM_ID="<team-uuid>"
AGENTS=$(aimaestro-teams.sh show "$TEAM_ID" | jq -r '.agentIds[]')
for AGENT_ID in $AGENTS; do
  AGENT_NAME=$(aimaestro-agent.sh show "$AGENT_ID" | jq -r '.agent.name')
  amp-send "$AGENT_NAME" "Team Update" "Your message here"
done
```

### Broadcast with Priority

```bash
TEAM_ID="<team-uuid>"
AGENTS=$(aimaestro-teams.sh show "$TEAM_ID" | jq -r '.agentIds[]')
for AGENT_ID in $AGENTS; do
  AGENT_NAME=$(aimaestro-agent.sh show "$AGENT_ID" | jq -r '.agent.name')
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

### Communication Graph — Adjacency Matrix (v3, 2026-05-04)

`Y` = allowed, `1` = reply-only, blank = forbidden.

**v2 → v3 change:** MANAGER's outbound edges to in-team non-COS titles
(ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER) flipped from `Y` to **blank**.
Real-world tests showed great confusion when MANAGER bypassed COS to issue
directives directly to team agents — COS or ORCHESTRATOR ended up
uninformed or issued contradictory instructions on the same task. The
**CHIEF-OF-STAFF is now the SOLE inbound and outbound gateway for
closed-team agents**. MANAGER still freely reaches COS, peer MANAGERs,
MAINTAINER, AUTONOMOUS, and HUMAN.

| Sender \ Recipient | HUMAN | MANAGER | COS | ORCH | ARCH | INT | MEM | MAINT | AUTO |
|---------------------|:-----:|:-------:|:---:|:----:|:----:|:---:|:---:|:-----:|:----:|
| **HUMAN**           |   Y   |    Y    |  Y  |  Y   |  Y   |  Y  |  Y  |   Y   |  Y   |
| **MANAGER**         |   Y   |    Y    |  Y  |      |      |     |     |   Y   |  Y   |
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
| **R6.2** | MANAGER has `Y` to COS + peer MANAGER + governance layer (MAINTAINER, AUTONOMOUS) + HUMAN. **In-team non-COS titles (ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER) are blank for MANAGER as of v3 (2026-05-04)** — MANAGER must route through COS. |
| **R6.3** | CHIEF-OF-STAFF is the SOLE inbound/outbound gateway for closed-team agents — `Y` to MANAGER + peer COS + team roles (ORCH/ARCH/INT/MEM); `1` to HUMAN; blank to MAINTAINER + AUTONOMOUS. |
| **R6.4** | ORCHESTRATOR — `Y` to COS + ARCHITECT + INTEGRATOR + MEMBER; `1` to HUMAN; blank elsewhere. |
| **R6.5** | ARCHITECT / INTEGRATOR / MEMBER — `Y` to COS + ORCHESTRATOR; `1` to HUMAN; blank elsewhere. |
| **R6.5a** | AUTONOMOUS — `Y` to MANAGER + peer AUTONOMOUS + HUMAN; blank to COS + team roles + MAINTAINER. |
| **R6.5b** | MAINTAINER — `Y` to MANAGER + HUMAN; blank to COS + team roles + AUTONOMOUS + peer MAINTAINER. |
| **R6.6** | HUMAN has full `Y` outbound to every node including self. Inbound to H from team titles is `1` (reply-only). Inbound to H from governance titles is `Y`. Agents SHOULD NOT proactively initiate user contact even when persona-permitted — `1` is the hard server-enforced floor, persona is the soft floor. |
| **R6.7** | Blocked messages MUST return HTTP 403 with a routing suggestion. Cross-team routes go through MANAGER → recipient's COS; intra-team routes from MANAGER also go through that team's COS. |
| **R6.8** | Three enforcement layers: (1) server `validateMessageRoute()`, (2) role-plugin main-agent `.md` listing recipients, (3) sub-agents forbidden from AMP entirely. |
| **R6.9** | Sub-agents have no AMP identity, cannot authenticate, communicate only with their spawning main-agent. |
| **R6.10** | Reply-only enforcement requires `options.inReplyToMessageId` referencing an inbound H→agent message. AMP inbox marks original `replied=true` on delivery, refusing a second reply. |
| **R6.11–R6.14** | Canonical agent address format (2026-05-06): single ID per host, wire form `<agent-id>@<host>` or `<host>:<agent-id>`, bare `<agent-id>` resolves to writer's host. Persona name may alias the agent-id when no collision exists; collisions return HTTP 409 `disambiguation_required`. The legacy 3-level hierarchical (`team/sub/name`) format is deprecated — see R6 in the bundled governance rules. |

### Key Rules

- **MANAGER** reaches COS, peer MANAGER, MAINTAINER, AUTONOMOUS, HUMAN. v3 (2026-05-04) **removes** MANAGER's direct edges to ORCHESTRATOR/ARCHITECT/INTEGRATOR/MEMBER — route via COS.
- **CHIEF-OF-STAFF** is the SOLE gateway for closed-team agents: `Y` to MANAGER + peer COS + team roles; `1` (reply-only) to HUMAN; blank to MAINTAINER and AUTONOMOUS.
- **ORCHESTRATOR** can message COS and team workers (ARCHITECT, INTEGRATOR, MEMBER) but **NOT** MANAGER directly; `1` to HUMAN.
- **Workers** (ARCHITECT, INTEGRATOR, MEMBER) can **ONLY** message COS and ORCHESTRATOR; `1` to HUMAN.
- **MAINTAINER** reaches MANAGER + HUMAN only.
- **AUTONOMOUS** reaches MANAGER + peer AUTONOMOUS + HUMAN only.
- **Team titles (COS / ORCH / ARCH / INT / MEM) MUST NOT proactively initiate user contact** — only reply to a prior user message via the `1` edge, which consumes the one-reply-per-inbound quota.
- Blocked connections return HTTP 403 `title_communication_forbidden` with a `suggestion` routing path. Cross-layer routes go **through MANAGER → COS**, never directly.

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

1. Find COS ID: `aimaestro-teams.sh show <team-id> | jq -r '.chiefOfStaffId'`
2. Resolve COS name: `aimaestro-agent.sh show <cos-id> | jq -r '.agent.name'`
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

Verify role: `aimaestro-governance.sh whoami | jq .` -- must be MANAGER or COS of target team.

### "Agent already in closed team"

Agent can only belong to one closed team. Use MANAGER cross-team transfer.

### "Invalid governance password"

Ask user to re-provide password. Passwords are never stored or cached.

### COS cannot manage other teams

COS authority is scoped to assigned team only. Cross-team ops require MANAGER.
