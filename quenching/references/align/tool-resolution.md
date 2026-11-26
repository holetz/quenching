# Resolving the quenching tool

Front-neutral: every command body shells out to the same single entry point, `cq`, naming its
front as the first argument. The fronts are `specs`, `git`, `knowledge`, `components`, `design`,
`ops`, `proof`, `toolchain`, `delivery`, and `security`; all resolve it the same way.

## Resolving the tool

**Source spelling: bare `cq …`.** Every command body and reference in the source writes
`.agents/quenching/bin/cq specs …`, never a path and never `python3 …/cq`; `cq deploy` rewrites each call to the
target-local launcher it installs (below).

A body that runs `cq` declares `Bash(cq:*)` in its `allowed-tools`, which the deploy rewrites the
same way; without it the call prompts (or is denied in a never-prompt session). A body must not
widen it to `Bash(python3:*)` to reach the tool.

The command is followed by the front and its subcommand: `.agents/quenching/bin/cq specs ...`, `.agents/quenching/bin/cq git ...`,
`.agents/quenching/bin/cq knowledge ...`, `.agents/quenching/bin/cq components ...`, `.agents/quenching/bin/cq design ...`, `.agents/quenching/bin/cq ops ...`, `.agents/quenching/bin/cq proof ...`,
`.agents/quenching/bin/cq toolchain ...`, `.agents/quenching/bin/cq delivery ...` and `.agents/quenching/bin/cq security ...`. **There is no second form and no third
rung**: never look for a copy under a target's `.claude/hooks/`, never install one there, never
merge anything into a target's `.claude/settings.json` to make a tool resolve.

Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json` payload, never on
prose.

**With the `quenching` MCP server connected, a body must call the tool, never the shell.** One
long-lived process keeps the store read, where each shell call starts a Python (0.58 s against
0.024 s measured on `specs status`).

### Citing a verb in a body: the tool, with named arguments

The server publishes **one tool per pillar and class** — `<pillar>_read`, `<pillar>_write`,
`<pillar>_external` — and the verb is its first argument. A body cites the verb **as the call it
makes**: the published tool, unprefixed, `verb` first, then the arguments named as that verb's
schema names them — `specs_read(verb="status", spec=<id>)`,
`specs_read(verb="section", spec=<id>, headings="Design,Tasks")`,
`components_read(verb="read", path="<ref>", sections=["§A", "§B"], rules_only=true)`,
`specs_write(verb="record", spec=<id>, name="run", fields={"state": "<STATE>", "date": "<today>"})`.
The verb is the logical name minus its pillar (the logical `git_pr_merge` is `git_external(verb="pr_merge")`);
the class is the verb's: `read` changes nothing, `write` changes the repository or the spec store,
`external` reaches a remote. Values are a `<placeholder>`, a quoted string, `true`, a list `[…]` or
an object `{…}`. A mention that calls nothing still names the call: `` `specs_read(verb="status")` ``.
The harness adds its prefix — Claude Code calls `mcp__quenching__<tool>`, OpenCode
`quenching_<tool>` — and the body never writes it. `--json` is the server's and is never written.
A call that acts on a tree other than the server's workspace — a worktree, a target repository —
names it as `root`, which every verb takes: `git_write(verb="commit", subject="<subject>",
root="<worktree>")`, `delivery_read(verb="status", root="<target root>")`. Several spec sections go
in ONE `specs_write(verb="section_write", spec=<id>, sections=[{"heading": …, "body": …}, …])`,
atomic as the CLI's stream, and an `approved` the human did not decide carries its `by`:
`specs_write(verb="record", spec=<id>, name="approved", by="session")`.

`verb="help"` answers the verbs of one tool and their schemas (`of=<verb>` narrows it to one); a
call with a bad argument is refused with the `inputSchema` of that verb, and an unknown verb with
`mcp-unknown-verb` and the tool's verbs. `cq deploy` grants each agent and skill the published
tools its `Bash(cq …)` grants reach: a grant of one verb opens its pillar-and-class tool, so the
other verbs of that class come with it — never another pillar, never another class, and a read-only
agent stays read-only.

`cq components lint` holds the form: `sk-cq-cli-citation` names a `cq <pillar> <verb>` whose verb
has a tool, in a body the check enforces; `sk-mcp-unknown-tool` names a `<pillar>_<…>(` that is no
published tool, a published tool whose first argument names no verb it serves, or a per-verb name
(`` `git_state(` ``), with the grouped form to cite instead.

### Where a body still writes the CLI

1. **The verb has no tool**: the exceptions of `mcp/coverage.py` (`cq deploy`, `cq modules`,
   `cq specs migrate`, `cq specs export`, `cq specs serve`, `cq specs delegate`,
   `cq specs claim take`, …) and any verb the server's `tools/list` does not name.
2. **A line marked `cli: <reason>`** — `<!-- cli: <reason> -->` at the end of the line, or alone on
   the line before a block (it then covers that whole paragraph or fenced block), and
   `# cli: <reason>` at the end of a line inside a fenced block. The reasons are closed:
   - **flag** — the call needs a flag the tool does not publish (`specs_read(verb="next")` no `table`,
     `specs_write(verb="promote")` no `force`).
   - **fallback** — the block documents the CLI synopsis itself, beside the tool it falls back
     from (a surface table such as `specs-develop/specs-surface.md`).

### The fallback: a session with no server

With no `quenching` server, or a verb the server does not list, the call runs `cq` as below and
**the run's report says so** — `MCP: fallback cq <pillar> <verb> — <no tool | no server>` — so a
fallback is never silent. The call maps back mechanically: `<pillar>_<class>(verb="<verb…>", …)` is
`cq <pillar> <verb…>` (the class drops; each `_` of the verb a word break, `-` inside a word:
`knowledge_read(verb="site_source")` is `cq knowledge site-source`, `cq <pillar> --help` settles a
doubt), and each other argument is the flag of the same name with `_` read as `-`
(`rules_only=true` is `--rules-only`, a list repeats the flag).
The hand-written specs tools name their arguments apart from the CLI:

| Tool | CLI |
| --- | --- |
| `specs_read(verb="status", spec=X)`, `specs_read(verb="show", spec=X, tasks=[T])` | `cq specs status --spec X`, `cq specs show --spec X --task T` |
| `specs_read(verb="section", spec=X, headings=H, moment=M, scope=S)` | `cq specs section X "H"` / `--moment M --scope S` |
| `specs_write(verb="section_write", spec=X, heading=H, body=B)` | `cq specs section X "H" --write` with `B` on stdin |
| `specs_write(verb="record", spec=X, name=N, fields={"k": "v"})` | `cq specs record X N --set k=v` |
| `specs_write(verb="task", spec=X, action=A, task=T, reason=R, subject=S, commit=C, replaced_by=P)` | `cq specs task --spec X --check T --subject S --commit C` (`A` is the flag: `--check`, `--uncheck`, `--block` or `--descope`, the last two with `--reason R`; `--descope` may add `--replaced-by P`) |
| `specs_write(verb="discover", spec=X, text=F)` | `cq specs discover X "F"` |
| `specs_write(verb="create", name=N, title=T, …)` | `cq specs new N --title T …` |
| `specs_read(verb="list", phase=P)`, `specs_read(verb="next", spec=X)`, `specs_read(verb="next")` | `cq specs list --phase P`, `cq specs next --spec X`, `cq specs next --front` |
| `specs_write(verb="promote", spec=X, to=P, outcome=O)` | `cq specs promote X --to P --outcome O` |
| `specs_write(verb="link_add", epic=E, spec=X, after=A)`, `specs_read(verb="epic_progress", epic=E)` | `cq specs link add E X --after A`, `cq specs status --spec E` |
| `specs_external(verb="push")` | `cq specs push` |

### Deploy mode: the target-local payload

quenching reaches a repository only through `cq deploy`. The target carries the tool at
`.agents/quenching/bin/cq`, and its command bodies call that literal target-local path; the
generated grant is `Bash(.agents/quenching/bin/cq:*)`. This is a **generated** copy owned by
`.agents/.quenching-deploy.json`, never a hand-installed third rung: upgrade it with
`cq deploy --write` from a new release, and never copy a `cq` into `.claude/hooks/` or edit the
user's `PATH`. The reference `.agents/quenching/bin/cq components read` remains the same; the local payload carries the
shared references under `.agents/quenching/references/`.

### Modules: one `cq`, the fronts of the deployed modules

The surface is cut into modules (`quenching-specs`, `quenching-align`, `quenching-design`, …), and
`cq deploy --modules` decides which a target carries; the one `cq` reaches the packages of every
**deployed** module. A front whose module is not deployed answers **exit 2** naming the module,
never a traceback. `cq modules --json` lists every module with `enabled: true|false`.

### Routing into another module

A route into a command of another module — a `Skill` call, an offer, a `Not for:` hand-off — runs
only when that module is deployed. Read `cq modules --json` once, where the route is about to be
taken: an enabled owner gets the route as written; an absent one is reported as
`not-installed: <module>` and the step continues without it (an offer is dropped, a stage is
skipped and named in the report). Never invoke a `Skill` whose module is absent, and never
manufacture the command it would have run.

### Working on the quenching repository itself

This repository deploys its own surface, so `.agents/quenching/bin/cq` runs the copy last deployed
rather than the code being written. When editing this repository, run the checkout's own file
explicitly — `python3 quenching/assets/bin/cq …` — as the author's check. That is a
developer invocation, never something a command body or reference writes for a target.

### `.agents/quenching` in the source

The source spells its own payload root `.agents/quenching`; `cq deploy` substitutes the
target-local `.agents/quenching/` for it. **A shell has no such variable**: the same spelling
reached any other way expands to nothing. Anything executable the payload ships locates itself
from its own `__file__`, never from `.agents/quenching`.

### Write the resolved path literally on every invocation

Never hold an interpreter plus a path in a shell variable and expand it as a command — zsh does not
word-split scalars. Write `cq` on each call. **Chain several writes so a failure stops the run** —
`set -e`, or `&&` between them:

```bash
set -e
.agents/quenching/bin/cq specs section my-spec "Proposal" --write <<'EOF'
…
EOF
.agents/quenching/bin/cq specs validate --spec my-spec --json
```
