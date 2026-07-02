# Engagement checklist — definition of done

Nothing ships until it passes this gate. Run top to bottom; the build gate is
non-negotiable.

## Hard gates (build must be green)
- [ ] **`uv run mkdocs build --strict`** passes with zero warnings.
- [ ] **No orphan pages** — every `docs/*.md` is in `nav`, every `nav` entry has a
      file.
- [ ] **All internal links relative and resolving** (`--strict` enforces this).
- [ ] **Every extension used is enabled** in `markdown_extensions` (tabs, emoji,
      Mermaid, cards).

## Content gates (the human read)
- [ ] **No README dump** — every page was rewritten for a reader who arrived from
      search, not from the repo root.
- [ ] **No wall of text** — no section runs longer than a screen without a
      heading, list, table, or callout.
- [ ] **Every page has a hook** — the first sentence states what it is / why
      you're here.
- [ ] **One central idea per page.**
- [ ] **Comparisons are tables, processes are flows, options are cards** — not
      prose.
- [ ] **Risks/tips/tradeoffs are callouts.**
- [ ] **Every page ends with a next step.**
- [ ] **Every rule states its why.**

## Visual gates (intent, not carnival)
- [ ] **No visual without a function** — every diagram/card/tab/icon carries
      information.
- [ ] **Icons/emoji are semantic signposts**, consistent site-wide, one per
      card/section max.
- [ ] **Mermaid** used for flows/architecture; ≤ ~9 nodes each; edges labeled.
- [ ] **Images cleared first** — external images proposed by strategy (screenshot
      / Mermaid / local asset) and vendored locally; none block the build.
- [ ] **Palette/typography** match the repo; light **and** dark both look right.

## Integrity gates (truth)
- [ ] **No invented facts** — every technical claim traces to a source `.md`, the
      code, or a provided link.
- [ ] **No fact only in an image** — critical facts also exist in text.
- [ ] **Gaps flagged, not fabricated** — where the sources are silent, the docs say
      so rather than inventing.

## Agent-readability gates
- [ ] Headings descriptive and stable; anchors resolve
      ([llm-readability.md](llm-readability.md)).
- [ ] Reusable contracts carry a `TL;DR for agents` block.
- [ ] Examples are real, copyable, with expected output.
- [ ] Core terms defined once (glossary) and linked; a concept map/routing table
      exists.

## Journey gate (the whole read)
- [ ] Walk the 2–3 reader journeys from
      [information-architecture.md](information-architecture.md) end to end — no
      dead-ends, no forced backtracking.
- [ ] Preview live (light + dark, narrow viewport) and read it as a stranger would.

## Reporting done
When it passes, report: what changed, the journeys it now serves, the strict-build
result, and any gaps flagged for the source owners to fill. Never claim done on a
red build.
