---
type: project
title: Command catalog
description: All thirty-eight commands by front — one line each — plus the cq rail's exit-code contract.
resource: plugins/quenching/README.md
tags:
  - reference
  - commands
timestamp: 2026-08-28
audience: both
authority: current
source: derived from plugins/quenching/README.md §The thirty-eight commands and §The specs flow (tables preserved, long rows condensed); the machine authority is cq components doctor --json
maintainer: Israel Holetz
---

# Command catalog

All thirty-eight commands, grouped by the front (or pillar) that owns them. Typing a command is
the explicit entry point; Claude also auto-routes to one by its `description`. This page is
derived from the product manual, whose tables a test holds in lockstep with the real surface —
`cq components doctor --json` is the machine authority on the count.

## The cq rail

Every command drives the bundled stdlib CLI rather than touching providers or files ad hoc:

```bash
cq knowledge …   # the OKF bundle: validate, project, …
cq specs …       # the provider-owned specs front
cq components …  # the .claude/ surface: doctor, lint, registry, translate
cq git …         # the git pillar's deterministic queries
```

| Exit code | Meaning |
| --- | --- |
| `0` | ok — nothing to report |
| `1` | findings — named, file-level, actionable |
| `2` | refusal — a precondition failed; nothing was attempted |

All listing commands accept `--json`. The tool resolves per call: bare `cq` on the session
PATH, or `<plugin>/assets/bin/cq` spelled out — the same file either way.

## The knowledge front

Acts on the `/docs/` OKF bundle.

| Command | Does |
| --- | --- |
| `/quenching:knowledge:align` | Forces `/docs/` into the canonical OKF bundle and pulls in out-of-band content — probe first, ONE confirmed plan, looped to a fixpoint. |
| `/quenching:knowledge:status` | The front's only **read-only** view: where the bundle stands, what drifted. Writes nothing. |
| `/quenching:knowledge:add` | Inserts ONE concept doc — right home, right type, honest stamp. |
| `/quenching:knowledge:learn` | Captures ONE piece of generic understanding into `concepts/`. |
| `/quenching:knowledge:define` | Adds or refines ONE entry in the fixed glossary. |
| `/quenching:knowledge:glossary-backfill` | Sweeps the whole bundle for terms nobody defined, and backfills them. |
| `/quenching:knowledge:import` | Imports an external source — files, folders, URLs — into the bundle as many docs, with provenance. |
| `/quenching:knowledge:import-memory` | Drains the project's Claude Code memory into the bundle, then clears it. |
| `/quenching:knowledge:documentation:produce` | Conducts the whole documentation pipeline: site layer, sourced pages, bounded review, strict-build QA. |
| `/quenching:knowledge:documentation:plan` | Builds the sourced architecture — reader journeys and the output contracts each page answers to. |
| `/quenching:knowledge:documentation:write` | Writes the Diátaxis pages from that plan, sourced and never invented. |
| `/quenching:knowledge:documentation:review` | Scores pages against the quality gate **without changing a byte**. |
| `/quenching:knowledge:documentation:build` | Owns the Zensical site layer — extensions, CSS, nav, and the strict build. |

## The specs front

Acts on provider-owned specs — GitHub issues or Azure Boards work items. The lifecycle these
commands share is explained in [The spec lifecycle](../explanation/spec-lifecycle.md).

| Command | Does |
| --- | --- |
| `/quenching:specs:status` | The front's only **read-only** view: specs by derived stage, the records as history, verifier and provider findings. |
| `/quenching:specs:create` | ONE spec, ONE call, ONE closing screen — a sentence becomes `## Problem` and `summary:`; a plan file becomes every section it actually supports. |
| `/quenching:specs:develop` | Compose + refine in one pass: takes the spec to a closed ready set, argues with it, ends at the approval close. Records `refined:`; never edits code. |
| `/quenching:specs:execute` | Builds `## Tasks` one verified commit at a time — clean tree, inline isolation offer, `verify:` under the spec's policy, code and tick in ONE commit. |
| `/quenching:specs:conclude` | Closes a spec out, **merging last**: branch review, emergent `/docs/`, archive (`outcome:`), distillation, `merge:` stamp — then the merge, and nothing after it. |
| `/quenching:specs:triage` | Ranks the whole front in ONE confirmed table, writing `priority:` per spec and nothing else — merging, never clobbering a human's ranking. |
| `/quenching:specs:cycle` | The cycle conductor over ONE spec — capture, define, build, close — two halves authorized separately, writing nothing itself. |
| `/quenching:specs:execute-queue` | Builds N specs as a **serial queue over a single isolation**: isolate once, execute N times, one conclude closing the lot. |
| `/quenching:specs:develop-batch` | Takes N specs toward `ready` as a **parallel batch** — safe because defining writes no code; approvals stay with the conductor. |

## The components front

Acts on the target repository's `.claude/` automation surface.

| Command | Does |
| --- | --- |
| `/quenching:components:align` | Converges `.claude/` onto one file per entry point, audits every body against the writing doctrine, rewrites every description. |
| `/quenching:components:command:new` | Mints or edits ONE command — the structural half, including its `description`. |
| `/quenching:components:command:eval` | Measures whether a command actually teaches anything: with/without runs, graded on evidence. |
| `/quenching:components:command:retro` | Mines ONE session for what it evidences about ONE command that ran in it — cost, redundancy, bugs. |
| `/quenching:components:agent:new` | Mints or edits ONE subagent definition, scoping tools to the narrowest set and pricing its always-on cost. |
| `/quenching:components:hook:new` | Wires ONE scoped hook — narrowest scope, cheapest handler. Warns by default; blocks only on the human's word. |
| `/quenching:components:harness:align` | Refactors `CLAUDE.md`/`AGENTS.md` into thin pointers over the bundle, so doctrine lives once. |

## The git pillar

Answers questions about the repository's own git state; converges no tree, so it carries no
align. The specs front hands off to it rather than executing git itself.

| Command | Does |
| --- | --- |
| `/quenching:git:branch` | Takes isolation for a build — worktree, branch, or in place — stating the cost and stamping the `branch:` record. |
| `/quenching:git:commit` | Commits what is already staged, under the target's own convention when one is declared. Never `git add -A`. |
| `/quenching:git:pr:create` | Pushes and opens a pull request, reporting plainly whether a `Closes #<n>` keyword will actually close its issue. |
| `/quenching:git:merge` | Merges a branch home on one of four strategies — offered, never chosen for the human. |
| `/quenching:git:sync` | Rebases a work branch onto the latest base, with `--update-refs` so a stacked branch is not orphaned. |
| `/quenching:git:cleanup` | Prunes branches merged or gone and worktrees git registers with no directory on disk — nothing the human did not pick. |
| `/quenching:git:pr:review` | Works through a PR's unresolved review threads, one confirmation per thread. |

## The root commands

| Command | Does |
| --- | --- |
| `/quenching:align` | The one align spanning the three fronts on ONE confirmation — conducting each front's own align, never reimplementing any. |
| `/quenching:handoff` | Compacts the current conversation into a handoff document a fresh session can continue from. |

**Next:** this repository's own local automation surface (four development commands) is the
[automation registry](automation.md); every term used above resolves in the
[glossary](../glossary.md).
