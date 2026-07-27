---
description: Refactor CLAUDE.md/AGENTS.md into thin pointers over the docs/ bundle
argument-hint: [optional-harness-file]
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task
---

# /docs:harness — make CLAUDE.md a thin, honest pointer into the bundle

**Input**: `$ARGUMENTS` (an optional specific harness file; omit to sweep every CLAUDE.md/AGENTS.md).

Refactors a repo's **harness files** (the root `CLAUDE.md`, every subfolder `CLAUDE.md`, and
`AGENTS.md`) into thin navigation pointers over the OKF `docs/` bundle. A harness file is **context
tax** the agent pays on every turn, so it earns each line: operational rules stay; durable knowledge
is **moved** into its `docs/` home and cited, never re-inlined. This matters because the validator
**skips** harness files by design (okf-spec §strict-7) — knowledge inlined there escapes validation,
is invisible to anyone browsing `docs/`, and drifts. Assumes the bundle already exists (run
`/docs:align` first if not). It also **creates** a thin subfolder `CLAUDE.md` where discovery
finds a folder with a local operational surface but no harness — evidence-gated, never one per
directory (routing §6). The unit → verdict → home routing and the pointer-honesty gate are
in [docs-harness/harness-routing.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-harness/harness-routing.md); the home boundaries, `type`
vocabulary, molds, and index/log procedure are shared with `/docs:add`
([docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)) and
`/docs:align` ([docs-align/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/taxonomy.md),
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md),
[docs-align/migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/migration.md)). Harness
molds live at `${CLAUDE_PLUGIN_ROOT}/assets/templates/harness/`.

## Doctrine

- **Commands and etiquette stay; knowledge moves.** The one test: would the agent need this on
  **EVERY** task under this file's folder (keep) — or only when working on **that subject** (move +
  pointer)? A harness file is context tax paid on every turn; it earns each line.
- **A folder earns a harness; a harness is never assumed.** Beyond slimming the files that exist,
  the skill **creates** a thin subfolder `CLAUDE.md` where a folder has local operational commands
  but none — but only where the folder earns it (routing §6). Never blanket-create one per
  directory; data, output, and asset folders earn nothing.
- **Move, never copy.** After the run each fact lives in exactly **ONE** place — its concept doc.
  A rule restated in CLAUDE.md is the same drift as a lying index; the pointer **cites** the doc,
  it never paraphrases it.
- **Plan first, execute on one confirmation.** Read every harness file, classify every unit, and
  present **ONE** table — file → unit → verdict → destination. A single OK executes the batch; an
  edit whose blast radius reaches **product code** is its own confirmation item. **Exception —
  cycle-authorized runs:** invoked by `/docs:align-and-update` under its cycle-authorization contract
  ([align-and-update-all/convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align-and-update-all/convergence.md)), the plan is
  presented as narration, not a gate; a product-code edit still confirms on its own, always. The
  cycle may hand this skill a **pre-collected steps 1–4 table** (gathered read-only while
  `/docs:import-memory` ran — cycle.md §Parallel prep); before writing, re-verify any unit
  whose home/subject intersects the docs that run just created — a fresh doc can flip a MOVE
  into a DEDUPE (the staleness delta-recheck); the rest of the table stands.
- **Write-then-verify-then-cut.** A unit leaves the harness file **only after** its concept doc is
  written, indexed, logged, and passes the conformance self-check. A failed insert leaves the unit
  in place (the same contract as `/docs:import-memory`' write-then-verify-then-delete).
- **Never silently drop a unit.** Unroutable content **stays** and is reported; a contradiction
  with `docs/` is a **FLAG** resolved per item; secrets and personal notes are flagged and **NEVER**
  filed into shared `docs/` (`CLAUDE.local.md` is treated like a `user` memory).
- **This skill is the validator for harness files.** `okf-validate.py` skips `CLAUDE.md`/`AGENTS.md`
  by design — pointer honesty (every link resolves, every pointer describes what its target really
  holds) is verified **HERE**, in step 8.

## Workflow

### 1. Inventory the harness surface (read-only)
`Glob` `**/CLAUDE.md`, `**/AGENTS.md`, and `CLAUDE.local.md`; add a `grep --no-ignore` sweep to
catch gitignored ones. Confirm `docs/index.md` carries `okf_version` — if there is no OKF bundle,
**stop** and offer `/docs:align` first. List every harness file found.

Then **discover greenfield candidates** (read-only), swept **repo-wide from the repository
root** — one pass over the entire tree, e.g. `find . -type f \( -name '*.sh' -o -name Makefile
-o -name package.json -o -name justfile \)` anchored at the root, never a search pre-scoped to a
hand-picked list of top-level directories (a known failure mode: reusing the set of folders you
already read for step 2 — because they already hold a `CLAUDE.md` — silently drops any candidate
outside that set, e.g. a `templates/` or `tools/` folder no existing harness file points to yet;
the folders most likely to need a *new* pointer are exactly the ones nothing already references).
Folders that have a **local operational surface** but **no** `CLAUDE.md` qualify only if they
carry commands the agent would need on **every** task under them that **don't derive from the
root** — a `*.sh` / `Makefile` / `justfile` / `package.json`-script, a distinct toolchain, or a
`README` whose fenced blocks are run-commands. **Exclude** generated-output, asset, and vendored
dirs (`.build/`, `dist/`, `build/`, `target/`, `node_modules/`, `**/__pycache__/`, `fonts/`,
`assets/`, `.venv/`, any nested `site-packages`/vendored dependency tree) and anything gitignored
as a build artifact — check each hit with `git check-ignore`, don't assume from the path alone.
Each survivor is a **proposed** subfolder `CLAUDE.md`, carried into the plan (step 5) as its own
gated item — never auto-created. See [docs-harness/harness-routing.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-harness/harness-routing.md) §6.

On a large repo, delegate this repo-wide `find`/`grep` sweep to **one read-only `Task`
sub-agent** (`model: haiku`, `effort: low`) that only **collects** — harness paths, candidate
folders and the operational evidence found in each (`folder → [Makefile, run.sh, …]`) — while
every qualify/exclude judgment stays with the orchestrator; the sweep is mechanical, the routing
is not.

### 2. Parse each file into content units
Segment into units — heading section / fenced command block / bullet run / paragraph — capturing
each unit's text, its anchor, and its links. **One verdict per unit**; split a mixed unit (a
build command paired with an architecture note becomes two).

