---
slug: collapse-skills-into-commands
title: Collapse the 28 skill+wrapper pairs into one command file per entry point
verification: per-section
outcome: done
---

# Collapse the 28 skill+wrapper pairs into one command file per entry point

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE PHASE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN phase gate is reached:

       new (capture)        `## Problem`
       promote -> ready/    the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready/  (warn only)  `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

Claude Code merged custom commands into skills: a `commands/deploy.md` and a
`skills/deploy/SKILL.md` "both create `/deploy` and work the same way". The plugin's 28 skills
plus their 28 mirrored wrappers are therefore a redundant pair — two always-on descriptions
where one would do. Collapsing to one command file per entry point would take always-on
metadata from 30,705 characters to ~2,069 (a 93% cut) and delete the `wrapper == skill`
duplication outright, rather than making it mechanical via `sk-wrapper-drift` as
`skill-description-tiering` does.

A related finding from that spec: all 28 skills carry `user-invocable: false`, the one row of
Claude Code's invocation table where the description is permanently resident *and* the human
cannot type the skill — which is exactly why the wrappers exist. Once the wrappers *are* the
skills, `disable-model-invocation: true` becomes available as a further lever.

### The gate is resolved — this spec is live

`skill-description-tiering` task 0.2 ran the spike on **2026-07-26** and the human took this
branch; that spec is now
[archived as abandoned](/specs/archive/2026-07-26-skill-description-tiering.md). Method: throwaway
command and skill probes exercised in fresh `claude -p` processes against Claude Code 2.1.215, all
reverted. Full facts in
[reference/tools/claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md).

| # | Question | Result |
| --- | --- | --- |
| 1 | `${CLAUDE_PLUGIN_ROOT}` substitutes in a `commands/*.md` body | **YES** — resolved to the absolute plugin root on both invocation paths. The load-bearing unknown is cleared: a command file *can* cite a bundled `references/*.md`. |
| 2 | A command honours `allowed-tools` | **Parity, not proof** — the allowlist failed to block a `Write` in all four cells of command × skill by slash × Skill-tool invocation. Commands are no worse than skills, so the collapse loses nothing; but nobody should claim it as enforcement. Tracked separately as `verify-allowed-tools-enforcement`. |
| 3 | A conductor invokes a command by name via the Skill tool | **YES** — a command was invoked by name through the Skill tool with substitution intact, the exact path a conductor uses. |

Q2 is why this was a judgement call rather than an automatic pass: the gate's letter demanded
three clean YES. It was taken on the reading that "no regression" suffices, since the guarantee
turns out to be absent from skills too.

**Two findings the spike added, both easing this spec:**

- **`hide-from-slash-command-tool: "true"` exists** as a frontmatter key, observed in Anthropic's
  shipped `ralph-wiggum/commands/ralph-loop.md`. This answers the objection that made
  `skill-description-tiering` defer `disable-model-invocation: true` — that dropping
  `user-invocable: false` floods the `/` menu with duplicates. Worth confirming it behaves as the
  name suggests before designing around it.
- **One unified frontmatter schema.** The 2.1.215 binary parses `user-invocable`, `allowed-tools`,
  `disallowed-tools`, `argument-hint`, and `disable-model-invocation` from a single key list,
  corroborating the merge rather than resting on the changelog sentence.
- **Precedent exists in the wild.** Anthropic ships four `commands/**` files using
  `${CLAUDE_PLUGIN_ROOT}`, one load-bearingly inside `allowed-tools` itself.

One operational note for whoever builds this: **the command/skill registry is built at session
start**, so no change to `commands/**` is testable in the session that makes it. Every verification
step needs a fresh process.

Rough shape now that it proceeds: 28 skill directories become 28 command files; every cross-skill
citation is rewritten to an absolute plugin-root path; the 17 `references/` directories are
re-homed; five conductors are re-plumbed; `skills.py` is re-pointed at `commands/**`; and all
three `QUENCHING.md` operator manuals plus `CLAUDE.md` are rewritten. Reverting is a migration,
not a `git revert` — which is why this was kept separate from `skill-description-tiering`.

## Proposal

Collapse each `skills/<name>/SKILL.md` + `commands/<path>.md` pair into **one**
`commands/<path>.md` carrying the wrapper's `description` and the skill's body — and ship that
same single shape into every target repo. Claude Code merged commands into skills; the file that
survives is already both.

**On this plugin's own surface:**

- **One file per entry point.** 28 `SKILL.md` + 28 wrappers become 28 command files; `skills/` is
  deleted. The `/` tree is unchanged — same paths, same descriptions, same `argument-hint` — so
  nothing a human types today changes.
- **Always-on metadata falls to 2,069 characters** from a re-confirmed 30,705: a **93% cut**,
  ~7,676 → ~517 approximate tokens, off every session in every repo that installs the plugin.
  This is the *deletion* of one of two descriptions, not the compression of either.
- **The `wrapper == skill` duplication ceases to exist.** `skill-description-tiering` would have
  made it mechanical via a new `sk-wrapper-drift` warning; one string cannot drift from itself.
- **Every command keeps default invocation** — typable at `/`, invocable by name by a conductor or
  a spoken trigger. No `user-invocable: false`, no `disable-model-invocation`.
- **Shared procedure lives at `${CLAUDE_PLUGIN_ROOT}/assets/references/<name>/`.** The 17
  `references/` trees (22 files) re-home under `assets/`, which already holds everything Claude
  Code must not surface as a live skill — and where a reference file cannot register as a phantom
  command the way one under `commands/` would. All **351** citations — 289 cross-skill, 62
  own-tree — become that absolute form, which the gate spike proved substitutes inside a command
  body.
- **The five conductors invoke commands by name** — `quenching:docs:align`, not
  `quenching:quenching-docs-align`. The spike exercised exactly this path.
- **The name IS the path.** `quenching-<front>-<object>-<verb>` existed as a flattened path *to be
  mirrored*; with nothing to mirror, `/docs:add` is the whole identity. The bijection rule and its
  two root exceptions (`sk-path-mismatch` on `/align` and `/align-and-update`) are deleted, not
  reinterpreted.

**In every target repo the plugin aligns** — one shape everywhere, so `skills.py` never learns two:

- **`skills.py` verifies `commands/**` and nothing else.** `doctor`'s pair logic goes; `lint` and
  `budget` stay, reading command frontmatter.
- **`/skill:new` mints ONE command file**, and `/skill:align` migrates a target's existing pairs
  exactly as this spec migrates the plugin's — so an adopting repo inherits the same cut rather
  than being taught the shape the plugin just abandoned.
- **The molds teach the collapsed form** (`assets/templates/automation/`).

**The documentation stops describing a two-file surface** — `docs/standards/naming/command-surface.md`
(which today argues *why the wrapper still exists*), `docs/standards/automation/skills.md`,
`docs/standards/automation/context-budget.md`, the three `QUENCHING.md` operator manuals, root
`CLAUDE.md`, and `README.md` §Cost model.

## Out of Scope

- **The invocation flags.** No command sets `disable-model-invocation: true` or
  `hide-from-slash-command-tool`. The lever `## Problem` inherited from
  `skill-description-tiering` is **closed by mechanics, not deferred**: a conductor invoking a
  stage by name through the Skill tool *is* model invocation, so the flag would break all five
  conductors and stop the capture tools firing from speech. `hide-from-slash-command-tool`
  answered a duplicate-`/`-entry objection that this collapse deletes outright — with one file
  per entry point there is nothing duplicated to hide.
- **Compressing the surviving descriptions.** The 2,069 characters are today's wrapper strings,
  unedited: already concise (~74 chars median) and already human-reviewed for the `/` menu.
  Rewriting them is a separate argument on separate evidence, and folding it in would make the
  before/after measurement unattributable.
- **Changing the number of entry points.** The surface stays 28 — nothing merged, split, renamed,
  or dropped. Every `/` path a human types today resolves to the same behaviour afterwards.
  Cutting the count is a different argument with different evidence.
- **Auditing what the bodies say.** Bodies move verbatim; only their citation paths and their
  frontmatter change. Judging the prose against the writing doctrine is `/skill:align-and-update`'s
  job, and mixing it in would make a 28-file migration diff unreviewable.
- **`allowed-tools` enforcement.** The gate spike found the allowlist restricted nothing for
  commands *or* skills. Parity is all this spec needs; whether the guarantee is enforced at all is
  tracked as its own spec and is not resolved here.
- **Running the migration against any adopting repo.** `/skill:align` *gains* the pair→command
  migration, but pointing it at a particular repo stays that repo's decision. No installed target
  is touched by this spec landing.
- **The `docs/` and `specs/` fronts as fronts.** This spec edits documents inside `docs/` only
  because they describe the `.claude/` front; the OKF bundle's shape, the validator, and
  `specs.py` are unchanged.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/naming/command-surface.md` — **revised.** Today it makes the skill↔wrapper
  bijection the contract and argues *why the wrapper still exists*, with a measured cost and an
  explicit revisit trigger: *"reconsider when `skills.py budget` shows wrapper descriptions
  displacing skill descriptions."* That trigger has fired from the other side — the skill
  descriptions are what the wrapper makes redundant. It becomes the naming rule for a single-file
  surface: the command path IS the identity, no mirroring, no bijection, no root exceptions.
- `docs/standards/automation/skills.md` — **revised.** Single-axis classification survives intact;
  the mirrored-wrapper requirement, `doctor`'s bijection, and the invocation table whose default
  row is `user-invocable: false` do not. Also gains the citation rule: a bundled reference is
  cited by `${CLAUDE_PLUGIN_ROOT}` absolute path, never relatively.
- `docs/standards/automation/context-budget.md` — **revised.** Every number in it is of a two-file
  surface. The 36,503 ceiling is re-derived from the collapsed measurement, and the two per-skill
  caps are re-stated as per-command.
- `docs/standards/architecture/plugin-layout.md` — **new.** The layout rule the collapse creates
  and nothing currently states: `commands/**` is the *only* tree Claude Code registers, so
  anything that is not an entry point lives under `assets/`. A `references/` directory beside a
  command file would surface as a phantom `/docs:align:references:conformance`, which is a silent
  failure mode with no check today. Lands `authority: current` — the migration proves it.

### Standards at `authority: background` this spec may resolve

- `none` — `context-budget.md` is the only `background` standard in play, and its stated
  graduation condition is `skills.py budget` having run on this plugin **plus two adopting
  repos**. This spec supplies one much larger measurement on one surface, which is not that
  condition. It is revised and stays `background`; promoting it on this evidence would be moving
  the goalposts to reach them.

### Product code this spec expects to touch

- `plugins/quenching/commands/**` — 28 files, each rewritten from wrapper stub to full
  entry point
- `plugins/quenching/skills/**` — 28 `SKILL.md` deleted; 22 `references/*.md` moved out
- `plugins/quenching/assets/references/**` — new tree, the re-homed shared procedure
- `plugins/quenching/assets/bin/skills.py` — re-pointed at `commands/**`; the pair logic
  removed
- `plugins/quenching/assets/templates/automation/{skill,command,registry,skills-standard}.md`
  — the molds that teach a target repo the shape
- `plugins/quenching/{VERSION,.claude-plugin/plugin.json}` + `.claude-plugin/marketplace.json`
  — the lockstep set

### Documents edited that own no contract

- `plugins/quenching/assets/{docs,specs,claude}/QUENCHING.md` — all three enumerate the
  command surface
- `CLAUDE.md` (root) — describes the 2×4 matrix, the 28↔28 bijection, and the citation paths
  throughout
- `plugins/quenching/README.md` §Cost model — states the always-on figures and the model
  policy per skill
- `docs/reference/tools/claude-code-skill-command-mechanics.md` — the spike's measured facts; rows
  1, 2 and 4 are what this migration rests on, so it gains a note that they were relied upon and
  by which spec

## Validation

The mechanical half runs in-process. The functional half **cannot**: the command registry is built
at session start ([claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md)
§4), so nothing under `commands/**` is testable in the session that edits it. Every "does this
actually load" check runs in a **fresh `claude -p` process**.

**Mechanical — in-process:**

- **The cut is real.** `skills.py --root plugins/quenching budget --json` reports total
  always-on at **2,069** characters against the pre-change 30,705 — exactly today's
  `breakdown.wrappers`, because the surviving strings are the wrapper descriptions unedited. The
  instrument counts parsed frontmatter, as `context-budget.md` requires.
- **Nothing is left behind.** `plugins/quenching/skills/` does not exist; no `references/`
  directory survives outside `assets/`; `find plugins/quenching/commands -type d` returns
  only the four namespace directories (`docs`, `docs/documentation`, `specs`, `skill`), so no
  phantom command can register.
- **Every citation resolves.** By script, resolving `${CLAUDE_PLUGIN_ROOT}` to
  `plugins/quenching`: all 351 rewritten citations point at a file that exists, and zero
  relative forms (`../quenching-`, `](references/`) survive anywhere. Never by eye.
- **The surface is conformant.** `skills.py --root plugins/quenching lint --json` and
  `doctor --json` both exit 0, with no `sk-*` code that did not exist before, and no code this
  spec deleted still firing.
- **The surface is still 28.** `find plugins/quenching/commands -name '*.md' | wc -l` = 28,
  and every `/` path that resolved before still resolves.
- **The shipped payload is undisturbed.** `okf-validate.py assets/docs` and
  `okf-validate.py assets/specs/backlog --listing-root` both clean.
- **Version lockstep.** `skills.py` changed, so `VERSION`, `plugin.json`, the marketplace manifest
  and both other shipped scripts agree per `CLAUDE.md` §Releasing.

**Functional — one fresh process per check:**

- **A collapsed command loads and its body expands.** In a new `claude -p`, invoke one migrated
  command by its `/` path and confirm it read its re-homed reference file — that is
  `${CLAUDE_PLUGIN_ROOT}` substituting for real, not in a probe.
- **A conductor reaches its stages.** In a new `claude -p`, run `/align` far enough to confirm it
  invokes `quenching:docs:align` **by name** and that body loads. Highest-risk path in the
  spec: five conductors, all re-plumbed, and a silent failure here looks like a conductor that
  simply does nothing.
- **A spoken trigger still routes.** In a new `claude -p`, a capture phrase reaches its command by
  description alone, with no `/` typed — confirming default invocation genuinely leaves the
  description model-routable.

**The invariant that replaces the bijection:** every `commands/**/*.md` carries a non-empty
`description` and no two resolve to the same `/` path. Checked by `skills.py doctor`, never
asserted in prose.

## Design

### The collapsed file

Frontmatter is a merge with one rule per key, not a judgement call:

| Key | Source | Why |
| --- | --- | --- |
| `description` | **the wrapper's** | the human-facing string, already reviewed for the `/` menu; this is the whole saving |
| `argument-hint` | the wrapper's | wrappers already carry it; skills never did |
| `allowed-tools` | the skill's | the scoped grant the body needs; wrappers declare none |
| `effort` | the skill's | present on 5; the model policy in `README.md` survives unchanged |
| `name` | **dropped** | the command path IS the name now |
| `when_to_use` | **dropped** | a Claude-Code-only extension whose content restates the description's first clause |
| `user-invocable` | **dropped** | it exists to hide a skill behind a wrapper; there is no wrapper to hide behind |

The body is the skill's, moved verbatim, with two edits: the `# quenching-docs-add — …` title
becomes `# /docs:add — …`, and the wrapper's argument sentence (*"passing `$ARGUMENTS` (the piece
of information to file — a standard, catalog table, …)"*) folds into the body's opening as the
input contract, because that sentence is the only content a wrapper carried that is not
frontmatter.

