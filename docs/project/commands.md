---
type: project
title: Command catalog
description: The complete command catalog by front — one line each — plus the cq rail's exit-code contract.
resource: quenching/README.md
tags:
  - reference
  - commands
timestamp: 2026-10-29
audience: both
authority: current
source: quenching/README.md §The 61 commands (long rows condensed); command set held in lockstep by test_commands_catalog.py
maintainer: Israel Holetz
---

# Command catalog

All commands, grouped by the front (or pillar) that owns them. Typing a command is
the explicit entry point; Claude also auto-routes to one by its `description`. This page is
derived from the product manual, whose tables a test holds in lockstep with the real surface —
`cq components doctor --json` is the machine authority on the count.

## The cq rail

Every command drives the bundled stdlib CLI rather than touching providers or files ad hoc:

```bash
cq knowledge …   # the OKF bundle: validate, project, …
cq design …      # the DTCG source: build, import, render, …
cq specs …       # the provider-owned specs front
cq components …  # the .claude/ surface: doctor, lint, registry, translate
cq proof …       # the target-declared verification surface: inventory, doctor, status, ratchet
cq git …         # the git pillar's deterministic queries
cq deploy …      # install the surface in a target repository (top-level, not a front)
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
| `/quenching-knowledge` | The single entry point of the knowledge flows: picks one of the thirteen flows (add, align, define, learn, import, import-memory, glossary-backfill, status, documentation build, plan, produce, review, write) by the flow you name and loads that flow's reference; each typed shortcut stays. |
| `/quenching-knowledge align` | Forces `/docs/` into the canonical OKF bundle and pulls in out-of-band content — probe first, ONE confirmed plan, looped to a fixpoint. |
| `/quenching-knowledge status` | The front's only **read-only** view: where the bundle stands, what drifted. Writes nothing. |
| `/quenching-knowledge add` | Inserts ONE concept doc — right home, right type, honest stamp. |
| `/quenching-knowledge learn` | Captures ONE piece of generic understanding into `concepts/`. |
| `/quenching-knowledge define` | Adds or refines ONE entry in the fixed glossary. |
| `/quenching-knowledge glossary-backfill` | Sweeps the whole bundle for terms nobody defined, and backfills them. |
| `/quenching-knowledge import` | Imports an external source — files, folders, URLs — into the bundle as many docs, with provenance. |
| `/quenching-knowledge import-memory` | Drains the project's Claude Code memory into the bundle, then clears it. |
| `/quenching-knowledge documentation-produce` | Conducts the whole documentation pipeline: site layer, sourced pages, bounded review, strict-build QA. |
| `/quenching-knowledge documentation-plan` | Builds the sourced architecture — reader journeys and the output contracts each page answers to. |
| `/quenching-knowledge documentation-write` | Writes the Diátaxis pages from that plan, sourced and never invented. |
| `/quenching-knowledge documentation-review` | Scores pages against the quality gate **without changing a byte**. |
| `/quenching-knowledge documentation-build` | Owns the Zensical site layer — extensions, CSS, nav, and the strict build. |

## The specs front

Acts on specs stored on the `quenching` branch, with GitHub or Azure Boards cards. The lifecycle these
commands share is explained in [The spec lifecycle](../documentation/spec-lifecycle.md).

| Command | Does |
| --- | --- |
| `/quenching-specs` | The single entry point of the specs flows: picks `create`, `develop`, `execute`, `conclude`, `triage`, `status` or `orchestrate` by the flow you name or the spec's stage, and loads that flow's reference. The seven typed commands stay as thin shortcuts. |
| `/quenching-specs status` | The front's only **read-only** view: specs by derived stage, the records as history, verifier and provider findings. |
| `/quenching-specs create` | ONE spec, ONE call, ONE closing screen — a sentence becomes `## Problem` and `summary:`; a plan file becomes every section it actually supports. |
| `/quenching-specs develop` | Compose + refine in one pass: takes the spec to a closed ready set, argues with it, ends at the approval close. Records `refined:`; never edits code. |
| `/quenching-specs execute` | Builds `## Tasks` one verified commit at a time — clean tree, inline worktree cut from the base, `verify:` under the spec's policy, code and tick in ONE commit. |
| `/quenching-specs conclude` | Closes a spec out, **merging last**: branch review, emergent `/docs/`, archive (`outcome:`), distillation, `merge:` stamp — then the merge, and nothing after it. |
| `/quenching-specs improve` | Typed only. Maps relevant improvement opportunities with evidence, settles the owner's decisions, and turns the approved plan into an epic of member specs. |
| `/quenching-specs orchestrate` | Launches the `orchestrator` agent over an epic or a list of specs: waves, at most 3 workers, accepted only on a verifier PASS. |
| `/quenching-specs autopilot` | Typed only. Unattended improvement — triage, map, epic, orchestrate `autonomous`, correctness review (Claude plus Codex when the quota allows), gate. Runs ONE round by default; `--until-dry` or `--until` repeat rounds (each resumable from a round record, the next in a fresh context), and `--max-launches` (provisional 40) caps the launches of the whole tree. Never forces a widening decision. |
| `/quenching-specs triage` | Ranks the whole front in ONE confirmed table, writing `priority:` per spec and nothing else — merging, never clobbering a human's ranking. |
| `/quenching-specs board` | Human-only launcher for the local spec portal (`cq specs serve`): board, ranking, detail, search, capture and approve in the browser, over the same backend; its contract is [specs-portal.md](../standards/architecture/specs-portal.md). |

