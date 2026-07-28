# Change log — `docs/` bundle

History of the OKF bundle, most recent first. Each entry is grouped under a
`## YYYY-MM-DD` heading and prefixed `**Creation**` / `**Update**` / `**Deprecation**`.
`quenching-docs-align` and `quenching-docs-add` append here whenever they scaffold, migrate, or insert.

## 2026-07-28

**Creation**: [Reassess whether specs/plans/index.md is needed](/specs/plans/2026-07-28-decide-plans-index-need.md) — captures the ask to re-examine the `specs/plans/index.md` listing: whether its GENERATED zone still earns the reindex call every creating, promoting and ranking command pays, given `specs.py list`/`status` derive the same view from disk.

**Creation**: [Prefer worktrees for spec isolation and remove them after a successful merge](/specs/plans/2026-07-28-prefer-worktree-isolation.md) — captures two asks about isolation: make the worktree the preferred path in `/specs:isolate` rather than the branch, and have `/specs:conclude` remove the worktree once its merge succeeds instead of leaving it on disk pointing at an integrated branch.

**Creation**: [Revise the fixed docs/standards subject folders](/specs/plans/2026-07-28-revise-standards-subject-folders.md) — captures the ask to revisit the canonical `docs/standards/` subject folders, starting with `mlops`, which names a far narrower arm than its siblings and lands empty in nearly every target.

