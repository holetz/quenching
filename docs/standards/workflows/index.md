# `standards/workflows/`

The job/task/schema framework — how work is defined, its parameters, scheduling, and
orchestration. In this repo the unit of work is a **plan** under `specs/`, so the standards here
govern what a plan's artifacts must contain and how its tasks are executed.

**Boundary:** the *framework that runs the work*; the *build/deploy* of that code lives in
[../ci-cd/](../ci-cd/index.md). One standard per file (files, not sub-folders); each
carries `type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

| Doc | Covers |
| --- | --- |
| [plan-artifacts.md](plan-artifacts.md) | The required sections of a plan's artifacts, the parsed `## Impact` declaration, the refinement record, and what `applyReady` does and does not guarantee |
| [task-execution.md](task-execution.md) | How a plan's task is executed — verification policies, the failure budget, commit-per-task, the two-level review split, and the delegation + `[P]` disjunction rules |

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`job-framework` · `task-parameters` · `scheduling` · `orchestration`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- _(none yet — fill on population)_
