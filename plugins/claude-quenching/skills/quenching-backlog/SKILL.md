---
name: quenching-backlog
description: >-
  Captures ONE task into the repo's OKF backlog/ — the task inbox — in seconds: a minimal
  type: task stamp, with optional priority/tags/complexity only when the human states them
  inline. Use when the user asks to "add to the backlog", "park a task", "capture a task",
  "note this for later", or "backlog this". Extracts title + gist from the phrasing ("park X,
  high priority, theme auth, ~8h" → priority: high, tags: [auth], complexity: 8; tags
  normalized against ones already in the backlog), dedupes by slug/title (MERGE, never clobber), writes
  backlog/<task-slug>.md from the task mold, regenerates the derived GENERATED zone in
  backlog/index.md, logs the creation, and self-checks. Zero interrogation: what was not
  said is left out — no priority means untriaged, a valid state. Not for: prioritizing
  the whole backlog → quenching-backlog-triage; any other kind of doc → quenching-insert.
when_to_use: >-
  parking ONE task in the backlog/ inbox, fast and minimal. The prioritization sweep is
  quenching-backlog-triage; routing any other kind of doc is quenching-insert.
allowed-tools: Read, Grep, Glob, Write, Edit
effort: low
---

# quenching-backlog — park one task in the inbox

Files ONE task into the canonical OKF bundle's task inbox,
[`backlog/`](../../assets/docs/backlog/index.md) — the fast, low-ceremony landing spot for
a unit of work, raw (it seeds the OpenSpec cycle, `openspec-explore` / `openspec-propose`,
before it becomes work) or already clear in scope, parked between "I thought of this" and
"I'm working on this". The mold is
`${CLAUDE_PLUGIN_ROOT}/assets/templates/backlog/task.md`; the routing row, the derived-zone
format, and the shared index/log/glossary procedure live with `quenching-insert`
([../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)); the
`type` vocabulary and conformance rules with `quenching-align`
([../quenching-align/references/taxonomy.md](../quenching-align/references/taxonomy.md),
[.../conformance.md](../quenching-align/references/conformance.md)). For prioritizing the
whole inbox instead of capturing one task, see `quenching-backlog-triage`.

## Doctrine

- **Capture in seconds — the stamp stays minimal.** `type: task`, title, one-sentence
  gist, timestamp. `priority` (`critical|high|medium|low`), `tags` (themes), and
  `complexity` (a rough size in development hours) are stamped ONLY when the human states
  them inline. No `done-criteria`, no `vision_refs`, no detailed planning — that thinking
  belongs to the OpenSpec cycle or execution, never to capture; `complexity` is the one
  rough estimate that may be stamped here. `resource` is deliberately omitted (nothing built yet to point at); the
  resulting `missing-resource` WARN is expected, not a defect.
- **Zero interrogation.** Never ask for a priority, a theme, or scope. What was not said
  is left out; a task without `priority` is **untriaged** — a valid state
  `quenching-backlog-triage` exists to fill, not a gap to chase at capture time.
- **Tags are normalized, never minted casually.** Reuse a theme already present in the
  backlog's tasks (`auth`, not a fresh `authentication`); a genuinely new theme is fine.
- **Flat home, English kebab slug.** One task per file, `backlog/<task-slug>.md`, no
  subfolders. Frontmatter is canonical English; the 1–3-sentence body may follow the
  repo's language.
- **MERGE, never clobber.** A slug/title collision merges into the existing task (fill
  missing keys, sharpen the gist) or aborts if it is the same task — never overwrite.
- **The zone is derived, never hand-edited.** `backlog/index.md`'s task listing is
  rebuilt exclusively from the tasks' frontmatter, only between the GENERATED markers,
  per the `backlog/index.md` bullet in
  [../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)
  §**Updating `index.md`**. The Completed ledger stays outside the zone, untouched.

## Workflow

### 1. Resolve the bundle
Find `docs/backlog/` (the bundle root may be a variant — resolve it as the other skills
do). If the home or its `index.md` is **missing**, stop and offer `quenching-align` to
install the skeleton, then resume.

### 2. Extract from the user's phrasing
Take the title and one-sentence gist from what the human said. Parse `priority`/`tags`
ONLY when stated inline ("park X, high priority, theme auth" → `priority: high`,
`tags: [auth]`). Normalize tags against the ones already present in `backlog/*.md`
frontmatter. **Zero interrogation** — what was not said is left out.

### 3. Dedupe
`Grep`/`Glob` `backlog/` for a similar slug or title. On a collision, MERGE into the
existing task (never clobber a filled key) — or abort and say so if it is the same task.

### 4. Stamp and write
Fill the `task.md` mold and write `backlog/<task-slug>.md` (English kebab slug). Drop the
optional keys (`priority`/`tags`/`complexity`) that were not stated; `priority` only ever
takes `critical|high|medium|low`, and `complexity` is development hours (a number or a range
like `4-8`).

### 5. Regenerate the derived zone
Rebuild `backlog/index.md`'s GENERATED zone from the tasks' frontmatter, per the
`backlog/index.md` bullet in **Updating `index.md`**
([../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)). If
a target's `backlog/index.md` predates the markers, install them without touching the
fixed prose around them.

### 6. Log and enrich the glossary
Append `**Creation**: [<title>](/docs/backlog/<task-slug>.md) — <one line>` per
**Appending to `log.md`**, then run the shared glossary tail step per **Enriching the
glossary** (both in
[../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)) —
normally a no-op for a task.

### 7. Self-check against the conformance core
Verify every file you touched against
[../quenching-align/references/conformance.md](../quenching-align/references/conformance.md),
plus this skill's own gate: the GENERATED zone matches the tasks on disk and every zone
link resolves.

## Invariants to never violate

- Never interrogate the human at capture — no priority, theme, or scope questions; absent
  keys stay absent (untriaged is a valid state).
- Never invent a `priority` or a tag the human did not state, and never use a priority
  value outside `critical|high|medium|low`.
- Never clobber an existing task on collision — MERGE or abort.
- Never hand-edit inside the GENERATED markers, never touch the Completed ledger at
  capture, and never add frontmatter to `backlog/index.md`.
- Never expand the stamp beyond the mold — no `done-criteria`, `vision_refs`, assignees, or a
  status field (`complexity` in dev hours is the one allowed estimate); status is positional
  (in the tree = open).
