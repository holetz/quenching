# Kit-map design spec

The visual language of the layered "kit" infographic (the *Agent Development Kit*
poster look), and how to build it as one self-contained HTML file.

## Anatomy
```text
┌─────────────────────────── header (title · subtitle · mark) ───────────────────────────┐
│  ┌────────┐   ┌───────────────── numbered layer bands ─────────────────┐   ┌────────┐   │
│  │  LEFT  │   │  [1] Layer title — subtitle                             │   │ RIGHT  │   │
│  │  RAIL  │ → │      [ card ] [ card ] [ card ] [ card ]                │ → │  RAIL  │   │
│  │ inputs │   │  [2] Layer title …                                      │   │ outputs│   │
│  └────────┘   └────────────────────────────────────────────────────────┘   └────────┘   │
│                       footer · principles row (icon + caption)                            │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

## Palette (warm paper, pastel accents)
```css
:root{
  --paper:#f6f4ec; --ink:#26241f; --muted:#6b6558; --line:#e2ddce; --card:#fffdf7;
  --l1:#3f9d78; --l2:#2f8f9d; --l3:#e08a3c; --l4:#8b6cc9; --l5:#3f6fd1; /* per-layer accents */
}
:root[data-theme="dark"]{
  --paper:#1c1b18; --ink:#efece3; --muted:#a49d8c; --line:#332f28; --card:#24221d;
}
```
Each layer uses **one** accent (`--lN`) for its number badge, left card accent, and
band tint (`color-mix(in srgb, var(--lN) 8%, var(--paper))`). Never more than ~5
accents — the poster reads calm because color is rationed.

## Layer band
- Full-width rounded block, soft tinted background, ~1px `--line` border.
- **Number badge**: a rounded square in the layer accent, white numeral.
- **Title** (bold) + **subtitle** (muted, the layer's role, e.g. "The Knowledge
  Layer").
- A responsive **card grid** inside (`display:grid; grid-template-columns:
  repeat(auto-fit,minmax(180px,1fr)); gap`).

## Card
- White (`--card`), rounded, thin border, **left accent stripe** in the layer color.
- Icon (emoji or inline SVG) + bold label + a short line.
- Bullets use `■`/`✓` in the accent color.
- `data-detail="…"` holds the one-line explanation surfaced on click.
- Hover: translateY(-3px) + accent border + soft shadow.

## Side rails
Two narrow vertical panels flanking the bands: **left = inputs** (raw md, README,
specs, docs tree), **right = outputs** (the site; humans, engineers, LLMs). Each is
a stack of small chips with an icon. On narrow screens they collapse to full-width
strips above/below the bands.

## Connectors
Thin vertical guides between bands: a centered 1–2px `--line` rule, or small
downward chevrons (`▾`) in `--muted`. Keep them subtle — they imply flow, they
don't shout. Rails connect to bands with a `→` glyph or a short horizontal rule.

## Typography
- Title: large (clamp 1.8–2.6rem), heavy, slightly condensed; a small ✳/●
  mark before it.
- System font stack only (no web fonts — self-contained):
  `-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.
- Body 14–15px, muted subtitles, generous line-height.

## Interactivity (inline JS, robust)
- **Detail panel**: a fixed/sticky strip (or a slide-down under the clicked card)
  that shows `data-detail`. Click again / Esc to close.
- **Theme toggle**: button flips `document.documentElement.dataset.theme`; default
  from `matchMedia('(prefers-color-scheme: dark)')`.
- **Hover highlight** is pure CSS.
- **JS-off safety**: cards render fully without JS; `data-detail` can also be a
  `title=` attribute so hovering still surfaces it.
- Honor `@media (prefers-reduced-motion: reduce)` — kill transforms/animation.

## Responsive
- Desktop: rails as side columns via `grid-template-columns: 200px 1fr 200px`.
- ≤ ~900px: single column — rails become horizontal chip strips; bands stack;
  card grid drops to 1–2 columns. Never allow horizontal page scroll.

## Self-contained checklist
- [ ] No `<link rel=stylesheet>`, no `<script src>`, no web fonts, no remote images.
- [ ] All CSS in one `<style>`, all JS in one `<script>`.
- [ ] Icons are emoji or inline `<svg>`.
- [ ] Opens with `file://` offline; light + dark both legible.
- [ ] Every card/label traces to a real component of the mapped system.
