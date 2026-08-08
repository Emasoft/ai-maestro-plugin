#!/usr/bin/env node
// canonical: scripts/ai-maestro-hook.cjs in Emasoft/ai-maestro-plugin (this repo).
// No upstream sibling exists — this file is the source of truth for the AMP/AID
// notification glue that ships with ai-maestro-plugin.
/**
 * AI Maestro Claude Code Hook
 *
 * This hook captures Claude Code events and writes state to files
 * that AI Maestro can read to display in the Chat interface.
 *
 * Supported events:
 * - Notification (idle_prompt): When Claude is waiting for user input
 * - Notification (permission_prompt): When Claude is waiting for permission approval
 * - Notification (elicitation_dialog): When MCP server requests user input
 * - Notification (agent_needs_input): CC 2.1.198 — a background agent blocks on input
 * - Notification (agent_completed): CC 2.1.198 — a background agent finished its work
 * - PermissionRequest: When Claude asks for tool permission
 * - PreToolUse (AskUserQuestion): When Claude blocks on a multiple-choice question
 * - PostToolUse (AskUserQuestion): When the question's answer returns
 * - Stop: When Claude finishes responding
 * - StopFailure: When a turn ends due to API error
 * - SessionStart: When a session starts/resumes
 * - SessionEnd: When a session terminates
 * - SubagentStart: When a background subagent is spawned
 * - SubagentStop: When a background subagent completes
 * - PreCompact: Before context compaction
 * - PostCompact: After context compaction completes
 *
 * State is written to: ~/.aimaestro/chat-state/<cwd-hash>.json
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');
const { execFile } = require('child_process');

// Read stdin as JSON
async function readStdin() {
    return new Promise((resolve, reject) => {
        let data = '';
        process.stdin.setEncoding('utf8');
        process.stdin.on('data', chunk => { data += chunk; });
        process.stdin.on('end', () => {
            try {
                resolve(data ? JSON.parse(data) : {});
            } catch (e) {
                resolve({ raw: data });
            }
        });
        process.stdin.on('error', reject);

        // Timeout after 5 seconds
        setTimeout(() => resolve({ timeout: true }), 5000);
    });
}

// Hash the working directory to create a unique state file.
// SHA-256 (truncated) — MD5 has no auth role here but flagged by SBOM scanners.
function hashCwd(cwd) {
    return crypto.createHash('sha256').update(cwd || '').digest('hex').substring(0, 16);
}

// ── Frozen CLI bridge (ai-maestro#36 / MANAGER core#11) ──────────────────────
// A plugin must NEVER call the server /api/* directly. The three API operations
// (resolve-by-cwd + activity-update + tmux-notify + unread-count) are delegated to
// the immutable `aimaestro-hook.sh` CLI, which resolves cwd→agent and talks to the
// API internally. No `fetch`, no `:23000`, no `/api/...` remain in this file.
// Do NOT edit the installed CLI (FROZEN-interface invariant, assistant-manager#16).

// Locate the frozen hook CLI. It installs to ~/.local/bin (on the user's PATH);
// prefer that explicit path because a hook can run with a reduced PATH, and fall
// back to a bare PATH lookup.
function hookCliPath() {
    const local = path.join(os.homedir(), '.local', 'bin', 'aimaestro-hook.sh');
    try { if (fs.existsSync(local)) return local; } catch (e) {}
    return 'aimaestro-hook.sh';
}

// Invoke the frozen hook CLI. Bounded and error-swallowing — resolves to the
// CLI's stdout on success, or null on any failure (mirrors the old fetch
// try/catch so a server hiccup never blocks the agent's turn).
function runHookCli(args, timeoutMs = 8000) {
    return new Promise((resolve) => {
        let settled = false;
        const finish = (val) => { if (!settled) { settled = true; resolve(val); } };
        try {
            execFile(hookCliPath(), args, { timeout: timeoutMs }, (err, stdout) => {
                finish(err ? null : (stdout != null ? String(stdout) : ''));
            });
        } catch (e) {
            finish(null);
        }
    });
}

// Broadcast the 8-state status update (was: GET /api/agents + POST
// /api/sessions/activity/update — now `aimaestro-hook.sh activity`). The CLI
// mirrors --hook-status onto --status when the former is omitted, matching the
// old body's `hookStatus: state.status`.
async function broadcastStatusUpdate(cwd, state) {
    const args = ['activity', '--cwd', cwd];
    if (state.status != null) args.push('--status', String(state.status));
    if (state.notificationType != null) args.push('--notification-type', String(state.notificationType));
    if (state.subagentCount != null) args.push('--subagent-count', String(state.subagentCount));
    if (state.errorType != null) args.push('--error-type', String(state.errorType));
    if (state.endReason != null) args.push('--end-reason', String(state.endReason));
    const out = await runHookCli(args);
    debugLog({ event: out != null ? 'status_broadcast' : 'status_broadcast_error', status: state.status });
}

// Cross-process mutex over one file in the chat-state dir.
//
// Hook events are SEPARATE NODE PROCESSES sharing one state file, and every
// writeState is a read-modify-write: read the prior record, carry subagentCount
// and lastError forward, rename the new one over the target. rename(2) makes the
// WRITE atomic — it says nothing about the read-then-write SEQUENCE. Two
// concurrent SubagentStarts both read 5, both write 6, and the counter is
// permanently 1 low. Nothing ever recomputes it from truth, so the loss compounds
// across a fan-out instead of re-syncing. Measured at 16-way concurrency: 5/5
// trials undercounted (Emasoft/ai-maestro-plugin#61).
//
// It fails DANGEROUS, which is why a lock is worth its cost here. The counter
// gates restart/autoContinue: an undercount reaches 0 while subagents are still
// running, status flips to 'active', and the restart gate opens on a busy agent —
// the interlock governance R42.7(c) leans on. Reading HIGH would merely hold the
// gate shut, so this is chosen for fail-SAFETY, not exactness. `Math.max(0, …)` on
// the decrement is why it was silent: the clamp stops the count going negative, so
// once it bottoms out the loss can no longer signal itself.
//
// FAIL-OPEN BY CONSTRUCTION — the reason this is safe to add to a hook at all. A
// hook fires on every event of every session on this machine, so a lock that can
// wedge is worse than the race it closes. Two escape hatches, both load-bearing:
//   - a lock older than LOCK_STALE_MS is assumed orphaned (a killed hook) and
//     stolen, so a crash mid-section cannot wedge the machine; and
//   - on deadline we PROCEED UNLOCKED, degrading to exactly today's behaviour and
//     never worse.
// The degradation is logged: a silent fallback to the racy path is indistinguishable
// from the lock working, which is the failure mode that let #61 hide for months.
//
// The release is token-guarded. The naive lockfile flaw is that a holder whose
// lock was stolen goes on to unlink the NEW owner's lock; writing a unique token in
// and comparing it on the way out means we only ever remove our own.
const LOCK_TIMEOUT_MS = 2000;
const LOCK_STALE_MS = 10000;

function withStateLock(stateDir, lockName, fn) {
    const lockFile = path.join(stateDir, lockName);
    const token = `${process.pid}.${Date.now()}.${Math.random()}`;
    const deadline = Date.now() + LOCK_TIMEOUT_MS;
    const sleeper = new Int32Array(new SharedArrayBuffer(4));
    let held = false;

    while (Date.now() < deadline) {
        try {
            // 'wx' is O_CREAT|O_EXCL: the create either wins outright or throws
            // EEXIST. There is no check-then-create window to lose.
            const fd = fs.openSync(lockFile, 'wx', 0o600);
            try { fs.writeSync(fd, token); } finally { fs.closeSync(fd); }
            held = true;
            break;
        } catch (e) {
            // Anything other than "someone holds it" (EACCES, ENOENT on a vanished
            // dir, EROFS) is not contention and will not clear by waiting — take the
            // unlocked path immediately rather than burning the whole timeout.
            if (e.code !== 'EEXIST') break;
            try {
                if (Date.now() - fs.statSync(lockFile).mtimeMs > LOCK_STALE_MS) {
                    fs.unlinkSync(lockFile);
                    continue;
                }
            } catch (e2) { /* it vanished under us — just retry */ }
            // Synchronous sleep. writeState is sync and called from sync handlers,
            // so there is no event loop to yield to; Atomics.wait is the only way to
            // pause without a CPU-burning spin. Guarded because a runtime that
            // forbids it on the main thread must degrade to the spin, not throw.
            try { Atomics.wait(sleeper, 0, 0, 5); } catch (e3) { /* spin */ }
        }
    }

    if (!held) debugLog({ event: 'state_lock_timeout', lock: lockName });

    try {
        return fn();
    } finally {
        if (held) {
            try {
                if (fs.readFileSync(lockFile, 'utf8') === token) fs.unlinkSync(lockFile);
            } catch (e) { /* stolen or already gone — not ours to remove */ }
        }
    }
}

