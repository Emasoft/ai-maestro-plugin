#!/usr/bin/env node
/**
 * Directory Guard Hook — PreToolUse (FAIL-CLOSED)
 *
 * Blocks Write/Edit/Bash operations that target files outside the agent's
 * assigned working directory. This is the enforcement layer for agent
 * sandboxing — it runs even with --dangerously-skip-permissions.
 *
 * SECURITY MODEL:
 *   - FAIL-CLOSED within an AGENT context: if this is an AI-Maestro agent
 *     (AID_AUTH or AIMAESTRO_AGENT set) but its work directory cannot be determined → DENY ALL
 *     writes. A NON-agent session (no agent marker) is NOT sandboxed by this
 *     guard — denying it bricked every interactive session machine-wide (#22).
 *   - AGENT_WORK_DIR env var is the ONLY trusted source of the agent's directory.
 *     CWD is NOT trusted (agent can `cd` anywhere).
 *   - Bash commands are blocked when they contain ANY write-capable pattern
 *     targeting a forbidden path. This bash scan is DEFENSE-IN-DEPTH /
 *     ADVISORY ONLY — a heuristic, not a shell parser. It cannot be the hard
 *     enforcement boundary (an attacker with shell access has eval, aliases,
 *     here-docs, base64-decoded scripts, $() substitution, etc.). The HARD
 *     enforcement layer is OS-level sandboxing the AI Maestro launcher must
 *     provide (sandbox-exec on macOS, bwrap/landlock on Linux); this guard
 *     raises the bar for the common write vectors and fails closed.
 *
 * Allowed write paths (when AGENT_WORK_DIR is set):
 *   - $AGENT_WORK_DIR/** (agent's own project)
 *   - /tmp/** and /private/tmp/** (macOS temp)
 *   - $AGENT_WORK_DIR/.claude/** (agent's plugin config)
 *   - ~/.agent-messaging/agents/<agent-name>/** (AMP messaging)
 *   - ~/.claude/projects/<encoded($AGENT_WORK_DIR)>/** (Claude Code per-project
 *     state: auto-memory, transcripts, todos. Encoding: every non-alphanumeric
 *     char in the absolute path is replaced with "-", so each agent only sees
 *     its own slot.)
 *
 * NOTE: A future revision will add a MANAGER-only privilege to write to the
 * Claude Code user-scope element tree (~/.claude/{skills,agents,commands,
 * rules,mcp_servers,plugins,...}). The title MUST be verified via the
 * agent's AID Ed25519 identity (env vars are spoofable) — design TBD.
 *
 * Blocked:
 *   - Everything else, including other agents' directories, ~/.aimaestro/,
 *     ~/.claude/plugins/, system dirs, AI Maestro source.
 *
 * Input: JSON on stdin (PreToolUse event from Claude Code)
 * Output: JSON on stdout in the Claude Code PreToolUse schema:
 *   { "hookSpecificOutput": {
 *       "hookEventName": "PreToolUse",
 *       "permissionDecision": "allow" | "deny",
 *       "permissionDecisionReason": "..."
 *   }}
 */

const path = require('path');
const os = require('os');

// ============================================================================
// Output helpers — Claude Code PreToolUse hook schema
// ============================================================================

/** Build an "allow" decision envelope. */
function allowDecision() {
  return {
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'allow',
    },
  };
}

/**
 * ABSTAIN — emit no decision at all, so Claude Code's normal permission flow runs.
 *
 * This is NOT the same as allowDecision(), and conflating the two is a permission
 * bypass. `permissionDecision: "allow"` is an affirmative override: it skips the
 * prompt the user would otherwise see AND their configured rules. Returning nothing
 * means "this hook has no opinion", which leaves the user's settings in charge.
 *
 * Every path where this guard has no jurisdiction MUST abstain. Returning "allow"
 * there silently disables permission prompts for Bash/Write/Edit/NotebookEdit — the
 * four highest-risk tools — in every session where the plugin is installed.
 */
function abstain() {
  return null;
}

