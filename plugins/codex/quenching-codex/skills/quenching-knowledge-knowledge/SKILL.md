---
name: quenching-knowledge-knowledge
description: "Run one knowledge flow on the OKF bundle (add, learn, define, import, align, status, documentation). Use for \"add a standard\", \"define this term\", \"align the docs\". Not for: specs → quenching-specs-specs."
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/knowledge.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-knowledge-knowledge — one entry point for the knowledge flows

**Input**: `$ARGUMENTS` — an optional flow name, then what that flow takes. The remaining words go to the flow untouched.

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
flow's input. No flow named → the request's own words pick it. An input that fits two flows is asked on a decision sheet, never guessed; a sub-agent
returns `STATE: blocked` with `NOTE: needs-human:` carrying it.

| Flow | Reference | Picked when |
| --- | --- | --- |
| `add` | [knowledge-flows/add.md](../../references/knowledge-flows/add.md) | a new concept doc (standard, table, announcement) for the bundle |
| `learn` | [knowledge-flows/learn.md](../../references/knowledge-flows/learn.md) | one piece of generic knowledge to record in `concepts/` |
| `define` | [knowledge-flows/define.md](../../references/knowledge-flows/define.md) | one glossary term to add or refine |
| `glossary-backfill` | [knowledge-flows/glossary-backfill.md](../../references/knowledge-flows/glossary-backfill.md) | a sweep of the whole bundle for missing glossary terms |
| `import` | [knowledge-flows/import.md](../../references/knowledge-flows/import.md) | an external source (files, folders, URLs) to ingest as many docs |
| `import-memory` | [knowledge-flows/import-memory.md](../../references/knowledge-flows/import-memory.md) | the host memory to drain into the bundle and clear |
| `align` | [knowledge-flows/align.md](../../references/knowledge-flows/align.md) | forcing `/docs/` into the canonical bundle |
| `status` | [knowledge-flows/status.md](../../references/knowledge-flows/status.md) | a read-only report of where the bundle stands |
| `documentation-plan` | [knowledge-flows/documentation-plan.md](../../references/knowledge-flows/documentation-plan.md) | a sourced documentation plan with reader journeys |
| `documentation-write` | [knowledge-flows/documentation-write.md](../../references/knowledge-flows/documentation-write.md) | pages to write from a documentation plan |
| `documentation-review` | [knowledge-flows/documentation-review.md](../../references/knowledge-flows/documentation-review.md) | a score of documentation pages against the quality gate |
| `documentation-build` | [knowledge-flows/documentation-build.md](../../references/knowledge-flows/documentation-build.md) | the Zensical site layer, navigation or strict build |
| `documentation-produce` | [knowledge-flows/documentation-produce.md](../../references/knowledge-flows/documentation-produce.md) | the whole documentation pipeline in one run |


**Done when:** exactly one flow is chosen, with its input.

### 2. Load the flow and follow it
Run `cq components read` on the chosen flow's reference from the table above, with its
`../../references/knowledge-flows/` path. Read the flow whole, once, and follow it from its own `## Workflow` with the input from step 1:
its steps, `Done when:` lines and invariants bind this run exactly as they bound the standalone
command. A `quenching-knowledge-<flow>` the flow names as the next step is the typed shortcut to
the same reference, and a conductor reaches the same flow by calling this command with the flow name and
the input.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.

## Invariants

- Never run two flows in one invocation; the flow's own next-step block names the following one.
- Never edit what a flow's reference says: a flow's behavior changes in its reference, never here.
