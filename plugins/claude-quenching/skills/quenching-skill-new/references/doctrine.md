# The skill-writing doctrine

How a `SKILL.md` earns its place in a target repo's context. `quenching-skill-new` applies this
doctrine to every skill it mints or edits; `quenching-skill-align` cites it when judging
conformance gaps. Adapted from mattpocock/skills' `writing-great-skills`, folded into this
plugin's own constraints (the description cap, the references/ pattern, the plan → OK gate).

## Predictability is the root virtue

A skill is a promise: the `name` + `description` are always in context, the body only loads
when the skill fires. The reader — human or agent — must be able to predict from the
description alone **when the skill fires and what will exist when it finishes**. Every other
rule below serves that one property:

- The description **front-loads the leading concept** — the first sentence says what the
  skill does and to what, in the skill's own vocabulary, before any qualifier.
- **One trigger per distinct branch.** Each distinct way a user asks for the job gets one
  verbatim quoted trigger phrase ("create a skill", "wire a command for this"); a branch
  without a trigger is a branch that never fires, and two triggers for the same branch are
  sediment. Triggers sit in the **second** sentence so a truncated description keeps them.
- The description ends with the boundary: `Not for: <adjacent job> → <owning skill>` — the
  routing story lives in the description, not in a shared router doc.

## The loading hierarchy

Doctrine flows downhill; context is paid at each level, so each fact sits at the **lowest**
level that still reaches it in time:

1. **In-skill steps** — the numbered workflow. Only what every run needs, in execution
   order. This is the most expensive real estate: it loads on every invocation.
2. **In-skill reference** — sections after the workflow (`## Special cases`,
   `## Invariants`) consulted when a step points at them.
3. **`references/*.md`** — doctrine, tables, and formats loaded only when a step reads
   them. Shared procedure lives **once**, in its owning skill's `references/`; every other
   skill cites the owner's file and never restates it (restatement is how copies drift).

## Steps carry checkable completion criteria

A step is done when a stated condition is observable — a file exists, a diff is empty, a
command exits 0, a table matches disk. "Handle the edge cases" is not a step; "the
GENERATED zone diffs clean against `.claude/skills/`" is. A skill whose last step has a
checkable criterion cannot end early and call itself done — that is the guard against
premature conclusion.

## The no-op test

For every line, name an input on which the agent behaves **differently** because the line
exists. A line with no such input — restated context, praise for the approach, a rule
already enforced by a stricter rule — is a no-op: delete it. Apply the test on every mint
**and every edit**; a skill body only grows when new behavior arrives, and prose that stopped
changing behavior leaves with the edit that obsoleted it.

## Positive prescription

State the target behavior, not the prohibition: "name the file after the folder path" beats
"don't use arbitrary names" — a prohibition leaves the agent choosing among everything not
forbidden, which is the opposite of predictability. Negation is reserved for **hard
invariants** whose violation is irreversible or costly (a deletion, a clobber, an unguarded
write), stated once, with the consequence attached.

## Named failure modes

Judge a draft (and an existing skill under review) against these six; each has a named cure:

| Failure mode | Smell | Cure |
| --- | --- | --- |
| **Premature conclusion** | The skill can claim "done" while work remains | End-state criteria per step; a final self-check step that diffs the promise against disk |
| **Duplication** | Procedure restated from another skill or doc | Cite the owner's `references/` file; one owner per fact |
| **Sediment** | Lines surviving edits that no longer change behavior | Re-run the no-op test on every edit; delete with the edit that obsoleted them |
| **Sprawl** | Body creeping toward the context it was meant to save | Push doctrine down the hierarchy; body stays well under 500 lines; description within the per-skill cap |
| **No-op** | A line no input can distinguish from its absence | The no-op test, at mint and at every edit |
| **Negation** | Rules phrased as prohibitions with no stated target | Rewrite positively; keep negation only for hard invariants with consequences |