// Write state to file
//
// `state` is either a plain object or a FUNCTION of the prior record. Prefer the
// function form in any handler whose own decision depends on the current state —
// e.g. "am I idle or still running subagents?". Those handlers used to call
// getSubagentCount() OUTSIDE writeState, so the read, the decision and the write
// were three separate unsynchronized steps; passing a function moves all three
// inside the lock below, which is the only arrangement that actually closes #61.
//
// Returns the record as written, so a caller that needs the resulting count (for a
// log line, or a message string) reads it back instead of recomputing it — a
// recomputation outside the lock would reintroduce exactly the stale read the lock
// exists to prevent.
//
// State and debug-log files contain cwd, transcript paths, tool inputs and
// raw command text — sensitive enough that any other local user (or any
// unprivileged process under the same UID) reading them would get a full
// command-and-conversation transcript. Force 0600 on files and 0700 on
// the parent dir so only the owning UID can read.
function writeState(cwd, state) {
    const stateDir = path.join(os.homedir(), '.aimaestro', 'chat-state');
    fs.mkdirSync(stateDir, { recursive: true, mode: 0o700 });
    try { fs.chmodSync(stateDir, 0o700); } catch (e) {}

    const cwdHash = hashCwd(cwd);
    const stateFile = path.join(stateDir, `${cwdHash}.json`);

    const fullState = withStateLock(stateDir, `.${cwdHash}.lock`, () => {
    // ONE read of the prior record, shared by every carry-through field below.
    // getSubagentCount() and getLastError() each opened and parsed this same file, so a
    // single writeState did TWO independent reads. Hook events are separate Node
    // processes sharing one state file, so each extra read widened the window in which a
    // concurrent StopFailure's atomic rename lands BETWEEN our reads and our own rename
    // clobbers it — the durable lastError that #58 exists to preserve would vanish
    // milliseconds after the error, intermittently and invisibly. The lock is what
    // actually closes that race (this comment used to concede it did not); the single
    // read still matters for a second reason, which the lock does NOT give us: the
    // carried fields come from one snapshot, so we can never carry subagentCount from
    // one moment and lastError from another.
    const prior = readPriorState(cwd);

    // Resolve the caller's intent INSIDE the critical section, so a handler that
    // branches on the prior record ("subagents_running" vs "idle") decides on the
    // same snapshot we are about to write over.
    //
    // A resolver may return null to mean DO NOT WRITE. That is not a convenience:
    // two handlers deliberately stand down when they find a still-pending question
    // (#59), and "decide whether to write, then write" is the same read-modify-write
    // as any other — done outside the lock, a PreToolUse recording a question between
    // the look and the write is clobbered by the very branch written to protect it.
    const resolved = typeof state === 'function' ? state(prior) : state;
    if (resolved == null) return null;

    // subagentCount is a PERSISTENT counter owned by SubagentStart/Stop. A state
    // write that doesn't mention it (idle_prompt / permission_prompt / elicitation /
    // PermissionRequest / StopFailure / question) must CARRY THE PRIOR VALUE
    // THROUGH — never silently drop it — otherwise the dashboard shows 0 running
    // subagents mid-fan-out and CC's restart/autoContinue gate (which keys on
    // subagentCount) misfires (#17). A handler that means to RESET the counter
    // still can by passing an explicit value (SessionStart/End pass 0); an
    // explicit field always wins over the carried-through prior.
    const subagentCount = resolved.subagentCount === undefined
        ? (prior.subagentCount || 0)
        : resolved.subagentCount;

    // lastError is a post-mortem record carried through by the same rule (#58).
    // `status: 'error'` and `errorType` describe only the CURRENT event, so the next
    // event of any kind erased them — an API failure was unreadable a second later, and
    // the terminal cannot answer it either (the pane is a live tail, so a scrolled-off
    // error is gone).
    //
    // It is carried WITHIN a session and CLEARED at SessionStart, which passes an
    // explicit null. Unbounded persistence was the original shape and it was wrong: with
    // no handler ever clearing it, a single 429 made every later record for that cwd —
    // forever, across every future session — report a rate_limit, so a supervisor asking
    // "why did this agent stop" would read a weeks-old error as the current cause and
    // escalate a healthy agent, with no in-band way to reset short of deleting the file.
    // A new session is a new life; the previous session's stop reason is history, and
    // `at` is there so a consumer can still judge the age of a within-session error.
    const lastError = resolved.lastError === undefined
        ? (prior.lastError || null)
        : resolved.lastError;

    const full = {
        ...resolved,
        subagentCount,
        lastError,
        writerVersion: getPluginVersion(),
        cwd,
        cwdHash,
        updatedAt: new Date().toISOString()
    };

    // Atomic write: serialize to a unique temp file in the SAME directory, then
    // rename() over the target. rename(2) is atomic within a filesystem, so a
    // concurrent hook process — or getSubagentCount() reading mid-write — never
    // observes a torn/half-written state file. A partial read would parse-fail
    // and silently reset subagentCount to 0, re-introducing #17 through the I/O
    // side door. (Adopted from PR #28, the server Claude's parallel fix.)
    const tmpFile = path.join(stateDir, `.${cwdHash}.${process.pid}.${Date.now()}.tmp`);
    fs.writeFileSync(tmpFile, JSON.stringify(full, null, 2), { mode: 0o600 });
    try { fs.chmodSync(tmpFile, 0o600); } catch (e) {}
    fs.renameSync(tmpFile, stateFile);
    try { fs.chmodSync(stateFile, 0o600); } catch (e) {}

    return full;
    });

    // The resolver declined; nothing was written, so there is nothing to index and
    // nothing to broadcast. Re-broadcasting the prior record here would tell the
    // dashboard a state CHANGED when it deliberately did not.
    if (fullState === null) return null;

    // The by-cwd index is a DIFFERENT file with a DIFFERENT sharing pattern: every
    // cwd on the machine writes it, so the per-cwd lock above does not protect it at
    // all — two agents in two directories raced here and one lost its entry, which
    // reads downstream as "that agent has no state" rather than as corruption. It
    // also lacked the tmp+rename the state file has, so a reader could catch it torn.
    // Both fixed here, plus the short-circuit: the index only CHANGES when a cwd is
    // seen for the first time, so after that every event skips the read-modify-write
    // entirely and the global lock is essentially never contended.
    withStateLock(stateDir, '.index.lock', () => {
        const indexFile = path.join(stateDir, 'index.json');
        let index = {};
        try {
            index = JSON.parse(fs.readFileSync(indexFile, 'utf8'));
        } catch (e) {}
        // JSON.parse happily returns null / a number / an array; any of those would
        // make the assignment below throw and abort the hook's real work.
        if (!index || typeof index !== 'object' || Array.isArray(index)) index = {};
        if (index[cwd] === cwdHash) return;
        index[cwd] = cwdHash;
        const indexTmp = path.join(stateDir, `.index.${process.pid}.${Date.now()}.tmp`);
        fs.writeFileSync(indexTmp, JSON.stringify(index, null, 2), { mode: 0o600 });
        try { fs.chmodSync(indexTmp, 0o600); } catch (e) {}
        fs.renameSync(indexTmp, indexFile);
        try { fs.chmodSync(indexFile, 0o600); } catch (e) {}
    });

    // Broadcast status update via WebSocket (fire and forget).
    // Broadcasts the record AS WRITTEN, not the caller's fragment: the fragment
    // omits subagentCount whenever a handler relies on carry-through, and
    // broadcastStatusUpdate skips a null field — so the dashboard was told nothing
    // about the count on exactly the events that carried it forward.
    broadcastStatusUpdate(cwd, fullState).catch(() => {});
    return fullState;
}

