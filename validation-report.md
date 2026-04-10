
============================================================
Plugin Validation Report
============================================================

Summary:
  CRITICAL: 0
  MAJOR:    6
  MINOR:    16
  NIT:      2
  WARNING:  31

Details:
  [WARNING] Unknown manifest field 'displayName' — not part of the Claude Code plugin spec. If used by plugin scripts, consider documenting it. (.claude-plugin/plugin.json)
  [WARNING] Unknown manifest field 'requirements' — not part of the Claude Code plugin spec. If used by plugin scripts, consider documenting it. (.claude-plugin/plugin.json)
  [WARNING] Unknown manifest field 'storage' — not part of the Claude Code plugin spec. If used by plugin scripts, consider documenting it. (.claude-plugin/plugin.json)
  [MINOR] pyproject.toml not found — recommended for Python plugins
  [WARNING] .python-version not found — recommended for reproducible builds
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [WARNING] Command hook timeout is 5ms — very short, may cause premature timeouts (hooks/hooks.json)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/agent-identity/SKILL.md)
  [NIT] Referenced file 'detailed-guide.md' (linked from a list in SKILL.md) has no Table of Contents section. All .md reference files should include a TOC for progressive discovery. (skills/agent-identity/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/agent-messaging/SKILL.md)
  [MAJOR] SKILL.md has 5599 characters (max 5000). Must use progressive disclosure — move content to reference files. (skills/agent-messaging/SKILL.md)
  [NIT] Referenced file 'detailed-guide.md' (linked from a list in SKILL.md) has no Table of Contents section. All .md reference files should include a TOC for progressive discovery. (skills/agent-messaging/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/ai-maestro-agents-management/SKILL.md)
  [WARNING] Link to 'REFERENCE.md' in a list entry of SKILL.md has 5/43 TOC headings embedded. SKILL.md must copy the COMPLETE TOC of each referenced .md file immediately after its link. Any missing TOC entry will never be discovered by the progressive discovery algorithm — that content becomes invisible to agents. If this is a reference, embed all 43 headings. If this is a TOC title, avoid using markdown links to prevent this ambiguity. (skills/ai-maestro-agents-management/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/debug-hooks/SKILL.md)
  [WARNING] Many tools permitted (13) - consider limiting (skills/debug-hooks/SKILL.md)
  [WARNING] Link to 'REFERENCE.md' in a list entry of SKILL.md has 6/8 TOC headings embedded. SKILL.md must copy the COMPLETE TOC of each referenced .md file immediately after its link. Any missing TOC entry will never be discovered by the progressive discovery algorithm — that content becomes invisible to agents. If this is a reference, embed all 8 headings. If this is a TOC title, avoid using markdown links to prevent this ambiguity. (skills/debug-hooks/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/docs-search/SKILL.md)
  [WARNING] Link to 'REFERENCE.md' in a list entry of SKILL.md has 3/8 TOC headings embedded. SKILL.md must copy the COMPLETE TOC of each referenced .md file immediately after its link. Any missing TOC entry will never be discovered by the progressive discovery algorithm — that content becomes invisible to agents. If this is a reference, embed all 8 headings. If this is a TOC title, avoid using markdown links to prevent this ambiguity. (skills/docs-search/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/graph-query/SKILL.md)
  [WARNING] Link to 'REFERENCE.md' in a list entry of SKILL.md has 4/14 TOC headings embedded. SKILL.md must copy the COMPLETE TOC of each referenced .md file immediately after its link. Any missing TOC entry will never be discovered by the progressive discovery algorithm — that content becomes invisible to agents. If this is a reference, embed all 14 headings. If this is a TOC title, avoid using markdown links to prevent this ambiguity. (skills/graph-query/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/mcp-discovery/SKILL.md)
  [WARNING] Link to 'REFERENCE.md' in a list entry of SKILL.md has 3/8 TOC headings embedded. SKILL.md must copy the COMPLETE TOC of each referenced .md file immediately after its link. Any missing TOC entry will never be discovered by the progressive discovery algorithm — that content becomes invisible to agents. If this is a reference, embed all 8 headings. If this is a TOC title, avoid using markdown links to prevent this ambiguity. (skills/mcp-discovery/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/memory-search/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/network-security/SKILL.md)
  [MAJOR] SKILL.md has 7739 characters (max 5000). Must use progressive disclosure — move content to reference files. (skills/network-security/SKILL.md)
  [MAJOR] Required section missing: '## Instructions' (Nixtla strict mode) (skills/network-security/SKILL.md)
  [MAJOR] Required section missing: '## Output' (Nixtla strict mode) (skills/network-security/SKILL.md)
  [MAJOR] Required section missing: '## Examples' (Nixtla strict mode) (skills/network-security/SKILL.md)
  [MAJOR] Required section missing: '## Resources' (Nixtla strict mode) (skills/network-security/SKILL.md)
  [MINOR] No checklist pattern found (best practice: use [ ] / [x] for complex workflows) (skills/network-security/SKILL.md)
  [MINOR] Reference file has no table of contents in the first 200 characters (72 lines): references/REFERENCE.md (skills/network-security/references/REFERENCE.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/planning/SKILL.md)
  [WARNING] Link to 'REFERENCE.md' in a list entry of SKILL.md has 3/13 TOC headings embedded. SKILL.md must copy the COMPLETE TOC of each referenced .md file immediately after its link. Any missing TOC entry will never be discovered by the progressive discovery algorithm — that content becomes invisible to agents. If this is a reference, embed all 13 headings. If this is a TOC title, avoid using markdown links to prevent this ambiguity. (skills/planning/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/team-governance/SKILL.md)
  [WARNING] Link to 'REFERENCE.md' in a list entry of SKILL.md has 5/9 TOC headings embedded. SKILL.md must copy the COMPLETE TOC of each referenced .md file immediately after its link. Any missing TOC entry will never be discovered by the progressive discovery algorithm — that content becomes invisible to agents. If this is a reference, embed all 9 headings. If this is a TOC title, avoid using markdown links to prevent this ambiguity. (skills/team-governance/SKILL.md)
  [MINOR] Non-user-invocable skill should include 'Loaded by <agent-name>' or 'Used by <agent-name>' so it's clear which agent consumes this skill. (skills/team-kanban/SKILL.md)
  [WARNING] Link to 'api-reference.md' in a list entry of SKILL.md has 2/17 TOC headings embedded. SKILL.md must copy the COMPLETE TOC of each referenced .md file immediately after its link. Any missing TOC entry will never be discovered by the progressive discovery algorithm — that content becomes invisible to agents. If this is a reference, embed all 17 headings. If this is a TOC title, avoid using markdown links to prevent this ambiguity. (skills/team-kanban/SKILL.md)
  [WARNING] Link to 'github-sync.md' in a list entry of SKILL.md has 3/16 TOC headings embedded. SKILL.md must copy the COMPLETE TOC of each referenced .md file immediately after its link. Any missing TOC entry will never be discovered by the progressive discovery algorithm — that content becomes invisible to agents. If this is a reference, embed all 16 headings. If this is a TOC title, avoid using markdown links to prevent this ambiguity. (skills/team-kanban/SKILL.md)
  [WARNING] Dead URL (unreachable): <https://api.crabmail.ai> in commands/amp-register.md (commands/amp-register.md)
  [WARNING] Dead URL (unreachable): <https://trycrabmail.com> in commands/amp-register.md (commands/amp-register.md)
  [WARNING] Dead URL (HTTP 404): <https://github.com/23blocks-OS/ai-maestro/blob/main/docs/AGENT-REGISTRY.md> in skills/ai-maestro-agents-management/references/REFERENCE.md (skills/ai-maestro-agents-management/references/REFERENCE.md)
  [WARNING] Dead URL (HTTP 404): <https://github.com/23blocks-OS/ai-maestro/blob/main/docs/PLUGIN-DEVELOPMENT.md> in skills/ai-maestro-agents-management/references/REFERENCE.md (skills/ai-maestro-agents-management/references/REFERENCE.md)
  [WARNING] Possible broken backtick path: `./install-doc-tools.sh` in skills/docs-search/SKILL.md (skills/docs-search/SKILL.md)
  [WARNING] Possible broken backtick path: `./install-memory-tools.sh` in skills/memory-search/SKILL.md (skills/memory-search/SKILL.md)
  [MINOR] Broken backtick path: `scripts/setup-tailscale-serve.sh` in skills/network-security/SKILL.md — file not found in plugin (skills/network-security/SKILL.md)
  [WARNING] No cliff.toml found — recommended for automated changelog generation

------------------------------------------------------------
✗ MAJOR issues found - significant problems
SUMMARY: CRITICAL=0 MAJOR=6 MINOR=16 NIT=2 WARNING=31
