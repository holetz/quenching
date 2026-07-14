# Distill — the OKF bridge from an archived change to `docs/`

How `openspec-archive-change` offers to carry the **durable** knowledge a completed change
produced into the repo's OKF `docs/` bundle. This is the plugin's adaptation layer between
the two systems: the OpenSpec side keeps its own history (the archived change folder IS the
record of what was proposed, designed, and done); the OKF side receives **only** what outlives
the change. Nothing is bulk-copied. The insert mechanics (stamp → index → log → glossary →
self-check) live with `quenching-insert`
([../../quenching-insert/references/homes.md](../../quenching-insert/references/homes.md)) —
this file only decides **what crosses** and cites that procedure for **how**.

## What crosses, what stays

| The change produced… | Cross? | OKF home / route |
| --- | --- | --- |
| a **decision with considered alternatives** (usually in `design.md`) that binds beyond this change | yes | `decisions/NNNN-<slug>.md` (`type: decision`, ADR mold) via the insert procedure |
| **generic understanding** gained (domain insight, mental model, a learning from implementation) | yes | `knowledge/<subject>/<slug>.md` (`type: knowledge`) |
| a **repo-specific term** the change coined or clarified | yes | an entry in `knowledge/glossary.md` (§Enriching the glossary in homes.md) |
| a rule for **how WE build** that the change proved out | yes | `standards/<subject>/<concept>.md` (`type: standard`) — only if genuinely proven, else it is a `decision` |
| a **follow-up idea** the change surfaced but did not pursue | yes | `backlog/<idea-slug>.md` (`type: idea`, idea mold) |
| the **behavior** the change implemented | no | already synced into `openspec/specs/` (main specs) — that store owns current behavior |
| proposal.md / design.md / tasks.md as documents | no | they are the OpenSpec archive's history; copying them into `docs/` duplicates a source of truth |
| task checklists, progress notes, transient debugging chatter | no | transient by nature |

Boundary tie-breakers (standards vs decisions vs knowledge vs reference) are the ones in
[homes.md](../../quenching-insert/references/homes.md) §Classification — apply them verbatim.

## The procedure (one confirmation)

Runs **after** the archive move succeeds, as the skill's final step:

1. **Harvest candidates.** Read the archived change's artifacts (`proposal.md`, `design.md`,
   delta specs, `tasks.md`) and the conversation's own context. List each candidate as
   *one line*: what it is → proposed home + `type` + path (per the table above). Expect
   **zero to a few** candidates — a change that taught nothing durable is normal; say so
   and skip to done.
2. **One plan, one OK.** Present the candidate list as a single distillation plan and ask
   one confirmation. The user may strike items. If the OKF bundle is missing
   (no `docs/index.md` with `okf_version`), offer `quenching-align` first, or skip
   distillation entirely — never scaffold ad hoc.
3. **Mint each approved doc** under the insert procedure
   ([homes.md](../../quenching-insert/references/homes.md)): fill the home's mold, stamp the
   frontmatter (`resource` may cite the archived change path — it exists, so the link is
   derived, not invented; `source:` names the change), update the home's `index.md`, enrich
   the glossary when a term warrants it.
4. **Log the bridge.** One `docs/log.md` entry per minted doc per §Appending to `log.md`,
   e.g. `**Creation**: [<title>](/docs/<path>.md) — distilled from openspec change <name>`.
5. **Self-check** every touched file against
   [../../quenching-align/references/conformance.md](../../quenching-align/references/conformance.md).

## Invariants

- **Never bulk-copy** an artifact into `docs/` — distill the durable unit, cite the archive.
- **Never delete or edit** the archived change while distilling — the archive is history.
- **Never mint without the one confirmation**, and never fabricate a candidate to have
  something to distill: an empty harvest is a valid outcome.
- A distilled `standard` claims `authority: current` **only** when the change actually
  implemented and proved it; otherwise stamp `authority: background` or keep it a `decision`.
