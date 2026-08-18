---
name: quenching-knowledge-glossary-backfill
description: "Sweep the whole bundle to backfill glossary.md with missing terms. Triggers on \"scan the docs for glossary terms\", \"backfill the glossary\", \"find terms we never added to the glossary\". Not for: ONE term on demand → quenching-knowledge-define."
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/glossary-backfill.md -->


# quenching-knowledge-glossary-backfill — backfill the glossary from the whole bundle

**Input**: `$ARGUMENTS` (an optional home/slice to scope the sweep; omit to scan the whole bundle).

Sweeps the canonical OKF bundle's **entire** `/.knowledge/` tree — every doc already sitting there,
written before the glossary existed, migrated in by `quenching-knowledge-align`, or hand-authored — for
repo-specific terms that were never fed into
[`glossary.md`](../../knowledge/glossary.md), and backfills them in one
consolidated pass. This is a **retroactive, whole-bundle** sweep, not a capture: it never
writes a `concepts/` concept doc and never asks the human what a term means — those stay
`quenching-knowledge-learn`'s job. The glossary format and the shared **Enriching the glossary**
procedure live with `quenching-knowledge-add`
([knowledge-add/homes.md](../../references/knowledge-add/homes.md)); the
`type` vocabulary and conformance rules with `quenching-knowledge-align`
([knowledge-align/taxonomy.md](../../references/knowledge-align/taxonomy.md),
[knowledge-align/conformance.md](../../references/knowledge-align/conformance.md)). The fan-out convention
(bounded recon, sliced `Task` agents, compact partials, one merged plan) follows
`quenching-knowledge-import-memory`, the only other skill in this plugin that uses `Task`.

## Doctrine

- **Sweep, don't recapture.** A retroactive, bulk pass over what the bundle *already says* —
  never asks the human "what does this mean," never authors a `concepts/` doc itself (that
  stays exclusively `quenching-knowledge-learn`'s job).
- **Bounded reconnaissance, sliced fan-out.** List doc paths cheaply first (`Glob`/`find`, no
  bodies). Slice by top-level home by default (further splitting a large home to ~15–20
  docs/agent). One `Task` sub-agent per slice reads only its slice's docs and returns compact
  `{term, one-sentence definition, candidate doc path}` candidates — never full bodies back
  to the orchestrator. Apply the same caution `quenching-knowledge-import-memory` applies to
  `catalog/**` and `external/repositories/**`: list-only by default (skip body scanning),
  reported as excluded, opt-in only.
- **One glossary, one writer.** Sub-agents only propose; the orchestrator is the sole editor
  of `glossary.md` (one file — parallel writers would race).
- **Derive, never invent.** A candidate's definition must trace to the source doc's own
  words; a slice agent drops a candidate it can't honestly derive rather than guessing.
- **An unlinked entry is a valid, permanent state** — not a gap to chase, no escalation.
- **Plan first, one confirmation.** Merge every slice into ONE consolidated list before any
  write (mirrors `quenching-knowledge-align`/`quenching-knowledge-import-memory`'s posture). **Exception —
  cycle-authorized runs:** invoked as a stage of `quenching-knowledge-align`'s cycle (or of `/align`) under the cycle-authorization contract
  ([align/convergence.md](../../references/align/convergence.md)), the
  consolidated plan is presented as narration, not a gate — this skill has no code-coupled
  items, so cycle-authorized means zero pauses.
- **MERGE, never clobber; keep it sorted; skip what's already listed** — identical contract
  to `quenching-knowledge-define` Step 4, in the bullet syntax from
  [`glossary.md`](../../knowledge/glossary.md).

## Workflow

### 1. Locate the glossary and read the baseline
Find `/.knowledge/glossary.md` — the bundle root is the fixed `/.knowledge/` convention. If the
`concepts/` home or the glossary seed is missing, stop and offer
`quenching-knowledge-align` to install the skeleton, then resume. Read the current entries once — this
is the dedupe baseline every slice's candidates get checked against.

### 2. List the bundle, bounded
List every doc path under `/.knowledge/` (`Glob`/`find`, paths only — never read bodies here),
excluding `index.md`, `log.md`, and harness files (`AGENTS.md`/`AGENTS.md`). `catalog/**` and
`external/repositories/**` are listed but **not** body-scanned by default — note them as
excluded from the sweep.

### 3. Slice and fan out
Group the remaining paths by top-level home (`standards/`, `vision/`,
`documentation/`, `concepts/`, `external/` minus the excluded slice);
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
(`catalog/**`/`external/repositories/**`) and why. **Wait for one confirmation** before
writing anything — never present a plan per slice.

### 6. Write on confirmation
The orchestrator alone edits `glossary.md`: insert each **add** in alphabetical
position as `* [<Term>](<path>.md) — <definition>` (linked) or `* **<Term>** —
<definition>` (unlinked); for each **refine**, add the missing link to an existing unlinked
entry — never overwrite a filled definition or link. The glossary is the only file this
command writes; the count of terms added and refined belongs in the report, not in the bundle.

### 7. Self-check against the conformance core
Verify every file you touched against
[knowledge-align/conformance.md](../../references/knowledge-align/conformance.md),
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
- Never blindly descend into `catalog/**` or `external/repositories/**` — list-only by
  default, reported as excluded, opt-in only.
- Never author a `concepts/` concept doc or ask the human what a term means — that is
  `quenching-knowledge-learn`'s job, not this skill's.