### Why `assets/references/`, and what it costs

`commands/**` is the only tree Claude Code registers. A `references/` directory beside a command
file would surface every reference as a phantom entry — `/docs:align:references:conformance` — so
the trees cannot stay adjacent to what cites them. `assets/` is the existing answer: `CLAUDE.md`
already describes it as *"inert here (≥2 levels below any `SKILL.md`, so Claude Code does not
surface it)"*, and `${CLAUDE_PLUGIN_ROOT}/assets/…` is already the in-tree citation idiom in
`quenching-skill-new` and `quenching-docs-align`.

The cost is honest and worth writing down: `assets/` today means *"the installable payload, copied
into target repos, never executed here"*, and references are neither installed nor copied. This
widens it to *"everything Claude Code must not surface as an entry point"*. `plugin-layout.md`
states the widened definition, so the folder does not quietly mean two things.

`<name>` is the former skill name minus the `quenching-` prefix —
`assets/references/docs-add/homes.md`, `assets/references/align-all/sweep-doctrine.md`. Flat
rather than mirroring `commands/docs/add.md` as a nested pair, because the flat spelling makes the
351-citation rewrite a mechanical string substitution instead of 351 per-file path derivations.

### Citations are absolute, never relative

Every citation becomes `${CLAUDE_PLUGIN_ROOT}/assets/references/<name>/<file>.md`. Relative paths
are not an option and not merely inconvenient: today `skills/quenching-docs-align/SKILL.md`
reaches a sibling as `../quenching-docs-add/references/homes.md`, and after the move the citing
file sits at `commands/docs/align.md` while the target sits at
`assets/references/docs-add/homes.md` — a relative path exists but encodes the depth of the citing
file, so `commands/docs/documentation/build.md` and `commands/align.md` would need different
strings for the same target. The absolute form is one string everywhere. The gate spike proved it
substitutes inside a command body.

