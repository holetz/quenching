# `standards/agents/`

**How we instruct agents** — what this repo's always-on surface declares to whoever reads it at
session start: the language its prose is written in, and the conduct expected of the agent writing
it. Not the definition of an agent, and not the surface that carries one.

**Boundary:** `agents/` governs the *instructions* given to an agent — what holds in every task,
command or not. The plugin's own command surface, and how a command, hook or agent definition is
classified, authored and swept, lives in [../automation/](../automation/index.md) — including
[../automation/agents.md](../automation/agents.md), which despite the name is the definition
contract for `.claude/agents/` and not part of this subject. Naming lives in
[../naming/](../naming/index.md). One standard per file (files, not sub-folders); each carries
`type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`communication`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- _(none yet — fill on population)_
