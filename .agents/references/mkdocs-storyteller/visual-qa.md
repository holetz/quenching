# Visual QA

A green build proves the *markup* is valid — not that the *page looks right*.
Phase 8 validates both: the strict build **and** the rendered experience across
viewports and themes.

## Build first (server-safe)
A running `mkdocs serve` locks `site/`. Build to a throwaway dir so QA never
collides with a live preview:
```bash
mkdocs build --strict --site-dir .mkdocs-check    # or: uv run mkdocs build ...
# … inspect .mkdocs-check/ …
rm -rf .mkdocs-check
```
`--strict` fails on dangling links, orphan pages, and unknown extensions. Fix every
warning before looking at pixels.

## The visual checklist
Walk each item; a page isn't done until all pass.

| Check | What "pass" means |
| --- | --- |
| **Home — desktop** | hero fits one fold; no horizontal scroll |
| **Home — mobile / narrow** | cards reflow to one column; nothing clips |
| **Dark mode** | text/badges/cards legible; no invisible-on-dark elements |
| **Light mode** | same, inverted |
| **Cards** | no text overflow; even heights; links reachable |
| **Hero** | present only on landings; doesn't dominate the whole screen |
| **Mermaid** | renders as SVG (not a raw code block); readable in both themes |
| **Tabs** | switch correctly; content not duplicated/leaking |
| **Buttons & links** | visible in both themes; hit targets sane |
| **Contrast** | body text meets ~AA against its background |
| **Motion** | animations honor `prefers-reduced-motion: reduce` |

## How to actually check
**If a browser/Playwright/screenshot tool is available:** load the built site (or
`mkdocs serve`), screenshot the landing and one deep page at desktop and narrow
widths, in both themes, and eyeball the table above.

**If it is NOT available (common):** fall back to static verification of the built
HTML and **declare the limitation**:
```bash
grep -oE '<title>[^<]*</title>' .mkdocs-check/index.html | head -1   # title detected
grep -c 'class="mermaid"'  .mkdocs-check/**/index.html                # diagrams present
grep -c 'class="q-badge"'  .mkdocs-check/**/index.html                # badges present
grep -oE 'stylesheets/[^"]+|javascripts/[^"]+' .mkdocs-check/index.html | sort -u
grep -Eo 'prefers-reduced-motion' docs/stylesheets/*.css             # motion guard exists
```
Then report: *"Static checks pass (markup, assets wired, components present).
Pixel-level dark/light/mobile QA not run — no browser tool available; recommend a
manual pass at `http://127.0.0.1:8000`."* Never claim visual QA you didn't do.

## Reduced-motion & theming rules (build them in)
- Any animation ships with an `@media (prefers-reduced-motion: reduce)` off-switch.
- Any custom color reads from Material's CSS variables (or defines both schemes) so
  light **and** dark both work — a page that only looks right in one mode fails QA.

## Output
Produce a short **validation report** for phase 9: build result, the checklist
outcome (or the declared static-only fallback), and any visual defect that sent a
page back into the [editorial loop](editorial-loop.md).
