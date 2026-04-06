#!/usr/bin/env node
/**
 * Directory Guard Hook — PreToolUse
 *
 * Blocks Write/Edit/Bash operations that target files outside the agent's
 * assigned working directory. This is the enforcement layer for agent
 * sandboxing — it runs even with --dangerously-skip-permissions.
 *
 * Allowed paths:
 *   - Agent's working directory (~/agents/<agent-name>/ or CWD)
 *   - /tmp/ and /private/tmp/ (macOS temp)
 *   - The agent's own .claude/ config (for plugin settings)
 *
 * Blocked paths:
 *   - Other agents' directories (~/agents/<other-agent>/)
 *   - AI Maestro source directory
 *   - System directories (~/.aimaestro/, ~/.claude/plugins/)
 *   - Any path outside the allowed set
 *
 * Input: JSON on stdin (PreToolUse event from Claude Code)
 * Output: JSON on stdout ({ decision: "allow" } or { decision: "deny", reason: "..." })
 */

const path = require('path');
const os = require('os');

// Read stdin
let input = '';
process.stdin.setEncoding('utf-8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const event = JSON.parse(input);
    const result = evaluateAccess(event);
    process.stdout.write(JSON.stringify(result));
  } catch (err) {
    // On error, allow (fail-open to avoid breaking the agent)
    process.stdout.write(JSON.stringify({ decision: 'allow' }));
  }
});

function evaluateAccess(event) {
  const toolName = event.tool_name || '';
  const toolInput = event.tool_input || {};

  // Only guard write-capable tools
  const GUARDED_TOOLS = ['Write', 'Edit', 'NotebookEdit'];
  const isBash = toolName === 'Bash';

  if (!GUARDED_TOOLS.includes(toolName) && !isBash) {
    return { decision: 'allow' };
  }

  // Resolve the agent's working directory
  const agentWorkDir = resolveAgentWorkDir();
  if (!agentWorkDir) {
    // Cannot determine work dir — allow (don't break agents without config)
    return { decision: 'allow' };
  }

  if (GUARDED_TOOLS.includes(toolName)) {
    // Write/Edit/NotebookEdit — check file_path
    const filePath = toolInput.file_path || toolInput.path || '';
    if (!filePath) return { decision: 'allow' };

    const resolved = path.resolve(filePath);
    if (!isAllowedPath(resolved, agentWorkDir)) {
      return {
        decision: 'deny',
        reason: `Directory guard: write to "${resolved}" blocked. Agent "${path.basename(agentWorkDir)}" can only write to its own directory (${agentWorkDir}) or /tmp/.`
      };
    }
    return { decision: 'allow' };
  }

  if (isBash) {
    // For Bash, scan for output redirects targeting forbidden paths
    const command = toolInput.command || '';
    const dangerousPatterns = extractOutputTargets(command);

    for (const target of dangerousPatterns) {
      const resolved = path.resolve(target);
      if (!isAllowedPath(resolved, agentWorkDir)) {
        return {
          decision: 'deny',
          reason: `Directory guard: bash output to "${resolved}" blocked. Agent "${path.basename(agentWorkDir)}" can only write to its own directory or /tmp/.`
        };
      }
    }
    return { decision: 'allow' };
  }

  return { decision: 'allow' };
}

/**
 * Resolve the agent's working directory from environment variables.
 * Priority: AGENT_WORK_DIR > CWD matching ~/agents/<name>/
 */
function resolveAgentWorkDir() {
  // Explicit override
  if (process.env.AGENT_WORK_DIR) {
    return path.resolve(process.env.AGENT_WORK_DIR);
  }

  // Infer from CWD if it's under ~/agents/
  const cwd = process.cwd();
  const agentsBase = path.join(os.homedir(), 'agents');
  if (cwd.startsWith(agentsBase + path.sep) || cwd === agentsBase) {
    // Return the immediate child of ~/agents/ as the agent root
    const relative = path.relative(agentsBase, cwd);
    const agentName = relative.split(path.sep)[0];
    if (agentName) {
      return path.join(agentsBase, agentName);
    }
  }

  // Use CWD as the agent's work directory (for non-standard setups)
  return cwd;
}

/**
 * Check if a path is within the allowed set.
 */
function isAllowedPath(resolvedPath, agentWorkDir) {
  const home = os.homedir();

  // 1. Inside agent's own directory
  if (resolvedPath.startsWith(agentWorkDir + path.sep) || resolvedPath === agentWorkDir) {
    return true;
  }

  // 2. /tmp/ and /private/tmp/ (macOS)
  if (resolvedPath.startsWith('/tmp/') || resolvedPath.startsWith('/private/tmp/') ||
      resolvedPath === '/tmp' || resolvedPath === '/private/tmp') {
    return true;
  }

  // 3. Agent's own .claude/ config in the work dir
  const dotClaude = path.join(agentWorkDir, '.claude');
  if (resolvedPath.startsWith(dotClaude + path.sep) || resolvedPath === dotClaude) {
    return true;
  }

  // 4. Agent's own AMP messaging directory
  const agentName = path.basename(agentWorkDir);
  const ampDir = path.join(home, '.agent-messaging', 'agents', agentName);
  if (resolvedPath.startsWith(ampDir + path.sep) || resolvedPath === ampDir) {
    return true;
  }

  // Everything else is blocked
  return false;
}

/**
 * Extract file paths that a bash command would write to.
 * Looks for output redirects (>, >>), tee, and cp/mv targets.
 */
function extractOutputTargets(command) {
  const targets = [];

  // Output redirects: > file, >> file, 2> file
  const redirectRegex = /(?:>>?|2>>?)\s*([^\s;|&]+)/g;
  let match;
  while ((match = redirectRegex.exec(command)) !== null) {
    targets.push(match[1]);
  }

  // tee command: tee [-a] file
  const teeRegex = /\btee\s+(?:-a\s+)?([^\s;|&]+)/g;
  while ((match = teeRegex.exec(command)) !== null) {
    targets.push(match[1]);
  }

  return targets;
}
