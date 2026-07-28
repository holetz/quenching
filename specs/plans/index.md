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
**22 specs** · 2 executing · 1 designed · 19 captured

### Executing

| Spec | Title | Since |
| --- | --- | --- |
| [docs-verification-layer](2026-07-25-docs-verification-layer.md) | Verification layer for the docs/ front | 2026-07-25 |
| [move-conclude-merge-last](2026-07-28-move-conclude-merge-last.md) | Make the merge the last action of /specs:conclude | 2026-07-28 |

### Designed

| Spec | Title | Since |
| --- | --- | --- |
| [restructure-claude-front-namespace](2026-07-27-restructure-claude-front-namespace.md) | Rename the /skill namespace to /automation and split it into artifact contexts | 2026-07-27 |

### Captured

| Spec | Title | Since |
| --- | --- | --- |
| [add-import-provenance](2026-07-25-add-import-provenance.md) | Add provenance and idempotent re-ingestion to quenching-docs-import | 2026-07-25 |
| [decide-agents-md-harness-default](2026-07-25-decide-agents-md-harness-default.md) | Decide whether AGENTS.md becomes the default harness target | 2026-07-25 |
| [decide-plan-quick-skill](2026-07-25-decide-plan-quick-skill.md) | Decide whether quenching-specs-plan-quick is still needed | 2026-07-25 |
| [decide-sp-unrefined-severity](2026-07-25-decide-sp-unrefined-severity.md) | Decide whether sp-unrefined should escalate to error | 2026-07-25 |
| [expose-finding-advisory-as-data](2026-07-25-expose-finding-advisory-as-data.md) | Expose a finding's advisory/blocking status as data in okf-validate --json | 2026-07-25 |
| [split-specs-py-backlog-renderer](2026-07-25-split-specs-py-backlog-renderer.md) | Split the backlog-zone renderer out of specs.py | 2026-07-25 |
| [verify-allowed-tools-enforcement](2026-07-26-verify-allowed-tools-enforcement.md) | Verify Allowed Tools Enforcement | 2026-07-26 |
| [add-specs-py-record-writer](2026-07-27-add-specs-py-record-writer.md) | Give the frontmatter records a mechanical writer in specs.py | 2026-07-27 |
| [dedupe-specs-py-spec-reader](2026-07-27-dedupe-specs-py-spec-reader.md) | Fold the four copies of read-parse-derive in specs.py into one helper | 2026-07-27 |
| [fix-skills-py-description-truncation](2026-07-27-fix-skills-py-description-truncation.md) | skills.py silently truncates a description at the first ' | 2026-07-27 |
| [isolate-functional-checks-probes](2026-07-27-isolate-functional-checks-probes.md) | functional-checks.sh check 3 creates real specs in the repo it probes | 2026-07-27 |
| [name-the-scaffolded-stage](2026-07-27-name-the-scaffolded-stage.md) | Decide whether a spec with an unwritten Problem gets a named stage | 2026-07-27 |
| [retire-skill-vocabulary](2026-07-27-retire-skill-vocabulary.md) | Retire the skill vocabulary left behind by the collapse | 2026-07-27 |
| [rewrite-readme-for-collapsed-surface](2026-07-27-rewrite-readme-for-collapsed-surface.md) | Rewrite README.md for the collapsed command surface | 2026-07-27 |
| [improve-command-from-session](2026-07-28-improve-command-from-session.md) | Mine a session for improvements to the command that started it | 2026-07-28 |
| [make-sk-unscoped-bash-read-the-body](2026-07-28-make-sk-unscoped-bash-read-the-body.md) | sk-unscoped-bash cannot read the body its own remedy points at | 2026-07-28 |
| [notice-installed-tool-version-drift](2026-07-28-notice-installed-tool-version-drift.md) | Nothing notices an installed tool copy falling behind the plugin | 2026-07-28 |
| [probe-a-frontmatter-hook-firing](2026-07-28-probe-a-frontmatter-hook-firing.md) | No probe observes a frontmatter hooks: block actually fire | 2026-07-28 |
| [restore-routing-info-on-docs-commands](2026-07-28-restore-routing-info-on-docs-commands.md) | Restore trigger phrases and boundaries on the nine bare /docs:* descriptions | 2026-07-28 |
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
