# Engagement checklist — definition of done

The hard gate. Nothing ships until it passes. A page that fails **any** gate goes
back into the [editorial loop](editorial-loop.md); it is never silently shipped.

## Score gate (the rubric decides)
- [ ] **Every page scored** on all ten [rubric](quality-rubric.md) dimensions.
- [ ] **No dimension scores 0** on any shipped page.
- [ ] **Critical dimensions ≥ 2:** Integrity/source · Scannability · Navigation.
- [ ] **Overall average ≥ 2.5** per page (landings & indexes **≥ 3.5**).
- [ ] Any page below threshold is **reported as such**, with the failing dimensions
      and the reason (usually a source gap) — not passed off as done.

## The five forbiddens (auto-fail)
- [ ] **No fake depth** — no page that sounds technical but says nothing checkable.
- [ ] **No pretty-but-useless** — no visual, hero, or flourish without a function.
- [ ] **No README dump** — every page rewritten for a reader who arrived from search.
- [ ] **No claims without source** — see the ledger gate below.
- [ ] **No section without intent** — every section answers "why keep reading?".

## Hard build gates (must be green)
- [ ] **`mkdocs build --strict --site-dir .mkdocs-check`** passes with zero
      warnings (throwaway dir so a live server can't block it; then `rm -rf`).
- [ ] **No orphan pages** — every `docs/*.md` in `nav`; every `nav` entry has a file.
- [ ] **All internal links relative and resolving** (`--strict` enforces this).
- [ ] **Every extension used is enabled** (tabs, emoji, Mermaid, cards).

## Content gates (the human read)
- [ ] **Every page has a hook** — first line states what it is / why you're here.
- [ ] **One central idea per page.**
- [ ] **No wall of text** — nothing longer than a screen without a heading, list,
      table, or callout.
- [ ] **Comparisons are tables, processes are flows, options are cards** — not prose.
- [ ] **Risks/tips/tradeoffs are callouts**; **every rule states its why**.
- [ ] **Every page ends with a next step.**

## Visual gates (intent, not carnival)
- [ ] **No visual without a function**; icons are consistent semantic signposts.
- [ ] **Mermaid** for flows/architecture; ≤ ~9 nodes; edges labeled.
- [ ] **Images cleared first** — proposed by strategy, vendored locally, none block
      the build ([visual-language.md](visual-language.md)).
- [ ] **Palette/typography** match the repo; light **and** dark both look right.

## Source-ledger gate (truth)
- [ ] **A [source ledger](source-ledger.md) exists** for pages with strong claims.
- [ ] **No invented facts** — every strong claim traces to file / code / provided
      doc / user link / **marked** inference.
- [ ] **No fact only in an image** — critical facts also in text.
- [ ] **Open `source gap`s flagged**, never fabricated over.

## Agent-readability gate
- [ ] Headings descriptive & stable; anchors resolve ([llm-readability.md](llm-readability.md)).
- [ ] Reusable contracts carry a `TL;DR for agents` block.
- [ ] Examples are real, copyable, with expected output.
- [ ] Core terms defined once (glossary) and linked; a concept map/routing table exists.

## Visual-QA gate
- [ ] Ran the [visual QA](visual-qa.md) pass (or declared the static-only fallback
      + its limitation honestly).
- [ ] Dark/light both legible; mobile/narrow reflows; motion honors
      `prefers-reduced-motion`.

## Journey gate (the whole read)
- [ ] Walk the 3 reader journeys ([information-architecture.md](information-architecture.md))
      end to end — no dead-ends, no forced backtracking.

## Reporting done (phase 9)
Report: per-page **rubric scores**, the **source ledger** for strong claims, the
**validation** result (build + visual QA or declared fallback), **residual gaps**,
and any page marked below threshold. **Never claim done on a red build.**
