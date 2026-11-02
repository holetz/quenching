---
name: quenching-specs-specs
description: "Run one specs flow (create, develop, execute, conclude, triage, status, orchestrate), picked by name or stage. Use for \"build it\", \"rank the backlog\". Not for: git → quenching-git-branch; rounds → quenching-specs-autopilot."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/specs.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-specs-specs — one entry point for the specs flows

**Input**: `$ARGUMENTS` — an optional flow name, then what that flow takes (a spec id, a
description, a plan path, flags). The remaining words go to the flow untouched.

This command carries no flow of its own. It picks ONE flow, loads that flow's reference and
follows it as if it were this body, so the model's skill list pays for one description and each
flow's text is read only when the flow runs.

**Grant.** The router grants only `cq` and `Read`, enough to load a flow's reference; it widens no flow's tool grant. A tool the chosen flow needs beyond that comes from the conductor agent's own tools, or is asked of the human in a main session; the typed shortcut carries the flow's exact grant.

## Resolving the tool

Resolve `cq` (`cq components read` is the section reader every `§X` citation resolves through)
per [align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Workflow

### 1. Pick the flow
The first word of `$ARGUMENTS` naming a flow in the table below picks it, and the rest is the
flow's input. No flow named → with an id, `cq specs status --spec <id> --json` and the derived
stage pick it; with no id, the request's own words do (a problem to capture, a ranking, a status
question). An input that fits two flows is asked on a decision sheet, never guessed; a sub-agent
returns `STATE: blocked` with `NOTE: needs-human:` carrying it.

| Flow | Reference | Picked when |
| --- | --- | --- |
| `create` | [specs-flows/create.md](../../references/specs-flows/create.md) | a problem, plan or idea to capture; no spec id |
| `develop` | [specs-flows/develop.md](../../references/specs-flows/develop.md) | stage `captured`, `proposed` or `designed`, or a refine request |
| `execute` | [specs-flows/execute.md](../../references/specs-flows/execute.md) | stage `ready` or `approved`, or a build with tasks still open |
| `conclude` | [specs-flows/conclude.md](../../references/specs-flows/conclude.md) | every task checked, or an explicit close or abandon |
| `triage` | [specs-flows/triage.md](../../references/specs-flows/triage.md) | a ranking of the open front |
| `status` | [specs-flows/status.md](../../references/specs-flows/status.md) | a read of the front or of one spec's state |
| `orchestrate` | [specs-flows/orchestrate.md](../../references/specs-flows/orchestrate.md) | an epic or a list of specs to run through the orchestrator |

`autopilot`, `improve` and `board` are typed-only commands and are never routed here.
**Done when:** exactly one flow is chosen, with its input.

### 2. Load the flow and follow it
Run `cq components read` on the chosen flow's reference from the table above, with its
`../../references/specs-flows/` path. Read the flow whole, once, and follow it from its own `## Workflow` with the input from step 1:
its steps, `Done when:` lines and invariants bind this run exactly as they bound the standalone
command. A `quenching-specs-<flow>` the flow names as the next step is the typed shortcut to
the same reference, and a conductor reaches the same flow by calling this command with `flow` and
the id.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.

## Invariants

- Never run two flows in one invocation; the flow's own next-step block names the following one.
- Never edit what a flow's reference says: a flow's behavior changes in its reference, never here.
- Never route `autopilot`, `improve` or `board`.
