---
name: team-governance
description: Manage AI Maestro teams and governance titles (roles, chief-of-staff, membership)
---
# /team-governance

Manage teams and governance titles — roles, chief-of-staff delegation, and team membership.

## Usage

```text
/team-governance [what you want to do]
```

## Implementation

Load the `team-governance` skill and follow it, passing the user's request through. The
skill drives `aimaestro-governance.sh`, `aimaestro-teams.sh`, and `aimaestro-agent.sh`.

## Examples

```text
/team-governance list the current titles
/team-governance who is the chief-of-staff for the backend team
```

## Notes

Governance operations are permission-gated by your role — the skill carries the authority
matrix and refuses an operation your title does not hold, rather than attempting it and
failing partway.