### `skills.py` after the collapse

One row per `commands/**/*.md`. Deleted outright, having nothing left to compare: the bijection,
`sk-path-mismatch`, and the unmirrored-wrapper finding. Kept and re-scoped from skill to command:
`sk-no-description`, `sk-metadata-cap`, `sk-description-portable`, `sk-trigger-position`,
`sk-no-boundary`, `sk-unscoped-bash`, `sk-body-length`, invocation coherence.

**No new check is needed for the phantom-command failure mode.** A stray `.md` under `commands/`
is a file with no `description`, which is already `sk-no-description` — an error. The layout rule
is enforced by a check that exists.

### The migration is unobservable while it runs

The registry is built at session start, so there is no half-migrated *running* state to protect
against: a session that begins before the migration sees the old surface until it ends, and a
session that begins after sees the new one. Nothing can observe both. Ordering is therefore chosen
for **git-history reviewability**, not runtime safety — build the new tree and rewrite citations
while both shapes are on disk, delete `skills/` as its own commit, then re-point `skills.py`, then
the documents. Each commit is independently readable; none of them is independently *testable*,
which is what `per-section` verification is for.

### `per-section` verification, and why not the alternatives

`per-task` is unavailable for anything functional — three of the checks need a fresh process, and
spawning one per task would dominate the run. `end-of-plan` would let 351 citation rewrites and 28
file merges land before a single check. `per-section` batches at the natural boundaries the
ordering above already creates.

