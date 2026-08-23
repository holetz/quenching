---
name: quenching-knowledge-import-memory
description: "Drain the project's Codex memory into the OKF bundle, then clear it. Triggers on \"convert the memory into docs\", \"move project memory into the knowledge base\", \"flush the memory into docs\". Not for: importing an external source of files/URLs → quenching-knowledge-import."
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/import-memory.md -->


# quenching-knowledge-import-memory — drain project memory into the OKF bundle

**Input**: `$ARGUMENTS` (an optional subset or scope; omit to drain all project memory).

Promotes the durable facts the user has accumulated in **project memory** into the canonical
OKF `/.knowledge/` bundle, then clears them from memory — so knowledge that was living in
`~/.codex/projects/<cwd>/memory/` becomes conformant docs anyone browsing the repo can find.
Assumes the bundle already exists (run `quenching-knowledge-align` first if not). The memory-type → home routing
and the deletion contract are in [knowledge-import-memory/memory-routing.md](../../references/knowledge-import-memory/memory-routing.md);
the home boundaries, `type` vocabulary, molds, and index/log procedure are shared with
`quenching-knowledge-add` ([knowledge-add/homes.md](../../references/knowledge-add/homes.md)) and
`quenching-knowledge-align` ([knowledge-align/taxonomy.md](../../references/knowledge-align/taxonomy.md),
[knowledge-align/conformance.md](../../references/knowledge-align/conformance.md)). Molds live at
`../../templates/`.

## Doctrine

- **Plan first, execute on one confirmation.** Cover **every** memory, classify each, and present
  ONE table — every memory → its target home + doc path + whether it will be deleted. Execute the
  whole batch on a single OK. This is invasive (it writes docs **and** deletes memory); the user
  sees the full blast radius before anything moves. **Exception — cycle-authorized runs:**
  invoked as a stage of `quenching-knowledge-align`'s cycle (or of `/align`) under the cycle-authorization contract
  ([align/convergence.md](../../references/align/convergence.md)), the plan is
  presented as narration, not a gate — the write-then-verify-then-delete contract is unchanged.
- **Three destinations only.** This skill writes into exactly two `/.knowledge/` homes — `standards/`
  and `concepts/` — plus `/.specs/plans/` for a **unit of work** (a quenching-managed folder
  outside the OKF bundle). A memory whose natural fit is a
  `vision`, `documentation`, or `external` doc is **re-routed to the nearest of the three** per the routing
  table ([knowledge-import-memory/memory-routing.md](../../references/knowledge-import-memory/memory-routing.md)); a memory that fits none of
  them **stays** in memory and is flagged (like a `user`/unroutable fact). Never create a
  `vision/`, `documentation/`, `external/`, or `catalog/` doc from a
  memory.
- **Bounded reconnaissance — read indexes, not the whole tree.** Because the skill writes to only
  two `/.knowledge/` homes (plus the backlog), it only ever inspects those. **Never enumerate the whole bundle** (`find .knowledge
  -type f`, `find .knowledge -type d`): a real repo's `catalog/` and `external/repositories/` can hold
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
  [knowledge-import-memory/memory-routing.md](../../references/knowledge-import-memory/memory-routing.md), each returning a partial table. The
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
  ([knowledge-import-memory/memory-routing.md](../../references/knowledge-import-memory/memory-routing.md)), reusing `quenching-knowledge-add`'s home
  boundaries. Split a memory that carries several facts into one concept per file.
- **Salvage, don't transcribe.** A memory is terse; the doc is structured. Keep the
  `**Why:**`/`**How to apply:**` prose in the body, derive `resource` honestly (never invent),
  resolve `[[links]]` to the migrated docs' paths.
- **Full OKF stamp, honest attribution.** Every doc gets a non-empty `type`, the OKF recommended
  fields, and the method labels; `source` defaults to "project memory"; an unproven rule enters
  `authority: background`.
- **Feed the glossary.** When a migrated memory introduces a repo-specific term, add its entry to
  `glossary.md` (the fixed A–Z lookup) as the tail of that memory's insert — the same
  step `quenching-knowledge-add`/`quenching-knowledge-learn` run — so the term is resolvable once the doc lands.
