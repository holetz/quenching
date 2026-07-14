# Backlog → task inbox with priorities, themes, and two dedicated skills

Supersedes in part
[2026-07-08-backlog-idea-inbox-design.md](2026-07-08-backlog-idea-inbox-design.md): the
item concept is renamed `idea` → `task` (same purpose, same minimal-mold doctrine, same
lifecycle shape), the stamp gains two **optional** keys (`priority`, `tags`), the home's
`index.md` gains a derived listing zone, and — reversing that spec's "no new skill"
stance — two dedicated skills are added (capture + triage), taking the plugin from ten
skills to twelve.

## Problem

`backlog/` today is the raw idea inbox: deliberately minimal (`type: idea`; only
title / one-sentence gist / timestamp), flat, feeding `superpowers:brainstorming`. Three
gaps in practice:

1. **Input is not frictionless enough.** Capture rides `quenching-insert`'s generic
   classify-everything routing; there is no dedicated trigger ("park this task") and no
   inline parsing of priority/theme when the human states them.
2. **The index shows no picture of the whole.** `backlog/index.md` is doctrine prose plus
   a ledger — it lists no items, no themes, no priority levels. Answering "what's parked,
   on which themes, what first?" requires opening every file.
3. **Nothing helps prioritization.** There is no priority metadata and no skill that
   reviews the set and proposes a ranking.

Constraints set by the user: do **not** expand per-item detail (capture stays a
seconds-fast, minimal stamp); everything stays OKF v0.1-conformant inside the existing
bundle contract; canonical English terms.

## Decision

### The task and its stamp

`backlog/` becomes the **task inbox**: `type: task` replaces `type: idea` in the fixed
vocabulary. A *task* is a unit of work captured in seconds — raw (needs
`superpowers:brainstorming` before it becomes work) or already clear in scope — parked
between "I thought of this" and "I'm working on this". Same purpose as today's ideas;
the name matches how the inbox is actually used. The home stays **flat** (no subfolders),
slugs kebab-case English.

Mold `assets/templates/backlog/idea.md` → `assets/templates/backlog/task.md`:

```yaml
---
type: task                             # required
title: <one-line name>
description: <one sentence — the gist>
timestamp: <ISO 8601>
tags: [<theme>, ...]                   # OPTIONAL — the task's theme(s)
priority: <critical|high|medium|low>   # OPTIONAL — absent = untriaged
---
```

- `priority` is a fixed four-value English enum: `critical | high | medium | low`. A task
  without the key is **untriaged** — a valid state, not a defect; triage exists to fill it.