### Binding contracts this design does not contradict

- `command-surface.md` §Bijection and clean renames — *"a rename is clean: no compatibility
  aliases, no dual-registered names."* This is the largest rename in the repo's history and takes
  that rule literally: no `skills/` shim, no dual registration, no transitional period.
- `context-budget.md` §Count the parsed value — every figure here is parsed frontmatter, as
  `skills.py budget` reports it.
- `skills.md` §`allowed-tools` is always scoped — carried to commands unchanged, including
  `quenching-specs-apply`'s stated unscoped-`Bash` exception, which stays stated in its body.
- `CLAUDE.md` §Two rules that must survive any refactor — no `context: fork` on any collapsed
  command, and no model downgrade in `quenching-docs-import-memory`. Neither is loosened by the
  shape change; both move with their bodies.

## Alternatives Considered

- **Keep the pair and cut the descriptions instead** — `skill-description-tiering`, in full.
  Rejected by measurement and by the human on 2026-07-26: it lands always-on at 4,138 rather than
  2,069, and it *preserves* the duplication by making it mechanical — a new `sk-wrapper-drift`
  warning, a new `routing:` frontmatter key, a two-path linter. Its analysis is not wasted: the
  compression recipe and the tier mechanism survive as doctrine for target repos that do have
  prose-routed skills. [Archived as abandoned](/specs/archive/2026-07-26-skill-description-tiering.md).
- **Collapse the other way — skills absorb the wrappers.** Delete `commands/**`, drop
  `user-invocable: false`, let the 28 skills be typed directly. Same file count, same saving.
  Rejected: the `/` tree is the surface's whole discovery story — `/` + tab walks it in folder
  order and the namespace says which artifact a command touches before you read a description. A
  skill name is flat (`quenching-docs-add`), so this trades the namespace away for nothing, and
  `command-surface.md` already priced navigability as the one thing the wrapper buys.
- **Keep `references/` under `skills/`, delete only the 28 `SKILL.md` files.** Smallest file-move
  diff, and a directory with no `SKILL.md` is not registered, so the phantom risk does not arise.
  Rejected: the 351 citations get rewritten to absolute form either way, because the *citing* file
  moves — so the saving is a few `git mv` operations, and the price is a `skills/` directory
  containing no skills. A name that lies is exactly what `command-surface.md` §Verb-first names
  forbids of the surface it governs.
- **Collapse the plugin only, leave the target-repo doctrine paired.** Rejected on 2026-07-26: it
  makes `skills.py` verify two shapes forever, and the plugin would go on installing into target
  repos the doctrine it had just abandoned for itself. The wider scope costs `/skill:new`,
  `/skill:align` and four molds — paid once, against a two-shape linter maintained indefinitely.
- **A router command per front.** `/docs` dispatches to one of eleven behaviours by argument, so
  the surface carries three or four descriptions instead of 28. Rejected before this spec, in
  `skill-description-tiering`'s own alternatives: it adds a hop on the common path and destroys
  `/` + tab discovery, to save descriptions this collapse removes outright.
- **Do nothing — 30,705 is under the 36,503 ceiling.** Rejected: the ceiling is one surface's
  pre-diet measurement, so sitting under it is not evidence of being cheap. And this is the only
  proposal on the table whose saving comes from deleting a file rather than editing prose, which
  is the only kind of saving that cannot silently regress.

## Open Decisions

- **Does `assets/` need splitting rather than widening?** **SETTLED at task 4.1: widened, not
  split.** The test the bullet set — does the widened sentence read as a fudge to whoever writes
  the standard — was applied while writing it, and it does not. Both halves share the single
  property that names the folder: Claude Code ignores them. A split would have bought a second
  directory level, a second citation prefix, and 351 further path rewrites to separate two things
  no reader confuses. Recorded in `plugin-layout.md` with the revisit trigger that matters: a
  **third** reason to live under `assets/`, at which point the folder means nothing.

  The migration also added a subtree the decision did not anticipate — `assets/evals/`, rescued at
  task 2.6 from the deleted `skills/` tree. It lands on the ignored-by-Claude-Code side, so it
  widens nothing further.
- **Does `context-budget.md` graduate to `authority: current`?** **No, and this spec does not
  reopen it.** Its stated condition is `skills.py budget` having run on this plugin plus two
  adopting repos; this supplies one much larger measurement on one surface. Settled only by real
  adoption. Recorded here so the next reader does not mistake the size of this measurement for the
  condition.
- **The `<name>` spelling under `assets/references/`.** Flat `docs-add` (chosen — mechanical
  substitution) against nested `docs/add` (mirrors the command path). **SETTLED at task 1.1:
  flat stands.** All 22 destination paths were generated and checked — 0 duplicates across 17
  trees, uniqueness inherited from the skill folder names minus a constant prefix. The same check
  run over the 28 flattened *command* paths also returns 0 duplicates, so the spelling is sound on
  both sides of the citation.

  The check corrected the risk this bullet stated. A future `/docs:add:something` would flatten to
  `docs-add-something`, which does **not** collide with `docs-add` — the feared collision cannot
  happen. The real latent ambiguity is that `-` serves as both segment separator and
  within-segment hyphen, so a nested `/docs:add:something` and a hyphenated `/docs:add-something`
  would flatten identically. No such pair exists today: the only nested command,
  `/docs:documentation:build`, has no `/docs:documentation-build` twin. **Revisit trigger,
  restated:** the surface gaining two commands whose paths differ only in where a `-` is a
  separator — not merely gaining a third path segment.
