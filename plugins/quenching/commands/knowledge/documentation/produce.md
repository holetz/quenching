---
description: Conduct the complete documentation pipeline from site setup through sourced pages, bounded editorial review and strict build QA. Triggers on "produce the documentation", "run the documentation pipeline", or "generate the complete docs site". Not for: planning only → /quenching:knowledge:documentation:plan; writing an assigned page set → /quenching:knowledge:documentation:write; reviewing without writes → /quenching:knowledge:documentation:review; site-layer configuration or a standalone build → /quenching:knowledge:documentation:build.
argument-hint: [optional-source-scope]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Skill
---

# /quenching:knowledge:documentation:produce — conduct the documentation pipeline

**Input**: `$ARGUMENTS` (optional source scope; omit to run the complete target-repository pipeline).

This conductor coordinates the four sibling stages through the `Skill` tool and owns no writes.
The shared contracts are in
[knowledge-documentation/quality.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-documentation/quality.md)
and the cycle authorization wording is in
[align/convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md) §The cycle-authorization contract.

## Doctrine

- **Conductor, not author.** Every mutation belongs to `plan`, `write` or `build`; this body reports the run.
- **One authorization.** Present the complete stage plan, name `/quenching:knowledge:documentation:produce` as grantor, and use one OK for the cycle.
- **Build first and last.** The first pass establishes extensions before pages use them; the last pass runs strict build and rendered QA.
- **Editorial loop is bounded.** Route `review → write` for at most three rounds; an unresolved page is reported below threshold.
- **Stages are named registry entries.** Invoke `quenching:knowledge:documentation:build`, `quenching:knowledge:documentation:plan`, `quenching:knowledge:documentation:write` and `quenching:knowledge:documentation:review` with the `Skill` tool.

Running under `/quenching:knowledge:documentation:produce` authorization granted at run start — skip your plan-confirmation pause; present your plan as narration and execute; code-coupled and irreversible items still gate individually.

## Workflow

### 1. Probe the target and present one cycle plan

Read-only probe the bundle, documentation home, source scope and existing site layer. Present the
ordered stages, files each stage may write, round cap, build fallback and source-gap policy. **Done when:**
the user gives one OK or the run stops with no stage invoked.

### 2. Establish the site layer

Use the `Skill` tool to invoke `quenching:knowledge:documentation:build` as the first pass. It
ensures the MkDocs extensions and CSS payload exist before prose is written. **Done when:** build
returns its site-layer report, including `unverified` when the toolchain is absent.

### 3. Create the plan of record

Invoke `quenching:knowledge:documentation:plan` with the source scope and the cycle authorization
sentence above. **Done when:** `.quenching/documentation/plan.md` contains all six contracts and
the accepted page assignments.

### 4. Write and review the pages

Invoke `quenching:knowledge:documentation:write`, then `quenching:knowledge:documentation:review`.
When the verdict is below threshold, pass the ranked defects to `write` and repeat this pair up to
three rounds. A source gap remains a reported gap. **Done when:** every page passes the rubric or
is explicitly marked below threshold with dimensions and evidence.

### 5. Validate the finished site

Invoke `quenching:knowledge:documentation:build` again. Read the strict-build result and static
rendered checks; distinguish site-layer fixes from page-level reports and state browser-QA limits.
**Done when:** the final report names the build result, QA mode, CSS/components checks and all
residual findings.

### 6. Close the run with an accountable report

Summarize stages, files written by each owner, per-page scores, ledger gaps, review rounds and the
next command for every residual. **Done when:** the report is self-contained and no page below the
threshold is represented as shipped.

## Invariants to never violate

- Never use `Write` or `Edit` from this conductor; it has no such grant.
- Never bypass a stage's own write and read-only boundaries.
- Never run more than three review→write rounds.
- Never claim strict build or pixel QA when the environment reported `unverified` or static-only.
