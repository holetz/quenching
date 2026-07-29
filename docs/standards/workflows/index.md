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
| [plan-artifacts.md](plan-artifacts.md) | The one-file spec, its thirteen canonical sections, the phase-scoped explicit-none rule, the parsed `## Impact` sub-heading, the duplicated template, and how to read a v1 plan in `specs/archive/` |
| [plan-git-record.md](plan-git-record.md) | How a plan's work is recorded in git — the per-task commit field, the branch and merge frontmatter records, the squash caveat, and the read-if-present contract for a target's own docs/standards/git/ |
| [plan-lifecycle.md](plan-lifecycle.md) | The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, and the append-only archive rule for facts that did not exist at the move |
| [task-execution.md](task-execution.md) | How a spec's task is executed — the verification policies, the failure budget, commit-per-task, the two-level review split and the commands that own each level, and the delegation + `[P]` disjunction rules |

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`job-framework` · `task-parameters` · `scheduling` · `orchestration`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- _(none yet — fill on population)_
