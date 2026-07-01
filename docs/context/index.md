# Why the harness is the work

You installed this method to *organize a repo's knowledge*. Before the how, the
why — because the why is not obvious, and it is changing fast.

The short version: **the model is no longer the hard part.** The hard part is
everything you put *around* the model. That surrounding structure has a name —
the **harness** — and getting it right is most of the job. This method is a way
to engineer one specific harness: the knowledge a Claude Code agent loads about
*your* repository.

This page makes that case, grounded in a recent industry survey; the
[next page](knowledge-surface.md) turns the abstract harness into the concrete
files in your repo and shows how they rot. Together they are the *context*
movement — the problem, in depth — before the [Technical guide](../plugin/install.md)
shows you how to run the tool against it.

!!! quote "The grounding source"
    Addy Osmani, Shubham Saboo & Sokratis Kartakis, **"The New SDLC With Vibe
    Coding — From ad-hoc prompting to Agentic Engineering,"** Google, May 2026.
    Page citations below refer to this report.

## From writing code to expressing intent

The report opens on a shift it calls profound: development is moving *from writing
code to expressing intent* (p6–8). The numbers it cites for early 2026 are no
longer fringe — **85% of professional developers use AI coding agents, 51% daily,
and 41% of new code is AI-generated.** When the machine writes the code, the
scarce skill is no longer producing syntax; it is stating *what you want* clearly
enough that the machine produces the right thing.

That reframes the whole activity. If the agent can write the code, the leverage
moves to whatever shapes *how* it writes it — the instructions it reads, the
examples it sees, the guardrails it must respect. None of that is the model. All
of it is the harness.

## Agent = Model + Harness

The report's central equation is blunt (p26–31):

> **Agent = Model + Harness.** The model is the engine. The harness is the car,
> the road, and the traffic laws.

And the split is lopsided — the report puts it at roughly **harness ≈ 90% /
model ≈ 10%** (Fig. 7). The harness is *everything that surrounds the model*:
rule files (CLAUDE.md and its kin), tools and MCP servers, sandboxes,
orchestration logic, guardrails and hooks — *"things the agent should never
forget but often does"* — and observability. Crucially, the report notes this is
*"the team's surface area, not the model provider's."* You do not get to tune the
model. You own the harness entirely.

The consequence lands as the report's sharpest line:

> **"Most agent failures, examined honestly, are configuration failures."**

It backs this with a benchmark result: one team moved an agent from *outside the
Top 30 to Top 5 on Terminal Bench 2.0 by changing only the harness* — same model,
different surrounding structure. The spectrum from ad-hoc *vibe coding* to
deliberate *agentic engineering*, the report says, "is defined by how deliberately
you configure and apply the harness" (p8, p31), not by which tool or model you
picked.

## Context engineering — and the static/dynamic boundary

Zoom into the harness and the report names the real skill inside it: **context
engineering** (p15–18). Output quality, it argues, "depends less on the cleverness
of your prompts and more on the quality of the *context*." It sorts context into
six types — **Instructions, Knowledge, Memory, Examples, Tools, Guardrails** — and
draws one distinction that this method leans on heavily:

- **Static context** — CLAUDE.md / AGENTS.md / GEMINI.md, global memory, core
  guardrails — is *"expensive because every token is present in every
  interaction."* It is loaded before you say a word, and it costs that budget on
  every single turn, forever.
- **Dynamic context** — skills, tool results, retrieval, windowed history — is
  paid *"only when needed."* It stays out of the way until something calls it in.

The report's prescription is the design principle this whole method is built to
serve:

> "The best systems treat this boundary as a first-class architectural decision,
> **reviewed and versioned like any other configuration.**"

It singles out **Agent Skills** as the mechanism for dynamic context: portable
procedural knowledge delivered by **progressive disclosure**, which solves
*context rot from overloaded prompts, the absence of procedural memory,
multi-agent overhead, and the need for portability*. The question it says every
team must answer is exactly the one this method operationalizes: *"What would a new
team member need to know … and how do I encode that knowledge in a form the AI can
use?"*

## The economics — why this is worth doing

The report frames the payoff as capital structure (p39–42). Ad-hoc vibe coding is
**low CapEx, high OpEx**: cheap to start, but every under-specified session pays
interest in re-explanation, wrong turns, and hidden debt. Agentic engineering
inverts it — **high CapEx, low OpEx**: you invest up front in the harness, and
every later interaction runs cheaper because the context is already there and
correct. Context engineering, in this framing, is a *financial lever*, not a
tidiness exercise.

## The turn: this harness lives in your repo — and it rots

Here is where the report meets this method. Its abstract "harness" is not
abstract at all in a codebase: it *is* the repository's **knowledge surface** —
the CLAUDE.md an agent loads, the docs it reads, the skills and hooks it runs, the
boundaries that keep each fact in one place. The report's harness components and
its six context types map almost one-for-one onto the **15 dimensions** this method
audits. Static-vs-dynamic is simply CLAUDE.md (always loaded, costs budget forever)
versus docs and skills (on-demand, progressive disclosure) — which is the exact
line the dimension pages teach. (The working directory of this very project is
named `harness-gestao` — *harness management* — which is not a coincidence.)

In the report's own vocabulary, **claude-quenching is a method for engineering the
harness.** But a harness is not built once. It is a living surface, and left alone
it decays — as the code moves under it, as models improve past the workarounds you
wrote, as the team changes. That decay has a name too, *context rot*, and it is the
subject of the [next page](knowledge-surface.md): the knowledge surface, dimension
by dimension, and how it rots.
