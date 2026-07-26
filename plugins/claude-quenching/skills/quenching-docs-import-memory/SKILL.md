---
name: quenching-docs-import-memory
description: >-
  Migrates the project's Claude Code memory (the per-project ~/.claude/projects/<cwd>/memory/
  files) into the OKF docs/ bundle and clears each memory once it has landed. Use when the
  user asks to "convert the memory into docs", "move project memory into the knowledge
  base", "turn memories into standards/backlog/knowledge", "flush the memory into docs",
  or "migrate ~/.claude memory to docs/". Classifies each memory by content into
  standards/ or knowledge/ (in docs/), or a task in specs/backlog/, presents ONE migration
  plan executed on a single confirmation, and deletes a memory only after its doc lands and self-checks —
  user/unroutable memories are flagged and kept. Not for: ONE fresh fact the human states
  → quenching-docs-learn; a single doc into any home → quenching-docs-add.
when_to_use: >-
  draining the project's ~/.claude memory files into the OKF bundle, then clearing them.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task
user-invocable: false
---

# quenching-docs-import-memory — drain project memory into the OKF bundle

Promotes the durable facts the user has accumulated in **project memory** into the canonical
OKF `docs/` bundle, then clears them from memory — so knowledge that was living in
`~/.claude/projects/<cwd>/memory/` becomes conformant docs anyone browsing the repo can find.
Assumes the bundle already exists (run `quenching-docs-align` first if not). The memory-type → home routing
and the deletion contract are in [references/memory-routing.md](references/memory-routing.md);
the home boundaries, `type` vocabulary, molds, and index/log procedure are shared with
`quenching-docs-add` ([../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md)) and
`quenching-docs-align` ([../quenching-docs-align/references/taxonomy.md](../quenching-docs-align/references/taxonomy.md),
[.../conformance.md](../quenching-docs-align/references/conformance.md)). Molds live at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/`.

## Doctrine

- **Plan first, execute on one confirmation.** Cover **every** memory, classify each, and present
  ONE table — every memory → its target home + doc path + whether it will be deleted. Execute the
  whole batch on a single OK. This is invasive (it writes docs **and** deletes memory); the user
  sees the full blast radius before anything moves. **Exception — cycle-authorized runs:**
  invoked by `quenching-docs-align-and-update` under its cycle-authorization contract
  ([../quenching-align-and-update-all/references/convergence.md](../quenching-align-and-update-all/references/convergence.md)), the plan is
  presented as narration, not a gate — the write-then-verify-then-delete contract is unchanged.
- **Three destinations only.** This skill writes into exactly two `docs/` homes — `standards/`
  and `knowledge/` — plus `specs/backlog/` for a **task** (a quenching-managed folder outside
  the OKF bundle). A memory whose natural fit is a
  `vision`, `documentation`, or `reference` doc is **re-routed to the nearest of the three** per the routing
  table ([references/memory-routing.md](references/memory-routing.md)); a memory that fits none of
  them **stays** in memory and is flagged (like a `user`/unroutable fact). Never create a
  `vision/`, `documentation/`, `reference/`, or `catalog/` doc from a
  memory.
- **Bounded reconnaissance — read indexes, not the whole tree.** Because the skill writes to only
  two `docs/` homes (plus the backlog), it only ever inspects those. **Never enumerate the whole bundle** (`find docs
  -type f`, `find docs -type d`): a real repo's `catalog/` and `reference/repositories/` can hold
  thousands of files and will drown the session at startup — the exact failure this skill must
  avoid. To learn a home's existing subjects (so a concept path doesn't collide), read that home's
  top `index.md` (the honest listing) plus at most a `-maxdepth 2` directory listing — never a
  recursive file dump, never a descent into `catalog/`. Defer reading any concept doc's body to the
  moment you actually MERGE-write into that home (Step 5).
- **Metadata-first orchestrator; bodies read lazily.** Building the plan does **not** require the
  orchestrator to load every memory body. Read `MEMORY.md` (index + hooks) and each memory's
  frontmatter (`name`/`description`/`metadata.type`) up front; that routes most memories at plan
  time. Read a full body only when the hook is too thin to route — and for a large dir, defer that
  to the per-slice sub-agents (below). A 50 KB memory should never enter the main context just to be
  classified.
- **Scale by fanning out — one plan, still.** When the memory set is too large to read+classify in
  a single pass, you **MAY** split the memory dir into disjoint slices (by count, ~10–15 memories
  per agent, or by the filename type-prefix `feedback_*` / `project_*` / `reference_*`) and dispatch
  a sub-agent per slice (via `Task`) to read the full bodies for its slice and classify against
  [references/memory-routing.md](references/memory-routing.md), each returning a partial table. The
  orchestrator stays metadata-first — it only reads `MEMORY.md` + frontmatter to draw the slice
  boundaries and merge partials; the sub-agents are the only readers of full bodies. Dispatch
  **classification** sub-agents with `model: sonnet`, `effort: low` — routing a fact to its home is
  real judgment (a misroute becomes a wrong deletion decision), but each slice is small. Consolidate
  the partials into the **one** plan — a single confirmation still gates every write and delete.
  Execution MAY likewise fan out per slice, each agent honoring write-then-verify-then-delete; **no
  agent deletes a memory before its doc lands and self-checks**. **Executor** sub-agents (the
  write-verify-delete leg) inherit the session model — never downgrade them: their self-check is
  what authorizes deleting a memory. Fan-out must never fracture the single up-front plan or skip a
  memory.
- **Delete only after the doc lands.** A memory is removed **only after** its concept doc is
  written and passes the conformance self-check. Write-then-verify-then-delete, per memory —
  never delete ahead of a successful insert. A failed insert leaves that memory untouched.
- **Never silently drop a memory.** A `user` memory (who the user is) usually does **not** belong
  in shared repo docs — flag it and ask; migrate only a durable, team-relevant fact. Any memory
  with no documentary home **stays** in memory and is reported. Deletion is only ever the tail of
  a successful migration.
- **Content decides the home; `metadata.type` is a hint.** Route by what the fact IS
  ([references/memory-routing.md](references/memory-routing.md)), reusing `quenching-docs-add`'s home
  boundaries. Split a memory that carries several facts into one concept per file.
- **Salvage, don't transcribe.** A memory is terse; the doc is structured. Keep the
  `**Why:**`/`**How to apply:**` prose in the body, derive `resource` honestly (never invent),
  resolve `[[links]]` to the migrated docs' paths.
- **Full OKF stamp, honest attribution.** Every doc gets a non-empty `type`, the OKF recommended
  fields, and the method labels; `source` defaults to "project memory"; an unproven rule enters
  `authority: background`.
- **Feed the glossary.** When a migrated memory introduces a repo-specific term, add its entry to
  `knowledge/glossary.md` (the fixed A–Z lookup) as the tail of that memory's insert — the same
  step `quenching-docs-add`/`quenching-docs-learn` run — so the term is resolvable once the doc lands.

## Workflow

### 1. Locate the memory dir
The project's memory lives at `~/.claude/projects/<encoded-cwd>/memory/`, where `<encoded-cwd>`
is the absolute working directory with `/` and `.` replaced by `-`. Compute and verify it, e.g.:

```bash
enc="$(pwd | sed 's#[/.]#-#g')"; dir="$HOME/.claude/projects/$enc/memory"
ls -la "$dir" 2>/dev/null || ls -d "$HOME"/.claude/projects/*/memory 2>/dev/null
```

If the exact match is absent, list the candidates and pick the one whose de-encoded name is the
current repo (or ask). If there is no memory dir or it is empty, report that and stop.
**In a git worktree** `pwd` encodes the worktree path, but memory is keyed to the **main
checkout** — the computed path will miss; fall back to the candidate whose de-encoded name is the
repo (drop any `.worktrees/...` suffix).

### 2. Take inventory (metadata-first)
Read `MEMORY.md` (the index) and, for each memory `.md`, its **frontmatter** (`name`,
`description`, `metadata.type`) and MEMORY.md hook. Do **not** read every body here — that is what
drowns a large dir at startup. Judge the volume: if the set is small enough to read+classify in one
pass, read the bodies inline as you go; if it is large (dozens of files, or any very large ones),
switch to the fan-out posture (see the *Scale* doctrine) — slice the dir and let a sub-agent
(`model: sonnet`, `effort: low`) read the bodies for each slice. Full bodies are salvaged either
inline (small dir) or by the per-slice sub-agent (large dir) — never all at once in the
orchestrator.

### 3. Classify each → destination + `type` + mold
First **orient, bounded**: read the two target `docs/` homes' listings and the backlog index —
never enumerate the whole tree (`catalog/` and `reference/repositories/` will overflow the session):

```bash
for h in standards knowledge; do
  echo "== docs/$h =="; cat "docs/$h/index.md" 2>/dev/null
  find "docs/$h" -maxdepth 2 -name index.md 2>/dev/null
done
echo "== specs/backlog =="; cat "specs/backlog/index.md" 2>/dev/null
```

Then apply [references/memory-routing.md](references/memory-routing.md): map by content (type is a
hint) to its destination, `type`, and mold. This skill writes to **only** `standards/` and
`knowledge/` (in `docs/`) plus `specs/backlog/` (a `task`); a memory whose natural fit is `vision`,
`documentation`, or `reference` is **re-routed to the nearest of the three** per the routing table, and a
memory that fits none is flagged. Split multi-fact memories. Mark `user` memories and any
unroutable fact as **KEEP (ask)** — not for deletion.

### 4. Present the migration plan
Show ONE table: `memory → target home → doc path (type) → action (migrate+delete | keep, ask)`.
Fan-out partials **merge into ONE table** — never one table per slice. Note any `[[link]]` that
will dangle. **Wait for a single confirmation** before writing anything.

### 5. Per memory: write, verify, then delete
For each **migrate** row that lands in `docs/` (`standards/` / `knowledge/`), run the full insert
procedure exactly as
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md) specifies it —
stamp → index → log → glossary → self-check (against
[../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md)) —
with this skill's deltas kept inline:
- `source` defaults to "project memory"; salvage the terse body into a structured doc; the log
  line is `**Creation**: [<title>](/docs/<path>.md) — migrated from project memory`.
- A **task** row instead follows the `quenching-specs-capture` capture path: stamp the `task.md` mold
  into `specs/backlog/<slug>.md`, regenerate its DERIVED zone, and run the on-write self-check
  per [../quenching-specs-capture/references/backlog-zone.md](../quenching-specs-capture/references/backlog-zone.md)
  (the OKF hook does not cover the backlog); the bundle-log line is
  `**Creation**: [<title>](/specs/backlog/<slug>.md) — migrated from project memory`.
- **Only after the self-check passes:** delete the memory `.md` and prune its `- [..](..)` line
  from `MEMORY.md`. A failed write leaves that memory untouched — write-then-verify-then-delete,
  and a per-slice executor sub-agent honors the same contract (never deleting ahead of a landed,
  self-checked doc).

### 6. Report
Summarize: docs created (by home), memories deleted, and memories **kept** (with the reason —
`user`/unroutable/failed insert) so the user can decide on those. Leave `MEMORY.md` in place even
if it ends empty. If the `okf-validate.py` hook is wired, it machine-verifies each write.

## Invariants to never violate

- Never delete a memory before its doc is written **and** passes the self-check.
- Never delete a `user` memory or an unroutable fact without the user's explicit say-so.
- Never fabricate a `resource` or `source`; never clobber a filled key on merge.
- Never add frontmatter to an `index.md`; keep every touched index and log honest.
- Never skip the single up-front plan+confirmation — this writes docs and deletes memory. A
  cycle-authorized run (convergence.md §contract) replaces the gate with narration; the plan is still
  presented in full and write-then-verify-then-delete still holds.
- Never write outside the three destinations (`standards/` + `knowledge/` in `docs/`, or a task
  in `specs/backlog/`) — re-route to the nearest, or flag-and-keep; never fabricate a
  `vision`/`documentation`/`reference`/`catalog` doc from a memory.
- Fan-out never fractures the single up-front plan, never skips a memory, and never lets a
  sub-agent delete ahead of a landed, self-checked doc.
- When a migrated memory names a repo-specific term, feed `knowledge/glossary.md` before deleting
  the memory — but never clobber a filled glossary entry, and keep it a one-liner + link.
- Never enumerate the whole bundle (`find docs -type f`) or descend into `catalog/` /
  `reference/repositories/` — inspect only the two `docs/` homes' `index.md` plus the backlog
  index (bounded). Never load every memory body into the orchestrator; recon is metadata-first,
  bodies are read inline (small dir) or by per-slice sub-agents (large dir).
