#!/usr/bin/env node
/*
 * install-governance-rules.cjs — SessionStart hook (ai-maestro-plugin).
 *
 * Fleet-readiness "fool-proof rule injection" (MANAGER design TRDD-f5883dcc,
 * issue #8): the core plugin bundles the four AI-Maestro governance rules and
 * makes them present in EVERY agent's context by installing them into
 * ~/.claude/rules/ at session start — the same proven mechanism the janitor
 * uses for markdown-memory-recall.md.
 *
 * SAFETY (deliberate): this v1 is INSTALL-IF-MISSING — it writes a bundled rule
 * only when the destination file does not exist. It NEVER overwrites a rule the
 * user (or another plugin) already placed, so it cannot clobber a customized or
 * newer copy, nor propagate any local drift. This guarantees the design's core
 * invariant ("a fresh agent on a clean machine gets the rules") with zero risk.
 * Overwrite-on-version-bump (keeping installed rules current) is a deliberate
 * follow-up pending the MANAGER's confirmation of the rule-ownership model
 * (who owns these four rules and may overwrite a user's copy) — see #8.
 *
 * Contract: best-effort, never throws into SessionStart, always exits 0, and
 * emits nothing on stdout unless it installed something (a SessionStart hook's
 * stdout is surfaced to the user / parsed as JSON, so silence is the default).
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const RULES = [
  'trdd-design-tasks.md',
  'trdd-approval-tiers.md',
  'prrd-design-rules.md',
  'manager-approval-defaults.md',
];

try {
  const srcDir = path.join(__dirname, '..', 'rules');
  const destDir = path.join(os.homedir(), '.claude', 'rules');
  fs.mkdirSync(destDir, { recursive: true });

  const installed = [];
  for (const name of RULES) {
    const src = path.join(srcDir, name);
    const dest = path.join(destDir, name);
    if (!fs.existsSync(src)) continue;        // bundled rule absent — skip
    if (fs.existsSync(dest)) continue;        // already present — never clobber
    // Atomic-ish write: tmp then rename, so a concurrent reader never sees a partial file.
    const tmp = `${dest}.tmp.${process.pid}`;
    fs.writeFileSync(tmp, fs.readFileSync(src));
    fs.renameSync(tmp, dest);
    installed.push(name);
  }

  if (installed.length > 0) {
    // additionalContext keeps the turn going without a hook-error label (CC 2.1.144).
    process.stdout.write(
      JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'SessionStart',
          additionalContext:
            `ai-maestro-plugin installed ${installed.length} governance rule(s) ` +
            `into ~/.claude/rules/ (${installed.join(', ')}).`,
        },
      })
    );
  }
} catch (_e) {
  // Never break SessionStart on any I/O / permission error.
}
process.exit(0);
