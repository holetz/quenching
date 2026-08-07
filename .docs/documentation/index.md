# `documentation/` — product documentation (Diátaxis, renderable site)

Prose documentation written for a human reader, structured as a Diátaxis site — the pages
you publish with a static-site generator. Absorbs the former `guides/` home. Each page
carries `type: documentation`.

**Boundary:** a page you would put on the published documentation site (narrative, for a
human) lives here; structured/typed knowledge for the team+agent to operate lives in the
other homes.

- vs. [knowledge/](/.docs/knowledge/index.md) — a published-site explanation page →
  `concepts/`; internal team understanding (mental model, learning, glossary) → `knowledge/`.
- vs. [standards/](/.docs/standards/index.md) — a how-to that describes the current
  *contract* (the rule) is a `standard`; teaching how to *execute* a task is a how-to here.
- vs. the root [reference/](/.docs/reference/index.md) — our product's own reference lives in
  `reference/` below; facts about an external asset WE CONSUME go to the root `reference/` home.

## Sections (Diátaxis)

* [getting-started/](getting-started/index.md) — tutorials: learning-oriented, "get it running"
* [how-to/](how-to/index.md) — task-oriented recipes (the former `guides/`)
* [reference/](reference/index.md) — reference for our own product / API
* [concepts/](concepts/index.md) — explanation: how and why, for the site's reader

## Rendering this home

This home is a plain Markdown tree, consumable by any documentation site generator. The
plugin ships a batteries-included **mkdocs-material** setup at the repo root (`mkdocs.yml`,
`requirements.txt`) — first installed by `quenching-docs-align`, and created/updated/verified from
then on by **`/docs:documentation:build`** (the site layer's owner: config, `.pages` nav, and
a `mkdocs build --strict` check):

- The generator points here — `docs_dir: .docs/documentation` in `mkdocs.yml` (kept at the
  repo root, **outside** the bundle).
- Each reserved `index.md` doubles as the **section landing page** (mkdocs-material's
  `navigation.indexes` feature) — no separate landing file needed.
- Navigation follows the folder tree automatically via `mkdocs-awesome-pages-plugin`; the
  `.pages` file in each section sets its title and order. A new section has no `.pages` until
  `/docs:documentation:build` writes one.
- **Link caveat:** absolute OKF links (`/.docs/standards/…`) point outside a site rooted at
  `documentation/` and will not resolve in the built HTML — keep these pages self-contained
  and cross-link to other homes sparingly.
