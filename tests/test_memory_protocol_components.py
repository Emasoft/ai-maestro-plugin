"""Tests for this plugin's memory-protocol surface.

Real tests only (no mocks, per this project's no-mock rule).

CORE no longer hosts or ships `memgrep`. Per the ai-maestro ownership ruling
(`Emasoft/ai-maestro#106`) the **ai-maestro-janitor** owns the crate and
publishes the binaries; CORE's vendored copy was a 4806-LOC subset of the
janitor's 12354-LOC crate, shipped under the same binary name and the same
`version = "0.1.0"`. What remains here is the `memory-search` skill, which
CONSUMES that binary, plus a regression guard proving CORE does not ship a
rival one.
"""

from __future__ import annotations

from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class TestCanonicalArtifacts:
    """CORE's memory-protocol surface: what it consumes, and what it must NOT ship."""

    def test_memory_search_disambiguates_from_global_wiki_recall(self) -> None:
        """memory-search points at the janitor GLOBAL wiki-memory skills as its complement."""
        text = (PLUGIN_ROOT / "skills" / "memory-search" / "SKILL.md").read_text()
        assert "/janitor-memory-recall" in text
        assert "/janitor-memory-write" in text

    def test_core_does_not_ship_a_rival_memgrep(self) -> None:
        """CORE vendors no memgrep crate and publishes no memgrep asset (ai-maestro#106).

        This is a REGRESSION GUARD, not bookkeeping. CORE once vendored a 4806-LOC
        subset of the janitor's crate under the SAME binary name and the SAME
        `version = "0.1.0"`, and release.yml shipped it. Whichever build won
        `cargo install` last owned `~/.cargo/bin/memgrep`, and `--version` could not
        tell them apart — so a host that installed CORE's could not run
        `memgrep validate|lint|add-atom|add-lesson|new-page`, which
        `~/.claude/rules/markdown-memory-recall.md` MANDATES after every memory edit.
        Re-vendoring it would silently break that machine-wide protocol again.
        """
        assert not (PLUGIN_ROOT / "scripts" / "memgrep").exists()
        assert not (PLUGIN_ROOT / "scripts" / "install-memgrep.sh").exists()
        wf = (PLUGIN_ROOT / ".github" / "workflows" / "release.yml").read_text()
        assert "build-memgrep:" not in wf
        assert "memgrep-darwin-arm64" not in wf
