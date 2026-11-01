---
name: quenching-handoff
description: "Compact the current conversation into a handoff stored beside its spec, ready for another agent to continue. Use for \"generate a handoff\" or \"prepare a handoff for the next session\". Not for: implementing → the owning command."
---

<!-- GENERATED FROM plugins/quenching/commands/handoff.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


**Input**: `$ARGUMENTS` (the focus of the next session).

The handoff is a file the next session READS BEFORE IT ACTS, and it belongs to a spec whenever one
exists: it is stored on the `quenching` branch under `specs/artifacts/<id>/`, travels with
`cq specs push`, and is readable from any clone — not left in a temp directory that the next
machine cannot see.

## Workflow

### 1. Fix the next session's focus

Use `$ARGUMENTS` when provided. When it is omitted, use the main unfinished objective in the
current conversation as the focus. **Done when:** the focus is fixed in one sentence.

### 2. Resolve the spec, never invent one

An id already stated in the conversation or in `$ARGUMENTS` wins. Otherwise resolve the current
branch:

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
cq specs find --branch "$(git branch --show-current)" --json
```

One match → that id. No match, no store, or any failure → **no spec**, and the report says so
explicitly: a standalone handoff is honest, an invented id is not. **Done when:** the spec id or
its explicit absence is decided.

### 3. Name and draft the handoff

Name it `handoff-<YYYY-MM-DD>-<focus-slug>.md` — the session's date, then a kebab-case slug of the
focus. Write the draft to `.quenching/handoff/<name>` with the Write tool: that path is the
sanctioned ephemeral location, and the draft doubles as the fallback when no store answers.

Compose the summary for the fixed focus: objective, current status, decisions, completed work, open
work, validation evidence, blockers, and next actions. Reference existing PRDs, plans, ADRs,
issues, commits, diffs, or other artifacts by path or URL instead of duplicating their contents.
Suggest skills for the next session when they apply. **Done when:** the draft contains enough
context to resume the work and points to existing artifacts rather than copying them.

### 4. Store it through the door, then read it back

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
cq specs artifact write --spec <id> --name <name> --from .quenching/handoff/<name>
cq specs push
```

Omit `--spec` when step 2 found none: the artifact then lives under `specs/artifacts/_handoffs/`.
The write leaves the handoff in the clone's pending ref; the push sends it. Then read it back
through the same door:

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
cq specs artifact read --spec <id> --name <name>
```

Branch on the exit code, never on prose. The write refusing with `sp-artifact-unsupported`,
`sp-artifact-no-store` or a backend refusal means this repository has no store to hold it: the
`.quenching/handoff/` draft IS the handoff, and the report says it stayed local. Any OTHER refusal
is reported as the failure it is — it never silently becomes the fallback. A failed
`cq specs push` (offline, lease taken) leaves the artifact pending and the report says
`not sent — cq specs push`. **Done when:** the artifact was read back and matches the draft, or the
fallback is stated with the reason it was taken.

### 5. Close with the direction block

The handoff is worthless if the next session does not know where it is. Print ONE block, with
these three fields in this order: the locator, the command that reads it, and the prompt that
starts the next session. The structure and the field order are literal; the labels and the prompt
follow the conversation's language — this repository is `pt-BR`, so its printed form is:

```
## Handoff

quenching:specs/artifacts/2138/handoff-2026-11-01-destination.md

Cole numa sessão nova:

    Leia o handoff em
    quenching:specs/artifacts/2138/handoff-2026-11-01-destination.md antes de agir:
    `cq specs artifact read --spec 2138 --name handoff-2026-11-01-destination.md`.
    Ele pertence à spec 2138; siga com `quenching-specs-execute 2138`.
```

Three substitutions, and nothing else changes:

- **No spec** → the last sentence becomes `nenhuma spec está atrelada; pergunte o que fazer`, and
  the read command loses `--spec`.
- **Not sent** → one line under the block says `não enviado — cq specs push`.
- **Fallback** → the locator becomes `.quenching/handoff/<name>`, the read command becomes a plain
  file read, and one line says `só local — este repositório não tem store git de specs`.

**Done when:** the block is printed with the locator, the read command and the prompt, and every
substitution that applies is stated rather than implied.

## Invariants

- Keep the handoff focused on the next session's work.
- Reference durable artifacts instead of duplicating their contents.
- Suggest only skills that are relevant to the recorded next actions.
- Never write the handoff into a file only this machine can see without saying so.
