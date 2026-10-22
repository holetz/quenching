---
name: quenching-ops-entrypoint-new
description: "Mint ONE Python ops entry point, register it in the router and regenerate the registry. Use for \"mint an ops entry point\", \"add a command to the ops router\". Not for: repairs → quenching-ops-align."
---

<!-- GENERATED FROM plugins/quenching/commands/ops/entrypoint/new.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-ops-entrypoint-new — mint one operations entry point

**Input**: `$ARGUMENTS` (one proposed operation name or a short description of the entry point).

This command creates one Python entry point in the target repository's declared operations root.
The seven-rule contract lives in
[ops-align/entrypoint-contract.md](../../references/ops-align/entrypoint-contract.md);
the target tree, lifecycle and router boundary live in
[ops-align/target-structure.md](../../references/ops-align/target-structure.md)
and [ops-align/lifecycle.md](../../references/ops-align/lifecycle.md).
The mold is `../../templates/ops/entrypoint.py.tmpl`; router registrations
come from `../../templates/ops/router-snippets.md`.

Resolve `cq` per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool. Use the resolved path literally, pass the target root to every `cq ops` call,
and branch on exit code and JSON: `0` is clean, `1` carries findings, and `2` is a refusal.

## Workflow

### 1. Prove the target boundary

Set `TARGET_ROOT` to the target repository root, or `.` when the caller did not provide a separate
target. Run:

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
cq --root "$TARGET_ROOT" ops doctor --json
```

Read the returned configuration and inventory state. Stop on exit `2`, naming every missing key;
do not invent `scripts/`, a bootstrap module, a router, or a registry path. Locate the one shared
bootstrap module already used by the target's entry points and check the proposed normalized name
and module path against the inventory. A collision is an edit decision, not permission to overwrite
an existing file.

**Done when:** the declared `opsRoot`, router, registry path, shared bootstrap and collision state
are fixed, or a refusal has stopped the run without writes.

### 2. Ask the four binding questions

Ask these questions in this order, retaining the answers as the minting contract:

1. What does the entry point do, in one line? Use the answer for the module docstring, parser
   description and registry purpose.
2. Which domain package owns it? Use the answer to place the file under the active domain package,
   or under `_archive/<domain>/` when the lifecycle answer makes it one-shot.
3. Does it write outside the repository? A `yes` answer requires the preview-first `--apply`
   guard; a `no` answer removes the write-capable shape from the scaffold.
4. Is its lifecycle `active` or `archived`? Only `active` entry points enter the active router;
   an `archived` entry point is born under `_archive/` and remains visible to the registry.

Reject a non-answer or an answer that would create a second router. Do not ask about choices the
mold fixes: bootstrap import, typed `main()`, `SystemExit`, data/diagnostic streams and JSON shape
come from the template.

**Done when:** the purpose, domain, write policy and lifecycle are explicit and map to one output
path and one router action.

### 3. Present one plan and gate once

Show the exact file path, the shared bootstrap import, the selected write shape, the lifecycle,
the router snippet, the registry regeneration and both closing probes. State every file that will
change. Ask once for authorization of this mint. If the plan is rejected, write nothing.

**Done when:** one authorization covers the listed writes, or rejection ends the run with no diff.

### 4. Scaffold from the mold

Copy the mold into the chosen path and replace every placeholder with the accepted answers. Keep
these invariants in the resulting module:

- root resolution, `sys.path` preparation and shared flags come only from the target's bootstrap;
- `main() -> int` returns `0` for success, `1` for findings and `2` for misuse, and `__main__`
  carries that value out with `SystemExit(main())`;
- data stays on `stdout`, diagnostics stay on `stderr`, and `--json` puts only serialized data on
  `stdout`;
- a write-capable entry point previews the intended external change and performs it only after an
  explicit `--apply`; source edits and ambient environment state never arm it.

For a non-writing entry point, set `WRITES_OUTSIDE_REPOSITORY = False` and remove the write guard.
For a writing entry point, set it to `True`, add the explicit `--apply` argument from the mold and
make the operation refuse the write while that flag is absent. Never leave a placeholder or an
unarmed write branch in the target file.

**Done when:** the new Python file exists, has a useful `--help` example, and its source satisfies
the contract's bootstrap, exit, stream, JSON, arming and lifecycle rules.

### 5. Register and regenerate

Apply the snippet for the declared router from
`../../templates/ops/router-snippets.md`. Register an active entry point;
leave an archived entry point out of the active router. Then regenerate the registry:

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
cq --root "$TARGET_ROOT" ops registry --write --json
```

The generator owns the marked block. Preserve authored prose around it and do not edit generated
rows by hand.

**Done when:** the router reaches the new active operation when applicable and the registry names
the new entry point with its purpose, invocation, lifecycle and write signal.

### 6. Re-verify the mint

Run the closing verifier and, when it reports a finding, fix only the new entry point, its declared
router registration or the generated registry block:

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
cq --root "$TARGET_ROOT" ops doctor --json
cq --root "$TARGET_ROOT" ops registry --check --json
```

For a write-capable entry point, exercise the preview path without `--apply` and confirm no
external write occurs. Exercise `--help` and the JSON path; diagnostics must not contaminate JSON
stdout. Do not run the external write merely to prove the arming flag.

**Done when:** `ops doctor` has zero findings, `registry --check` reports unchanged, and the
selected write/non-write shape has a captured help, preview or JSON proof.

### 7. Report

Report the invocation, created path, purpose, domain, lifecycle, router, registry path, write
policy, verification payloads and any target-owned residue. State explicitly when the command
refused before writing or when a judgement finding remains for `quenching-ops-align`.

**Done when:** one new entry point and its proof are fully accounted for, with no claim beyond the
captured verifier output.

## Invariants

- One invocation mints one Python entry point; existing paths are never silently overwritten.
- The target's declared router and shared bootstrap are required; neither is guessed.
- The four answers bind the path, write shape and lifecycle; the mold supplies the deterministic
  contract.
- A write outside the repository is preview-first and explicitly armed; there is no unarmed branch.
- The registry's generated block is regenerated by `cq ops registry`, never hand-composed.
- Never hand this command `context: fork`; its confirmation gate is mid-flow.
