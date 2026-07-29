# `standards/automation/`

How this repo's Claude Code **automation surface** — skills and their command wrappers — is
classified, named, authored, and swept into conformance.

**Boundary:** `automation/` governs the `.claude/`-style skill + command surface (here, the
plugin's own `skills/` + `commands/`). The naming of the commands themselves lives one level over
in [../naming/command-surface.md](../naming/command-surface.md); code conventions live in
[../code/](../code/index.md). One standard per file; each carries `type: standard` + a derived
`resource:`.

## Current docs

| Doc | Covers |
| --- | --- |
| [agents.md](agents.md) | When work becomes a subagent, the definition contract for .claude/agents/, and how the surface is inventoried |
| [context-budget.md](context-budget.md) | What a command surface costs before anything fires — the two description caps, what the description may carry, and the per-surface ceiling |
| [hooks.md](hooks.md) | Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys |
| [skill-evaluation.md](skill-evaluation.md) | What it takes to claim a skill works — with/without runs in isolated processes, assertions graded on quoted evidence, a rate reported with its fixture, and a delta reported even when it is zero |
| [skills.md](skills.md) | How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point |
