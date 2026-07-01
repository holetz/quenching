# Dimension 14 · Guardrails

Guardrails are **how the LLM should behave when it codes** — think before coding, stay
simple and surgical, work to the goal. The dimension has two targets: the agent's behavior
in the repo, and the **quality of the executable artifacts** the surface exposes — hooks,
audit scripts, skill tools — which speak to the agent through their failure messages.

> **Canonical home — a guardrails skill cited by CLAUDE.md, plus enforcement hooks ·
> Adaptive.** The repo cites the skill (never copies it); enforcement globs are derived
> from the target. See [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

Two findings from Anthropic's tool-design work drive this dimension. First, **errors should
be actionable**: *you can prompt-engineer your error responses to communicate specific,
actionable improvements, instead of opaque error codes or tracebacks* — a failure message
that says *what is wrong and how to fix it* turns a blind retry loop into a self-correction
([Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)).
Second, **poka-yoke**: *change the arguments so it's harder to make a mistake* — the
canonical example is switching a relative path to an absolute one, which eliminates an entire
class of errors at the parameter level, before any message is needed
([Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)).

The third thread crosses into [hooks](08-hooks.md): where an invariant must hold,
**deterministic enforcement beats probabilistic guidance**. Prose in CLAUDE.md telling the
agent "never edit the generated file" is a guardrail the model can ignore; a `PreToolUse`
hook that blocks the edit with an actionable reason is one it cannot
([How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude)).

## What "good" looks like

- A guardrails skill present and **cited** (not copied) by the root CLAUDE.md.
- Every hook/script/tool the agent can trigger returns an **actionable** failure message,
  not a raw stack trace or bare exit code.
- Parameters are designed for **poka-yoke** (absolute over relative, enum over free string).
- Invariants that must hold are enforced by a blocking hook, not just guidance.

## How it drifts

- **Guardrail copied into CLAUDE.md prose** instead of linked; or absent in a repo that
  codes heavily.
- **Opaque error** — a hook/script that fails with a traceback or `exit 2` and no
  explanation, stranding the agent in a retry loop.
- **Error-prone parameter** — accepts an ambiguous format where a fixed one would make the
  mistake impossible.

## How the method closes the gap

It links the guardrails skill from CLAUDE.md, rewrites opaque failures into actionable ones,
and hardens parameters; where a generated artifact needs protection, it installs the
`protect-generated.py` enforcement hook. The payload is the `quenching-guardrails` skill plus
that hook — see [Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Writing effective tools for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents) — Anthropic · 2025-09-11
- [Introducing advanced tool use on the Claude Developer Platform — Anthropic Engineering](https://www.anthropic.com/engineering/advanced-tool-use) — Anthropic · accessed 2026-06-28
- [How we contain Claude across products — Anthropic Engineering](https://www.anthropic.com/engineering/how-we-contain-claude) — Anthropic · accessed 2026-06-28
