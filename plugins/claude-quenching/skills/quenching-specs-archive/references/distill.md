# Distill — the OKF bridge from an archived plan to `docs/`

How `quenching-specs-archive` offers to carry the **durable** knowledge a completed plan
produced into the repo's OKF `docs/` bundle. This is **the single bridge** between the two
systems: the archive side keeps its own history (the archived plan folder IS the record of what
was proposed, designed, and done); the OKF side receives **only** what outlives the plan and was
not already written into `docs/` while the plan was built. Nothing is bulk-copied. The insert
mechanics (stamp → index → log → glossary → self-check) live with `quenching-docs-add`
([../../quenching-docs-add/references/homes.md](../../quenching-docs-add/references/homes.md)) —
this file only decides **what crosses** and cites that procedure for **how**.

## What crosses, what stays

| The plan produced… | Cross? | OKF home / route |
| --- | --- | --- |
| the **behavior/rule the plan implemented** | **no** | the plan **already wrote it into `docs/standards/`** as it was built (`quenching-specs-apply`) — nothing to do here. There is no separate spec store to sync |
| a **decision** (rationale + considered alternatives, usually in `## Design`) not yet captured as a standard | yes | `standards/<subject>/<concept>.md` (`type: standard`; `authority: current` if the plan proved it, else `background`) — there is no separate ADR home |
| **generic understanding** gained (domain insight, mental model, a learning from implementation) | yes | `knowledge/<subject>/<slug>.md` (`type: knowledge`) |
| a **repo-specific term** the plan coined or clarified | yes | an entry in `knowledge/glossary.md` (§Enriching the glossary in homes.md) |
| a **follow-up task** the plan surfaced but did not pursue | yes | `specs/backlog/<task-slug>.md` (`type: task`, task mold — untriaged unless the human states a priority; via `quenching-specs-capture`, outside the `docs/` bundle) |
| ## Proposal / ## Design / ## Tasks as documents | no | they are the archive's history; copying them into `docs/` duplicates a source of truth |
| task checklists, progress notes, transient debugging chatter | no | transient by nature |

The top row is the load-bearing difference from the old delta model: because a plan writes the
binding rule **straight into `docs/standards/`** during apply, the archive's job is not to *sync a
behavior* — it is to catch the **by-products** (a decision left in `## Design`, an understanding, a
term, a follow-up) that were not committed to a home yet. Most of what a plan proves is already in
`docs/` by the time it is archived; the harvest is usually small.

This table decides **what a completed plan hands over**. It is not a restatement of the `specs/` ↔
`docs/` boundary, which is owned once by
[`../../quenching-specs-develop/references/spec-driven.md`](../../quenching-specs-develop/references/spec-driven.md)
§Boundary — that section says which tree answers which question; this one says which of a plan's
by-products survive it. When the two seem to disagree, the boundary wins and this table is wrong.

Boundary tie-breakers **within** `docs/` (standards vs knowledge vs reference) are the ones in
[homes.md](../../quenching-docs-add/references/homes.md) §Classification — apply them verbatim.

## The procedure (one confirmation)

Runs **after** the archive move succeeds, as the skill's final step:

1. **Harvest candidates.** Read the archived plan's artifacts (`## Problem`/`## Proposal`, `## Design`,
   `## Tasks`) and the conversation's own context, and check what `docs/standards/` already
   received during apply. List each **remaining** candidate as *one line*: what it is → proposed
   home + `type` + path (per the table above). Expect **zero to a few** — a plan that captured its
   rules as it went, and taught nothing else durable, is normal; say so and skip to done.
2. **One plan, one OK.** Present the candidate list as a single distillation plan and ask one
   confirmation. The user may strike items. If the OKF bundle is missing (no `docs/index.md` with
   `okf_version`), offer `quenching-docs-align` first, or skip distillation entirely — never
   scaffold ad hoc.
3. **Mint each approved doc** under the insert procedure
   ([homes.md](../../quenching-docs-add/references/homes.md)): fill the home's mold, stamp the
   frontmatter (`resource` may cite the archived plan path — it exists, so the link is derived, not
   invented; `source:` names the plan), update the home's `index.md`, enrich the glossary when a
   term warrants it. A follow-up **task** instead uses the `quenching-specs-capture` capture
   path into `specs/backlog/` (outside the `docs/` bundle).
4. **Log the bridge.** One `docs/log.md` entry per minted doc per §Appending to `log.md`,
   e.g. `**Creation**: [<title>](/docs/<path>.md) — distilled from plan <name>`.
5. **Self-check** every touched file against
   [../../quenching-docs-align/references/conformance.md](../../quenching-docs-align/references/conformance.md).

## Invariants

- **Never bulk-copy** an artifact into `docs/` — distill the durable unit, cite the archive.
- **Never delete or edit** the archived plan while distilling — the archive is history.
- **Never mint without the one confirmation**, and never fabricate a candidate to have something
  to distill: an empty harvest is a valid outcome.
- A distilled `standard` claims `authority: current` **only** when the plan actually implemented
  and proved it; otherwise stamp `authority: background`.
