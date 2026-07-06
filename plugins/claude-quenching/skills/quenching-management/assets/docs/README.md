---
title: docs/ — canonical knowledge taxonomy of the repo
audience: both
authority: current
source: quenching-management
maintainer: quenching-management
updated: 2026-06-29
---

# `docs/` — canonical taxonomy

This is the canonical knowledge tree of the repository. Each **home** has a fixed
name and a unique purpose; the content inside each home follows Diátaxis (tutorial /
how-to / reference / explanation). Folder names in **English kebab-case** (stable
across repos); the **agent-facing content is English too** (only `audience: human`
material — `presentations/`, `communications/` — follows the project language).
Anyone moving between repos finds the **same** tree in the same place.

Open the `README.md` of each home to see what lives there and which subfolders exist.

| Home | Purpose | README |
| --- | --- | --- |
| `standards/` | current/active reference — OUR contracts/conventions | [standards/README.md](standards/README.md) |
| `decisions/` | ADR — open decision; when implemented, distill to `standards/` and remove | [decisions/README.md](decisions/README.md) |
| `vision/` | direction segmented by area, no deadline | [vision/README.md](vision/README.md) |
| `backlog/` | what is missing, by pillar | [backlog/README.md](backlog/README.md) |
| `guides/` | how-to + tutorials | [guides/README.md](guides/README.md) |
| `reference/` | EXTERNAL reference material (what we consume) | [reference/README.md](reference/README.md) |
| `catalog/` | data / domain catalog — `system/catalog/schema/table`, detailed × consolidated, access + scripts | [catalog/README.md](catalog/README.md) |
| `communications/` | directed communication (outbound) — message to an audience; template per channel | [communications/README.md](communications/README.md) |
| `presentations/` | human deliverables (via sidecar) | [presentations/README.md](presentations/README.md) |

## Boundaries (memorable summary)

- `standards/` = "how **WE** do it (current/active)".
- `reference/` = "facts about what **WE CONSUME** (external, background)".
- `catalog/` = "our **data** / domain".
- `communications/` = "**messages we send to an audience**" (directed,
  dated; one template per channel in [communications/templates/](communications/templates/README.md)).
- `presentations/` = "our **visual** deliverables" (the LLM reads the sidecar `.md`,
  never the binary — mold applied by the `quenching-docs` skill).
- `decisions/` → `standards/` when implemented (distill and remove).
- `patterns` **is not a silo** — dissolves into `standards/architecture/`.

> _Skeleton installed by `quenching-management`. The complete specification
> of the tree (purpose / Diátaxis / audience / authority / boundary per home +
> migration doctrine for variants) lives in
> `references/docs-taxonomy.md` of the method._
