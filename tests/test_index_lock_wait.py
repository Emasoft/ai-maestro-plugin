#!/usr/bin/env python3
"""Publish must survive a concurrent git holding `.git/index.lock`.

Two publishes died mid-run here (v3.1.1, v3.1.7), each time at step 10 and each
time leaving the version-bump artifacts on disk. Measured cause (git 2.55.0, 120
iterations per arm, the watcher validated against a `git add` positive control):

    git status --porcelain              -> .git/index.lock OBSERVED
    git --no-optional-locks status …    -> never observed
    GIT_OPTIONAL_LOCKS=0 git status …   -> never observed

`git status` takes the lock to refresh its stat cache. This machine runs a
5-minute janitor heartbeat whose detectors run `git status` on every project, and
a publish's window is minutes wide, so the overlap is not unlucky — it is
scheduled. The reason it looked random is the asymmetry: `git status` fails SOFT
(exit 0 even when denied the lock), so the reader never reports anything, while
the writer dies.

Real repos and real git throughout — the whole subject is what git does with a
file on disk, so a mocked runner would be testing the mock.
"""
from __future__ import annotations

import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish  # noqa: E402


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "r"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@e.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "T"], check=True)
    (repo / "a.txt").write_text("one\n")
    subprocess.run(["git", "-C", str(repo), "add", "a.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "init"], check=True)
    return repo


def test_a_held_lock_really_does_break_git_add(tmp_path: Path) -> None:
    """The premise, falsified first: without the wait, `git add` FAILS.

    If this ever goes green-by-passing (git stops caring about the lock), every
    other test in this file is testing a scenario that cannot happen, and they
    should be deleted rather than trusted.
    """
    repo = _repo(tmp_path)
    (repo / ".git" / "index.lock").write_text("held\n")
    (repo / "b.txt").write_text("two\n")
    r = subprocess.run(["git", "-C", str(repo), "add", "b.txt"], capture_output=True, text=True)
    assert r.returncode != 0, "a held index.lock no longer breaks `git add` — this suite is obsolete"
    assert "index.lock" in (r.stderr + r.stdout)


def test_no_lock_returns_immediately(tmp_path: Path) -> None:
    """The common path costs nothing: no lock, no wait, no output."""
    repo = _repo(tmp_path)
    started = time.monotonic()
    publish._await_index_lock(repo)
    assert time.monotonic() - started < 1.0


def test_it_waits_for_a_transient_lock_and_then_proceeds(tmp_path: Path) -> None:
    """A lock held briefly by a concurrent reader is waited out, not failed on.

    0.4s stands in for the milliseconds a real `git status` holds it; the assert
    is that the call BLOCKED (did not return early and did not raise), which is
    the whole behavioural difference from the version that died.
    """
    repo = _repo(tmp_path)
    lock = repo / ".git" / "index.lock"
    lock.write_text("held\n")
    threading.Timer(0.4, lock.unlink).start()
    started = time.monotonic()
    publish._await_index_lock(repo)
    waited = time.monotonic() - started
    assert waited >= 0.35, f"returned after {waited:.2f}s — it did not actually wait"
    assert not lock.exists()


def test_a_lock_that_never_clears_fails_fast_and_loudly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Waiting is bounded. It exits non-zero and NEVER unlinks the lock itself.

    Deleting another process's lock corrupts the index it protects, so the
    recovery stays manual and the message says how — a publish that silently
    stole the lock would trade a visible failure for an invisible one.
    """
    repo = _repo(tmp_path)
    lock = repo / ".git" / "index.lock"
    lock.write_text("held\n")
    monkeypatch.setattr(publish, "_LOCK_WAIT_S", 0.2)
    with pytest.raises(SystemExit) as exc:
        publish._await_index_lock(repo)
    assert exc.value.code == 1
    assert lock.exists(), "the lock was removed — publish must never unlink a foreign lock"
    assert "index.lock" in capsys.readouterr().out


def test_run_awaits_only_for_subcommands_that_write_the_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Routing: `add`/`commit` wait, reads and non-git commands do not.

    A wait in front of every git call would serialise publish behind its own
    reads for no benefit; a wait in front of none of them is the bug. `echo add`
    is the load-bearing negative — the check must look at the command, not for
    the word anywhere in the argv.
    """
    calls: list[Path | None] = []
    monkeypatch.setattr(publish, "_await_index_lock", lambda cwd: calls.append(cwd))
    repo = _repo(tmp_path)
    (repo / "c.txt").write_text("three\n")

    publish.run(["git", "--no-optional-locks", "status", "--porcelain"], cwd=repo, capture=True)
    assert calls == [], "waited before a read-only status"

    publish.run(["echo", "add"], cwd=repo, capture=True)
    assert calls == [], "waited before a non-git command whose ARGUMENT is 'add'"

    publish.run(["git", "add", "c.txt"], cwd=repo)
    assert calls == [repo], "did not wait before `git add`"


def test_git_dir_resolves_a_linked_worktree_rather_than_guessing(tmp_path: Path) -> None:
    """In a worktree `.git` is a FILE; the lock lives in the main repo's git dir.

    Guessing `cwd/.git/index.lock` would watch a path that never appears, so the
    wait would pass instantly and the publish would die exactly as before — a
    guard that is green precisely when it is not working.
    """
    repo = _repo(tmp_path)
    wt = tmp_path / "wt"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", str(wt), "-b", "side"], check=True)
    assert (wt / ".git").is_file(), "expected a worktree pointer file, not a directory"
    resolved = publish._git_dir(wt)
    assert resolved is not None
    assert resolved.is_dir()
    assert (repo / ".git").resolve() in resolved.resolve().parents or resolved.resolve().is_relative_to(
        (repo / ".git").resolve()
    )


def test_end_to_end_a_publish_style_add_survives_a_concurrent_holder(tmp_path: Path) -> None:
    """The actual failure, reproduced and then survived.

    Same shape as the two dead publishes: something else holds the index while
    the release commit stages its files. With the wait in `run()`, the add lands.
    """
    repo = _repo(tmp_path)
    lock = repo / ".git" / "index.lock"
    lock.write_text("held by a concurrent git\n")
    (repo / "d.txt").write_text("four\n")
    threading.Timer(0.5, lock.unlink).start()

    publish.run(["git", "add", "d.txt"], cwd=repo)

    staged = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
    )
    assert "d.txt" in staged.stdout
