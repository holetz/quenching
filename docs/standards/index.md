# `standards/` — current/active reference, OUR contracts

The current/active **standard/contract** — "how it should be and why", versioned, the
shared source of truth. One standard per file; subfolder names by **subject**. Each
concept doc carries `type: standard` + a derived `resource:` (the repo scope it governs).

**Boundary:** `standards/` = "how **WE** do it (current/active)". Distinct from
[external/](../external/index.md) (external facts we consume) and
[catalog/](../catalog/index.md) (our data). Direction lives in
[vision/](../vision/index.md). An **agreed-but-unproven** rule sits here as
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

<!-- BEGIN GENERATED: rebuilt from disk by `quenching:knowledge:align`/`quenching:knowledge:add` — DO NOT edit by hand.
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
| [communication.md](agents/communication.md) | The two language bands an agent writes in — durable artifacts in canonical English so they stay portable and greppable across repos, conversation in the one BCP-47 tag the root harness line declares — and the conduct contract that holds whether or not a language is declared |
| [ephemeral-writes.md](agents/ephemeral-writes.md) | Where an agent puts a file it creates — the three destinations, the one question that sorts them, and the session-start declaration that makes the durable-ignored path present before the first write |

### architecture/

| Doc | Covers |
| --- | --- |
| [bundle-root.md](architecture/bundle-root.md) | The OKF bundle of a target repo lives at the fixed `/docs/` root and the design source at `/.design/` — neither root is configurable, because an LLM executor runs command bodies literally and a root it must resolve from configuration is a root it can resolve wrong |
| [configuration-arbitration.md](architecture/configuration-arbitration.md) | A shared configuration artifact has one writer for each semantic key, separate reader metadata, and no arbiter row for a read-only pillar, with a generated declaration first applied to pyproject.toml |
| [design-front.md](architecture/design-front.md) | The single DTCG source, its portable and editorial projections, explicit arbitration with Impeccable, and the boundary between web and non-web drift |
| [front-mold.md](architecture/front-mold.md) | The one binding minimum for a local front declaration, route, align/status surface, disposition bands and Codex projection, with measured domain-specific deltas |
| [generated-listings.md](architecture/generated-listings.md) | A listing regenerated from disk is a second source of a fact something else already derives, so it earns its keep only where nothing else derives that fact and a checker can decide freshness; the decision criterion is whether a command already answers the same question on demand, the /docs/ bundle index.md files are the counterexample that bounds the rule, and a convergence condition may name only what a checker decides |
| [align-surface.md](architecture/align-surface.md) | The aligned-front column — one align per local front carrying its content stages, the `security` and `git` pillars declared outside the conductor, the probe-before-inventory rule that makes a no-op align cost a couple of tool calls, the rule that no sweep records itself, and the conductor categories sharing the cycle-authorization contract — `/align` conducts the seven local fronts (`knowledge`, `design`, `components`, `ops`, `proof`, `toolchain`, `delivery`); none reimplements what it conducts |
| [install-profiles.md](architecture/install-profiles.md) | A profile declares which of the seven local fronts, provider-owned `specs`, and the `security` and `git` pillars a repository uses, in `.claude/quenching.json` — what it turns on and off is the residency of an entry's command descriptions (`disable-model-invocation: true`), never a command or a file; the `/align` conductor runs the installed local fronts in dependency order and names an uninstalled one in its report instead of failing on it, while the pillars carry no conductor to skip at all, only their own residency toggles |
| [ops-front.md](architecture/ops-front.md) | The target repository's current operations surface — one normalized router, its entry-point contract, lifecycle and finding vocabulary, verified by the shipped cq ops route |
| [plugin-layout.md](architecture/plugin-layout.md) | commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path |
| [proof-front.md](architecture/proof-front.md) | The target repository's canonical verification surface — layered tests, explicit fixture reach, measured source roots, a coverage ratchet, order evidence and a CI gate |
| [read-only-views.md](architecture/read-only-views.md) | A front's read-only view is a separate command holding no write tools, never a dry-run mode on the command that writes — because allowed-tools is granted per command, so a mode flag can only ever be a promise the grant does not enforce |
| [reference-loading.md](architecture/reference-loading.md) | A body that needs a reference section at step N loads that section at step N, with the literal, copy-pasteable cq components read invocation — a preamble citation says where the rule lives and does not make the session open the file, and the opposite was measured happening across the eight /quenching:specs:* bodies |
| [report-mold.md](architecture/report-mold.md) | The shape a front's commands print their report in belongs to ONE section every one of them cites — three fixed bands, an ordered set of columns each command takes a subset of, and every column naming a command executable as printed — and a block whose cells come from a payload is rendered by the TOOL, with the body quoting the output, because a format rewritten in eight bodies goes stale in seven, a table rewritten in three renderers diverges in all three, and no checker sees either |
| [retiring-a-reserved-artifact.md](architecture/retiring-a-reserved-artifact.md) | A reserved filename that is retired keeps its slot in RESERVED and its skip in the hard block; only its checker goes, because unreserving it silently converts every surviving file into a malformed concept doc — plus the one departure this house made knowingly, and the three things that made it payable |
| [root-migration.md](architecture/root-migration.md) | When a plugin release renames a root it itself declares — the bundle root moved from `/.docs/` to `/docs/` once — the migration is detected site by site from what sits on disk, never gated on a version bump, and resolved through exactly one route, `/quenching:knowledge:align` |
| [shared-mold-keys.md](architecture/shared-mold-keys.md) | A frontmatter mold cited by several commands is a fill-in invitation, so a key only one writer may legitimately set stays out of it and lives with that writer's own contract — prevention where a deterministic check is not available |
| [spec-backend.md](architecture/spec-backend.md) | Provider-owned GitHub and Azure Boards specs share five document primitives, one native-ID identity and one refusal boundary; external serialisation may use native fields only when it reassembles the canonical document, while locators, lean listings, placement, and the memory fake keep every consumer on the same contract, a direct read by native ID that reuses an in-process listing rather than paying a request per spec |
| [surface-translation.md](architecture/surface-translation.md) | A repository may carry Claude and Codex surfaces together; Claude owns configuration and deterministic translation keeps their command, reference, and harness artifacts aligned |
| [type-follows-home.md](architecture/type-follows-home.md) | Every home in the canonical tree owns exactly one `type:` value (`standards/` → `standard`, `concepts/` → `concept`, and so on) — a home that renames without restamping every doc's `type:` recreates the naming complaint one level down, in the most greppable field of the bundle, and nothing today checks for the mismatch |

