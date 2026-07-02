# MkDocs Material toolkit

The Material features that carry the "engaging Claude-docs look" — and, for
each, the `markdown_extensions` it needs in `mkdocs.yml`. Enable an extension
**before** using its syntax, or `--strict` fails.

## Extensions to enable (superset for a rich site)
```yaml
markdown_extensions:
  - admonition            # !!! note / tip / warning callouts
  - attr_list             # {.class} / {: attrs } — needed by grids, buttons
  - md_in_html            # Markdown inside <div> — needed by card grids
  - tables
  - toc:
      permalink: true
  - pymdownx.superfences  # nested code / content in fences
  - pymdownx.highlight
  - pymdownx.inlinehilite
  - pymdownx.details      # ??? collapsible admonitions
  - pymdownx.tabbed:      # content tabs
      alternate_style: true
  - pymdownx.emoji:       # :material-icon: / :rocket: signposts
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
```
The repo currently ships the first block (admonition, tables, toc, superfences,
highlight, inlinehilite, details). Add `attr_list`, `md_in_html`,
`pymdownx.tabbed`, `pymdownx.emoji` when a page starts using grids, tabs or
icons — don't enable what no page uses.

## Theme features worth turning on
```yaml
theme:
  features:
    - navigation.instant      # SPA-like, fast page loads
    - navigation.instant.progress
    - navigation.tracking     # URL follows the active anchor
    - navigation.top          # back-to-top button
    - navigation.indexes      # section landing pages
    - navigation.footer       # prev/next footer — powers the "one read"
    - toc.follow
    - content.code.copy       # copy button on code blocks
    - content.code.annotate   # (1) annotations inside code
    - content.tabs.link       # tabs sync across the page
    - search.suggest
    - search.highlight
```

## Snippets

### Admonitions — meaning by color
```markdown
!!! tip "Applied tip"
    The right position on the spectrum depends on the stakes.

!!! warning "Don't"
    Never remove a pre-existing artifact without an explicit OK.

??? note "Why it's built this way (click to expand)"
    Progressive disclosure: the skimmer skips this; the curious opens it.
```

### Card grid — "choose your path" (needs `attr_list` + `md_in_html`)
```markdown
<div class="grid cards" markdown>

-   :rocket: **Quick start**

    ---

    Run it in one command and see output in 30 seconds.

    [:octicons-arrow-right-24: Get started](install.md)

-   :material-map: **The 8-step workflow**

    ---

    How the tool actually thinks, step by step.

    [:octicons-arrow-right-24: Read the workflow](workflow.md)

</div>
```

### Content tabs — one concept, many contexts (needs `pymdownx.tabbed`)
```markdown
=== "macOS / Linux"
    ```bash
    make docs-serve
    ```
=== "Windows (PowerShell)"
    ```powershell
    uv run mkdocs serve
    ```
```

### Code annotations (needs `content.code.annotate` + `superfences`)
````markdown
```yaml
nav:
  - Home: index.md   # (1)!
```

1.  Labels here are the reader's map — make them descriptive, not filenames.
````

### Buttons (needs `attr_list`)
```markdown
[Get started](install.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/...){ .md-button }
```

## Palette
The repo uses `indigo`. Keep it unless the user wants a brand shift. Both a
light (`default`) and dark (`slate`) scheme with a toggle are already wired —
preserve the toggle; a site that only looks right in one mode reads as broken.

## When to reach past Material
Almost never. A card grid, tabs, admonitions and annotations cover the
Claude-docs feel. Only add `extra_css` for something Material genuinely can't
express (a true hero band, a bespoke landing). Custom CSS is maintenance debt —
justify it before adding it.
