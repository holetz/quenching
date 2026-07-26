---
name: quenching-docs-glossary-backfill
description: >-
  Sweeps the ENTIRE OKF docs/ bundle to backfill knowledge/glossary.md with repo-specific
  terms that are already documented but were never listed. Use when the user asks to
  "scan the docs for glossary terms", "backfill the glossary", "sweep the bundle for
  missing terms", "find terms we never added to the glossary", or "catch up the glossary
  on what's already documented". Lists doc paths cheaply, fans one Task sub-agent out per
  home slice to return compact term candidates, merges everything into ONE consolidated
  plan for a single confirmation, then writes glossary.md as its sole editor; catalog/**
  and reference/repositories/** are listed but not body-scanned by default. Not for:
  capturing ONE fresh concept → quenching-docs-learn; a single on-demand term →
  quenching-docs-define.
when_to_use: >-
  retroactively sweeping the WHOLE docs/ bundle for glossary terms never fed into
  knowledge/glossary.md. The bulk counterpart of the per-capture glossary tail step.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task
user-invocable: false
effort: medium
---

# quenching-docs-glossary-backfill — backfill the glossary from the whole bundle

Sweeps the canonical OKF bundle's **entire** `docs/` tree — every doc already sitting there,
written before the glossary existed, migrated in by `quenching-docs-align`, or hand-authored — for
repo-specific terms that were never fed into
[`knowledge/glossary.md`](../../assets/docs/knowledge/glossary.md), and backfills them in one
consolidated pass. This is a **retroactive, whole-bundle** sweep, not a capture: it never
writes a `knowledge/` concept doc and never asks the human what a term means — those stay
`quenching-docs-learn`'s job. The glossary format and the shared **Enriching the glossary**
procedure live with `quenching-docs-add`
([../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md)); the
`type` vocabulary and conformance rules with `quenching-docs-align`
([../quenching-docs-align/references/taxonomy.md](../quenching-docs-align/references/taxonomy.md),
[.../conformance.md](../quenching-docs-align/references/conformance.md)). The fan-out convention
(bounded recon, sliced `Task` agents, compact partials, one merged plan) follows
`quenching-docs-import-memory`, the only other skill in this plugin that uses `Task`.

## Doctrine

- **Sweep, don't recapture.** A retroactive, bulk pass over what the bundle *already says* —
  never asks the human "what does this mean," never authors a `knowledge/` doc itself (that
  stays exclusively `quenching-docs-learn`'s job).
- **Bounded reconnaissance, sliced fan-out.** List doc paths cheaply first (`Glob`/`find`, no
  bodies). Slice by top-level home by default (further splitting a large home to ~15–20
  docs/agent). One `Task` sub-agent per slice reads only its slice's docs and returns compact
  `{term, one-sentence definition, candidate doc path}` candidates — never full bodies back
  to the orchestrator. Apply the same caution `quenching-docs-import-memory` applies to
  `catalog/**` and `reference/repositories/**`: list-only by default (skip body scanning),
  reported as excluded, opt-in only.
- **One glossary, one writer.** Sub-agents only propose; the orchestrator is the sole editor
  of `glossary.md` (one file — parallel writers would race).
- **Derive, never invent.** A candidate's definition must trace to the source doc's own
  words; a slice agent drops a candidate it can't honestly derive rather than guessing.
- **An unlinked entry is a valid, permanent state** — not a gap to chase, no escalation.
- **Plan first, one confirmation.** Merge every slice into ONE consolidated list before any
  write (mirrors `quenching-docs-align`/`quenching-docs-import-memory`'s posture). **Exception —
  cycle-authorized runs:** invoked by `quenching-docs-align-and-update` under its cycle-authorization contract
  ([../quenching-align-and-update-all/references/convergence.md](../quenching-align-and-update-all/references/convergence.md)), the
  consolidated plan is presented as narration, not a gate — this skill has no code-coupled
  items, so cycle-authorized means zero pauses.
- **MERGE, never clobber; keep it sorted; skip what's already listed** — identical contract
  to `quenching-docs-define` Step 4, in the bullet syntax from
  [`knowledge/glossary.md`](../../assets/docs/knowledge/glossary.md).

## Workflow

### 1. Locate the glossary and read the baseline
Find `docs/knowledge/glossary.md` (the bundle root may be a variant — resolve it as the other
skills do). If the `knowledge/` home or the glossary seed is missing, stop and offer
`quenching-docs-align` to install the skeleton, then resume. Read the current entries once — this
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
entry — never overwrite a filled definition or link. Then append **one** summarizing entry
to `docs/log.md` (not one per term), per **Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md):
`**Update**: [Glossary](/docs/knowledge/glossary.md) — backfilled N terms from a bundle-wide
scan (M linked)`.

### 7. Self-check against the conformance core
Verify every file you touched against
[../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md),
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
  `quenching-docs-learn`'s job, not this skill's.