## The design front

Acts on the `/.design/` DTCG source and its generated interoperability, editorial, and internal
adapter artifacts.

| Command | Does |
| --- | --- |
| `/quenching-design` | The single entry point of the design flows: picks `align`, `status`, `genre-new` by the flow you name or by the words of the request. |
| `/quenching-design align` | Installs or converges the brand pack, arbitrates external DESIGN.md proposals, and rebuilds every projection. |
| `/quenching-design status` | Reports source validity, generated identity, sidecar/assets, genres, adapters, and optional Impeccable detector state without writing. |
| `/quenching-design genre-new` | Mints ONE editorial genre contract with fields, register, and HTML/Typst/PDF destinations. |

`cq design build` is deterministic and byte-checked; `cq design import` is the explicit route for
folding an Impeccable proposal back into the source. The portable DESIGN.md boundary is lossy by
design, so rich motion, shadows, breakpoints, and snippets remain in DTCG/sidecar data.

## The components front

Acts on the target repository's `.claude/` automation surface.

| Command | Does |
| --- | --- |
| `/quenching-components` | The single entry point of the components flows: picks `command-new`, `agent-new`, `hook-new`, `align`, `status` or `harness-align` by the flow you name and loads that flow's reference; each typed shortcut stays. |
| `/quenching-components align` | Converges `.claude/` onto one file per entry point, audits every body against the writing doctrine, rewrites every description. |
| `/quenching-components status` | Reports command count, fronts and finding codes for the target automation surface without writing. |
| `/quenching-components command-new` | Mints or edits ONE command — the structural half, including its `description`. |
| `/quenching-components command-eval` | Measures whether a command actually teaches anything: with/without runs, graded on evidence. |
| `/quenching-components command-retro` | Mines ONE session for what it evidences about ONE command that ran in it — cost, redundancy, bugs. |
| `/quenching-components agent-new` | Mints or edits ONE subagent definition, scoping tools to the narrowest set and pricing its always-on cost. |
| `/quenching-components hook-new` | Wires ONE scoped hook — narrowest scope, cheapest handler. Warns by default; blocks only on the human's word. |
| `/quenching-components harness-align` | Refactors `AGENTS.md` into a thin pointer over the bundle, so doctrine lives once; legacy `CLAUDE.md` is removed. |

## The ops front

Acts on the target repository's declared operations root and canonical router.

| Command | Does |
| --- | --- |
| `/quenching-ops` | The single entry point of the ops flows: picks `align`, `status`, `entrypoint-new` by the flow you name or by the words of the request. |
| `/quenching-ops align` | Probes the operations surface, applies mechanical and structural drift under one plan, and reports judgement findings without driving them. |
| `/quenching-ops status` | Reports root, router, packages, lifecycle, findings by band, and registry freshness without writing. |
| `/quenching-ops entrypoint-new` | Mints ONE Python entry point from the contract, registers it in the declared router, and regenerates the operations registry. |

## The proof front

Acts on the target repository's declared verification surface.

| Command | Does |
| --- | --- |
| `/quenching-proof` | The single entry point of the proof flows: picks `align`, `status`, `layer-new` by the flow you name or by the words of the request. |
| `/quenching-proof align` | Probes the proof gate, applies bounded repairs under one plan, defers an unsafe floor write, and reports judgement findings without driving them. |
| `/quenching-proof status` | Reports layers, fixtures, measured roots, floors, CI evidence, and findings by band without writing; it states that the suite was not run. |
| `/quenching-proof layer-new` | Mints one named layer with its marker, reach, budget, fixture home and collection rule, then proposes test moves for a separate confirmation. |

