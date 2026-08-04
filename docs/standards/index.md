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
* [git/](git/index.md) — branches de longa duração, o gatilho de publicação, as convenções lidas como read-if-present
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
| [generated-listings.md](architecture/generated-listings.md) | A listing regenerated from disk is a second source of a fact something else already derives, so it earns its keep only where nothing else derives that fact and a checker can decide freshness; the decision criterion is whether a command already answers the same question on demand, the docs/ bundle index.md files are the counterexample that bounds the rule, and a convergence condition may name only what a checker decides |
| [plugin-layout.md](architecture/plugin-layout.md) | commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path |
| [read-only-views.md](architecture/read-only-views.md) | A front's read-only view is a separate command holding no write tools, never a dry-run mode on the command that writes — because allowed-tools is granted per command, so a mode flag can only ever be a promise the grant does not enforce |
| [retiring-a-reserved-artifact.md](architecture/retiring-a-reserved-artifact.md) | A reserved filename that is retired keeps its slot in RESERVED and its skip in the hard block; only its checker goes, because unreserving it silently converts every surviving file into a malformed concept doc |
| [shared-mold-keys.md](architecture/shared-mold-keys.md) | A frontmatter mold cited by several commands is a fill-in invitation, so a key only one writer may legitimately set stays out of it and lives with that writer's own contract — prevention where a deterministic check is not available |
| [spec-backend.md](architecture/spec-backend.md) | Where a repo's specs live is configurable, and the interface that makes every backend behave identically — five primitives over the canonical document rather than one method per CLI verb, a single shared derivation, the selected backend as sole source of truth, hybrid serialisation confined to each external implementation with the whole document (not just the parts it models) as its reassembly obligation, and the in-memory fake that turns "identical" into a checked property |

### automation/

| Doc | Covers |
| --- | --- |
| [agents.md](automation/agents.md) | When work becomes a subagent, the definition contract for .claude/agents/, and how the surface is inventoried |
| [context-budget.md](automation/context-budget.md) | What a command surface costs before anything fires — the two description caps, what the description may carry including the tier for one that is not in context at all, the per-surface ceiling and its two firing modes, and the disable-model-invocation exit that lets a typed-only command cost nothing at all, with the routed/typed-only split that keeps that exit auditable; and the other half — what a body costs once it fires, where every turn re-sends the whole conversation so a block costs tokens × turns remaining |
| [context-discipline.md](automation/context-discipline.md) | The two halves of a run's integral `tokens × turns remaining` and the only two ways to cut it — open less (the declared files rather than the folder, the cited sections rather than the file, N sections in ONE call, and the rules/rationale marker convention) and run for less time (the section boundary as a legitimate stopping point, triggered by an event and never by a threshold); plus the two things measured and refused, segmenting the bundle into more files and deleting rationale to compact it |
| [hooks.md](automation/hooks.md) | Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys |
| [session-evidence.md](automation/session-evidence.md) | How a session transcript is read as evidence for the command that drove it — where transcripts live, the two entry forms, the JSONL-first arm ladder with the arm declared in the output, and the rule that a counted claim comes from code, never from a model recalling its own run |
| [skill-evaluation.md](automation/skill-evaluation.md) | What it takes to claim a skill works — with/without runs in isolated processes, assertions graded on quoted evidence, a rate reported with its fixture, and a delta reported even when it is zero |
| [skills.md](automation/skills.md) | How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point, including the admission criterion that decides whether a command's description stays resident in context or goes typed-only |

### ci-cd/

| Doc | Covers |
| --- | --- |
| [versioning-release.md](ci-cd/versioning-release.md) | Every version string the plugin ships must be bumped together, because two different consumers read two different halves — Claude Code decides an upgrade from the manifest pair, and the three tool constants are the lockstep unit each tool's own selftest holds to — bumped once per spec at conclude, immediately before the merge, never as a task, plus the half a bump cannot do, which is noticing the legacy copies a target still carries under .claude/hooks/ from before resolution went plugin-first, and the seventh version-carrying file that stays outside the six because no consumer reads it |

### code/

| Doc | Covers |
| --- | --- |
| [canonical-set-parsing.md](code/canonical-set-parsing.md) | How the shipped tools consume a declared set — slice it by declared membership and never by position, because an ordinal index is a claim about the set's shape that nothing re-checks when the set grows; why a byte-for-byte lockstep check proves the copies agree but never that the code reading them still means the same thing, so a membership invariant is owed its own assertion; and why a case list must exercise the function that ships rather than a copy of its rule written inside the selftest |
| [frontmatter-parsing.md](code/frontmatter-parsing.md) | The YAML subset the three shipped tools read — the comment rule (a `#` opens a comment only at the start of a value or after whitespace, and never inside a quoted scalar), the canonical case list all three must decide identically, the anomaly set each must be able to name, and the three-copy lockstep obligation that replaces the shared module they cannot have |
| [superseded-format-recognition.md](code/superseded-format-recognition.md) | How a recogniser is changed when the format it reads is superseded — the new pattern must be asserted against the OLD form, because a pattern that describes the new one correctly often matches the old one whole and yields a confident wrong answer with no finding; and a store's recogniser must separate "not mine" from "mine, but stale", because sending both to the same discard makes a half-migrated front vanish in silence |