### 3. Classify every unit
Apply the [docs-harness/harness-routing.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-harness/harness-routing.md) table →
**KEEP / MOVE / DEDUPE / FLAG / UNROUTABLE**. A **MOVE** derives its home + `type` + mold via
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md); a **DEDUPE**
cites the existing doc (`Grep docs/` to confirm coverage); a **FLAG** quotes both sides of the
contradiction.

### 4. Sweep the blast radius
Per `/docs:align`'s migration doctrine
([docs-align/migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/migration.md) §3–4):
`git grep` + `grep -rn --no-ignore` for anything that reads or links the harness files or their
anchors. As in step 1, a large sweep goes to one read-only `Task` collector (`model: haiku`,
`effort: low`) returning `anchor → [file:line, …]`; the orchestrator judges each hit. Any hit in
**product code** (a path constant, an import, a docstring) becomes a **separately gated**
confirmation item.

### 5. Present ONE refactor plan → gate on one OK
Show the table (`file → unit → verdict → destination`) plus, per rewritten file, its **target
shape** (which mold, which KEEP residue). Include evidence-gated subfolder-`CLAUDE.md` creations —
both units scoped to a folder and greenfield-discovered folders (step 1 / routing §6), each its own
item — FLAG items, and code-coupled items awaiting their **own** OK. **Wait for a single
confirmation** before writing anything.

### 6. Per MOVE unit: insert, verify, then cut
For each MOVE row, run the full insert procedure exactly as
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md) specifies it —
stamp → index → log → glossary → self-check (against
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md)) —
with this skill's deltas kept inline:
- `source:` = the harness file the unit came from; an unproven rule enters
  `authority: background`; the log line is
  `**Creation**: [<title>](/docs/<path>.md) — moved from CLAUDE.md`.
- **Only after the self-check passes:** cut the unit from the harness file. A failed insert
  leaves the unit in place; a **DEDUPE** unit is cut once the existing doc is confirmed to
  cover it.

### 7. Rewrite each harness file from its mold
Root from `${CLAUDE_PLUGIN_ROOT}/assets/templates/harness/claude-root.md`, a subfolder from
`.../harness/claude-subfolder.md`. Structure and links are canonical English; prose may follow the
repo's language. UNROUTABLE and FLAG-pending units stay under a clearly marked residue section.
**No frontmatter, ever.**

### 8. Verify and report
**Resolve EVERY link** in every rewritten harness file (the validator won't). Confirm no moved fact
is still restated inline; run `okf-validate.py` over `docs/` → 0 errors and the structural WARNs
clean; confirm each moved doc is indexed and logged. Report counts: **moved** (by home) /
**deduped** / **kept** / **flagged** / **unroutable** / **harness created** (subfolder pointers).

## Invariants to never violate

- Never **copy** — a moved unit is **removed** from the harness file (one fact, one place).
- Never cut a unit before its doc is written **and** passes the conformance self-check.
- Never silently drop a unit; never file secrets or personal notes into shared `docs/`.
- Never leave a lying pointer — **every** link in a rewritten harness file resolves before the run ends.
- Never give a harness file frontmatter or a `type` (okf-spec §strict-7 — they are exempt).
- Never skip the single up-front plan + confirmation; a product-code edit confirms on its own. A
  cycle-authorized run (convergence.md §contract) replaces the batch gate with narration — never the
  product-code item's own OK — and a pre-collected table is delta-rechecked before any write.
- Never blanket-create subfolder `CLAUDE.md`s — creation is evidence-gated per routing §6, and a
  data/output/asset folder earns none.
