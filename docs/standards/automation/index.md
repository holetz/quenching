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
| [context-discipline.md](context-discipline.md) | The two halves of a run's integral and the only two ways to cut it — open less (declared files, cited sections, N in one call, the rules/rationale markers) and run for less time (the section boundary), plus segmenting and deleting rationale as measured refusals |
| [hooks.md](hooks.md) | Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys |
| [session-evidence.md](session-evidence.md) | How a session transcript is read as evidence for the command that drove it — where transcripts live, the two entry forms, the JSONL-first arm ladder, and the rule that a counted claim comes from code, never a model recalling its own run |
| [skill-evaluation.md](skill-evaluation.md) | What it takes to claim a skill works — with/without runs in isolated processes, assertions graded on quoted evidence, a rate reported with its fixture, and a delta reported even when it is zero |
| [skills.md](skills.md) | How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point |