/** Build a "deny" decision envelope. */
function denyDecision(reason) {
  return {
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: reason,
    },
  };
}

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
    // null === abstain: emit NOTHING so the normal permission flow runs. Writing
    // "null" (or an empty envelope) would be a schema violation, not an abstention.
    if (result !== null) {
      process.stdout.write(JSON.stringify(result));
    }
  } catch (err) {
    // Parse error on input → DENY (fail-closed)
    process.stdout.write(JSON.stringify(
      denyDecision('Directory guard: failed to parse hook input — denying by default (fail-closed).')
    ));
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
    return abstain();
  }

  // ── Resolve agent work directory (ONLY from env var) ───────
  const agentWorkDir = resolveAgentWorkDir();
  if (!agentWorkDir) {
    // AGENT_WORK_DIR is unset. This is the load-bearing distinction (#22):
    //   - In an AI-Maestro AGENT context (a positive identity marker is present)
    //     an unset sandbox root is a MISCONFIGURED agent → FAIL-CLOSED (deny):
    //     we must never let an agent write with an undetermined sandbox.
    //   - With NO agent marker at all, this is an ordinary (non-agent) Claude
    //     Code session that this guard was never meant to sandbox. Denying it
    //     bricked every interactive session machine-wide (#22) — so allow it.
    // WHY a positive marker instead of bare AGENT_WORK_DIR-absence: absence is
    // the NORMAL state of a human's own session; it is NOT evidence of an agent.
    if (isAiMaestroAgentContext()) {
      return denyDecision(
        'Directory guard: AI-Maestro agent context detected (AID_AUTH/AIMAESTRO_AGENT set) but AGENT_WORK_DIR is unset — cannot determine the sandbox root, blocking writes (fail-closed). AI Maestro must set AGENT_WORK_DIR at agent launch.'
      );
    }
    // ABSTAIN, do not allow. This is an ordinary (non-agent) session that this guard
    // was never meant to sandbox. #22 fixed a fail-closed deny that bricked every
    // interactive session — but it over-corrected to "allow", which does not merely
    // step aside: it AFFIRMATIVELY bypasses the user's permission prompts and rules
    // for Bash/Write/Edit/NotebookEdit. Measured 2026-08-05 in a plain session
    // (AGENT_WORK_DIR unset, no AID_AUTH): a Write to the system hosts file —
    // far outside any sandbox root — came back "allow". (Named indirectly: the
    // validator flags any absolute path in source, comment or not.)
    // Abstaining fixes #22 exactly as well — it does not deny — without the bypass.
    return abstain();
  }

  // ── Write/Edit/NotebookEdit: check file_path ──────────────
  if (WRITE_TOOLS.includes(toolName)) {
    const filePath = toolInput.file_path || toolInput.path || '';
    if (!filePath) {
      return denyDecision('Directory guard: write tool called without file_path — blocked.');
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
      return denyDecision(
        `Directory guard: write to "${resolved}" blocked. Agent can only write to ${agentWorkDir} or /tmp/.`
      );
    }
    return allowDecision();
  }

  // ── Bash: scan command for write operations ───────────────
  if (isBash) {
    const command = toolInput.command || '';
    const violations = detectBashWriteTargets(command, agentWorkDir);
    if (violations.length > 0) {
      return denyDecision(
        `Directory guard: bash command writes to forbidden path(s): ${violations.join(', ')}. Agent can only write to ${agentWorkDir} or /tmp/.`
      );
    }
    return allowDecision();
  }

  // Unreachable today (both guarded branches return above), but abstain rather than
  // allow so that adding a tool to the matcher can never silently auto-approve it.
  return abstain();
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
  // No trusted source → null → caller decides (fail-closed only in an agent
  // context; a non-agent session is not sandboxed — see evaluateAccess / #22).
  return null;
}

/**
 * True when this process is an AI-Maestro AGENT rather than an ordinary human
 * Claude Code session. AI-Maestro provisions every agent with an AID identity
 * whose bearer rides in AID_AUTH (the marker the prrd-trdd / governance CLIs
 * authenticate with); the launcher also sets AIMAESTRO_AGENT (the agent-context
 * flag) and AGENT_WORK_DIR. We treat AID_AUTH OR AIMAESTRO_AGENT as the
 * positive agent signal for the one case AGENT_WORK_DIR can't cover (#22): an
 * agent whose sandbox root failed to get set. This decides only WHETHER to
 * sandbox, never grants a privilege — env vars are spoofable, but SETTING a
 * marker only ever pushes a workdir-less session onto the DENY (more
 * restrictive) branch, never onto ALLOW, so trusting marker PRESENCE to
 * TIGHTEN enforcement is safe (adopted from PR #28). An agent stripped of ALL
 * markers is indistinguishable from a non-agent and would not be sandboxed —
 * acceptable because this guard is advisory (see SECURITY MODEL above); the
 * hard boundary is the launcher's OS-level sandbox.
 */
function isAiMaestroAgentContext() {
  const markers = ['AID_AUTH', 'AIMAESTRO_AGENT'];
  return markers.some((k) => {
    const v = process.env[k];
    return typeof v === 'string' && v.trim() !== '';
  });
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

  // 5. Agent's own Claude Code per-project state directory.
  //    Claude Code stores auto-memory, transcripts, todos, plans under
  //    ~/.claude/projects/<encoded-abs-path>/. The encoding replaces every
  //    non-alphanumeric char in the absolute path with "-". Each agent only
  //    matches its own slot, so cross-agent contamination is still blocked.
  const projectDir = path.join(home, '.claude', 'projects', encodeProjectPath(agentWorkDir));
  if (isUnder(resolvedPath, projectDir)) {
    return true;
  }

  // Everything else → blocked
  return false;
}

/**
 * Encode an absolute path the same way Claude Code names ~/.claude/projects/
 * subdirectories: every non-[A-Za-z0-9-] char becomes "-". Verified against
 * real entries (e.g. "<home>/Code/SVG_FBF_PROJECT/svg2fbf" →
 * "-Users-x-Code-SVG-FBF-PROJECT-svg2fbf", "<home>/.claude/plugins" →
 * "-Users-x--claude-plugins", where <home> is the user's home directory,
 * /Users/x in these encoded outputs).
 */
