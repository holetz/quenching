# `standards/agents/`

**How we instruct agents** — what this repo's always-on surface declares to whoever reads it at
session start: the language its prose is written in, and the conduct expected of the agent writing
it. Not the definition of an agent, and not the machinery that runs one.

**Boundary:** `agents/` governs the *instructions* a repo gives an agent — what holds in every
task, whichever tool is driving. Where a repo also keeps a subject for its own automation surface
(how a command, hook or agent definition is classified and authored), that surface is a different
subject and this one never restates it. Naming lives in [../naming/](../naming/index.md); the
shape of the system in [../architecture/](../architecture/index.md). One standard per file (files,
not sub-folders); each carries `type: standard` + a derived `resource:`; add each to
[../index.md](../index.md).

## Current docs

| Doc | Covers |
| --- | --- |
| [communication.md](communication.md) | The language a repo declares for the prose its agents author — one BCP-47 tag on the root harness line, governing artifact and conversation alike — and the conduct contract that holds in every repo whether or not a language is declared |

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`communication`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- [communication.md](communication.md) — the declared language and the conduct constant (present)
