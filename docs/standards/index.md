# `standards/` — current/active reference, OUR contracts

The current/active **standard/contract** — "how it should be and why", versioned, the
shared source of truth. One standard per file; subfolder names by **subject**. Each
concept doc carries `type: standard` + a derived `resource:` (the repo scope it governs).

**Boundary:** `standards/` = "how **WE** do it (current/active)". Distinct from
[reference/](/docs/reference/index.md) (external facts we consume) and
[catalog/](/docs/catalog/index.md) (our data). Direction lives in
[vision/](/docs/vision/index.md). An **agreed-but-unproven** rule sits here as
`authority: background` and graduates to `current` once proven — there is no separate decisions
home.

Keep only the subtopics that apply to the repo; within each, break standards **one
concept per file** by considering the candidate sub-standards catalog (a
**consideration** checklist, evidence-gated generation, recorded deferral — not a blind
generate list). The **agent-facing pointer** for this home is [CLAUDE.md](CLAUDE.md)
(auto-loaded); the change history is [log.md](log.md).

## Subtopics

* [architecture/](architecture/index.md) — system structure + architectural patterns (patterns live here)
* [automation/](automation/index.md) — the Claude Code skill + command surface (classification, authoring, alignment)
* [code/](code/index.md) — code conventions, imports, lint, pins, SYMBOL naming
* [naming/](naming/index.md) — naming conventions (here: the command surface)
* [data-modeling/](data-modeling/index.md) — grain, key, joins, catalog/schema choice
* [ci-cd/](ci-cd/index.md) — build/deploy, "code defines YAML", manifest generation
* [workflows/](workflows/index.md) — job/task/schema framework, job parameters
* [mlops/](mlops/index.md) — model lifecycle, lineage, regulatory interface
* [quality/](quality/index.md) — data quality, drift/stability, model monitoring
* [platform/](platform/index.md) — deploy targets, permissions/governance, external services

## Current docs

<!-- BEGIN GENERATED: rebuilt from disk by `quenching-docs-align`/`quenching-docs-add` — DO NOT edit by hand.
     Scans standards/**/*.md, reads title/description/timestamp/type, grouped by subject subfolder.
     Row model per subfolder:
       ### code/
       | Doc | Covers |
       | --- | --- |
       | [imports.md](code/imports.md) | <the doc's description:> |
-->
### automation/

| Doc | Covers |
| --- | --- |
| [skills.md](automation/skills.md) | How the plugin's skills are classified, authored, named, mirrored as commands, and swept into conformance |

### naming/

| Doc | Covers |
| --- | --- |
| [command-surface.md](naming/command-surface.md) | How the plugin's skills and command wrappers are named, namespaced, and paired one-to-one |

### quality/

| Doc | Covers |
| --- | --- |
| [bundle-verification.md](quality/bundle-verification.md) | What the docs/ front machine-checks versus what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check, and the resource glob-set format |

### workflows/

| Doc | Covers |
| --- | --- |
| [plan-artifacts.md](workflows/plan-artifacts.md) | The required sections of a plan's artifacts, the parsed Impact declaration, the refinement record, and what applyReady does and does not guarantee |
| [task-execution.md](workflows/task-execution.md) | How a plan's task is executed — the verification policies, the failure budget, commit-per-task, the two-level review split, and the delegation and `[P]` disjunction rules |
<!-- END GENERATED -->
