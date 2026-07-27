# Distill — the OKF bridge from a concluded spec to `docs/`

How `/specs:conclude` offers to carry the **durable** knowledge a spec produced into the repo's
OKF `docs/` bundle. This is **the single bridge** between the two systems: the archive side keeps
its own history (the archived spec IS the record of what was proposed, designed and done); the OKF
side receives **only** what outlives the spec and was not already written into `docs/` while it was
built. Nothing is bulk-copied. The insert mechanics (stamp → index → log → glossary → self-check)
live with `/docs:add`
([docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)) — this file only
decides **what crosses** and cites that procedure for **how**.

## What crosses, what stays

| The spec produced… | Cross? | OKF home / route |
| --- | --- | --- |
| a rule a task **explicitly named** under `## Impact` | **no** | `/specs:execute` **already wrote it into `docs/standards/`** as part of that task — nothing to do here. There is no separate spec store to sync |
| a **decision** (rationale + considered alternatives, usually in `## Design`) not yet captured as a standard | yes | `standards/<subject>/<concept>.md` (`type: standard`; `authority: current` if the spec proved it, else `background`) — there is no separate ADR home |
| **generic understanding** gained (domain insight, mental model, a learning from implementation) | yes | `knowledge/<subject>/<slug>.md` (`type: knowledge`) |
| a **repo-specific term** the spec coined or clarified | yes | an entry in `knowledge/glossary.md` (§Enriching the glossary in homes.md) |
| a **follow-up** the spec surfaced but did not pursue | yes | a fresh spec in `specs/plans/` via `/specs:create` — outside the `docs/` bundle, and never stamped with an OKF `type:` |
| `## Proposal` / `## Design` / `## Tasks` as documents | no | they are the archive's history; copying them into `docs/` duplicates a source of truth |
| task checklists, progress notes, transient debugging chatter | no | transient by nature |

The top row is the load-bearing difference from the old delta model: because a task writes the
binding rule **straight into `docs/standards/`** while it is built, concluding is not a *sync* — it
is catching the **by-products** (a decision left in `## Design`, an understanding, a term, a
follow-up) that were never committed to a home. Most of what a spec proves is already in `docs/` by
the time it closes; the harvest is usually small.

This table decides **what a concluded spec hands over**. It is not a restatement of the `specs/` ↔
`docs/` boundary, which is owned once by
[`specs-develop/spec-driven.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§Boundary — that section says which tree answers which question; this one says which of a spec's
by-products survive it. When the two seem to disagree, the boundary wins and this table is wrong.

Boundary tie-breakers **within** `docs/` (standards vs knowledge vs reference) are the ones in
[homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md) §Classification — apply them verbatim.

## Two moments, one table

The table above decides **what** crosses. `/specs:conclude` applies it **twice**, at two moments
that differ only in when the doc has to exist:

| Moment | What it catches | Where it lands |
| --- | --- | --- |
| **emergent** — before the merge | a rule the work *revealed*: a `## Discoveries` line worth a doc, something the branch review surfaced | on the **work branch**, in its own commit, so the rule ships with the code that proved it |
| **distillation** — after the archive move | the by-products that outlive the spec: a decision still in `## Design`, an understanding, a term, a follow-up | on the **base branch**, after the merge |

A rule the code demonstrates belongs beside that code in history; a by-product of the *thinking*
has no code to ship with and is cheapest to harvest once the spec is closed. Both take one plan and
one confirmation, and neither ever fabricates a candidate to have something to write.

## The procedure (one confirmation)

Runs **after** the archive move succeeds, as the command's distillation step:

1. **Harvest candidates.** Read the archived spec's sections (`## Problem`, `## Proposal`,
   `## Design`, `## Discoveries`, `## Outcome`) and the conversation's own context, and check what
   `docs/` already received — during execution, and at the emergent moment above. List each
   **remaining** candidate as *one line*: what it is → proposed home + `type` + path (per the table
   above). Expect **zero to a few** — a spec that captured its rules as it went, and taught nothing
   else durable, is normal; say so and skip to done.
2. **One plan, one OK.** Present the candidate list as a single distillation plan and ask one
   confirmation. The user may strike items. If the OKF bundle is missing (no `docs/index.md` with
   `okf_version`), offer `/docs:align` first, or skip distillation entirely — never scaffold ad hoc.
3. **Mint each approved doc** under the insert procedure
   ([homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)): fill the home's mold, stamp the
   frontmatter (`resource` may cite the archived spec path — it exists, so the link is derived, not
   invented; `source:` names the spec), update the home's `index.md`, enrich the glossary when a
   term warrants it. A follow-up instead goes through `/specs:create` into `specs/plans/` (outside
   the `docs/` bundle).
4. **Log the bridge.** One `docs/log.md` entry per minted doc per §Appending to `log.md`,
   e.g. `**Creation**: [<title>](/docs/<path>.md) — distilled from spec <slug>`.
5. **Self-check** every touched file against
   [docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md).

## Invariants

- **Never bulk-copy** an artifact into `docs/` — distill the durable unit, cite the archive.
- **Never delete or edit** the archived spec while distilling — the archive is history.
- **Never mint without the one confirmation**, and never fabricate a candidate to have something
  to distill: an empty harvest is a valid outcome.
- A distilled `standard` claims `authority: current` **only** when the spec actually implemented
  and proved it; otherwise stamp `authority: background`.
