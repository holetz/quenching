# `standards/workflows/`

The job/task/schema framework — how work is defined, its parameters, scheduling, and
orchestration. In this repo the unit of work is a **plan** under `/.specs/`, so the standards here
govern what a plan's artifacts must contain and how its tasks are executed.

**Boundary:** the *framework that runs the work*; the *build/deploy* of that code lives in
[../ci-cd/](../ci-cd/index.md). One standard per file (files, not sub-folders); each
carries `type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

| Doc | Covers |
| --- | --- |
| [plan-artifacts.md](plan-artifacts.md) | The one-file spec, its fourteen canonical sections, the phase-scoped explicit-none rule, the parsed Impact sub-heading, the duplicated template and the three-copy record vocabulary, and how to read a v1 plan in /.specs/archive/ |
| [plan-git-record.md](plan-git-record.md) | How a plan's work is recorded in git — the commit sha as the task→commit anchor where the spec no longer shares a branch with the code, the commit subject as the anchor a co-branching spec still needs, the branch and merge frontmatter records, why every record is written before the thing it describes, the squash caveat, the merge that runs via git -C in the base's own checkout and the worktree removed after it, and the read-if-present contract for a target's own /.docs/standards/git/ |
| [plan-lifecycle.md](plan-lifecycle.md) | The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, and the append-only archive rule for facts that did not exist at the move |
| [plugin-configuration.md](plugin-configuration.md) | `.claude/quenching.json` as the plugin's single configuration home — where it lives and why it left the specs workspace, the four recognised keys and their defaults, the one key that deliberately has none and refuses instead, why every other way it can be wrong is a field rather than an exception, and why a stranded `/.specs/config.json` is named instead of merged |
| [task-execution.md](task-execution.md) | How a spec's task is executed — the verification policies, the failure budget, commit-per-task, the two-level review split, and the delegation and [P] disjunction rules |
| [worktree-setup.md](worktree-setup.md) | The `worktreeSetup` hook — what it is for, where it is declared now that the plugin's config moved to `.claude/quenching.json`, what its absence means, who runs the declared command and with which cwd, why the consent is the isolation offer rather than a prompt of its own, and the record of why the specs front took a config file at all |

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`job-framework` · `task-parameters` · `scheduling` · `orchestration`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- _(none yet — fill on population)_
