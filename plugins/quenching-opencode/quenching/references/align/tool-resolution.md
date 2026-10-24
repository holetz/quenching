# Resolving a plugin tool

Front-neutral: every command body shells out to the same single entry point, `cq`, naming its
front as the first argument. The fronts are `specs`, `git`, `knowledge`, `components`, `design`,
`ops`, `proof`, `toolchain`, `delivery`, `security` and `codex`; all resolve it the same way.

## Resolving the tool

OpenCode does **not** require `cq` on the user's PATH. A bare `cq` in the examples below means the
shell function defined at the start of the same bash call:

```bash
cq() { python3 "${QUENCHING_OPENCODE_ROOT:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode/quenching}/scripts/cq" "$@"; }
```

It runs the bundled `scripts/cq` of the installed payload — `$QUENCHING_OPENCODE_ROOT` when set,
else `~/.config/opencode/quenching`. Define it again in every bash call: shell state does not
survive between calls, and a subagent may start with a fresh environment. Never install `cq`
into a target repository and never edit the user's PATH to make it resolve.

Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json` payload, never on
prose.

### Write the resolved path literally on every invocation

Do not copy a relative path from a reference into a command; the wrapper above is the portable
form, including for subagents.

**Chain several writes so a failure stops the run** — `set -e`, or `&&` between them.
