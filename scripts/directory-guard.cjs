#!/usr/bin/env node
/**
 * Directory Guard Hook — PreToolUse (FAIL-CLOSED)
 *
 * Blocks Write/Edit/Bash operations that target files outside the agent's
 * assigned working directory. This is the enforcement layer for agent
 * sandboxing — it runs even with --dangerously-skip-permissions.
 *
 * SECURITY MODEL:
 *   - FAIL-CLOSED: if work directory cannot be determined → DENY ALL writes.
 *   - AGENT_WORK_DIR env var is the ONLY trusted source of the agent's directory.
 *     CWD is NOT trusted (agent can `cd` anywhere).
 *   - Bash commands are blocked when they contain ANY write-capable pattern
 *     targeting a forbidden path. This is best-effort but covers common vectors.
 *
 * Allowed write paths (when AGENT_WORK_DIR is set):
 *   - $AGENT_WORK_DIR/** (agent's own project)
 *   - /tmp/** and /private/tmp/** (macOS temp)
 *   - $AGENT_WORK_DIR/.claude/** (agent's plugin config)
 *   - ~/.agent-messaging/agents/<agent-name>/** (AMP messaging)
 *
 * Blocked:
 *   - Everything else, including other agents' directories, ~/.aimaestro/,
 *     ~/.claude/plugins/, system dirs, AI Maestro source.
 *
 * Input: JSON on stdin (PreToolUse event from Claude Code)
 * Output: JSON on stdout ({ decision: "allow" } or { decision: "deny", reason: "..." })
 */

const path = require('path');
const os = require('os');

// ============================================================================
// Stdin → evaluate → stdout
// ============================================================================

let input = '';
process.stdin.setEncoding('utf-8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const event = JSON.parse(input);
    const result = evaluateAccess(event);
    process.stdout.write(JSON.stringify(result));
  } catch (err) {
    // Parse error on input → DENY (fail-closed)
    process.stdout.write(JSON.stringify({
      decision: 'deny',
      reason: 'Directory guard: failed to parse hook input — denying by default (fail-closed).'
    }));
  }
});

// ============================================================================
// Main evaluation
// ============================================================================

function evaluateAccess(event) {
  const toolName = event.tool_name || '';
  const toolInput = event.tool_input || {};

  // Only guard write-capable tools
  const WRITE_TOOLS = ['Write', 'Edit', 'NotebookEdit'];
  const isBash = toolName === 'Bash';

  if (!WRITE_TOOLS.includes(toolName) && !isBash) {
    return { decision: 'allow' };
  }

  // ── Resolve agent work directory (ONLY from env var) ───────
  const agentWorkDir = resolveAgentWorkDir();
  if (!agentWorkDir) {
    // FAIL-CLOSED: cannot determine sandbox → block all writes
    return {
      decision: 'deny',
      reason: 'Directory guard: AGENT_WORK_DIR not set — all writes blocked. AI Maestro must set this env var at agent launch.'
    };
  }

  // ── Write/Edit/NotebookEdit: check file_path ──────────────
  if (WRITE_TOOLS.includes(toolName)) {
    const filePath = toolInput.file_path || toolInput.path || '';
    if (!filePath) {
      return {
        decision: 'deny',
        reason: 'Directory guard: write tool called without file_path — blocked.'
      };
    }

    // Resolve symlinks to prevent symlink-escape attacks:
    // Agent creates symlink inside sandbox pointing outside → path.resolve() sees
    // it as inside, but actual write goes outside. realpathSync() follows symlinks.
    let resolved;
    try {
      const fs = require('fs');
      // If file exists, resolve symlinks. If not, resolve the parent dir's symlinks.
      if (fs.existsSync(filePath)) {
        resolved = fs.realpathSync(filePath);
      } else {
        const dir = path.dirname(filePath);
        const base = path.basename(filePath);
        const realDir = fs.existsSync(dir) ? fs.realpathSync(dir) : path.resolve(dir);
        resolved = path.join(realDir, base);
      }
    } catch {
      resolved = path.resolve(filePath);
    }

    if (!isAllowedPath(resolved, agentWorkDir)) {
      return {
        decision: 'deny',
        reason: `Directory guard: write to "${resolved}" blocked. Agent can only write to ${agentWorkDir} or /tmp/.`
      };
    }
    return { decision: 'allow' };
  }

  // ── Bash: scan command for write operations ───────────────
  if (isBash) {
    const command = toolInput.command || '';
    const violations = detectBashWriteTargets(command, agentWorkDir);
    if (violations.length > 0) {
      return {
        decision: 'deny',
        reason: `Directory guard: bash command writes to forbidden path(s): ${violations.join(', ')}. Agent can only write to ${agentWorkDir} or /tmp/.`
      };
    }
    return { decision: 'allow' };
  }

  return { decision: 'allow' };
}

// ============================================================================
// Work directory resolution — ONLY env var, never CWD
// ============================================================================

/**
 * Resolve the agent's working directory from AGENT_WORK_DIR env var ONLY.
 *
 * CWD is NOT trusted because an agent can `cd` to any directory, which
 * would trick CWD-based resolution into expanding the sandbox.
 *
 * Returns null if AGENT_WORK_DIR is not set → triggers fail-closed denial.
 */
function resolveAgentWorkDir() {
  const envDir = process.env.AGENT_WORK_DIR;
  if (envDir && envDir.trim()) {
    return path.resolve(envDir.trim());
  }
  // No trusted source → null → fail-closed
  return null;
}

// ============================================================================
// Path allowlist
// ============================================================================

