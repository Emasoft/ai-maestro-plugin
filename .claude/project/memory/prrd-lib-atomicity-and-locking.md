---
name: prrd-lib-atomicity-and-locking
description: "why is write_prrd not a simple write_text / the PRRD came back half empty after a crash / a failed write destroyed the rules file / is my atomicity test actually testing anything / os.replace across filesystems / why must the temp file be a sibling / two writers edit the PRRD concurrently / lost update last writer wins on PRRD / prrd_lock protocol mkdir lockdir / prrdgrep and prrd-edit interop / where do the lock constants come from"
ocd: 2026-08-05
lmd: 2026-08-29
metadata:
  node_type: memory
  type: project
  tier: component
  globs: ["rules/**"]
publish-globally: false
split-lineage: cc9840b5939c4effac960eb58cab1b1e
---

# prrd-lib-atomicity-and-locking

`scripts/prrd-trdd/prrd_lib.py`'s two safety mechanisms for `design/requirements/PRRD.md`:
the atomic temp+rename write, and the cross-process file lock two independent writers share.

^ATOM-53N0-V0IF [desc:"write_prrd in scripts/prrd-trdd/prrd_lib.py is atomic temp+rename because it re-emits the WHOLE PRRD — a failed plain write partially ERASED the project constitution (#54)", keywords: the_PRRD_came_back_half_empty_after_a_crash a_failed_write_destroyed_the_rules_file why_is_write_prrd_not_a_simple_write_text is_my_atomicity_test_actually_testing_anything os.replace_across_filesystems why_must_the_temp_file_be_a_sibling, ocd: 2026-08-13, lmd: 2026-08-13]

`write_prrd` in `scripts/prrd-trdd/prrd_lib.py` writes ATOMICALLY via temp+rename, and the reason
is severity, not tidiness: `render_prrd` re-emits the WHOLE document from a parsed model, so the
previous `p.write_text(render_prrd(doc))` truncated the target first. A crash, a full disk, or a
SIGKILL mid-write did not leave one rule wrong — it left the project's constitution PARTIALLY
ERASED (`edfdae9`, #54).

Three details carry the guarantee and NONE is incidental:

- **The temp is a SIBLING of the target.** `os.replace` is atomic only WITHIN one filesystem. A
  `/tmp` staging file silently degrades to a cross-device copy — and still passes on a dev box
  where `/tmp` and the repo are the same mount, so the regression is invisible exactly where it
  is tested.
- **`fsync` precedes the rename**, so the bytes are durable before the name points at them.
- **The `finally` unlink** is a no-op after a successful replace and removes the temp on every
  failure path, so a crash cannot litter `design/requirements/`.

Atomicity is not serialisation: the locking half of #54 landed separately — see `ATOM-JONB-6FIU` on this page. What proves this atomicity is tested rather than asserted is `ATOM-FLE3-FVEX`.


^ATOM-FLE3-FVEX [desc:"the write_prrd atomicity suite is only meaningful because of its 5th test — the falsification control that re-runs the OLD body and asserts it DOES destroy the file", keywords: my_atomicity_test_passes_but_would_it_pass_on_the_broken_version_too how_do_I_know_an_injected-failure_test_reaches_the_failure_window a_suite_that_became_a_tautology_without_anyone_noticing testing_os.replace_was_actually_called_not_just_that_content_changed, ocd: 2026-08-13, lmd: 2026-08-13]

The `write_prrd` atomicity suite (see `ATOM-53N0-V0IF` on this page) is meaningful ONLY because of
its fifth test. Every other assertion in it would ALSO pass against the old `write_text` one-liner,
because the interesting states exist only when a write dies partway — so passing proves nothing
about atomicity on its own.

The fifth test re-runs the OLD body against the SAME injected failure and asserts it DOES destroy
the file. That is the control: if it ever stops holding, the injection no longer reaches the
truncation window and the whole suite has quietly become a tautology that cannot fail.

Two assertions in the same suite exist for the same reason — that `os.replace` is actually CALLED
(not merely that the file's content changed, which a plain write also achieves), and that its
source is a SIBLING of the target, since the cross-device degradation has no other witness on a
box where the temp dir and the repo share a mount.


^ATOM-JONB-6FIU [desc:"prrd_lib.prrd_lock mirrors ai-maestro withJsonLock byte-for-byte (<file>.lock mkdir-dir, 30s/20s/50ms) and must span each edit's whole parse-to-write, not just the write", keywords: two_writers_edit_the_prrd_concurrently lost_update_last_writer_wins_on_prrd prrd_lock_protocol_mkdir_lockdir why_does_prrd_lock_span_parse_to_write prrdgrep_and_prrd-edit_interop where_do_the_lock_constants_come_from, ocd: 2026-08-05, lmd: 2026-08-05]

Two independent writers edit `design/requirements/PRRD.md`: CORE's `prrd-edit.py` and
ai-maestro's `prrdgrep`. They exclude each other ONLY because the lock protocol matches
byte-for-byte — the lock is the DIRECTORY `<file>.lock` beside the target, acquired with a
bare non-recursive mkdir (EEXIST == held), stale-broken past 30s of lockdir mtime, released
by recursively deleting the lockdir, 20s max wait at 50ms polls (`prrd_lib.prrd_lock`,
shipped for #54). The constants were READ from `ai-maestro lib/json-io.ts::withJsonLock`,
never chosen — change them only in lockstep with that source. The lock must span each edit
op's WHOLE parse→write (as prrd-edit.py does): serialising only the write still loses
updates, because both editors parse the same base and the last full re-emission drops the
other's rule. `write_prrd` also takes the lock re-entrantly for direct library callers.
Real-process race + blocked-writer tests: `tests/test_prrd_write_lock.py`.

## Governed by
- [[architecture]] — the functionality hub this component sits under (its `## Applies to`
  carries the reciprocal link).

## Notes and lessons learned
(none yet)
