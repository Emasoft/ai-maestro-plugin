"""`prrd_lock` must exclude the OTHER writer too (ai-maestro-plugin#54, second half).

ai-maestro shipped `prrdgrep`, a second writer for the same PRRD file, locking via
`lib/json-io.ts::withJsonLock`: the lock is the DIRECTORY `<file>.lock` next to the
target, acquired with a bare non-recursive mkdir (EEXIST == held), stale-broken on
the lockdir's mtime, released with rm -rf. These tests pin the Python side to that
EXACT protocol — the two writers exclude each other only while the lockdir string
and the acquisition semantics match byte-for-byte — and prove the lost-update defect
is gone with two REAL racing processes, not mocks.

The constants (30s stale / 20s max-wait / 50ms poll) were read from the TS source,
not guessed; a lock that excludes nothing is worse than no lock, which is why the
earlier atomicity fix deliberately shipped without one until that source was read.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts" / "prrd-trdd"))

import prrd_lib  # noqa: E402, I001  — must follow the sys.path.insert above

PRRD_EDIT = PLUGIN_ROOT / "scripts" / "prrd-trdd" / "prrd-edit.py"

# A minimal but PARSEABLE constitution: both section markers present so
# render_prrd can re-emit either kind of rule.
SKELETON = (
    "---\n"
    "title: PRRD\n"
    "version: \"1.0.0\"\n"
    "---\n"
    "\n"
    "## 🥇 GOLDEN\n"
    "\n"
    "- **G1.1** — the original golden rule\n"
    "\n"
    "## 🥈 SILVER\n"
    "\n"
    "- **S2.1** — the original silver rule\n"
)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A throwaway project root with a canonical-path PRRD for the lock to guard."""
    prrd = tmp_path / "design" / "requirements" / "PRRD.md"
    prrd.parent.mkdir(parents=True)
    prrd.write_text(SKELETON, encoding="utf-8")
    return tmp_path


def _prrd(project: Path) -> Path:
    return project / "design" / "requirements" / "PRRD.md"


def test_lockdir_string_matches_other_writer(project: Path) -> None:
    """While held, the lock is the DIRECTORY `<file>.lock` — byte-for-byte withJsonLock's string."""
    p = _prrd(project)
    with prrd_lib.prrd_lock(p):
        lock_dir = Path(str(p.resolve()) + ".lock")
        assert lock_dir.is_dir(), "lockdir must exist, as a directory, while held"


def test_lock_released_on_clean_exit(project: Path) -> None:
    """Leaving the context removes the lockdir, exactly like the TS release's rm -rf."""
    p = _prrd(project)
    with prrd_lib.prrd_lock(p):
        pass
    assert not Path(str(p.resolve()) + ".lock").exists()


def test_lock_released_on_exception(project: Path) -> None:
    """A holder that raises must still release — a leaked lockdir stalls every writer for stale_s."""
    p = _prrd(project)
    with pytest.raises(RuntimeError):
        with prrd_lib.prrd_lock(p):
            raise RuntimeError("boom")
    assert not Path(str(p.resolve()) + ".lock").exists()


def test_contention_times_out(project: Path) -> None:
    """A fresh foreign lockdir is respected: acquisition waits, then raises TimeoutError."""
    p = _prrd(project)
    foreign = Path(str(p.resolve()) + ".lock")
    os.mkdir(foreign)  # another process holds the lock, mtime is NOW
    start = time.monotonic()
    with pytest.raises(TimeoutError):
        with prrd_lib.prrd_lock(p, max_wait_s=0.3, poll_s=0.02):
            pass
    assert time.monotonic() - start >= 0.3, "must actually wait before giving up"
    os.rmdir(foreign)


def test_stale_lock_is_broken(project: Path) -> None:
    """A lockdir older than stale_s is a dead holder: break it and acquire."""
    p = _prrd(project)
    foreign = Path(str(p.resolve()) + ".lock")
    os.mkdir(foreign)
    old = time.time() - 120
    os.utime(foreign, (old, old))
    with prrd_lib.prrd_lock(p, stale_s=30.0, max_wait_s=2.0):
        assert foreign.is_dir(), "we now hold a re-created lockdir"
    assert not foreign.exists()


def test_reentrant_nested_acquire(project: Path) -> None:
    """A nested acquire by the same process must not self-deadlock (write_prrd inside an edit op)."""
    p = _prrd(project)
    with prrd_lib.prrd_lock(p, max_wait_s=1.0):
        with prrd_lib.prrd_lock(p, max_wait_s=1.0):  # would deadlock without re-entrancy
            assert Path(str(p.resolve()) + ".lock").is_dir()
    assert not Path(str(p.resolve()) + ".lock").exists(), "outer exit releases exactly once"


def test_write_prrd_takes_the_lock(project: Path) -> None:
    """`write_prrd` itself must respect a foreign holder — direct library callers are covered too.

    write_prrd uses the default 20s wait, so the check is bounded from outside:
    a subprocess attempting the write against a FRESH foreign lockdir must still
    be running (blocked) after 1.5s, where an unlocked writer finishes in ms.
    """
    p = _prrd(project)
    foreign = Path(str(p.resolve()) + ".lock")
    os.mkdir(foreign)
    try:
        code = (
            f"import sys; sys.path.insert(0, r'{PLUGIN_ROOT / 'scripts' / 'prrd-trdd'}')\n"
            "import prrd_lib\n"
            f"doc = prrd_lib.parse_prrd(prrd_lib.Path(r'{p}'))\n"
            "prrd_lib.write_prrd(doc)\n"
        )
        proc = subprocess.Popen([sys.executable, "-c", code], cwd=project)
        try:
            proc.wait(timeout=1.5)
            blocked = False
        except subprocess.TimeoutExpired:
            blocked = True
        finally:
            proc.kill()
            proc.wait()
        assert blocked, "write_prrd must wait on a fresh foreign lockdir, not write through it"
    finally:
        os.rmdir(foreign)


def test_concurrent_edits_both_land(project: Path) -> None:
    """THE defect test: two REAL concurrent `prrd-edit.py add` processes must both survive.

    Before the lock, both parsed the same base and the last writer re-emitted a
    document without the other's rule — silent lost update. With the lock spanning
    parse→write, one serialises behind the other and BOTH rules are present.
    """
    cmds = [
        [sys.executable, str(PRRD_EDIT), "--user", "add", "S", f"racer rule {i}"]
        for i in (1, 2)
    ]
    procs = [subprocess.Popen(c, cwd=project, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for c in cmds]
    outs = [p.communicate(timeout=30) for p in procs]
    for proc, (out, err) in zip(procs, outs):
        assert proc.returncode == 0, f"edit failed: {out!r} {err!r}"
    final = _prrd(project).read_text(encoding="utf-8")
    assert "racer rule 1" in final, "first concurrent edit was lost"
    assert "racer rule 2" in final, "second concurrent edit was lost"
    assert not Path(str(_prrd(project).resolve()) + ".lock").exists(), "no lock leaked"
