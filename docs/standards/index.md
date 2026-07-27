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
### architecture/

| Doc | Covers |
| --- | --- |
| [align-surface.md](architecture/align-surface.md) | The 1×4 align column that replaced the 2×4 matrix — one align per front carrying its content stages, and the probe-before-inventory rule that makes a no-op align cost a couple of tool calls |
| [plugin-layout.md](architecture/plugin-layout.md) | commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path |

### automation/

| Doc | Covers |
| --- | --- |
| [context-budget.md](automation/context-budget.md) | What a command surface costs before anything fires — the two description caps, what the description may carry, and the per-surface ceiling |
| [skill-evaluation.md](automation/skill-evaluation.md) | What it takes to claim a skill works — with/without runs in isolated agents, assertions graded on quoted evidence, and a reported delta |
| [skills.md](automation/skills.md) | How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point |

### naming/

| Doc | Covers |
| --- | --- |
| [command-surface.md](naming/command-surface.md) | How the plugin's commands are named and namespaced — one file per entry point, where the path is the identity |

### quality/

| Doc | Covers |
| --- | --- |
| [bundle-verification.md](quality/bundle-verification.md) | What the docs/ front machine-checks versus what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check, and the resource glob-set format |
| [surface-verification.md](quality/surface-verification.md) | How a change to the command surface is proven — a fresh process because the registry is built at session start, assertions on captured tool_use rather than prose, and the three preconditions a functional check must satisfy to measure what it claims |

### workflows/

| Doc | Covers |
| --- | --- |
| [plan-artifacts.md](workflows/plan-artifacts.md) | The one-file spec, its thirteen canonical sections, the phase gates and the phase-scoped explicit-none rule, promote-as-the-human-OK, and how to read a v1 plan in specs/archive/ |
| [plan-git-record.md](workflows/plan-git-record.md) | How a plan's work is recorded in git — the per-task commit field, the branch and merge frontmatter records, the squash caveat, and the read-if-present contract for a target's own docs/standards/git/ |
| [plan-lifecycle.md](workflows/plan-lifecycle.md) | The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, and the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else |
| [task-execution.md](workflows/task-execution.md) | How a spec's task is executed — the verification policies, the failure budget, commit-per-task, the two-level review split, and the delegation and [P] disjunction rules |
<!-- END GENERATED -->