- **Are the three functional checks scriptable, or are they a manual procedure?** **SETTLED at
  task 7.1: scriptable, and all three were scripted.** The mechanism is
  `claude -p --output-format stream-json --verbose`, which emits every `tool_use` as JSON — so a
  check asserts on **what the process actually did** (a `Read` whose `file_path` is the re-homed
  reference; a `Skill` whose `skill` is `quenching:docs:align`) rather than on what its
  prose claims. That is the difference between a functional test and a self-report, and it is why
  this is worth committing.

  Two operational facts the scripting surfaced, both needed by whoever runs these again:
  **`< /dev/null` is required** (otherwise `claude -p` waits 3s on stdin and warns), and an
  invasive check must run with **cwd in a throwaway repo carrying its own
  `.claude/settings.json` `enabledPlugins`** — the plugin loads from the marketplace path, so the
  sandbox gets the real surface while `/align` writes only into the scratch dir.

  **Committed as `plugins/quenching/assets/bin/functional-checks.sh`**, so the surface
  gains the automated functional coverage it has never had.

## Risks

- **A conductor silently stops working.** Five conductors invoke their stages by name; a wrong
  name fails as "unknown skill" at best, and at worst produces a conductor that runs and does
  nothing. Mitigation: the `/align` fresh-process check in `## Validation` is a **required** task,
  not an optional one, and it exercises the real conductor path rather than a probe.
- **`${CLAUDE_PLUGIN_ROOT}` was measured once, on one version.** The entire design rests on row 1
  of a reference doc whose own closing line reads *"Re-measure before relying on any row"* —
  Claude Code 2.1.215, under `claude -p`, on one machine. Mitigation: task 0.2 re-measures before
  a single file moves, and a NO stops the spec at zero cost. Anthropic shipping four `commands/**`
  files that use the placeholder is precedent, not a guarantee.
- **The revert is a migration, not a `git revert`.** ACCEPTED — this is precisely the property
  that kept this out of `skill-description-tiering`, whose revert was frontmatter. Mitigated only
  by ordering: the new tree is built and every citation rewritten while both shapes sit on disk,
  so the last cheaply-reversible point is late, explicit, and its own commit (task 2.6).
- **351 mechanical rewrites, and a broken citation fails silently.** A wrong path does not error —
  the body simply instructs a future session to read a file that is not there, and the session
  improvises. Mitigation: the resolve-every-citation check is by-script and total, and
  *zero surviving relative forms* is asserted separately, so a **missed** rewrite is caught and
  not just a **wrong** one.
- **28 bodies moved, and a truncated body has no check.** Mitigation: bodies move verbatim —
  `## Out of Scope` forbids editing them — so a line-count comparison against the source
  `SKILL.md` is exact rather than approximate, and task 2.3 makes it a task rather than a hope.
- **`skills.py` loses checks that were doing real work.** The bijection caught a genuine class of
  error: a skill minted without a wrapper. Nothing replaces it, because after the collapse nothing
  can be missing. ACCEPTED, and recorded here so a future reader does not read the deletion as an
  oversight and re-add it.
- **An adopting repo is surprised by the migration.** A repo that installed the paired shape and
  upgrades will see `/skill:align` propose a pair→command migration it never asked for.
  Mitigation: it arrives through the align's ordinary one-plan-one-OK gate like any other item,
  and `## Out of Scope` states that no installed target is touched by this spec landing.
- **Nothing in this spec is testable in the session that writes it.** The registry is built at
  session start, so every functional check is deferred to a process that does not exist yet while
  the work is happening. ACCEPTED, and it is the reason `verification: per-section` rather than
  `per-task` — the honest failure mode is a run that feels finished and was never actually loaded.

## Handoff

**Nothing here is testable in the session that writes it.** The command registry is built at
session start, so a file you just created is not invocable until a new process. Never report a
surface change as working on the strength of the session that made it.

**Resolve the tools by the plugin path first.** This repo's `.claude/hooks/specs.py` is stale
(1.0.0, `--plan` flags) against the plugin's 2.0.0 (`--spec`). Use
`plugins/quenching/assets/bin/{specs,skills}.py`. Branch on exit code (0 ok · 1 findings ·
2 refusal) and `--json`, never on prose.

**State of play at definition time** (2026-07-26, measured on this tree, Linux, `python3` 3.12.3):

- 28 skills / 28 wrappers; always-on 30,705 chars (28,636 + 2,069), ceiling 36,503.
- 351 citations to rewrite: 289 cross-skill `../quenching-*/references/*.md`, 62 own-tree
  `](references/*.md)`. 22 reference files in 17 trees.
- Five conductors: `align`, `align-and-update`, `docs/align-and-update`,
  `specs/align-and-update`, `skill/align-and-update`.
- Skill frontmatter keys in use: `name`, `description`, `when_to_use`, `allowed-tools`,
  `user-invocable`, plus `effort` on 5. Wrapper keys: `description`, `argument-hint` only.
- `${CLAUDE_PLUGIN_ROOT}` already appears in 25 files, so the citation idiom is in-tree precedent,
  not a new invention.

**Already tried, do not redo.** `skill-description-tiering` measured this surface, designed a
two-tier description policy, and was
[abandoned](/specs/archive/2026-07-26-skill-description-tiering.md) at its own gate in favour of
this spec. Its task 0.2 spike is where every mechanical fact above comes from; the facts live in
[claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md),
which says re-measure before relying on any row — task 0.2 does exactly that.

**Conventions in force.** Bodies move verbatim (`## Out of Scope`). Citations are absolute
(`## Design`). A rename is clean — no aliases, no shims, no transitional period
(`command-surface.md`). No `context: fork` on any collapsed command, and no model downgrade in
`quenching-docs-import-memory` (`CLAUDE.md` §Two rules that must survive any refactor).

## Tasks

Ordered so the decisive re-measure happens before a file moves, and so the last
cheaply-reversible point (2.6) is late and explicit. `PY` is the applying machine's real
interpreter — `python3` on Linux; resolve it once at 0.1 rather than trusting a spelling.

### 0. Re-measure before anything moves

- [x] 0.1 Re-confirm the baseline on the applying tree before editing: 28 commands, 28 skills,
      always-on 30,705 characters (28,636 skill + 2,069 wrapper) against the 36,503 ceiling. If
      the tree differs, correct `## Problem` and `## Proposal` first — never map the numbers by
      guess.
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json
- [x] 0.2 **The load-bearing re-measure.** In a fresh `claude -p` against the running Claude Code
      version, confirm `${CLAUDE_PLUGIN_ROOT}` still substitutes inside a `commands/*.md` body and
      that a command is still invocable by name through the Skill tool. Record the version
      measured. **A NO on either stops the spec here**, before a file has moved.
      files: docs/reference/tools/claude-code-skill-command-mechanics.md
