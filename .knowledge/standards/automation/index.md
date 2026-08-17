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
| [context-discipline.md](context-discipline.md) | The two halves of a run's integral and the three ways to cut it — open less (declared files, cited sections, N in one call, the block inside a section, the rules/rationale markers), run for less time (the section boundary), and emit fewer turns per unit of work (the batching contract, and the ban on a turn that only announces the next tool call), plus segmenting and deleting rationale as measured refusals |
| [extension-points.md](extension-points.md) | The extension point a command declares for the repository's own work — the three-part contract (config read, never interpreted; the body announces and moves on; `condition` never evaluated by whoever announces) and why the extension lives in config, not in a command |
| [hooks.md](hooks.md) | Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys |
| [plan-gates.md](plan-gates.md) | Quando o gate de plano de um comando pode cair — as duas classes protegidas são o teste inteiro, o que substitui a janela de aprovação quando o gate sai, e as três formas intermediárias rejeitadas |
| [session-evidence.md](session-evidence.md) | How a session transcript is read as evidence for the command that drove it — where transcripts live, the two entry forms, the JSONL-first arm ladder, and the rule that a counted claim comes from code, never a model recalling its own run |
| [skill-evaluation.md](skill-evaluation.md) | What it takes to claim a skill works — with/without runs in isolated processes, assertions graded on quoted evidence, a rate reported with its fixture, and a delta reported even when it is zero |
| [skills.md](skills.md) | How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point |
