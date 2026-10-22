---
name: quenching-components-agent-new
description: "Mint or edit ONE subagent definition in .agents/agents/. Use for \"create an agent\", \"add a subagent\", \"make a verifier agent\". Not for: commands → quenching-components-command-new; hooks → quenching-components-hook-new."
---

<!-- GENERATED FROM plugins/quenching/commands/components/agent/new.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-components-agent-new — mint ONE subagent definition

**Input**: `$ARGUMENTS` (the agent to create or edit — a name or a description of the work
to delegate).

Creates or edits **ONE FILE** in the target repo's agent surface — `.agents/agents/<name>.md`,
a definition whose description routes delegation to it and whose body is its system prompt.
The delegation economics and the definition contract live in
[components-command-new/capabilities.md](../../references/components-command-new/capabilities.md)
§Subagents. The mold is
`../../templates/automation/agent.md`.

## Doctrine

- **The rule governs; the plan proposes.** In a target repo the rule is
  `/docs/standards/automation/agents.md` — read it before drafting and follow it when present.
  Absent + OKF bundle present → the plan offers creating it from
  `automation/agents-standard.md`, born `authority: background`; never created without the OK.
- **No bundle, no tail — but the mint proceeds.** `/docs/index.md` without `okf_version` (or
  absent) means: write the definition only, skip the OKF tail silently, suggest `quenching-knowledge-align`
  **once**.
- **One plan, one OK, nothing before.** The delegation buy, the name, the profile, every
  file, and the tail appear in ONE plan; a declined plan writes nothing.
- **MERGE, never clobber.** An edit preserves the body and any hand-written content; only the
  gap being fixed changes. This skill never deletes an agent.
- **An agent's description is always-on context.** The same two caps as a command's, counted
  on the parsed value.

Resolve `cq` per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

## Workflow

### 1. Read the rule
Read `/docs/standards/automation/agents.md` and confirm the bundle (`/docs/index.md` carries
`okf_version`). Rule present → it governs. Rule absent, bundle present → add "create the rule
from `automation/agents-standard.md`" to the plan. No bundle → note the tail as skipped and
plan the `quenching-knowledge-align` suggestion. **Done when:** the governing rule (or its planned
creation, or the no-bundle note) is fixed.

### 2. Apply the delegation test
Per [capabilities.md](../../references/components-command-new/capabilities.md)
§Subagents: the work qualifies when its returned summary is much smaller than the work
itself, when slices run in parallel, or when its tool set must be narrower than the
conversation's. Work that fails the test is a command or an inline step — say so and route
to `quenching-components-command-new`. **Done when:** the delegation
buy is stated in one line, or the request is rerouted.

### 3. Derive the name, check collisions
Kebab-case identity naming what the agent *is* (`migration-verifier`), never `helper`.
`Glob` `.agents/agents/*.md`: an existing path is a MERGE target (edit), never silently
overwritten. **Done when:** the path is fixed, collision-free or resolved as an edit.

### 4. Draft from the mold
Fill `automation/agent.md`: a description carrying the work **and the timing** ("after X is
modified", "when asked to audit Y") within the caps; `tools` at the narrowest set (spawning is controlled by `Agent` in `tools`);
`model`/`effort` per the pinning rules (mechanical extraction may run cheap — judgment never
downgrades; a pin here is cache-safe); `skills`, `memory` only with a
stated reason. The body is a **system prompt in second person**. Inspection work takes the
verifier shape: numbered check areas, a "not checked here" list, if-present guards, a fixed
report format — and it never edits. **Done when:** the draft passes
[capabilities.md](../../references/components-command-new/capabilities.md)
§Subagents read top to bottom.

### 5. Present ONE plan → gate on the OK
Show: the delegation buy, the name, the profile fields with reasons, every file (the
definition, the rule if planned, and the tail steps. Wait for the single
confirmation. **Done when:** the user has answered; declined → report "nothing written" and
stop.

### 6. Write
Write the definition (and the rule if planned). **Done when:** every planned file exists
with its planned content.

### 7. OKF tail (bundle present)
The registry's GENERATED zone lists commands only. Offer, as follow-up commands rather than writes
in this run, one curated registry-prose line for the agent surface and `quenching-knowledge-define`
for a coined repo-specific term; the user decides both. **Done when:** each offer is answered.

### 8. Self-check
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
cq components doctor --json
cq components lint --json
```
`lint` takes no argument here: `lint <file>` never reaches the agents. Keep every finding whose
`path` is this file, from either payload, whatever its code (`sk-cq-flag` included). Then read the definition against the contract by eye: tools scoped, voice second-person, a
verifier states it never edits. Report what was written and the always-on cost the
description adds. **Done when:** neither `doctor` nor `lint` reports any finding for this file and
the report states the description's parsed character count.

## Invariants

- Never write before the single OK; a declined plan leaves the repo untouched.
- Never delete an agent, and never clobber an existing body — MERGE.
- Never leave `tools` unstated by accident — omitting it grants everything, and the plan
  says so when that is the choice.
- Never mint a verifier that edits; findings re-enter through the command that owns
  authoring.
- Never hand this command file `context: fork` — the plan gate is mid-flow.
