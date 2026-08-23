---
description: Mint or edit ONE subagent definition in this repo's .claude/agents/ — a delegation that returns a summary, not a trail. Use when the user asks to "create an agent", "add a subagent", "make a verifier agent", "delegate this to an agent", or "set up something that audits our migrations and reports back". Applies the delegation test, scopes tools to the narrowest set, prices the definition's always-on cost, and lands the OKF tail on one OK.
argument-hint: [agent-name-or-description]
allowed-tools: Bash(python3:*), Bash(py:*), Read, Grep, Glob, Write, Edit
---

# /quenching:components:agent:new — mint ONE subagent definition

**Input**: `$ARGUMENTS` (the agent to create or edit — a name or a description of the work
to delegate).

Creates or edits **ONE FILE** in the target repo's agent surface — `.claude/agents/<name>.md`,
a definition whose description routes delegation to it and whose body is its system prompt.
The delegation economics and the definition contract live in
[components-command-new/capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/capabilities.md)
§Subagents — owned by `/quenching:components:command:new`'s doctrine set and applied here. The mold is
`${CLAUDE_PLUGIN_ROOT}/assets/templates/automation/agent.md`.

## Doctrine

- **The rule governs; the plan proposes.** In a target repo the rule is
  `/.knowledge/standards/automation/agents.md` — read it before drafting and follow it when present.
  Absent + OKF bundle present → the plan offers creating it from
  `automation/agents-standard.md`, born `authority: background`; never created without the OK.
- **No bundle, no tail — but the mint proceeds.** `/.knowledge/index.md` without `okf_version` (or
  absent) means: write the definition only, skip the OKF tail silently, suggest `/quenching:knowledge:align`
  **once**.
- **One plan, one OK, nothing before.** The delegation buy, the name, the profile, every
  file, and the tail appear in ONE plan; a declined plan writes nothing.
- **MERGE, never clobber.** An edit preserves the body and any hand-written content; only the
  gap being fixed changes. This skill never deletes an agent.
- **An agent's description is always-on context.** The same two caps as a command's, counted
  on the parsed value; a definition earns its standing cost the way a command does.

Resolve `cq` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

## Workflow

### 1. Read the rule
Read `/.knowledge/standards/automation/agents.md` and confirm the bundle (`/.knowledge/index.md` carries
`okf_version`). Rule present → it governs. Rule absent, bundle present → add "create the rule
from `automation/agents-standard.md`" to the plan. No bundle → note the tail as skipped and
plan the `/quenching:knowledge:align` suggestion. **Done when:** the governing rule (or its planned
creation, or the no-bundle note) is fixed.

### 2. Apply the delegation test
Per [capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/capabilities.md)
§Subagents: the work qualifies when its returned summary is much smaller than the work
itself, when slices run in parallel, or when its tool set must be narrower than the
conversation's. Work that fails the test is a command or an inline step — say so and route
to `/quenching:components:command:new` instead of minting a wrapper around nothing. **Done when:** the delegation
buy is stated in one line, or the request is rerouted.

### 3. Derive the name, check collisions
Kebab-case identity naming what the agent *is* (`migration-verifier`), never `helper`.
`Glob` `.claude/agents/*.md`: an existing path is a MERGE target (edit), never silently
overwritten. **Done when:** the path is fixed, collision-free or resolved as an edit.

### 4. Draft from the mold
Fill `automation/agent.md`: a description carrying the work **and the timing** ("after X is
modified", "when asked to audit Y") within the caps; `tools` at the narrowest set;
`model`/`effort` per the pinning rules (mechanical extraction may run cheap — judgment never
downgrades; a pin here is cache-safe); `spawned-agents`, `skills`, `memory` only with a
stated reason. The body is a **system prompt in second person**. Inspection work takes the
verifier shape: numbered check areas, a "not checked here" list, if-present guards, a fixed
report format — and it never edits. **Done when:** the draft passes
[capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/capabilities.md)
§Subagents read top to bottom.

### 5. Present ONE plan → gate on the OK
Show: the delegation buy, the name, the profile fields with reasons, every file (the
definition, the rule if planned, the log), and the tail steps. Wait for the single
confirmation. **Done when:** the user has answered; declined → report "nothing written" and
stop.

### 6. Write
Write the definition (and the rule if planned). **Done when:** every planned file exists
with its planned content.

### 7. OKF tail (bundle present)
The registry's GENERATED zone lists commands only — offer ONE line in its **curated prose**
pointing at the agent surface, and a `glossary.md` entry if the agent coined a term;
the user decides both. **Done when:** each offer is answered.

### 8. Self-check
```bash
cq components doctor --json   # the definition carries a description — no sk-agent-no-description
```
Then read the definition against the contract by eye: tools scoped, voice second-person, a
verifier states it never edits. Report what was written and the always-on cost the
description adds. **Done when:** `doctor` reports no `sk-agent-*` finding for this file and
the report states the description's parsed character count.

## Invariants

- Never write before the single OK; a declined plan leaves the repo untouched.
- Never delete an agent, and never clobber an existing body — MERGE.
- Never leave `tools` unstated by accident — omitting it grants everything, and the plan
  says so when that is the choice.
- Never mint a verifier that edits; findings re-enter through the command that owns
  authoring.
- Never hand this command file `context: fork` — the plan gate is mid-flow.
