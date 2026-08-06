# CLAUDE.md — claude-quenching

A Claude Code **plugin marketplace** holding one plugin, `quenching`
([plugins/quenching/](plugins/quenching/)): a three-front aligner that forces a *target* repo's
`/.docs/` OKF bundle, native `/.specs/` workspace, and `.claude/` command surface into one canonical
shape. There is no application code, no build step and no test framework — the repo is markdown
command bodies plus four dependency-free stdlib Python tools.

Language: pt-BR — the contract is [/.docs/standards/agents/communication.md](/.docs/standards/agents/communication.md).

## Operating this repo

**Command bodies are the source code.** `commands/**/*.md` and `assets/references/**/*.md` are
prose instructions a future Claude session executes literally, so precision in wording matters as
much as correctness in a normal codebase. Treat an edit there like an edit to a function.

Verify the shipped skeleton after touching anything under `plugins/quenching/`:

```bash
cd plugins/quenching
# version lockstep — VERSION and all three shipped scripts must agree
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
python3 assets/bin/session.py --version                                   # outside the six; nothing else reads it
# the shipped skeleton is conformant by construction — read as ZERO ERRORS, never as a warning total
python3 assets/hooks/okf-validate.py assets/docs                          # 0 error(s); stale-doc warns are advisory
# the command surface
python3 assets/bin/skills.py --root . doctor --json                       # 25 commands, no findings
python3 assets/bin/skills.py --root . lint --json                         # exit 0 (warnings reported, not fatal)
python3 assets/bin/skills.py --root . budget --json                       # exit 1 = over the ceiling; re-measure, never estimate
# each tool proves the shared frontmatter rule against the SAME canonical case list
python3 assets/bin/skills.py selftest                                     # + the layout rule's fixture
python3 assets/bin/specs.py selftest
python3 assets/hooks/okf-validate.py selftest
```

**`stale-doc` is never counted as a failure**, here or anywhere. The skeleton's
`standards/agents/communication.md` declares `resource: /.docs/**, /.specs/**` — a legitimate
bundle-aggregate scope, per
[bundle-verification.md](/.docs/standards/quality/bundle-verification.md) §The `resource` glob-set
format — so **any** commit under either tree ages it, and a branch that touches `/.docs/` cannot help
raising the count. The resource moved; the rule did not. Read the gate as zero errors.

`budget` is in that list because a surface can cross its ceiling with **no command minted** — three
description edits put it 149 characters over, and nothing in this block ran the only instrument that
says so. Both firing modes and the two exits →
[context-budget.md](/.docs/standards/automation/context-budget.md).

**Nothing above tests that the surface actually LOADS** — the registry is built at session start,
so no change under `commands/**` is testable in the session that writes it:

```bash
./assets/checks/functional-checks.sh          # default: checks 1, 2, 4 — body, citation path, stage name
./assets/checks/functional-checks.sh --only 3 # opt-in: spoken routing. Prefer /skill:eval — see below
```
`exit 0` all measured assertions passed · `1` one failed · `2` nothing could be measured, which is
**not** a pass.

**It belongs to the skill front — `/skill:new` after minting or editing a command here, and
`/skill:eval` when it tunes a description.** It is not a repo-wide mandate, and it does not go in a
spec's `## Validation` or a task's `verify:`: every check is a billed agent session, and measured
across the whole archive, **every red run this harness ever produced traced to a defect in the
harness itself, none to a surface regression**. For spoken routing reach for `/skill:eval`, which
measures it graded and with a boundary arm; check 3 is a worse copy kept opt-in. Full reasoning →
[surface-verification.md](/.docs/standards/quality/surface-verification.md).

`specs.py` has no fixture in the repo; exercise it in a throwaway workspace (`specs.py new x` →
`status`/`next`/`task` → `promote x --outcome abandoned`) when its logic changes.

### Two rules that must survive any refactor

