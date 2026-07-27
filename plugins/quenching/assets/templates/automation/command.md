---
description: >-
  <Leading concept first: what this command does and to what, in one sentence, before any
  qualifier.> Use when the user asks to "<trigger 1>", "<trigger 2>", or "<one verbatim
  trigger per distinct branch — a branch without a trigger never fires>". <One sentence on
  what exists when it finishes: files written, zones regenerated, checks run.> Not for:
  <adjacent job> → <owning command>.
argument-hint: [<the input this command accepts — e.g. subject, target file, options>]
allowed-tools: <only the tools the steps actually use, each SCOPED — e.g. Read, Grep, Glob,
  Write, Edit, Bash(python3:*), Bash(git status:*). A bare `Bash` grants the whole shell for
  the turn and is reported as `sk-unscoped-bash`; it is legitimate only for a command running
  the TARGET repo's own toolchain, whose body says so and says why.>
# effort: <low | medium — omit to inherit the session's. Set it only when the work is
#   genuinely cheaper or genuinely harder than the default.>
# disable-model-invocation: <true blocks programmatic invocation, so a conductor can no
#   longer reach this command by name and a spoken trigger can no longer route to it. Use it
#   only for a command whose cost or blast radius means a human must choose it.>
---

# /<front>:<verb> — <one-line role>

**Input**: `$ARGUMENTS` (<what the caller passes; say "none" if the command takes nothing>).

<Context paragraph: where the command acts (the bound folder for a domain-bound command),
what it assumes exists, and which bundled references or sibling docs it cites instead of
restating.>

## Workflow

### 1. <Step name>
<What to do. **Done when:** <a checkable, observable condition — a file exists, a diff is
empty, a command exits 0>.>

### 2. <Step name>
<...each step ends with its own **Done when:** criterion...>

### N. Self-check
<Diff the result against the description's promise: everything the description says will
exist, exists; every step's criterion held. Report what was written.>

<!-- MOLD (quenching · automation command) → becomes
     `.claude/commands/<folder-path>/<verb>.md` in a target repo, invocable as
     `/<folder>:<subfolder>:<verb>` — native `:` separator, one per path segment — and minted
     by `/skill:new` under the taxonomy rule (`docs/standards/automation/skills.md`) and the
     writing doctrine (predictability as the root virtue).

     ONE FILE PER ENTRY POINT. Claude Code merged custom commands into skills, so this file
     carries BOTH the description that routes to it and the body that runs. There is no
     `SKILL.md` half and no wrapper to mirror: the command's PATH is its whole identity, so
     nothing derives a second name to keep in step with it.

     THE PATH IS THE ONLY THING UNDER `commands/`. That tree is the only one Claude Code
     registers, so anything that is not an entry point — shared procedure, references,
     fixtures, eval cases — lives OUTSIDE it. A `references/` folder beside this file would
     register every reference as a phantom command like `/docs:align:references:conformance`.
     Cite shared procedure by absolute path instead; in a plugin that is
     `${CLAUDE_PLUGIN_ROOT}/assets/references/<name>/<file>.md`, which substitutes inside a
     command body.

     VERIFY IT, don't eyeball it: `skills.py lint <this-file> --json` decides every mechanical
     rule and names each gap by a stable `sk-*` code; `skills.py doctor --json` decides the
     surface-wide invariant (every command has a non-empty description, no two resolve to the
     same `/` path, every segment kebab-case). Thresholds live in
     `docs/standards/automation/skills.md` and `docs/standards/automation/context-budget.md` —
     this mold never restates a number.

     What lint checks (fix an `error`, report a `warn` by its code):
       • the two caps — the description against `sk-metadata-cap` (error) and against
         `sk-description-portable` (warn), both counted on the PARSED value, never the YAML
         source lines.
       • triggers in the SECOND sentence (`sk-trigger-position`), so truncation never eats them.
       • the `Not for:` boundary present (`sk-no-boundary`).
       • body length (`sk-body-length`) — on-demand doctrine goes to a bundled reference.
       • a `**Done when:**` criterion per numbered step (`sk-step-criterion`) — that literal
         marker is what the tool counts.
       • scoped tool grants (`sk-unscoped-bash`) and coherent invocation control
         (`sk-unreachable`, `sk-invocation-value`).

     What no tool checks — the reason the doctrine still gets read:
       • every line passes the no-op test (name an input the line changes; else delete it);
         prescriptions are positive; negation is reserved for hard invariants.
       • the description is the ONLY always-on text, and it is now the only one there is.
         Its triggers and its `Not for:` boundary are what route a spoken request here; a
         description trimmed to a `/`-menu label routes nothing.
       • never `context: fork` on a command that gates on a mid-flow confirmation — a forked
         context cannot present the plan whose OK the run depends on. -->
