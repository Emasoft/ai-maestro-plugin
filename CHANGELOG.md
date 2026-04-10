# Changelog

All notable changes to this project will be documented in this file.
    ## [2.5.2] - 2026-04-10

### Bug Fixes

- Remove explicit skills array — auto-discovered from standard paths    
- Remove AMP/AID scripts from plugin — scripts live in main repo    
- Update script paths — reference ~/.local/bin/ not plugin scripts/    
- Add frontmatter to all command files, fix plugin.json format    
- Prefix command paths with ./ for CPV validation    
- Remove commands array — auto-discovered from commands/ dir    
- Restructure skills for CPV Nixtla strict mode compliance    
- Use numbered steps in Instructions sections for CPV compliance    
- Resolve 8 MINOR CPV issues — shorter description, checklists, markdown links    
- Add 'Use when'+'Trigger with' phrases, checklist tracking text    
- Rename plugin to ai-maestro-plugin to match GitHub repo name    
- Mention AI Maestro server requirement in description    
- Reference official 23blocks-OS/ai-maestro repo, not fork    
- Set all 11 skills to user-invocable: false    
- Quote user-invocable as string for OpenSpec compliance    
- Use bool (not string) for top-level user-invocable    
- 6 issues — planning user-invocable, jq nesting bug, stale open teams refs, ghost script    
- Remove hardcoded IPs/hostnames from network-security skill — universal guide for all platforms    
- Add title_communication_forbidden to error codes table    
- Correct communication rules in governance skills    
- Register all 10 hook events in hooks.json (7 were missing — dead code)    
- Publish.py runs CPV validation remotely + pre-push enforces --strict    
- Ruff F541 — remove extraneous f-prefix in publish.py    
- Remove CPV_PUBLISH_PIPELINE bypass from pre-push hook — CPV --strict always runs    
- Publish.py + pre-push use cpv-remote-validate via uvx    
- CPV --strict validation — fix all MAJOR/MINOR/NIT issues + publish pipeline    
- Directory-guard hook — update to current PreToolUse output schema    
- Publish.py — make ALL validation steps unskippable (no-skip policy)    
- Add hatch wheel config so uv run doesn't crash on editable install    

### Documentation

- Amp-delete — add text language to fenced code blocks (MD040)    
- Lint fixes on command markdown files (MD031/MD040/MD013/MD060/MD033)    
- Lint cleanup — TOC headings, code fence languages, markdown fixes    

### Features

- Incorporate AMP messaging and AID identity into plugin    
- 8-state agent activity model — SubagentStart/Stop, SessionEnd, errors    
- Add network-security skill + bump to v2.4.0    
- Add title-based communication graph to messaging and governance skills    
- Add smart publish pipeline + pre-push hook enforcement    
- Directory guard hook (PreToolUse) + version bump to 2.5.0    

### Miscellaneous

- Bump version to 2.3.0    
- Bump version to 2.5.1    
- Add permissive markdownlint config    
- Update uv.lock    

### Refactor

- Move all scripts to main repo — plugin keeps only hook + skills + commands    
- Remove dead PermissionRequest handler from hook    

### Security

- Directory guard fail-closed + expanded bash detection    
- Resolve symlinks before path check (anti-symlink escape)    

### Ci

- Strict publish.py with process-ancestry pre-push hook    

### Sync

- Update hook from main repo — restore PermissionRequest handler    


