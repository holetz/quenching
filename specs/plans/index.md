# `plans/` — every spec that is not closed

Where a spec is **captured, proposed, designed, refined, approved and built** — its whole life
until it is closed out. A spec lands here in seconds as a raw problem and leaves, by a gated
`promote`, only when it is done or abandoned.

This is one of the two phase folders of the `specs/` tree, **outside** the `docs/` OKF bundle. Its
only sibling is `archive/` (done or abandoned).

**One spec is ONE file for its whole lifecycle.** There is no separate task inbox, no plan folder,
and no second folder to be promoted into: the thing you park and the thing you build are the same
file, enriched section by section and moved exactly once. That is why there is no Completed ledger
here — a finished spec is in `archive/`, told apart by its `outcome:` frontmatter, and
`git log --follow` is its history.

## Organization

```
plans/
  index.md                        # this listing (frontmatter-free, generated zone below)
  YYYY-MM-DD-<slug>.md            # one spec per file — flat, no subfolders
```

The date prefix is stamped **once, at capture**, and never rewritten — `promote` moves a file
without renaming it. So a plain `ls` is chronological, and *how long has this sat here?* is
answered by the listing itself rather than by a tool.

## Derived stages

A spec's stage is **computed from section completeness and frontmatter**, never declared — declared
state is forgotten on edit and goes stale, while derived state regresses on its own when a section
empties. The last rule that matches wins, so the list reads as a progression.

| Stage | Reached when |
| --- | --- |
| `captured` | only `## Problem` is filled |
| `proposed` | `## Proposal` is filled |
| `designed` | `## Design` is filled |
| `refined` | a `refined` record is in the frontmatter |
| `ready` | all ten gate sections are filled — the nine `## Problem` … `## Risks` plus `## Tasks` |
| `approved` | an `approved` record is in the frontmatter |
| `executing` | any task is `[x]` or `[!]`, or `## Handoff` is filled |

**`ready` is a floor, not a verdict, and nothing refuses on it.** An empty section counts as filled
when it carries an explicit `- none — <reason>`; a heading present with an empty body is malformed.

## Where the folder split went

Earlier versions had a `backlog/` folder for definition and a `ready/` folder for execution, and a
`promote` between them. That split bought exactly one fact no derivation can reproduce — **a human
said go** — at the cost of a second folder, a split listing, and a `promote` that refused often.

That one fact is now the `approved: {date}` record in frontmatter, and everything else the split
implied is derived by the table above. Building an unapproved spec does **not** refuse: the stamp is
asked for inline, because refusing would rebuild the gate the fold removed.

## Leaving this folder

`specs.py promote <slug> --to archive` moves a spec to `archive/` and stamps
`outcome: done | abandoned`. It **refuses (exit 2)** to archive as `done` while `- [ ]` boxes remain
— overridable with `--force`. `abandoned` is always allowed, because open tasks are exactly what
closing out unbuilt work looks like.

## What does NOT go here

- A finished or dropped spec (→ `archive/`, with `outcome:`).
- Settled direction with no deadline (→ `docs/vision/`).
- A durable rule the spec proved (→ `docs/standards/`, written as the spec runs).

## Current specs

