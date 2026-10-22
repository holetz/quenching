---
name: quenching-design-status
description: "Report the /.design/ front: source validity, generated identity, genres and drift, read-only. Use for \"design status\", \"is DESIGN.md current\". Not for: fixes → quenching-design-align."
---

<!-- GENERATED FROM plugins/quenching/commands/design/status.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-design-status — read the whole design front

**Input**: `$ARGUMENTS` (optional focus; omission reads the whole front).

The common front contract is in
[front-align/mold.md](../../references/front-align/mold.md), and the
design-specific disposition map is in
[design-align/bands.md](../../references/design-align/bands.md). This
read-only view preserves design's source arbitration, projection and optional-detector deltas.

Resolve `cq` per
[tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool, then run:

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
cq --root . design status --json
cq --root . design build --check --json
```

Read the source and named findings only as needed to explain them. Do not write, import, build,
render, install Impeccable, or reinterpret an external `DESIGN.md` as source.

Report one compact table:

| Band | Evidence |
| --- | --- |
| Source | DTCG schema/version, token count, external schema stamps |
| Product | PRODUCT schema 1 projection and its OKF source homes |
| Portable design | DESIGN.md byte identity and five projected groups |
| Sidecar | schema 2, extensions and canonical/editorial component counts |
| Editorial | genre list, declared media and MEDIUM.md identity |
| Internal adapters | CSS, Typst, Python and brand API identity |
| Residue | orphan assets, non-web literals, missing optional web detector |

Separate errors from warnings and name the exact closing command for each actionable finding.
Impeccable absence is a capability note, not a finding: this front emits a portable format even
when no consumer is installed.

**Done when:** every band has authoritative evidence or an explicit missing state, every finding
keeps its code, and the report states that nothing was written.

## Invariants

- Never repair while reporting status.
- Never call a missing optional detector healthy.
- Never infer round-trip fidelity beyond the five portable groups.