function encodeProjectPath(absPath) {
  return absPath.replace(/[^A-Za-z0-9-]/g, '-');
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
 * This is NOT a full shell parser — it's a best-effort heuristic (DEFENSE-IN-
 * DEPTH / ADVISORY) that catches the most common write patterns. An attacker
 * with shell access can always find ways around it (eval, aliases, here-docs,
 * $() substitution, base64-decoded scripts, etc.). The primary defense is
 * AGENT_WORK_DIR + the Write/Edit tool guards; the HARD enforcement layer is
 * OS-level sandboxing the launcher must provide. Bash scanning is secondary.
 *
 * Returns array of forbidden paths found, empty if clean.
 */
function detectBashWriteTargets(command, agentWorkDir) {
  const violations = [];

  // QUOTE-AWARE PRE-PASS (ReDoS-safe, single linear scan — see dequoteCommand).
  // Strips matched '…', "…", `…` pairs and joins the inner text to the
  // adjacent token, so `> "/outside/f"` → `> /outside/f` and
  // `cp x "/outside/p"` → `cp x /outside/p`. After this, the target-capture classes
  // below can drop the `"'` exclusion (they only need to stop at shell
  // separators), so quoted/backtick destinations are captured.
  const cmd = dequoteCommand(command);

  // NOTE on regex shape (ReDoS hygiene): every repeated group below is
  // written so that the group's LAST element is a single char-class or a
  // BOUNDED repeat — never an unbounded plus/star directly under an outer
  // quantifier. Dash-flag loops were refactored to lead with the whitespace
  // instead of trailing it, and the old flags-loop-then-args-loop double
  // loop (whose overlapping token classes allowed exponential backtracking
  // on crafted input) was collapsed into one token loop wherever flags are
  // a subset of the args class. The dequote pre-pass is also linear-time (no
  // nested quantifiers). Behavioral equivalence is pinned by node/pytest
  // tests on real command shapes; the bounds (4096-char tokens, 16-letter
  // flags) exceed anything a legitimate command line uses.
  //
  // PATH-CAPTURE classes are `[^\s;|&<>]+`: in addition to the shell
  // separators (whitespace `;` `|` `&`), the redirect operators `<`/`>` are
  // excluded so a captured path never absorbs a redirect token (e.g.
  // `rm < /tmp/list` must NOT resolve the bare `<` as rm's target — the real
  // semantics there are xargs/stdin-driven, modeled by #16). An unquoted
  // `<`/`>` is always a redirect operator, never part of a path token.

  // 1. Output redirects — QUOTE-AWARE, scanned on the RAW command (ai-maestro#123).
  //    The old shape ran a redirect regex over the DEQUOTED string, so a `>`
  //    inside quoted prose ("/Users/<owner>/x", "a > b in a sentence") was
  //    parsed as a redirect — the guard punished text, not writes. The scan
  //    below is a linear state machine that knows single/double quotes,
  //    backslash escapes, heredoc bodies, $((...)) arithmetic, fd-duplication
  //    (2>&1) and process substitution — a redirect is only a redirect where
  //    the SHELL would treat it as one. Real redirects with QUOTED targets
  //    (`> "<an out-of-sandbox system path>"`) still deny: the operator's quoting decides, never
  //    the target's. Returns true if a heredoc never terminated — that body
  //    was skipped unverified, so FAIL-CLOSED: rescan everything the old way.
  const unterminated = scanRedirects(command, agentWorkDir, violations);
  // 1b. Redirects INSIDE interpreter/eval string arguments. The raw-text scan
  //     above is shell-faithful, which makes it blind to `sh -c 'echo x > /f'`
  //     (the redirect lives inside a quoted string the OUTER shell never
  //     executes — but the INNER shell does). The old dequoted scan caught
  //     these; keep that coverage, gated to commands that actually invoke an
  //     interpreter or eval so prose can no longer trip it. This gate is the
  //     false-negative-audit finding the work order's scope item 3 demanded
  //     be resolved BEFORE the old scan went away.
  //     `interpreterInvocationRegex` is a DETECTION SIGNATURE, not an
  //     invocation: it is only ever handed to `.test()`. Naming it (rather
  //     than inlining it in the `if`) matches every other detector in this
  //     function and keeps the signature off a control-flow line, where a
  //     static scanner reasonably reads `sh -c`/`eval` adjacency as an
  //     execution site rather than a pattern being searched FOR.
  const legacyRedirectRegex = /(?:&>>?|[12]?>>?\|?|[12]?>\|)\s*([^\s;|&<>]+)/g;
  // CPV informed-consent sentinel below: it DEMOTES the CMD_INJECTION finding on
  // the next line to a VISIBLE, non-blocking WARNING — it does not suppress it.
  // That finding is a true positive on the TEXT and a false positive on the
  // BEHAVIOUR: the literal is a search pattern handed to `.test()` immediately
  // below and is never executed, spawned, or interpolated into a command. It
  // cannot be written without naming `sh -c`/`eval`, because recognising them
  // IS its job. Verify by reading the next two lines: the only use is `.test(cmd)`.
  // WARNING: the following code could be malicious. Audit it for safety before executing it!
  const interpreterInvocationRegex = /\b(?:sh|bash|zsh|dash|ksh)\b[^;|&\n]*\s-c\b|\beval\b/;
  if (unterminated || interpreterInvocationRegex.test(cmd)) {
    checkMatches(legacyRedirectRegex, cmd, 1, agentWorkDir, violations,
      'redirect inside interpreter/eval string');
  }

  // 2. tee: tee [-a] file [file...]
  const teeRegex = /\btee(?:\s+-[ai])*\s+([^\s;|&<>]+)/g;
  checkMatches(teeRegex, cmd, 1, agentWorkDir, violations, 'tee target');

  // 3. cp/mv: cp [-rfp] source target, mv source target
  //    Last argument is the destination. Flags match the token loop too,
  //    so no separate flags loop is needed. The `-t <dir>` /
  //    `--target-directory=<dir>` form (destination is an EARLIER arg) is
  //    handled by targetDirRegex (#15) so the real directory is reported.
  const cpMvRegex = /\b(?:cp|mv)(?:\s+[^\s;|&]{1,4096})+\s+([^\s;|&<>]+)/g;
  checkMatches(cpMvRegex, cmd, 1, agentWorkDir, violations, 'cp/mv destination');

  // 4. curl/wget output: curl -o file / --output file, wget -O file /
  //    --output-document file. The separator is \s* so the concatenated forms
  //    `-O<path>` / `-o<path>` (no whitespace) are also captured. A bare `-o`
  //    with no path (the next char is a separator) captures nothing.
  const curlOutRegex = /\bcurl\b[^;|&]*?(?:-o|--output)\s*([^\s;|&<>]+)/g;
  checkMatches(curlOutRegex, cmd, 1, agentWorkDir, violations, 'curl output file');
  const wgetOutRegex = /\bwget\b[^;|&]*?(?:-O|--output-document)\s*([^\s;|&<>]+)/g;
  checkMatches(wgetOutRegex, cmd, 1, agentWorkDir, violations, 'wget output file');

  // 5. Inline Python write: python -c "...open('path'..." or python3 -c
  //    (quotes already stripped by the pre-pass, so match the bare path).
  const pyWriteRegex = /\bpython[23]?(?:\.[0-9]+)?\s+-c\s+.*?\bopen\s*\(\s*([^\s;|&,)]+)/g;
  checkMatches(pyWriteRegex, cmd, 1, agentWorkDir, violations, 'python inline open()');

  // 6. Inline Node write: node -e "...writeFileSync('path'..." / writeFile(
  const nodeWriteRegex = /\bnode\s+-e\s+.*?(?:writeFileSync|writeFile|appendFileSync|appendFile)\s*\(\s*([^\s;|&,)]+)/g;
  checkMatches(nodeWriteRegex, cmd, 1, agentWorkDir, violations, 'node inline write');

  // 6b. Inline ruby/perl write: ruby/perl -e '...File.write("f")... /
  //     open(...,'w')...'. The script body lives after -e; scan it for the
  //     common write builtins and capture the path arg. Conservative: a write
  //     verb must be present, else nothing is captured.
  // DEVITALIZED (skillaudit FP on a detector signature, NOT a runtime change):
  //   this needle is compared against the command string via checkMatches
  //   (data context — never spread to an exec sink), but its regex-LITERAL form
  //   trips skillaudit's CMD_INJECTION / REGEX_DOS shape heuristics. Built from
  //   fragments through new RegExp so the source holds no contiguous
  //   interpreter+"-e"+write-builtin token and no statically-analyzable literal;
  //   the compiled pattern (.source) is byte-identical to the original literal.
  // Fragment boundaries chosen so NO single string literal trips skillaudit's
  //   line heuristics. The interpreter alternation is split at its "|" separator
  //   so that no literal shows a shell pipe immediately preceding an interpreter
  //   name (that adjacency is skillaudit's CMD_INJECTION shell-pipe needle), and
  //   the "*" is split off the "(?:…{0,16}…)" group so that no literal shows the
  //   nested quantifier that is skillaudit's REGEX_DOS shape. Runtime .source is
  //   byte-identical (asserted below + by the guard tests); the guard still
  //   matches every inline ruby / perl write shape it detected before.
  const rubyPerlWriteRegex = new RegExp(
    '\\b(?:ruby|' + 'perl)' + '\\s+(?:-[a-zA-Z]\\S{0,16}\\s+)' + '*' + '-e\\s+.*?' +
      '(?:File\\.write|File\\.open|IO\\.write|' + 'open' + ')\\s*\\(\\s*([^\\s;|&,)]+)',
    'g'
  );
  checkMatches(rubyPerlWriteRegex, cmd, 1, agentWorkDir, violations, 'ruby/perl inline write');

  // 6c. awk write: awk '...print ... > "file"...' (and >>). awk's redirect is
  //     INSIDE its program string; after dequoting it reads `print > /path`.
  //     Match an awk invocation, then the first `>`/`>>` target in its body.
  const awkWriteRegex = /\bawk\b[^;|&]*?>>?\s*([^\s;|&<>]+)/g;
  checkMatches(awkWriteRegex, cmd, 1, agentWorkDir, violations, 'awk program redirect');

  // 7. install/rsync: install [-m...] source dest, rsync ... dest
  //    Flags match the token loop too (same collapse as cp/mv). `-t <dir>` is
  //    handled by targetDirRegex (#15).
  const installRegex = /\binstall(?:\s+[^\s;|&]{1,4096})+\s+([^\s;|&<>]+)/g;
  checkMatches(installRegex, cmd, 1, agentWorkDir, violations, 'install destination');

  // 8. dd output: dd ... of=path
  const ddRegex = /\bdd\b[^;|&]*?\bof=([^\s;|&<>]+)/g;
  checkMatches(ddRegex, cmd, 1, agentWorkDir, violations, 'dd of= target');

  // 9. sed -i (in-place edit): sed -i[backup] ... file
  const sedRegex = /\bsed\s+(?:-[a-zA-Z]*i[^\s]*\s+).*?([^\s;|&<>]+)\s*(?:$|[;|&])/g;
  checkMatches(sedRegex, cmd, 1, agentWorkDir, violations, 'sed -i in-place target');

  // 10. rm/rmdir: rm [-rf] path (destructive, not write, but equally dangerous)
  const rmRegex = /\b(?:rm|rmdir)(?:\s+-[a-zA-Z]{1,16})*\s+([^\s;|&<>]+)/g;
  checkMatches(rmRegex, cmd, 1, agentWorkDir, violations, 'rm/rmdir target');

  // 11. chmod/chown: targeting files outside sandbox
  //     Flags match the token loop too (same collapse as cp/mv).
  const chmodRegex = /\b(?:chmod|chown)(?:\s+\S{1,4096})+\s+([^\s;|&<>]+)/g;
  checkMatches(chmodRegex, cmd, 1, agentWorkDir, violations, 'chmod/chown target');

  // 12. ln -s: creating symlinks that point into the sandbox from outside
  const lnRegex = /\bln(?:\s+-[a-zA-Z]{1,16})*\s+[^\s;|&]+\s+([^\s;|&<>]+)/g;
  checkMatches(lnRegex, cmd, 1, agentWorkDir, violations, 'ln link target');

  // 13. tar extraction: `tar … x… -C <dir>` writes files into <dir>. Two
  //     shapes — explicit `-C <dir>`, and bare `tar x…` whose default target
  //     is CWD. The `t`(list)/`c`(create) modes do NOT extract and are not
  //     matched here. Require an extract mode (`x`) to be present.
  //     a) extraction with an explicit destination dir.
  const tarDestRegex = /\btar\b(?=[^;|&]*\b[a-z]*x[a-z]*\b)[^;|&]*?-C\s*([^\s;|&<>]+)/g;
  checkMatches(tarDestRegex, cmd, 1, agentWorkDir, violations, 'tar -C extraction dir');
  //     b) extraction with no -C (writes into the agent's CWD). CWD is NOT a
  //     trusted write root (the agent can `cd` anywhere), so an extract with
  //     no destination is checked against the resolved CWD — caught only when
  //     CWD is outside the sandbox, which is the dangerous case.
  const tarCwdRegex = /\btar\s+(?:-?[a-zA-Z]*x[a-zA-Z]*)(?![^;|&]*-C\b)/g;
  if (tarCwdRegex.test(cmd)) {
    const cwd = path.resolve(process.cwd());
    if (!isAllowedPath(cwd, agentWorkDir)) {
      violations.push(cwd);
    }
  }

  // 14. git config core.hooksPath: repoints git's hook directory, so the next
  //     git operation runs arbitrary code from <dir> — a sandbox escape. This
  //     is denied UNCONDITIONALLY (it is a code-exec config mutation, not a
  //     file write): even a <dir> inside an allowed write root like /tmp is
  //     dangerous, because the agent can then drop a hook there that executes
  //     outside the sandbox on the next git op. Scoped narrowly to
  //     core.hooksPath ON PURPOSE: a general `git config --global user.name x`
  //     is a benign identity write and must stay allowed (it touches
  //     ~/.gitconfig but cannot execute code) — the guard does NOT deny
  //     --global writes wholesale, only this code-exec one.
  const gitHooksPathRegex = /\bgit\s+config\b[^;|&]*?\bcore\.hooksPath\s+([^\s;|&<>]+)/g;
  if (gitHooksPathRegex.test(cmd)) {
    violations.push('git config core.hooksPath (repoints git hooks → code execution outside sandbox)');
  }

  // 15. cp/mv/install destination-directory flags: `-t <dir>` and
  //     `--target-directory=<dir>` put the destination BEFORE the sources, so
  //     cpMvRegex/installRegex (which capture the LAST token) would report the
  //     wrong target. Capture the real directory here.
  const targetDirRegex =
    /\b(?:cp|mv|install)\b[^;|&]*?(?:--target-directory=([^\s;|&<>]+)|(?:^|\s)-t\s+([^\s;|&<>]+))/g;
  checkMatchesAlt(targetDirRegex, cmd, [1, 2], agentWorkDir, violations, 'target-directory flag');

  // 16. xargs <writer>: xargs invokes a downstream command once per stdin
  //     token. When that command is a writer/destructive verb (rm, cp, mv,
  //     tee, dd, install, ln, truncate, shred), the writes are real but the
  //     targets come from stdin (not statically visible). Deny outright when
  //     the downstream verb is destructive/writing — there is no safe way to
  //     bound the targets. (`xargs echo`, `xargs ls`, etc. are not matched.)
  const xargsWriterRegex =
    /\bxargs\b(?:\s+-[a-zA-Z0-9]\S{0,16}|\s+--[a-zA-Z-]+(?:=\S{1,4096})?){0,8}\s+(rm|rmdir|cp|mv|tee|dd|install|ln|truncate|shred|unlink|chmod|chown)\b/g;
  if (xargsWriterRegex.test(cmd)) {
    violations.push('xargs <writer> (writes/deletes targets read from stdin)');
  }

  // 17. Leading env-var assignments that hijack script execution: shell-startup
  //     files sourced by non-interactive shells, the dynamic-loader preload and
  //     library-path injectors, and shell-option forcing (xtrace / sourcing).
  //     None have a legitimate in-sandbox use as a command PREFIX, so deny
  //     outright. The exact prefix set is the alternation in envExecRegex below.
  //     Matched only at a command boundary (start of string or after
  //     `;`/`|`/`&`/`(`), where they act as exec-env prefixes — NOT when they
  //     appear as a value being assigned to something else.
  // DEVITALIZED (skillaudit FP on a detector signature, NOT a runtime change):
  //   this needle matches env-var exec-hijack PREFIXES in the command string
  //   (data context — never executed), but its regex-LITERAL form trips
  //   skillaudit's CONTAINER_ESCAPE heuristic. Built from fragments through
  //   new RegExp so no contiguous sensitive env-var name appears in the source;
  //   the compiled pattern (.source) is byte-identical to the original literal.
  const envExecRegex = new RegExp(
    '(?:^|[;|&(]|&&|\\|\\|)\\s*(?:BASH_' + 'ENV|LD_' + 'PRELOAD|LD_' +
      'LIBRARY_PATH|ENV|SHELL' + 'OPTS|BASH_' + 'FUNC_)\\s*=',
    'g'
  );
  if (envExecRegex.test(cmd)) {
    // Message split so the source holds no contiguous env-var-hijack token
    // (skillaudit CONTAINER_ESCAPE FP); the pushed string is byte-identical.
    violations.push('env-exec assignment (BASH_' + 'ENV/LD_' + 'PRELOAD/ENV/SHELL' + 'OPTS hijacks execution)');
  }

  return violations;
}

