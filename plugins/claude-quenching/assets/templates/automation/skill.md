---
name: <skill-name — domain-bound: <flattened-folder-path>-<verb>; generic: <verb-object>>
description: >-
  <Leading concept first: what this skill does and to what, in one sentence, before any
  qualifier.> Use when the user asks to "<trigger 1>", "<trigger 2>", or "<one verbatim
  trigger per distinct branch — a branch without a trigger never fires>". <One sentence on
  what exists when it finishes: files written, zones regenerated, checks run.> Not for:
  <adjacent job> → <owning skill>.
when_to_use: >-
  <the job this skill is for, in one clause. It may add a relation the description does not
  state; it may NOT restate the `Not for:` boundary — that is the same routing paid for twice
  inside one always-on budget.>
allowed-tools: <only the tools the steps actually use, each SCOPED — e.g. Read, Grep, Glob,
  Write, Edit, Bash(python3:*), Bash(git status:*). A bare `Bash` grants the whole shell for
  the turn and is reported as `sk-unscoped-bash`; it is legitimate only for a skill running the
  TARGET repo's own toolchain, whose body says so and says why. `${CLAUDE_SKILL_DIR}` resolves
  to this skill's directory inside a scope, e.g. Bash(python3 ${CLAUDE_SKILL_DIR}/bin/x.py:*).>
user-invocable: <false for a skill reached through a command wrapper — it hides the / menu
  entry and does NOT block programmatic invocation. Omit for a skill a human picks by name.>
# disable-model-invocation: <true is the ONLY field that blocks programmatic invocation. Use it
#   for a skill whose cost or blast radius means a human must choose it. Setting it together
#   with `user-invocable: false` leaves NO caller — that is `sk-unreachable`, an error.>
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
     VERIFY IT, don't eyeball it: `skills.py lint <this-skill-folder> --json` decides every
     mechanical rule and names each gap by a stable `sk-*` code; `skills.py doctor --json`
     decides the bijection. Thresholds live in `docs/standards/automation/skills.md` and
     `docs/standards/automation/context-budget.md` — this mold never restates a number.

     What lint checks (fix an `error`, report a `warn` by its code):
       • the two caps — description + when_to_use (`sk-metadata-cap`, error) and description
         alone (`sk-description-portable`), both counted on the PARSED value, never the YAML
         source lines.
       • triggers in the SECOND sentence (`sk-trigger-position`), so truncation never eats them.
       • the `Not for:` boundary present (`sk-no-boundary`).
       • body length (`sk-body-length`) — on-demand doctrine goes to references/ files.
       • a `**Done when:**` criterion per numbered step (`sk-step-criterion`) — that literal
         marker is what the tool counts.
       • scoped tool grants (`sk-unscoped-bash`) and coherent invocation control
         (`sk-unreachable`, `sk-invocation-value`).

     What no tool checks — the reason the doctrine still gets read:
       • every line passes the no-op test (name an input the line changes; else delete it);
         prescriptions are positive; negation is reserved for hard invariants.
       • a domain-bound skill is mirrored by a thin wrapper at
         `.claude/commands/<folder-path>/<verb>.md` (mold: automation/command.md); a
         generic skill is never mirrored.
       • never `context: fork` on a skill that gates on a mid-flow confirmation — a forked
         context cannot present the plan whose OK the run depends on. -->
