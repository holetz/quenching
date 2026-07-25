---
name: quenching-specs-plan-propose
description: >-
  Proposes a new plan — scaffolds specs/<name>/ and generates every planning artifact
  (proposal.md, design.md, tasks.md — every section required-with-explicit-fallback), reading
  the OKF docs/ bundle first so
  standards and glossary terminology shape them; it writes NO delta specs. Use when the user
  asks to "propose a plan", "create a spec-driven plan", "start a plan", "draft a proposal",
  "generate the plan artifacts", or "develop this backlog task into a plan". Derives a
  kebab-case name, runs specs.py new <name>, then loops specs.py status/next → write until
  apply-ready; a specs/backlog/ task used as seed is retired into the Completed ledger at
  apply-ready (one confirmation). Not for: implementing the tasks → quenching-specs-plan-apply;
  revising an existing plan's artifacts → quenching-specs-plan-update; open-ended thinking
  before committing → quenching-specs-explore; a durable doc straight into docs/ →
  quenching-docs-add.
when_to_use: >-
  creating a new plan and generating all its artifacts until apply-ready. Implementation is
  quenching-specs-plan-apply; revising existing artifacts is quenching-specs-plan-update;
  pre-plan thinking is quenching-specs-explore.
allowed-tools: Bash(python3:*), Bash(py:*), Read, Glob, Grep, Write, Edit, AskUserQuestion, TodoWrite
user-invocable: false
---

# quenching-specs-plan-propose — create a plan with all artifacts

Propose a new **plan** — scaffold `specs/<name>/` and generate all its artifacts in one pass:
`proposal.md` (what & why + declared scope), `design.md` (how), `tasks.md`
(implementation steps). When ready to implement, run `/specs:plan:apply`.

The spec-driven facts — the `specs/` layout, the plan artifact graph, the artifact formats,
the `specs.py` tool surface, and the `specs/` ↔ `docs/` boundary — live in
[references/spec-driven.md](references/spec-driven.md). The per-artifact **authoring doctrine**
(what belongs in each of the three files, when a `design.md` is warranted vs. deleted, how to
shape the `tasks.md` checkboxes including the standards-writing items) lives in
[references/artifacts.md](references/artifacts.md). Read both if anything below is unclear.

