# The command-writing doctrine

How a command file earns its place in a target repo's context. `/skill:new` applies this
doctrine to every command it mints or edits; `/skill:align` cites it when judging
conformance gaps. Adapted from mattpocock/skills' `writing-great-skills`, folded into this
plugin's own constraints (the description caps, the bundled-reference pattern, the plan → OK
gate).

**One file, one description, and it is the only always-on text there is.** The collapse to one
file per entry point deleted the second description, not the second file only — so the triggers
and the `Not for:` boundary that used to live in a skill description now have nowhere else to
be. A description written as a `/`-menu label routes nothing.

**This file owns the judgement; the tool owns the thresholds.** Every number a rule below depends
on — the two description caps, the body line limit, trigger position, the `Not for:` boundary —
lives in `docs/standards/automation/context-budget.md` and `docs/standards/automation/skills.md`,
and is checked by `skills.py lint` under a stable `sk-*` code. This file names the code and never
restates the number, so the rule and its checker cannot drift apart.

| Doctrine rule | Checked by | Code |
| --- | --- | --- |
| Triggers in the second sentence | `lint` | `sk-trigger-position` |
| The `Not for:` boundary is present | `lint` | `sk-no-boundary` |
| The metadata fits Claude Code's cap | `lint` | `sk-metadata-cap` (error) |
| The description is portable | `lint` | `sk-description-portable` |
| The body stays under the size cap | `lint` | `sk-body-length` |
| Every numbered step has a criterion | `lint` | `sk-step-criterion` |
| `allowed-tools` is scoped | `lint` | `sk-unscoped-bash` |
| Invocation control is coherent | `lint` | `sk-unreachable`, `sk-invocation-value` |
| `context: fork` never beside a mid-flow gate | `lint` | `sk-fork-gate` (error) |
| `effort`/`context` values Claude Code can parse | `lint` | `sk-profile-value` |
| **The no-op test, sediment, sprawl, positive prescription** | **a reader** | — |
| **Every non-default lever carries a stated buy** | **a reader** | — |

The last row is the boundary. Each of those needs a claim about how an agent would *behave*, and
no parser makes one. They are why this file exists, and why a clean `lint` is a floor rather than
a verdict.

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

1. **In-body steps** — the numbered workflow. Only what every run needs, in execution
   order. This is the most expensive real estate: it loads on every invocation.
2. **In-body reference** — sections after the workflow (`## Special cases`,
   `## Invariants`) consulted when a step points at them.
3. **A bundled reference file** — doctrine, tables, and formats loaded only when a step reads
   them. It lives OUTSIDE `commands/`, because that tree is the only one Claude Code registers
   and a reference parked in it becomes a phantom command; cite it by absolute path
   (`${CLAUDE_PLUGIN_ROOT}/assets/references/<name>/<file>.md` in a plugin). Shared procedure
   lives **once**, in its owning file; every other command cites the owner and never restates
   it (restatement is how copies drift).

## Steps carry checkable completion criteria

A step is done when a stated condition is observable — a file exists, a diff is empty, a
command exits 0, a table matches disk. "Handle the edge cases" is not a step;
"`skills.py registry reindex` reports `changed: false`" is. Write the criterion as
`**Done when:** …` — that literal marker is what `lint` counts (`sk-step-criterion`). A skill
whose last step has a checkable criterion cannot end early and call itself done — that is the
guard against premature conclusion.

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

## The execution profile

The writing rules above govern what a command **says**; which capabilities it **uses** —
`context: fork`, a model or effort pin, a subagent, a hook, the invocation-surface controls,
dynamic context — is a second authored decision set with its own doctrine, owned by
[skill-new/capabilities.md](capabilities.md). The default profile is empty; every departure
is priced there and enters the mint's plan with its stated reason. A lever whose buy nobody
can state is the **sediment** failure mode wearing frontmatter.

## Named failure modes

Judge a draft (and an existing skill under review) against these six; each has a named cure:

| Failure mode | Smell | Cure |
| --- | --- | --- |
| **Premature conclusion** | The skill can claim "done" while work remains | End-state criteria per step; a final self-check step that diffs the promise against disk |
| **Duplication** | Procedure restated from another command or doc | Cite the owner's reference file by absolute path; one owner per fact |
| **Sediment** | Lines surviving edits that no longer change behavior | Re-run the no-op test on every edit; delete with the edit that obsoleted them |
| **Sprawl** | Body creeping toward the context it was meant to save | Push doctrine down the hierarchy; `lint` reports the caps (`sk-body-length`, `sk-metadata-cap`) — staying *well* under them is the judgement it cannot make |
| **No-op** | A line no input can distinguish from its absence | The no-op test, at mint and at every edit |
| **Negation** | Rules phrased as prohibitions with no stated target | Rewrite positively; keep negation only for hard invariants with consequences |
