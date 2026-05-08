# TRDD-9a8aba94-b5d7-4d48-b05f-bdbd72295a13 — Reconcile `amp-send` vs `amp-send.sh` CLI naming

**TRDD ID:** `9a8aba94-b5d7-4d48-b05f-bdbd72295a13`
**Filename:** `design/tasks/TRDD-9a8aba94-b5d7-4d48-b05f-bdbd72295a13-amp-send-vs-amp-send-sh-cli.md`
**Tracked in:** this repo (design/tasks/ is git-tracked)
**Source audit:** `reports/v258-pre-publish-audit/skill-content-audit.md` (A11.2)
**Severity:** HIGH (CLI consistency / docs drift)
**Status:** Not started
**Filed:** 2026-05-08

## Problem

Two skills teach two different CLI names for the same operation:

- `skills/agent-messaging/SKILL.md` — uses `amp-send.sh`, `amp-inbox.sh`,
  `amp-read.sh` (with `.sh` extension) throughout. allowed-tools is
  `Bash(amp-*:*)` (glob, accepts both forms).
- `skills/team-governance/SKILL.md` — uses bare `amp-send`,
  `amp-inbox` (no `.sh`) in its Instructions example. allowed-tools is
  `Bash(amp-send:*), Bash(amp-inbox:*)` (bare-name only).

**Verification (2026-05-08):** Both binaries DO exist on disk in
`~/.local/bin/`:

```
amp-send
amp-send.sh
amp-inbox
amp-inbox.sh
```

The bare `amp-send` is a wrapper. So both forms run. The issue is
**documentation consistency**, not a runtime bug — but a casual reader
moving between the two skills sees inconsistent guidance.

## Design

### Approach 1 — Pick `.sh` as the canonical name, document the wrapper

- Rationale: agent-messaging is the canonical AMP skill (12+ commands
  documented). team-governance only mentions amp-send/amp-inbox as
  ancillary broadcast helpers.
- Changes:
  - team-governance/SKILL.md: change examples to `amp-send.sh ...`
    and `amp-inbox.sh ...`.
  - team-governance/SKILL.md `allowed-tools`: switch from
    `Bash(amp-send:*), Bash(amp-inbox:*)` to `Bash(amp-*:*)` (glob,
    matches what agent-messaging uses).
  - Document in `agent-messaging/reference/detailed-guide.md`: bare
    `amp-send` exists as a convenience wrapper; both forms are
    equivalent.

### Approach 2 — Pick bare names as canonical (drop `.sh`)

- Rationale: bare names are more idiomatic CLI UX (cf. `git`, not
  `git.sh`). Modern POSIX tools rarely keep `.sh` extensions on
  user-facing wrappers.
- Changes: opposite of Approach 1. Sweep agent-messaging (and the
  detailed-guide, install-messaging.sh docs) to drop `.sh`.
- Cost: bigger sweep, touches more files, risk of breaking external
  documentation that points at the agentmessaging.org spec.

## Recommendation

**Approach 1.** Smaller surface area, doesn't touch the canonical AMP
skill, doesn't risk breaking links to the agentmessaging.org
specification (which uses `.sh`).

## Acceptance criteria

- [ ] team-governance/SKILL.md Instructions example uses `amp-send.sh`
  and `amp-inbox.sh`
- [ ] team-governance/SKILL.md allowed-tools is `Bash(amp-*:*)` (glob)
- [ ] team-governance/SKILL.md remains within 5000-char CPV ceiling
- [ ] agent-messaging/reference/detailed-guide.md adds a one-line note
  documenting the bare-name wrapper
- [ ] CPV strict still PASS

## Dependencies

- None.

## Out of scope

- install-messaging.sh changes (the install script already creates
  both forms; no change needed)
- Renaming the binaries themselves (would break every existing user's
  shell history and shell scripts; not worth it)
