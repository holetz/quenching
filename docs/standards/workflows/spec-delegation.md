---
type: standard
title: Spec delegation contract
description: How an approved spec is delivered to the GitHub Copilot cloud agent — the facts the delegation requires (`approved`, `branch:`, the `github` project, a GitHub provider and the branch on `origin`), the briefing that carries the protocol and never the spec's body, the spec branch as the pull request's base, the setup workflow on the default branch, the `REVIEW.md` seed, and the records the delegation never writes
resource: quenching/assets/bin/quenching/specs/commands/delegate.py, quenching/assets/bin/quenching/specs/commands/cli.py, quenching/assets/bin/quenching/deploy/tree.py, quenching/assets/bin/quenching/deploy/translate.py, quenching/references/specs-develop/specs-surface.md, quenching/references/align/tool-resolution.md
tags: [workflows, specs, delegation, copilot, branch, records]
timestamp: 2026-11-25
audience: both
authority: current
source: spec 464 (epic 453, S12); GitHub Docs pages for the Copilot cloud agent environment, custom agents, the GitHub CLI `agent-task` preview and code-review custom instructions, retrieved 2026-11-25
maintainer: quenching
---

# Spec delegation contract

<!-- rules -->

A spec can be built by the GitHub Copilot cloud agent when a human delegates it. The delegation
is a **command**, not a second orchestrator: it reads the store, refuses before any remote write
when a fact the cloud session depends on is missing, and hands the client one deterministic
briefing. It never copies the spec, never invents a branch and never writes a record.

## The delegation requires five facts

`cq specs delegate <id>` refuses — exit 2, nothing sent — unless all five hold:

| Fact | Why the session depends on it | Refusal |
| --- | --- | --- |
| the spec is `approved` | the human's go-ahead is what a build needs; a delegated build is still a build | `sp-delegate-approved` |
| the spec carries `branch: {base, work}` | `branch.work` is the pull request's base and the integration branch; the delegation does not derive a name from a title | `sp-delegate-branch` |
| the repository declares `shared.projections: ["github"]` | the setup workflow and the projected runner agent are the environment; without them the cloud session has no `cq` runtime | `sp-delegate-projection` |
| the provider is GitHub | `gh agent-task` is the invocation; another provider is another route, not a fallback | `sp-delegate-provider` |
| the branch is on `origin` | `--base` needs a ref the cloud host can resolve; a local-only branch would open the PR against nothing | `sp-delegate-remote` |

The projected custom agent (`quenching-spec-runner`, or `--custom-agent <name>`) must exist at
`.github/agents/<name>.agent.md`; `sp-delegate-agent` is the refusal, and a name that is not a flat
project-file slug refuses the same way. An unreadable configuration is `sp-delegate-config`.

## The briefing carries the protocol, not the spec

The task description is generated from the spec's identity and records, never from its section
bodies: the ID and title, the store branch and the `cq specs show <id> --full` command, the
`work` branch as the PR base, the count of open tasks, the one-task-one-commit rule, the subject
convention, the `cq specs task --check --subject --commit` tick, the `## Handoff` limit and the
fixed report. The spec stays on the `quenching` branch: a copy in the task description would be a
second truth that drifts, and the cloud agent can read the store through the same `cq`.

## The spec branch is the PR base, never the head

The cloud agent works on one branch of its own per task and opens one pull request. `--base` makes
that PR target `branch.work`; the head stays the client's. `branch.work` therefore remains the
integration branch and the spec's `branch:` record, and the delegation never rewrites it. The
agent's PR is not the spec's `pr:` record: `pr:` remains the PR of the spec branch into `base`,
written by `git:pr:create` or the conclude. The agent never merges, never concludes and never
archives; those stay the human's.

## The environment is generated, and the review is seeded

The `github` projection writes two artifacts the cloud session reads. The first is
`.github/workflows/copilot-setup-steps.yml`, generated from the target's own declarations: the
Python of `.python-version` or the `requires-python` of `pyproject.toml` (else the 3.11 floor),
`uv` when the deploy runtime is `uvx`, and `shared.worktreeSetup` verbatim. It has one job named
`copilot-setup-steps`, `contents: read`, and it must be on the **default branch** for the client to
run it — the spec branch that delegates inherits it from the base. The second is `REVIEW.md`, a
**seed** like `AGENTS.md`: created only when absent, never in the deploy manifest, never checked
for drift, and never removed with the key. It points the code review at
`/docs/standards/index.md` and `/docs/glossary.md`; the review policy is the repository's, so the
deploy writes the pointer once and the target edits the file. No `.github/copilot-instructions.md`
is generated: the root `AGENTS.md` is already the shared instruction and the code review reads it.

The client facts — the setup path and job name, the `REVIEW.md` reader, the `gh agent-task`
flags — are dated (GitHub Docs, 2026-11-25) and live in one place each: the workflow template, the
review seed and `delegate._gh_agent_task`. A client change is one line and one test, never a scan.

## The delegation writes no record

`cq specs delegate` writes nothing to the spec: not `branch:`, not `pr:`, not a new record. The
agent task is a fact of the git host until its pull request exists, and the records that describe
the spec's own branch stay with the commands that own them ([plan-git-record.md](plan-git-record.md)).
Re-running the command with `--send` creates another task; the operator owns that choice.

## Limits

- **GitHub only.** The route is `gh agent-task`; Azure Boards or another cloud agent is another
  spec, never a branch inside this verb.
- **The head branch is the client's.** The contract controls the base; nothing promises the
  cloud agent works directly on `plan/<id>-<handle>`.
- **The preview moves.** `gh agent-task create` is a preview command; the invocation is one
  function and its test pins it.
- **The live halves are measured after merge.** That the code review loads `REVIEW.md` and that
  the client honors `--base` are `unmeasured-live` in the spec that introduced them; a failure
  changes the surface, not the mechanism.

<!-- rationale -->

The alternative shapes lose on the epic's invariant. A `--harness copilot` mode would branch the
deploy by client name, which the owner rejected and the bench proves refused. Generating
`.github/copilot-instructions.md` would duplicate the `AGENTS.md` the client already reads. Putting
the spec's body in the task description would create a second register that drifts from the store.
Naming the branch from the title instead of the record would make the record a decoration. The
chosen shape keeps one source (the store), one branch contract (the record) and one client call
(a single function), and every refusal is a fact the session cannot work without.
