# Fix Log — ai-maestro-plugin — 2026-04-04

## Summary

Fixed 6 MAJOR + 16 MINOR + 2 NIT = 24 issues. 31 WARNINGs skipped (advisory).

---

## MAJOR Issues Fixed (6/6)

### MAJOR-1: agent-messaging/SKILL.md — 5599 chars (max 5000)

- **Fix**: Moved the full communication adjacency matrix table and 6 key-rule
  bullets to `reference/detailed-guide.md`. Replaced with a compact summary
  (~150 chars). New size: 4890 chars.

### MAJOR-2: network-security/SKILL.md — 7739 chars (max 5000)

- **Fix**: Rewrote file with progressive disclosure. Moved platform-specific
  notes, all diagnostics details, and known limitations into
  `references/REFERENCE.md`. New size: 3291 chars.

### MAJOR-3: network-security/SKILL.md — Missing `## Instructions` section

- **Fix**: Added numbered `## Instructions` section with 6 steps covering
  Tailscale setup through mobile access.

### MAJOR-4: network-security/SKILL.md — Missing `## Output` section

- **Fix**: Added `## Output` section describing server logs, tailscale
  status, and lsof output.

### MAJOR-5: network-security/SKILL.md — Missing `## Examples` section

- **Fix**: Added `## Examples` section with bash code blocks for finding
  Tailscale IP, testing connectivity, and checking bind address.

### MAJOR-6: network-security/SKILL.md — Missing `## Resources` section

- **Fix**: Added `## Resources` section linking to `references/REFERENCE.md`
  with embedded TOC of all 6 sections.

---

## MINOR Issues Fixed (16/16)

### MINOR-1: pyproject.toml not found

- **Fix**: Created `/tmp/ai-maestro-plugin/pyproject.toml` with project
  metadata, Python 3.12 requirement, and dev extras (ruff, pytest).

### MINOR-2 through MINOR-13: Non-user-invocable skills missing "Loaded by" text

All 12 SKILL.md files had `user-invocable: false` but lacked consumer
identification text.

- **Fix**: Added `Loaded by ai-maestro-plugin main agents.` line before the
  `# <Skill Name>` heading in all 12 files:

  - `skills/agent-identity/SKILL.md`
  - `skills/agent-messaging/SKILL.md`
  - `skills/ai-maestro-agents-management/SKILL.md`
  - `skills/debug-hooks/SKILL.md`
  - `skills/docs-search/SKILL.md`
  - `skills/graph-query/SKILL.md`
  - `skills/mcp-discovery/SKILL.md`
  - `skills/memory-search/SKILL.md`
  - `skills/network-security/SKILL.md`
  - `skills/planning/SKILL.md`
  - `skills/team-governance/SKILL.md`
  - `skills/team-kanban/SKILL.md`

### MINOR-14: network-security — broken backtick path reference

- **Fix**: Removed the broken `scripts/setup-tailscale-serve.sh` reference in
  the rewrite. The note about setup-tailscale-serve.sh was relocated to
  REFERENCE.md context without the broken path.

### MINOR-15: network-security/references/REFERENCE.md — No TOC in first 200 chars

- **Fix**: Added `## Table of Contents` section with 6 anchor links
  immediately after the `# Network Security Reference` heading.

### MINOR-16: network-security/SKILL.md — No checklist pattern

- **Fix**: Added a checklist with 4 items in the `## Prerequisites` section.

---

## NIT Issues Fixed (2/2)

### NIT-1: agent-identity/SKILL.md — detailed-guide.md link has no TOC embedded

- **Fix**: Added all 9 section headings from `reference/detailed-guide.md`
  as indented bullets under the link in `## Resources`.

### NIT-2: agent-messaging/SKILL.md — detailed-guide.md link has no TOC embedded

- **Fix**: Added all 14 section headings from `reference/detailed-guide.md`
  as indented bullets under the link in `## Resources`.

---

## Files Modified

| File                                  | Changes                        |
|---------------------------------------|--------------------------------|
| `agent-identity/SKILL.md`             | "Loaded by"; 9-entry TOC       |
| `agent-messaging/SKILL.md`            | "Loaded by"; reduced to 4890   |
| `ai-maestro-agents-management/SKILL`  | "Loaded by"                    |
| `debug-hooks/SKILL.md`                | "Loaded by"; 8-entry TOC       |
| `docs-search/SKILL.md`                | "Loaded by"                    |
| `graph-query/SKILL.md`                | "Loaded by"                    |
| `mcp-discovery/SKILL.md`              | "Loaded by"                    |
| `memory-search/SKILL.md`              | "Loaded by"                    |
| `network-security/SKILL.md`           | Rewrite: 7757→3291, 4 sections |
| `network-security/references/REF.md`  | Added TOC in first 200 chars   |
| `planning/SKILL.md`                   | "Loaded by"                    |
| `team-governance/SKILL.md`            | "Loaded by"                    |
| `team-kanban/SKILL.md`                | "Loaded by"                    |
| `pyproject.toml`                      | Created                        |

All files are under `skills/` except `pyproject.toml` at repo root.

---

## WARNINGs Skipped (31)

Advisory only — do not block push. Includes: unknown manifest fields
(displayName, requirements, storage), hook timeout warnings, dead URLs,
partial TOC embeddings in WARNING-severity items, missing .python-version,
missing cliff.toml.
