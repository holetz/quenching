---
name: quenching-skill-map
description: "Use to turn a skill, agent system, or architecture into a single self-contained interactive HTML \"kit map\" — one .html file, no external dependencies, opens offline in any browser. Triggers: \"criar um mapa visual da skill\", \"gerar um .html do que foi construído\", \"infográfico/fluxo em HTML\", \"mapa interativo da arquitetura\", \"kit map\", \"visualize this skill/system as HTML\"."
---

<!-- GENERATED FROM .claude/commands/skill-map.md -->


# /skill-map

Turn a system you built — a skill and its references, an agent studio, a layered
architecture — into **one self-contained interactive HTML map**: a layered "kit"
infographic like the *Agent Development Kit* poster (a header, numbered layer
bands, cards, input/output side rails, connectors, a principles footer).

> **What it produces.** A single `.html` file with **inline CSS + JS and no
> external requests** (no CDN, no web fonts, no remote images — emoji/inline SVG
> only), so it opens offline in any browser and can be shared as a file.

## Non-negotiables
- **One self-contained file.** Everything inlined; nothing fetched at runtime.
- **Facts only.** Every layer, card, and label maps to a real component of the
  system (read it with `rg`/Read first) — never invent a layer or a feature.
- **Legible in light and dark**, and responsive (bands stack on narrow screens).
- **Interactive but robust** — with JS off, the full map is still readable.

## Language / localization
The map is generated in the **requested language** (or the sources' language) —
default English; produce **pt-BR** when asked. Translate the *prose*: title
subtitle & tagline, layer titles/roles, card labels & one-line details, the side
rails, the footer principles, and the UI strings (theme button, "expand all", the
detail close). **Keep identifiers in their original form** — file names
(`storytelling.md`), agent names (`docs-architect`), commands (`--strict`,
`mkdocs build`), and product names (MkDocs Material, TL;DR). Set the matching
`<html lang="…">`, and keep the `title=` fallback in the same language as the
`data-detail`. Emit one file per language (e.g. `map.html`, `map.pt-br.html`); a
single file may instead carry an EN/PT toggle if the user prefers.

## The workflow

### 1 — Inventory the system (read-only)
Read the real thing with `rg`/Glob before drawing. For a skill, that's its
`SKILL.md` + `references/` + any sub-agents. Extract:
- **Inputs** (what goes in) and **outputs** (what comes out) → the side rails.
- **Layers** — the 3–6 conceptual bands (e.g. cycle · library · agents · gates).
- **Cards** — the concrete items inside each layer (each with a one-line detail).
- **Principles** — the invariants → the footer.

### 2 — Map to the visual model
Assign each layer a number, an accent color, and an icon; place items as cards.
The anatomy, palette, and component specs are in
[design-spec.md](.agents/references/skill-cartographer/design-spec.md).

### 3 — Generate the HTML
Write one `.html` following the spec: header (title · subtitle · optional mark),
left rail (inputs) → numbered layer bands (each: badge + title + subtitle + card
grid) → right rail (outputs), a connectors motif, and a footer principles row.
Inline all CSS/JS. Each card carries a `data-detail` used by the click-to-expand
panel.

### 4 — Add interactivity
- **Hover** — card lifts + accent border.
- **Click** — opens a detail panel (or inline reveal) with the card's `data-detail`.
- **Theme toggle** — light/dark via a `data-theme` attribute + `prefers-color-scheme`.
- Respect `prefers-reduced-motion`.

### 5 — Verify & deliver
Confirm the file is self-contained and parses:
```bash
grep -Eic 'https?://[^"]*\.(css|js)|cdn|googleapis|unpkg|jsdelivr' map.html   # want 0 external asset refs
```
Report the path; offer to open it or publish it as an Artifact for instant viewing.

## Style target
The *Agent Development Kit* poster look: warm paper background, a centered title
with a small mark, **numbered layer bands** in soft pastel tints, white cards with
a colored left accent and checkmark/■ bullets, thin connectors between bands, two
vertical **side rails** (inputs left, outputs right), and a **footer row** of small
icons + captions. Elegant restraint — every card carries information, never
decoration. Full recipe: [design-spec.md](.agents/references/skill-cartographer/design-spec.md); a complete
worked file is in [examples/](.agents/references/skill-cartographer/examples/).

## References
- [design-spec.md](.agents/references/skill-cartographer/design-spec.md) — palette, layer/card anatomy, side
  rails, connectors, typography, interactivity, responsive rules.
- [examples/mkdocs-storyteller.html](.agents/references/skill-cartographer/examples/mkdocs-storyteller.html) — a full
  map of the legacy documentation studio (EN); copy it as the working template.
- [examples/mkdocs-storyteller.pt-br.html](.agents/references/skill-cartographer/examples/mkdocs-storyteller.pt-br.html)
  — the same map localized to **pt-BR** (identifiers kept in English).
