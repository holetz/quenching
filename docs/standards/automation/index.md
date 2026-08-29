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
| [context-discipline.md](context-discipline.md) | The two halves of a run's integral `tokens × turns remaining` and the three ways to cut it — open less (the declared files rather than the folder, the cited sections rather than the file, N sections in ONE call, the block rather than the section where a section has blocks, and the rules/rationale marker convention), run for less time (the section boundary as a legitimate stopping point, triggered by an event and never by a threshold), and emit fewer turns per unit of work (the batching contract, and the ban on a turn that exists only to announce the next tool call); plus the two things measured and refused, segmenting the bundle into more files and deleting rationale to compact it |
| [dependency-sweep.md](dependency-sweep.md) | The contract of the sub-agent dependency sweep that runs at the open of a /quenching:specs:develop pass, before it asks anything — trigger, tool profile, deliverable, and the persistence of the map with the date it carries |
| [extension-points.md](extension-points.md) | The extension point — an event a command declares for the repository that installed the plugin to attach its own work; the three-part contract (the declaration lives in config the core reads and never interprets; the body announces name, command and prompt and moves on; `condition` is never evaluated by whoever announces); the declared shape; and why the extension lives in config rather than in a command |
| [hooks.md](hooks.md) | Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys |
| [plan-gates.md](plan-gates.md) | The two protected classes — a code-coupled item, an irreversible cycle action — are the whole test, and a command in which neither occurs has nothing to confirm; what replaces the approval window when the gate goes (the record's URL, announced before any read and repeated in the report), the difference between the confirmation that drops and the consolidation that stays, what still stops the pass either way, the three intermediate forms measured and rejected, and the three conditions under which a gear's authority replaces the person at the go/no-go |
| [session-evidence.md](session-evidence.md) | How a session transcript is read as evidence for the command that drove it — where transcripts live, the two entry forms, the JSONL-first arm ladder with the arm declared in the output, and the rule that a counted claim comes from code, never from a model recalling its own run |
| [skill-evaluation.md](skill-evaluation.md) | What it takes to claim a skill works — with/without runs in isolated processes, assertions graded on quoted evidence, a rate reported with its fixture, and a delta reported even when it is zero |
| [skills.md](skills.md) | How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point, including the admission criterion that decides whether a command's description stays resident in context or goes typed-only |