- **One resolver, both platforms.** The memory directory is derived from the **native** working
  directory, so it is resolved in Python — the runtime this plugin already requires — and never
  from shell string-munging. `pwd` under Windows Git Bash reports the MSYS form (`/c/Users/…`),
  which encodes to a directory name that does **not** exist, while the real one is keyed to
  `c:\Users\…`; a POSIX-only recipe therefore misses on every Windows target and silently reports
  "no memory". Resolution is by data — an exact match, then the nearest ancestor, then the
  candidate list — never by a guess, and it is **case-insensitive** because the drive letter's
  case is not stable.

**Why `Bash` is scoped here.** `python3`/`py` runs the Step 1 resolver and the two checkers
(`cq specs`, `cq knowledge validate`); `rm` deletes a memory file once its doc has landed and
self-checked. Nothing else in this command needs a shell — the reconnaissance is `Read`/`Glob`
and the edits are `Write`/`Edit`.

Resolve `cq` per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

## Workflow

### 1. Locate the memory dir
The project's memory lives at `~/.codex/projects/<encoded-cwd>/memory/`, where `<encoded-cwd>` is
the **native** absolute working directory with every `\`, `/`, `:` and `.` replaced by `-`
(`c:\repos\app` → `c--repos-app`; `/home/me/repos/app` → `-home-me-repos-app`). Run the resolver
below **as-is** — it is the same on Linux, macOS and Windows, and it also covers the worktree and
ambiguity cases that used to need a second pass:

```bash
python3 - <<'PY'
import sys
from pathlib import Path
# Codex replaces \ / : . with '-'. chr(92) IS the backslash, spelled this way so no
# quoting layer can eat the escape; Path.cwd() reports the native path on every platform.
PUNCT = set(chr(92) + "/:.")
enc = lambda p: "".join("-" if c in PUNCT else c for c in str(p))
cwd = Path.cwd().resolve()
# .lower(): a Windows drive letter's case is not stable (c:\ vs C:\), the rest is exact.
have = {d.name.lower(): d for d in (Path.home() / ".claude" / "projects").glob("*")
        if (d / "memory").is_dir()}
hit = None
for p in (cwd, *cwd.parents):   # nearest first: a worktree or subdir falls back to its checkout
    if enc(p).lower() in have:
        hit = (have[enc(p).lower()], "exact" if p == cwd else "ancestor " + str(p))
        break
if hit is None:
    print("NO MATCH for", enc(cwd))
    for k in sorted(have):
        print("  candidate:", have[k])
    sys.exit(1)
mem = hit[0] / "memory"
files = sorted(f.name for f in mem.glob("*.md"))
print("dir:", mem, "| matched:", hit[1], "| memories:", len(files))
for f in files:
    print("  ", f)
