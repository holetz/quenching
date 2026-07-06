# The knowledge surface & how it rots

The [previous page](index.md) argued that the harness — everything around the
model — is where the work is, and that in a repository the harness *is* the
knowledge surface. This page makes that concrete: the actual files that make up
the surface, why it decays, and the one rule that keeps it coherent. It is the
bridge from the abstract case to the [15-dimension anatomy](../method/dimensions/index.md)
that follows.

## The abstract harness, made of files

The report's harness is a list of component *types* — rule files, tools,
guardrails, orchestration, observability. In a Claude Code repository each type
lands in a specific, inspectable place:

| The harness component | Where it lives in a repo |
| --- | --- |
| Rule file / always-on instructions | `CLAUDE.md` (the always-loaded entry map) |
| Knowledge | `docs/` — standards, vision, backlog, decisions, the domain catalog |
| Procedural knowledge (dynamic) | Skills |
| Isolated workers / orchestration | Sub-agents |
| Guardrails (deterministic) | Hooks + the `scripts/` they call |
| Repeatable steps | Commands |
| Memory | Auto-memory + what CLAUDE.md pins |
| Tools / external reach | MCP (`.mcp.json`) |
| The rule that binds them | Boundary doctrine · conventions |

That is the whole surface. It is not a metaphor an agent reasons about — it is a
set of files an agent *loads*, and every one of them is yours to get right or get
wrong. The method's job is to look at each of these and ask: is it present, is it
current, and does it earn its place?

## Static vs. dynamic — the budget that never resets

The single most important line running through the whole surface is the
[static/dynamic boundary](index.md#context-engineering-and-the-staticdynamic-boundary)
the report insists teams version deliberately.

- **`CLAUDE.md` is static.** It enters context before the first message, so every
  token in it is paid on *every* interaction, forever. A bloated CLAUDE.md is not
  just untidy — it is a standing tax on every turn the agent ever takes.
- **`docs/` and skills are dynamic.** They sit dormant and cost nothing until a
  trigger or a link pulls the relevant piece in — *progressive disclosure*. This is
  why the method pushes detail *out* of CLAUDE.md and *into* linked docs and
  trigger-routed skills: the same knowledge, moved from the always-paid column to
  the pay-per-use column.

Read the surface through this lens and most "knowledge base" problems resolve into
one question: *is this fact in the right budget column?* An always-loaded rule that
only matters once a quarter belongs in a doc. A procedure re-explained in three
prompts belongs in a skill.

## How the surface rots

A surface that is perfect today is not perfect for long, because everything it
describes is moving. *Context rot* is the accumulation of that drift:

- **The code moves out from under the docs.** A path, a command, or an invariant
  changes; the CLAUDE.md line describing it does not. The agent now reads a
  confident, wrong instruction — worse than no instruction.
- **The model improves past your workarounds.** Much of a harness is written to
  compensate for a model's weaknesses. When the model gets better, a skill or rule
  that used to earn its keep becomes pure overhead — a token cost that buys nothing.
  (This is why the method revisits the base *on model release*, not just on code
  change.)
- **The team changes and duplicates.** The same fact gets written in CLAUDE.md,
  again in a doc, again in a skill. Now they disagree, and no one knows which is
  canonical. Duplication is the most common way a surface silently goes stale.

Rot is not failure of the surface — it is the *normal* state of any living
configuration. The report's answer is to treat the surface like code: reviewed and
versioned, with a maintenance loop, not a one-time cleanup. The method's Step 8
installs exactly that loop; the workflow's
[Scenario C](../plugin/workflow.md#scenario-c-repo-that-already-applied-maintenance-structure-evolution)
is the maintenance story in full.

## One home per fact — the organizing principle

If duplication is how the surface rots, then the antidote is a single rule, and it
is the doctrine the whole method is organized around: **one home per fact.** Every
piece of knowledge has exactly one canonical place; everything else *links* to it
rather than restating it. A path lives in one doc; a procedure lives in one skill;
an always-true rule lives in CLAUDE.md and nowhere else.

This is what makes the static/dynamic boundary enforceable. You cannot decide "this
fact is dynamic, load it on demand" if the fact is smeared across four files — you
have to know where it *lives*. One home per fact is the precondition for every other
decision the method makes, which is why it is called out as its own dimension
(boundary doctrine) and why the method only ever *proposes* changes to it — it is a
human judgment about where a fact belongs, not a mechanical move.

## Here is that surface, dimension by dimension

So the harness is a set of files; the files sit in two budget columns; they rot as
the code, models and team move; and one home per fact is what keeps them coherent
under that pressure. That is the problem, whole.

The rest of the *context* movement makes it precise. The method cuts the surface
into **15 dimensions**, each a distinct part of the harness with its own "what good
looks like" and its own way of drifting. The next page lays them out as an
anatomy — grouped into four layers — and every dimension gets its own page.

→ [The 15 dimensions](../method/dimensions/index.md)
