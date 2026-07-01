# Dimension 6 · Skills

A skill is an **actionable capability** the agent reaches for by matching a request to the
skill's description. The description (plus when-to-use) is *routing code*, not prose — the
only text always visible to the model, and what it uses to pick the right skill among many.

> **Canonical home — `.claude/skills/<prefix>-<name>/` · Adaptive.** The thematic prefix
> and naming follow the repo's taxonomy; the method does not impose its own. See
> [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

Skills are the mechanism that makes **progressive disclosure** real: a capability's detail
stays out of context until its description matches, so the agent can carry hundreds of
skills without paying for them every turn
([Introducing Agent Skills](https://claude.com/blog/skills),
[Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)).
That only works if the **description is engineered as a trigger** — third person, specific,
naming the literal phrases a user would type and what distinguishes this skill from its
neighbors. Anthropic's skill-authoring guidance is explicit that a skill that works when
invoked by name but never fires on its own has a *description* bug, not an instruction bug
([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

The opposite failure is **bloat**. Every extra skill consumes routing context and adds
ambiguity; the healthy target is a *few powerful* skills, not many overlapping ones. The
method's test is sharp: *if an engineer can't say with certainty which skill applies, the
agent won't either* — and the fix for genuinely overlapping scopes is to **consolidate**,
not to multiply exclusion clauses ([Agent Skills Specification](https://agentskills.io/specification)).

## What "good" looks like

- A description in **third person** with what-it-does + when-to-use + literal user phrases,
  distinct from neighboring skills.
- `SKILL.md` under ~500 lines, detail pushed to `references/`; `name` = folder name.
- Side-effect skills (deploy/commit/send) carry `disable-model-invocation: true`.
- Each skill passes a **trigger test** — 3–5 requests that should fire it, 3–5 tricky ones
  that should not.

## How it drifts

- **Weak/vague description** ("helps with X") or written in first/second person.
- **Trigger collision** — two descriptions sharing keywords with no separating clause
  (latent false-trigger); fix with an exclusion clause.
- **Toolset bloat** — two skills whose scopes actually overlap; fix by merging.
- **Side-effect skill without `disable-model-invocation`.**
- **Recurring domain procedure (≥3×) with no skill** to capture it.

## How the method closes the gap

It sharpens descriptions, adds exclusion clauses, consolidates overlapping skills, and —
where a recurring domain need has no artifact — **proposes the skeleton** (name,
description-trigger, home, empty `references/`) while leaving the procedure content to the
repo. The payload is the `quenching-skills` skill plus a skill template — see
[Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Introducing Agent Skills — Claude Blog](https://claude.com/blog/skills) — Anthropic · 2025-10-16
- [Skill authoring best practices — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Anthropic · accessed 2026-06-28
- [Equipping agents for the real world with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — Anthropic · accessed 2026-06-28
- [Agent Skills Specification — agentskills.io](https://agentskills.io/specification) — accessed 2026-06-28
