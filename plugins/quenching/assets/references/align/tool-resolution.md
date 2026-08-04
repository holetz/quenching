# Resolving a plugin tool, and writing its path

Front-neutral: every `/docs:*`, `/specs:*` and `/skill:*` command body that shells out to
`specs.py`, `skills.py` or `okf-validate.py` resolves it the same way.

## Resolving the tool

Invoke the tool at its plugin path — `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py`,
`${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py`,
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py` (the plugin's own `hooks/hooks.json` wires
that last one the same way). **There is no fallback and no manual rung**: never look for a copy
under a target's `.claude/hooks/`, never install one there, never merge anything into a target's
`.claude/settings.json` to make a tool resolve.

Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json` payload, never on
prose.

### Write the resolved path literally on every invocation

Never hold the interpreter plus the script path in a shell variable and expand it as a command —
zsh does not word-split scalars, so the call fails silently:

```bash
SP="python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py"
$SP status --spec my-spec --json      # WRONG
```

Write the path in full and **quoted** — `${CLAUDE_PLUGIN_ROOT}` can contain spaces — on each call:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py" status --spec my-spec --json
```

When one `Bash` call issues several invocations, a shell **function** is the only correct
abbreviation, and only *within that call* — shell state does not survive between calls:

```bash
sp() { python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py" "$@"; }
sp section my-spec "Proposal" --write <<'EOF'
…
EOF
sp validate --spec my-spec --json
```

**Chain several writes so a failure stops the run** — `set -e`, or `&&` between them.
