# AI Maestro Plugin

<!--BADGES-START-->
![version](https://img.shields.io/badge/version-2.7.1-blue)
![license](https://img.shields.io/badge/license-MIT-green)
<!--BADGES-END-->

The umbrella core plugin for the AI Maestro ecosystem — shared skills, AMP
messaging, AID identity, governance, kanban, and the universal PRRD/TRDD/Kanban
workflow that every role plugin inherits.

**Skills:** 15 | **Commands:** 12 | **Scripts:** 15 Python/shell (+ the bundled
`memgrep` Rust crate under `scripts/memgrep/`)

Last updated: 2026-06-11

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
/prrd-trdd-kanban          # read/mutate PRRD rules, author/find TRDDs, render the board
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
| `memory-recall`                 | Curated-note memory recall (memgrep)         |
| `memory-write`                  | Curated-note memory authoring                |
| `network-security`              | Network security checks                      |
| `planning`                      | Task planning (persistent files)             |
| `prrd-trdd-kanban`              | Universal PRRD / TRDD / Kanban workflow      |
| `team-governance`               | Team governance and COS management           |
| `team-kanban`                   | Team kanban boards and tasks                 |

## Memory: transcripts vs curated notes (two complementary systems)

The plugin ships TWO memory surfaces — they answer different questions:

| System | Skill(s) | Corpus | Question it answers |
|--------|----------|--------|---------------------|
| Conversation memory | `memory-search` | AI Maestro's indexed conversation transcripts | "what did we SAY / discuss / decide?" |
| Markdown note memory | `memory-recall` + `memory-write` | curated, symptom-indexed markdown notes | "what did we LEARN that must not be re-derived?" |

The note memory is the **canonical home of the AI-Maestro memory protocol**
(`rules/memory-protocol.md`): notes are recalled from the SYMPTOM with
[`memgrep`](scripts/memgrep/SKILL.md), a markdown-aware search engine whose
source ships in `scripts/memgrep/`. Install it with:

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