**Update**: [Glossary](/docs/knowledge/glossary.md) — distilled from spec `fix-skills-py-description-truncation`: three terms it made load-bearing and none of them resolvable from its name — **Canonical case list** (the twelve frontmatter rows all three tools must decide identically, duplicated byte-identically as each tool's `CANONICAL_CASES`; the **lockstep unit** standing in for the shared module they cannot have, which works by localising a break to the parser that drifted, and which by construction can never contain a form a tool does *not* read), **Anomaly sidecar** (a *second* function reporting what a parse could not represent, chosen over a `(value, understood)` return precisely so none of the nine call sites — including mid-cycle `status`/`next`/`triage`, which today refuse nothing — has to decide what an un-understood input means) and **Parse honesty** (the obligation the whole spec exists to satisfy: a verifier names its own parse failure rather than reporting it as a content gap, at **warn**, because a deliberate comment and lost prose are byte-identical). `Anchorless strategy` was also moved back into alphabetical order, where the previous distillation had left it after `Approved record`.

**Creation**: [Retire the docs/ log](/specs/plans/2026-07-28-retire-docs-log.md) — captures the ask to end `docs/log.md` entirely: not scaffolded by `/docs:align`, not appended to by the capture commands, not required by the OKF conformance contract.

**Creation**: [Add customizable run modes to the specs cycle commands](/specs/plans/2026-07-28-add-specs-cycle-run-modes.md) — `develop`, `execute` and `conclude` each run one fixed way, so a human wanting a cheaper or a more thorough pass has no lever short of editing the command body; captures the ask for a run mode asked at invocation, on three named axes (how many questions reach the human, whether the run moves into a worktree, and effort as rounds of critique).

**Creation**: [Declare the repo's body language in docs/standards so every command reads it for free](/specs/plans/2026-07-28-declare-repo-body-language.md) — spec bodies are English-only today, which costs comprehension in a repo whose working language is not; captures the ask for a declared home under `docs/standards/` and a near-free read path (a hook that reads it automatically is one candidate).

**Creation**: [Route a 10x command surface without per-command always-on descriptions](/specs/plans/2026-07-28-route-commands-without-always-on-descriptions.md) — the surface is expected to grow ~10x and the always-on description model survives in no variant at that size (~4,560 tokens per session with bare labels, ~32,800 obeying the standard); captures that the short descriptions were deliberate rather than collapse damage, and that one cheap spike gates everything — whether `disable-model-invocation: true` blocks only autonomous selection or also an explicit by-name Skill call, which is what conductors depend on.

**Creation**: [Add an ELI5 section that makes a spec comprehensible to a human](/specs/plans/2026-07-28-add-eli5-section-to-specs.md) — a spec's sections are already written for a human and comprehension still costs real effort; captures the ask for an ELI5 rendering, with the complementary-section vs per-section-subsection choice left open.

**Update**: [Glossary](/docs/knowledge/glossary.md) — distilled from spec `move-conclude-merge-last`: three terms it made load-bearing and none of them resolvable — **Branch record** (`branch: {base, work}`, whose `base` git cannot recover after the merge, and whose signal is the live ref rather than the record), **Merge record** (`merge: {strategy, subject}`, stamped on the work branch *before* the merge, which is what makes the merge conclude's last action) and **Anchorless strategy** (the two strategies that produce no merge commit, so the record carries an explicit none — `sp-bad-merge` fires on getting it backwards either way).

**Creation**: two follow-up specs distilled from `move-conclude-merge-last`'s `## Discoveries`, neither owned by any task — [`conclude --outcome abandoned` can harvest a note and delete it in the same run](/specs/plans/2026-07-28-fix-conclude-abandoned-branch-harvest.md) (pre-existing, and deliberately frozen by that spec's `## Out of Scope`, so it crossed untouched) and [`functional-checks.sh` fails for lack of evidence, not by verdict](/specs/plans/2026-07-28-fix-functional-checks-encoding.md) (a cp1252 read of a UTF-8 capture, measured non-deterministic three times — the rule is now in [Surface verification](/docs/standards/quality/surface-verification.md), the script still disobeys it).

**Update**: [archive/](/specs/archive/) — spec [Make the merge the last action of /specs:conclude](/specs/archive/2026-07-28-move-conclude-merge-last.md) closed with `outcome: done`, all 25 tasks checked, merged with a **merge commit** so every recorded `subject:` resolves from `main` forever. The spec→git link is now the commit's *subject* rather than its sha: known before the commit exists, so the ticked box travels inside its own task commit and `merge: {strategy, subject}` is stamped on the work branch — which is what makes the merge the last action of `/specs:conclude`. Adds the 25th command, `/specs:isolate`, now the owner of the `branch:` record. Its own close followed the new order, and `main` — which had moved under it — was merged *into* the branch first, so nothing was written to the base after the merge.

**Update**: eight docs refreshed at the close of [move-conclude-merge-last](/specs/archive/2026-07-28-move-conclude-merge-last.md)'s branch review — their `resource` globs cover `commands/**`, `specs.py`, the templates or `schema.json`, all touched by the spec, and none was declared by a task. Four carried stale content: [Command surface naming](/docs/standards/naming/command-surface.md) still named a root `/align-and-update` deleted three specs ago, contradicting [Align surface](/docs/standards/architecture/align-surface.md); [Always-on context budget](/docs/standards/automation/context-budget.md) records that its zero-headroom ratchet **fired as predicted** on the 25th command (11,565 → 12,726) and what that shape costs; [Spec file contract](/docs/standards/workflows/plan-artifacts.md) gains the **third** lockstep copy of the record vocabulary, `schema.json`, which *shadows* `DEFAULT_SCHEMA` rather than falling back to it; [Surface verification](/docs/standards/quality/surface-verification.md) gains a fourth precondition (read the evidence encoding-safely, or the check fails for lack of evidence rather than reaching a verdict) and the ordering-check pattern. The other four were re-read and found accurate.

**Update**: [Glossary](/docs/knowledge/glossary.md) — **Commit record** redefined: it is the commit's *subject*, not its sha. Known before the commit exists, which is what lets the ticked box travel inside its own task commit and the merge record be stamped on the work branch. Both forms are read forever; neither is backfilled.

**Update**: [Plan git record contract](/docs/standards/workflows/plan-git-record.md) — rewritten around the commit **subject** as the task→commit anchor: a subject is known before the commit exists, so every record is now written before the thing it describes, the box travels inside its own task commit, and `merge: {strategy, subject}` is stamped on the work branch — which is what lets the merge be the last action of `/specs:conclude`. Rebase stops destroying the record; the squash caveat stands.

**Creation**: [Read-only views are their own command](/docs/standards/architecture/read-only-views.md) — distilled from spec `docs-verification-layer` at its conclusion: the one decision left sitting in `## Design` that no task ever wrote into a home, and that the repo has since proved twice.

**Update**: [Glossary](/docs/knowledge/glossary.md) — distilled from spec `docs-verification-layer`: three terms its verification layer made load-bearing and none of them resolvable — **Advisory finding** (the WARN the verify gate does not block on, `stale-doc` alone), **Bundle density** (the figures carrying no finding code, which is the whole reason the spec existed) and **Resource glob set** (the comma-separated `*`/`**` segment-wise convention that replaced the `file:line` anchor doctrine).

**Update**: [archive/](/specs/archive/) — spec [Verification layer for the docs/ front](/specs/archive/2026-07-25-docs-verification-layer.md) closed with `outcome: done`, all 26 tasks checked. Built in place before the `branch:` record existed, so there is no branch diff to review and no merge; its `## Outcome` records that every `plugins/quenching/skills/` path it names is now dead, and that task 6.2's `27 ↔ 27` bijection was superseded rather than completed — the bijection was retired outright, citing this exact staleness.

**Update**: [plans/](/specs/plans/index.md) — ranked 20 specs (20 new, 0 re-ranked): the front's first `priority` pass, over 22 candidates none of which carried a ranking. Two stay deliberately unranked — `decide-plan-quick-skill` (its own revisit date is ~2026-08-08, and its premise names a flow `specs-flow-consolidation` replaced) and `decide-sp-unrefined-severity` (parked on evidence that does not exist yet: exactly one spec on the front carries a `refined` record).

**Creation**: [Mine a session for improvements to the command that started it](/specs/plans/2026-07-28-improve-command-from-session.md) — a command's body is only ever revised from taste; the transcript that ran it holds the evidence of what it costs, repeats, gets wrong or leaves unresolved, and it is thrown away when the session ends.

**Creation**: [Make the merge the last action of /specs:conclude](/specs/plans/2026-07-28-move-conclude-merge-last.md) — conclude merges before distilling, so the emergent docs and the distillation land as loose commits on `main` instead of inside the spec's branch.

**Update**: [Glossary](/docs/knowledge/glossary.md) — distilled from spec `instrument-and-extend-skill-front`: four terms the capability layer made load-bearing and none of them resolvable, two of which `skills.py`'s own finding messages already name — **Scope ladder**, **Handler ladder**, **Cache trap** and **Always-on ceiling**.

**Creation**: four follow-up specs distilled from `instrument-and-extend-skill-front`'s `## Discoveries`, none of which any task owned — [routing information never restored on nine `/docs:*` descriptions](/specs/plans/2026-07-28-restore-routing-info-on-docs-commands.md) (and the zero-headroom ceiling it collides with), [`sk-unscoped-bash` cannot read the body its own remedy points at](/specs/plans/2026-07-28-make-sk-unscoped-bash-read-the-body.md), [nothing notices an installed tool copy falling behind](/specs/plans/2026-07-28-notice-installed-tool-version-drift.md) (this repo ran `specs.py` 1.0.0 against a 4.1.0 plugin), and [no probe observes a frontmatter `hooks:` block firing](/specs/plans/2026-07-28-probe-a-frontmatter-hook-firing.md).

**Update**: [Skill evaluation](/docs/standards/automation/skill-evaluation.md) — **graduated to `authority: current`** on its own stated gate (two committed benchmarks, `/skill:agent:new` and `/skill:hook:new`), and gained the four rules `instrument-and-extend-skill-front`'s runs measured: isolation is a property of the **process**, not of the agent (a sub-agent inherits the plugin registry, so its without-arm still lists the command); a routing rate is **conditional on its fixture** (5/5 in a repo shipping `agents.md`, a miss in a bare one); a **truncated run is inconclusive**, never a measured miss; and a rename must **carry its eval tree**.

**Update**: [Scoped hooks](/docs/standards/automation/hooks.md) — a handler whose script may not be installed **guards its own absence**: `python3 <missing-file>` exits 2, which the hook protocol reads as an error, so an unguarded handler reported a failure on every matched call in any repo that declined the optional install.

## 2026-07-27

**Creation**: [Rename the /skill namespace to /claude and separate the skill, agent and hook contexts](/specs/plans/2026-07-27-restructure-claude-front-namespace.md) — `skill` names both the whole `.claude/` front and one artifact kind inside it, and `assets/` cites commands without the `quenching:` prefix.

**Update**: [Glossary](/docs/knowledge/glossary.md) — distilled from spec `specs-flow-consolidation`: **Derived stage**, **Phase gate** and **Promote** still defined the retired v2 contract (promote-into-`ready/` as the human OK, a stage list with no `ready`/`approved`, gates that only ever moved a file) and now describe v3; **`[P]` marker** and **Verification policy** lost the retired propose/apply verbs.

**Creation**: five follow-up specs distilled from `specs-flow-consolidation`'s `## Discoveries`, none of which any task owned — [a mechanical writer for the frontmatter records](/specs/plans/2026-07-27-add-specs-py-record-writer.md) (the one part of the contract `specs.py` does not own, so `writeOnce` is enforced by nothing), [skills.py's silent description truncation at `#`](/specs/plans/2026-07-27-fix-skills-py-description-truncation.md) (reported as absence, not as a parse failure), [functional-checks.sh creating real specs in the repo it probes](/specs/plans/2026-07-27-isolate-functional-checks-probes.md), [the four copies of read-parse-derive in specs.py](/specs/plans/2026-07-27-dedupe-specs-py-spec-reader.md), and [the unnamed scaffolded stage](/specs/plans/2026-07-27-name-the-scaffolded-stage.md).

**Update**: [Consolidate the specs/ front around one router, and fold align-and-update into align](/specs/archive/2026-07-27-specs-flow-consolidation.md) archived `outcome: done` — 32/32 tasks, squash-merged into `main` with the branch **kept**, because each task line's `commit:` sha resolves only there. Its branch review also reconciled two `authority: current` standards the diff contradicted ([plan-artifacts.md](/docs/standards/workflows/plan-artifacts.md), [task-execution.md](/docs/standards/workflows/task-execution.md)) and rewrote both manifest descriptions off the retired twenty-seven-skill shape.

**Update**: `specs/` workspace migrated v2 → v3 by `specs.py migrate` (`specs-flow-consolidation` task 5.6) — the 12 active specs moved from `backlog/` + `ready/` into the single `plans/` folder with basenames unchanged, `archive/**` byte-untouched; the old `backlog/index.md` listing retired for [plans/index.md](/specs/plans/index.md), regenerated by `specs.py plans reindex`. The lifecycle contract is [plan-lifecycle.md](/docs/standards/workflows/plan-lifecycle.md).

**Creation**: [Subagent authoring](/docs/standards/automation/agents.md) and [Scoped hooks](/docs/standards/automation/hooks.md) — the `.claude/` front's capability standards, born `authority: background` from the capability research (hookify, plugin-dev, agent-sdk-dev, official docs): the delegation test and definition contract for `.claude/agents/`, and the hook scope/handler ladders with warn-by-default, born-disabled intrusives, and the per-hook cost claim.

**Update**: [Command authoring and alignment](/docs/standards/automation/skills.md) — gained §The execution profile (fork/pins/paths/frontmatter-hooks as priced, authored decisions; `disable-model-invocation`'s zero always-on cost) and the verifier's new codes (`sk-fork-gate`, `sk-profile-value`, and doctor's report-only wider surface `sk-agent-*`/`sk-hook-*`); the pricing doctrine itself lives in the plugin's `skill-new/capabilities.md`, cited by `/skill:new` step 4 and the two new mints `/skill:agent:new` + `/skill:hook:new`.

**Creation**: [Retire the skill vocabulary left behind by the collapse](/specs/backlog/2026-07-27-retire-skill-vocabulary.md) — distilled from the archived `collapse-skills-into-commands` spec: the noun "skill" where "command" is meant, in the 28 bodies, the 22 reference files, and four stale spots in `docs/` the spec did not record.

**Creation**: [Rewrite README.md for the collapsed command surface](/specs/backlog/2026-07-27-rewrite-readme-for-collapsed-surface.md) — distilled from the archived `collapse-skills-into-commands` spec: task 5.3 rewrote §Cost model, leaving ~131 lines describing the deleted two-file architecture.

**Update**: [Glossary](/docs/knowledge/glossary.md) — gained Always-on metadata, Entry point and Phantom command, the three terms `collapse-skills-into-commands` made load-bearing.

**Creation**: [Surface verification](/docs/standards/quality/surface-verification.md) — distilled from the archived `collapse-skills-into-commands` spec: a change under `commands/**` is not testable in the session that writes it, so it is proven in a fresh `claude -p` asserting on captured `tool_use` rather than prose, under three preconditions (stdin redirected, an invasive check sandboxed with its own `enabledPlugins`, and the command's own preconditions satisfied or the check measures the precondition).

**Update**: [specs/](/specs/archive/2026-07-26-collapse-skills-into-commands.md) — archived `collapse-skills-into-commands` (outcome: done) at 35/35 tasks: 28 skill+wrapper pairs collapsed to one command file per entry point, always-on metadata 30,705 → 2,083 characters, shipped as plugin 3.0.0.

## 2026-07-26

**Update**: [Claude Code skill and command loading mechanics](/docs/reference/tools/claude-code-skill-command-mechanics.md) — gained §What has been relied upon, and by whom (rows 1, 2 and 4 are load-bearing for `collapse-skills-into-commands`; row 6 explicitly declined) and §Re-measurements recording the 2026-07-26 re-check against Claude Code 2.1.215.

**Creation**: [Claude Code skill and command loading mechanics](/docs/reference/tools/claude-code-skill-command-mechanics.md) — distilled from the abandoned `skill-description-tiering` spec: `${CLAUDE_PLUGIN_ROOT}` substitutes in command bodies, commands are Skill-tool invocable, discovery is at startup, and one frontmatter schema serves both.

**Update**: [specs/](/specs/archive/2026-07-26-skill-description-tiering.md) — archived `skill-description-tiering` (outcome: abandoned) at its own task 0.2 gate, in favour of the collapse spec. Two of three spike questions passed; the third proved parity rather than a YES.

**Creation**: [Collapse the 28 skill+wrapper pairs into one command file per entry point](/specs/backlog/2026-07-26-collapse-skills-into-commands.md) — captured as the mutually-exclusive alternative to `skill-description-tiering`, gated on that spec's task 0.2 spike.

**Update**: [specs/](/specs/archive/2026-07-25-specs-front-v2.md) — archived `specs-front-v2` (outcome: done): the `specs/` front is v2 (one file per spec, three phase
folders, gated promote), shipped as plugin 2.0.0. Glossary gains Derived stage, Phase gate,
and Promote.

## 2026-07-25

**Creation**: [Bundle verification](/docs/standards/quality/bundle-verification.md) — what the
`docs/` front machine-checks versus what it leaves to a skill's prose self-check, the rule that an
invariant restated in more than two skills is owed a deterministic check (the glossary tail step
was specified six times and produced zero entries), the WARN-but-blocking severity model and why no
new check is born at ERROR, and the `resource` glob-set format. Written while implementing the
`docs-verification-layer` plan, which proved the rule by replacing prose with four checks.

**Creation**: [Skill evaluation](/docs/standards/automation/skill-evaluation.md) — what "this skill
works" has to mean before anyone says it: two arms (with the skill and without) in isolated agents
on the same model, assertions that name observable outcomes, every grade carrying a quoted excerpt
or an explicit `unknown`, one case per branch plus one exercising the `Not for:` boundary, and the
delta reported **including when it is zero or negative**. Description tuning is the only edit
measurement authorizes, and a trigger is removed only on a measured miss. Born
`authority: background` — the contract is written and `quenching-skill-eval` implements it, but no
skill here has been measured against it yet.

**Update**: [Command surface naming](/docs/standards/naming/command-surface.md) — §Bijection stops
transcribing a skill count (it read 27 against a surface of 28) and names `skills.py doctor` as
the reporter; the two root commands `/align` and `/align-and-update` are recorded as intended
`sk-path-mismatch` exceptions. New §Why the wrapper still exists states the trade-off now that
Claude Code produces `/x` from a command **or** a skill: the wrapper buys the `:`-namespaced `/`
tree at a measured 2,072 characters, with a revisit trigger — `skills.py budget` showing wrappers
displacing skill descriptions.

**Creation**: [Always-on context budget](/docs/standards/automation/context-budget.md) — the
metadata every session pays before a skill fires: the two caps (1,536 Claude Code for
`description` + `when_to_use`, 1,024 for `description` under the Agent Skills standard), the rule
that both are counted on the PARSED value and never on the YAML source, what each field may carry,
and the per-surface ceiling at this plugin's measured baseline of 36,503. Born
`authority: background` — the ceiling is one surface's measurement, and graduates once
`skills.py budget` has run on two adopting repos.

**Update**: [Skill authoring and alignment](/docs/standards/automation/skills.md) — gains
§Invocation and permission (the `user-invocable` × `disable-model-invocation` × `context: fork`
decision table, and the scoped-`allowed-tools` rule with its stated-reason exception) and §The
verifier, naming `skills.py` as the `.claude/` front's checker and its `sk-*` codes as the
normative statement of every threshold this standard names. The convergence condition stops being
a judgement and becomes the tool's exit codes.

**Update**: [Skill authoring and alignment](/docs/standards/automation/skills.md) — §Single-axis
classification gains the variant rule (a technique is a parameter of a verb, not a new axis),
distilled from the archived `refine-and-execute-specs-flow` plan
(`specs/archive/2026-07-25-refine-and-execute-specs-flow/`), which proved it by shipping four
interrogation modes as one skill's `--mode` rather than four skills.

**Update**: [Glossary](/docs/knowledge/glossary.md) — first four real terms, replacing the seed
placeholder: verification policy, failure budget, `[P]` marker, and refinement record, each linked
to the workflow standard that defines it. Distilled from the same archived plan.

**Creation**: [Plan artifact contract](/docs/standards/workflows/plan-artifacts.md) — the required
sections of a plan's artifacts (explicit-none rather than omission), the one parsed sub-heading of
`## Impact`, the refinement record, and what `applyReady` is and is not evidence of. Written while
implementing the `refine-and-execute-specs-flow` plan, which proved each rule as it landed.

**Creation**: [Task execution contract](/docs/standards/workflows/task-execution.md) — the three
verification policies and when each applies, the five-attempt failure budget with a re-read at
two, commit-per-task, the per-task/end-of-plan review split, and the executor-delegation and `[P]`
disjunction rules (including why delegating a sub-agent is **not** `context: fork`).

## 2026-07-24

**Creation**: [Skill authoring and alignment](/docs/standards/automation/skills.md) distilled from
the archived `add-quenching-skill-pair` plan (`specs/archive/2026-07-24-add-quenching-skill-pair/`)
— the single-axis classification, authoring, and alignment contract for the skill surface.

**Creation**: [Command surface naming](/docs/standards/naming/command-surface.md) — the plugin's
skill + command-wrapper naming standard, superseding the retired `openspec/specs/command-naming`
spec (the `opsx:`/`openspec-*` rules no longer hold now that the spec-driven front is native).

**Update**: spec-driven workspace migrated `openspec/` → `specs/` (flat plans, no `config.yaml`,
no delta store); the OKF `docs/` bundle installed at the repo root and the `okf-validate.py` +
`specs.py` tools installed into `.claude/hooks/`.

## 2026-07-07

**Update**: [Glossary](/docs/knowledge/glossary.md) reformatted from a
`| Term | Definition | See |` table to a flat, `index.md`-style bullet list
(`* [<Term>](<path>.md) — <definition>`, or `* **<Term>** — <definition>` when unlinked) —
normalizes the glossary onto the same syntax every other listing uses; an unlinked entry
is a valid, permanent state. Also backfillable in bulk by the new `quenching-docs-glossary-backfill`.

**Creation**: [Glossary](/docs/knowledge/glossary.md) fixed seed added to `knowledge/` — the
repo's A–Z term lookup (`| Term | Definition | See |`), enriched by `quenching-docs-define` and, as
a tail step, by `quenching-docs-add` / `quenching-docs-learn` / `quenching-docs-import-memory`.

## 2026-07-06

**Creation**: [`knowledge/`](/docs/knowledge/index.md) home added — generic knowledge we hold
(concepts, explanations, learnings; `type: knowledge`), filled by `quenching-docs-learn`.

**Creation**: OKF bundle skeleton installed by `quenching` (`quenching-docs-align`) —
homes scaffolded, `index.md` listings established, `okf_version: "0.1"` set at the root.
