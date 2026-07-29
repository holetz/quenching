---
description: Sweep the whole bundle to backfill knowledge/glossary.md with missing terms
argument-hint: [optional-home-scope]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Write, Edit, Task
---

# /docs:glossary-backfill — backfill the glossary from the whole bundle

**Input**: `$ARGUMENTS` (an optional home/slice to scope the sweep; omit to scan the whole bundle).

Sweeps the canonical OKF bundle's **entire** `docs/` tree — every doc already sitting there,
written before the glossary existed, migrated in by `/docs:align`, or hand-authored — for
repo-specific terms that were never fed into
[`knowledge/glossary.md`](${CLAUDE_PLUGIN_ROOT}/assets/docs/knowledge/glossary.md), and backfills them in one
consolidated pass. This is a **retroactive, whole-bundle** sweep, not a capture: it never
writes a `knowledge/` concept doc and never asks the human what a term means — those stay
`/docs:learn`'s job. The glossary format and the shared **Enriching the glossary**
procedure live with `/docs:add`
([docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)); the
`type` vocabulary and conformance rules with `/docs:align`
([docs-align/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/taxonomy.md),
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md)). The fan-out convention
(bounded recon, sliced `Task` agents, compact partials, one merged plan) follows
`/docs:import-memory`, the only other skill in this plugin that uses `Task`.

## Doctrine

- **Sweep, don't recapture.** A retroactive, bulk pass over what the bundle *already says* —
  never asks the human "what does this mean," never authors a `knowledge/` doc itself (that
  stays exclusively `/docs:learn`'s job).
- **Bounded reconnaissance, sliced fan-out.** List doc paths cheaply first (`Glob`/`find`, no
  bodies). Slice by top-level home by default (further splitting a large home to ~15–20
  docs/agent). One `Task` sub-agent per slice reads only its slice's docs and returns compact
  `{term, one-sentence definition, candidate doc path}` candidates — never full bodies back
  to the orchestrator. Apply the same caution `/docs:import-memory` applies to
  `catalog/**` and `reference/repositories/**`: list-only by default (skip body scanning),
  reported as excluded, opt-in only.
- **One glossary, one writer.** Sub-agents only propose; the orchestrator is the sole editor
  of `glossary.md` (one file — parallel writers would race).
- **Derive, never invent.** A candidate's definition must trace to the source doc's own
  words; a slice agent drops a candidate it can't honestly derive rather than guessing.
- **An unlinked entry is a valid, permanent state** — not a gap to chase, no escalation.
- **Plan first, one confirmation.** Merge every slice into ONE consolidated list before any
  write (mirrors `/docs:align`/`/docs:import-memory`'s posture). **Exception —
  cycle-authorized runs:** invoked as a stage of `/docs:align`'s cycle (or of `/align`) under the cycle-authorization contract
  ([align/convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)), the
  consolidated plan is presented as narration, not a gate — this skill has no code-coupled
  items, so cycle-authorized means zero pauses.
- **MERGE, never clobber; keep it sorted; skip what's already listed** — identical contract
  to `/docs:define` Step 4, in the bullet syntax from
  [`knowledge/glossary.md`](${CLAUDE_PLUGIN_ROOT}/assets/docs/knowledge/glossary.md).

## Workflow

### 1. Locate the glossary and read the baseline
Find `docs/knowledge/glossary.md` (the bundle root may be a variant — resolve it as the other
skills do). If the `knowledge/` home or the glossary seed is missing, stop and offer
`/docs:align` to install the skeleton, then resume. Read the current entries once — this
is the dedupe baseline every slice's candidates get checked against.

### 2. List the bundle, bounded
List every doc path under `docs/` (`Glob`/`find`, paths only — never read bodies here),
excluding `index.md`, `log.md`, and harness files (`CLAUDE.md`/`AGENTS.md`). `catalog/**` and
`reference/repositories/**` are listed but **not** body-scanned by default — note them as
excluded from the sweep.

### 3. Slice and fan out
Group the remaining paths by top-level home (`standards/`, `vision/`,
`documentation/`, `knowledge/`, `reference/` minus the excluded slice);
split further if a home runs large (~15–20 docs per
agent). Dispatch one `Task` sub-agent per slice — with `model: haiku` and `effort: low`:
a slice agent does pure extraction and returns compact tuples, and over-collection is
harmless because the orchestrator cross-checks every candidate against the Step 1
baseline before anything reaches the plan. It reads only its slice's doc bodies and
returns a compact candidate list — `{term, one-sentence definition, source doc path}` —
dropping anything it can't honestly derive from the text. No sub-agent reads outside its
slice or writes `glossary.md`.

### 4. Merge, dedupe, cross-check
Consolidate every slice's candidates: drop a candidate whose term is already listed in the
Step 1 baseline **unless** it now offers a link the existing entry lacks (a **refine**);
dedupe candidates for the same term found in more than one slice, preferring the most
specific source doc.

### 5. Present ONE consolidated plan
Show a single table: `Term | definition | link (or none) | source doc | action
(add/refine-link/skip)`, plus which homes were excluded from body-scanning
(`catalog/**`/`reference/repositories/**`) and why. **Wait for one confirmation** before
writing anything — never present a plan per slice.

### 6. Write on confirmation
The orchestrator alone edits `knowledge/glossary.md`: insert each **add** in alphabetical
position as `* [<Term>](<path>.md) — <definition>` (linked) or `* **<Term>** —
<definition>` (unlinked); for each **refine**, add the missing link to an existing unlinked
entry — never overwrite a filled definition or link. The glossary is the only file this
command writes; the count of terms added and refined belongs in the report, not in the bundle.

### 7. Self-check against the conformance core
Verify every file you touched against
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md),
plus this skill's own gate: the list is still sorted and its links resolve.

## Invariants to never violate

- Never invent a definition or a link target — a candidate must trace to its source doc's
  own words, and a link must point at a doc that actually exists.
- Never let a sub-agent write `glossary.md` directly — sub-agents only propose; the
  orchestrator is the sole writer.
- Never skip the single consolidated confirmation or present per-slice lists — every slice
  merges into ONE plan before any write. A cycle-authorized run (convergence.md §contract) replaces
  the gate with narration but still merges everything into ONE presented plan.
- Never clobber a filled entry (definition or link) on merge, and never leave the list
  unsorted.
- Never blindly descend into `catalog/**` or `reference/repositories/**` — list-only by
  default, reported as excluded, opt-in only.
- Never author a `knowledge/` concept doc or ask the human what a term means — that is
  `/docs:learn`'s job, not this skill's.
