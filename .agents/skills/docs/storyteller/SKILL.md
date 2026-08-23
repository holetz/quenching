---
name: quenching-docs-storyteller
description: "Use to GENERATE documentation, not just prettify Markdown — raw Markdown, a README, specs, notes or a whole docs/ tree becomes a MkDocs Material site humans want to read, engineers can execute, and LLMs can copy, navigate and reconstruct. Triggers: \"transformar/gerar os md em mkdocs\", \"montar/reestruturar a documentação\", \"reconstruir o /docs\", \"documentação mais engajante\", \"organizar a navegação dos docs\", \"criar landing da doc\", \"rodar/subir o mkdocs local\", \"documentação que um LLM consiga reutilizar\", \"make the docs a joy to read\", \"docs studio\", \"score the docs\"."
---

<!-- GENERATED FROM .claude/commands/docs/storyteller.md -->


# /docs:storyteller — the documentation studio

A **documentation-generation machine**, not a style guide. It turns raw material
into a MkDocs Material site that is, at once, a joy to read, executable by
engineers, and a reliable substrate for agents — the way the
[Codex](https://code.claude.com/docs/en/claude-directory),
[Codex Platform](https://platform.claude.com/docs) and Databricks docs read.

It thinks in six roles and works in cycles: **information architect · technical
editor · experience designer · critical reviewer · LLM reader · build validator.**

> **Division of labor.** This skill owns the **story, the architecture, and
> LLM-readability**; MkDocs owns **rendering**. It never invents facts — every
> claim traces to a source (see [source-ledger.md](.agents/references/mkdocs-storyteller/source-ledger.md)).

## Non-negotiables (read first)
- **Contracts before edits.** You may not touch a page until you have produced the
  six intermediate contracts ([output-contracts.md](.agents/references/mkdocs-storyteller/output-contracts.md)).
- **Score everything.** Every page is scored against the rubric
  ([quality-rubric.md](.agents/references/mkdocs-storyteller/quality-rubric.md)); a page below threshold is
  **not done**.
- **Beauty never replaces precision** — image ≠ fact, slogan ≠ contract, visual ≠
  structure ([signature-experience.md](.agents/references/mkdocs-storyteller/signature-experience.md)).
- **The build gate is hard.** Never declare done on a red `--strict` build, a
  broken link, or an orphan page ([engagement-checklist.md](.agents/references/mkdocs-storyteller/engagement-checklist.md)).
- **Scope:** work only inside the target docs. Don't touch `plugins/…` or
  unrelated files without confirmation.

## The three audiences (design for all, never average them)

| Reader | Wants | Optimize for |
| --- | --- | --- |
| **Human — skimmer** | "Is this for me? Where do I start?" | hook, scannability, next step |
| **Human — implementer** | "How exactly do I do this?" | real examples, exact commands, edge cases |
| **Agent (LLM)** | "What can I copy, reconstruct, cite?" | stable headings, contracts, TL;DR blocks, copyable code |

## The studio cycle (9 phases, in order)

### 1 — Diagnose (read-only)
Map the terrain with `rg`/Glob (`rg --files -g '*.md'`, read `mkdocs.yml`, the
`docs/` tree). Produce the **Diagnosis** contract. Method:
[information-architecture.md](.agents/references/mkdocs-storyteller/information-architecture.md).

### 2 — Information architecture
Design the site as a journey, by intent, not by filename. Produce the **Reader
journeys** and **IA proposal** contracts. Method:
[information-architecture.md](.agents/references/mkdocs-storyteller/information-architecture.md).

### 3 — Write (draft)
Rewrite, never relocate — hook, fast path, progressive depth, real examples, clear
next step. Craft: [storytelling.md](.agents/references/mkdocs-storyteller/storytelling.md). Skeletons per page
type: [page-patterns.md](.agents/references/mkdocs-storyteller/page-patterns.md).

### 4 — Visual design
Apply the **Visual plan** contract — every element carries meaning or is cut.
Decisions: [visual-language.md](.agents/references/mkdocs-storyteller/visual-language.md). Syntax:
[material-toolkit.md](.agents/references/mkdocs-storyteller/material-toolkit.md).

### 5 — LLM-readability
Make the same page reusable by agents (stable headings, anchors, `TL;DR for
agents`, contracts, glossary). Produce the **LLM-readability plan** contract.
Doctrine: [llm-readability.md](.agents/references/mkdocs-storyteller/llm-readability.md).

### 6 — Critique (hard)
Run the critical pass: hunt empty marketing, unsourced claims, useless visuals,
README-dump pages, fake depth. Score with the rubric. Roles & how to run the loop:
[editorial-loop.md](.agents/references/mkdocs-storyteller/editorial-loop.md).

### 7 — Reconstruct
Fix what critique flagged and re-score. Loop **critique → reconstruct** at most
**2–3 rounds** unless the user asks for more (limit in [editorial-loop.md](.agents/references/mkdocs-storyteller/editorial-loop.md)).

### 8 — Validate
Build strict and QA the rendered site (desktop/mobile, dark/light, Mermaid, tabs,
motion). Use a throwaway site dir so a live server never blocks it:
```bash
mkdocs build --strict --site-dir .mkdocs-check && rm -rf .mkdocs-check
```
Full runbook: [visual-qa.md](.agents/references/mkdocs-storyteller/visual-qa.md) · [live-preview.md](.agents/references/mkdocs-storyteller/live-preview.md).

### 9 — Deliver with a score
Report per-page rubric scores, the **Source ledger** for strong claims
([source-ledger.md](.agents/references/mkdocs-storyteller/source-ledger.md)), residual gaps, and the build
result. Nothing below threshold ships without being flagged.

## The editorial loop (how phases 3–8 actually run)
`draft → critique → reconstruct → validate`, bounded to 2–3 rounds. The main skill
orchestrates and may wear each role as a **pass**, or delegate to small
sub-agents that return a **condensed verdict** (never edit unbounded). See
[editorial-loop.md](.agents/references/mkdocs-storyteller/editorial-loop.md) — the sub-agents there are
**proposed**, created only with your confirmation, in `.agents/agents/`.

## Reference map

| When you're… | Read |
| --- | --- |
| Producing the required intermediate outputs | [output-contracts.md](.agents/references/mkdocs-storyteller/output-contracts.md) |
| Diagnosing & designing the site | [information-architecture.md](.agents/references/mkdocs-storyteller/information-architecture.md) |
| Writing a page | [storytelling.md](.agents/references/mkdocs-storyteller/storytelling.md) · [page-patterns.md](.agents/references/mkdocs-storyteller/page-patterns.md) |
| Learning by example (before → after) | [rewrite-examples.md](.agents/references/mkdocs-storyteller/rewrite-examples.md) |
| Choosing visuals / the syntax | [visual-language.md](.agents/references/mkdocs-storyteller/visual-language.md) · [material-toolkit.md](.agents/references/mkdocs-storyteller/material-toolkit.md) |
| Making it reusable by agents | [llm-readability.md](.agents/references/mkdocs-storyteller/llm-readability.md) |
| Making it memorable | [signature-experience.md](.agents/references/mkdocs-storyteller/signature-experience.md) |
| Running the critique/rewrite loop | [editorial-loop.md](.agents/references/mkdocs-storyteller/editorial-loop.md) |
| Scoring a page | [quality-rubric.md](.agents/references/mkdocs-storyteller/quality-rubric.md) |
| Tracing claims to sources | [source-ledger.md](.agents/references/mkdocs-storyteller/source-ledger.md) |
| Validating (build + visual QA) | [visual-qa.md](.agents/references/mkdocs-storyteller/visual-qa.md) · [live-preview.md](.agents/references/mkdocs-storyteller/live-preview.md) |
| Deciding if it's done | [engagement-checklist.md](.agents/references/mkdocs-storyteller/engagement-checklist.md) |
