# `standards/` — current/active reference, OUR contracts

The current/active **standard/contract** — "how it should be and why", versioned, the
shared source of truth. One standard per file; subfolder names by **subject**. Each
concept doc carries `type: standard` + a derived `resource:` (the repo scope it governs).

**Boundary:** `standards/` = "how **WE** do it (current/active)". Distinct from
[reference/](/.docs/reference/index.md) (external facts we consume) and
[catalog/](/.docs/catalog/index.md) (our data). Direction lives in
[vision/](/.docs/vision/index.md). An **agreed-but-unproven** rule sits here as
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

<!-- BEGIN GENERATED: rebuilt from disk by `quenching-knowledge-align`/`quenching-knowledge-add` — DO NOT edit by hand.
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
| [align-surface.md](architecture/align-surface.md) | The 1×4 align column that replaced the 2×4 matrix — one align per front carrying its content stages, the probe-before-inventory rule that makes a no-op align cost a couple of tool calls, the rule that no sweep records itself: an align's account of its own run goes in the report, never into the bundle, and the two conductor categories sharing the cycle-authorization contract — `/align` conducts the three fronts, `/quenching:specs:orchestrate` conducts the four stages of one spec, and neither reimplements what it conducts |
| [generated-listings.md](architecture/generated-listings.md) | A listing regenerated from disk is a second source of a fact something else already derives, so it earns its keep only where nothing else derives that fact and a checker can decide freshness; the decision criterion is whether a command already answers the same question on demand, the /.docs/ bundle index.md files are the counterexample that bounds the rule, and a convergence condition may name only what a checker decides |
| [install-profiles.md](architecture/install-profiles.md) | A profile declares which of the three fronts a repository uses, in `.claude/quenching.json` — what it turns on and off is the residency of a front's command descriptions (`disable-model-invocation: true`), never a command or a file, and the `/align` conductor runs the installed fronts in dependency order and names an uninstalled one in its report instead of failing on it |
| [plugin-layout.md](architecture/plugin-layout.md) | commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path |
| [read-only-views.md](architecture/read-only-views.md) | A front's read-only view is a separate command holding no write tools, never a dry-run mode on the command that writes — because allowed-tools is granted per command, so a mode flag can only ever be a promise the grant does not enforce |
| [reference-loading.md](architecture/reference-loading.md) | Um corpo que precisa de uma seção de reference no passo N carrega essa seção no passo N, com a invocação literal e copiável de cq components read — uma citação de preâmbulo diz onde a regra mora e não faz a sessão abrir o arquivo, e o oposto foi medido acontecendo nos oito corpos /quenching:specs:* |
| [report-mold.md](architecture/report-mold.md) | A forma em que os comandos de uma frente imprimem seu relatório pertence a UMA seção citada por todos — três bandas fixas, um conjunto ordenado de colunas do qual cada comando toma um subconjunto, e um bloco de próximo passo executável como impresso — porque um formato reescrito em oito corpos envelhece em sete e nenhum checker vê |
| [retiring-a-reserved-artifact.md](architecture/retiring-a-reserved-artifact.md) | A reserved filename that is retired keeps its slot in RESERVED and its skip in the hard block; only its checker goes, because unreserving it silently converts every surviving file into a malformed concept doc — plus the one departure this house made knowingly, and the three things that made it payable |
| [shared-mold-keys.md](architecture/shared-mold-keys.md) | A frontmatter mold cited by several commands is a fill-in invitation, so a key only one writer may legitimately set stays out of it and lives with that writer's own contract — prevention where a deterministic check is not available |
| [spec-backend.md](architecture/spec-backend.md) | Where a repo's specs live is configurable, and the interface that makes every backend behave identically — five primitives over the canonical document rather than one method per CLI verb, a single shared derivation, the selected backend as sole source of truth, hybrid serialisation confined to each external implementation with the whole document (not just the parts it models) as its reassembly obligation, rendering derived state onto a native surface as a third category beside projection and storage, the receipt a tolerant slug resolution owes every payload and why it is folded in at a choke point rather than written verb by verb, and the in-memory fake that turns "identical" into a checked property |

### automation/

| Doc | Covers |
| --- | --- |
| [agents.md](automation/agents.md) | When work becomes a subagent, the definition contract for .claude/agents/, and how the surface is inventoried |
| [context-discipline.md](automation/context-discipline.md) | The two halves of a run's integral `tokens × turns remaining` and the only two ways to cut it — open less (the declared files rather than the folder, the cited sections rather than the file, N sections in ONE call, and the rules/rationale marker convention) and run for less time (the section boundary as a legitimate stopping point, triggered by an event and never by a threshold); plus the two things measured and refused, segmenting the bundle into more files and deleting rationale to compact it |
| [extension-points.md](automation/extension-points.md) | The extension point — an event a command declares for the repository that installed the plugin to attach its own work; the three-part contract (the declaration lives in config the core reads and never interprets; the body announces name, command and prompt and moves on; `condition` is never evaluated by whoever announces); the declared shape; and why the extension lives in config rather than in a command |
| [hooks.md](automation/hooks.md) | Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys |
| [session-evidence.md](automation/session-evidence.md) | How a session transcript is read as evidence for the command that drove it — where transcripts live, the two entry forms, the JSONL-first arm ladder with the arm declared in the output, and the rule that a counted claim comes from code, never from a model recalling its own run |
| [skill-evaluation.md](automation/skill-evaluation.md) | What it takes to claim a skill works — with/without runs in isolated processes, assertions graded on quoted evidence, a rate reported with its fixture, and a delta reported even when it is zero |
| [skills.md](automation/skills.md) | How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point, including the admission criterion that decides whether a command's description stays resident in context or goes typed-only |