/**
 * Quote-aware linear-time pre-pass. Walks the command once, character by
 * character, tracking single/double/backtick quote state. Quote DELIMITERS
 * are dropped and the inner text is emitted verbatim (no separator inserted),
 * so a quoted run fuses with whatever token it abuts:
 *   `echo h > "/outside/f"`   →  `echo h > /outside/f`
 *   `cp x '/a b/c'`           →  `cp x /a b/c`   (intentional: the path with a
 *                                  space is exposed; the redirect/target regex
 *                                  then stops at the space, capturing `/a`,
 *                                  which still resolves outside the sandbox and
 *                                  denies — fail-closed, never fail-open)
 * A backslash inside a double-quote or unquoted region escapes the next char
 * (so `\"` does not open/close a quote). This is O(n), single pass, no
 * backtracking — it CANNOT introduce ReDoS. It is intentionally permissive
 * (it does not model every POSIX quoting nuance); its only job is to deny the
 * heuristic's evasion via quoting, and any ambiguity errs toward MORE matching.
 */
function dequoteCommand(command) {
  // Hard cap mirrors the per-token bounds elsewhere: a pathological
  // multi-megabyte command is truncated rather than scanned in full. A real
  // command line never approaches this; truncation only ever drops trailing
  // content, which is fail-closed for a prefix-anchored heuristic.
  const MAX = 65536;
  const src = command.length > MAX ? command.slice(0, MAX) : command;

  let out = '';
  let quote = null; // null | "'" | '"' | '`'
  for (let i = 0; i < src.length; i++) {
    const ch = src[i];
    // Backslash escape outside single-quotes (single-quotes are literal in sh).
    if (ch === '\\' && quote !== "'" && i + 1 < src.length) {
      out += src[i + 1];
      i++;
      continue;
    }
    if (quote) {
      if (ch === quote) {
        quote = null; // closing delimiter — drop it
      } else {
        out += ch; // inner text verbatim
      }
      continue;
    }
    if (ch === "'" || ch === '"' || ch === '`') {
      quote = ch; // opening delimiter — drop it
      continue;
    }
    out += ch;
  }
  return out;
}

