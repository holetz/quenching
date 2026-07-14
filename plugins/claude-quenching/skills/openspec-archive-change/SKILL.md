---
name: openspec-archive-change
description: >-
  Archives a completed OpenSpec change — checks artifact and task completion, offers the
  delta-spec sync into main specs, moves the change folder to changes/archive/YYYY-MM-DD-
  <name>/, then offers ONE OKF distillation pass: minting into docs/ the durable knowledge
  the change produced (decision with alternatives → ADR, generic understanding →
  knowledge/, new terms → glossary). Use when the user asks to "archive the change",
  "finalize the change", "close out this openspec change", or "the change is done, wrap it
  up". Warnings never block (incomplete items just confirm); nothing is bulk-copied — the
  archived change stays the OpenSpec history, only durable knowledge crosses the bridge.
  Requires the openspec CLI (`@fission-ai/openspec`). Not for: implementing remaining tasks
  → openspec-apply-change; syncing specs without archiving → openspec-sync-specs; inserting
  an arbitrary doc into docs/ → quenching-insert.
when_to_use: >-
  finalizing and archiving a completed OpenSpec change, including the post-archive OKF
  distillation offer. Implementation is openspec-apply-change; sync-only is
  openspec-sync-specs.
allowed-tools: Bash(openspec:*), Bash(mkdir:*), Bash(mv:*), Read, Glob, Grep, Write, Edit
metadata:
  generatedBy: "1.6.0"
---

# openspec-archive-change — archive a completed change, then distill

Archive a completed change, then offer to distill its durable knowledge into the OKF
`docs/` bundle.

OpenSpec facts (layout, artifact graph, formats, CLI surface) live in
[../openspec-propose/references/openspec.md](../openspec-propose/references/openspec.md).
**Store selection:** per §Store selection there. The distillation doctrine (what crosses to
`docs/`, what stays) lives in [references/distill.md](references/distill.md).

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from
conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **If no change name provided, prompt for selection**

   Run `openspec list --json` to get available changes. Use the **AskUserQuestion tool** to
   let the user select.

   Show only active changes (not already archived).
   Include the schema used for each change if available.

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose.

2. **Check artifact completion status**

   Run `openspec status --change "<name>" --json` to check artifact completion.

   Parse the JSON to understand:
   - `schemaName`: The workflow being used
   - `planningHome`, `changeRoot`, `artifactPaths`, and `actionContext`: path and scope
     context
   - `artifacts`: List of artifacts with their status (`done` or other)

   **If any artifacts are not `done`:**
   - Display warning listing incomplete artifacts
   - Use **AskUserQuestion tool** to confirm user wants to proceed
   - Proceed if user confirms

3. **Check task completion status**

   Read the tasks file (typically `tasks.md`) to check for incomplete tasks.

   Count tasks marked with `- [ ]` (incomplete) vs `- [x]` (complete).

   **If incomplete tasks found:**
   - Display warning showing count of incomplete tasks
   - Use **AskUserQuestion tool** to confirm user wants to proceed
   - Proceed if user confirms

   **If no tasks file exists:** Proceed without task-related warning.

4. **Assess delta spec sync state**

   Use `artifactPaths.specs.existingOutputPaths` from status JSON to check for delta specs.
   If none exist, proceed without sync prompt.

   **If delta specs exist:**
   - Compare each delta spec with its corresponding main spec at
     `openspec/specs/<capability>/spec.md`
   - Determine what changes would be applied (adds, modifications, removals, renames)
   - Show a combined summary before prompting

   **Prompt options:**
   - If changes needed: "Sync now (recommended)", "Archive without syncing"
   - If already synced: "Archive now", "Sync anyway", "Cancel"

   If user chooses sync, use Task tool (subagent_type: "general-purpose", prompt: "Use
   Skill tool to invoke claude-quenching:openspec-sync-specs for change '<name>'. Delta
   spec analysis: <include the analyzed delta spec summary>"). Proceed to archive
   regardless of choice.

5. **Perform the archive**

   Create an `archive` directory under `planningHome.changesDir` if it doesn't exist:
   ```bash
   mkdir -p "<planningHome.changesDir>/archive"
   ```

   Generate target name using current date: `YYYY-MM-DD-<change-name>`

   **Check if target already exists:**
   - If yes: Fail with error, suggest renaming existing archive or using different date
   - If no: Move `changeRoot` to the archive directory

   ```bash
   mv "<changeRoot>" "<planningHome.changesDir>/archive/YYYY-MM-DD-<name>"
   ```

6. **Distill durable knowledge into the OKF bundle (the OKF bridge)**

   If the repo carries an OKF bundle (`docs/index.md` with `okf_version`), run the
   distillation procedure in [references/distill.md](references/distill.md):
   - **harvest** the archived artifacts for durable candidates (decision with alternatives
     → ADR in `decisions/`; generic understanding → `knowledge/`; new repo-specific terms →
     `knowledge/glossary.md`; proven build-rule → `standards/`; unpursued follow-up task →
     `backlog/`);
   - present them as **one plan, one confirmation** (an empty harvest is a valid outcome —
     say so and finish);
   - mint each approved doc under the insert procedure
     ([../quenching-insert/references/homes.md](../quenching-insert/references/homes.md))
     and log each in `docs/log.md` as distilled from the change;
   - self-check against
     [../quenching-align/references/conformance.md](../quenching-align/references/conformance.md).

   No bundle → skip silently (optionally mention `quenching-align` installs one).

7. **Display summary**

   Show archive completion summary including:
   - Change name
   - Schema that was used
   - Archive location
   - Whether specs were synced (if applicable)
   - What was distilled into `docs/` (docs minted, or "nothing durable — archive only")
   - Note about any warnings (incomplete artifacts/tasks)

**Output On Success**

```
## Archive Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Archived to:** the archive path derived from `planningHome.changesDir`/YYYY-MM-DD-<name>/
**Specs:** ✓ Synced to main specs (or "No delta specs" or "Sync skipped")
**Distilled:** <N docs minted into docs/> (or "nothing durable to distill")

All artifacts complete. All tasks complete.
```

**Guardrails**
- Always prompt for change selection if not provided
- Use artifact graph (openspec status --json) for completion checking
- Don't block archive on warnings - just inform and confirm
- Preserve .openspec.yaml when moving to archive (it moves with the directory)
- Show clear summary of what happened
- If sync is requested, use openspec-sync-specs approach (agent-driven)
- If delta specs exist, always run the sync assessment and show the combined summary before
  prompting
- Distillation is **offer-and-confirm, never automatic**: one plan, one OK, strike-able
  items; never bulk-copy artifacts into `docs/`, never edit the archived change, never
  fabricate a candidate (per [references/distill.md](references/distill.md) §Invariants)