<!-- BEGIN GENERATED: rebuilt from the spec files' headings and frontmatter by
     `specs.py plans reindex` — DO NOT edit by hand. Content, in order:
       **N specs** · X executing · Y approved · Z ready · … · W captured
       one table per DERIVED STAGE (most advanced first: Executing → Approved → Ready →
       Refined → Designed → Proposed → Captured, then Plans; empty groups omitted),
       columns `Spec | Title | Since` (Since = the filename's date prefix), rows
       OLDEST-FIRST within each group so stale specs surface.

     A spec appears under **Plans** when no stage rule matched at all — `## Problem` is
     still the scaffold comment `specs.py new` wrote. It is the phase name standing in for
     a stage, which is what "nobody has written anything yet" looks like.
-->
**33 specs** · 2 executing · 30 ready · 1 captured

### Executing

| Spec | Title | Since |
| --- | --- | --- |
| [declare-repo-body-language](2026-07-28-declare-repo-body-language.md) | Declare the repo's communication language and conduct in docs/standards so every command reads it for free | 2026-07-28 |
| [restore-routing-info-on-docs-commands](2026-07-28-restore-routing-info-on-docs-commands.md) | Restore trigger phrases and boundaries on the nine bare /docs:* descriptions | 2026-07-28 |

### Ready

| Spec | Title | Since |
| --- | --- | --- |
| [decide-agents-md-harness-default](2026-07-25-decide-agents-md-harness-default.md) | Decide whether AGENTS.md becomes the default harness target | 2026-07-25 |
| [decide-plan-quick-skill](2026-07-25-decide-plan-quick-skill.md) | Decide whether quenching-specs-plan-quick is still needed | 2026-07-25 |
| [decide-sp-unrefined-severity](2026-07-25-decide-sp-unrefined-severity.md) | Decide whether sp-unrefined should escalate to error | 2026-07-25 |
| [expose-finding-advisory-as-data](2026-07-25-expose-finding-advisory-as-data.md) | Expose a finding's advisory/blocking status as data in okf-validate --json | 2026-07-25 |
| [split-specs-py-backlog-renderer](2026-07-25-split-specs-py-backlog-renderer.md) | Split the backlog-zone renderer out of specs.py | 2026-07-25 |
| [add-specs-py-record-writer](2026-07-27-add-specs-py-record-writer.md) | Give the frontmatter records a mechanical writer in specs.py | 2026-07-27 |
| [dedupe-specs-py-spec-reader](2026-07-27-dedupe-specs-py-spec-reader.md) | Fold the four copies of read-parse-derive in specs.py into one helper | 2026-07-27 |
| [isolate-functional-checks-probes](2026-07-27-isolate-functional-checks-probes.md) | functional-checks.sh check 3 creates real specs in the repo it probes | 2026-07-27 |
| [name-the-scaffolded-stage](2026-07-27-name-the-scaffolded-stage.md) | Decide whether a spec with an unwritten Problem gets a named stage | 2026-07-27 |
| [restructure-claude-front-namespace](2026-07-27-restructure-claude-front-namespace.md) | Rename the /skill namespace to /automation and split it into artifact contexts | 2026-07-27 |
| [retire-skill-vocabulary](2026-07-27-retire-skill-vocabulary.md) | Retire the skill vocabulary left behind by the collapse | 2026-07-27 |
| [rewrite-readme-for-collapsed-surface](2026-07-27-rewrite-readme-for-collapsed-surface.md) | Rewrite README.md for the collapsed command surface | 2026-07-27 |
| [add-specs-cycle-run-modes](2026-07-28-add-specs-cycle-run-modes.md) | Add customizable run modes to the specs cycle commands | 2026-07-28 |
| [align-in-worktree-then-merge](2026-07-28-align-in-worktree-then-merge.md) | Have the align commands propose a worktree and merge at the end, as specs already does | 2026-07-28 |
| [check-the-lockstep-itself](2026-07-28-check-the-lockstep-itself.md) | Assert the seven-surface version lockstep in skills.py selftest | 2026-07-28 |
| [decide-plans-index-need](2026-07-28-decide-plans-index-need.md) | Reassess whether specs/plans/index.md is needed | 2026-07-28 |
| [fix-conclude-abandoned-branch-harvest](2026-07-28-fix-conclude-abandoned-branch-harvest.md) | conclude --outcome abandoned can harvest a note and delete it in the same run | 2026-07-28 |
| [make-sk-unscoped-bash-read-the-body](2026-07-28-make-sk-unscoped-bash-read-the-body.md) | sk-unscoped-bash cannot read the body its own remedy points at | 2026-07-28 |
| [plugin-dir-for-functional-checks](2026-07-28-plugin-dir-for-functional-checks.md) | Make functional-checks.sh witness which plugin copy it graded | 2026-07-28 |
| [probe-a-frontmatter-hook-firing](2026-07-28-probe-a-frontmatter-hook-firing.md) | No probe observes a frontmatter hooks: block actually fire | 2026-07-28 |
| [reduce-execute-conclude-cost](2026-07-28-reduce-execute-conclude-cost.md) | Re-evaluate /specs:execute and /specs:conclude runs for cost reduction | 2026-07-28 |
| [resolve-spec-from-worktree](2026-07-28-resolve-spec-from-worktree.md) | Resolve a spec from its own worktree before falling back to the current branch | 2026-07-28 |
| [revise-standards-subject-folders](2026-07-28-revise-standards-subject-folders.md) | Revise the fixed docs/standards subject folders | 2026-07-28 |
| [route-commands-without-always-on-descriptions](2026-07-28-route-commands-without-always-on-descriptions.md) | Route a 10x command surface without per-command always-on descriptions | 2026-07-28 |
| [stop-develop-offering-follow-up-specs](2026-07-28-stop-develop-offering-follow-up-specs.md) | /specs:develop should not offer to create a follow-up spec | 2026-07-28 |
| [upgrade-okf-to-v0-2](2026-07-28-upgrade-okf-to-v0-2.md) | Upgrade the OKF contract to v0.2 or later | 2026-07-28 |
| [commit-on-worktree-specs](2026-07-29-commit-on-worktree-specs.md) | Commit work at the end of develop, create and execute when a spec is already isolated in a worktree | 2026-07-29 |
| [narrow-the-stale-doc-trigger-to-content-drift](2026-07-29-narrow-the-stale-doc-trigger-to-content-drift.md) | Narrow stale-doc — retire the verdict, report resource activity as a figure | 2026-07-29 |
| [wire-the-overview-consumers](2026-07-29-wire-the-overview-consumers.md) | Wire the three consumers to read `## Overview` | 2026-07-29 |
| [correct-command-citation-form](2026-07-30-correct-command-citation-form.md) | Corrigir a forma de citação de comando — bare versus prefixada pelo plugin | 2026-07-30 |

### Captured

| Spec | Title | Since |
| --- | --- | --- |
| [cut-specs-execute-turns](2026-07-30-cut-specs-execute-turns.md) | Cut /specs:execute's turn count through body wording | 2026-07-30 |
<!-- END GENERATED -->

## Frontmatter

A spec file carries the lifecycle schema, **not** an OKF `type:` — it is not a concept doc, it
lives outside the bundle, and `specs.py validate` is what checks it:

```yaml
---
slug: <the identity key every command names>
title: <one line>
verification: per-task            # per-task | per-section | end-of-plan
priority: {level: 2, criticality: high, complexity: medium, date: 2026-07-25}
refined: {mode: premortem, date: 2026-07-25}
approved: {date: 2026-07-26}
branch: {base: main, work: plan/<slug>}
reviewed: {date: 2026-07-28}
merge: {strategy: squash, commit: abc1234}
---
```

Every optional record above is a **human judgment nothing else can answer** — that is the whole
admission test. There is no `created` field (the filename prefix is that fact), no `phase` field
(the folder is that fact), no `ready` field (the ten gate sections are that fact) and no attempt
counter. `okf-validate.py plans --listing-root` checks **this listing**; the spec files are
`specs.py validate`'s business.