**No deltas.** This front is entirely native: a plan writes its durable rules **directly** into
`docs/standards/` as it is built (that is `quenching-specs-plan-apply`'s job), so there are no
ADDED/MODIFIED/REMOVED delta specs, no `changes/<n>/specs/`, and no sync. The proposal only
**declares** that scope in `## Impact` (prose) and lists each standard as a `tasks.md` item.

## Resolving the tool

Resolve `specs.py` by the fallback in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§Resolving the tool: the plugin path `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then the
target's `.claude/hooks/specs.py`, and if neither resolves, do the equivalent check by hand and
**say in the report that it was manual**. Invoke with `python3` or `py`. Every subcommand takes
`--json`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the JSON, never on prose.

**Input**: The user's request should include a plan name (kebab-case) OR a description of what
they want to build — possibly a `specs/backlog/` task to develop.

**Steps**

1. **If no clear input provided, ask what they want to build**

   Use the **AskUserQuestion tool** (open-ended, no preset options) to ask:
   > "What plan do you want to work on? Describe what you want to build or fix."

   From their description, derive a kebab-case name (e.g. "add user authentication" →
   `add-user-auth`).

   **IMPORTANT**: Do NOT proceed without understanding what the user wants to build.

2. **Read the OKF bundle as context (the OKF bridge)**

   If the repo carries an OKF bundle (`docs/index.md` with `okf_version`), before generating
   anything read what constrains this plan:
   - `docs/standards/` docs for the subjects the plan touches — binding contracts for how we
     build; the design must not contradict them, and a `standard` at `authority: background` is
     an agreed-but-unproven rule this plan may resolve (promote to `current` once proved);
   - `docs/knowledge/glossary.md` — use the repo's canonical terminology in every artifact;
   - if the seed is a `specs/backlog/<task-slug>.md` task, read it — it is the proposal's germ,
     and it is retired in step 7.

   No bundle → skip silently; this step never blocks a repo that hasn't adopted OKF.

3. **Scaffold the plan, and declare its verification policy**
   ```bash
   specs.py new "<name>" [--title "<T>"] [--backlog-task <slug>] [--verification <policy>]
   ```
   This creates `specs/<name>/` with `.specs.json` and the three templates stamped from
   `assets/specs/templates/`. Pass `--backlog-task <slug>` when a `specs/backlog/` task seeds
   the plan — it records the linkage in `.specs.json` so step 7 knows which task to retire. If a
   plan with that name already exists (exit ≠ 0), ask whether to continue it
   (`quenching-specs-plan-update`) or pick a new name.

   **`--verification` is decided here, at propose time, and never again.** It records when
   `quenching-specs-plan-apply` runs each task's check, so implementation never has to guess and
   never has to interrupt the human mid-task to ask:

   | Policy | Runs the check | Choose when |
   | --- | --- | --- |
   | `per-task` | after every task | the suite is fast, or each step can break the last |
   | `per-section` *(default)* | after each `## N.` section's last task | most repos |
   | `end-of-plan` | once, after the final task | the suite is slow, or nothing is meaningful until the whole plan lands |

   Pick from what the repo actually is — its test command, its CI, its `docs/standards/quality/`
   contracts if it has any. The default is right often enough that it needs no ceremony; state the
   choice in one line rather than asking.

4. **Get the artifact build order**
   ```bash
   specs.py status --plan "<name>" --json
   ```
   Parse the JSON: each artifact's `state` (`done` / `ready` / `blocked`), `applyReady`, and the
   **resolved file paths**. Use these paths — never assume repo-local ones.

5. **Create artifacts in sequence until apply-ready**

   Use the **TodoWrite tool** to track progress through the three artifacts. Loop:

   a. Ask the tool for the single next action:
      ```bash
      specs.py next --plan "<name>"
      ```
      It collapses the graph to one instruction (write proposal · write design · write
      tasks · implement task N · ready to archive) — never infer the next step from prose.

   b. **Write that artifact** to its resolved path, following
      [references/artifacts.md](references/artifacts.md) for what belongs in it. Every section is
      **required-with-explicit-fallback**: the heading always exists and an empty one is answered
      `- none` (`- none — <reason>` in `design.md`), never deleted and never padded.
      - `proposal.md` → `## Why`, `## What Changes`, `## Out of Scope`, `## Validation`,
        `## Impact`. Under `## Impact`, the `### Standards this plan will write into
        docs/standards/` sub-heading is **parsed** — every path bulleted there must also become a
        `tasks.md` item, or `validate` reports `sp-impact-uncovered`.
      - `design.md` → `## Context`, `## Decisions`, `## Alternatives Considered`,
        `## Open Decisions`, `## Risks`. **Never delete this file.** An absent `design.md` cannot
        distinguish *we weighed the alternatives and there were none* from *nobody thought about
        it*; an explicit `- none — <reason>` can. A file left as the bare scaffold is reported as
        `sp-design-scaffold` (warn) — it does not block apply.
      - `tasks.md` → dependency-ordered checkboxes, with an explicit item for each standard the
        plan will write into `docs/standards/` and for verification.
      Apply the step-2 OKF context as constraints: standards constrain the design, glossary
      terms name things, the seed task's gist anchors the proposal — do not copy any of it in
      verbatim as boilerplate.

   c. **Re-run `specs.py status --plan "<name>" --json`** after each write and continue until
      `applyReady` is true (proposal + tasks present and well-formed).

      `applyReady` is a **floor, not a verdict**: it means the required artifacts have content,
      never that the plan is any good. `specs.py validate` reports what it cannot —
      `sp-design-scaffold`, `sp-impact-uncovered`, `sp-unrefined` — and none of them gates.

   d. **If an artifact needs user input** (unclear scope, a decision only the human can make),
      use **AskUserQuestion** to clarify, then continue.

6. **Show final status, and offer a refinement pass**
   ```bash
   specs.py status --plan "<name>" --json
   ```
   Confirm `applyReady: true` and that `specs.py validate --plan "<name>"` exits 0.

   Then **offer one refinement pass** — `/specs:plan:refine <name>` — before the plan is built.
   The plan just reached apply-ready without anyone having disagreed with it, and this guardrail's
   own "prefer reasonable decisions to keep momentum" is exactly what a refinement is there to go
   back and check. Recommend the mode the plan's state argues for (`critic` for a large or
   code-reaching plan, `premortem` for an irreversible one, `alternatives` when only one approach
   was ever weighed, `interview` otherwise).

   **Offer it; never impose it, and never gate on it.** A declined offer is a complete answer —
   the plan stays apply-ready and `validate` carries `sp-unrefined` as the honest record that
   nobody interrogated it.

