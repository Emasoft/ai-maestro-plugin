# TRDD frontmatter — canonical schema

**Scope:** Field-by-field schema for the YAML frontmatter of a v2 TRDD.
Consumed by `findtrdd.py`, `kanban.py`, validators, and per-role skills.
The schema is **open** — agents may add project-specific fields without
breaking the canonical set, but the canonical set MUST be respected
verbatim.

## Contents

- Schema invariants (grep-friendliness)
- Field schema
- Type forms
- Schema extension
- Validation
- Migration from v1
- Anti-patterns

## Schema invariants (grep-friendliness)

Every field is engineered to answer a real grep question in one line.

1. **One field per line.** No multi-line strings, no folded scalars
   (`>`, `|`), no nested mappings.
2. **Lists are flow-style.** `[a, b, c]` — never block style.
3. **Enum values are bare kebab-case.** Never quoted.
4. **Titles never contain colons.** Use em-dash or hyphen for sub-clauses.
5. **Dates are ISO 8601 with local TZ offset.** Format
   `YYYY-MM-DDTHH:MM:SS±HHMM`. Generate via `date +%Y-%m-%dT%H:%M:%S%z`.
6. **No trailing whitespace, no trailing comments.**

## Field schema

### 1. Identity (mandatory on every TRDD)

| Field | Type | Default | Notes |
|---|---|---|---|
| `trdd-id` | UUID | — | RFC 4122 UUIDv4, full form. The 8-char prefix derives from this. Generate: `python3 -c "import uuid; print(uuid.uuid4())"` |
| `title` | string | — | Single line, ≤80 chars, no colons. The TRDD's headline. |
| `column` | enum | — | Current kanban column. See [column-transitions.md](column-transitions.md) for the transition matrix and [trdd-design-tasks.md](trdd-design-tasks.md) for the full enum (incl. the proposal-lifecycle values `proposal`/`planned`/`refused`/`cancelled` — see [approval-tiers-and-zones.md](approval-tiers-and-zones.md)). Mandatory. |
| `created` | datetime | — | When this TRDD was authored. Never changes after creation. |
| `updated` | datetime | — | Last modification time. Bump on EVERY edit. |

### 2. Ownership

