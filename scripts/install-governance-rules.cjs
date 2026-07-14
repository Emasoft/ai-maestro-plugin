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
 * REFRESH SEMANTICS (issue #16): install-if-missing PLUS a SAFE
 * overwrite-on-version-change. The installer stamps every rule it writes with the
 * sha256 of the exact bytes it installed (in .ai-maestro-governance-stamps.json).
 * On a later session, when the bundled rule has changed, it overwrites the on-disk
 * copy ONLY when that copy is byte-identical to the stamp — i.e. we provably
 * installed it and the user has NOT customized it since. If the on-disk copy
 * differs from our stamp (user edited it) or we hold no stamp for it (we can't
 * prove we installed it), it is PRESERVED untouched.
 *
 * WHY the stamp instead of a plain overwrite: this resolves the #8 ownership
 * concern WITHOUT needing the "who owns these four rules" model settled — we only
 * ever replace bytes we ourselves last wrote and the user left alone, so a
 * customized or third-party copy is never clobbered. Known narrow gap: a rule the
 * PRE-stamp (install-if-missing) installer wrote, that has since diverged from the
 * current bundled version, carries no stamp, so it is preserved (not refreshed) on
 * the first run of this version — the safe choice; it self-heals on the next
 * install (delete → reinstall) and every go-forward bump refreshes normally.
 *
 * Contract: best-effort, never throws into SessionStart, always exits 0, and
 * emits nothing on stdout unless it changed something (a SessionStart hook's
 * stdout is surfaced to the user / parsed as JSON, so silence is the default).
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

const RULES = [
  'trdd-design-tasks.md',
  'trdd-approval-tiers.md',
  'prrd-design-rules.md',
  'manager-approval-defaults.md',
];

const sha256 = (buf) => crypto.createHash('sha256').update(buf).digest('hex');

try {
  const srcDir = path.join(__dirname, '..', 'rules');
  const destDir = path.join(os.homedir(), '.claude', 'rules');
  fs.mkdirSync(destDir, { recursive: true });

  const stampFile = path.join(destDir, '.ai-maestro-governance-stamps.json');
  let stamps = {};
  try { stamps = JSON.parse(fs.readFileSync(stampFile, 'utf8')) || {}; } catch (_e) { stamps = {}; }

  // Atomic write (tmp + rename) so a concurrent reader never sees a partial file.
  const atomicWrite = (dest, buf) => {
    const tmp = `${dest}.tmp.${process.pid}`;
    fs.writeFileSync(tmp, buf);
    fs.renameSync(tmp, dest);
  };

  const installed = [];
  const refreshed = [];
  let stampsChanged = false;

  for (const name of RULES) {
    const src = path.join(srcDir, name);
    const dest = path.join(destDir, name);
    if (!fs.existsSync(src)) continue;            // bundled rule absent — skip
    const srcBuf = fs.readFileSync(src);
    const srcHash = sha256(srcBuf);

    if (!fs.existsSync(dest)) {
      atomicWrite(dest, srcBuf);                  // fresh install
      stamps[name] = srcHash; stampsChanged = true;
      installed.push(name);
      continue;
    }

    const destHash = sha256(fs.readFileSync(dest));
    if (destHash === srcHash) {
      // Already current. Adopt the stamp so a FUTURE bump can safely refresh a
      // copy that currently matches ours byte-for-byte (identical content means
      // there is no user customization to lose).
      if (stamps[name] !== srcHash) { stamps[name] = srcHash; stampsChanged = true; }
      continue;
    }

    // dest differs from the bundled rule. Overwrite ONLY if it is byte-identical
    // to what we last installed (the user has not customized it since).
    if (stamps[name] && destHash === stamps[name]) {
      atomicWrite(dest, srcBuf);                  // safe refresh — ours, unmodified
      stamps[name] = srcHash; stampsChanged = true;
      refreshed.push(name);
    }
    // else: user-modified, third-party, or unprovable ownership → leave untouched.
  }

  if (stampsChanged) {
    try { atomicWrite(stampFile, Buffer.from(JSON.stringify(stamps, null, 2))); } catch (_e) {}
  }

  if (installed.length + refreshed.length > 0) {
    const parts = [];
    if (installed.length) parts.push(`installed ${installed.length} (${installed.join(', ')})`);
    if (refreshed.length) parts.push(`refreshed ${refreshed.length} (${refreshed.join(', ')})`);
    // additionalContext keeps the turn going without a hook-error label (CC 2.1.144).
    process.stdout.write(
      JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'SessionStart',
          additionalContext:
            `ai-maestro-plugin governance rules: ${parts.join('; ')} in ~/.claude/rules/.`,
        },
      })
    );
  }
} catch (_e) {
  // Never break SessionStart on any I/O / permission error.
}
process.exit(0);