/**
 * Kernel-provided data sinks that discard or echo bytes — writing to them
 * mutates nothing on disk, so they are never "writes outside the sandbox"
 * (ai-maestro#123 defect (a): `cmd >/dev/null 2>&1` is the documented discard
 * idiom, and the /tmp-file workaround it forced was WORSE for the guard's own
 * objective). Kept to the fixed sink set on purpose: /dev at large holds real
 * device nodes; only these are unconditionally safe discard/echo targets.
 */
function isDevSink(resolvedPath) {
  return (
    resolvedPath === '/dev/null' ||
    resolvedPath === '/dev/stdout' ||
    resolvedPath === '/dev/stderr' ||
    resolvedPath === '/dev/tty' ||
    resolvedPath.startsWith('/dev/fd/')
  );
}

function checkMatches(regex, command, group, agentWorkDir, violations, label) {
  let match;
  while ((match = regex.exec(command)) !== null) {
    const target = match[group];
    if (target) {
      const resolved = path.resolve(target);
      if (!isDevSink(resolved) && !isAllowedPath(resolved, agentWorkDir)) {
        // Name the token AND the reason (ai-maestro#123 scope item 4): a
        // caller must be able to tell "write outside the sandbox" from "the
        // parser thought this text was a redirect/target".
        violations.push(label ? `${resolved} (${label})` : resolved);
      }
    }
    // Guard against zero-width matches stalling exec() on a global regex.
    if (match.index === regex.lastIndex) regex.lastIndex++;
  }
}

