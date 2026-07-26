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
| [context-budget.md](context-budget.md) | What the skill surface costs before anything fires — the two description caps, what `when_to_use` may carry, and the per-surface ceiling |
| [skill-evaluation.md](skill-evaluation.md) | What it takes to claim a skill works — with/without runs, evidence-backed grading, and a reported delta |
| [skills.md](skills.md) | How the plugin's skills are classified, authored, named, mirrored as commands, and swept into conformance |
