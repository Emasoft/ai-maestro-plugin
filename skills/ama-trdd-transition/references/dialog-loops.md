# Dialog loops + INT-owns-completed — the token-saving handshakes

**This is the CANONICAL definition.** Every role plugin
(`amoa-`/`amaa-`/`amia-`/`ampa-`/`amama-`/`amcos-`/autonomous/maintainer)
defers to this file. The loops below are the back-and-forth that PREVENTS
wasted tokens — a MEMBER who codes the wrong thing for 40 minutes is far
more expensive than three short clarifying messages up front.

The fleet workflow has **three dialog loops** and **one ownership rule**:

```text
  ARCH designs TRDD ──► dispatch ──► dev
                                      │
            (a) TASK-COMPREHENSION HANDSHAKE   ORCH ⇄ MEMBER   ← before any code
                                      │
                                      ▼
                                  MEMBER codes
                                      │
            (b) IN-DEV ISSUE DIALOG            MEMBER ⇄ ORCH (⇄ ARCH/INT)   ← any time
                                      │
                                      ▼
            (c) PRE-PR GATE                    MEMBER ⇄ ORCH   ← before PR opens
                                      │
                                      ▼
                                   PR opened ──► INT validates ──► INT flips → complete
                                                 (NOBODY self-marks completed)
```

---

## Contents

- Loop (a) — Task-comprehension handshake (BEFORE coding starts)
- Loop (b) — In-dev issue dialog (DURING coding, any time)
- Loop (c) — Pre-PR gate (BEFORE the PR opens)
- Ownership rule — INTEGRATOR owns the column → `completed` flip
- Why this exists

## Loop (a) — Task-comprehension handshake (BEFORE coding starts)

**When:** the instant a MEMBER is assigned a TRDD (`dispatch → dev`), before
writing a single line of code.

**Who:** ORCHESTRATOR ⇄ assigned MEMBER. Unresolved items escalate to ARCHITECT
(via ORCH — within-team ORCH↔ARCH is a direct edge per R6 v3).

**The MEMBER MUST answer ALL of these before coding:**

1. **Restate the task** in the MEMBER's own words — proves comprehension, not
   echo. ORCH confirms the restatement matches the TRDD's intent.
2. **Files / domains you will touch** — the concrete surface. ORCH cross-checks
   against single-writer-per-domain (does the MEMBER own every domain it named,
   or must it delegate / take a claim?).
3. **Ambiguities** — every part of the TRDD the MEMBER cannot act on without a
   decision. Each ambiguity is resolved here, NOT improvised later.
4. **Foreseen risks / issues** — what could go wrong, what edge cases the TRDD
   didn't mention, what might break downstream.
5. **Anticipated NPT / EHT** — the derived tasks (Necessary Prerequisite Tasks,
   Effects Handling Tasks) the MEMBER expects to spawn. ORCH/ARCH confirm these
   are real and assign/sequence them.

**Resolution path for problems surfaced here:**

- A **comprehension gap** → ORCH clarifies; MEMBER re-restates.
- A **design flaw** (the TRDD's plan is wrong/incomplete) → goes BACK through
  ORCH to ARCHITECT. ARCH revises the TRDD or authors new TRDDs (NPT/EHT, or a
  split). The MEMBER does NOT silently work around a design flaw.
- An **out-of-scope domain** → ORCH delegates that domain to its owner, or the
  MEMBER takes a documented claim (single-writer-per-domain).

The handshake is complete only when EVERY item is answered and ORCH gives the
explicit "go". Coding before the handshake clears is a process violation.

---

## Loop (b) — In-dev issue dialog (DURING coding, any time)

**When:** the moment a MEMBER hits ANY issue, ambiguity, or blocker mid-dev.

**Who:** MEMBER ⇄ ORCH immediately. ORCH pulls in the right authority:

- **design problem** → ARCHITECT (the TRDD's plan needs to change).
- **CI / merge / branch / release problem** → INTEGRATOR.

**The rule:** never silently improvise around a design flaw. A MEMBER who
discovers the design is wrong STOPS and routes it through ORCH — improvising a
workaround produces code that doesn't match the TRDD, which INT will reject at
the completed-gate anyway (so the improvisation is pure wasted tokens).

A blocker that needs another TRDD to land first → the MEMBER's TRDD goes
`dev → blocked` with the blocker in `blocked-by:`; ORCH manages the red column.

---

## Loop (c) — Pre-PR gate (BEFORE the PR opens)

**When:** the MEMBER believes the work is done and is about to open a PR (or
notify INTEGRATOR).

**Who:** MEMBER ⇄ ORCH. The MEMBER must clear **"I believe it's done — PR now?"**
with ORCH BEFORE opening the PR or pinging INT.

**Why:** this protects INTEGRATOR tokens. A premature or incomplete PR forces
INT to spend a full review cycle discovering the work isn't ready. The pre-PR
gate is ORCH's cheap sanity check (are all acceptance criteria addressed? all
EHTs terminal? tests green locally?) that catches the obvious-incomplete case
before it reaches the expensive reviewer.

ORCH says "go" → MEMBER opens the PR and the TRDD advances toward `testing` /
`ai_review`. ORCH says "not yet" → back to loop (b) with the specific gap.

---

## Ownership rule — INTEGRATOR owns the column → `completed` flip

**Nobody self-marks a TRDD `completed`.** Not the MEMBER who wrote the code, not
the ORCHESTRATOR who coordinated it.

**INTEGRATOR validates the MERGED PR actually satisfies the TRDD** — every
acceptance criterion met, every EHT terminal, tests green in CI — and only then
flips the column to `complete`. INT is the single writer of the completed-state
for the same reason a developer doesn't approve their own PR: the author is the
worst-placed person to judge "is it actually done".

This is the post-merge counterpart of loop (c): loop (c) is ORCH's pre-PR sanity
check; the completed-flip is INT's post-merge acceptance check. ORCH does **not**
own the final flip.

(Mechanically, `testing → ai_review` and the soak transitions remain as in
[column-transitions.md](column-transitions.md); the load-bearing change is that
the move INTO `complete` is performed by INTEGRATOR after PR-satisfies-TRDD
validation, never self-assigned by the author.)

---

## Why this exists

The three loops + the ownership rule are not bureaucracy — each one closes a
concrete token-waste hole:

| Loop / rule | Hole it closes |
|---|---|
| (a) comprehension handshake | MEMBER codes the wrong thing because it misread the TRDD |
| (b) in-dev dialog | MEMBER improvises around a design flaw → code that must be thrown away |
| (c) pre-PR gate | INT burns a review cycle on an obviously-incomplete PR |
| INT-owns-completed | a half-done TRDD is marked done by its optimistic author and ships broken |

A few short messages at the right moment are always cheaper than a wrong
implementation discovered late.