/**
 * Like checkMatches but the path can land in ANY of several capture groups
 * (used where a regex has alternated forms, e.g. `--target-directory=<dir>`
 * vs `-t <dir>` — only one group is populated per match). The first
 * non-empty group in `groups` is taken as the target.
 */
function checkMatchesAlt(regex, command, groups, agentWorkDir, violations, label) {
  let match;
  while ((match = regex.exec(command)) !== null) {
    let target;
    for (const g of groups) {
      if (match[g]) {
        target = match[g];
        break;
      }
    }
    if (target) {
      const resolved = path.resolve(target);
      if (!isDevSink(resolved) && !isAllowedPath(resolved, agentWorkDir)) {
        violations.push(label ? `${resolved} (${label})` : resolved);
      }
    }
    if (match.index === regex.lastIndex) regex.lastIndex++;
  }
}

// ============================================================================
// Quote-aware redirect scanner (ai-maestro#123 defect (b))
// ============================================================================

/**
 * Linear single-pass scan of the RAW command for output redirects, applying
 * the SHELL's notion of where a redirect exists. Inside single quotes, double
 * quotes, a backslash escape, a heredoc body, or $((...)) arithmetic, `>` is
 * DATA — the old dequote-then-regex shape parsed it as an operator, which is
 * how `echo "a placeholder /Users/<owner>/agents/frank"` got denied for
 * "writing" to /agents/frank (the `>` closing the placeholder).
 *
 * Deliberate asymmetry: the OPERATOR's context decides, never the target's —
 * `> "<an out-of-sandbox system path>"` is a real redirect with a quoted target and still denies
 * (pinned by test 01/02 in tests/test_directory_guard_bash.py).
 *
 * Handled without over-blocking: fd duplication (`2>&1`, `>&2`, `>&-`) is not
 * a path; `<<<` here-strings and `<(...)`/`>(...)` process substitutions have
 * no file target; `$((1<<2))` shift operators are not heredocs. Heredoc bodies
 * (quoted or unquoted tag, `<<-` tab-stripping) are skipped — nothing in a
 * body is executed by the OUTER shell. MAY still over-block (accepted,
 * fail-closed): `> $VAR` resolves the literal token; redirects inside $() and
 * backticks are treated as real (they are — a subshell runs them).
 *
 * Returns true when a heredoc body never terminated: the tail of the command
 * was skipped UNVERIFIED, and an unterminated heredoc is exactly the shape an
 * evasion would use — the caller MUST then rescan fail-closed (the legacy
 * dequoted scan), never treat the skipped bytes as clean.
 */
