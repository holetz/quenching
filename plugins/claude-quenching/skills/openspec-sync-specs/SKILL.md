---
name: openspec-sync-specs
description: >-
  Syncs a change's delta specs into the main specs under openspec/specs/ — the source of
  truth for CURRENT behavior — by intelligently merging ADDED/MODIFIED/REMOVED/RENAMED
  requirement blocks, without archiving the change. Use when the user asks to "sync the
  specs", "apply the delta specs to main", "update main specs from the change", or "merge
  the spec deltas". Agent-driven merging: partial updates are applied as intent (add a
  scenario without copying the whole requirement), content the delta doesn't mention is
  preserved, and the operation is idempotent. Requires the openspec CLI
  (`@fission-ai/openspec`). Boundary: openspec/specs/ holds WHAT the product currently does;
  docs/standards/ holds HOW we build — never duplicate content between them. Not for:
  archiving the change (which offers this sync) → openspec-archive-change; revising the
  delta itself → openspec-update-change.
when_to_use: >-
  merging a change's delta specs into the main specs without archiving. Archive-time sync
  is offered by openspec-archive-change; editing the delta is openspec-update-change.
allowed-tools: Bash(openspec:*), Read, Glob, Grep, Write, Edit
user-invocable: false
metadata:
  generatedBy: "1.6.0"
---

# openspec-sync-specs — merge delta specs into main specs

Sync delta specs from a change to main specs.

This is an **agent-driven** operation - you will read delta specs and directly edit main
specs to apply the changes. This allows intelligent merging (e.g., adding a scenario
without copying the entire requirement).

OpenSpec facts (layout, spec/delta format, CLI surface) live in
[../openspec-propose/references/openspec.md](../openspec-propose/references/openspec.md) —
§Spec format holds the delta format reference. **Store selection:** per §Store selection
there.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from
conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **If no change name provided, prompt for selection**

   Run `openspec list --json` to get available changes. Use the **AskUserQuestion tool** to
   let the user select.

   Show changes that have delta specs (under `specs/` directory).

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose.

2. **Resolve change context**

   Run:
   ```bash
   openspec status --change "<name>" --json
   ```

3. **Find delta specs**

   Use `artifactPaths.specs.existingOutputPaths` from the status JSON as the list of delta
   spec files.

   Each delta spec file contains sections like:
   - `## ADDED Requirements` - New requirements to add
   - `## MODIFIED Requirements` - Changes to existing requirements
   - `## REMOVED Requirements` - Requirements to remove
   - `## RENAMED Requirements` - Requirements to rename (FROM:/TO: format)

   If no delta specs found, inform user and stop.

4. **For each delta spec, apply changes to main specs**

   For each repo-local capability delta spec path returned by the CLI:

   a. **Read the delta spec** to understand the intended changes

   b. **Read the main spec** at `openspec/specs/<capability>/spec.md` (may not exist yet)

   c. **Apply changes intelligently**:

      **ADDED Requirements:**
      - If requirement doesn't exist in main spec → add it
      - If requirement already exists → update it to match (treat as implicit MODIFIED)

      **MODIFIED Requirements:**
      - Find the requirement in main spec
      - Apply the changes - this can be:
        - Adding new scenarios (don't need to copy existing ones)
        - Modifying existing scenarios
        - Changing the requirement description
      - Preserve scenarios/content not mentioned in the delta

      **REMOVED Requirements:**
      - Remove the entire requirement block from main spec

      **RENAMED Requirements:**
      - Find the FROM requirement, rename to TO

   d. **Create new main spec** if capability doesn't exist yet:
      - Create `openspec/specs/<capability>/spec.md`
      - Add Purpose section (can be brief, mark as TBD)
      - Add Requirements section with the ADDED requirements

5. **Show summary**

   After applying all changes, summarize:
   - Which capabilities were updated
   - What changes were made (requirements added/modified/removed/renamed)

**Key Principle: Intelligent Merging**

Unlike programmatic merging, you can apply **partial updates**:
- To add a scenario, just include that scenario under MODIFIED - don't copy existing
  scenarios
- The delta represents *intent*, not a wholesale replacement
- Use your judgment to merge changes sensibly

**Output On Success**

```
## Specs Synced: <change-name>

Updated main specs:

**<capability-1>**:
- Added requirement: "New Feature"
- Modified requirement: "Existing Feature" (added 1 scenario)

**<capability-2>**:
- Created new spec file
- Added requirement: "Another Feature"

Main specs are now updated. The change remains active - archive when implementation is
complete.
```

**Guardrails**
- Read both delta and main specs before making changes
- Preserve existing content not mentioned in delta
- If something is unclear, ask for clarification
- Show what you're changing as you go
- The operation should be idempotent - running twice should give same result
- **Stay out of `docs/`**: `openspec/specs/` owns WHAT the product currently does
  (capability behavior); `docs/standards/` owns HOW we build (binding contracts). A sync
  never writes into the OKF bundle, and behavior statements never get mirrored into
  `standards/` — if a delta reveals a build-rule worth codifying, offer `quenching-add`
  separately.