7. **Retire the seed task (only when the seed was a `specs/backlog/` task)**

   The backlog lifecycle: once a plan's artifacts are apply-ready, the task has been
   **developed** and leaves the inbox. With ONE confirmation ("the plan is apply-ready — retire
   the seed task `<slug>`?"):
   - add a row to the Completed ledger in `specs/backlog/index.md`:
     `| <task title> | plan <name> | YYYY-MM-DD |` (the Outcome column reads `plan <name>` — that
     is what marks the row *developed*, not *done*);
   - delete `specs/backlog/<task-slug>.md`, then regenerate the index's DERIVED zone from the
     remaining tasks' frontmatter — run `specs.py backlog reindex`, never hand-edit inside the
     markers (per
     [../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md));
   - if the repo carries an OKF `docs/` bundle, append to `docs/log.md` (per §Appending to
     `log.md` in [../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md)):
     `**Deprecation**: <task title> — developed into plan <name>` (the bundle log records the
     cross-boundary event).

   If the user declines, or the artifacts stopped short of apply-ready, the task stays put — an
   abandoned exploration leaves the inbox untouched.

   **The row means *developed*, not *done*.** The work has left the inbox but has not shipped;
   the ledger records both transitions and the Outcome column tells them apart
   ([../quenching-specs-align/references/conformance.md](../quenching-specs-align/references/conformance.md)
   §The ledger's two meanings). If this plan is later dropped, `quenching-specs-plan-abandon`
   (`/specs:plan:abandon`) strikes the row and restores the task — so retiring it here is a
   reversible handoff, not a deletion.

**Output**

After completing all artifacts, summarize:
- Plan name and `specs/<name>/` location
- Artifacts created, and any section answered `- none` with its reason
- Which OKF inputs shaped them (standards read, seed task, glossary terms) — one line
- What's ready: "All artifacts created — apply-ready." plus any open `validate` warning
- Prompt: "Refine it first (`/specs:plan:refine`), or run `/specs:plan:apply` to start the tasks."

**Guardrails**
- Create all three artifacts. `design.md` is required as a **section set** (never deleted; an
  empty section answered `- none — <reason>`) but not as a **dependency** — `applyRequires` stays
  `["tasks"]`, so a thin design never blocks apply.
- Drive the loop off `specs.py next` / `status --json` and its exit codes — never infer state
  from prose, never assume artifact paths.
- Always read completed artifacts (and the step-2 OKF context) before writing the next one.
- If context is critically unclear, ask — but prefer reasonable decisions to keep momentum, then
  **offer the refinement pass** (step 6) so the decisions momentum made get argued with before the
  plan is built. Momentum is the right default for authoring and the wrong default for shipping;
  `/specs:plan:refine` is where the difference gets settled.
- Never write a delta spec, a `spec.md`, or sync anything: durable rules go **directly** into
  `docs/standards/` at apply time, not into a second store.
- Never delete a seed task without the step-7 confirmation, and never touch `docs/` beyond
  step 7's `docs/log.md` line — durable knowledge the proposal surfaces routes through
  `quenching-docs-add`/`quenching-docs-learn`, and archive-time distillation belongs to
  `quenching-specs-plan-archive`.
