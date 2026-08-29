# Resolving a plugin tool, and writing its path

Front-neutral: every `quenching-knowledge-*`, `quenching-specs-*`, `quenching-design-*` and `quenching-components-*` command body
shells out to the same single entry point, `cq`, naming its pillar (`specs`, `knowledge` or
`components`) as the first argument. All three resolve it the same way.

## Resolving the tool

Codex does **not** require `cq` to be installed in the user's PATH.  A bare `cq` in the
examples below means the shell function defined at the start of the same Bash call; never
assume that `cq` is an independently installed command, and never ask the user to add it to
their shell startup files.

```bash
cq() {
  local plugin_root="${PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-}}"
  [ -n "$plugin_root" ] || plugin_root="$(codex plugin list 2>/dev/null | awk '$1 ~ /^quenching-codex@/ {print $NF; exit}')"
  [ -n "$plugin_root" ] || plugin_root="$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f \( -path '*/quenching-codex/*/scripts/cq' -o -path '*/quenching-codex/scripts/cq' \) -print -quit 2>/dev/null | sed 's#/scripts/cq$##')"
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}
```

The function uses the plugin-provided root when the host exposes one, otherwise it resolves the
installed `quenching-codex` copy through `codex plugin list` or the standard Codex cache.  It then
executes the bundled `scripts/cq` by absolute path.  Defining it again in each Bash call is
intentional: shell state does not survive between calls, and sub-agents may receive a fresh
environment.

There is no target-repository installation step and no third rung: never look for a copy under a
target's `.agents/hooks/`, never install one there, and never modify the user's PATH to make this
tool resolve.

Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json` payload, never on
prose.

### Write the resolved path literally on every invocation

The wrapper resolves the installed plugin at the point of execution.  Do not copy a relative path
from this reference into a command: a fresh Bash call has no shared working-directory or shell
state to make a plugin-relative path reliable.  Defining the function again in every Bash call is
the portable form, including for sub-agents.

**Chain several writes so a failure stops the run** — `set -e`, or `&&` between them.
