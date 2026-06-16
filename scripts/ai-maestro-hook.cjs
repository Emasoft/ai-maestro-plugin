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
 * - PermissionRequest: When Claude asks for tool permission
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

// Broadcast status update via WebSocket (non-blocking)
// DECOUPLE-BLOCKED ai-maestro#36 (MANAGER core#11): the two /api/ calls below
// (GET /api/agents to resolve the agent by cwd; POST /api/sessions/activity/update
// to push the 8-state status) have NO frozen CLI verb yet — `aimaestro-agent.sh`
// has no `resolve --cwd` and no session-activity verb (cmd_session only attaches).
// Left functional per the directive; flip to the CLI once those verbs land via #36.
// Do NOT patch installed scripts (FROZEN-interface invariant, assistant-manager#16).
async function broadcastStatusUpdate(cwd, state) {
    try {
        // Find the session name for this working directory
        const agentsResponse = await fetch('http://localhost:23000/api/agents');
        if (!agentsResponse.ok) return;

        const agentsData = await agentsResponse.json();
        const agent = (agentsData.agents || []).find(a => {
            const agentWd = a.workingDirectory || a.session?.workingDirectory;
            if (!agentWd) return false;
            // Match exact cwd or strict subdirectory only. A parent dir is NOT
            // an agent's working dir — matching `agentWd.startsWith(cwd)`
            // caused cross-session prompt-injection when cwd was $HOME.
            if (agentWd === cwd) return true;
            if (cwd.startsWith(agentWd + '/')) return true;
            return false;
        });

        if (!agent) return;

        const sessionName = agent.name || agent.alias || agent.session?.tmuxSessionName;
        if (!sessionName) return;

        // Broadcast the status update with all state fields for the 8-state model
        await fetch('http://localhost:23000/api/sessions/activity/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionName,
                status: state.status,
                hookStatus: state.status,
                notificationType: state.notificationType,
                subagentCount: state.subagentCount,
                errorType: state.errorType,
                endReason: state.endReason
            })
        });

        debugLog({ event: 'status_broadcast', sessionName, status: state.status });
    } catch (err) {
        debugLog({ event: 'status_broadcast_error', error: err.message });
    }
}

// Write state to file
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

    const fullState = {
        ...state,
        cwd,
        cwdHash,
        updatedAt: new Date().toISOString()
    };

    fs.writeFileSync(stateFile, JSON.stringify(fullState, null, 2), { mode: 0o600 });
    try { fs.chmodSync(stateFile, 0o600); } catch (e) {}

    // Also write to a "by-cwd" index for easy lookup
    const indexFile = path.join(stateDir, 'index.json');
    let index = {};
    try {
        index = JSON.parse(fs.readFileSync(indexFile, 'utf8'));
    } catch (e) {}
    index[cwd] = cwdHash;
    fs.writeFileSync(indexFile, JSON.stringify(index, null, 2), { mode: 0o600 });
    try { fs.chmodSync(indexFile, 0o600); } catch (e) {}

    // Broadcast status update via WebSocket (fire and forget)
    broadcastStatusUpdate(cwd, state).catch(() => {});
}

// Log to debug file (mode 0600 — see writeState rationale)
function debugLog(data) {
    const debugFile = path.join(os.homedir(), '.aimaestro', 'chat-state', 'hook-debug.log');
    const timestamp = new Date().toISOString();
    const line = `[${timestamp}] ${JSON.stringify(data)}\n`;
    fs.appendFileSync(debugFile, line, { mode: 0o600 });
    try { fs.chmodSync(debugFile, 0o600); } catch (e) {}
}

