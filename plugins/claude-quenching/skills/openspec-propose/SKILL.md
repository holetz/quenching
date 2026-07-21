---
name: openspec-propose
description: >-
  Proposes a new OpenSpec change — creates the change and generates every planning artifact
  (proposal.md, delta specs, design.md, tasks.md) in one CLI-driven pass, reading the OKF
  docs/ bundle first so standards and glossary terminology shape the artifacts. Use
  when the user asks to "propose a change", "create an openspec change", "start a spec-driven
  change", "draft a proposal", "generate the change artifacts", or "develop this backlog task
  into a change". Derives a kebab-case name, runs `openspec new change`, then loops
  `status --json` → `instructions --json` → write, until apply-ready; a backlog/ task used as
  seed is retired into the Completed ledger on completion (one confirmation). Requires the
  openspec CLI (`@fission-ai/openspec`). Not for: implementing the tasks →
  openspec-apply-change; revising an existing change's artifacts → openspec-update-change;
  open-ended thinking before committing to a change → openspec-explore; a durable doc
  straight into docs/ → quenching-add.
when_to_use: >-
  creating a new OpenSpec change and generating all its artifacts until apply-ready.
  Implementation is openspec-apply-change; revising existing artifacts is
  openspec-update-change; pre-change thinking is openspec-explore.
allowed-tools: Bash(openspec:*), Read, Glob, Grep, Write, Edit
user-invocable: false
metadata:
  generatedBy: "1.6.0"
---

# openspec-propose — create a change with all artifacts

Propose a new change — create the change and generate all artifacts in one step:
`proposal.md` (what & why), delta specs, `design.md` (how), `tasks.md` (implementation
steps). When ready to implement, run `/opsx:implement`.

OpenSpec facts (layout, artifact graph, spec/delta format, CLI surface, `config.yaml`) live
in [references/openspec.md](references/openspec.md) — read it if any of those is unclear.
**Store selection:** per §Store selection there.

**Input**: The user's request should include a change name (kebab-case) OR a description of
what they want to build — possibly an `openspec/backlog/` task to develop.

**Steps**

1. **If no clear input provided, ask what they want to build**

   Use the **AskUserQuestion tool** (open-ended, no preset options) to ask:
   > "What change do you want to work on? Describe what you want to build or fix."

   From their description, derive a kebab-case name (e.g., "add user authentication" →
   `add-user-auth`).

   **IMPORTANT**: Do NOT proceed without understanding what the user wants to build.

2. **Read the OKF bundle as context (the OKF bridge)**

   If the repo carries an OKF bundle (`docs/index.md` with `okf_version`), before generating
   anything read what constrains this change:
   - `docs/standards/` docs for the subjects the change touches (binding contracts for how
     we build — the design must not contradict them; a `standard` with `authority: background`
     is an agreed-but-unproven rule the change may resolve);
   - `docs/knowledge/glossary.md` — use the repo's canonical terminology in every artifact;
   - if the seed is an `openspec/backlog/<task-slug>.md` task, read it — it is the proposal's
     germ, and it will be retired in step 7.

   No bundle → skip silently; this step never blocks a repo that hasn't adopted OKF.

3. **Create the change directory**
   ```bash
   openspec new change "<name>"
   ```
   This creates a scaffolded change in the planning home resolved by the CLI with
   `.openspec.yaml`.

4. **Get the artifact build order**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to get:
   - `applyRequires`: array of artifact IDs needed before implementation (e.g., `["tasks"]`)
   - `artifacts`: list of all artifacts with their status and dependencies
   - `planningHome`, `changeRoot`, `artifactPaths`, and `actionContext`: path and scope
     context. Use these instead of assuming repo-local paths.

