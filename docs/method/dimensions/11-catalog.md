# Dimension 11 · Catalog

The catalog is the **domain made legible to the agent** — table and model metadata
(generated) plus editorial curation (versioned), and the doctrine for how skills consume it.
Its canonical home is `docs/catalog/`. It applies only to repos with an explicit data or
domain layer.

> **Canonical home — `docs/catalog/` · Fixed (canonical).** `docs/catalogo_dados/` or
> `docs/dominio/` are variants to migrate, with your OK. Installed only where the repo
> actually has a domain. See [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

An agent reasoning over a data domain needs **curated context about that domain**, not just
the raw schema — which entities matter, what they mean, how they're consumed. This is
exactly the gap the industry is standardizing around: Google's **Open Knowledge Format**
frames curated, vendor-neutral, markdown domain context as a first-class artifact for AI
agents ([How the Open Knowledge Format can improve data sharing](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing),
[OKF — MarkTechPost](https://www.marktechpost.com/2026/06/16/google-cloud-introduces-open-knowledge-format-okf-a-vendor-neutral-markdown-spec-for-giving-ai-agents-curated-context/)).

The method's specific rule is the **generated × curated split**, the same *"X defines Y"*
invariant that governs hooks: the auto-generated metadata is regenerated from the source and
**never hand-edited**, while human curation lives in a separately versioned area. Mixing the
two means curation gets silently overwritten on the next regeneration — and a catalog the
agent can't trust is worse than none.

## What "good" looks like

- AUTO-GENERATED metadata and human curation are **separated**; the generated part is never
  hand-edited.
- Curation is versioned on its own.
- A single doctrine governs how skills consume the domain.

## How it drifts

- **Curation written inside the generated block** — it will be overwritten.
- **Catalog outdated** versus the manifest/source.
- **Domain with no consumption mapping** — present but not wired to how skills use it.

## How the method closes the gap

It moves curation out of generated blocks and points to the correct generator for the
metadata. Catalog generators are repo-specific, so the method does **not** carry them — the
payload is the `quenching-docs` domain/consumption doctrine plus the `docs/catalog/`
scaffold and templates; the generated × curated separation is **signalled**, not installed.
See [Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [How the Open Knowledge Format can improve data sharing — Google Cloud Blog](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) — Google Cloud · 2026-06-12
- [Google Cloud introduces the Open Knowledge Format (OKF) — MarkTechPost](https://www.marktechpost.com/2026/06/16/google-cloud-introduces-open-knowledge-format-okf-a-vendor-neutral-markdown-spec-for-giving-ai-agents-curated-context/) — 2026-06-16
- [Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic · accessed 2026-06-28
