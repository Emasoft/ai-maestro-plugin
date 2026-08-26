---
name: external-claude-session-is-not-an-ai-maestro-agent
description: "should this plugin-dev session register with ai-maestro / claim an AID / use AMP or AIP scripts / act as an ai-maestro agent — no, an external Claude Code session is NOT an agent until the MAESTRO USER imports it via the server dashboard"
ocd: 2026-08-26
lmd: 2026-08-26
metadata:
  node_type: memory
  type: project
  tier: aspect
publish-globally: false
---

# external-claude-session-is-not-an-ai-maestro-agent


^ATOM-2Q8M-EQD2 [desc: "USER 2026-08-26: an external Claude session is not an ai-maestro agent — no self-registration; coordinate via SendMessage only", keywords: am_i_an_ai-maestro_agent register_with_ai-maestro AID_identity_claim AMP_AIP_protocol_access ai-maestro_server_not_running coordinate_with_the_ai-maestro_claude plugin_dev_session_outside_the_harness, type: project, ocd: 2026-08-26, lmd: 2026-08-26]

**USER directive (2026-08-26).** A Claude Code plugin-development session is **NOT an ai-maestro
agent**. It becomes one only when BOTH hold in the future: it runs inside the ai-maestro harness,
AND the MAESTRO USER imports the instance via the ai-maestro server dashboard.

**Until then:**

- **No registration with ai-maestro of any kind** may be performed by an external Claude instance —
  not an AID claim, not a workdir registration, not an agent-roster entry.
- The only sanctioned cross-instance channel is **`SendMessage` to the ai-maestro Claude**, which is
  itself an ORDINARY external instance (you cannot develop ai-maestro from inside ai-maestro), not
  an agent.
- This project stays an **ordinary Claude project**, independent of whether the ai-maestro server,
  its API, or its services are running.
- On import (future), registration, AMP/AIP protocol access, and the ai-maestro scripts are granted
  **automatically** — never self-granted beforehand.

**Why:** self-registration would fake an identity the harness never issued, and would couple this
repo's work to a server it must not depend on.

## Notes and lessons learned
