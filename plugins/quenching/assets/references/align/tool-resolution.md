# Resolving a plugin tool, and writing its path

Front-neutral: every `/quenching:knowledge:*`, `/quenching:specs:*` and `/quenching:components:*` command body
shells out to the same single entry point, `cq`, naming its pillar (`specs`, `knowledge` or
`components`) as the first argument. All three resolve it the same way.

## Resolving the tool

**Two routes to the same file, in this order.**

1. **`cq …`, bare.** Claude Code appends `<pluginRoot>/bin` to `PATH` for every enabled plugin, and
   the plugin ships an executable `bin/cq` there. This is why command bodies write `cq specs …`
   and not a path; where the PATH holds, it is the whole answer.
2. **`python3 "<pluginRoot>/assets/bin/cq" …`**, with the root written out in full. Use it wherever
   route 1 does not resolve — a restricted `allowed-tools`, a shell that never got the session's
   PATH — and **always when working on the quenching repository itself**: the PATH entry names the
   *installed* checkout, so a bare `cq` there runs the plugin the session loaded rather than the
   code being written.

Either route is followed by the pillar and its subcommand: `cq specs ...`, `cq knowledge ...`,
`cq components ...`. **There is no third rung**: never look for a copy under a target's
`.claude/hooks/`, never install one there, never merge anything into a target's
`.claude/settings.json` to make a tool resolve. The two routes are one file reached two ways, never
two installations.

Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json` payload, never on
prose.

### `${CLAUDE_PLUGIN_ROOT}` is empty in a shell

The variable is substituted into a **command body's text** when Claude Code loads it, so a body
citing `${CLAUDE_PLUGIN_ROOT}/…` arrives already expanded and its absolute path can be copied
straight into a call. **The shell has no such variable.** The same spelling reached any other way —
most often by opening a reference with `Read` — expands to nothing, and the call silently becomes
`python3 "/assets/bin/cq"`.

So route 2 is written with the **expanded** root, never with the variable. `<pluginRoot>` below
stands for that absolute path, the one the citing body arrived with:

```bash
python3 "<pluginRoot>/assets/bin/cq" specs status --spec my-spec --json
```

The same rule binds anything executable the plugin ships: it locates itself from its own
`__file__`, never from `${CLAUDE_PLUGIN_ROOT}` — which is what `bin/cq` does to find
`assets/bin/cq`.

### Write the resolved path literally on every invocation

Never hold the interpreter plus the script path in a shell variable and expand it as a command —
zsh does not word-split scalars, so the call fails silently:

```bash
CQ="python3 <pluginRoot>/assets/bin/cq"
$CQ specs status --spec my-spec --json      # WRONG
```

Write the path in full and **quoted** — a plugin root can contain spaces — on each call. When one
`Bash` call issues several invocations, a shell **function** is the only correct abbreviation, and
only *within that call* — shell state does not survive between calls:

```bash
cq() { python3 "<pluginRoot>/assets/bin/cq" "$@"; }
cq specs section my-spec "Proposal" --write <<'EOF'
…
EOF
cq specs validate --spec my-spec --json
```

**Chain several writes so a failure stops the run** — `set -e`, or `&&` between them.
