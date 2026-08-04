# Resolving a plugin tool, and writing its path

Front-neutral: every `/docs:*`, `/specs:*` and `/skill:*` command body that shells out to one of
this plugin's three tools — `specs.py`, `skills.py`, `okf-validate.py` — resolves it the same way.

## Resolving the tool

A command body always invokes `${CLAUDE_PLUGIN_ROOT}/assets/{bin,hooks}/<tool>` —
`${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py`, `${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py`,
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py`. **There is no fallback and no manual rung.**
The plugin's own `hooks/hooks.json` wires `okf-validate.py` the same way, so nothing is installed
into a target's `.claude/hooks/` and no align merges anything into a target's
`.claude/settings.json` to make a tool resolve.

Every command branches on the **exit code** (0 ok · 1 findings · 2 refusal) and the
`--json` payload, never on prose. That contract is what lets the commands stay short: the tool
decides, the command reports.

### Write the resolved path literally on every invocation

**Never hold the interpreter and the script path in a shell variable and expand it as a command.**
This is the one shell idiom that silently breaks the resolution above:

```bash
SP="python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py"
$SP status --spec my-spec --json      # WRONG
```

Under **bash** this works, because unquoted expansion is word-split. Under **zsh** it does not:
zsh does not word-split scalars, so `$SP` is one word and the shell looks for a command whose
literal filename is `python3 /…/specs.py`. Measured 2026-07-27 — bash prints the version, zsh
answers `command not found: python3 --version`.

The failure mode is what makes it worth a rule: it is **shell-dependent and silent**. Nothing is
written, the exit status is a plain non-zero, and a command that does not read stderr closely
reports "sections written" over a file it never touched. Since a target repo's shell is whatever
the human uses, a pattern that passes on the author's bash is not evidence of anything.

Write the resolved path in full on each call:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py" status --spec my-spec --json
```

A shell **function** is the only correct abbreviation, and only *within a single `Bash` call* —
shell state does not survive between calls, so a function defined in one call is gone by the next
(measured 2026-07-27). When one call issues several invocations:

```bash
sp() { python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py" "$@"; }
sp section my-spec "Proposal" --write <<'EOF'
…
EOF
sp validate --spec my-spec --json
```

**Quote the path.** `${CLAUDE_PLUGIN_ROOT}` can contain spaces, which splits an unquoted path into
two arguments and produces the same "no such file" with a different cause.

**When several writes run in one call, chain them so a failure stops the run** — `set -e`, or
`&&` between them. A loop of independent writes where the first silently fails and the rest
proceed is how a partial spec gets reported as complete.