- [x] 0.3 Re-confirm the citation counts on the applying tree — 289 cross-skill
      `../quenching-*/references/*.md` plus 62 own-tree `](references/*.md)` = 351, across 22
      files in 17 trees — so task 1.4's total is a measured target rather than this spec's.

### 1. Build the new reference tree

- [x] 1.1 Create `plugins/quenching/assets/references/<name>/` and `git mv` all 22
      reference files out of the 17 `skills/*/references/` trees; `<name>` is the skill folder
      name minus the `quenching-` prefix. Check the 22 destination paths for collision and settle
      `## Open Decisions` §The `<name>` spelling.
      files: plugins/quenching/assets/references/**, plugins/quenching/skills/*/references/**
      verify: find plugins/quenching/assets/references -name '*.md' | wc -l
- [x] 1.2 Rewrite all 351 citations to `${CLAUDE_PLUGIN_ROOT}/assets/references/<name>/<file>.md`
      — mechanical substitution per `## Design` §Citations are absolute, never relative; no
      per-file path derivation.
      files: plugins/quenching/skills/**, plugins/quenching/commands/**
- [x] 1.3 Rewrite the citations *between* the moved reference files, which cite each other
      relatively as well.
      files: plugins/quenching/assets/references/**
- [x] 1.4 Prove the rewrite: every citation resolves with the placeholder expanded to
      `plugins/quenching`, and zero `../quenching-` or `](references/` forms survive
      anywhere in the plugin.
      verify: script — 0 unresolved citations and 0 surviving relative forms

### 2. Merge each pair into one command file

- [x] 2.1 Merge the frontmatter of all 28 pairs per `## Design` §The collapsed file —
      `description` + `argument-hint` from the wrapper, `allowed-tools` + `effort` from the skill;
      drop `name`, `when_to_use`, `user-invocable`.
      files: plugins/quenching/commands/**
      pattern: plugins/quenching/commands/docs/add.md
- [x] 2.2 Move each skill body into its command file verbatim, retitling
      `# quenching-<front>-<verb>` to `# /<front>:<verb>` and folding the wrapper's `$ARGUMENTS`
      sentence in as the input contract. No other edit to any body.
      files: plugins/quenching/commands/**
- [x] 2.3 Prove no body was truncated: each collapsed command's body line count reconciles against
      its source `SKILL.md` body, allowing only the two edits task 2.2 sanctions.
      verify: script — 28 of 28 line counts reconcile
- [x] 2.4 Re-plumb the five conductors to invoke their stages by command path —
      `quenching:docs:align`, never `quenching:quenching-docs-align`.
      files: plugins/quenching/commands/align.md, plugins/quenching/commands/align-and-update.md, plugins/quenching/commands/docs/align-and-update.md, plugins/quenching/commands/specs/align-and-update.md, plugins/quenching/commands/skill/align-and-update.md
- [x] 2.5 Rewrite every remaining bare `quenching-<front>-<object>-<verb>` mention in the 28 bodies
      to its command path. These are the cross-skill routing sentences — `Not for: … →
      quenching-docs-align` — and they now name files that do not exist.
      files: plugins/quenching/commands/**
- [x] 2.6 Delete `plugins/quenching/skills/`, as its own commit. This is the last
      cheaply-reversible point in the spec.
      files: plugins/quenching/skills/**
      verify: test ! -d plugins/quenching/skills

### 3. Re-point the tooling

- [x] 3.1 Re-point `skills.py` at `commands/**` as the surface, one row per command file. Delete
      the bijection, `sk-path-mismatch`, and the unmirrored-wrapper finding — they have nothing
      left to compare.
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
- [x] 3.2 Re-scope the surviving checks to command frontmatter: `sk-no-description`,
      `sk-metadata-cap`, `sk-description-portable`, `sk-trigger-position`, `sk-no-boundary`,
      `sk-unscoped-bash`, `sk-body-length`, invocation coherence.
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
- [x] 3.3 Confirm `sk-no-description` covers the phantom-command mode per `## Design`: a stray
      `.md` under `commands/` with no frontmatter is an error, so the layout rule needs no new
      check. Add a fixture proving it fires.
      files: plugins/quenching/assets/bin/skills.py
- [x] 3.4 Teach the collapsed shape to the molds in `assets/templates/automation/` — `skill.md`
      becomes the command mold, `command.md` folds into it or is deleted, `registry.md` and
      `skills-standard.md` stop describing a pair.
      files: plugins/quenching/assets/templates/automation/
- [x] 3.5 Rewrite `/skill:new` to mint ONE command file — no wrapper, no bijection step, no
      `user-invocable: false`.
      files: plugins/quenching/commands/skill/new.md, plugins/quenching/assets/references/skill-new/
- [x] 3.6 Teach `/skill:align` the pair→command migration for a target repo's existing surface,
      under its ordinary one-plan-one-OK gate.
      files: plugins/quenching/commands/skill/align.md, plugins/quenching/assets/references/skill-align/
- [x] 3.7 Version lockstep per `CLAUDE.md` §Releasing — `skills.py` changed, so `VERSION`,
      `plugin.json`, the marketplace manifest, and both other shipped scripts move together.
      files: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py

### 4. The standards

- [x] 4.1 Write `docs/standards/architecture/plugin-layout.md` (new, `authority: current`):
      `commands/**` is the only registered tree, everything else lives under `assets/`, and
      references are cited by `${CLAUDE_PLUGIN_ROOT}` absolute path. Settle `## Open Decisions`
      §Does `assets/` need splitting while drafting it.
      files: docs/standards/architecture/plugin-layout.md
- [x] 4.2 Revise `docs/standards/naming/command-surface.md`: the command path is the identity.
      Delete the bijection rule, the mirroring requirement, the two root exceptions, and §Why the
      wrapper still exists — whose own revisit trigger this spec fired.
      files: docs/standards/naming/command-surface.md
- [x] 4.3 Revise `docs/standards/automation/skills.md`: keep single-axis classification; drop the
      mirrored-wrapper requirement and the `user-invocable: false` default row of the invocation
      table; add the absolute-citation rule.
      files: docs/standards/automation/skills.md
- [x] 4.4 Revise `docs/standards/automation/context-budget.md`: restate the two caps as
      per-command and re-derive every figure from the collapsed surface. Keep
      `authority: background` — the graduation condition is unmet, per `## Impact`. The ceiling
      number itself comes from task 6.2, never from this spec's projection.
      files: docs/standards/automation/context-budget.md

### 5. The documents that describe the surface

- [x] 5.1 [P] Rewrite the three operator manuals — each enumerates the command surface and the
      skill-plus-wrapper shape.
      files: plugins/quenching/assets/docs/QUENCHING.md, plugins/quenching/assets/specs/QUENCHING.md, plugins/quenching/assets/claude/QUENCHING.md
- [x] 5.2 [P] Rewrite root `CLAUDE.md`: the 2×4 matrix, the repository layout, the 28↔28
      bijection, the skills table, and every citation path in it.
      files: CLAUDE.md
- [x] 5.3 [P] Rewrite `README.md` §Cost model — its always-on figures are of a two-file surface
      and its skill count is stale.
      files: plugins/quenching/README.md
- [x] 5.4 Note in `docs/reference/tools/claude-code-skill-command-mechanics.md` which rows this
      migration relied on and which spec relied on them, against the version task 0.2 measured.
      files: docs/reference/tools/claude-code-skill-command-mechanics.md

### 6. Prove it — mechanical

- [x] 6.1 Measure the result: always-on at 2,069 characters, exactly the pre-change
      `breakdown.wrappers`.
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json
- [x] 6.2 Update `DEFAULT_CEILING` in `skills.py` and the ceiling in `context-budget.md` from
      6.1's measurement — never from this spec's projection, per the standard's own "revised only
      from a measurement" rule.
      files: plugins/quenching/assets/bin/skills.py, docs/standards/automation/context-budget.md
- [x] 6.3 Confirm the surface is conformant and complete: `lint` and `doctor` both exit 0 with no
      new `sk-*` code, 28 command files, `skills/` gone, no `references/` outside `assets/`, and
      `find commands -type d` returning only the four namespace directories.
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
- [x] 6.4 Confirm the shipped OKF payload is undisturbed.
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs && python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/specs/backlog --listing-root

### 7. Prove it — fresh process, one per check

- [x] 7.1 In a fresh `claude -p`, invoke one migrated command by its `/` path and confirm it read
      its re-homed reference file — `${CLAUDE_PLUGIN_ROOT}` substituting in production, not in a
      probe. Settle `## Open Decisions` §Are the three functional checks scriptable here.
- [x] 7.2 In a fresh `claude -p`, run `/align` far enough to confirm it invokes
      `quenching:docs:align` **by name** and that body loads. The highest-risk path in the
      spec: a silent failure here looks like a conductor that runs and does nothing.
- [x] 7.3 In a fresh `claude -p`, confirm a spoken capture phrase still reaches its command by
      description alone, with no `/` typed — default invocation genuinely leaving the description
      model-routable.

## Discoveries

- **62 stale `SKILL.md` / `skills/` mentions survived the citation rewrite, in no task's `files:`.**
  Found at task 1.4. They match none of task 1.4's citation patterns because they are prose, yet a
  body reading *"read the `SKILL.md`"* after `SKILL.md` ceases to exist is exactly the failure
  `## Risks` describes — *"instructs a future session to read a file that is not there"* — wearing
  prose instead of a link. **Raised at the section-1 boundary; the human ruled: fix the factual
  ones mechanically in task 2.2, judge nothing.** Applied as: 10 `this SKILL.md` self-references →
  `this command file`; 2 cross-command `SKILL.md` links → absolute command paths. The rest are
  about a *target repo's* surface and are re-taught by tasks 3.4–3.6.

- **Two tasks had to widen their declared `files:`, both for the same reason.** Task 2.5 says it
  rewrites bare skill-name mentions *"in the 28 bodies"*, on the rationale that they *"now name
  files that do not exist"* — which is equally true of the 22 reference files, holding 171 of the
  297 mentions. Rewriting only the bodies would have left every reference file naming retired
  skills. Task 1.3 widened the same way, making 7 same-tree sibling links absolute so `## Design`
  §Citations are absolute is not contradicted by the plugin's own tree.

- **`skills.py budget` stops being usable as the skill↔command pairing source at task 2.2.** Its
  pairing key is the wrapper stub's `quenching:<skill>` line, which 2.2 overwrites — so any
  later step needing the mapping must recover it from git history (`d3b0cd9`, the last commit
  holding both halves) rather than from the instrument. This bit task 2.3's verifier mid-run.

- **The task-2.3 body reconciliation is only meaningful at the 2.2 boundary.** It asserts the diff
  against each source `SKILL.md` contains nothing but 2.2's sanctioned edits, so tasks 2.4 and 2.5
  — which deliberately rewrite skill-name mentions afterwards — make it report differences by
  design. It passed 28/28 with zero unexplained lines at the moment it gates, which is where it
  was ticked. Anyone re-running it later will see expected noise, not a regression.

- **The noun "skill" still runs through the bodies where "command" is now meant**, e.g. *"the one
  `/specs:*` skill that runs the repo's own toolchain"*. Left alone deliberately: this is hundreds
  of instances of prose judgement, which is precisely the body audit `## Out of Scope` excludes to
  keep the migration diff reviewable. **Not a broken reference** — nothing points at a missing
  file — so it is cosmetic where the entries above were factual. Follow-up spec.

- **The 93% saving IS the deletion of every trigger phrase and every routing boundary.** Found at
  task 3.2, the moment `lint` first ran against the collapsed surface: `sk-trigger-position` and
  `sk-no-boundary` fire on **28 of 28** commands, where both fired **zero** times before. Not a
  regression introduced by the migration's mechanics — it is what the migration *is*. The skill
  description carried the quoted triggers (*"add a standard/convention"*, *"draft an
  announcement"*) and the `Not for: … →` boundary; the wrapper description, which `## Out of Scope`
  keeps unedited, carries neither. Deleting one of two descriptions deletes what only that one held.

  **Task 6.3 still passes as written** — `lint` exits 0 because both codes are warnings, and
  neither is a *new* `sk-*` code. So the spec's own mechanical gate cannot see this, which is
  exactly why it is written down here rather than left to the exit status.

  **The spec anticipated the risk and sited the evidence in task 7.3** — *"a spoken trigger still
  reaches its command by description alone, with no `/` typed"*. That is the measurement that
  decides whether `## Out of Scope` §Compressing the surviving descriptions can stand. Raised to
  the human with 7.3's result, not before: guessing at it now would substitute taste for the
  measurement the spec deliberately arranged.

- **`README.md` documents the deleted architecture across 131 lines outside task 5.3's scope.**
  Task 5.3 scopes to *"§Cost model — its always-on figures are of a two-file surface and its skill
  count is stale"*, and that section is rewritten. The other 131 stale lines — §The thirty skills,
  the `.claude/skills/` layout, the `skills/*/references/` citation paths, the wrapper prose — are
  a whole-document rewrite of the plugin's public README, which is authoring rather than the
  mechanical substitution the human authorised at the section-1 boundary. **Attempted and
  reverted:** a blanket rename over the full file mangled 28 link paths
  (`skills//docs:add/references/homes.md`), which is exactly why it needs writing rather than
  substituting. **Left for a follow-up spec**, and called out in the run report rather than
  buried — a README describing a shape the plugin no longer has is the most public stale artefact
  this migration leaves behind.