### automation/

| Doc | Covers |
| --- | --- |
| [agents.md](automation/agents.md) | When work becomes a subagent, the definition contract for .claude/agents/, and how the surface is inventoried |
| [context-discipline.md](automation/context-discipline.md) | The two halves of a run's integral `tokens × turns remaining` and the three ways to cut it — open less (the declared files rather than the folder, the cited sections rather than the file, N sections in ONE call, the block rather than the section where a section has blocks, and the rules/rationale marker convention), run for less time (the section boundary as a legitimate stopping point, triggered by an event and never by a threshold), and emit fewer turns per unit of work (the batching contract, and the ban on a turn that exists only to announce the next tool call); plus the two things measured and refused, segmenting the bundle into more files and deleting rationale to compact it |
| [dependency-sweep.md](automation/dependency-sweep.md) | The contract of the sub-agent dependency sweep that runs at the open of a /quenching:specs:develop pass, before it asks anything — trigger, tool profile, deliverable, and the persistence of the map with the date it carries |
| [extension-points.md](automation/extension-points.md) | The extension point — an event a command declares for the repository that installed the plugin to attach its own work; the three-part contract (the declaration lives in config the core reads and never interprets; the body announces name, command and prompt and moves on; `condition` is never evaluated by whoever announces); the declared shape; and why the extension lives in config rather than in a command |
| [hooks.md](automation/hooks.md) | Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys |
| [plan-gates.md](automation/plan-gates.md) | The two protected classes — a code-coupled item, an irreversible cycle action — are the whole test, and a command in which neither occurs has nothing to confirm; what replaces the approval window when the gate goes (the record's URL, announced before any read and repeated in the report), the difference between the confirmation that drops and the consolidation that stays, what still stops the pass either way, the three intermediate forms measured and rejected, and the three conditions under which a gear's authority replaces the person at the go/no-go |
| [session-evidence.md](automation/session-evidence.md) | How a session transcript is read as evidence for the command that drove it — where transcripts live, the two entry forms, the JSONL-first arm ladder with the arm declared in the output, and the rule that a counted claim comes from code, never from a model recalling its own run |
| [skill-evaluation.md](automation/skill-evaluation.md) | What it takes to claim a skill works — with/without runs in isolated processes, assertions graded on quoted evidence, a rate reported with its fixture, and a delta reported even when it is zero |
| [skills.md](automation/skills.md) | How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point, including the admission criterion that decides whether a command's description stays resident in context or goes typed-only |

### ci-cd/

| Doc | Covers |
| --- | --- |
| [versioning-release.md](ci-cd/versioning-release.md) | Every published Claude and Codex version surface must agree at release time, including both marketplace entries and the generated Codex manifest |

### code/

| Doc | Covers |
| --- | --- |
| [canonical-set-parsing.md](code/canonical-set-parsing.md) | How the shipped tools consume a declared set — slice it by declared membership and never by position, because an ordinal index is a claim about the set's shape that nothing re-checks when the set grows; why a byte-for-byte lockstep check proves the copies agree but never that the code reading them still means the same thing, so a membership invariant is owed its own assertion; and why a case list must exercise the function that ships rather than a copy of its rule written inside the selftest |
| [conditional-projection-guards.md](code/conditional-projection-guards.md) | A projection that falls back to "store it whole" when its shape check refuses is invisible on the way down — so the guard must be asserted against the shape the contract writes TODAY, and a contract change that removes a frontmatter key has to be traced into every guard that named it, because the failure is a silent loss of a capability rather than an error anyone sees |
| [file-relative-path-resolution.md](code/file-relative-path-resolution.md) | Every `__file__`-relative expression silently encodes how deep its module sits; moving a script into a package re-evaluates it somewhere else without erroring, and the two instances this repo measured failed in opposite directions — one turned a lockstep check off and exited 0, the other made a subcommand refuse forever |
| [frontmatter-parser.md](code/frontmatter-parser.md) | The YAML subset `common/frontmatter.py` reads — the comment rule (a `#` opens a comment only at the start of a value or after whitespace, and never inside a quoted scalar), the canonical case list its tests hold it to, the anomaly sidecar, and why the union it now reads is wider than any of the three parsers it replaced |
| [optional-payload-fields.md](code/optional-payload-fields.md) | Optional `cq specs` JSON fields use `null` for the absence of a usable answer, never a sentinel; the former `overview` projection and `summary` field are retired, and any future body projection must name one source and one shared detector |
| [root-override-validation.md](code/root-override-validation.md) | Specs are provider-owned, so a root override cannot redirect them to a repository store; provider selection comes from the repository remote, unsupported legacy root settings refuse, and diagnostics report the same configuration fact without inventing a local tree |
| [superseded-format-recognition.md](code/superseded-format-recognition.md) | How a recogniser is changed when the format it reads is superseded — the new pattern must be asserted against the OLD form, because a pattern that describes the new one correctly often matches the old one whole and yields a confident wrong answer with no finding; and a store's recogniser must separate "not mine" from "mine, but stale", because sending both to the same discard makes a half-migrated front vanish in silence |

### git/

| Doc | Covers |
| --- | --- |
| [branching.md](git/branching.md) | One long-lived branch — the primary (main) — where every PR merges and review lives, the release as a deliberate local act that bumps, tags and publishes what the primary accumulated, the trigger on demand and with no cadence, the question that pushes toward grouping when the primary carries a single PR since the last tag, and the transition for anyone coming from the two-branch flow |

### naming/

| Doc | Covers |
| --- | --- |
| [command-surface.md](naming/command-surface.md) | How the plugin's commands are named and namespaced — one file per entry point, where the path is the identity; the design namespace for DTCG source and projections; the proof namespace for the verification surface rather than its test artifact; the seventh namespace (`git`, a pillar rather than a front) and its coexistence with a target's own `git` category; the components front's four sibling contexts, each named for the artifact it mints, and the rule that keeps a front-level verb off an artifact-level context |

### quality/

| Doc | Covers |
| --- | --- |
| [bundle-verification.md](quality/bundle-verification.md) | What the knowledge front machine-checks versus what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check, where an accepted gap is recorded, and the resource glob-set format |
| [citation-verification.md](quality/citation-verification.md) | How citation-check.sh proves a citation resolves against the base it claims — half 1 that the old name died and half 2 that the new name was born, blind and with no allowlist, and half 3 that the prose the plugin SHIPS promises only what the published skeleton delivers, since a command body and a reference are read inside a target checkout where our standards do not exist — the three scope rules read from the script's own header (the instrument does not measure itself, .specs/ is out of scope, golden/eval fixtures are frozen data), the spelling rule half 3 rests on (a markdown link promises a destination, a bare inline-code path names a doc the target may not have), that it runs manually and is documented rather than gated automatically (Open Decision 2, with a second real use case as the trigger to revisit), and why the "every red is a harness defect" precedent stays scoped to functional-checks.sh alone until citation-check.sh earns its own evidence (Open Decision 3, opportunistic) |
| [computed-fact-prose-fanout.md](quality/computed-fact-prose-fanout.md) | Any fact a tool computes and prose restates — a schema's fields, a surface's command count — fans out the moment it changes, and no checker sees it: why the validators are blind by construction, the two independent measurements this rule was set from, the grep on the fact's spelled-out form that finds the sites while the change is still cheap, a doc's own `description` as the nearest instance with its two listing consumers (one hand-maintained, one a GENERATED zone that is stale between sweeps by design), and why it belongs to the task that makes the change rather than to a later sweep |
| [empty-response-honesty.md](quality/empty-response-honesty.md) | An empty response from a third-party transport is two states — one that never arrived and one that legitimately has nothing — and only one of them can be proved; the rule to refuse at the choke point where the proof is structural, to warn where there is only corroborated suspicion, and to never let the diagnostic refuse |
| [finding-remedy-applicability.md](quality/finding-remedy-applicability.md) | A declared remedy names an action the surface that emitted the finding actually offers — the measured case where the same CLI refused both actions it advised, why an inapplicable remedy teaches readers to ignore the whole findings output and not just that one item, and the refusal of its own that a case with no path still owes |
| [parse-honesty.md](quality/parse-honesty.md) | A verifier names its own parse failure instead of reporting it as a content gap — the sidecar shape that adds the signal without changing a return type, why the finding is a warn rather than an error, and the rule that a checker never gains a lossy transform without the diagnostic that reports it |
| [prose-deletion-seams.md](quality/prose-deletion-seams.md) | Removing prose damages the text left behind, not only the text never opened — the hard wrap makes the line a unit the sentence does not respect, an orphaned continuation is promoted under the neighbouring bullet rather than left as litter, and a grant's justification outlives the use that earned it; the three seams measured on one branch, why every checker stays green through all three, and the reading that closes them |
| [prose-sweeps.md](quality/prose-sweeps.md) | A find-and-replace over prose corrupts exactly the sentences that talk ABOUT the form being replaced — how to recognise those sites, why the check written to guard the sweep cannot see them, and the mitigation that survives both |
| [prose-verify-pins-wording.md](quality/prose-verify-pins-wording.md) | A check written as a grep over prose does not prove the prose — it pins it to the phrase the check named, and the resulting failure is ambiguous between "the text is wrong" and "the check named a phrase nobody agreed to"; how to write the assertion, how to read the failure, the third reading that is never permitted, and the negative face where the check forbids a string the spec itself requires elsewhere |
| [self-matching-guards.md](quality/self-matching-guards.md) | A checker whose finding text quotes the pattern it prohibits will match itself — the self-accusation this repo measured on its first run, why the fix is parsing the construct rather than excluding the checker, and the narrow case where a substring scan is still honest |
| [selftest-mutation.md](quality/selftest-mutation.md) | A test that has never been observed to fail is untested — the mutation pass that earns the claim, one mutation per rule the fixture exists to prove, why the pass is run once at authoring rather than wired into CI, and the graduation gate the repo's new tests/ suite has not yet cleared |
| [surface-verification.md](quality/surface-verification.md) | How a change to the command surface is proven — a fresh process because the registry is built at session start, assertions on captured tool_use rather than prose, the five preconditions a functional check must satisfy to measure what it claims, why the harness belongs to the components front rather than the spec cycle and how to scope its cost, and how an ordering property is verified by running a real cycle |
| [translation-drift.md](quality/translation-drift.md) | Translation divergence is a named, repairable finding with exit 1; refusal remains exit 2 and neither result is a silent success |
| [unanswerable-verify-lines.md](quality/unanswerable-verify-lines.md) | A `verify:` whose verdict does not come from the state of the code — the pattern the shell mangles before it compares, the YAML scalar the parser truncates before it reads, the entry point that exited 0 without running anything — and the rule of exercising the line in both directions at the moment it is written, never at the moment it has to close |
| [unproven-capability-warning.md](quality/unproven-capability-warning.md) | Where a caveat about a capability that ships without end-to-end proof belongs — the two failure shapes that decide it, the standing fact as a verifier finding and the moment-of-risk line once per process on stderr, why a per-operation warning is a permanent context tax and silence is not the alternative, and the one edit that retires both together |
| [withdrawn-contract-residue.md](quality/withdrawn-contract-residue.md) | When a change removes a contract rather than changing a computed value, its prose residue has no canonical spelling to grep for — the sites assert it in their own words — so `## Impact` must name the CLASS of documents that assert it and derive the file list mechanically; the five misses measured on one branch, why naming the file is not enough either, and why the reviewer's question is "what did this make false?" rather than "which files changed?" |

### workflows/

| Doc | Covers |
| --- | --- |
| [agent-choice-catalogues.md](workflows/agent-choice-catalogues.md) | The one shape `subjects`, `tagCatalog` and `workItemTypes` all share — an abstract key mapping to a human-facing description an agent reads to PROPOSE and a human CONFIRMS — why the three converged on it independently, the one invariant that shape enforces on every consumer, and why a fourth catalogue should reuse it rather than invent its own review mechanism |
| [plan-artifacts.md](workflows/plan-artifacts.md) | The one provider-owned spec document, its thirteen canonical sections, the phase-scoped explicit-none rule, the parsed Impact sub-heading, the duplicated template and the three-copy record vocabulary, and how to read a v1 plan in /.specs/archive/ |
| [plan-git-record.md](workflows/plan-git-record.md) | How a provider-owned spec records the git facts that cannot be derived later — per-task commit subjects, branch, pull request and merge records, branch marks for conclude discovery, base inference, merge routes, and safe local and remote branch cleanup |
| [plan-lifecycle.md](workflows/plan-lifecycle.md) | The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, `conclude` archiving before the merge and what `## Outcome` asserts because of it, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, `branch`/`pr`/`merge` split across `execute`-or-`git:branch`, `git:pr:create` and `git:merge` now that `conclude` writes neither of the last two, the append-only archive rule for facts that did not exist at the move — no longer all landing in the same run — and the moment a follow-up becomes a spec — definition parks it as a Discoveries line, close-out mints it |
| [plugin-configuration.md](workflows/plugin-configuration.md) | `.claude/quenching.json` is the plugin's single configuration home; provider selection is derived from the repository remote, while placement, Azure mappings, lifecycle hooks, profiles and proposal catalogues remain explicit target settings |
| [retiring-a-standard.md](workflows/retiring-a-standard.md) | How a bundle standard is retired — removal, never deprecation (the verb is `git rm`; a doc that survives annotated becomes a ritual nobody acts on); the inheriting doc carries the `retired with <doc> (<spec>, <data>)` stamp in its `source:` and in its body; the citation sweep is human and `## Impact` must name the class of docs that cite it; the listing's GENERATED zone is rebuilt in the same movement; and the branch review is the net — with resource activity read as a figure, never as a failure |
| [task-execution.md](workflows/task-execution.md) | How a spec's task is executed — the verification policies, `verify:` scoped at authoring, the three causes of a check that can never pass (one of them invisible to the falsification run), `files:` naming the derived artifacts an edit invalidates, the failure budget, one commit per task retained across section boundaries, the two-level review split, the four-event Handoff refresh cadence, and the delegation and [P] disjunction rules |
| [worktree-setup.md](workflows/worktree-setup.md) | The `worktreeSetup` hook prepares a code-isolation worktree from `.claude/quenching.json`; its absence is normal, the execute offer displays and authorizes the command, and provider-owned specs never use this hook as persistent storage |

<!-- END GENERATED -->
