---
name: quenching-specs-plan-propose
description: >-
  Proposes a new plan — scaffolds specs/<name>/ and generates every planning artifact
  (proposal.md, an optional design.md, tasks.md), reading the OKF docs/ bundle first so
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
`proposal.md` (what & why + declared scope), an optional `design.md` (how), `tasks.md`
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

3. **Scaffold the plan**
   ```bash
   specs.py new "<name>" [--title "<T>"] [--backlog-task <slug>]
   ```
   This creates `specs/<name>/` with `.specs.json` and the three templates stamped from
   `assets/specs/templates/`. Pass `--backlog-task <slug>` when a `specs/backlog/` task seeds
   the plan — it records the linkage in `.specs.json` so step 7 knows which task to retire. If a
   plan with that name already exists (exit ≠ 0), ask whether to continue it
   (`quenching-specs-plan-update`) or pick a new name.

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
      It collapses the graph to one instruction (write proposal · write/delete design · write
      tasks · ready to archive) — never infer the next step from prose.

   b. **Write that artifact** to its resolved path, following
      [references/artifacts.md](references/artifacts.md) for what belongs in it:
      - `proposal.md` → `## Why`, `## What Changes`, `## Impact` (the declared `docs/` + code
        scope; every `docs/standards/` path here also becomes a `tasks.md` item);
      - `design.md` → written **only if there is a real decision to record**; otherwise
        **delete the scaffolded file** (absent is valid — do not fill it with restated proposal
        text);
      - `tasks.md` → dependency-ordered checkboxes, with an explicit item for each standard the
        plan will write into `docs/standards/` and for verification.
      Apply the step-2 OKF context as constraints: standards constrain the design, glossary
      terms name things, the seed task's gist anchors the proposal — do not copy any of it in
      verbatim as boilerplate.

   c. **Re-run `specs.py status --plan "<name>" --json`** after each write and continue until
      `applyReady` is true (proposal + tasks present and well-formed; design present or
      deliberately absent).

   d. **If an artifact needs user input** (unclear scope, a decision only the human can make),
      use **AskUserQuestion** to clarify, then continue.

6. **Show final status**
   ```bash
   specs.py status --plan "<name>" --json
   ```
   Confirm `applyReady: true` and that `specs.py validate --plan "<name>"` exits 0.

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
- Artifacts created (and whether `design.md` was written or deliberately omitted)
- Which OKF inputs shaped them (standards read, seed task, glossary terms) — one line
- What's ready: "All artifacts created — apply-ready."
- Prompt: "Run `/specs:plan:apply` or ask me to implement to start working on the tasks."

**Guardrails**
- Create every artifact `applyRequires` names (`proposal`, `tasks`); `design.md` is optional —
  write it only when warranted, else delete the scaffold.
- Drive the loop off `specs.py next` / `status --json` and its exit codes — never infer state
  from prose, never assume artifact paths.
- Always read completed artifacts (and the step-2 OKF context) before writing the next one.
- If context is critically unclear, ask — but prefer reasonable decisions to keep momentum.
- Never write a delta spec, a `spec.md`, or sync anything: durable rules go **directly** into
  `docs/standards/` at apply time, not into a second store.
- Never delete a seed task without the step-7 confirmation, and never touch `docs/` beyond
  step 7's `docs/log.md` line — durable knowledge the proposal surfaces routes through
  `quenching-docs-add`/`quenching-docs-learn`, and archive-time distillation belongs to
  `quenching-specs-plan-archive`.