PY
```

Use `py - <<'PY'` where `python3` is not on PATH (common on Windows). Branch on what it printed,
never on a guess:
- **`matched: exact`** — proceed.
- **`matched: ancestor <path>`** — the cwd is a git **worktree** or a subdirectory; memory is keyed
  to the main checkout, which is what the walk found. Confirm the path names this repo before any
  deletion, since a parent directory could carry unrelated memory.
- **`NO MATCH`** — pick the candidate whose de-encoded name is this repo, or ask. Never invent one.
- **`memories: 0`** or no directory at all — report that and stop.

**Do not** derive the path with `pwd`: under Windows Git Bash it reports the MSYS form
(`/c/Users/…`), which encodes to a name that does not exist, and the run misreports an empty
memory on a target that has one.

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
First **orient, bounded** — three `Read`s and two `Glob`s, no shell, so it behaves identically on
every platform. Never enumerate the whole tree (`catalog/` and `external/repositories/` will
overflow the session):

- `Read` — `/.knowledge/standards/index.md` and `/.knowledge/concepts/index.md` (the honest listings; a missing
  file just means that home is empty). For what `/.specs/plans/` already holds, `cq specs list --json`
  derives it from disk — there is no listing file to read.
- `Glob` — `/.knowledge/standards/*/index.md` and `/.knowledge/concepts/*/index.md` for the existing subject
  folders, so a new concept path does not collide. One level only, and never a recursive file dump.

Then apply [knowledge-import-memory/memory-routing.md](../../references/knowledge-import-memory/memory-routing.md): map by content (type is a
hint) to its destination, `type`, and mold. This skill writes to **only** `standards/` and
`concepts/` (in `/.knowledge/`) plus `/.specs/plans/` (a spec); a memory whose natural fit is `vision`,
`documentation`, or `external` is **re-routed to the nearest of the three** per the routing table, and a
memory that fits none is flagged. Split multi-fact memories. Mark `user` memories and any
unroutable fact as **KEEP (ask)** — not for deletion.

### 4. Present the migration plan
Show ONE table: `memory → target home → doc path (type) → action (migrate+delete | keep, ask)`.
Fan-out partials **merge into ONE table** — never one table per slice. Note any `[[link]]` that
will dangle. **Wait for a single confirmation** before writing anything.

### 5. Per memory: write, verify, then delete
For each **migrate** row that lands in `/.knowledge/` (`standards/` / `concepts/`), run the full insert
procedure exactly as
[knowledge-add/homes.md](../../references/knowledge-add/homes.md) specifies it —
stamp → index → log → glossary → self-check (against
[knowledge-align/conformance.md](../../references/knowledge-align/conformance.md)) —
with this skill's deltas kept inline:
- `source` defaults to "project memory"; salvage the terse body into a structured doc; the log
  line is `**Creation**: [<title>](/.knowledge/<path>.md) — migrated from project memory`.
- A **unit of work** row instead follows the `quenching-specs-create` path: run `cq specs new
  <name>` and write the memory's content into `## Problem` and nothing else, then `cq specs
  validate --spec <id>` — the ID the create reported — as the self-check per
  [specs-develop/spec-driven.md](../../references/specs-develop/spec-driven.md)
  (`cq knowledge validate` never covers the specs front); the bundle-log line is
  `**Creation**: [<title>](<the locator the create reported>) — migrated from project memory`.
  **Never stamp an OKF `type:` on it** — a spec is not a concept doc, and never invent a
  `priority`: an unranked spec is `quenching-specs-triage`'s to place.
- **Only after the self-check passes:** delete the memory `.md` (`rm` — the one destructive shell
  this command runs, and the only reason `Bash(rm:*)` is granted) and prune its `- [..](..)` line
  from `MEMORY.md` with `Edit`. Pass the path the Step 1 resolver printed, quoted, so a Windows
  path with spaces survives. A failed write leaves that memory untouched — write-then-verify-then-delete,
  and a per-slice executor sub-agent honors the same contract (never deleting ahead of a landed,
  self-checked doc).

### 6. Report
Summarize: docs created (by home), memories deleted, and memories **kept** (with the reason —
`user`/unroutable/failed insert) so the user can decide on those. Leave `MEMORY.md` in place even
if it ends empty.

## Invariants to never violate

- Never delete a memory before its doc is written **and** passes the self-check.
- Never delete a `user` memory or an unroutable fact without the user's explicit say-so.
- Never fabricate a `resource` or `source`; never clobber a filled key on merge.
- Never add frontmatter to an `index.md`; keep every touched index and log honest.
- Never skip the single up-front plan+confirmation — this writes docs and deletes memory. A
  cycle-authorized run (convergence.md §contract) replaces the gate with narration; the plan is still
  presented in full and write-then-verify-then-delete still holds.
- Never write outside the three destinations (`standards/` + `concepts/` in `/.knowledge/`, or a spec
  in `/.specs/plans/`) — re-route to the nearest, or flag-and-keep; never fabricate a
  `vision`/`documentation`/`external`/`catalog` doc from a memory.
- Fan-out never fractures the single up-front plan, never skips a memory, and never lets a
  sub-agent delete ahead of a landed, self-checked doc.
- When a migrated memory names a repo-specific term, feed `glossary.md` before deleting
  the memory — but never clobber a filled glossary entry, and keep it a one-liner + link.
- Never enumerate the whole bundle (`find .knowledge -type f`) or descend into `catalog/` /
  `external/repositories/` — inspect only the two `/.knowledge/` homes' `index.md` plus the backlog
  index (bounded). Never load every memory body into the orchestrator; recon is metadata-first,
  bodies are read inline (small dir) or by per-slice sub-agents (large dir).