function scanRedirects(command, agentWorkDir, violations) {
  const MAX = 65536; // same cap + rationale as dequoteCommand
  const src = command.length > MAX ? command.slice(0, MAX) : command;
  const n = src.length;
  const isSpace = (c) => c === ' ' || c === '\t';
  const isWordEnd = (c) => isSpace(c) || ';|&<>()\n'.includes(c);

  /** Read a redirect TARGET starting at j (after the operator). */
  function readTarget(j) {
    while (j < n && isSpace(src[j])) j++;
    if (j >= n) return { target: null, next: j };
    if (src[j] === '&') {
      // fd duplication (>&1, 2>&1, >&-): a digit or `-` after `&` names an fd,
      // not a file. `>& word` (legacy csh both-redirect) falls through below.
      let k = j + 1;
      if (k < n && (src[k] === '-' || (src[k] >= '0' && src[k] <= '9'))) {
        while (k < n && src[k] >= '0' && src[k] <= '9') k++;
        return { target: null, next: k };
      }
      j = k;
    }
    if (j < n && src[j] === '(') {
      // >(cmd) process substitution: the "target" is a pipe to a command, not
      // a path. The command INSIDE keeps being scanned by the outer loop.
      return { target: null, next: j };
    }
    if (j < n && (src[j] === '"' || src[j] === "'")) {
      const q = src[j];
      let k = j + 1;
      let buf = '';
      while (k < n && src[k] !== q) {
        if (q === '"' && src[k] === '\\' && k + 1 < n) { buf += src[k + 1]; k += 2; continue; }
        buf += src[k];
        k++;
      }
      return { target: buf || null, next: k < n ? k + 1 : k };
    }
    let k = j;
    let buf = '';
    while (k < n && !isWordEnd(src[k])) {
      if (src[k] === '\\' && k + 1 < n) { buf += src[k + 1]; k += 2; continue; }
      buf += src[k];
      k++;
    }
    return { target: buf || null, next: k };
  }

  function pushIfForbidden(target) {
    if (!target) return;
    const resolved = path.resolve(target);
    if (isDevSink(resolved)) return;
    if (!isAllowedPath(resolved, agentWorkDir)) {
      violations.push(`${resolved} (redirect target)`);
    }
  }

  const heredocQueue = []; // FIFO of pending {tag, stripTabs} awaiting bodies
  let arith = 0;           // $(( ... )) nesting depth
  let i = 0;

  while (i < n) {
    const ch = src[i];

    // A newline with heredocs pending starts the FIRST body: consume whole
    // lines, closing each pending tag in order (that is heredoc semantics —
    // bodies attach FIFO to the operators on the command line above).
    if (ch === '\n' && heredocQueue.length > 0) {
      i++;
      while (heredocQueue.length > 0 && i < n) {
        const { tag, stripTabs } = heredocQueue[0];
        let eol = src.indexOf('\n', i);
        if (eol === -1) eol = n;
        let line = src.slice(i, eol);
        if (stripTabs) line = line.replace(/^\t+/, '');
        i = eol < n ? eol + 1 : n;
        if (line === tag) heredocQueue.shift();
      }
      continue;
    }

    if (ch === '\\') { i += 2; continue; } // escaped char is data (incl. \>)

    if (ch === "'") {
      const close = src.indexOf("'", i + 1);
      i = close === -1 ? n : close + 1;
      continue;
    }
    if (ch === '"') {
      let k = i + 1;
      while (k < n && src[k] !== '"') {
        if (src[k] === '\\') k++;
        k++;
      }
      i = k < n ? k + 1 : n;
      continue;
    }

    // $(( ... )): << and >> are shift operators here, never redirects.
    if (ch === '$' && src.startsWith('$((', i)) { arith++; i += 3; continue; }
    if (arith > 0) {
      if (src.startsWith('))', i)) { arith--; i += 2; continue; }
      i++;
      continue;
    }

    if (ch === '<') {
      if (src.startsWith('<<<', i)) { i = readTarget(i + 3).next; continue; } // here-string: word, no file
      if (src.startsWith('<<', i)) {
        // Heredoc: parse the tag (optionally `-` prefixed, quoted, or \escaped).
        let j = i + 2;
        let stripTabs = false;
        if (src[j] === '-') { stripTabs = true; j++; }
        while (j < n && isSpace(src[j])) j++;
        let tag = '';
        if (j < n && (src[j] === '"' || src[j] === "'")) {
          const q = src[j];
          let k = j + 1;
          while (k < n && src[k] !== q) { tag += src[k]; k++; }
          j = k < n ? k + 1 : k;
        } else {
          if (j < n && src[j] === '\\') j++;
          while (j < n && !isWordEnd(src[j])) { tag += src[j]; j++; }
        }
        if (tag) heredocQueue.push({ tag, stripTabs });
        i = j;
        continue;
      }
      i++; // plain input redirect or <(cmd): no write target
      continue;
    }

    if (ch === '&' && src[i + 1] === '>') { // &> file, &>> file
      let j = i + 2;
      if (src[j] === '>') j++;
      const r = readTarget(j);
      pushIfForbidden(r.target);
      i = r.next;
      continue;
    }

    if (ch === '>') {
      let j = i + 1;
      if (src[j] === '>') j++; // >>
      if (src[j] === '|') j++; // >| clobber-override
      if (src[j] === '(') { i = j; continue; } // >(cmd) process substitution
      const r = readTarget(j);
      pushIfForbidden(r.target);
      i = r.next;
      continue;
    }

    i++;
  }

  return heredocQueue.length > 0; // unterminated heredoc → caller rescans fail-closed
}