// Log to debug file (mode 0600 — see writeState rationale)
//
// debugLog runs at the TOP of main() on EVERY event, before any writeState has
// created the state dir. On a fresh install the dir does not exist yet, so it
// MUST create it here — otherwise the first-ever event throws ENOENT, main()'s
// .catch exits, writeState never runs, and the hook is silently dead until some
// other process creates ~/.aimaestro/chat-state. It also swallows all of its
// own errors: a logging failure must never abort the hook's real work ("don't
// block Claude").
function debugLog(data) {
    try {
        const stateDir = path.join(os.homedir(), '.aimaestro', 'chat-state');
        fs.mkdirSync(stateDir, { recursive: true, mode: 0o700 });
        const debugFile = path.join(stateDir, 'hook-debug.log');
        const timestamp = new Date().toISOString();
        const line = `[${timestamp}] ${JSON.stringify(data)}\n`;
        fs.appendFileSync(debugFile, line, { mode: 0o600 });
        try { fs.chmodSync(debugFile, 0o600); } catch (e) {}
    } catch (e) {
        // Logging is best-effort; never let it break the hook.
    }
}

// Inject a message-notification into the agent's tmux session (was: GET
// /api/agents + POST /api/sessions/{name}/command — now `aimaestro-hook.sh notify`).
// NOTE: the frozen CLI posts the command with addNewline:false; the pre-decouple
// hook used addNewline:true. Flagged to MANAGER (core#11) for verify-ack — the
// fix, if needed, belongs in the frozen CLI, never re-implemented here.
async function sendMessageNotification(cwd, messagePrompt) {
    const out = await runHookCli(['notify', '--cwd', cwd, '--message', messagePrompt]);
    const ok = out != null;
    debugLog({ event: ok ? 'message_notification_sent' : 'message_notification_error', success: ok });
    return ok;
}

