# CLAUDE.md — claude-quenching

A Claude Code **plugin marketplace** holding one plugin, `quenching`
([plugins/quenching/](plugins/quenching/)): a three-front aligner that forces a *target* repo's
`docs/` OKF bundle, native `specs/` workspace, and `.claude/` command surface into one canonical
shape. There is no application code, no build step and no test framework — the repo is markdown
command bodies plus three dependency-free stdlib Python tools.

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
# the skeleton and the plans seed are conformant by construction
python3 assets/hooks/okf-validate.py assets/docs                          # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root    # 0 error(s), 0 warning(s)
# the command surface
python3 assets/bin/skills.py --root . doctor --json                       # 26 commands, no findings
python3 assets/bin/skills.py --root . lint --json                         # exit 0 (warnings reported, not fatal)
# each tool proves the shared frontmatter rule against the SAME canonical case list
python3 assets/bin/skills.py selftest                                     # + the layout rule's fixture
python3 assets/bin/specs.py selftest
python3 assets/hooks/okf-validate.py selftest
```

**Nothing above tests that the surface actually LOADS** — the registry is built at session start,
so no change under `commands/**` is testable in the session that writes it:

```bash
./assets/bin/functional-checks.sh        # 9 assertions across 7 sandboxed sessions, exit 0 = all passed
```

**Run it after any change to `commands/**`, to a citation path, or to a conductor's stage names** —
those are the three things it is the only check for. Why a fresh process and why assertions run on
captured tool calls → [surface-verification.md](docs/standards/quality/surface-verification.md).

`specs.py` has no fixture in the repo; exercise it in a throwaway workspace (`specs.py new x` →
`status`/`next`/`task` → `promote x --outcome abandoned`) when its logic changes.

### Two rules that must survive any refactor

- **Never add `context: fork` to these commands.** Every sweep command gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  (`assets/references/align-all/convergence.md` §cycle-authorization) must still surface
  code-coupled confirmations mid-flow, which a forked context cannot present.
- **Never downgrade classification or executor sub-agents to `haiku` in `/docs:import-memory`.**
  A misclassification there becomes a wrong memory deletion — see the model-policy table in
  [README.md](plugins/quenching/README.md#cost-model) for which sub-agent calls elsewhere are safe
  on cheaper models/effort.

## Where knowledge lives

Knowledge is **NOT** in this file — it lives in the OKF bundle at [docs/](docs/index.md).

**Resolving a term.** Hit an unfamiliar repo word or codename? The glossary first →
[docs/knowledge/glossary.md](docs/knowledge/glossary.md) (`grep -i '<term>' docs/knowledge/glossary.md`).

**How this repo is operated** — which command adds a doc, what the hook checks, how to read a
validator finding → [docs/QUENCHING.md](docs/QUENCHING.md).

- [docs/standards/](docs/standards/index.md) — how WE build: the proven contracts. Start here for
  the [command surface's naming](docs/standards/naming/command-surface.md) (one file per entry
  point, the path is the identity), the [align surface](docs/standards/architecture/align-surface.md)
  (one align per front, probe first), the [plugin layout rule](docs/standards/architecture/plugin-layout.md)
  (`commands/**` is the only registered tree, which is why shared procedure lives under `assets/`),
  and the [release lockstep](docs/standards/ci-cd/versioning-release.md).
- [docs/knowledge/](docs/knowledge/index.md) — generic understanding we hold; its
  [glossary.md](docs/knowledge/glossary.md) is the A–Z term lookup.
- [docs/reference/](docs/reference/index.md) — facts about what we consume.
- [docs/catalog/](docs/catalog/index.md), [docs/vision/](docs/vision/index.md) and
  [docs/documentation/](docs/documentation/index.md) exist but are empty — this repo has no data,
  and direction and the site layer have not been written.
- [specs/plans/](specs/plans/index.md) — the spec workspace, a quenching-managed sibling
  **outside** the `docs/` bundle.

To create / edit / move knowledge (keeping the listing + `log.md` in sync), use the plugin's own
commands: `/docs:add` for one doc, `/docs:define` for a glossary term, `/docs:align` to
migrate/normalize, `/docs:harness` to keep this file thin.

## The plugin itself

What the twenty-six commands are, what each front gets, the cost model and the install/upgrade
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
     repo-wide operations + the docs/ home map. Knowledge is MOVED into docs/, never copied here.
     Maintained by the quenching plugin; this file is a harness pointer, not an OKF concept. -->