## The toolchain front

Acts on the target repository's manifests, locks, language pins and tool configuration.

| Command | Does |
| --- | --- |
| `/quenching-toolchain` | The single entry point of the toolchain flows: picks `align`, `status` by the flow you name or by the words of the request. |
| `/quenching-toolchain align` | Probes applicability, inventories the target's toolchain artifacts, applies only mechanical and bounded structural repairs, and reports target-owned build policy. |
| `/quenching-toolchain status` | Reports applicability, manifests, locks, language pins, tool configuration and `tc-*` findings without writing. |

## The delivery front

Acts on the target repository's provider-equivalent workflows and release shape.

| Command | Does |
| --- | --- |
| `/quenching-delivery` | The single entry point of the delivery flows: picks `align`, `status` by the flow you name or by the words of the request. |
| `/quenching-delivery align` | Probes provider-equivalent workflows, applies bounded pipeline-shape repairs under one plan, and reports provider and release policy without choosing it. |
| `/quenching-delivery status` | Reports applicability, workflow inventory, reachability, provenance and `delivery-*` findings without writing or running a pipeline. |

## The opensource front

Acts on the target repository's license, community and governance artifacts, and aggregates every
owner's open source catalog answers.

| Command | Does |
| --- | --- |
| `/quenching-opensource` | The single entry point of the opensource flows: picks `align`, `status`, `readiness` by the flow you name or by the words of the request. |
| `/quenching-opensource align` | Plans the license, community and governance artifacts on one OK and writes each from a pinned template through `cq opensource apply`, never choosing the owner's answers. |
| `/quenching-opensource status` | Reports every owner's catalog answers, the baseline level reached and `os-*` findings without writing. |
| `/quenching-opensource readiness` | Assesses tree and history before publication and reports blockers, warnings and unmeasured coverage, read-only; never approves publication. |

## The security pillar

Answers read-only repository security questions; it converges no tree and carries no align.

| Command | Does |
| --- | --- |
| `/quenching-security` | The single entry point of the security flows: picks `status` by the flow you name or by the words of the request. |
| `/quenching-security status` | Reports workflow permissions, secret and ignore coverage, advisory dependency configuration and access ownership without writing repository values. |

## The git pillar

Answers questions about the repository's own git state; converges no tree, so it carries no
align. The specs front hands off to it rather than executing git itself.

| Command | Does |
| --- | --- |
| `/quenching-git` | The single entry point of the git flows: picks `branch`, `commit`, `merge`, `sync`, `pr-create`, `pr-review` or `pr-status` by the flow you name and loads that flow's reference; each typed shortcut stays. |
| `/quenching-git branch` | Takes isolation for a build: a worktree by default and unasked, a plain branch only when the human asks, stating the cost and stamping the `branch:` record. |
| `/quenching-git commit` | Commits what is already staged, under the target's own convention when one is declared. Never `git add -A`. |
| `/quenching-git commit-incremental` | Turns the current worktree's pending changes into cohesive commits with explicit paths and safe stop conditions. |
| `/quenching-git push` | Publishes one branch to an exact remote and refspec after measuring preconditions and receiving confirmation, without force or PR side effects. |
| `/quenching-git revert` | Creates a compensating commit for one known target after showing its effect and requiring an explicit mainline for merges, without rewriting history. |
| `/quenching-git pr-create` | Pushes and opens a pull request, reporting plainly whether a `Closes #<n>` keyword will actually close its issue. |
| `/quenching-git pr-status` | Reports one read-only snapshot of a pull request's provider state, checks, reviews, threads and mergeability, preserving unknown causes. |
| `/quenching-git merge` | Merges a branch home on one of four strategies — offered, never chosen for the human. |
| `/quenching-git sync` | Rebases a work branch onto the latest base, with `--update-refs` so a stacked branch is not orphaned. |
| `/quenching-git cleanup` | Prunes branches merged or gone and worktrees git registers with no directory on disk — nothing the human did not pick. |
| `/quenching-git pr-review` | Works through a PR's unresolved review threads, one confirmation per thread. |

## The root commands

| Command | Does |
| --- | --- |
| `/quenching-align` | The one align spanning the eight local fronts on ONE confirmation — conducting each front's own align, never reimplementing any. |
| `/quenching-handoff` | Compacts the current conversation into a handoff stored on the `quenching` branch, and closes with the next session's opening prompt. |

**Next:** this repository's own local automation surface (four development commands) is the
[automation registry](automation.md); every term used above resolves in the
[glossary](../glossary.md).
