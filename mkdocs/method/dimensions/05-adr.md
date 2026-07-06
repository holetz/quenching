# Dimension 5 · ADR

A decision record captures a choice **not yet implemented** — under debate, with its
alternatives weighed. Its canonical home is `docs/decisions/`.

> **Canonical home — `docs/decisions/` · Fixed (canonical).** `docs/adr/` is a variant to
> migrate (and the two coexisting is a single-home violation), with your OK. See
> [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

The whole point of an Architectural Decision Record is to preserve the **why and the
alternatives** — the context that the code itself can never show
([ADR](https://adr.github.io/)). Without it, a future agent (or human) re-litigates
settled questions because the reasoning evaporated. The canonical home isn't an arbitrary
choice either: MADR, the most widely used ADR template, says *verbatim* to "create folder
`docs/decisions`" ([MADR](https://adr.github.io/madr/)) — so the method converges there
rather than inventing a name.

The lifecycle rule is what keeps decisions from rotting: once a decision is **implemented,
it is distilled into a [standard](02-standards.md) and removed** from the
decisions tree (a small "distilled" ledger preserves the trail). An ADR is *explanation*
in Diátaxis terms — "why we decided" — and a decision that has become "how it is today"
belongs in the reference layer, not stalled as an open ADR.

## What "good" looks like

- One `NNNN-slug/` folder per decision under `decisions/`.
- Implemented decisions are **distilled to `standards/` and removed**, with a ledger entry.
- Frontmatter references the direction/spec it serves; the ADR carries the *why*, not the
  implementation "how".

## How it drifts

- **Implemented ADR that didn't leave the tree.**
- **A current decision stalled as an open ADR** (it is now a standard).
- **Implementation detail inside the ADR** — "how" where only "why" belongs.
- **`docs/adr/`** instead of `docs/decisions/`, or both coexisting.

## How the method closes the gap

It distills implemented decisions to `standards/`, updates the ledger, and proposes the
`docs/adr/` → `docs/decisions/` migration. The payload is the `quenching-docs` skill plus
the `docs/decisions/` scaffold and an ADR template — see
[Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Architectural Decision Records (ADRs) — adr.github.io](https://adr.github.io/) — accessed 2026-06-28
- [MADR — Markdown Any Decision Records — adr.github.io](https://adr.github.io/madr/) — accessed 2026-06-29
- [Diátaxis — A systematic framework for technical documentation](https://diataxis.fr/) — accessed 2026-06-28
