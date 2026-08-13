---
okf_version: "0.1"
---

# `/.knowledge/` — OKF knowledge bundle

The canonical knowledge tree of this repository, an **Open Knowledge Format (OKF v0.1)**
bundle. Each **home** has a fixed name and a single purpose; anyone moving between
repositories that adopt this method finds the **same tree in the same place**. This
`index.md` is the bundle's front door (a reserved listing — the only one that carries
frontmatter, and only `okf_version`). Folder names and frontmatter keys are canonical
English kebab-case; all prose the agent authors follows the repo's declared language —
[standards/agents/communication.md](/.knowledge/standards/agents/communication.md) owns that rule.

## Homes

* [standards/](/.knowledge/standards/index.md) — how **WE** do it (current contracts/conventions), by subject; agreed-but-unproven rules sit here as `authority: background`
* [vision/](/.knowledge/vision/index.md) — direction segmented by area, no deadline
* [documentation/](/.knowledge/documentation/index.md) — product docs site (Diátaxis: tutorials, how-to, reference, explanation)
* [concepts/](/.knowledge/concepts/index.md) — generic knowledge we hold (domain concepts, explanations, learnings); ships the fixed [glossary.md](/.knowledge/glossary.md) term lookup
* [external/](/.knowledge/external/index.md) — facts about what **WE CONSUME** (external, background)
* [catalog/](/.knowledge/catalog/index.md) — our **data** / domain (`system/catalog/schema/table`)

## Boundaries (memorable summary)

- `standards/` = "how **WE** do it (current/active)"; an agreed-but-unproven rule sits here as `authority: background` (no separate decisions home).
- `concepts/` = "generic **understanding** we hold" (concepts/explanations; non-binding).
- `external/` = "facts about what **WE CONSUME** (external, background)".
- `catalog/` = "our **data** / domain".
- The **task inbox** lives at `/.specs/backlog/`, **outside** this bundle (quenching-managed).
- `patterns` **is not a silo** — it dissolves into `standards/architecture/`.

**Resolving a term.** Unfamiliar repo word, acronym, or codename? Look it up in the glossary
first — [glossary.md](/.knowledge/glossary.md), the A–Z lookup (one entry per
term, linked to its full doc when one exists): `grep -i '<term>' /.knowledge/glossary.md`.

The full contract (homes, types, migration doctrine, conformance) lives in the `quenching`
skills' `references/`.