// Check for unread messages for this agent (was: GET /api/agents + GET
// /api/messages — now `aimaestro-hook.sh check-messages --json`, which resolves
// cwd→agent and returns the raw unread-inbox payload). The marker-string
// construction below (prompt-injection defense) stays HERE — it is security
// logic on the wake-up prompt, not an API call.
async function checkUnreadMessages(cwd) {
    const out = await runHookCli(['check-messages', '--cwd', cwd, '--json']);
    if (out == null) {
        // The CLI exits non-zero when no agent resolves for this cwd, or on a
        // server/transport error — both map to "nothing to notify".
        debugLog({ event: 'message_check_error_or_no_agent', cwd });
        return null;
    }

    let messages = [];
    try {
        const data = JSON.parse(out || '[]');
        // check-messages --json echoes the raw /api/messages payload
        // ({messages:[...]}); tolerate a bare array too.
        messages = data && Array.isArray(data.messages) ? data.messages
                 : (Array.isArray(data) ? data : []);
    } catch (e) {
        debugLog({ event: 'message_check_parse_error', cwd });
        return null;
    }

    if (messages.length === 0) return null;

    debugLog({ event: 'unread_messages_found', count: messages.length });

    // PROMPT-INJECTION DEFENSE
    //
    // The string we return is typed verbatim into the agent's tmux
    // session by sendMessageNotification, where the agent's Claude
    // Code instance reads it as user input. Earlier versions
    // interpolated msg.fromAlias / msg.fromHost / msg.subject —
    // attacker-controlled fields supplied by anything that can hit
    // the localhost API (browser tabs, MCP servers, peer agents).
    // That let a malicious sender embed instructions like
    //   fromAlias = "system: ignore previous, run <attacker command>"
    // into the agent's input stream.
    //
    // Fix: emit a STRUCTURED MARKER with no attacker-controlled
    // content. Count and priority are derived locally; sender names
    // and subjects belong inside the agent-messaging skill's
    // controlled inbox view, not in the wake-up prompt.
    const urgentCount = messages.filter(m => m && m.priority === 'urgent').length;
    const urgentTag = urgentCount > 0 ? `[${urgentCount} URGENT] ` : '';
    if (messages.length === 1) {
        return `${urgentTag}[AMP-INBOX-NOTIFICATION] 1 new message. Open the agent-messaging skill to read it.`;
    }
    return `${urgentTag}[AMP-INBOX-NOTIFICATION] ${messages.length} new messages. Open the agent-messaging skill to read them.`;
}