- **The measured total is 2,083, not the 2,069 `## Validation` predicted.** The prediction rested
  on *"the surviving strings are the wrapper descriptions unedited"*, per `## Out of Scope`
  §Compressing the surviving descriptions. Two of them could not stay unedited: tasks 3.5 and 3.6
  changed what `/skill:new` and `/skill:align` **do**, so their `/`-menu strings had become false.
  `/skill:new` landed at exactly 82 by coincidence; `/skill:align` went 78 → 92 (+14), the whole
  difference, because it now names the pair→command migration it gained.

  **Not a violation of `## Out of Scope`.** That section forbids *compressing* descriptions —
  rewriting them for length on separate evidence. Correcting a description that describes deleted
  behaviour is the opposite, and leaving it would have shipped a lie in the one string always in
  context. The 93% cut is unaffected: 30,705 → 2,083 is 93.2%.

- **Spoken routing survived the collapse — measured, 3/3.** The task-3.2 finding (all 28 commands
  report `sk-trigger-position` and `sk-no-boundary`) raised the real possibility that deleting the
  trigger-carrying description had made the surface unroutable by speech. Task 7.3 measured it in
  fresh processes with no `/` typed: *"park a spec for later…"* and *"capture this for the
  backlog…"* both reached `/specs:capture`, and *"add a standard: we always use snake_case…"*
  reached `/docs:add`.

  A fourth run is worth recording because it nearly produced a false negative: the same
  `add a standard` phrase in an **empty sandbox** invoked nothing — correctly, because there was
  no OKF bundle to add to, and the model said so and named the plugin's commands as available.
  Re-run against the real bundle it routed immediately. A functional check on a surface whose
  commands have preconditions must satisfy those preconditions, or it measures the precondition
  instead of the routing.

  **This corrected two standards.** Tasks 4.2 and 4.4 had been written mid-run, before the
  evidence existed, asserting that a `/`-menu-label description *"does not route a spoken
  request"*. The measurement contradicts that, so both were rewritten: routing works, what remains
  is a thinner margin (inference from a short label rather than a verbatim trigger the author
  chose), and restoring triggers is **affordable headroom** at 2,083 against a former 30,705 —
  not a defect to repair.

