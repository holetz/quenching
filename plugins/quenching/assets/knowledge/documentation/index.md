# `documentation/` — product documentation (Diátaxis, renderable site)

Prose documentation written for a human reader, structured as a Diátaxis site — the pages
you publish with a static-site generator. Absorbs the former `guides/` home. Each page
carries `type: documentation`.

**Boundary:** a page you would put on the published documentation site (narrative, for a
human) lives here; structured/typed knowledge for the team+agent to operate lives in the
other homes.

- vs. the `concepts/` home — a published-site explanation page →
  `documentation/explanation/`; internal team understanding (mental model, learning, glossary) → `concepts/`.
- vs. the `standards/` home — a how-to that describes the current
  *contract* (the rule) is a `standard`; teaching how to *execute* a task is a how-to here.
- vs. the root `external/` home — our product's own reference lives in
  `reference/` below; facts about an external asset WE CONSUME go to the root `external/` home.

## Sections (Diátaxis)

* [tutorials/](tutorials/index.md) — tutorials: learning-oriented, "get it running"
* [how-to/](how-to/index.md) — task-oriented recipes (the former `guides/`)
* [reference/](reference/index.md) — reference for our own product / API
* [explanation/](explanation/index.md) — explanation: how and why, for the site's reader

## Rendering this home

This home is a plain Markdown tree, consumable by any documentation site generator. The
plugin ships a batteries-included **Zensical** setup at the repo root (`zensical.toml`,
`requirements.txt`) — first installed by `quenching:knowledge:align`, and created/updated/verified from
then on by the **documentation family** — `plan`, `write`, `review`,
and `build`, conducted end to end by `produce` (the site layer's owner is `build`, which handles
config, the `nav`, CSS and a `zensical build --strict` check):

- The generator points here — `docs_dir = ".knowledge/documentation"` in `zensical.toml` (kept at
  the repo root, **outside** the bundle).
- Each reserved `index.md` doubles as the **section landing page** (the theme's
  `navigation.indexes` feature) — no separate landing file needed.
- Navigation is the explicit `nav` list in `zensical.toml`: no plugin derives it from the folder
  tree, so a new page is a new line there, written by
  `/quenching:knowledge:documentation:build`. A page absent from the list is still built and
  still searchable — it is only missing from the sidebar.
- **Editorial publication map:** `plan` decides, for every home, whether it is published,
  published through a curated route below `documentation/`, or not published. An exposed home is
  linked through that route; a `não publicar` home has no site link. Never publish an internal
  `/.knowledge/<home>/…` path as dead prose or as a broken URL.
