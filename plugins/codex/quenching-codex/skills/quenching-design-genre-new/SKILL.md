---
name: quenching-design-genre-new
description: "Mint ONE editorial genre under /.design/genres/ with fields, register and medium templates. Use for \"create a design genre\", \"define a deck contract\". Not for: whole front → quenching-design-align."
---

<!-- GENERATED FROM plugins/quenching/commands/design/genre/new.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-design-genre-new — one genre, N destinations

**Input**: `$ARGUMENTS` (one genre name or a short description of it).

This command mints one stable editorial contract. It does not produce an instance of the document;
`cq design render` does that after fields have data.

## Workflow

### 1. Prove the front exists

Resolve `cq` per
[tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool and run `design status --json`. An absent or invalid front routes to
`quenching-design-align` and stops. Read existing genres and medium templates for name/path
collisions.

**Done when:** the front is healthy and the proposed genre has no collision.

### 2. Fix the contract

Derive a canonical-English kebab-case slug and ask only for missing choices that change output:

- display name and editorial register;
- fields, each required or optional with a one-line meaning;
- destinations among HTML, Typst and PDF (PDF uses the Typst template and compiler);
- composition and guardrails that stay true in every destination.

Use button, input, navigation, chip and card when the genre needs UI-like primitives; eyebrow,
rule and frame are the editorial extensions. Fields hold content, never token values.

**Done when:** slug, register, fields, media, composition and guardrails are explicit.

### 3. Present one plan and gate

Show the genre file, one template per underlying medium (`pdf` shares Typst), the exact CLI
invocation, and the MEDIUM.md regeneration. Execution profile is default: no fork, model pin,
background run or hook. Wait for one OK.

**Done when:** the user accepts; a decline writes nothing.

### 4. Mint through the deterministic tool

Invoke one command, repeating `--media` and `--field`:

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
cq --root . design genre new <slug> \
  --name "<name>" --register "<register>" \
  --media <medium> --field "<name>:<required|optional>:<description>" --json
```

Fill the generated genre's Composition and Guardrails sections with the accepted content without
putting primitive values in them. Merge only that gap; never overwrite an existing genre or
template.

**Done when:** the genre and every declared medium template exist with the accepted contract.

### 5. Verify

Run `design build --json`, `design doctor --json`, then render one smallest fixture into every
declared non-PDF medium. For PDF, run it only when `typst` already resolves; otherwise report PDF
as supported but locally unverified. Inspect outputs for unresolved `{{...}}` placeholders.

**Done when:** doctor exits 0, MEDIUM.md lists the genre, every available renderer succeeds, and
the PDF compiler result or absence is stated.

### 6. Report

Report the invocation, genre path, templates, destinations, smoke-render outputs and any
unverified PDF capability.

**Done when:** one genre — no sibling work — is fully accounted for.

## Invariants

- One invocation mints one genre.
- Genre fields never redeclare tokens.
- One genre may target many media; PDF is a Typst compilation, not a second template authority.
- Never overwrite a collision and never claim PDF verification without compiling it.
- Never hand this command `context: fork`; its plan gate is mid-flow.