### ci-cd/

| Doc | Covers |
| --- | --- |
| [versioning-release.md](ci-cd/versioning-release.md) | Every version string the plugin ships must be bumped together, because two different consumers read two different halves — Claude Code decides an upgrade from the manifest pair, and the one shared version module is what every pillar's --version reads — bumped once per release, at the develop → main merge, never at conclude and never as a task |

### code/

| Doc | Covers |
| --- | --- |
| [canonical-set-parsing.md](code/canonical-set-parsing.md) | How the shipped tools consume a declared set — slice it by declared membership and never by position, because an ordinal index is a claim about the set's shape that nothing re-checks when the set grows; why a byte-for-byte lockstep check proves the copies agree but never that the code reading them still means the same thing, so a membership invariant is owed its own assertion; and why a case list must exercise the function that ships rather than a copy of its rule written inside the selftest |
| [file-relative-path-resolution.md](code/file-relative-path-resolution.md) | Every `__file__`-relative expression silently encodes how deep its module sits; moving a script into a package re-evaluates it somewhere else without erroring, and the two instances this repo measured failed in opposite directions — one turned a lockstep check off and exited 0, the other made a subcommand refuse forever |
| [frontmatter-parser.md](code/frontmatter-parser.md) | The YAML subset `common/frontmatter.py` reads — the comment rule (a `#` opens a comment only at the start of a value or after whitespace, and never inside a quoted scalar), the canonical case list its tests hold it to, the anomaly sidecar, and why the union it now reads is wider than any of the three parsers it replaced |
| [superseded-format-recognition.md](code/superseded-format-recognition.md) | How a recogniser is changed when the format it reads is superseded — the new pattern must be asserted against the OLD form, because a pattern that describes the new one correctly often matches the old one whole and yields a confident wrong answer with no finding; and a store's recogniser must separate "not mine" from "mine, but stale", because sending both to the same discard makes a half-migrated front vanish in silence |

### git/

| Doc | Covers |
| --- | --- |
| [branching.md](git/branching.md) | A main acumulava duas funções que este standard separa — develop como branch de integração onde as specs mergeiam, main como canal de publicação que só recebe o merge deliberado develop → main — o gatilho por demanda e sem cadência, a pergunta que empurra para o agrupamento quando develop carrega um só merge desde a última tag, a publicação sempre local, e os dois consumidores que leem os nomes das branches declarados em .claude/quenching.json |

### naming/

| Doc | Covers |
| --- | --- |
| [command-surface.md](naming/command-surface.md) | How the plugin's commands are named and namespaced — one file per entry point, where the path is the identity; the components front's four sibling contexts, each named for the artifact it mints, and the rule that keeps a front-level verb off an artifact-level context |

### quality/

