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

## Current docs

| Doc | Covers |
| --- | --- |
| [communication.md](communication.md) | The two language bands an agent writes in — durable artifacts in canonical English so they stay portable and greppable across repos, conversation in the one BCP-47 tag the root harness line declares — and the conduct contract that holds whether or not a language is declared |
| [ephemeral-writes.md](ephemeral-writes.md) | Where an agent puts a file it creates — the three destinations, the one question that sorts them, and the session-start declaration that makes the durable-ignored path present before the first write |

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`communication` · `ephemeral-writes`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- [communication.md](communication.md) — the declared language and the conduct constant (present).
- [ephemeral-writes.md](ephemeral-writes.md) — the three write destinations and the sorting question (present).
