---
name: quenching-design-align
description: "Converge /.design/ from one DTCG source through PRODUCT.md, DESIGN.md, MEDIUM.md and adapters. Use for \"align the design\", \"install the brand pack\", \"fix design drift\". Not for: read-only → quenching-design-status."
---

<!-- GENERATED FROM plugins/quenching/commands/design/align.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-design-align — one source, every projection

**Input**: `$ARGUMENTS` (optional scope inside `/.design/`; omit for the whole front).

The front owns the design source and its documents. Impeccable remains an optional consumer and
the owner of screen craft: its `document` flow may propose a new `DESIGN.md`, but that file becomes
source only through the explicit import choice below.

The common front contract is in
[front-align/mold.md](../../references/front-align/mold.md); this command
keeps the design delta in
[design-align/bands.md](../../references/design-align/bands.md). The mold
does not choose a DTCG source winner or turn visual policy into an automatic repair.

Resolve `cq` per
[tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool. Use the resolved path literally and branch on exit codes
(0 ok · 1 findings · 2 refusal) and JSON, never prose.

## Workflow

### 1. Probe without writing

Run:

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
cq --root . design align --check --json
cq knowledge validate docs --json
```

Inventory `/docs/` headings that can project the product record, `/.design/tokens.json`, the
three root projections, `.impeccable/design.json`, genres, medium primitives and brand assets.
Classify an existing root `DESIGN.md` as **generated** only when its frontmatter carries the literal
generated notice emitted by `cq design build`; otherwise it is an Impeccable proposal awaiting the human's
import/build choice. Do the equivalent provenance check for `PRODUCT.md`, but fold its confirmed
facts into the correct OKF homes by judgment — there is no mechanical product importer.

**Done when:** every source, generated artifact, external proposal and blocker has a named state,
and nothing has been written.

### 2. Resolve only choices that change the source

For absent product truth, ask for the smallest confirmed set that establishes `Platform`, `Users`,
`Product Purpose` and `Positioning`; offer the remaining product-schema 1 headings only when they
are material. Write no answer yet. For an external `DESIGN.md`, ask one arbitration question:
**import** means its portable five groups win and unmentioned rich DTCG tokens remain; **build**
means `tokens.json` wins and overwrites the proposal. Never automate this taste decision.

On a first install with no visual decision, present the starter pack's actual thesis, palette,
typeface, radii and canonical primitives. The human may accept it, name changes, or route first to
Impeccable's `document` interview. Optional means optional: never install Impeccable or make its
absence a blocker.

**Done when:** product facts, initial visual source and any import/build arbitration are explicit.

### 3. Present one plan and gate once

Show every file to add or merge, the product facts moving into OKF, the chosen source winner, and
the commands that will run. State that the authorization covers at most five build/doctor passes.
When invoked by root `/align`, inherit its authorization, narrate this plan, and do not ask again.

Wait for one OK unless the inherited authorization applies.

**Done when:** the plan is accepted or inherited; a decline writes nothing.

### 4. Establish the source and knowledge homes

Create or merge the confirmed product facts under the applicable `/docs/vision/` and
`/docs/standards/` homes. Install only missing brand-pack files from
`../../assets/design/brand-pack/`; preserve every existing file. If the accepted
source is an external `DESIGN.md`, preserve it until the pack's `tokens.json` exists, then run:

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
cq --root . design import --json
```

Otherwise let the DTCG source win. Keep `.impeccable/config.json` untouched: it belongs to
Impeccable and is not generated by this front.

**Done when:** `tokens.json` is valid DTCG 2025.10, product facts live in OKF, and the chosen visual
source has been folded without overwriting the losing source prematurely.

### 5. Build all projections

Run:

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
cq --root . design build --json
```

This emits root `PRODUCT.md`, `DESIGN.md`, `MEDIUM.md`, `.impeccable/design.json` schema 2 and
`/.design/build/{tokens.css,tokens.typ,tokens.py,brand-api.md}`. The root artifacts remain at the
root because Impeccable's context and detector discovery agree there. Never replace one with a
pointer.

**Done when:** build exits 0 and reports every path it changed.

### 6. Verify to a fixpoint

Run `design doctor --json`, the knowledge validator, and — only when Impeccable already resolves
locally and the product platform includes web — `npx impeccable detect --json .`. Fix source or
projection defects through the owner that reported them, then rebuild. Maximum five passes; a pass
with no changed bytes and residual findings is residue, not a reason to spin.

The doctor owns byte identity, orphan assets and non-web literal drift. Impeccable owns web color,
font, radius, size and UI-quality drift. Report a missing optional detector as skipped, never green.

**Done when:** build check and doctor exit 0, OKF has no errors, the optional detector ran or is
reported skipped, and another build writes zero files.

### 7. Report

Report source decisions, installed/merged files, projections, genres, doctor results, optional
detector result and every residual warning. Name the lossy boundary: motion, shadows, breakpoints
and rich snippets remain in DTCG/sidecar and cannot round-trip through `DESIGN.md`. On a first
build, show the complete generated `DESIGN.md`, call out its non-obvious visual choices, and offer
to revise a section or add a missed component pattern.

**Done when:** the human can tell which source won, what was generated, and what remains.

## Invariants

- `/.design/tokens.json` is the only hand-written primitive declaration.
- Generated artifacts are complete projections, never pointers and never second authorities.
- Import/build arbitration is always human; a generated notice never makes the choice.
- `DESIGN.md` emits only colors, typography, rounded, spacing and eight-property components.
- `.impeccable/design.json` extends the frontmatter; it never duplicates primitive arrays.
- Impeccable is an optional consumer, not a declared dependency.
- Never hand this command `context: fork`; its confirmation and arbitration are mid-flow.
