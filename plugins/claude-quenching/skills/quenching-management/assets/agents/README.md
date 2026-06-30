# assets/agents/ — sub-agent payloads of the method

The **worker sub-agents** the [`quenching-management`](../../SKILL.md) method
installs live here. By the doctrine of dimension 7, a sub-agent *"does that work
in its own context and returns only the summary"* (Claude Code docs): runs in
**isolated context** and returns only the **condensed summary**, keeping the
main thread clean when the scan/authoring would flood the window. Every agent
here declares an **explicit `tools:`** (least-privilege — omitting it inherits
ALL tools from the parent) and a `model:` suited to the task (`haiku` for cheap
scanning, `opus` for heavy reasoning).

> **Not "active" in this skill.** They live under `assets/` (≥2 levels below),
> so Claude Code **does not** discover them as live sub-agents — they are
> **payloads**, copied to `.claude/agents/` of the target when the method is
> applied.

## Inventory

| Path | Type | Installs in | Addresses |
| --- | --- | --- | --- |
| `quenching-auditor.md` | sub-agent (worker) | `.claude/agents/` of target | 7 + READ-ONLY audit fan-out (Steps 1-7); returns Present/Partial/Drifted/Absent scorecard with `file:line`, never the dump |
| `quenching-writer.md` | sub-agent (worker) | `.claude/agents/` of target | 2 + AUTHORING fan-out: one worker per `standards/` topic, parallel; mines repo for `current` anchored at `file:line` + researches references; unimplemented gap becomes PROPOSAL, never current |

These are **method workers**: the fan-out of the `quenching-reaudit`,
`quenching-roadmap` and `quenching-standards` skills references them via
`agent:`, so they **accompany the installation** into `.claude/agents/` of the
target repo. Without them installed, the `agent:` of those skills points to
nothing.

> **Method meta-agents are NOT here.** The two agents that develop the **method
> itself** (`quenching-evolutionist` / `quenching-reviewer`) are **maintainer
> tooling** and, by doctrine, are **never installed into a target repo**. They
> live outside this shipped package, at the repository root
> (`.claude/agents/`), and are documented in the project's `CONTRIBUTING.md`.

## How to install (summary)

1. **Copy** the workers (`quenching-auditor.md`, `quenching-writer.md`) to
   `.claude/agents/` of the target.
2. **Rename** `name`/file to the derived taxonomy (`<prefix>`) and **translate**
   the `description` to the repo's language — it is **routing code** (dim 6/7).
3. **Keep the `tools:` minimal** and the `model:` appropriate; if the target
   already had an equivalent auditor/writer, point the skills' `agent:` to it
   and **deprecate** the duplicate (do not remove without OK).
4. **Fix** internal paths (detection reference, `docs/` skeletons) to the
   derived shape in Step 0 of
   [../../references/detection-and-smells.md](../../references/detection-and-smells.md).
