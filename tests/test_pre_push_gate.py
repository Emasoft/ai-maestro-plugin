"""Tests for the pre-push gate's process-ancestry check (TRDD-4b298890 L1 + T0).

`.githooks/pre-push` is a STATIC committed bash hook activated via
`core.hooksPath=.githooks`. It refuses every `git push` whose process-ancestry
does NOT include a genuine python/uv invocation of THIS repo's
`scripts/publish.py`. The original matcher did a pure argv substring test, so a
shell whose argv merely CONTAINED `python … scripts/publish.py` (bash -c,
python -c, exec -a) sailed through. The hardened matcher reads BOTH `ps -o comm=`
(real interpreter basename) and `ps -o command=` (full argv) and accepts only a
true python/uv interpreter whose first non-flag argument realpaths to the repo's
publish.py.

These tests drive the hook end-to-end as a real subprocess (no mocks, per this
project's no-mock rule) inside a THROWAWAY git repo in tmp_path — they never
touch the real repo and never actually push. Each scenario builds a real
ANCESTOR process whose argv is the payload, which then runs the hook as a
descendant, so the hook's upward `ps` walk observes exactly that ancestor.

Failing-first: the three spoof payloads (bash -c / python -c / exec -a) MUST
yield exit 1 — on the pre-hardening hook they yielded exit 0. Regression arm:
genuine `python scripts/publish.py` and `uv run python scripts/publish.py`
ancestry MUST yield exit 0 (a too-strict matcher here BRICKS all publishing),
and a bare push with no publish ancestor MUST yield exit 1.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REAL_HOOK = PLUGIN_ROOT / ".githooks" / "pre-push"

# The hook is bash; a POSIX `sh`/`bash` and `git` are required to drive it. Skip
# (fail-fast, not a mock) when the toolchain is unavailable.
pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None or shutil.which("git") is None,
    reason="bash and git are required to exercise the pre-push hook (no mock substitute)",
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def hook_repo(tmp_path: Path) -> Path:
    """A throwaway git repo wired exactly like the real one for the hook.

    Contains a COPY of the real `.githooks/pre-push` and a dummy
    `scripts/publish.py` whose realpath is what the hardened hook must match
    (`<git_root>/scripts/publish.py`). `core.hooksPath` points at `.githooks`,
    mirroring the activation `install_hook` performs. The hook is always invoked
    with cwd == this repo, so its `git rev-parse --show-toplevel` resolves HERE
    — which makes the suite hermetic: even if the *real* publish.py happens to
    be an ancestor (running the suite via the gate), its path differs from this
    repo's, so it can never spoof a match.
    """
    repo = tmp_path / "repo"
    (repo / ".githooks").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    _git(repo, "init", "-q")
    # The dummy publish.py only needs to EXIST so its path realpath-resolves;
    # the hook checks the path, never executes it.
    (repo / "scripts" / "publish.py").write_text("# dummy publish.py for path match\n")
    hook = repo / ".githooks" / "pre-push"
    shutil.copy2(REAL_HOOK, hook)
    hook.chmod(0o755)
    _git(repo, "config", "core.hooksPath", ".githooks")
    return repo


def _write_publish_launcher(repo: Path) -> Path:
    """Make the repo's `scripts/publish.py` a launcher that runs the hook.

    When a real python interpreter runs THIS file, the interpreter frame's argv
    is `<python> <repo>/scripts/publish.py`, so the hook's first-positional
    realpath check matches EXPECTED_PUBLISH — i.e. it faithfully reproduces the
    genuine `python scripts/publish.py` shape. The launcher runs the hook as a
    child (so the interpreter frame is the hook's ancestor) and propagates its
    exit code.
    """
    publish = repo / "scripts" / "publish.py"
    hook = repo / ".githooks" / "pre-push"
    publish.write_text(
        textwrap.dedent(
            f"""\
            import subprocess, sys
            r = subprocess.run(["bash", {str(hook)!r}], cwd={str(repo)!r})
            sys.exit(r.returncode)
            """
        )
    )
    return publish


def run_hook(argv: list[str], repo: Path) -> int:
    """Run `argv` (the constructed ancestor) with cwd==repo; return exit code.

    `argv` is a real command that, as a side effect, runs the repo's hook as a
    descendant. Its return code is the hook's exit code (the launchers and the
    spoof shells all propagate it).
    """
    proc = subprocess.run(
        argv,
        cwd=str(repo),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return proc.returncode


# ── Failing-first: SPOOF payloads. The hook MUST DENY (exit 1). ──
# Pre-hardening these all yielded exit 0 (pure argv substring match).


def test_spoof_bash_c_echo_denies(hook_repo: Path) -> None:
    """bash -c with `python scripts/publish.py` in an echo string → exit 1."""
    hook = hook_repo / ".githooks" / "pre-push"
    # bash stays the hook's PARENT (no exec) and its argv carries the spoof text;
    # comm=bash fails the python/uv family check.
    argv = [
        "bash",
        "-c",
        f'echo "python scripts/publish.py preview"; bash {str(hook)!r}',
    ]
    assert run_hook(argv, hook_repo) == 1


def test_spoof_python_dash_c_argv_denies(hook_repo: Path) -> None:
    """python -c with a sys.argv spoof → exit 1 (the -c arg is rejected)."""
    hook = hook_repo / ".githooks" / "pre-push"
    code = (
        "import os,sys,subprocess; "
        'sys.argv=["python","scripts/publish.py"]; '
        f"sys.exit(subprocess.run(['bash', {str(hook)!r}], cwd={str(hook_repo)!r}).returncode)"
    )
    argv = [sys.executable, "-c", code]
    assert run_hook(argv, hook_repo) == 1


def test_spoof_exec_a_argv0_denies(hook_repo: Path) -> None:
    """exec -a "python scripts/publish.py" bash → exit 1 (comm stays bash)."""
    hook = hook_repo / ".githooks" / "pre-push"
    # exec -a rewrites argv[0] of the inner bash to the spoof string, but its
    # comm remains `bash`; the comm-vs-argv[0] agreement check rejects it.
    argv = [
        "bash",
        "-c",
        f'exec -a "python scripts/publish.py" bash -c "bash {str(hook)!r}"',
    ]
    assert run_hook(argv, hook_repo) == 1


# ── Regression: GENUINE ancestry MUST ADMIT (exit 0). A too-strict matcher
#    here bricks all publishing — these are the brick-risk guards. ──


def test_genuine_python_publish_admits(hook_repo: Path) -> None:
    """python scripts/publish.py ancestry → exit 0 (real publish shape).

    Uses the REAL interpreter (sys.executable) — no faked binary — because the
    interpreter's true comm basename is platform-specific (macOS framework
    `Python`, Linux `python3.NN`) and the hook's family check must admit both.
    The argv is `<real-python> <repo>/scripts/publish.py`, exactly the genuine
    non-uv launch shape.
    """
    publish = _write_publish_launcher(hook_repo)
    assert run_hook([sys.executable, str(publish)], hook_repo) == 0


@pytest.mark.skipif(
    shutil.which("uv") is None,
    reason="uv is required to exercise the genuine `uv run python …` ancestry",
)
def test_genuine_uv_run_python_publish_admits(hook_repo: Path) -> None:
    """uv run python scripts/publish.py ancestry → exit 0 (the #1 prod shape).

    Drives the REAL `uv` so the full `uv → python → hook` chain is exercised
    honestly. The hook must admit via the PYTHON frame (venv python's comm
    basename is `python3`/`python`, first positional realpaths to publish.py) —
    there is intentionally NO uv-argv branch (it would be spoofable, see the two
    spoof tests below). `--no-project` keeps uv from resolving the throwaway repo.
    """
    publish = _write_publish_launcher(hook_repo)
    argv = ["uv", "run", "--no-project", "python", str(publish)]
    assert run_hook(argv, hook_repo) == 0


@pytest.mark.skipif(
    shutil.which("uv") is None,
    reason="uv is required to exercise the `uv run …` argv-spoof payload",
)
def test_spoof_uv_run_path_in_argv_denies(hook_repo: Path) -> None:
    """`uv run … <publish-path>` where NO python runs publish.py → exit 1.

    comm=uv passes the family check and uv's argv carries the publish.py path as a
    clean token, but the only descendant interpreter is bash (running the hook) —
    publish.py is never executed. The removed loose "comm==uv AND an argv token
    ends in publish.py" branch would have ADMITTED this (bypass); the strict gate
    denies it (uv's first positional is `run`; bash fails the family check).
    """
    publish = hook_repo / "scripts" / "publish.py"
    hook = hook_repo / ".githooks" / "pre-push"
    # The -c script runs the hook; the trailing arg (the publish path) becomes $0,
    # so it appears as a clean token in uv's argv without ever being executed.
    argv = ["uv", "run", "--no-project", "bash", "-c", f"bash {str(hook)!r}", str(publish)]
    assert run_hook(argv, hook_repo) == 1


@pytest.mark.skipif(
    shutil.which("uv") is None,
    reason="uv is required to exercise the `uv run python -c …` spoof payload",
)
def test_spoof_uv_run_python_dash_c_denies(hook_repo: Path) -> None:
    """`uv run python -c '<evil>' <publish-path>` → exit 1.

    A real python frame exists but its first argument is `-c` (rejected by (d)),
    with publish.py a mere argv string — not the interpreter target. The strict
    check denies the python frame on `-c`; with no loose uv-argv branch the uv
    frame denies too.
    """
    publish = hook_repo / "scripts" / "publish.py"
    hook = hook_repo / ".githooks" / "pre-push"
    code = f"import subprocess,sys; sys.exit(subprocess.run(['bash', {str(hook)!r}], cwd={str(hook_repo)!r}).returncode)"
    argv = ["uv", "run", "--no-project", "python", "-c", code, str(publish)]
    assert run_hook(argv, hook_repo) == 1


def test_bare_push_no_publish_ancestor_denies(hook_repo: Path) -> None:
    """A bare hook invocation with no publish ancestor → exit 1 (baseline)."""
    hook = hook_repo / ".githooks" / "pre-push"
    # The only ancestors are pytest's interpreter and this bash; neither targets
    # THIS repo's publish.py, so the gate refuses.
    assert run_hook(["bash", str(hook)], hook_repo) == 1


# ── Contributor path (TRDD-8ZVAPMSQ): verdicts decided from the pre-push
# stdin refspecs, exercised with NO publish ancestor anywhere. Real hook,
# real stdin, no mocks. Line format: `<lref> SP <lsha> SP <rref> SP <rsha>`.


def _run_hook_stdin(hook_repo: Path, refspecs: str) -> int:
    """Feed refspec lines to the real hook over a pipe; return its exit code."""
    hook = hook_repo / ".githooks" / "pre-push"
    proc = subprocess.run(
        ["bash", str(hook)],
        input=refspecs,
        cwd=str(hook_repo),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return proc.returncode


def test_feature_branch_push_allowed_without_ancestry(hook_repo: Path) -> None:
    """All remote refs are non-default branches → exit 0, no publish needed."""
    # hook_repo has no origin remote, so the hook's default-branch resolution
    # falls back to `main`; `feature/x` is therefore a non-default branch.
    assert _run_hook_stdin(hook_repo, "refs/heads/feature/x a1 refs/heads/feature/x b2\n") == 0


def test_default_branch_push_still_requires_ancestry(hook_repo: Path) -> None:
    """A remote ref hitting the default branch → the ancestry gate refuses."""
    assert _run_hook_stdin(hook_repo, "refs/heads/main a1 refs/heads/main b2\n") == 1


def test_tag_push_still_requires_ancestry(hook_repo: Path) -> None:
    """A tag ref → the ancestry gate refuses (releases stay publish-only)."""
    assert _run_hook_stdin(hook_repo, "refs/tags/v9.9.9 a1 refs/tags/v9.9.9 b2\n") == 1


def test_mixed_feature_and_tag_push_refused(hook_repo: Path) -> None:
    """One conforming ref does not launder a push that also moves a tag."""
    lines = "refs/heads/feature/x a1 refs/heads/feature/x b2\nrefs/tags/v9.9.9 c3 refs/tags/v9.9.9 d4\n"
    assert _run_hook_stdin(hook_repo, lines) == 1