### git/

| Doc | Covers |
| --- | --- |
| [branching.md](git/branching.md) | A main acumulava duas funções que este standard separa — develop como branch de integração onde as specs mergeiam, main como canal de publicação que só recebe o merge deliberado develop → main — o gatilho por demanda e sem cadência, a pergunta que empurra para o agrupamento quando develop carrega um só merge desde a última tag, a publicação sempre local, e os dois consumidores que leem os nomes das branches declarados em .claude/quenching.json |

### naming/

| Doc | Covers |
| --- | --- |
| [command-surface.md](naming/command-surface.md) | How the plugin's commands are named and namespaced — one file per entry point, where the path is the identity |

### quality/

| Doc | Covers |
| --- | --- |
| [bundle-verification.md](quality/bundle-verification.md) | What the docs/ front machine-checks versus what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check, where an accepted gap is recorded, and the resource glob-set format |
| [computed-fact-prose-fanout.md](quality/computed-fact-prose-fanout.md) | Any fact a tool computes and prose restates — a schema's fields, a surface's command count — fans out the moment it changes, and no checker sees it: why the validators are blind by construction, the two independent measurements this rule was set from, the grep on the fact's spelled-out form that finds the sites while the change is still cheap, and why it belongs to the task that makes the change rather than to a later sweep |
| [parse-honesty.md](quality/parse-honesty.md) | A verifier names its own parse failure instead of reporting it as a content gap — the sidecar shape that adds the signal without changing a return type, why the finding is a warn rather than an error, and the rule that a checker never gains a lossy transform without the diagnostic that reports it |
| [prose-sweeps.md](quality/prose-sweeps.md) | A find-and-replace over prose corrupts exactly the sentences that talk ABOUT the form being replaced — how to recognise those sites, why the check written to guard the sweep cannot see them, and the mitigation that survives both |
| [selftest-mutation.md](quality/selftest-mutation.md) | A selftest that has never been observed to fail is an untested test — the mutation pass that earns the claim, one mutation per rule the fixture exists to prove, why the pass is run once at authoring rather than wired into CI, and the graduation gate this repo's three shipped selftests have not yet cleared |
| [surface-verification.md](quality/surface-verification.md) | How a change to the command surface is proven — a fresh process because the registry is built at session start, assertions on captured tool_use rather than prose, the five preconditions a functional check must satisfy to measure what it claims, why the harness belongs to the skill front rather than the spec cycle and how to scope its cost, and how an ordering property is verified by running a real cycle |
| [unproven-capability-warning.md](quality/unproven-capability-warning.md) | Where a caveat about a capability that ships without end-to-end proof belongs — the two failure shapes that decide it, the standing fact as a verifier finding and the moment-of-risk line once per process on stderr, why a per-operation warning is a permanent context tax and silence is not the alternative, and the one edit that retires both together |
| [withdrawn-contract-residue.md](quality/withdrawn-contract-residue.md) | When a change removes a contract rather than changing a computed value, its prose residue has no canonical spelling to grep for — the sites assert it in their own words — so `## Impact` must name the CLASS of documents that assert it and derive the file list mechanically; the five misses measured on one branch, why naming the file is not enough either, and why the reviewer's question is "what did this make false?" rather than "which files changed?" |

### workflows/

| Doc | Covers |
| --- | --- |
| [plan-artifacts.md](workflows/plan-artifacts.md) | The one-file spec, its fourteen canonical sections, the phase-scoped explicit-none rule, the parsed Impact sub-heading, the duplicated template and the three-copy record vocabulary, and how to read a v1 plan in specs/archive/ |
| [plan-git-record.md](workflows/plan-git-record.md) | How a plan's work is recorded in git — the commit sha as the task→commit anchor where the spec no longer shares a branch with the code, the commit subject as the anchor a co-branching spec still needs, the branch and merge frontmatter records, the pull-request route and the `pr` field it alone writes, why every record is written before the thing it describes, the squash caveat, the merge that runs via git -C in the base's own checkout and the worktree removed after it, and the read-if-present contract for a target's own docs/standards/git/ |
| [plan-lifecycle.md](workflows/plan-lifecycle.md) | The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, and the append-only archive rule for facts that did not exist at the move |
| [plugin-configuration.md](workflows/plugin-configuration.md) | `.claude/quenching.json` as the plugin's single configuration home — where it lives and why it left the specs workspace, the five recognised keys and their defaults, the one key that deliberately has none and refuses instead, the one key a second tool reads and why it had nowhere else to live, why every other way it can be wrong is a field rather than an exception, and why a stranded `specs/config.json` is named instead of merged |
| [task-execution.md](workflows/task-execution.md) | How a spec's task is executed — the verification policies, `verify:` scoped at authoring, the failure budget, commit-per-task, the two-level review split, the four-event Handoff refresh cadence, and the delegation and [P] disjunction rules |
| [worktree-setup.md](workflows/worktree-setup.md) | The `worktreeSetup` hook — what it is for, where it is declared now that the plugin's config moved to `.claude/quenching.json`, what its absence means, who runs the declared command and with which cwd, why the consent is the isolation offer rather than a prompt of its own, and the record of why the specs front took a config file at all |
<!-- END GENERATED -->