function isAllowedPath(resolvedPath, agentWorkDir) {
  const home = os.homedir();

  // 1. Inside agent's own directory
  if (isUnder(resolvedPath, agentWorkDir)) {
    return true;
  }

  // 2. /tmp/ and /private/tmp/ (macOS)
  if (isUnder(resolvedPath, '/tmp') || isUnder(resolvedPath, '/private/tmp')) {
    return true;
  }

  // 3. Agent's own .claude/ config inside workDir (redundant with #1 but explicit)
  if (isUnder(resolvedPath, path.join(agentWorkDir, '.claude'))) {
    return true;
  }

  // 4. Agent's own AMP messaging directory (keyed by agent folder name, not CWD)
  const agentName = path.basename(agentWorkDir);
  const ampDir = path.join(home, '.agent-messaging', 'agents', agentName);
  if (isUnder(resolvedPath, ampDir)) {
    return true;
  }

  // Everything else → blocked
  return false;
}

/** True if `child` is `parent` itself or a descendant of `parent`. */
function isUnder(child, parent) {
  return child === parent || child.startsWith(parent + path.sep);
}

// ============================================================================
// Bash command analysis (best-effort, defense-in-depth)
// ============================================================================

/**
 * Detect bash commands that write to forbidden paths.
 *
 * This is NOT a full shell parser — it's a best-effort heuristic that catches
 * the most common write patterns. An attacker with shell access can always
 * find ways around it (eval, aliases, symlinks, etc.). The primary defense
 * is AGENT_WORK_DIR + the Write/Edit tool guards. Bash is secondary.
 *
 * Returns array of forbidden paths found, empty if clean.
 */
function detectBashWriteTargets(command, agentWorkDir) {
  const violations = [];

  // 1. Output redirects: > file, >> file, 2> file, 2>> file, &> file
  const redirectRegex = /(?:&>>?|[12]?>>?)\s*([^\s;|&"']+)/g;
  checkMatches(redirectRegex, command, 1, agentWorkDir, violations);

  // 2. tee: tee [-a] file [file...]
  const teeRegex = /\btee\s+(?:-[ai]\s+)*([^\s;|&"']+)/g;
  checkMatches(teeRegex, command, 1, agentWorkDir, violations);

  // 3. cp/mv: cp [-rfp] source target, mv source target
  //    Last argument is the destination
  const cpMvRegex = /\b(?:cp|mv)\s+(?:-[a-zA-Z]+\s+)*(?:[^\s;|&]+\s+)+([^\s;|&"']+)/g;
  checkMatches(cpMvRegex, command, 1, agentWorkDir, violations);

  // 4. curl/wget output: curl -o file, curl --output file, wget -O file
  const curlOutRegex = /\bcurl\b[^;|&]*?(?:-o|--output)\s+([^\s;|&"']+)/g;
  checkMatches(curlOutRegex, command, 1, agentWorkDir, violations);
  const wgetOutRegex = /\bwget\b[^;|&]*?(?:-O|--output-document)\s+([^\s;|&"']+)/g;
  checkMatches(wgetOutRegex, command, 1, agentWorkDir, violations);

  // 5. Inline Python write: python -c "...open('path'..." or python3 -c
  const pyWriteRegex = /\bpython[23]?\s+-c\s+["'].*?open\s*\(\s*["']([^"']+)["']/g;
  checkMatches(pyWriteRegex, command, 1, agentWorkDir, violations);

  // 6. Inline Node write: node -e "...writeFileSync('path'..." or node -e "...writeFile("
  const nodeWriteRegex = /\bnode\s+-e\s+["'].*?(?:writeFileSync|writeFile)\s*\(\s*["']([^"']+)["']/g;
  checkMatches(nodeWriteRegex, command, 1, agentWorkDir, violations);

  // 7. install/rsync: install [-m...] source dest, rsync ... dest
  const installRegex = /\binstall\s+(?:-[a-zA-Z]+\s+)*(?:[^\s;|&]+\s+)+([^\s;|&"']+)/g;
  checkMatches(installRegex, command, 1, agentWorkDir, violations);

  // 8. dd output: dd ... of=path
  const ddRegex = /\bdd\b[^;|&]*?\bof=([^\s;|&"']+)/g;
  checkMatches(ddRegex, command, 1, agentWorkDir, violations);

  // 9. sed -i (in-place edit): sed -i[backup] ... file
  const sedRegex = /\bsed\s+(?:-[a-zA-Z]*i[^\s]*\s+).*?([^\s;|&"']+)\s*(?:$|[;|&])/g;
  checkMatches(sedRegex, command, 1, agentWorkDir, violations);

  // 10. rm/rmdir: rm [-rf] path (destructive, not write, but equally dangerous)
  const rmRegex = /\b(?:rm|rmdir)\s+(?:-[a-zA-Z]+\s+)*([^\s;|&"']+)/g;
  checkMatches(rmRegex, command, 1, agentWorkDir, violations);

  // 11. chmod/chown: targeting files outside sandbox
  const chmodRegex = /\b(?:chmod|chown)\s+(?:-[a-zA-Z]+\s+)*(?:\S+\s+)+([^\s;|&"']+)/g;
  checkMatches(chmodRegex, command, 1, agentWorkDir, violations);

  // 12. ln -s: creating symlinks that point into the sandbox from outside
  const lnRegex = /\bln\s+(?:-[a-zA-Z]+\s+)*(?:[^\s;|&]+\s+)([^\s;|&"']+)/g;
  checkMatches(lnRegex, command, 1, agentWorkDir, violations);

  return violations;
}

function checkMatches(regex, command, group, agentWorkDir, violations) {
  let match;
  while ((match = regex.exec(command)) !== null) {
    const target = match[group];
    if (target) {
      const resolved = path.resolve(target);
      if (!isAllowedPath(resolved, agentWorkDir)) {
        violations.push(resolved);
      }
    }
  }
}