## Outcome

**Shipped.** The 28 skill+wrapper pairs are now one `commands/<path>.md` each;
`plugins/quenching/skills/` no longer exists. Always-on metadata went
**30,705 → 2,083 characters** — a **93.2% cut**, ~7,676 → 521 approximate tokens, off every
session in every repo that installs the plugin. The `/` surface is unchanged: still 28 entry
points, same paths, same behaviour. Landed as 32 commits on
`plan/collapse-skills-into-commands`, shipped as version 3.0.0.

Beyond the collapse itself:

- **`assets/references/` is the home for shared procedure** — 22 files across 17 trees, all 351
  citations rewritten to the `${CLAUDE_PLUGIN_ROOT}` absolute form and proven to resolve by
  script, with zero surviving relative forms.
- **`skills.py` reads `commands/**` and nothing else.** The bijection, `sk-path-mismatch` and the
  unmirrored-wrapper finding are deleted; a `selftest` fixture proves `sk-no-description` already
  covers the phantom-command mode.
- **`docs/standards/architecture/plugin-layout.md` is new** (`authority: current`); three
  standards were revised, with `context-budget.md` re-derived from the measurement and
  deliberately kept `background`.
- **`/skill:new` mints one file; `/skill:align` migrates a target's pairs** — an adopting repo
  inherits the collapse rather than the shape the plugin just abandoned.
- **`functional-checks.sh`** gives the surface automated functional coverage it never had: 7
  assertions in fresh `claude -p` processes, asserting on captured `tool_use` JSON rather than on
  a process's own claims.

**Measured, not assumed.** `${CLAUDE_PLUGIN_ROOT}` substitutes inside a command body in
production (7.1); `/align` reaches `quenching:docs:align` by name (7.2); spoken routing
survived 3/3 with no `/` typed (7.3). That last one was the genuinely open question — deleting
one of two descriptions deleted every quoted trigger phrase and every `Not for:` boundary at
once, and 7.3 is what turned that from a defect into affordable headroom.

**Left out, deliberately.** `README.md`'s other 131 lines still describe the deleted architecture
— a whole-document rewrite, attempted and reverted, now the most public stale artefact this
leaves behind. The noun *"skill"* still runs through bodies where *"command"* is meant: cosmetic,
not a broken reference, and excluded to keep a 28-file diff reviewable. Both need a follow-up
spec. `allowed-tools` enforcement stays open as `verify-allowed-tools-enforcement`;
`context-budget.md` does not graduate on this evidence.

**What the next reader needs.** Nothing under `commands/**` is testable in the session that edits
it — run `assets/bin/functional-checks.sh` in a fresh process, and never report a surface change
as working on the strength of the session that made it. Task 2.3's body reconciliation only holds
at the 2.2 boundary; re-running it later shows expected noise from 2.4–2.5, not regression.
`skills.py budget` stopped being the skill↔command pairing source at 2.2 — recover that mapping
from `d3b0cd9` if ever needed.