- `tags` (already an OKF-recommended key) carries the **themes**, a free list normalized
  against tags already present in the backlog (reuse `auth`, don't mint `authentication`).
- No `done-criteria`, no `vision_refs`, no estimates — that thinking still belongs to
  brainstorming/execution, per the 2026-07-08 spec. `resource` stays deliberately omitted
  (nothing built yet to point at); the resulting `missing-resource` WARN remains expected
  and documented in the mold comment.
- Body: 1–3 sentences; may follow the repo's language. Frontmatter stays canonical English.

### Lifecycle

1. **Capture** — a task lands in `backlog/<task-slug>.md` in seconds (`quenching-backlog`,
   or generic `quenching-insert` routing).
2. **Triage (optional)** — `quenching-backlog-triage` proposes priority/tags; a task may
   also be born triaged (stated inline at capture).
3. **Develop / execute** — brainstorming for raw tasks; direct execution for clear ones.
4. **Leave the tree** — once developed into an approved spec or done, the file is
   **removed** and recorded in the **Completed ledger** in `backlog/index.md` (renamed
   from "Developed ledger"; existing rows preserved). Columns: `Task | Outcome | Date`,
   where Outcome is a link to the resulting spec/PR/standard or a one-line "done — …".
   Removal happens on completion/approval, never on triage; an abandoned development
   leaves the task in place.

### The enriched index (derived zone)

`backlog/index.md` = fixed prose (doctrine, boundaries, lifecycle, "what does NOT go
here") + one **generated zone** + the Completed ledger (curated history, **outside** the
zone). The zone sits between `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->`
markers and is rebuilt **exclusively from the tasks' frontmatter** — never hand-edited —
exactly the `standards/index.md` precedent. Content, in order:

1. **Summary line** — `**N tasks** · X critical · Y high · Z medium · W low · K untriaged`.
2. **By priority** — one table per level, order Critical → High → Medium → Low →
   Untriaged, empty groups omitted. Columns `Task | Description | Tags | Since`
   (`Since` = the task's `timestamp`), rows sorted **oldest-first** within each group so
   stale tasks surface naturally.
3. **By theme** — alphabetical bullets `**<tag>** (n): [task-a](task-a.md), …`; a task
   with two tags appears under both.

Table links keep the validator's `index-orphan` check clean; the index stays
frontmatter-free (conformance intact). The zone's format is documented **once** in
`homes.md` §"Updating `index.md`" — a new bullet mirroring the existing
`standards/index.md` bullet ("rebuild only between the markers; never hand-edit inside") —
and the two new skills, `quenching-insert`, and `quenching-align` cite it. No new
`references/` file is created; both new skills are self-contained like
`quenching-glossary`.

Every capture logs `**Creation**` in `docs/log.md`; a triage logs one consolidated
`**Update**`.

### Skill: `quenching-backlog` — capture ONE task

Per-item pattern (peer of `quenching-glossary`): additive, one file, **no confirmation
gate** — mirrors `quenching-insert`. Trigger phrases: "add to the backlog", "park a
task", "capture a task", "note this for later". Workflow:

1. **Resolve the bundle** — `docs/backlog/` missing → stop and offer `quenching-align`
   (same protocol as the other skills).
2. **Extract from the user's phrasing** — title, gist, and priority/tags *when stated
   inline* ("park X, high priority, theme auth" → `priority: high`, `tags: [auth]`).
   **Zero interrogation**: what wasn't said is left out; no priority = untriaged. Tags
   normalized against existing ones.
3. **Dedupe** — `Grep` for similar title/slug; collision → MERGE into the existing task
   (never clobber) or abort if it is the same task.
4. **Stamp and write** — `task.md` mold, English kebab slug.
5. **Regenerate the derived zone** (per the `homes.md` bullet).
6. **Log** `**Creation**` + the shared glossary tail step (cites `homes.md`; normally a
   no-op for tasks).
7. **Self-check** against `conformance.md`.

Frontmatter: `allowed-tools: Read, Grep, Glob, Write, Edit` · `effort: low`.

### Skill: `quenching-backlog-triage` — the prioritization sweep

Sweep pattern (peer of `quenching-knowledge-scan`): **ONE plan → ONE OK**, and — like
every sweep skill — **never `context: fork`** (the mid-flow confirmation must be
presentable). Trigger phrases: "prioritize the backlog", "triage the backlog", "groom
the backlog", "re-rank the tasks". Workflow:

1. **Read all task frontmatter directly** (no sub-agents — the backlog is small by
   nature) + `vision/` context when present, to ground the proposals.
2. **Build ONE triage plan** as a table: per untriaged task, proposed priority + tags
   with a one-line rationale; re-ranks of already-triaged tasks **only with an explicit
   reason**; staleness flags (old `Since`); duplicate-merge suggestions. Completion /
   removal enters the plan **only when the human states the task is done** — never
   inferred.
3. **One OK** approves the whole plan (partial adjustments → re-plan).
4. **Apply** — frontmatter edits exactly as listed (MERGE; no silent clobber of a
   human-set priority). Approved merges/removals move content and add a Completed-ledger
   row for completions.
5. **Regenerate the zone**, log one consolidated `**Update**`, self-check.

Frontmatter: `allowed-tools: Read, Grep, Glob, Write, Edit`; no `effort` override
(priority judgment inherits the default; the human plan-gate contains misjudgment).
Both skills get rows in the README cost-model table (capture: cheap/safe; triage:
default effort, human-gated, no sub-agents).

### Boundaries

- **`quenching-insert`**: drops the "capture a raw idea" trigger; gains
  "Not for: parking a task in the backlog → quenching-backlog". The backlog row **stays**
  in `homes.md`'s routing table — generic routing and `quenching-memory-to-docs` still
  reach the home (using the `task.md` mold + zone regeneration).
- **`quenching-memory-to-docs`**: emits backlog tasks **always untriaged** — inventing a
  priority the human never stated would violate anti-fabrication.
- **`quenching-cycle`**: unchanged. Triage is an on-demand tool like `enrich`/`visualize`,
  not a loop stage.

### Migration (`quenching-align`)

- `migration.md` gains the legacy mappings: `backlog/*.md` with `type: idea` →
  `type: task`; index heading "Developed ledger" → "Completed ledger" (rows preserved);
  derived zone installed/regenerated (align already regenerates every `index.md`).
- The align **verify gate** (conformance.md §Verify gate) additionally checks the backlog
  GENERATED zone matches disk — mirroring the existing standards-zone check.
- In a target whose backlog `index.md` predates the markers, the new skills install the
  markers without touching the fixed prose around them.

### Error handling (consolidated)

- Missing bundle → offer `quenching-align`, then resume.
- Slug collision → MERGE or abort; never clobber.
- Rejected triage plan → nothing applied.
- Invalid priority value found in a target (e.g. `priority: urgent`) → the task renders
  under Untriaged and the next triage proposes the fix. The **validator is not extended**
  (unknown keys/values stay tolerated; no functional change to `okf-validate.py`).

## Files to update (mechanical propagation)

| File | Change |
| --- | --- |
| `skills/quenching-backlog/SKILL.md` | **NEW** — capture skill as specified |
| `skills/quenching-backlog-triage/SKILL.md` | **NEW** — triage skill as specified |
| `assets/templates/backlog/idea.md` → `task.md` | Rewrite mold: `type: task`, optional `tags`/`priority`, updated comment |
| `assets/docs/backlog/index.md` | Rewrite seed: task doctrine + empty GENERATED zone + empty Completed ledger |
| `assets/docs/index.md` | `backlog/` home one-liner → task inbox |
| `assets/docs/vision/index.md` | Boundary line: raw idea → raw task |
| `assets/templates/concept-front.md` | Type-enum comment: `idea` → `task` |
| `assets/templates/vision/area.md` | Boundary note: idea → task wording |
| `assets/templates/harness/claude-root.md` | Backlog pointer line wording |
| `assets/templates/README.md` | Mold row: `backlog/task.md` / `<task-slug>.md` / `task` |
| `assets/README.md` | Templates listing line (`backlog/task`) |
| `skills/quenching-align/references/taxonomy.md` | Tree comment, type-vocab table row, backlog home bullet (task doctrine + zone + priority/tags) |
| `skills/quenching-align/references/okf-spec.md` | Type vocabulary list |
| `skills/quenching-align/references/migration.md` | Legacy mappings: `idea`→`task`, ledger rename, zone install |
| `skills/quenching-align/references/conformance.md` | §Verify gate: backlog GENERATED zone matches disk |
| `skills/quenching-insert/references/homes.md` | Routing row (`task`, `backlog/task.md`); tie-breaker bullet rewrite; **new zone bullet** in §Updating `index.md` |
| `skills/quenching-insert/SKILL.md` | Trigger/Not-for changes; step 5 mentions the backlog zone alongside standards |
| `skills/quenching-harness/references/harness-routing.md` | Verdict row + boundary line: idea → task |
| `skills/quenching-memory-to-docs/references/memory-routing.md` | Routing rows: `task`, always untriaged |
| `skills/quenching-visualize/references/viz.md` | Type list: `idea` → `task` |
| `assets/tools/okf-visualize.py` | Palette gains `"task"` (same red), **keeps** `"idea"` for un-migrated bundles; `VERSION` const bump |
| `assets/hooks/okf-validate.py` | `VERSION` const bump only (lockstep; zero functional change) |
| `README.md` (plugin) | Skills table 10 → 12; cost-model rows; tree comment; `idea` prose mentions |
| `CLAUDE.md` (repo root) | "The ten skills" table → twelve; backlog contract wording |
| `.claude-plugin/plugin.json` | `version` bump; keywords gain `backlog` |
| `VERSION` | `0.10.0` → `0.11.0` (minor — new features) |
| `.claude-plugin/marketplace.json` (repo root) | Mirror the version bump |

## Verification

No test suite; the repo's manual verify contract:

1. `cd plugins/claude-quenching && python3 assets/hooks/okf-validate.py assets/docs` →
   `0 error(s), 0 warning(s)` (the shipped skeleton stays conformant by construction).
2. `python3 assets/tools/okf-visualize.py assets/docs --out /tmp/okf-diagram.html` exits 0;
   `--version` of **both** scripts reports `0.11.0` == `VERSION` == `plugin.json` ==
   marketplace entry.
3. `grep -rn "type: idea\|backlog/idea\|idea-slug\|raw idea" plugins/claude-quenching`
   returns only the legacy mappings in `migration.md` (the one deliberate survivor those
   patterns can match); `grep -n '"idea"' plugins/claude-quenching/assets/tools/okf-visualize.py`
   still shows the kept legacy palette entry next to the new `"task"` one.
4. New/edited skill `description`s ≤ 1,536 chars with trigger phrases in the second
   sentence; skill bodies well under 500 lines; neither new skill declares
   `context: fork`.

## Out of scope

- No changes to the `superpowers` plugin (external).
- No functional change to `okf-validate.py` — no priority/type-value/zone checks in the
  validator.
- No `quenching-cycle` stage addition — triage stays on-demand.
- No per-task detail expansion: done-criteria, estimates, assignees, due dates, and a
  status field all stay out. Status is positional: in the tree = open; removed = completed
  (ledger keeps the trail).
- No automatic promotion of a developed task into `decisions/`/`vision/` — stays a manual,
  optional `quenching-insert` step (unchanged from the 2026-07-08 spec).