// Send message notification to agent via tmux
// DECOUPLE-BLOCKED ai-maestro#36 (MANAGER core#11): the two /api/ calls below
// (GET /api/agents to resolve by cwd; POST /api/sessions/{name}/command to type the
// wake-up prompt into the agent's tmux) have NO frozen CLI verb yet —
// `aimaestro-agent.sh` has no `resolve --cwd` and cmd_session only `tmux attach`es
// (no send-command verb). Left functional; flip to the CLI once the verbs land (#36).
// Do NOT patch installed scripts (FROZEN-interface invariant, assistant-manager#16).
async function sendMessageNotification(cwd, messagePrompt) {
    try {
        const agentsResponse = await fetch('http://localhost:23000/api/agents');
        if (!agentsResponse.ok) return false;

        const agentsData = await agentsResponse.json();
        const agent = (agentsData.agents || []).find(a => {
            const agentWd = a.workingDirectory || a.session?.workingDirectory;
            if (!agentWd) return false;
            // Exact cwd or strict subdirectory only — see broadcastStatusUpdate.
            if (agentWd === cwd) return true;
            if (cwd.startsWith(agentWd + '/')) return true;
            return false;
        });

        if (agent && agent.session?.tmuxSessionName) {
            // Send via AI Maestro API
            const response = await fetch(
                `http://localhost:23000/api/sessions/${encodeURIComponent(agent.session.tmuxSessionName)}/command`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        command: messagePrompt,
                        requireIdle: false,  // Hook context ensures appropriate timing
                        addNewline: true
                    })
                }
            );
            const result = await response.json();
            debugLog({ event: 'message_notification_sent', success: result.success, session: agent.session.tmuxSessionName });
            return result.success;
        }
        return false;
    } catch (err) {
        debugLog({ event: 'message_notification_error', error: err.message });
        return false;
    }
}

// Check for unread messages for this agent
// DECOUPLE-BLOCKED ai-maestro#36 (MANAGER core#11): GET /api/agents (resolve by cwd)
// + GET /api/messages (unread count) below. `amp-inbox --count` is the frozen verb for
// the inbox count, but it needs the agent id from the resolve-by-cwd step, and
// `aimaestro-agent.sh` has no `resolve --cwd` verb yet. Left functional; flip the whole
// resolve→count chain to the CLI once the resolve verb lands via #36.
// Do NOT patch installed scripts (FROZEN-interface invariant, assistant-manager#16).
async function checkUnreadMessages(cwd) {
    try {
        // Find agent by working directory
        const agentsResponse = await fetch('http://localhost:23000/api/agents');
        if (!agentsResponse.ok) return null;

        const agentsData = await agentsResponse.json();
        const agents = agentsData.agents || [];

        // Find agent matching this working directory.
        // Match exact cwd or strict subdirectory only. A parent dir is NOT an
        // agent's working dir — the dropped `agentWd.startsWith(cwd + '/')`
        // clause caused cross-session prompt-injection when cwd was $HOME.
        const agent = agents.find(a => {
            const agentWd = a.workingDirectory || a.session?.workingDirectory;
            if (!agentWd) return false;
            if (agentWd === cwd) return true;
            if (cwd.startsWith(agentWd + '/')) return true;
            return false;
        });

        if (!agent) {
            debugLog({ event: 'no_agent_for_cwd', cwd });
            return null;
        }

        // Check for unread messages
        const messagesResponse = await fetch(
            `http://localhost:23000/api/messages?agent=${encodeURIComponent(agent.id)}&box=inbox&status=unread`
        );
        if (!messagesResponse.ok) return null;

        const messagesData = await messagesResponse.json();
        const messages = messagesData.messages || [];

        if (messages.length === 0) return null;

        debugLog({ event: 'unread_messages_found', agentId: agent.id, count: messages.length });

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
        const urgentCount = messages.filter(m => m.priority === 'urgent').length;
        const urgentTag = urgentCount > 0 ? `[${urgentCount} URGENT] ` : '';
        if (messages.length === 1) {
            return `${urgentTag}[AMP-INBOX-NOTIFICATION] 1 new message. Open the agent-messaging skill to read it.`;
        }
        return `${urgentTag}[AMP-INBOX-NOTIFICATION] ${messages.length} new messages. Open the agent-messaging skill to read them.`;
    } catch (err) {
        debugLog({ event: 'message_check_error', error: err.message });
        return null;
    }
}

