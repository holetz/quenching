---
okf_version: "0.1"
---

# `docs/` — OKF knowledge bundle

The canonical knowledge tree of this repository, an **Open Knowledge Format (OKF v0.1)**
bundle. Each **home** has a fixed name and a single purpose; anyone moving between
repositories that adopt this method finds the **same tree in the same place**. This
`index.md` is the bundle's front door (a reserved listing — the only one that carries
frontmatter, and only `okf_version`). Folder names and frontmatter keys are canonical
English kebab-case; only `audience: human` material follows the repo's language.

## Homes

* [standards/](/docs/standards/index.md) — how **WE** do it (current contracts/conventions), by subject
* [decisions/](/docs/decisions/index.md) — ADRs: open decisions; distill to `standards/` on implementation
* [vision/](/docs/vision/index.md) — direction segmented by area, no deadline
* [backlog/](/docs/backlog/index.md) — task inbox (raw or scoped; optional priority/tags), one file per task
* [documentation/](/docs/documentation/index.md) — product docs site (Diátaxis: getting-started, how-to, reference, concepts)
* [knowledge/](/docs/knowledge/index.md) — generic knowledge we hold (domain concepts, explanations, learnings); ships the fixed [glossary.md](/docs/knowledge/glossary.md) term lookup
* [reference/](/docs/reference/index.md) — facts about what **WE CONSUME** (external, background)
* [catalog/](/docs/catalog/index.md) — our **data** / domain (`system/catalog/schema/table`)

## Boundaries (memorable summary)

- `standards/` = "how **WE** do it (current/active)".
- `knowledge/` = "generic **understanding** we hold" (concepts/explanations; non-binding).
- `reference/` = "facts about what **WE CONSUME** (external, background)".
- `catalog/` = "our **data** / domain".
- `decisions/` → `standards/` on implementation (distill and leave).
- `patterns` **is not a silo** — it dissolves into `standards/architecture/`.

**Resolving a term.** Unfamiliar repo word, acronym, or codename? Look it up in the glossary
first — [knowledge/glossary.md](/docs/knowledge/glossary.md), the A–Z lookup (one entry per
term, linked to its full doc when one exists): `grep -i '<term>' docs/knowledge/glossary.md`.

The bundle's change history is in [log.md](log.md). The full contract (homes, types,
migration doctrine, conformance) lives in the `claude-quenching` skills' `references/`.
