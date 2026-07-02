---
name: mkdocs-storyteller
description: >-
  Use when turning raw Markdown (READMEs, specs, internal notes, a pasted
  document, or an existing docs/ tree) into a MkDocs Material documentation site
  that humans want to read AND agents can reuse, copy, and reconstruct precisely.
  It diagnoses the sources, designs an intent-based information architecture,
  rewrites each page into scannable technical storytelling, applies a visual
  language (icons, cards, tabs, Mermaid, badges, hero), makes the output
  LLM-readable, and previews it live. Triggers: "transformar os md em mkdocs",
  "montar/reestruturar a documentação", "reconstruir o /docs", "documentação
  mais engajante/palatável", "organizar a navegação dos docs", "criar landing da
  doc", "rodar/subir o mkdocs local", "make the docs a joy to read", "docs an LLM
  can reuse".
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# mkdocs-storyteller

Turn a pile of Markdown into documentation that is a **joy for humans** and a
**reliable substrate for agents** — the way the [Claude Code](https://code.claude.com/docs/en/claude-directory)
and [Claude Platform](https://platform.claude.com/docs) docs read: intent-first
navigation, "choose the right file" tables, actionable pages, elegant restraint.

> **Division of labor.** This skill owns three things: the **story** (what each
> page says and in what order), the **information architecture** (how a reader
> navigates by intent), and **LLM-readability** (how an agent reuses it). MkDocs
> Material owns **rendering**. You never invent facts — every claim traces to a
> source `.md`, the codebase, or a link the user gave you.

## The three audiences (design for all, never average them)

Every page serves one of three readers primarily. Know which before you write:

| Reader | Wants | Optimize for |
| --- | --- | --- |
| **Human — skimmer** | "Is this for me? Where do I start?" | hook, scannability, a clear next step |
| **Human — implementer** | "How exactly do I do this?" | real examples, exact commands, edge cases |
| **Agent (LLM)** | "What can I copy, reconstruct, and cite?" | stable headings, contracts, TL;DR blocks, copyable code |

A page that tries to serve all three at once serves none. Split them — or layer
them with progressive disclosure. See [llm-readability.md](references/llm-readability.md).

## The operating loop (run in order)

### 1 — Diagnose before writing (read-only)
Map the terrain with `rg`/Glob before touching anything:
- **Sources & site**: `rg --files -g '*.md'`, the READMEs, `mkdocs.yml`
  (theme, extensions, plugins, `nav`), the existing `docs/` tree.
- **Reader model**: who is this *for*, what is their intent and technical
  maturity, what journey are they on.
- **Faults**: gaps, duplication, orphan pages, weak titles, walls of text, and
  facts smeared across files.
- **Audience split**: tag each chunk human-skimmer / implementer / agent.

Report the diagnosis before proposing structure. Method:
[information-architecture.md](references/information-architecture.md) · agent lens:
[llm-readability.md](references/llm-readability.md).

### 2 — Design the architecture (the part that matters most)
Draft the site as a **journey**, not a file list:
- A narrative spine — **landing (promise) → problem → solution → mental model →
  quick start → workflow → reference → examples → maintenance** — each stage
  answering the question the last one raised.
- **Navigate by intent, not filename** ("Get started", "Guides", "Reference"),
  Databricks-style usage paths.
- **One central idea per page.** Two H1-sized ideas → two pages.
- Every section must earn *"why should I keep reading?"*.

Full method (journeys, nav wiring, the arc): [information-architecture.md](references/information-architecture.md).

### 3 — Write irresistible-but-objective pages
Rewrite, never relocate. Each page carries: a strong **hook**, a **scannable
summary**, the **fast path**, **progressive depth**, **real examples**, tables
for comparisons, flows for processes, diagrams for architecture, callouts for
risk/tips/decisions/tradeoffs, and a **clear next step**. Beautiful but
technically dense — never empty marketing. Craft & voice:
[storytelling.md](references/storytelling.md). Ready skeletons per page type:
[page-patterns.md](references/page-patterns.md).

### 4 — Apply the visual language with intent
Every visual element must carry meaning, never decorate. Choose the right form —
icons/emoji as semantic signposts, cards for "choose your path", tabs for
platforms/profiles/scenarios, Mermaid for flows/maps/architecture, badges for
status/audience/difficulty/read-time, a hero for the landing's first fold. Which
form for which content: [visual-language.md](references/visual-language.md).
Exact syntax + required extensions: [material-toolkit.md](references/material-toolkit.md).

!!! warning "Images are a proposal, not a default"
    Before adding any external image, **propose the strategy first** — real
    screenshot · Mermaid diagram · local asset · generated image — and never hide
    a critical fact only inside an image. Rules in [visual-language.md](references/visual-language.md).

### 5 — Make it LLM-readable too
The same page that delights a human must let an agent reuse it: descriptive,
stable headings; predictable anchors; `TL;DR for agents` blocks where useful;
copyable examples; explicit contracts; a glossary for core terms; consistent
relative links; a concept map/index. Doctrine: [llm-readability.md](references/llm-readability.md).

### 6 — Preview it live
Spin up the dev server and hand over a URL to judge:
```bash
make docs-serve      # → http://127.0.0.1:8000, live-reload; or: uv run mkdocs serve
```
Run it in the background, confirm it bound, report the URL. Runbook:
[live-preview.md](references/live-preview.md).

### 7 — Gate on quality (definition of done)
Nothing ships until it passes [engagement-checklist.md](references/engagement-checklist.md),
whose hard gate is a green **`uv run mkdocs build --strict`**.

## Invariants
- **Story, IA & agent-readability — not rendering.** Restructure and rewrite the
  Markdown; let MkDocs render. Reach for custom CSS/JS only when a Material
  feature genuinely can't express the idea (it's maintenance debt — justify it).
- **No invented facts.** Every technical claim resolves to a source `.md`, the
  code, or a provided link. A gap in the sources is a gap in the docs — flag it.
- **Beautiful *and* dense.** Never trade technical usefulness for polish. No
  empty marketing, no visual without a function, no page that reads like a README
  dump.
- **The repo's convention wins.** Match the existing palette, tone, extensions
  and layout unless asked to change them. Propose upgrades; don't impose them.
- **`--strict` is the floor**, not the ceiling.
- **Don't touch the shipped plugin** (`plugins/…`) or unrelated local changes
  without explicit confirmation.

## Reference map

| When you're… | Read |
| --- | --- |
| Diagnosing sources & designing the site | [information-architecture.md](references/information-architecture.md) |
| Writing the prose of a page | [storytelling.md](references/storytelling.md) |
| Reaching for a page skeleton | [page-patterns.md](references/page-patterns.md) |
| Deciding which visual to use | [visual-language.md](references/visual-language.md) |
| Needing the exact MkDocs syntax | [material-toolkit.md](references/material-toolkit.md) |
| Making the page reusable by agents | [llm-readability.md](references/llm-readability.md) |
| Running / previewing / building | [live-preview.md](references/live-preview.md) |
| Deciding if it's done | [engagement-checklist.md](references/engagement-checklist.md) |
