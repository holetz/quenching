# Specs store conformance

This reference defines the checks for the specs front. The documents on the `quenching` branch are
the source of truth and tracker cards are their projection; `cq specs` is the uniform surface that
reads and writes both. The `github` and `azure-boards` backends are deprecated, still work, and
`cq specs doctor` flags them (`sp-backend-deprecated`).

## Store configuration

The target's `.claude/quenching.json` selects the store (`"backend": "git"`) and may refine card
settings and project conventions; the branch's `quenching.json` holds the specs-axis keys. No
command silently switches the store. A legacy repository-store value is refused with an actionable
finding.

Configuration is validated before any write:

- The git store requires a remote that holds, or can receive, the `quenching` branch.
- A card provider requires a resolvable repository (GitHub) or the placement needed to create a
  work item (Azure Boards).
- An unknown backend refuses; it never falls back to another transport.

The configuration details and defaults live in
[plugin-configuration.md](plugin-configuration.md).

## Probes

Run the store checks before reading or changing a spec:

```bash
cq() {
  local plugin_root="${CODEX_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
  if [ -z "$plugin_root" ]; then
    plugin_root="$(set -o pipefail
codex plugin list --json | python3 -c '
import json, os, sys
from pathlib import Path
plugins = [p for p in json.load(sys.stdin)["installed"] if p.get("name") == "quenching-codex" and p.get("enabled")]
if len(plugins) != 1:
    sys.exit("quenching-codex: enable exactly one installation, or provide its plugin root")
p = plugins[0]
home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
print(p.get("installedPath") or home / "plugins/cache" / p["marketplaceName"] / p["name"] / p["version"])
')" || return 2
  fi
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}
cq specs doctor --json
cq specs config --json
cq specs validate --json
```

Exit `0` means the store and fetched front are conformant. Exit `1` reports findings that a
human or the owning lifecycle command must resolve. Exit `2` is a refusal: authentication,
store selection, or required configuration is missing or invalid.

## Lifecycle ownership

`create`, `develop`, `execute`, `status`, `triage`, and `conclude` own the spec lifecycle.
There is no installer step for the specs branch: the first write creates it, and
`cq specs migrate --to git` moves a deprecated tracker backend onto it. A complete spec is closed by
`conclude`, which records the outcome in the spec and distils durable knowledge into the OKF
bundle.

## Finding policy

Findings name the store or card provider, the missing configuration, and the command that owns the
repair. The checks must not invent a path, fabricate a phase, or offer a second store.
