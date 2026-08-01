# `standards/` — current/active reference, OUR contracts

The current/active **standard/contract** — "how it should be and why", versioned, the
shared source of truth. One standard per file; subfolder names by **subject**. Each
concept doc carries `type: standard` + a derived `resource:` (the repo scope it governs).

**Boundary:** `standards/` = "how **WE** do it (current/active)". Distinct from
[reference/](/docs/reference/index.md) (external facts we consume) and
[catalog/](/docs/catalog/index.md) (our data). Direction lives in
[vision/](/docs/vision/index.md). An **agreed-but-unproven** rule sits here as
`authority: background` and graduates to `current` once proven — there is no separate decisions
home.

Keep only the subtopics that apply to the repo; within each, break standards **one
concept per file** by considering the candidate sub-standards catalog (a
**consideration** checklist, evidence-gated generation, recorded deferral — not a blind
generate list). The **agent-facing pointer** for this home is [CLAUDE.md](CLAUDE.md)
(auto-loaded).

## Subtopics

* [agents/](agents/index.md) — how we instruct agents: the language our prose is written in, and the conduct expected of the agent writing it
* [architecture/](architecture/index.md) — system structure + architectural patterns (patterns live here)
* [automation/](automation/index.md) — the Claude Code skill + command surface (classification, authoring, alignment)
* [code/](code/index.md) — code conventions, imports, lint, pins, SYMBOL naming
* [naming/](naming/index.md) — naming conventions (here: the command surface)
* [data-modeling/](data-modeling/index.md) — grain, key, joins, catalog/schema choice
* [ci-cd/](ci-cd/index.md) — build/deploy, "code defines YAML", manifest generation
* [workflows/](workflows/index.md) — job/task/schema framework, job parameters
* [mlops/](mlops/index.md) — model lifecycle, lineage, regulatory interface
* [quality/](quality/index.md) — data quality, drift/stability, model monitoring
* [platform/](platform/index.md) — deploy targets, permissions/governance, external services

## Current docs

<!-- BEGIN GENERATED: rebuilt from disk by `quenching-docs-align`/`quenching-docs-add` — DO NOT edit by hand.
     Scans standards/**/*.md, reads title/description/timestamp/type, grouped by subject subfolder.
     Row model per subfolder:
       ### code/
       | Doc | Covers |
       | --- | --- |
       | [imports.md](code/imports.md) | <the doc's description:> |
-->
### agents/

| Doc | Covers |
| --- | --- |
| [communication.md](agents/communication.md) | The language this repo declares for the prose its agents author — one BCP-47 tag on the root harness line, governing artifact and conversation alike — and the conduct contract that holds whether or not a language is declared |

### architecture/

| Doc | Covers |
| --- | --- |
| [align-surface.md](architecture/align-surface.md) | The 1×4 align column that replaced the 2×4 matrix — one align per front carrying its content stages, the probe-before-inventory rule that makes a no-op align cost a couple of tool calls, and the rule that no sweep records itself: an align's account of its own run goes in the report, never into the bundle |
| [generated-listings.md](architecture/generated-listings.md) | A derived listing only pays for itself when a program can prove it is fresh — the decision criterion is whether a command already answers the same question on demand, the docs/ bundle index.md files are the counterexample that bounds the rule, and a convergence condition may name only what a checker decides |
| [plugin-layout.md](architecture/plugin-layout.md) | commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path |
| [read-only-views.md](architecture/read-only-views.md) | A front's read-only view is a separate command holding no write tools, never a dry-run mode on the command that writes — because allowed-tools is granted per command, so a mode flag can only ever be a promise the grant does not enforce |
| [retiring-a-reserved-artifact.md](architecture/retiring-a-reserved-artifact.md) | A reserved filename that is retired keeps its slot in RESERVED and its skip in the hard block; only its checker goes, because unreserving it silently converts every surviving file into a malformed concept doc |
| [shared-mold-keys.md](architecture/shared-mold-keys.md) | A frontmatter mold cited by several commands is a fill-in invitation, so a key only one writer may write stays out of it and lives with that writer's own contract — prevention where a deterministic check is not available |

### automation/

