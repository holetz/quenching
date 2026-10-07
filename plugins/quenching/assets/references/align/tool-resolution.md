# Resolving a plugin tool

Front-neutral: every command body shells out to the same single entry point, `cq`, naming its
front as the first argument. The fronts are `specs`, `git`, `knowledge`, `components`, `design`,
`ops`, `proof`, `toolchain`, `delivery` and `security`; all resolve it the same way.

## Resolving the tool

**One form: bare `cq …`.** Claude Code appends `<pluginRoot>/bin` to `PATH` for every enabled
plugin, and the plugin ships an executable `bin/cq` there (a shim that re-executes
`assets/bin/cq`). Every command body and reference writes `cq specs …`, never a path and never
`python3 …/cq`.

A body that runs `cq` declares `Bash(cq:*)` in its `allowed-tools`; without it the call prompts
(or is denied in a never-prompt session). A body must not widen it to `Bash(python3:*)`
to reach the tool.

The command is followed by the front and its subcommand: `cq specs ...`, `cq git ...`,
`cq knowledge ...`, `cq components ...`, `cq design ...`, `cq ops ...`, `cq proof ...`,
`cq toolchain ...`, `cq delivery ...`, `cq security ...`. **There is no second form and no third
rung**: never look for a copy under a target's `.claude/hooks/`, never install one there, never
merge anything into a target's `.claude/settings.json` to make a tool resolve.

Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json` payload, never on
prose.

### Working on the quenching repository itself

The `PATH` entry names the *installed* checkout, so a bare `cq` there runs the plugin the session
loaded rather than the code being written. When editing this repository, run the checkout's own
file explicitly — `python3 plugins/quenching/assets/bin/cq …` — as the author's check. That is a
developer invocation, never something a command body or reference writes for a target.

### `${CLAUDE_PLUGIN_ROOT}` is empty in a shell

The variable is substituted into a **command body's text** when Claude Code loads it. **The shell
has no such variable**: the same spelling reached any other way (most often by opening a reference
with `Read`) expands to nothing. Bare `cq` needs no root at all, which is why it is the one form.
Anything else executable the plugin ships locates itself from its own `__file__`, never from
`${CLAUDE_PLUGIN_ROOT}`.

### Write the resolved path literally on every invocation

Never hold an interpreter plus a path in a shell variable and expand it as a command — zsh does not
word-split scalars. Write `cq` on each call. **Chain several writes so a failure stops the run** —
`set -e`, or `&&` between them:

```bash
set -e
cq specs section my-spec "Proposal" --write <<'EOF'
…
EOF
cq specs validate --spec my-spec --json
```
