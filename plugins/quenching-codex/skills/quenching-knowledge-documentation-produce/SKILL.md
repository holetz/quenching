---
name: quenching-knowledge-documentation-produce
description: "Conduct the complete documentation pipeline from site setup through sourced pages, bounded editorial review and strict build QA. Triggers on \"produce the documentation\", \"run the documentation pipeline\", or \"generate the complete docs site\"."
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/documentation/produce.md -->


# quenching-knowledge-documentation-produce — conduct the documentation pipeline

**Input**: `$ARGUMENTS` (optional source scope and `--desde <git-ref>`; omit both to run the complete
target-repository pipeline).

This conductor coordinates the four sibling stages through the `Skill` tool and owns no writes.
The shared contracts are in
[knowledge-documentation/quality.md](../../references/knowledge-documentation/quality.md)
and the cycle authorization wording is in
[align/convergence.md](../../references/align/convergence.md) §The cycle-authorization contract.

## Doctrine

- **Conductor, not author.** Every mutation belongs to `plan`, `write` or `build`; this body reports the run.
- **One authorization.** Present the complete stage plan, name `quenching-knowledge-documentation-produce` as grantor, and use one OK for the cycle.
- **Build first and last.** The first pass establishes extensions before pages use them; the last pass runs strict build and rendered QA.
- **Catalog stages stay ordered.** When a catalog is mapped, plan inventories its source and gaps,
  write emits the derived index/details with lineage, review checks reachability, and the final build
  reports the derived route count.
- **Coverage is a delivery gate over the whole bundle.** Consolidate the ledger from
  `.quenching/documentation/`, inventory every `/docs/` home, and report
  `covered / mandatory mapped × 100`. A page selected for this pass cannot hide an uncovered
  `standards/`, `concepts/`, `external/`, `catalog/`, `vision/` or glossary surface. Empty sections,
  source gaps and leaked internal markers remain explicit, then name the next stage or route that
  leaves the current page.
- **Glossary is default-on when it has content.** The canonical `/docs/glossary.md` is a
  mandatory derived surface unless the accepted map contains an explicit `não publicar` decision.
  The write stage runs `cq knowledge project --write`; the final build runs its `--check` mode and
  the rendered site checker, including a known `<abbr>` assertion.
- **Delivery destination is explicit.** At cycle start, identify the selected host (GitHub Pages,
  Azure DevOps artifact, or local-only). Forward any local-preview request to `build` as its own
  confirmation; an artifact or preview is never reported as an external deployment.
- **Editorial loop is bounded.** Route `review → write` for at most three rounds; an unresolved page is reported below threshold.
- **Stages are named registry entries.** Invoke `quenching:knowledge:documentation:build`, `quenching:knowledge:documentation:plan`, `quenching:knowledge:documentation:write` and `quenching:knowledge:documentation:review` with the `Skill` tool.

Running under `quenching-knowledge-documentation-produce` authorization granted at run start — skip your plan-confirmation pause; present your plan as narration and execute; code-coupled and irreversible items still gate individually.

## Workflow

### 1. Probe the target and present one cycle plan

Read-only probe the complete bundle, every source home, documentation home, source scope and
existing site layer. Present the ordered stages, files each stage may write, mandatory-surface
denominator, round cap, build fallback, delivery destination and source-gap policy. **Done when:**
the user gives one OK or the run stops with no stage invoked.

When `--desde <ref>` is present, validate the ref with `git rev-parse`, read the prior plan and pass
the resulting changed-source set to plan, write and review. An invalid ref or missing prior plan
falls back to the complete run and is recorded in the report; the full run remains the default.

### 2. Establish the site layer

Use the `Skill` tool to invoke `quenching:knowledge:documentation:build` as the first pass. It
ensures the Markdown extensions and CSS payload exist before prose is written. **Done when:** build
returns its site-layer report, including `unverified` when the toolchain is absent.

### 3. Create the plan of record

Invoke `quenching:knowledge:documentation:plan` with the source scope and the cycle authorization
sentence above. **Done when:** `.quenching/documentation/plan.md` contains all seven contracts,
the complete publication map and the accepted page assignments.

### 4. Write and review the pages

Invoke `quenching:knowledge:documentation:write`, then `quenching:knowledge:documentation:review`.
When the verdict is below threshold, pass the ranked defects to `write` and repeat this pair up to
three rounds. A source gap remains a reported gap. **Done when:** every page passes the rubric or
is explicitly marked below threshold with dimensions and evidence.

### 5. Validate the finished site

Invoke `quenching:knowledge:documentation:build` again. Read the strict-build result, run the
projection gate and **always** run `documentation-site-check.py` immediately after the build;
distinguish site-layer fixes from page-level reports and state browser-QA limits.
If preview was authorized, include its loopback URL/PID and confirmed shutdown; keep the external
deployment status separate from the artifact result.
**Done when:** the final report names the build result, QA mode, CSS/components checks and all
residual findings.

### 6. Close the run with an accountable report

Summarize stages, files written by each owner, per-page scores, ledger gaps, review rounds and the
next command for every residual. Include the coverage percentage and every empty/excluded section;
do not represent a page with internal TODOs or a source gap as shipped. **Done when:** the report is
self-contained and no page below the threshold is represented as shipped.

Persist the same summary as `.quenching/documentation/report.md` with `ref`, UTC `timestamp`,
incremental scope, files by owner, scorecard paths, review rounds, strict-build/static-QA results,
coverage, source gaps and the pending versioning policy. Keep this report outside `docs_dir` and
link it only from the handoff, never from a published page.

End with an explicit handoff to `quenching-git-commit`, naming the report and the files awaiting
review. This conductor does not stage or commit; the human-owned git command decides what crosses
the repository boundary.

## Invariants to never violate

- Never use `Write` or `Edit` from this conductor; it has no such grant.
- Never bypass a stage's own write and read-only boundaries.
- Never run more than three review→write rounds.
- Never claim strict build or pixel QA when the environment reported `unverified` or static-only.
