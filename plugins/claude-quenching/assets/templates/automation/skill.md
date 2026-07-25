---
name: <skill-name — domain-bound: <flattened-folder-path>-<verb>; generic: <verb-object>>
description: >-
  <Leading concept first: what this skill does and to what, in one sentence, before any
  qualifier.> Use when the user asks to "<trigger 1>", "<trigger 2>", or "<one verbatim
  trigger per distinct branch — a branch without a trigger never fires>". <One sentence on
  what exists when it finishes: files written, zones regenerated, checks run.> Not for:
  <adjacent job> → <owning skill>.
allowed-tools: <only the tools the steps actually use — e.g. Read, Grep, Glob, Write, Edit>
---

# <skill-name> — <one-line role>

<Context paragraph: where the skill acts (the bound folder for a domain-bound skill), what
it assumes exists, and which references/ or sibling docs it cites instead of restating.>

## Workflow

### 1. <Step name>
<What to do. **Done when:** <a checkable, observable condition — a file exists, a diff is
empty, a command exits 0>.>

### 2. <Step name>
<...each step ends with its own **Done when:** criterion...>

### N. Self-check
<Diff the result against the description's promise: everything the description says will
exist, exists; every step's criterion held. Report what was written.>

<!-- MOLD (claude-quenching · automation skill) → becomes `.claude/skills/<skill-name>/SKILL.md`
     in a target repo, minted by `quenching-skill-new` under the taxonomy rule
     (`docs/standards/automation/skills.md`) and the writing doctrine (predictability as
     the root virtue; the plugin's `quenching-skill-new/references/doctrine.md` is the owner).
     Discipline the mint enforces — keep it when editing by hand:
       • description caps at the per-skill limit (Claude Code truncates description +
         when_to_use at 1,536 combined chars) with triggers in the SECOND sentence, so
         truncation never eats them.
       • every line passes the no-op test (name an input the line changes; else delete it);
         prescriptions are positive; negation is reserved for hard invariants.
       • body stays well under 500 lines — on-demand doctrine goes to references/ files.
       • a domain-bound skill is mirrored by a thin wrapper at
         `.claude/commands/<folder-path>/<verb>.md` (mold: automation/command.md); a
         generic skill is never mirrored.
       • never `context: fork` on a skill that gates on a mid-flow confirmation. -->
