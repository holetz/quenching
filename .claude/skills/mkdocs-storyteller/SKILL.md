---
name: mkdocs-storyteller
description: >-
  Use when turning raw Markdown (READMEs, specs, evolution notes, a pasted
  document) into an engaging, intuitive, technically-deep MkDocs Material
  documentation site — restructuring the .md into a story-driven page tree,
  wiring the nav, and previewing it live on a local mkdocs dev server. This
  skill authors the STORY; MkDocs renders it. Triggers: "transformar os md em
  mkdocs", "montar/reconstruir a documentação", "reconstruir o /docs", "deixar
  os docs mais engajantes/palatáveis", "rodar o mkdocs local", "subir o preview
  da doc", "make the docs a joy to read".
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# mkdocs-storyteller

Turn a pile of `.md` into documentation people *want* to read — the way the
[Claude docs](https://code.claude.com/docs/en/claude-directory) read: intent
first, scannable, one idea per page, technical depth on tap. You do the
**storytelling and structure**; MkDocs (a Python lib) does the rendering; the
reader gets a live local site to judge the result.

> **Division of labor.** This skill decides *what each page says, in what order,
> and in what shape*. It does **not** reinvent rendering — that is MkDocs
> Material's job. It does **not** invent facts — every claim traces back to a
> source `.md` or the codebase.

## The narrative loop (run in order)

### 1 — Derive the current shape (read-only)
Before writing anything, know the terrain:
- **Sources**: which `.md` files are the raw material (`git ls-files '*.md'`,
  READMEs, specs, the doc the user pasted). Note who each one is *for*.
- **Site state**: read `mkdocs.yml` (theme, `markdown_extensions`, `plugins`,
  `nav`) and the existing `docs/` tree. Is there a site already, or greenfield?
- **Toolchain**: how the site runs — here it's `uv` + `make docs-serve` /
  `make docs-build` (see [references/live-preview.md](references/live-preview.md)).

Report the shape in two lines before proposing changes.

### 2 — Design the story arc (the part that matters)
Documentation is a **read**, not a dump. Draft the arc first, on paper:
- **Audience & intent** per section — a newcomer skimming vs. an engineer
  implementing want different pages. Split them; don't average them.
- **One spine, prev→next.** Order pages so each answers the question the last
  one raised. A landing page hooks with the *problem*, then the *solution*,
  then *how*.
- **One idea per page.** If a page needs two H1-sized ideas, it's two pages.
- **Progressive disclosure.** Lead with the intent and the shortest path;
  push depth into later sections, tabs, and collapsible admonitions — never
  make the reader scroll past what they don't need yet.

Map each source `.md` → target page(s). Full patterns:
[references/storytelling.md](references/storytelling.md).

### 3 — Author each page for engagement *without* losing rigor
Rewrite, don't just relocate. Every page earns its keep with:
- a **one-sentence hook** up top (what this is / why you're here),
- **scannable structure** — short paragraphs, meaningful headings, tables for
  anything comparative,
- **the "why"**, not only the "what" — the reason a rule exists is the part
  that sticks,
- **runnable, real examples** (real package names, real commands — no `foo`),
- **Material affordances** to carry meaning: admonitions (`!!! note/tip/warning`),
  content tabs, card grids for "choose your path", code annotations, emoji/icons
  as signposts. The toolkit + copy-paste snippets + the extensions each needs:
  [references/material-toolkit.md](references/material-toolkit.md).

Keep the technical altitude high — palatable is not shallow. The goal is a
reader who understands *more* because it was pleasant, not less.

### 4 — Wire the navigation
Update `mkdocs.yml` `nav:` to match the new arc (labels are the reader's map —
make them descriptive, e.g. `The knowledge surface & how it rots`, not
`knowledge-surface`). Enable any `markdown_extensions`/`features` the new pages
depend on. Keep internal links **relative** (`context/index.md`) so
`--strict` resolves them.

### 5 — Preview it live
Spin up the dev server and hand the reader a URL to judge:
```bash
make docs-serve      # → http://127.0.0.1:8000, live-reloads on every save
```
Run it in the background, confirm it bound, and give the user the local URL.
Full runbook (including plain `uv run mkdocs serve`, port conflicts, and how to
read the reload log): [references/live-preview.md](references/live-preview.md).

### 6 — Gate on a strict build
Before calling it done:
```bash
make docs-build      # mkdocs build --strict — fails on any broken ref/nav
```
A green strict build is the definition of done. Fix every warning it prints
(dangling links, pages missing from `nav`, unknown extensions).

## Invariants
- **Story, not rendering.** Restructure and rewrite `.md`; let MkDocs render.
  Reach for CSS only when a Material feature genuinely can't express the idea.
- **No invented facts.** Every claim resolves to a source `.md` or the code. A
  gap in the sources is a gap in the docs — flag it, don't fabricate it.
- **The repo's convention wins.** Match the existing palette, tone, extensions
  and file layout unless the user asks to change them. Propose upgrades; don't
  impose them.
- **`--strict` is the bar.** Nothing ships with a red build.

## References
- [references/storytelling.md](references/storytelling.md) — the narrative
  patterns (arc, page shapes, the Claude-docs voice, progressive disclosure).
- [references/material-toolkit.md](references/material-toolkit.md) — MkDocs
  Material features → the engaging look, with snippets and required extensions.
- [references/live-preview.md](references/live-preview.md) — running the dev
  server, the strict build gate, and troubleshooting.
