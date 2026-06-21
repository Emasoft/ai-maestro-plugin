# AI Maestro Plugin

<!--BADGES-START-->
![version](https://img.shields.io/badge/version-2.7.14-blue)
![license](https://img.shields.io/badge/license-MIT-green)
<!--BADGES-END-->

The umbrella core plugin for the AI Maestro ecosystem — shared skills, AMP
messaging, AID identity, governance, kanban, and the universal PRRD/TRDD/Kanban
workflow that every role plugin inherits.

**Skills:** 22 | **Commands:** 12 | **Scripts:** 15 Python/shell (+ the bundled
`memgrep` Rust crate under `scripts/memgrep/`)

Last updated: 2026-06-16

See the [main repo][repo] for the wider ecosystem.

[repo]: https://github.com/Emasoft/ai-maestro-plugins

## Installation

Install from the `Emasoft/ai-maestro-plugins` marketplace inside Claude Code:

```text
/plugin marketplace add Emasoft/ai-maestro-plugins
/plugin install ai-maestro-plugin
```

The PRRD/TRDD/Kanban pillar scripts need Python 3.10+ on `PATH`. The AMP/AID
shell scripts need the `curl, jq, openssl, base64` CLI tools. The optional `memgrep`
note-recall engine installs from a prebuilt release binary via
`scripts/install-memgrep.sh` (cargo-build fallback; recall degrades to plain
grep without it). Most messaging features also require a running AI Maestro
server on `http://localhost:23000`.

## Usage

The plugin loads its skills automatically; invoke a workflow with its slash
command or by describing the task:

```text
/ama-prrd-get              # read a PRRD rule by number (every role)
/ama-trdd-write            # author a TRDD; /ama-trdd-transition moves columns
/ama-kanban-render         # render the design/spec board (read-only)
/team-governance           # team governance and COS management
/amp-inbox                 # check the inter-agent message inbox
/amp-send <to> <subj> <msg>  # send a message to another agent
```

Per-skill usage and examples live in each skill's `SKILL.md`; the AMP commands
are documented in the table below.

## Skills

| Skill                           | Description                                  |
|---------------------------------|----------------------------------------------|
| `ai-maestro-agents-management`  | Agent lifecycle management                   |
| `agent-identity`                | AID agent identity (Ed25519)                 |
| `agent-messaging`               | AMP inter-agent messaging                    |
| `debug-hooks`                   | Hook debugging utilities                     |
| `docs-search`                   | Documentation search                         |
| `graph-query`                   | Code graph querying                          |
| `mcp-discovery`                 | MCP server discovery                         |
| `memory-search`                 | Conversation memory search                   |
| `network-security`              | Network security checks                      |
| `planning`                      | Task planning (persistent files)             |
| `ama-prrd-get`                  | Read a PRRD rule by number (any role)        |
| `ama-prrd-find`                 | Search PRRD rules by content / metadata      |
| `ama-prrd-edit`                 | Mutate a SILVER PRRD rule (MANAGER-gated)    |
| `ama-prrd-propose`              | Propose a PRRD change (any role; non-binding)|
| `ama-trdd-find`                 | Find TRDD task-design docs (read-only)       |
| `ama-trdd-write`                | Author a new TRDD (tier-aware zone)          |
| `ama-trdd-update`               | Edit an existing TRDD's body / evidence      |
| `ama-trdd-transition`           | Move a TRDD between columns (matrix-enforced)|
| `ama-kanban-render`             | Render the design/spec board (read-only)     |
| `ama-proposal-approvals`        | Batch approve/refuse/archive (MANAGER-gated) |
| `team-governance`               | Team governance and COS management           |
| `team-kanban`                   | Team kanban boards and tasks                 |

## Memory: transcripts vs curated notes (two complementary systems)

Two memory surfaces answer different questions:

| System | Skill(s) | Corpus | Question it answers |
|--------|----------|--------|---------------------|
| Conversation memory | `memory-search` (this plugin) | AI Maestro's indexed conversation transcripts | "what did we SAY / discuss / decide?" |
| Wiki note memory | `/janitor-memory-{recall,write,update}` (janitor global) | curated, symptom-indexed wiki pages | "what did we LEARN that must not be re-derived?" |

The curated-note memory is now the **janitor's GLOBAL wiki-memory system**
(`/janitor-memory-recall`, `/janitor-memory-write`, `/janitor-memory-update`,
governed by `~/.claude/rules/markdown-memory-recall.md`). This plugin's own
note-memory skills were retired in favor of it; `memory-search`
(transcript search) stays and names the global skills as its complement.

This plugin still **HOSTS the `memgrep` engine** the wiki recall depends on —
[`memgrep`](scripts/memgrep/SKILL.md) is a markdown-aware search engine whose
source ships in `scripts/memgrep/` and is consumed across the ecosystem. Install
it with:

```bash
scripts/install-memgrep.sh    # prebuilt sha256-verified binary (macOS arm64/x64, linux x64);
                              # cargo-build fallback; recall degrades to plain grep without it
```

Prebuilt binaries are attached to each GitHub release as
`memgrep-<platform>.tar.gz` + `.sha256` — end-users need no Rust toolchain.

## AMP Commands (Agent Messaging Protocol)

12 slash commands for inter-agent communication:

| Command           | Description                                |
|-------------------|--------------------------------------------|
| `/amp-init`       | Initialize agent identity and messaging    |
| `/amp-identity`   | Quick identity check for context recovery  |
| `/amp-status`     | Show messaging status and registrations    |
| `/amp-inbox`      | Check message inbox                        |
| `/amp-read`       | Read a specific message                    |
| `/amp-send`       | Send a message to another agent            |
| `/amp-reply`      | Reply to a message                         |
| `/amp-delete`     | Delete a message                           |
| `/amp-register`   | Register with an external AMP provider     |
| `/amp-fetch`      | Fetch messages from external providers     |
| `/amp-download`   | Download attachments from a message        |
| `/amp-statusline` | Install AMP status line for Claude Code    |

## AMP Scripts

14 shell scripts installed to PATH for messaging operations:

- `amp-init.sh`, `amp-identity.sh`, `amp-status.sh`
- `amp-inbox.sh`, `amp-read.sh`, `amp-send.sh`
- `amp-reply.sh`, `amp-delete.sh`, `amp-register.sh`
- `amp-fetch.sh`, `amp-download.sh`, `amp-statusline.sh`
- `amp-helper.sh`, `amp-security.sh`

## AID Scripts (Agent Identity)

5 shell scripts for agent identity management:

| Script            | Description                              |
|-------------------|------------------------------------------|
| `aid-init.sh`     | Initialize Ed25519 agent identity        |
| `aid-register.sh` | Register identity with a provider        |
| `aid-status.sh`   | Show identity status                     |
| `aid-token.sh`    | Generate/exchange identity tokens        |
| `aid-helper.sh`   | Shared helper functions for AID scripts  |

## Requirements

External tools the plugin's shell scripts call:

- `curl(1)` — HTTP requests to AMP providers and AI Maestro
- `jq` — JSON parsing in shell scripts
- `openssl` — Ed25519 keypair generation for AID
- `base64` — message attachment encoding

## Storage

AMP/AID state is written under `~/.agent-messaging/`:

```text
~/.agent-messaging/
├── config.json          # local agent config
├── keys/                # Ed25519 keypair (private + public)
├── messages/
│   ├── inbox/           # received messages
│   └── sent/            # sent messages
├── registrations/       # external provider registrations
└── attachments/         # downloaded attachments
```

## License

MIT