| Field | Type | Default | Notes |
|---|---|---|---|
| `current-owner` | string \| null | null | Session name of the agent with write-lock on the body. **Single-writer-per-domain:** this is the ONE owner of every mutable surface the TRDD touches; a task needing a domain it does not own delegates to that owner or takes a documented claim (DERIVED NPT/EHT tasks must avoid colliding on a shared surface — see [approval-tiers-and-zones.md](approval-tiers-and-zones.md) §D). Coordination fields (`column:`, `assignee:`) can be mutated by MANAGER / ORCH regardless. |
| `assignee` | string \| null | null | Session name responsible for execution. Set by ORCH on dispatch → dev. |
| `priority` | int | 5 | 0 = highest, 9 = lowest. ORCH bumps priorities of red-column blockers. |
| `severity` | enum \| null | null | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NIT`. Optional; usually set for bugfix / security TRDDs. |
| `effort` | enum \| null | null | `S`, `M`, `L`, `XL`. Rough size estimate; set by ARCH during design. |
| `labels` | list[string] | `[]` | Free-form tags. Used by kanban filters. |

### 3. Classification

| Field | Type | Default | Notes |
|---|---|---|---|
| `task-type` | enum | — | `feature`, `bugfix`, `refactor`, `docs`, `infra`, `security`, `artifact`, `spike`, `audit`. Mandatory once the TRDD leaves `backburner`. |
| `artifact-kinds` | list[string] | `[]` | Only when `task-type=artifact`. Values like `icon`, `sound`, `html`, `animation`, `video`, `font`, `document`. |
| `approval-tier` | int | 0 | Approval authority needed before this TRDD may execute: `0` agent-independent (default; authored directly in `design/tasks/`), `1` CHIEF-OF-STAFF, `2` MANAGER, `3` USER. A tier-1/2/3 TRDD starts as a `proposal` in `design/proposals/`. Self-classified but audited against the objective tier-floor — see [approval-tiers-and-zones.md](approval-tiers-and-zones.md) §C. |

### 4. Relationships

| Field | Type | Default | Notes |
|---|---|---|---|
| `parent-trdd` | trdd-ref \| null | null | The TRDD that authored this one (from a split, or implicit handoff). Single. |
| `npt` | list[trdd-ref] | `[]` | **Necessary Prerequisite Task** children. Must complete BEFORE this TRDD can pass `dev`. |
| `eht` | list[trdd-ref] | `[]` | **Effects Handling Task** children. Must complete BEFORE this TRDD can pass `complete`. |
| `blocked-by` | list[trdd-ref] | `[]` | Runtime blockers. When non-empty AND `column != blocked`, drift signal. Subset of `npt:` while in-flight. |
| `supersedes` | list[trdd-ref] | `[]` | TRDDs replaced by this one (output of design-column split or group). |
| `superseded-by` | list[trdd-ref] | `[]` | Set only when this TRDD's `column = superseded`. |
| `pre-block-column` | enum \| null | null | The column to restore to when `blocked-by:` empties. |
| `relevant-rules` | list[rule-ref] | `[]` | PRRD rule numbers cited by this TRDD. Bare number = latest version (`64`); n.v = pinned (`64.134`). |

### 5. Delivery

| Field | Type | Default | Notes |
|---|---|---|---|
| `release-via` | enum | `none` | `publish` (tools/packages), `deploy` (services), `none` (internal-only). Determines which terminal columns are reachable. |
| `delivery` | enum | `pull-request` | `pull-request` or `direct-push`. |
| `target-branch` | string | `main` | The branch this TRDD's PR/push targets. |
| `feature-branch` | string \| null | null | Populated with branch name when assignee starts work. |
| `merge-strategy` | enum | `squash` | `squash`, `merge`, `rebase`. |
| `must-pass-tests-before-merge` | bool | true | Almost always true; toggle only for docs-only TRDDs. |
| `publish-target` | string \| null | null | When `release-via=publish`: marketplace/registry name (`npm`, `pypi`, `homebrew`, `cargo`, `github-release`, `vscode-marketplace`, …). |
| `publish-channel` | enum \| null | null | When `release-via=publish`: `stable`, `beta`, `nightly`. |
| `deploy-target` | string \| null | null | When `release-via=deploy`: `staging`, `production`, `dev-server`, or `<custom>`. |
| `soak-duration` | duration-string \| null | null | When `release-via=deploy`: time TRDD lives in `live_auditing` after `deploy → live`. Format: `"24h"`, `"7d"`. |

### 6. Verification requirements

| Field | Type | Default | Notes |
|---|---|---|---|
| `test-requirements` | list[enum] | `[]` | Subset of `unit`, `integration`, `e2e`, `dev-browser-headless`, `performance`, `lint`, `typecheck`. |
| `audit-requirements` | list[enum] | `[]` | Subset of `security-scan`, `adversarial-scan`, `dependency-audit`, `license-check`, `accessibility`. |
| `review-requirements` | list[enum] | `[]` | Subset of `human-review`, `human-evaluation`, `code-review`, `design-review`. `human-*` gates the move from `ai_review` to `human_review`. |
| `fixtures` | list[string] | `[]` | Named fixtures the test suite needs. Plugin / project defines what each name means. |
| `required-credentials` | list[string] | `[]` | Named user-supplied secrets. Example: `openai-api-key`, `github-pat`. |
| `runtime-targets` | list[enum] | `[macos]` | Platforms the test must pass on. Subset of `macos`, `linux`, `windows`, `docker`, `wasm`. |
| `docker-image` | string \| null | null | When `docker` in `runtime-targets:`. |

### 7. Impact

| Field | Type | Default | Notes |
|---|---|---|---|
| `impacts` | list[enum] | `[]` | Subset of `install-script`, `dependencies`, `config-schema`, `migration`, `public-api`, `ci-pipeline`. Documents non-primary effects of this TRDD. |
| `migration-direction` | enum \| null | null | Only when `migration` in `impacts:`. `forward`, `backward`, `both`. |

### 8. Runtime evidence (mutated as work proceeds)

| Field | Type | Default | Notes |
|---|---|---|---|
| `attempts` | int | 0 | Number of implementation attempts. Incremented on every `dev → testing → dev` bounce. |
| `test-failures` | int | 0 | Cumulative test failure count. Used by transition #10 (auto-fail threshold). |
| `last-test-result` | enum | `not-run` | `not-run`, `pass`, `fail`, `partial`. Updated by test runner. |
| `last-test-at` | datetime \| null | null | Updated by test runner. |
| `implementation-commits` | list[sha] | `[]` | **The backtracking field.** SHAs where this TRDD's code landed. A future bug discovered in commit X can locate the TRDD via `grep -l "implementation-commits:.*X" design/tasks/*.md`. |
| `pr-url` | url \| null | null | Populated once a PR is opened. |
| `ci-runs` | list[url] | `[]` | CI run URLs/IDs. Grows as the TRDD cycles through testing. |
| `published-version` | semver \| null | null | Populated on `publish → published`. The version users can install. |
| `published-at` | datetime \| null | null | Populated on `publish → published`. |
| `live-since` | datetime \| null | null | Populated on `deploy → live`. When this TRDD's code first served real traffic. |

### 9. Audit-flow (only when `task-type=audit`)

| Field | Type | Default | Notes |
|---|---|---|---|
| `audit-trigger` | enum \| null | null | `alert`, `sentry`, `log`, `scheduled`, `manual`, `user-report`. Why the investigation started. |
| `audit-target` | string \| null | null | Which deployed component is under investigation. |
| `audit-evidence` | list[url-or-path] | `[]` | Links / paths to logs, sentry events, screenshots, traces. |
| `audit-conclusion` | enum \| null | null | `benign`, `issue-confirmed`. `null` while investigating. Gates the transition out of `live_auditing` (entry mode). |

### 10. External (optional, free-form)

| Field | Type | Default | Notes |
|---|---|---|---|
| `external-refs` | list[string] | `[]` | External issue trackers, JIRA tickets, GitHub issues, Linear, etc. |

## Type forms

- **UUID** — RFC 4122 string, e.g. `9a8aba94-b5d7-4d48-b05f-bdbd72295a13`.
- **trdd-ref** — `TRDD-<uid-first-8>` (canonical) or full UUID. Tools accept either.
- **rule-ref** — bare number `64` (latest version) or `64.134` (pinned).
- **datetime** — ISO 8601 + local TZ, `2026-06-02T11:53:00+0200`.
- **duration-string** — `<int><unit>` where unit ∈ {`s`, `m`, `h`, `d`, `w`}.
- **sha** — full 40-char or short 7-char git commit hash.
- **url-or-path** — either an absolute URL or a path relative to the project root.

## Schema extension

Projects may add custom frontmatter fields. The convention is:

- **Custom field names use a project prefix** to avoid colliding with
  future canonical fields. Example: `myproject-customer-tier: enterprise`.
- **Custom fields follow the grep invariants** (one line, flow-style
  lists, etc.).
- **Tools ignore unknown fields** rather than erroring.

To propose promotion of a custom field into the canonical schema, the
team's ARCHITECT files a PRRD proposal (the schema is governed at the
PRRD layer, not per-TRDD).

## Validation

A TRDD frontmatter is VALID if:

1. All mandatory fields (identity group) are present.
2. All enum values match their declared set.
3. All list fields use flow-style (`[...]`), not block-style.
4. `column:` is consistent with conditional-mandatory fields:
   - `column in [publish, published]` requires `release-via: publish`.
   - `column in [deploy, live]` requires `release-via: deploy`.
   - `column == blocked` requires `blocked-by != []`.
   - `column == superseded` requires `superseded-by != []`.
   - `column == published` requires `published-version != null`.
   - `column == live` requires `live-since != null`.
5. `release-via = publish` requires `publish-target != null` once the
   TRDD reaches the `publish` column.
6. `release-via = deploy` requires `deploy-target != null` once the
   TRDD reaches the `deploy` column.
7. `npt`, `eht`, `blocked-by`, `supersedes`, `superseded-by` references
   resolve to existing TRDDs in the same project. (Cross-project
   references use full external refs in `external-refs:`.)
8. `relevant-rules:` references resolve to rules currently present in
   the project's PRRD. (Bare numbers AND pinned versions.)
9. `parent-trdd:` (if set) resolves to a TRDD whose `superseded-by:`
   contains this TRDD.

`findtrdd.py --validate <path>` runs these checks. The kanban renderer
runs them on every render and surfaces violations as drift signals.

## Migration from v1

v1 used `status:` with values `not-started | in-progress | completed |
failed | blocked | superseded`. The v2 equivalent:

| v1 `status:` | v2 `column:` | Notes |
|---|---|---|
| `not-started` | `backburner` | Default migration; can be promoted to `todo` / `dispatch` on edit |
| `in-progress` | `dev` | Default migration; can be set to `design` / `testing` / etc. based on context |
| `completed` | `complete` | Note: v2 distinguishes `complete` (built+tested, not shipped) from `published` / `live` |
| `failed` | `failed` | unchanged |
| `blocked` | `blocked` | unchanged |
| `superseded` | `superseded` | unchanged |

Tools (`findtrdd.py`, `kanban.py`) read both `status:` and `column:`.
When both are present, `column:` wins. When only `status:` is present,
the mapping above is applied read-only. On next edit, the agent
upgrades the TRDD to v2 frontmatter.

## Anti-patterns

- **Editing `created:`.** It's the creation timestamp; never changes.
- **Mutating `column:` without bumping `updated:`.** Breaks `--since`
  queries on the kanban view.
- **Multi-line string values.** Use the body for prose; frontmatter is
  for structured one-liners.
- **Block-style lists.** Always flow-style — `[a, b, c]`.
- **Quoting enum values.** `column: dev`, not `column: "dev"`.
- **Inventing your own enum values.** If `column: review` is what you
  mean and `review` isn't in the canonical set, you mean `ai_review` or
  `human_review`. Pick one.
- **Pasting URLs into `title:`.** Use `external-refs:` for that.
