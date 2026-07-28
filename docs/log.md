# Change log — `docs/` bundle

History of the OKF bundle, most recent first. Each entry is grouped under a
`## YYYY-MM-DD` heading and prefixed `**Creation**` / `**Update**` / `**Deprecation**`.
`quenching-docs-align` and `quenching-docs-add` append here whenever they scaffold, migrate, or insert.

## 2026-07-28

**Update**: [Plan git record contract](/docs/standards/workflows/plan-git-record.md) — rewritten around the commit **subject** as the task→commit anchor: a subject is known before the commit exists, so every record is now written before the thing it describes, the box travels inside its own task commit, and `merge: {strategy, subject}` is stamped on the work branch — which is what lets the merge be the last action of `/specs:conclude`. Rebase stops destroying the record; the squash caveat stands.

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
