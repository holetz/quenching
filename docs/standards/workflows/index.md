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
| [agent-choice-catalogues.md](agent-choice-catalogues.md) | The one shape `subjects`, `tagCatalog` and `workItemTypes` all share — an abstract key mapping to a human-facing description an agent reads to PROPOSE and a human CONFIRMS — why the three converged on it independently, the one invariant that shape enforces on every consumer, and why a fourth catalogue should reuse it rather than invent its own review mechanism |
| [plan-artifacts.md](plan-artifacts.md) | The one provider-owned spec document, its thirteen canonical sections, the phase-scoped explicit-none rule, the parsed Impact sub-heading, the duplicated template and the three-copy record vocabulary, and how to read a v1 plan in /.specs/archive/ |
| [plan-git-record.md](plan-git-record.md) | How a provider-owned spec records the git facts that cannot be derived later — per-task commit subjects, branch, pull request and merge records, branch marks for conclude discovery, base inference, merge routes, and safe branch cleanup |
| [plan-lifecycle.md](plan-lifecycle.md) | The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, `conclude` archiving before the merge and what `## Outcome` asserts because of it, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, `branch`/`pr`/`merge` split across `execute`-or-`git:branch`, `git:pr:create` and `git:merge` now that `conclude` writes neither of the last two, the append-only archive rule for facts that did not exist at the move — no longer all landing in the same run — and the moment a follow-up becomes a spec — definition parks it as a Discoveries line, close-out mints it |
| [plugin-configuration.md](plugin-configuration.md) | `.claude/quenching.json` is the plugin's single configuration home; provider selection is derived from the repository remote, while placement, Azure mappings, lifecycle hooks, profiles and proposal catalogues remain explicit target settings |
| [retiring-a-standard.md](retiring-a-standard.md) | How a bundle standard is retired — removal, never deprecation (the verb is `git rm`; a doc that survives annotated becomes a ritual nobody acts on); the inheriting doc carries the `retired with <doc> (<spec>, <data>)` stamp in its `source:` and in its body; the citation sweep is human and `## Impact` must name the class of docs that cite it; the listing's GENERATED zone is rebuilt in the same movement; and the branch review is the net — with resource activity read as a figure, never as a failure |
| [task-execution.md](task-execution.md) | How a spec's task is executed — the verification policies, `verify:` scoped at authoring, the three causes of a check that can never pass (one of them invisible to the falsification run), `files:` naming the derived artifacts an edit invalidates, the failure budget, one commit per task retained across section boundaries, the two-level review split, the four-event Handoff refresh cadence, and the delegation and [P] disjunction rules |
| [worktree-setup.md](worktree-setup.md) | The `worktreeSetup` hook prepares a code-isolation worktree from `.claude/quenching.json`; its absence is normal, the execute offer displays and authorizes the command, and provider-owned specs never use this hook as persistent storage |

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`job-framework` · `task-parameters` · `scheduling` · `orchestration`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- _(none yet — fill on population)_
