# Dimension 12 · Boundary doctrine

The boundary doctrine is the rule that **separates every other artifact** — map vs.
current standard vs. vision vs. ADR vs. description — so that each piece of
information has exactly **one home**. It is transversal: it doesn't add a file, it governs
where every other file's content belongs.

> **Canonical home — transversal · proposes only.** This is the method's core judgement,
> not an installable artifact. See [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

This is the dimension the whole method exists to enforce. The single most reliable way to
corrupt an agent's knowledge base is to write the same fact in two places: they drift, and
the agent gets contradictory context with no way to tell which is current. The classic
software answer is **single source of truth / DRY**; the documentation answer is
**Diátaxis**, which separates knowledge by purpose — reference, explanation, how-to,
orientation — precisely so a reader (or agent) always knows which home to trust
([Diátaxis](https://diataxis.fr/)). Context-engineering research makes the same point from
the agent side: duplicated, overlapping context is a primary driver of degraded responses
([Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

The method turns this into a **verifiable test**: *if an artifact serves two different
purposes, it has two homes, not one.* Classify each artifact into a single Diátaxis type —
CLAUDE.md is a map, a standard is current reference, an ADR is explanation, the backlog is
how-to, the vision is direction — and anything that has migrated quadrant (rationale piling
up in CLAUDE.md, a standard living in an ADR, the vision becoming a task list) is a boundary
violation to repair.

## What "good" looks like

- The boundary is **declared and consistent** across the root CLAUDE.md, the standards
  index, and the domain doctrine — all three say the same thing.
- No fact is duplicated across two artifacts; cross-references are **links**, not copies.
- Each artifact passes the **quadrant test** — it serves one purpose.

## How it drifts

- **Same fact in two places**, and diverging.
- **Cross-quadrant artifact** — a current standard inside a `vision/` or ADR (or vice
  versa); a guardrail copied into CLAUDE.md instead of linked.
- **Boundary table present in one artifact and absent/divergent in the others.**

## How the method closes the gap

It chooses the canonical home by quadrant, leaves only a link in the others, and
**proposes** the rearrangement — it never rewrites the content itself. This is the one
structural dimension with **no payload**: confronting the artifacts against each other *is*
the method's exclusive value; the actual moves are carried out by the writing skills
(`quenching-docs`). See [Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Diátaxis — A systematic framework for technical documentation](https://diataxis.fr/) — accessed 2026-06-28
- [The Divio Documentation System](https://docs.divio.com/documentation-system/) — accessed 2026-06-28
- [Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic · accessed 2026-06-28