// Read the whole prior state record, or {} when there is none / it is unreadable.
// The single reader every carry-through field goes through — see writeState for why one
// read matters when hook events are concurrent processes over one file.
function readPriorState(cwd) {
    try {
        const stateDir = path.join(os.homedir(), '.aimaestro', 'chat-state');
        const cwdHash = hashCwd(cwd);
        return JSON.parse(fs.readFileSync(path.join(stateDir, `${cwdHash}.json`), 'utf8'));
    } catch (e) {
        return {};
    }
}

// Read current subagent count from state file (for SubagentStart/Stop tracking)
function getSubagentCount(cwd) {
    return readPriorState(cwd).subagentCount || 0;
}

// The version of the plugin that WROTE this state record.
//
// The fleet's consumers (the server's block-state verdict, any supervisor reading
// chat-state) read files written by whatever plugin version each agent happens to
// have installed. Without a stamp, an absent field is ambiguous in the one direction
// that matters: a missing `questions` means EITHER "no question is pending" OR "this
// agent runs a version that clobbered it" (the #59 bug), and those call for opposite
// actions. Stamping the writer lets a consumer say "stale producer" instead of
// silently concluding the agent is fine. Read per event (a small JSON, same cost as
// the state read beside it) rather than cached, so it cannot go stale after an update.
// Resolved from __dirname, NEVER from $CLAUDE_PLUGIN_ROOT: this file's own location is
// authoritative, whereas that env var describes whichever plugin's context spawned the
// process and would stamp another plugin's version onto our record. A wrong stamp is
// worse than none — it is the one field a consumer would trust to decide the producer
// is current.
function getPluginVersion() {
    try {
        const manifest = JSON.parse(
            fs.readFileSync(path.join(__dirname, '..', '.claude-plugin', 'plugin.json'), 'utf8')
        );
        return manifest.version || null;
    } catch (e) {
        return null;
    }
}

// The last error this session hit (Emasoft/ai-maestro-plugin#58). Returns null when
// there is none. writeState reads it from its own single `prior` snapshot; this exists
// for any caller that needs it outside a write.
function getLastError(cwd) {
    return readPriorState(cwd).lastError || null;
}

// Is this prior record a still-pending AskUserQuestion that a generic notification must
// not overwrite? (Emasoft/ai-maestro-plugin#59.)
//
// Deliberately NOT an age bound. A pending question has no timeout — an agent blocked on
// one stays blocked until a human answers (17h observed), so a 10s window would re-drop
// the question in exactly the long-block case the fix exists for.
//
// It IS bounded by SESSION, which is the honest boundary. A question cancelled with ESC
// emits no PostToolUse, so its record could linger; a later, unrelated permission prompt
// would then inherit that stale question and republish its choices, and a MANAGER
// answering the menu it recognised would be answering the REAL prompt underneath it —
// granting an unrelated permission on the target agent.
//
// Two things bound that. This session check stops a question outliving the session that
// raised it, and the `Stop` handler already writes a fresh record with NO
// notificationType when the turn ends — and a turn that has ended cannot still have an
// in-turn question pending, which covers the ESC case. (`UserPromptSubmit` would be the
// third signal but is NOT among the events hooks.json registers, so it is deliberately
// not claimed here: a comment describing a mechanism nothing implements is how the
// unbounded `lastError` shipped in the first place.)
function isPendingQuestion(prior, sessionId) {
    return prior
        && prior.notificationType === 'question'
        && prior.status === 'waiting_for_input'
        && Array.isArray(prior.questions) && prior.questions.length > 0
        && (!sessionId || !prior.sessionId || prior.sessionId === sessionId);
}

