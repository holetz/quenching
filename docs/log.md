# Change log — `docs/` bundle

History of the OKF bundle, most recent first. Each entry is grouped under a
`## YYYY-MM-DD` heading and prefixed `**Creation**` / `**Update**` / `**Deprecation**`.
`quenching-docs-align` and `quenching-docs-add` append here whenever they scaffold, migrate, or insert.

## 2026-07-26

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

**Creation**: OKF bundle skeleton installed by `claude-quenching` (`quenching-docs-align`) —
homes scaffolded, `index.md` listings established, `okf_version: "0.1"` set at the root.