// Read current subagent count from state file (for SubagentStart/Stop tracking)
function getSubagentCount(cwd) {
    try {
        const stateDir = path.join(os.homedir(), '.aimaestro', 'chat-state');
        const cwdHash = hashCwd(cwd);
        const stateFile = path.join(stateDir, `${cwdHash}.json`);
        const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
        return state.subagentCount || 0;
    } catch (e) {
        return 0;
    }
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
                writeState(cwd, {
                    status: 'waiting_for_input',
                    message: input.message || 'Waiting for your input...',
                    notificationType,
                    sessionId,
                    transcriptPath
                });

                // Check for unread messages and notify the agent
                const messagePrompt = await checkUnreadMessages(cwd);
                if (messagePrompt) {
                    debugLog({ event: 'sending_message_notification', cwd, prompt: messagePrompt, trigger: 'idle_prompt' });
                    await sendMessageNotification(cwd, messagePrompt);
                }
            } else if (notificationType === 'permission_prompt') {
                // For permission prompts, preserve existing tool info if we have it
                const stateDir = path.join(os.homedir(), '.aimaestro', 'chat-state');
                const cwdHash = hashCwd(cwd);
                const stateFile = path.join(stateDir, `${cwdHash}.json`);

                let existingState = {};
                try {
                    if (fs.existsSync(stateFile)) {
                        existingState = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
                        // Only preserve if it's a recent permission_request (within 10 seconds)
                        const age = Date.now() - new Date(existingState.updatedAt).getTime();
                        if (existingState.status !== 'permission_request' || age > 10000) {
                            existingState = {};
                        }
                    }
                } catch (e) {}

                writeState(cwd, {
                    status: 'waiting_for_input',
                    message: input.message || 'Waiting for your input...',
                    notificationType,
                    sessionId,
                    transcriptPath,
                    // Preserve tool info from PermissionRequest if we have it
                    toolName: existingState.toolName,
                    toolInput: existingState.toolInput,
                    options: existingState.options,
                    description: existingState.description || input.message
                });
            } else if (notificationType === 'elicitation_dialog') {
                // MCP server is requesting user input — special blocking state
                writeState(cwd, {
                    status: 'elicitation',
                    message: input.message || 'MCP server requesting input…',
                    notificationType,
                    sessionId,
                    transcriptPath
                });
            }
            break;

        case 'Stop':
            // Claude finished responding — clear the waiting state but preserve subagent count
            {
                const currentSubagents = getSubagentCount(cwd);
                writeState(cwd, {
                    status: currentSubagents > 0 ? 'subagents_running' : 'idle',
                    message: null,
                    subagentCount: currentSubagents,
                    sessionId,
                    transcriptPath
                });
            }
            break;

        case 'StopFailure':
            // Turn ended due to API error (rate limit, auth failure, billing, etc.)
            writeState(cwd, {
                status: 'error',
                message: input.error || input.message || 'API error',
                errorType: input.error_type || input.stop_reason || 'unknown',
                sessionId,
                transcriptPath
            });
            break;

        case 'SessionStart':
            // Session started — reset subagent count and record session info
            writeState(cwd, {
                status: 'active',
                message: null,
                subagentCount: 0,
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
                const count = getSubagentCount(cwd) + 1;
                writeState(cwd, {
                    status: 'subagents_running',
                    message: `${count} subagent${count > 1 ? 's' : ''} running`,
                    subagentCount: count,
                    lastSubagentId: input.agent_id,
                    lastSubagentType: input.agent_type,
                    sessionId,
                    transcriptPath
                });
                debugLog({ event: 'subagent_start', agentId: input.agent_id, type: input.agent_type, count });
            }
            break;

        case 'SubagentStop':
            // Background subagent completed — decrement counter
            {
                const count = Math.max(0, getSubagentCount(cwd) - 1);
                writeState(cwd, {
                    status: count > 0 ? 'subagents_running' : 'active',
                    message: count > 0 ? `${count} subagent${count > 1 ? 's' : ''} running` : null,
                    subagentCount: count,
                    lastSubagentId: input.agent_id,
                    lastSubagentType: input.agent_type,
                    sessionId,
                    transcriptPath
                });
                debugLog({ event: 'subagent_stop', agentId: input.agent_id, type: input.agent_type, count });
            }
            break;

        case 'PreCompact':
            // Context compaction starting — agent temporarily unavailable
            writeState(cwd, {
                status: 'compacting',
                message: 'Context compaction in progress…',
                subagentCount: getSubagentCount(cwd),
                sessionId,
                transcriptPath
            });
            break;

        case 'PostCompact':
            // Context compaction completed — resume active state
            writeState(cwd, {
                status: 'active',
                message: null,
                subagentCount: getSubagentCount(cwd),
                sessionId,
                transcriptPath
            });
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
