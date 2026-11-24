# Resolving the quenching tool

Front-neutral: every command body shells out to the same single entry point, `cq`, naming its
front as the first argument. The fronts are `specs`, `git`, `knowledge`, `components`, `design`,
`ops`, `proof`, `toolchain`, `delivery`, `security` and `codex`; all resolve it the same way.

## Resolving the tool

**Source spelling: bare `cq …`.** Every command body and reference in the source writes
`.agents/quenching/bin/cq specs …`, never a path and never `python3 …/cq`; `cq deploy` rewrites each call to the
target-local launcher it installs (below).

A body that runs `cq` declares `Bash(cq:*)` in its `allowed-tools`, which the deploy rewrites the
same way; without it the call prompts (or is denied in a never-prompt session). A body must not
widen it to `Bash(python3:*)` to reach the tool.

The command is followed by the front and its subcommand: `.agents/quenching/bin/cq specs ...`, `.agents/quenching/bin/cq git ...`,
`.agents/quenching/bin/cq knowledge ...`, `.agents/quenching/bin/cq components ...`, `.agents/quenching/bin/cq design ...`, `.agents/quenching/bin/cq ops ...`, `.agents/quenching/bin/cq proof ...`,
`.agents/quenching/bin/cq toolchain ...`, `.agents/quenching/bin/cq delivery ...`, `.agents/quenching/bin/cq security ...`, `cq codex ...`. **There is no second form and no third
rung**: never look for a copy under a target's `.claude/hooks/`, never install one there, never
merge anything into a target's `.claude/settings.json` to make a tool resolve.

Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json` payload, never on
prose.

**With the `quenching` MCP server connected, a body must call the tool, never the shell.** One
long-lived process keeps the store read, where each shell call starts a Python (0.58 s against
0.024 s measured on `specs status`).

### Citing a verb in a body: the tool, with named arguments

A body cites the verb **as the tool it calls**: the canonical tool name, unprefixed, with the
arguments named as the tool's `inputSchema` names them —
`specs_status(spec=<id>)`, `specs_section(spec=<id>, headings="Design,Tasks")`,
`components_read(path="<ref>", sections=["§A", "§B"], rules_only=true)`,
`specs_record(spec=<id>, name="run", fields={"state": "<STATE>", "date": "<today>"})`. Values are a
`<placeholder>`, a quoted string, `true`, a list `[…]` or an object `{…}`. A mention that calls
nothing names the tool bare: `` `specs_status` ``. The harness adds its prefix — Claude Code calls
`mcp__quenching__<tool>`, OpenCode `quenching_<tool>` — and the body never writes it. `--root` and
`--json` are the server's and are never written. `cq deploy` grants each agent and skill exactly
the tools its `Bash(cq …)` grants cover.

`cq components lint` holds the form: `sk-cq-cli-citation` names a `cq <pillar> <verb>` whose verb
has a tool, in a body the check enforces; `sk-mcp-unknown-tool` names a `<pillar>_<verb>(` that is
no tool of the catalog.

### Where a body still writes the CLI

1. **The verb has no tool**: the exceptions of `mcp/coverage.py` (`cq deploy`, `cq modules`,
   `cq specs migrate`, `cq specs export`, `cq specs serve`, `cq codex implement`,
   `cq specs claim take`, …) and any verb the server's `tools/list` does not name.
2. **A line marked `cli: <reason>`** — `<!-- cli: <reason> -->` at the end of the line, or alone on
   the line before a block (it then covers that whole paragraph or fenced block), and
   `# cli: <reason>` at the end of a line inside a fenced block. The reasons are closed:
   - **root** — the server acts on its own root, the session's directory. A verb that reads or
     writes the working tree (`git commit`, `git state`, a test) called for a worktree that is not
     that root runs `cd <worktree> && cq …`.
   - **atomic** — a write of several spec sections in one call; `specs_section_write` writes one.
   - **by** — `approved` stamped `by=session` or `by=orchestrator-forced`; `specs_record` writes
     `approved` as `by=human`, after asking.

### The fallback: a session with no server

With no `quenching` server, or a verb the server does not list, the call runs `cq` as below and
**the run's report says so** — `MCP: fallback cq <pillar> <verb> — <no tool | no server>` — so a
fallback is never silent. The tool maps back mechanically: `<pillar>_<verb…>` is
`cq <pillar> <verb…>` (each `_` a word break, `-` inside a word: `knowledge_site_source` is
`cq knowledge site-source`, `cq <pillar> --help` settles a doubt), and each argument is the flag of
the same name with `_` read as `-` (`rules_only=true` is `--rules-only`, a list repeats the flag).
The hand-written specs tools name their arguments apart from the CLI:

| Tool | CLI |
| --- | --- |
| `specs_status(spec=X)`, `specs_show(spec=X, tasks=[T])` | `cq specs status --spec X`, `cq specs show --spec X --task T` |
| `specs_section(spec=X, headings=H, moment=M, scope=S)` | `cq specs section X "H"` / `--moment M --scope S` |
| `specs_section_write(spec=X, heading=H, body=B)` | `cq specs section X "H" --write` with `B` on stdin |
| `specs_record(spec=X, name=N, fields={"k": "v"})` | `cq specs record X N --set k=v` |
| `specs_task(spec=X, action=A, task=T, reason=R, subject=S, commit=C)` | `cq specs task --spec X --A T --reason R --subject S --commit C` |
| `specs_discover(spec=X, text=F)` | `cq specs discover X "F"` |
| `specs_create(name=N, title=T, …)` | `cq specs new N --title T …` |
| `specs_list(phase=P)`, `specs_next(spec=X)`, `specs_next()` | `cq specs list --phase P`, `cq specs next --spec X`, `cq specs next --front` |
| `specs_promote(spec=X, to=P, outcome=O)` | `cq specs promote X --to P --outcome O` |
| `specs_link_add(epic=E, spec=X, after=A)`, `specs_epic_progress(epic=E)` | `cq specs link add E X --after A`, `cq specs status --spec E` |
| `specs_push()` | `cq specs push` |

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