| Doc | Covers |
| --- | --- |
| [bundle-verification.md](quality/bundle-verification.md) | What the knowledge front machine-checks versus what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check, where an accepted gap is recorded, and the resource glob-set format |
| [computed-fact-prose-fanout.md](quality/computed-fact-prose-fanout.md) | Any fact a tool computes and prose restates — a schema's fields, a surface's command count — fans out the moment it changes, and no checker sees it: why the validators are blind by construction, the two independent measurements this rule was set from, the grep on the fact's spelled-out form that finds the sites while the change is still cheap, and why it belongs to the task that makes the change rather than to a later sweep |
| [parse-honesty.md](quality/parse-honesty.md) | A verifier names its own parse failure instead of reporting it as a content gap — the sidecar shape that adds the signal without changing a return type, why the finding is a warn rather than an error, and the rule that a checker never gains a lossy transform without the diagnostic that reports it |
| [prose-deletion-seams.md](quality/prose-deletion-seams.md) | Removing prose damages the text left behind, not only the text never opened — the hard wrap makes the line a unit the sentence does not respect, an orphaned continuation is promoted under the neighbouring bullet rather than left as litter, and a grant's justification outlives the use that earned it; the three seams measured on one branch, why every checker stays green through all three, and the reading that closes them |
| [prose-sweeps.md](quality/prose-sweeps.md) | A find-and-replace over prose corrupts exactly the sentences that talk ABOUT the form being replaced — how to recognise those sites, why the check written to guard the sweep cannot see them, and the mitigation that survives both |
| [self-matching-guards.md](quality/self-matching-guards.md) | A checker whose finding text quotes the pattern it prohibits will match itself — the self-accusation this repo measured on its first run, why the fix is parsing the construct rather than excluding the checker, and the narrow case where a substring scan is still honest |
| [selftest-mutation.md](quality/selftest-mutation.md) | A test that has never been observed to fail is untested — the mutation pass that earns the claim, one mutation per rule the fixture exists to prove, why the pass is run once at authoring rather than wired into CI, and the graduation gate the repo's new tests/ suite has not yet cleared |
| [surface-verification.md](quality/surface-verification.md) | How a change to the command surface is proven — a fresh process because the registry is built at session start, assertions on captured tool_use rather than prose, the five preconditions a functional check must satisfy to measure what it claims, why the harness belongs to the components front rather than the spec cycle and how to scope its cost, and how an ordering property is verified by running a real cycle |
| [unproven-capability-warning.md](quality/unproven-capability-warning.md) | Where a caveat about a capability that ships without end-to-end proof belongs — the two failure shapes that decide it, the standing fact as a verifier finding and the moment-of-risk line once per process on stderr, why a per-operation warning is a permanent context tax and silence is not the alternative, and the one edit that retires both together |
| [withdrawn-contract-residue.md](quality/withdrawn-contract-residue.md) | When a change removes a contract rather than changing a computed value, its prose residue has no canonical spelling to grep for — the sites assert it in their own words — so `## Impact` must name the CLASS of documents that assert it and derive the file list mechanically; the five misses measured on one branch, why naming the file is not enough either, and why the reviewer's question is "what did this make false?" rather than "which files changed?" |

### workflows/

| Doc | Covers |
| --- | --- |
| [agent-choice-catalogues.md](workflows/agent-choice-catalogues.md) | The one shape `subjects`, `tagCatalog` and `workItemTypes` all share — an abstract key mapping to a human-facing description an agent reads to PROPOSE and a human CONFIRMS — why the three converged on it independently, the one invariant that shape enforces on every consumer, and why a fourth catalogue should reuse it rather than invent its own review mechanism |
| [plan-artifacts.md](workflows/plan-artifacts.md) | The one-file spec, its fourteen canonical sections, the phase-scoped explicit-none rule, the parsed Impact sub-heading, the duplicated template and the three-copy record vocabulary, and how to read a v1 plan in /.specs/archive/ |
| [plan-git-record.md](workflows/plan-git-record.md) | How a plan's work is recorded in git — the commit sha as the task→commit anchor where the spec no longer shares a branch with the code, the commit subject as the anchor a co-branching spec still needs, the branch and merge frontmatter records, the base-inference chain a declared integration branch now wins ahead of origin/HEAD, the pull-request route and the `pr` field it alone writes, why every record is written before the thing it describes, the squash caveat, the merge that runs via git -C in the base's own checkout and the worktree removed after it, and the read-if-present contract for a target's own /.docs/standards/git/ |
| [plan-lifecycle.md](workflows/plan-lifecycle.md) | The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, the append-only archive rule for facts that did not exist at the move, and the moment a follow-up becomes a spec — definition parks it as a Discoveries line, close-out mints it |
| [plugin-configuration.md](workflows/plugin-configuration.md) | `.claude/quenching.json` as the plugin's single configuration home — where it lives and why it left the specs workspace, the seven recognised keys and their defaults, the one key that deliberately has none and refuses instead, the one key a second tool reads and why it had nowhere else to live, the two keys with two consumers each — the release verb and the base-inference chain — why every other way it can be wrong is a field rather than an exception, and why a stranded `/.specs/config.json` is named instead of merged |
| [retiring-a-standard.md](workflows/retiring-a-standard.md) | Como um standard do bundle é aposentado — remoção, nunca deprecação (o verbo é `git rm`; um doc que sobrevive anotado vira ritual que ninguém age sobre); o herdeiro carrega o carimbo `retired with <doc> (<spec>, <data>)` no `source:` e no corpo; a varredura das citações é humana e o `## Impact` deve nomear a classe de docs que citam; a zona GENERATED da listagem é reconstruída no mesmo movimento; e o review de branch é a rede — com `stale-doc` contando como aviso, nunca como falha |
| [task-execution.md](workflows/task-execution.md) | How a spec's task is executed — the verification policies, `verify:` scoped at authoring, the failure budget, commit-per-task, the two-level review split, the four-event Handoff refresh cadence, and the delegation and [P] disjunction rules |
| [worktree-setup.md](workflows/worktree-setup.md) | The `worktreeSetup` hook — what it is for, where it is declared now that the plugin's config moved to `.claude/quenching.json`, what its absence means, who runs the declared command and with which cwd, why the consent is the isolation offer rather than a prompt of its own, and the record of why the specs front took a config file at all |
<!-- END GENERATED -->