| Doc | Covers |
| --- | --- |
| [agents.md](automation/agents.md) | When work becomes a subagent, the definition contract for .claude/agents/, and how the surface is inventoried |
| [context-budget.md](automation/context-budget.md) | What a command surface costs before anything fires — the two description caps, what the description may carry, and the per-surface ceiling |
| [context-discipline.md](automation/context-discipline.md) | The two halves of a run's integral `tokens × turns remaining` and the only two ways to cut it — open less (the declared files rather than the folder, the cited sections rather than the file, N sections in ONE call, and the rules/rationale marker convention) and run for less time (the section boundary as a legitimate stopping point, triggered by an event and never by a threshold); plus the two things measured and refused, segmenting the bundle into more files and deleting rationale to compact it |
| [hooks.md](automation/hooks.md) | Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys |
| [session-evidence.md](automation/session-evidence.md) | How a session transcript is read as evidence for the command that drove it — where transcripts live, the two entry forms, the JSONL-first arm ladder with the arm declared in the output, and the rule that a counted claim comes from code, never from a model recalling its own run |
| [skill-evaluation.md](automation/skill-evaluation.md) | What it takes to claim a skill works — with/without runs in isolated processes, assertions graded on quoted evidence, a rate reported with its fixture, and a delta reported even when it is zero |
| [skills.md](automation/skills.md) | How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point |

### ci-cd/

| Doc | Covers |
| --- | --- |
| [versioning-release.md](ci-cd/versioning-release.md) | Every version string the plugin ships must be bumped together, because two different consumers read two different halves — Claude Code decides an upgrade from the manifest pair, and each installing align compares its own tool's --version against the copy already installed in a target repo — plus the half a bump cannot do, which is noticing that a target's copy has fallen behind, run ahead, or sits on disk with nothing invoking it |

### code/

| Doc | Covers |
| --- | --- |
| [canonical-set-parsing.md](code/canonical-set-parsing.md) | How the shipped tools consume a declared set — slice it by declared membership and never by position, because an ordinal index is an unchecked claim about the set's shape; why a byte-for-byte lockstep check proves the copies agree but never that the code reading them still means the same thing, so a membership invariant is owed its own assertion; and why a case list must exercise the function that ships rather than a copy of its rule written inside the selftest |
| [frontmatter-parsing.md](code/frontmatter-parsing.md) | The YAML subset the three shipped tools read — the comment rule (a `#` opens a comment only at the start of a value or after whitespace, and never inside a quoted scalar), the canonical case list all three must decide identically, the anomaly set each must be able to name, and the three-copy lockstep obligation that replaces the shared module they cannot have |

### naming/

| Doc | Covers |
| --- | --- |
| [command-surface.md](naming/command-surface.md) | How the plugin's commands are named and namespaced — one file per entry point, where the path is the identity |

### quality/

| Doc | Covers |
| --- | --- |
| [bundle-verification.md](quality/bundle-verification.md) | What the docs/ front machine-checks versus what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check, where an accepted gap is recorded, and the resource glob-set format |
| [parse-honesty.md](quality/parse-honesty.md) | A verifier names its own parse failure instead of reporting it as a content gap — the sidecar shape that adds the signal without changing a return type, why the finding is a warn rather than an error, and the rule that a checker never gains a lossy transform without the diagnostic that reports it |
| [prose-sweeps.md](quality/prose-sweeps.md) | A mechanical find-and-replace over prose corrupts exactly the sentences that talk about the form being swept — why the checker written to guard the sweep reports those sites clean, why the distinction between using a form and mentioning it belongs to the branch review, and the placeholder form that is immune to both |
| [selftest-mutation.md](quality/selftest-mutation.md) | A selftest that has never been observed to fail is an untested test — the mutation pass that earns the claim, one mutation per rule the fixture exists to prove, why the pass is run once at authoring rather than wired into CI, and the graduation gate this repo's three shipped selftests have not yet cleared |
| [surface-verification.md](quality/surface-verification.md) | How a change to the command surface is proven — a fresh process because the registry is built at session start, assertions on captured tool_use rather than prose, the five preconditions a functional check must satisfy to measure what it claims, and how an ordering property is verified by running a real cycle |

### workflows/

| Doc | Covers |
| --- | --- |
| [plan-artifacts.md](workflows/plan-artifacts.md) | The one-file spec, its fourteen canonical sections, the phase-scoped explicit-none rule, the parsed Impact sub-heading, the duplicated template and the three-copy record vocabulary, and how to read a v1 plan in specs/archive/ |
| [plan-git-record.md](workflows/plan-git-record.md) | How a plan's work is recorded in git — the commit subject as the task→commit anchor, the branch and merge frontmatter records, why every record is written before the thing it describes, the squash caveat, the merge that runs via git -C in the base's own checkout and the worktree removed after it, and the read-if-present contract for a target's own docs/standards/git/ |
| [plan-lifecycle.md](workflows/plan-lifecycle.md) | The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, and the append-only archive rule for facts that did not exist at the move |
| [task-execution.md](workflows/task-execution.md) | How a spec's task is executed — the verification policies, the failure budget, commit-per-task, the two-level review split, and the delegation and [P] disjunction rules |
| [worktree-setup.md](workflows/worktree-setup.md) | The specs/config.json contract — the one recognised key, where the file lives, what its absence means, who runs the declared command and with which cwd, and why the consent is the isolation offer rather than a prompt of its own |
<!-- END GENERATED -->
