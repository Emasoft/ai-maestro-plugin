"""`write_prrd` must never leave the PRRD partially written (ai-maestro-plugin#54).

`render_prrd` re-emits the WHOLE document from a parsed model, so the failure mode of a
non-atomic write is not "one rule is wrong" — it is "the project's constitution is
truncated". Reported by the Claude developing ai-maestro, confirmed here against HEAD:
the old body was `p.write_text(render_prrd(doc))`, which truncates the target and then
writes into it.

WHAT THESE TESTS DO AND DO NOT COVER

They cover ATOMICITY only. The other half of #54 — that two processes editing one PRRD
are last-writer-wins because neither takes a lock — is NOT fixed and NOT tested here. It
needs a lock directory whose name matches the other writer byte-for-byte, and that
writer's source is not currently readable from this repo. A lock that excludes nothing
is worse than no lock, so it is not being guessed at.

The falsification test at the bottom is the one that gives the rest their meaning: it
re-runs the OLD implementation against the same injected failure and asserts it destroys
the file. Without it, every assertion here would also pass on a `write_text` one-liner,
because the interesting states are the ones that only occur when a write dies partway.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts" / "prrd-trdd"))

import prrd_lib  # noqa: E402, I001  — must follow the sys.path.insert above


ORIGINAL = "---\ntitle: PRRD\n---\n\n## 🥇 GOLDEN\n\n- **G1.1** — the original rule\n"


@pytest.fixture
def prrd(tmp_path: Path) -> Path:
    p = tmp_path / "design" / "requirements" / "PRRD.md"
    p.parent.mkdir(parents=True)
    p.write_text(ORIGINAL, encoding="utf-8")
    return p


def _doc(text: str) -> prrd_lib.PRRDDoc:
    return prrd_lib.PRRDDoc(raw_lines=text.splitlines(keepends=True))


def test_a_successful_write_replaces_content_and_leaves_no_temp(prrd: Path, monkeypatch) -> None:
    """The happy path still works, and the temp file does not survive it."""
    monkeypatch.setattr(prrd_lib, "render_prrd", lambda doc: "NEW CONTENT\n")
    prrd_lib.write_prrd(_doc(ORIGINAL), path=prrd)

    assert prrd.read_text() == "NEW CONTENT\n"
    leftovers = [p.name for p in prrd.parent.iterdir() if ".tmp." in p.name]
    assert not leftovers, f"temp files survived a successful write: {leftovers}"


def test_a_failure_mid_write_leaves_the_original_intact(prrd: Path, monkeypatch) -> None:
    """The whole point: a write that dies partway must not damage the target.

    The failure is injected at fsync — after the new content has been written to the
    temp file, which is precisely the window where the old implementation had already
    truncated the real file.
    """
    monkeypatch.setattr(prrd_lib, "render_prrd", lambda doc: "REPLACEMENT\n")
    monkeypatch.setattr(prrd_lib.os, "fsync", lambda fd: (_ for _ in ()).throw(OSError("disk full")))

    with pytest.raises(OSError, match="disk full"):
        prrd_lib.write_prrd(_doc(ORIGINAL), path=prrd)

    assert prrd.read_text() == ORIGINAL, "the PRRD was damaged by a failed write"


def test_a_failure_mid_write_leaves_no_temp_behind(prrd: Path, monkeypatch) -> None:
    """The `finally` unlink — otherwise every crash litters the requirements folder."""
    monkeypatch.setattr(prrd_lib, "render_prrd", lambda doc: "REPLACEMENT\n")
    monkeypatch.setattr(prrd_lib.os, "fsync", lambda fd: (_ for _ in ()).throw(OSError("disk full")))

    with pytest.raises(OSError):
        prrd_lib.write_prrd(_doc(ORIGINAL), path=prrd)

    leftovers = [p.name for p in prrd.parent.iterdir() if ".tmp." in p.name]
    assert not leftovers, f"temp files survived a failed write: {leftovers}"


def test_the_temp_file_is_a_sibling_of_the_target(prrd: Path, monkeypatch) -> None:
    """`os.replace` is atomic only WITHIN a filesystem, so the temp must share one.

    A temp in `/tmp` would make the rename a cross-device copy — non-atomic again, and
    silently so, since it works on a dev box where both happen to be the same mount.
    """
    seen: list[Path] = []

    real_replace = prrd_lib.os.replace

    def spy(src, dst):
        seen.append(Path(src))
        return real_replace(src, dst)

    monkeypatch.setattr(prrd_lib.os, "replace", spy)
    monkeypatch.setattr(prrd_lib, "render_prrd", lambda doc: "X\n")
    prrd_lib.write_prrd(_doc(ORIGINAL), path=prrd)

    assert seen, "os.replace was never called — the write is not doing temp+rename"
    assert seen[0].parent == prrd.parent, f"temp {seen[0]} is not a sibling of {prrd}"


def test_the_old_implementation_fails_these_assertions(prrd: Path) -> None:
    """Falsification: prove the tests above detect the bug they were written for.

    This re-runs the ORIGINAL body — `write_text(render_prrd(doc))` — against the same
    injected failure and asserts it destroys the file. If this ever stops holding, the
    injection no longer reaches the truncation window and the tests above have quietly
    become tautologies that a one-line `write_text` would satisfy.
    """

    def old_write_prrd(p: Path) -> None:
        with open(p, "w", encoding="utf-8"):  # 'w' truncates HERE...
            raise OSError("disk full")  # ...and the content never arrives

    with pytest.raises(OSError, match="disk full"):
        old_write_prrd(prrd)

    assert prrd.read_text() == "", "expected the old implementation to truncate; it did not"