- **Never add `context: fork` to these commands.** Every sweep command gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  (`assets/references/align/convergence.md` §cycle-authorization) must still surface
  code-coupled confirmations mid-flow, which a forked context cannot present.
- **Never downgrade classification or executor sub-agents to `haiku` in `/docs:import-memory`.**
  A misclassification there becomes a wrong memory deletion — see the model-policy table in
  [README.md](plugins/quenching/README.md#cost-model) for which sub-agent calls elsewhere are safe
  on cheaper models/effort.

## Where knowledge lives

Knowledge is **NOT** in this file — it lives in the OKF bundle at [/.docs/](/.docs/index.md).

**Resolving a term.** Hit an unfamiliar repo word or codename? The glossary first →
[/.docs/knowledge/glossary.md](/.docs/knowledge/glossary.md) (`grep -i '<term>' /.docs/knowledge/glossary.md`).

**How this repo is operated** — which command adds a doc, what the hook checks, how to read a
validator finding → [/.docs/QUENCHING.md](/.docs/QUENCHING.md).

- [/.docs/standards/](/.docs/standards/index.md) — how WE build: the proven contracts. Start here for
  the [command surface's naming](/.docs/standards/naming/command-surface.md) (one file per entry
  point, the path is the identity), the [align surface](/.docs/standards/architecture/align-surface.md)
  (one align per front, probe first), the [plugin layout rule](/.docs/standards/architecture/plugin-layout.md)
  (`commands/**` is the only registered tree, which is why shared procedure lives under `assets/`),
  and the [release lockstep](/.docs/standards/ci-cd/versioning-release.md).
- [/.docs/knowledge/](/.docs/knowledge/index.md) — generic understanding we hold; its
  [glossary.md](/.docs/knowledge/glossary.md) is the A–Z term lookup.
- [/.docs/reference/](/.docs/reference/index.md) — facts about what we consume.
- [/.docs/catalog/](/.docs/catalog/index.md), [/.docs/vision/](/.docs/vision/index.md) and
  [/.docs/documentation/](/.docs/documentation/index.md) exist but are empty — this repo has no data,
  and direction and the site layer have not been written.
- The spec workspace — a quenching-managed front **outside** the `/.docs/` bundle, and **not a folder
  in this repo**: `.claude/quenching.json` declares `backend: github`, so every spec is an issue and
  there is nothing under `/.specs/` to read. `python3 plugins/quenching/assets/bin/specs.py list`
  derives the front from the declared backend on demand, and is the only honest way to see it.

To create / edit / move knowledge (keeping the listing in sync), use the plugin's own
commands: `/docs:add` for one doc, `/docs:define` for a glossary term, `/docs:align` to
migrate/normalize, `/docs:harness` to keep this file thin.

## The plugin itself

What the twenty-five commands are, what each front gets, the cost model and the install/upgrade
path are the **product's own documentation**, not repo standards — do not restate them here:

- [plugins/quenching/README.md](plugins/quenching/README.md) — the command-by-command manual, the
  three fronts, the cost model, install and upgrade.
- `plugins/quenching/commands/**` — each command's frontmatter `description` carries its trigger
  phrases and its `Not for: X → other-command` boundary. **Read the target command's frontmatter
  before assuming which one owns a task.**
- `plugins/quenching/assets/references/<name>/*.md` — shared procedure, owned once and cited by
  absolute `${CLAUDE_PLUGIN_ROOT}` path rather than restated. The OKF bundle contract itself is
  [assets/references/docs-align/okf-spec.md](plugins/quenching/assets/references/docs-align/okf-spec.md).

<!-- Root harness pointer, auto-loaded by Claude Code on every turn. Keep it a thin pointer:
     repo-wide operations + the /.docs/ home map. Knowledge is MOVED into /.docs/, never copied here.
     Maintained by the quenching plugin; this file is a harness pointer, not an OKF concept. -->
