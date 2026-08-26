# Documentation validation — strict build and honest rendered QA

The runbook for validating the generated site. It uses a throwaway build directory and reports
`unverified` when MkDocs is unavailable; it never claims a visual check that did not happen.

## Contents

`cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-documentation/validation.md`
returns the heading index; `--sections <name>` addresses one.

<!-- rules -->

## Strict build

Run from the target repository root:

```bash
mkdocs build --strict --site-dir <throwaway-dir>
```

Fallbacks are `python -m mkdocs build --strict --site-dir <throwaway-dir>` and
`uv run mkdocs build --strict --site-dir <throwaway-dir>`. Remove the throwaway directory after
inspection. Never run `mkdocs serve` from this command and never commit a built `site/`.

`--strict` must be zero-warning. It catches dangling links, orphan pages, unknown extensions and
nav mistakes. A warning is either fixed in the site layer or reported to the page-owning command.

## Static rendered checks

When a browser or Playwright is available, inspect the landing and one deep page at desktop and
narrow widths in both palettes. Otherwise run the static fallback over the built HTML:

```bash
grep -oE '<title>[^<]*</title>' <throwaway-dir>/index.html | head -1
grep -R -c 'class="mermaid"' <throwaway-dir>
grep -R -c 'class="q-badge"' <throwaway-dir>
grep -oE 'stylesheets/[^" ]+' <throwaway-dir>/index.html | sort -u
grep -R -Eo 'prefers-reduced-motion' .knowledge/documentation/assets/stylesheets/*.css
```

The static fallback verifies title, Mermaid markup, badges, CSS wiring and the motion guard. It
does not prove pixel-level dark/light/mobile layout; report that limitation and recommend a
manual browser pass. Check that cards reflow, contrast is readable, tabs switch, and Mermaid is
not a raw code block when a browser is available.

## Required rendered effects

The build report checks the page title, `class="mermaid"`, `class="q-badge"`, connected
`extra_css`, and `prefers-reduced-motion`. Custom colors use Material variables or both schemes;
animations have a reduced-motion off switch.

<!-- rationale -->

A green parser run proves markup, not pixels. Separating strict build from static and browser QA
keeps the report precise while retaining a useful no-browser fallback.