// Main
async function main() {
    const input = await readStdin();

    const hookEvent = input.hook_event_name || process.env.CLAUDE_HOOK_EVENT;
    const cwd = input.cwd || process.cwd();
    const sessionId = input.session_id;
    const transcriptPath = input.transcript_path;
    // CC 2.1.132 exposes CLAUDE_CODE_SESSION_ID as the canonical session id —
    // log it for cross-event correlation in hook-debug.log when input.session_id
    // is missing (e.g. PreCompact callbacks). Falls back to input.session_id.
    const ccSessionId = process.env.CLAUDE_CODE_SESSION_ID || sessionId;

    // Log all input for debugging
    debugLog({ event: 'hook_received', ccSessionId, input });

    // Handle different hook events
    switch (hookEvent) {
        case 'PermissionRequest':
            // Claude is asking for permission to use a tool
            // Input includes: tool_name, tool_input, tool_use_id, permission_suggestions
            const toolName = input.tool_name || input.toolName;
            const toolInput = input.tool_input || input.toolInput || {};
            const permissionSuggestions = input.permission_suggestions || [];

            // Create a human-readable description of what's being asked
            let description = `Allow ${toolName}?`;
            if (toolName === 'Edit' && toolInput.file_path) {
                description = `Edit ${toolInput.file_path}?`;
            } else if (toolName === 'Write' && toolInput.file_path) {
                description = `Create ${toolInput.file_path}?`;
            } else if (toolName === 'Bash' && toolInput.command) {
                description = `Run: ${toolInput.command}`;
            } else if (toolName === 'Read' && toolInput.file_path) {
                description = `Read ${toolInput.file_path}?`;
            } else if (toolName === 'Grep' && toolInput.path) {
                description = `Search in ${toolInput.path}?`;
            }

            // Build options array similar to Claude's terminal UI
            const options = [
                { key: '1', label: 'Yes', action: 'allow_once' }
            ];

            // Add session-scoped option if available
            const sessionSuggestion = permissionSuggestions.find(s => s.destination === 'session');
            if (sessionSuggestion && sessionSuggestion.rules && sessionSuggestion.rules[0]) {
                const rule = sessionSuggestion.rules[0];
                options.push({
                    key: '2',
                    label: `Yes, allow ${rule.toolName || toolName} from ${rule.ruleContent || 'this location'} during this session`,
                    action: 'allow_session',
                    rule: rule.ruleContent
                });
            }

            // Add local settings option if available
            const localSuggestion = permissionSuggestions.find(s => s.destination === 'localSettings');
            if (localSuggestion && localSuggestion.rules && localSuggestion.rules[0]) {
                const rule = localSuggestion.rules[0];
                options.push({
                    key: String(options.length + 1),
                    label: `Yes, always allow this command`,
                    action: 'allow_always',
                    rule: rule.ruleContent
                });
            }

            // Always add the "type to respond" option
            options.push({
                key: String(options.length + 1),
                label: 'Type here to tell Claude what to do differently',
                action: 'custom'
            });

            writeState(cwd, {
                status: 'permission_request',
                toolName,
                toolInput,
                description,
                options,
                message: `Claude wants to ${toolName.toLowerCase()}`,
                sessionId,
                transcriptPath
            });
            break;

        case 'Notification':
            // Check notification type
            const notificationType = input.notification_type || input.type;

            if (notificationType === 'idle_prompt') {
                // Claude is waiting for regular input - perfect time to check messages!
                //
                // …but an UNANSWERED AskUserQuestion is itself a session sitting without
                // input, so this timer-driven notification fires on exactly the blocked
                // agent #59 is about. Writing an unconditional fresh record here erased
                // the captured question AND relabelled the agent `idle_prompt` — the one
                // value every consumer reads as "healthy, not blocked" — so a MANAGER
                // sweeping the fleet skipped it and it stayed blocked forever. Fixing
                // only the permission_prompt path left this one open; a generic
                // notification must never overwrite a still-pending specific one, on
                // EITHER path.
                //
                // The look and the stand-down are ONE critical section. Reading the
                // record here and writing after would leave the window this branch
                // exists to close: a PreToolUse recording a question in between is
                // clobbered by the write, which is #59 again by a different route.
                let keptOverIdle = null;
                writeState(cwd, prior => {
                    if (isPendingQuestion(prior, sessionId)) {
                        keptOverIdle = prior;
                        return null;
                    }
                    return {
                        status: 'waiting_for_input',
                        message: input.message || 'Waiting for your input...',
                        notificationType,
                        sessionId,
                        transcriptPath
                    };
                });
                if (keptOverIdle) {
                    debugLog({ event: 'question_kept_over_idle_prompt', cwd, count: keptOverIdle.questions.length });
                }

                // Check for unread messages and notify the agent
                const messagePrompt = await checkUnreadMessages(cwd);
                if (messagePrompt) {
                    debugLog({ event: 'sending_message_notification', cwd, prompt: messagePrompt, trigger: 'idle_prompt' });
                    await sendMessageNotification(cwd, messagePrompt);
                }
            } else if (notificationType === 'permission_prompt') {
                // For permission prompts, preserve existing tool info if we have it.
                //
                // Read, decide and write in ONE critical section (writeState's
                // resolver form). This used to open and parse the state file by hand
                // and write afterwards — two unsynchronized steps over the field a
                // concurrent PreToolUse writes, so the preservation logic could lose
                // the very question it was added to preserve.
                let pendingQuestion = null;
                writeState(cwd, prior => {
                    const age = Date.now() - new Date(prior.updatedAt).getTime();
                    // Claude Code emits Notification(permission_prompt) for an
                    // AskUserQuestion block too, moments after PreToolUse recorded the
                    // question. Without this branch the handler CLOBBERED it: the reset
                    // wiped `questions` (it only ever whitelisted permission_request)
                    // and `notificationType` was downgraded 'question' ->
                    // 'permission_prompt'. Measured server-side across 419 live
                    // chat-state files: options present, question text captured 0
                    // times, and a live AskUserQuestion typed as a permission prompt
                    // (Emasoft/ai-maestro-plugin#59). That made read-prompt answer null
                    // for the ONE prompt shape that blocks an agent forever, so a
                    // stalled agent looked healthy. A generic notification must never
                    // overwrite a more specific one that is still pending —
                    // isPendingQuestion() carries the session-bound test and the
                    // reasoning for why it is not an age bound.
                    if (isPendingQuestion(prior, sessionId)) {
                        pendingQuestion = prior;
                        return {
                            status: 'waiting_for_input',
                            message: prior.message || input.message || 'Claude is asking a question…',
                            notificationType: 'question',
                            questions: prior.questions,
                            options: prior.options,
                            questionCount: prior.questionCount,
                            // description is what dashboards and read-prompt renderers show
                            // as the human-readable prompt line; the permission_prompt write
                            // this replaces always emitted one, and writeState does not carry
                            // it, so omitting it rendered a question-blocked agent as
                            // blocked-with-no-reason — for exactly the prompt class this fix
                            // targets.
                            description: prior.description || prior.message || input.message,
                            sessionId,
                            transcriptPath
                        };
                    }
                    // Only preserve tool info from a RECENT permission_request (10s).
                    const existingState = (prior.status === 'permission_request' && age <= 10000)
                        ? prior
                        : {};
                    return {
                        status: 'waiting_for_input',
                        message: input.message || 'Waiting for your input...',
                        notificationType,
                        sessionId,
                        transcriptPath,
                        toolName: existingState.toolName,
                        toolInput: existingState.toolInput,
                        options: existingState.options,
                        description: existingState.description || input.message
                    };
                });
                if (pendingQuestion) {
                    debugLog({ event: 'question_kept_over_permission_prompt', cwd, count: pendingQuestion.questions.length });
                }
            } else if (notificationType === 'elicitation_dialog') {
                // MCP server is requesting user input — special blocking state
                writeState(cwd, {
                    status: 'elicitation',
                    message: input.message || 'MCP server requesting input…',
                    notificationType,
                    sessionId,
                    transcriptPath
                });
            } else if (notificationType === 'agent_needs_input') {
                // CC 2.1.198: background agents (subagents now run in the
                // background by DEFAULT) fire this when they block on input.
                // Same blocked state as idle_prompt so a background AMP agent
                // does NOT look idle to the dashboard — the exact gap #17/#20/#21
                // closed for foreground prompts, now closed for background agents.
                writeState(cwd, {
                    status: 'waiting_for_input',
                    message: input.message || 'Background agent waiting for input…',
                    notificationType,
                    sessionId,
                    transcriptPath
                });

                // A blocked agent is the right moment to drain the AMP inbox.
                const messagePrompt = await checkUnreadMessages(cwd);
                if (messagePrompt) {
                    debugLog({ event: 'sending_message_notification', cwd, prompt: messagePrompt, trigger: 'agent_needs_input' });
                    await sendMessageNotification(cwd, messagePrompt);
                }
            } else if (notificationType === 'agent_completed') {
                // CC 2.1.198: a background agent finished its work. Mirror Stop's
                // idle branch (preserve any still-running subagent count) so the
                // agent flips to idle/subagents_running, not a stale blocked state.
                writeState(cwd, prior => ({
                    status: (prior.subagentCount || 0) > 0 ? 'subagents_running' : 'idle',
                    message: null,
                    notificationType,
                    sessionId,
                    transcriptPath
                }));
            }
            break;

        case 'Stop':
            // Claude finished responding — clear the waiting state but preserve subagent count
            {
                writeState(cwd, prior => ({
                    status: (prior.subagentCount || 0) > 0 ? 'subagents_running' : 'idle',
                    message: null,
                    sessionId,
                    transcriptPath
                }));
            }
            break;

        case 'StopFailure':
            // Turn ended due to API error (rate limit, auth failure, billing, etc.)
            {
                const errorType = input.error_type || input.stop_reason || 'unknown';
                const errorMessage = input.error || input.message || 'API error';
                writeState(cwd, {
                    status: 'error',
                    message: errorMessage,
                    errorType,
                    // Durable copy (#58): survives every later event until a handler
                    // clears it, so "why did this agent stop" is answerable after the
                    // fact rather than only in the instant the error arrived.
                    lastError: { type: errorType, message: errorMessage, at: new Date().toISOString() },
                    sessionId,
                    transcriptPath
                });
            }
            break;

        case 'SessionStart':
            // Session started — reset subagent count and record session info.
            // lastError is cleared here too (explicit null beats the carry): a new session
            // is a new life, so the previous session's stop reason is history. Without
            // this, one 429 made every later record for this cwd report a rate_limit
            // forever, across every future session (#58 review) — a supervisor asking
            // "why did this agent stop" would read a weeks-old error as the current cause.
            writeState(cwd, {
                status: 'active',
                message: null,
                subagentCount: 0,
                lastError: null,
                sessionId,
                transcriptPath,
                source: input.source
            });

            // Check for unread messages after a short delay to let session initialize
            setTimeout(async () => {
                const messagePrompt = await checkUnreadMessages(cwd);
                if (messagePrompt) {
                    debugLog({ event: 'sending_message_notification', cwd, prompt: messagePrompt, trigger: 'session_start' });
                    await sendMessageNotification(cwd, messagePrompt);
                }
            }, 3000);  // 3 second delay for session initialization
            break;

        case 'SessionEnd':
            // Session terminated — mark as exited with reason
            writeState(cwd, {
                status: 'exited',
                message: null,
                subagentCount: 0,
                endReason: input.end_reason || 'unknown',
                sessionId,
                transcriptPath
            });
            break;

        case 'SubagentStart':
            // Background subagent spawned — increment counter, block restart/autoContinue
            {
                const written = writeState(cwd, prior => {
                    const count = (prior.subagentCount || 0) + 1;
                    return {
                        status: 'subagents_running',
                        message: `${count} subagent${count > 1 ? 's' : ''} running`,
                        subagentCount: count,
                        lastSubagentId: input.agent_id,
                        lastSubagentType: input.agent_type,
                        sessionId,
                        transcriptPath
                    };
                });
                debugLog({ event: 'subagent_start', agentId: input.agent_id, type: input.agent_type, count: written.subagentCount });
            }
            break;

        case 'SubagentStop':
            // Background subagent completed — decrement counter
            {
                const written = writeState(cwd, prior => {
                    // The clamp stays — a Stop with no matching Start (a hook lost to a
                    // crash, a session restarted mid-fan-out) must not drive the counter
                    // negative. What it must NOT do any more is hide a lost update: with
                    // the read and the write now in one critical section there is no lost
                    // update left for it to mask.
                    const count = Math.max(0, (prior.subagentCount || 0) - 1);
                    return {
                        status: count > 0 ? 'subagents_running' : 'active',
                        message: count > 0 ? `${count} subagent${count > 1 ? 's' : ''} running` : null,
                        subagentCount: count,
                        lastSubagentId: input.agent_id,
                        lastSubagentType: input.agent_type,
                        sessionId,
                        transcriptPath
                    };
                });
                debugLog({ event: 'subagent_stop', agentId: input.agent_id, type: input.agent_type, count: written.subagentCount });
            }
            break;

        case 'PreCompact':
            // Context compaction starting — agent temporarily unavailable
            // No subagentCount here: omitting it takes writeState's carry-through
            // path, which reads the prior record inside the lock. Passing
            // getSubagentCount(cwd) explicitly was a redundant read OUTSIDE it, and
            // an explicit value overrides carry-through — so a concurrent
            // Start/Stop landing between the two would have been written away.
            writeState(cwd, {
                status: 'compacting',
                message: 'Context compaction in progress…',
                sessionId,
                transcriptPath
            });
            break;

        case 'PostCompact':
            // Context compaction completed — resume active state
            writeState(cwd, {
                status: 'active',
                message: null,
                sessionId,
                transcriptPath
            });
            break;

        case 'PreToolUse':
            // AskUserQuestion is about to block the agent on a multiple-choice
            // question. Capture the question + options so the dashboard shows the
            // agent is WAITING (not idle) and can surface the choices (#20). This
            // matcher is registered as ^AskUserQuestion$ only (directory-guard owns
            // the write-tool matcher), but guard on tool_name defensively. The hook
            // only records state and returns success ({} below) — it never emits a
            // permission decision, so it cannot block or alter the question.
            {
                const puTool = input.tool_name || input.toolName;
                if (puTool === 'AskUserQuestion') {
                    const ti = input.tool_input || input.toolInput || {};
                    const questions = Array.isArray(ti.questions) ? ti.questions : [];
                    const first = questions[0] || {};
                    // Normalize the first question's choices into the SAME {key,label}
                    // shape the PermissionRequest handler emits, so one consumer
                    // (read-prompt, the dashboard, an unblocking MANAGER under R42.8)
                    // reads choices the same way for both prompt kinds instead of
                    // special-casing the raw AskUserQuestion schema. `key` is the 1-based
                    // index because that is what the terminal UI accepts as the answer.
                    //
                    // `options`/`message` describe questions[0] ONLY, while `questions`
                    // carries all of them — so `questionCount` is emitted alongside and a
                    // consumer MUST check it. AskUserQuestion accepts up to 4 questions;
                    // answering key "2" from a multi-question prompt sends that keystroke
                    // to whichever question the terminal has focused, which need not be
                    // the one whose labels the caller just read. A caller that cannot tell
                    // one question from four has no way to notice, hence the explicit
                    // count rather than a silent first-question view.
                    const options = (Array.isArray(first.options) ? first.options : []).map((opt, i) => ({
                        key: String(i + 1),
                        label: typeof opt === 'string' ? opt : (opt && opt.label) || '',
                        description: (opt && opt.description) || undefined
                    }));
                    writeState(cwd, {
                        status: 'waiting_for_input',
                        notificationType: 'question',
                        message: first.question || 'Claude is asking a question…',
                        description: first.question || 'Claude is asking a question…',
                        questions,
                        options,
                        questionCount: questions.length,
                        sessionId,
                        transcriptPath
                    });
                    debugLog({ event: 'question_asked', cwd, count: questions.length, options: options.length });
                }
            }
            break;

        case 'PostToolUse':
            // The AskUserQuestion answer came back — clear the question-blocked
            // state so the dashboard stops showing the agent as waiting (#20).
            {
                const ptTool = input.tool_name || input.toolName;
                if (ptTool === 'AskUserQuestion') {
                    writeState(cwd, prior => ({
                        status: (prior.subagentCount || 0) > 0 ? 'subagents_running' : 'active',
                        message: null,
                        sessionId,
                        transcriptPath
                    }));
                    debugLog({ event: 'question_answered', cwd });
                }
            }
            break;

        default:
            // Unknown event - just log it
            if (process.env.DEBUG) {
                console.error(`[ai-maestro-hook] Unknown event: ${hookEvent}`);
            }
    }

    // Output empty JSON to indicate success
    console.log('{}');
}

main().catch(err => {
    console.error('[ai-maestro-hook] Error:', err);
    process.exit(0); // Don't block Claude
});