5. **Create artifacts in sequence until apply-ready**

   Use the **TodoWrite tool** to track progress through the artifacts.

   Loop through artifacts in dependency order (artifacts with no pending dependencies first):

   a. **For each artifact that is `ready` (dependencies satisfied)**:
      - Get instructions:
        ```bash
        openspec instructions <artifact-id> --change "<name>" --json
        ```
      - The instructions JSON includes:
        - `context`: Project background (constraints for you - do NOT include in output)
        - `rules`: Artifact-specific rules (constraints for you - do NOT include in output)
        - `template`: The structure to use for your output file
        - `instruction`: Schema-specific guidance for this artifact type
        - `resolvedOutputPath`: Resolved path or pattern to write the artifact
        - `dependencies`: Completed artifacts to read for context
      - Read any completed dependency files for context
      - Create the artifact file using `template` as the structure and write it to
        `resolvedOutputPath`
      - Apply `context` and `rules` as constraints - but do NOT copy them into the file
      - Apply the OKF context from step 2 the same way: standards constrain the design,
        glossary terms name things, the seed task's gist anchors the proposal
      - Show brief progress: "Created <artifact-id>"

   b. **Continue until all `applyRequires` artifacts are complete**
      - After creating each artifact, re-run `openspec status --change "<name>" --json`
      - Check if every artifact ID in `applyRequires` has `status: "done"` in the artifacts
        array
      - Stop when all `applyRequires` artifacts are done

   c. **If an artifact requires user input** (unclear context):
      - Use **AskUserQuestion tool** to clarify
      - Then continue with creation

6. **Show final status**
   ```bash
   openspec status --change "<name>"
   ```

7. **Retire the seed task (only when the seed was an `openspec/backlog/` task)**

   The backlog lifecycle: once a change's artifacts are apply-ready, the task has been
   **developed** and leaves the tree. With ONE confirmation ("the change is apply-ready —
   retire the seed task <slug>?"):
   - add a row to the Completed ledger in `openspec/backlog/index.md`:
     `| <task title> | openspec change <name> | YYYY-MM-DD |`;
   - delete `openspec/backlog/<task-slug>.md`, then regenerate the index's DERIVED zone from the
     remaining tasks' frontmatter (per
     [../openspec-backlog/references/backlog-zone.md](../openspec-backlog/references/backlog-zone.md)) —
     never hand-edit inside the markers;
   - if the repo carries an OKF `docs/` bundle, append to `docs/log.md` (per §Appending to
     `log.md` in [../quenching-add/references/homes.md](../quenching-add/references/homes.md)):
     `**Deprecation**: <task title> — developed into openspec change <name>` (the bundle log
     still records the cross-boundary event).

   If the user declines, or the artifacts stopped short of apply-ready, the task stays put —
   an abandoned exploration leaves the inbox untouched.

**Output**

After completing all artifacts, summarize:
- Change name and location
- List of artifacts created with brief descriptions
- Which OKF inputs shaped them (standards read, seed task, glossary terms) — one line
- What's ready: "All artifacts created! Ready for implementation."
- Prompt: "Run `/opsx:implement` or ask me to implement to start working on the tasks."

**Artifact Creation Guidelines**

- Follow the `instruction` field from `openspec instructions` for each artifact type
- The schema defines what each artifact should contain - follow it
- Read dependency artifacts for context before creating new ones
- Use `template` as the structure for your output file - fill in its sections
- **IMPORTANT**: `context` and `rules` are constraints for YOU, not content for the file
  - Do NOT copy `<context>`, `<rules>`, `<project_context>` blocks into the artifact
  - These guide what you write, but should never appear in the output

**Guardrails**
- Create ALL artifacts needed for implementation (as defined by schema's `apply.requires`)
- Always read dependency artifacts before creating a new one
- If context is critically unclear, ask the user - but prefer making reasonable decisions to
  keep momentum
- If a change with that name already exists, ask if user wants to continue it or create a
  new one
- Verify each artifact file exists after writing before proceeding to next
- Never delete a seed task without the step-7 confirmation, and never touch `docs/` beyond
  step 7's `docs/log.md` deprecation line (the task file + its ledger/zone live in
  `openspec/backlog/`) — durable knowledge the proposal surfaces routes through
  `quenching-add`/`quenching-learn`, and archive-time distillation belongs to
  openspec-archive-change
