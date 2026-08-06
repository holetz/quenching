---
type: knowledge
title: Glossary
description: The repo's single A–Z lookup of terms, acronyms, and domain vocabulary — one entry per term, each linking to its full concept doc when one exists.
resource: docs/**
tags: [glossary, vocabulary, terminology]
timestamp: 2026-08-05
audience: both
authority: current
source: quenching skeleton
maintainer: <the team>
---

# Glossary

The repository's **single source of truth for what a term means here**. One entry per
term, in the same bullet syntax every `index.md` uses: `* [<Term>](<path>.md) — <one-sentence
definition>` when a full concept doc exists, or `* **<Term>** — <one-sentence definition>`
when it doesn't — the glossary is the *index* of vocabulary, not the long-form home.

**Resolving a term.** When a repo-specific word, acronym, or piece of jargon is unclear,
**search this file first** (Ctrl-F, or `grep -i '<term>' docs/knowledge/glossary.md`). A
matching entry gives the local meaning and, when linked, points to the doc that explains
it in full. No entry means the term is not yet defined — capture it (see *How to enrich*).

**This file is the ONE deliberate exception to "one concept per file."** A glossary is
inherently a multi-term aggregate — a flat bullet list, not a concept doc per term. It is
also the one exception to an `index.md`'s "only list what exists" rule: an **unlinked**
entry (a term with no concept doc yet) is a normal, permanent, valid state, not a defect.
Keep the list **alphabetically sorted by Term**, keep each definition to a single
sentence, and **link out** rather than explaining in full here.

## Terms

- [**Advisory finding**](../standards/quality/bundle-verification.md) — a WARN the commands' verify
  gate does **not** treat as blocking, reported so a human can look and never so a run stops;
  `stale-doc` is the only one, against the WARN-but-must-fix set (`dir-no-index`,
  `index-broken-link`, `index-orphan`, `glossary-broken-link`, `resource-unresolved`,
  `resource-self`). The category has to stay small — a check that cannot tell "wrong" from "worth a
  look" belongs here or nowhere, and folding one into must-fix makes that set unusable.
- [**Always-on ceiling**](../standards/automation/skills.md) — the per-surface character
  total `skills.py budget` compares the summed descriptions against, commands **and** agent
  definitions alike; set from a measurement and never guessed, and deliberately kept EQUAL to the
  current total so it has no headroom and the next **always-on** command crosses it the day it is
  minted. A `disable-model-invocation: true` command counts 0 and crosses nothing, so the ratchet
  has two exits — re-measure, or make the command typed-only where that is the honest design.
  `budget` reports and never refuses — crossing it prompts a re-measure, not a block.
- [**Always-on metadata**](../standards/automation/skills.md) — the frontmatter
  `description` of every command, resident in every session's context before anything fires and
  therefore the only surface cost paid whether or not a command runs; measured by
  `skills.py budget` from the parsed value, never the YAML source.
- [**Anchorless strategy**](../standards/workflows/plan-git-record.md) — a merge strategy that
  produces **no merge commit** — `fast-forward` and `rebase` — so the **Merge record** has nothing
  to name and carries an explicit none instead of a fabricated pointer. Under both, the per-task
  commits land on the base directly and their subjects resolve there, which is why a merge pointer
  would add nothing rather than being merely unavailable. `specs.py validate` reports the mismatch
  in **both** directions (`sp-bad-merge`): an anchorless strategy carrying a real subject, and a
  merge-producing strategy carrying an explicit none.
- [**Anomaly sidecar**](../standards/quality/parse-honesty.md) — a *second* function reporting what
  a parse could not represent faithfully, placed beside the parser rather than folded into its
  return. `frontmatter_anomalies(text)` re-reads the frontmatter block and names each unfaithful
  read — a stripped comment, an unterminated quote, an indented form the tool does not read, a
  last-winning duplicate key — while `parse_frontmatter` keeps returning a bare dict. The shape is
  the whole point: a `(value, understood)` return would force all nine call sites to decide what an
  un-understood input means, including mid-cycle ones (`status`, `next`, `triage`) that today refuse
  nothing. Every entry is a suspicion the tool **cannot** resolve, never a proven violation, which
  is why callers surface them at warn.
- [**Approved record**](../standards/workflows/plan-lifecycle.md) — the `approved: {date}`
  frontmatter entry recording that a human said go, the one fact the retired `backlog/` → `ready/`
  `git mv` carried that no derivation reproduces; `execute` asks inline and stamps it rather than
  refusing an unapproved spec.
- [**Blocked task marker**](../standards/workflows/task-execution.md) — the `- [!] <id> <title> —
  blocked: <reason>` line implementation writes when attempts stop converging, replacing the
  earlier hidden attempt counter; `specs.py next` skips it and the reason stays legible to whoever
  unblocks it.
- [**Boundary reminder**](../standards/architecture/plugin-layout.md) — a one-clause line that
  states the *edge* of a rule the citing place already owns, seen from the other side (`/docs:add`
  saying the slug is canonical English while the body prose follows whatever language the repo
  declared), as opposed to a restatement, which repeats a fact the citing place neither owns nor
  can change. Note the paraphrase: writing the clause verbatim here would make this entry one more
  member of the census it describes — see
  [prose-sweeps.md](../standards/quality/prose-sweeps.md) §*Write the mention as a placeholder*. It is legitimate
  by the **ownership test** and stays legitimate only under the **verifiable guardrail** — one
  clause, no fact the owner states, and never a narrowing; the third is what caught
  `assets/README.md` scoping the language rule to `audience: human` docs for weeks.
- [**Branch de integração**](../standards/git/branching.md) — sob o fluxo develop/main, a
  `develop`: onde toda `plan/<slug>` mergeia ao concluir. Acumula quantas specs quiserem sem que
  nada seja publicado; só se torna público quando a **branch de publicação** recebe seu merge
  deliberado. Ver esse verbete para o outro lado do par.
- [**Branch de publicação**](../standards/git/branching.md) — sob o fluxo develop/main, a `main`:
  a única branch que recebe o merge deliberado `develop → main`, o único momento em que o lockstep
  de versão se move e uma tag é criada. Nunca acumula specs em integração — isso é a **branch de
  integração** (`develop`), de onde `plan/<slug>` é cortada e para onde mergeia. O gatilho da
  publicação é a demanda do mantenedor, nunca uma cadência, e a rota é sempre um merge local.
- [**Branch record**](../standards/workflows/plan-git-record.md) — the `branch: {base, work}`
  frontmatter entry stamped by `/specs:execute` for **any** branch that is not the repo's base —
  the one it cut and the one a human already had open alike — write-once. `work` is derivable
  while the branch is checked out; **`base` is not** — after the merge, git
  cannot say what the branch was cut from, which is the whole reason the record exists and why it
  is captured while still true. Work done on the base stamps nothing, because a record whose `base`
  equals its `work` states no fact. **The record is never the signal**: anything asking whether a
  spec is in flight asks git whether the ref is alive — the record's `work`, falling back to
  `plan/<slug>` — since a human may cut a branch with no record and a record outlives the branch
  it names.
- [**Bundle density**](../standards/quality/bundle-verification.md) — the figures `/docs:status`
  prints alongside conformance (concept docs per home, empty homes shown as `0`, glossary size,
  which `standards/` subjects hold anything), carrying **no finding code** by design: coding them
  would make permanent noise of a repo that legitimately has no `mlops/`, omitting them would hide
  a bundle passing every check while knowing nothing. A figure informs without accumulating as a
  defect to chase.
- [**Cache trap**](/plugins/quenching/assets/references/skill-new/capabilities.md) — the standing
  cost of an inline `model:`/`effort:` pin in a command's frontmatter: the pin is part of the
  session's prompt-cache key, so changing it makes the next request recompute every input token.
  A sub-agent's pin is cache-safe because it carries its own context; an orchestrator's is not,
  which is why five `effort: low`/`medium` pins were dropped rather than kept for their tier.
- [**Canonical case list**](../standards/code/frontmatter-parsing.md) — the twelve frontmatter rows
  that `skills.py`, `specs.py` and `okf-validate.py` must all decide **identically**, duplicated
  byte-identically as each tool's `CANONICAL_CASES` and run by each tool's own `selftest`. It is the
  **lockstep unit** standing in for the shared module the three cannot have — each is a
  self-contained single file and none may import the others — and it works by
  localising a break: a parser that drifts fails its OWN selftest on a row the other two still pass.
  A tool may read *more* than the list requires and must then not report the form it genuinely read,
  so a form a tool does **not** read can never become a row; that asymmetry is named per-tool
  instead, which is why a block scalar is diagnosed by two of the three and by neither the list nor
  the third.
- [**Canonical set**](../standards/code/canonical-set-parsing.md) — an ordered contract declared in
  one place and read in many: `schema.json`'s `sections` array, its `phases[].entryGate`, the
  frontmatter record vocabulary. Each declares **both** a membership (which members) and an order
  (in what sequence), and the two change independently — so code that consumes one must slice by
  declared membership and never by an ordinal position, which is an unchecked claim about the set's
  shape that keeps returning a plausible answer once the set grows. Distinct from the
  [Canonical case list](../standards/code/frontmatter-parsing.md), which is one specific lockstep
  unit rather than the general shape.
- [**Commit record**](../standards/workflows/plan-git-record.md) — the `subject: <line>` field on a
  completed task line, written mechanically by `specs.py task --check --subject`, that links the
  checkbox to the commit implementing it by naming that commit's **subject** and resolving with
  `git log --grep --fixed-strings`. Because a subject is known *before* the commit exists, the box
  is ticked into the commit it describes and no bookkeeping commit follows it — the same inversion
  that lets `merge: {strategy, subject}` be stamped on the work branch and the merge be the last
  action of `/specs:conclude`. Nothing is inscribed into the message as a trailer: the recorded
  subject is whatever the target repo's own convention produced. A spec built before this change
  carries `commit: <sha>` and resolves by sha; both forms are read forever and neither is
  backfilled.
- [**Context integral**](../standards/automation/context-discipline.md) — a run's true cost,
  `tokens × turns remaining`, not `tokens`: every turn re-sends the whole conversation, so a block
  loaded once is paid once for each turn that follows it. It has exactly two factors, so there are
  exactly two ways to cut it — **open less** and **run for less time** — and a proposal that does
  neither is not an optimisation. Because it is quadratic in the turn count, shortening the window
  beats shortening the reads. [skills.md](../standards/automation/skills.md)
  §The other half owns the integral itself and the 344-turn run it was measured on.
- [**Derived stage**](../standards/workflows/plan-lifecycle.md) — a spec's position in its life
  (`captured` → `proposed` → `designed` → `refined` → `ready` → `approved` → `executing`),
  COMPUTED from which headings are filled and which records frontmatter carries rather than
  declared in a field, so it regresses on its own when a section empties instead of going stale;
  resolution is last-match-wins, which is why `executing` sorts last.
- [**Entry point**](../standards/naming/command-surface.md) — one `commands/<path>.md` file, whose
  path IS its identity (`commands/docs/add.md` → `/docs:add`); since Claude Code merged commands
  into skills there is no second file to mirror, so there is nothing an entry point can drift from.
- [**Generated listing**](../standards/architecture/generated-listings.md) — a file, or a marked
  zone inside one, that a command rebuilds from what a directory holds. Always a **second source**
  of a fact the disk already carries, so it earns its keep only where nothing else derives that
  fact **and** a checker can decide its freshness — staleness being its only failure mode, and a
  silent one. The decision criterion is asked before any code: does a command already answer the
  same question on demand? Yes → the listing is duplication and its checker is pure cost; no → the
  listing IS the source and a checker is mandatory. The `docs/` bundle's `index.md` files are the
  bounding counterexample: nothing else enumerates the bundle, so they keep their checks; the
  retired `specs/plans/index.md` duplicated `specs.py list` and went with its four `sp-*` codes.
- [**Handler ladder**](../standards/automation/hooks.md) — the ordering a hook's handler is chosen
  from, cheapest first: a deterministic `command` script (zero tokens on no-match), then a `prompt`
  handler (one cheap judgment per firing), then an `agent` handler — which on a per-tool-call event
  is an LLM toll booth on every operation (`sk-hook-llm-frequent`). Climbed only when the rung
  below cannot express the check.
- [**Language declaration**](../standards/agents/communication.md) — the single line on a repo's
  **root** harness file naming one BCP-47 tag (`Language: pt-BR — the contract is …`), which governs
  all prose the agent authors, conversation as much as artifact. It carries a value and a citation
  and nothing else: never a paraphrase of the rule it cites, and never a second configuration key.
  Only the root file counts, because only that one is in context at session start — the property the
  form was chosen for. **Silence is not a default of `en`**; a repo that declares nothing is under no
  constraint, and adoption is opt-in per repo. Nothing machine-checks it, so `/docs:harness` classing
  the line **KEEP** is the only thing between it and a silent deletion.
- [**Merge record**](../standards/workflows/plan-git-record.md) — the
  `merge: {strategy, subject, pr}` frontmatter entry stamped by `/specs:conclude`, write-once,
  **on the work branch before the merge** — which is what makes the merge that command's last
  action and leaves nothing to be committed to the base after it. The strategy was a human choice
  and the subject names the merge commit it is about to produce; recording both is what tells a
  future reader whether the per-task subjects still resolve from the base. An **anchorless
  strategy** carries an explicit none here. `pr` exists only on the **pull-request route** and
  names the pull request the merge went through — absent on every local conclusion, and refused
  under `fast-forward`, which `gh pr merge` cannot perform (`sp-merge-pr-no-route`).
- [**Moment**](../standards/workflows/plan-artifacts.md) — the point on a spec's timeline a canonical
  section is read at, and the axis that replaced an `audience` field nobody read: `decision` (the
  human, weighing whether to build), `build` (the executor, at step 4 of `/specs:execute`), `close`
  (`/specs:conclude`, at archive time). One value per section, declared in `schema.json` and in
  `specs.py`'s `DEFAULT_SCHEMA`, and **resolved rather than enumerated** — `specs.py section <slug>
  --moment build` returns the six an executor needs, so a command body names the moment instead of
  repeating a heading list that can drift from the schema. `## Discoveries` carries no moment at
  all: captured indiscriminately while building, it is resolved by `/specs:develop`'s triage sweep
  on its own schedule. The axis replaced a human/agent binary that was **prose nobody applied** —
  measured, that binary cut 14% and named the wrong sections, leaving `## Out of Scope` invisible to
  the one reader it exists to constrain.
- [**Moment**](../standards/workflows/plan-artifacts.md) — the point on a spec's timeline a canonical
  section is read at, one value per section: `decision` (the human, weighing whether to build),
  `build` (the executor), `close` (`/specs:conclude`). Declared in `schema.json` and `DEFAULT_SCHEMA`
  and **resolved rather than enumerated** — `specs.py section <slug> --moment build` returns the six
  an executor needs, so a body names the moment instead of a heading list that can drift. Replaced
  an `audience` field nobody read; `## Discoveries` carries no moment at all.
- [**Origin key** (`source_uri`)](../standards/quality/bundle-verification.md) — the frontmatter key
  holding the **exact** URI or path of the source unit an imported doc was minted from, written by
  `/docs:import` and by no other command; a doc with no external origin simply does not have it.
  Single-valued, one line, no prose — that is what makes finding the doc that already covers a unit
  an equality test (`grep -rn 'source_uri: <uri>'`) instead of the model recognising prose it wrote
  itself. Distinct from `source:`, which stays prose about who originated a rule. Nothing checks the
  value: truthfulness is decidable only against the source at the instant it was read, and a unit
  collapsed from several seeds carries only one origin — both recorded as **accepted gaps**.
- [**Parked follow-up**](../standards/workflows/plan-lifecycle.md) — an out-of-scope finding a
  definition pass records as ONE line of `## Discoveries` on the spec it is developing, instead of
  minting a spec for it. Parking is free by construction: `## Discoveries` appears in no stage rule,
  so filling it moves no derived state. Turning one into a file belongs to `/specs:conclude`'s
  harvest, which runs once the parent's fate is known — and a line another open spec already covers
  never becomes a file at all, resolving as `dismissed: already covered by {slug}`.
- [**Parse honesty**](../standards/quality/parse-honesty.md) — the obligation that a verifier names
  its own parse failure rather than reporting it as a content gap. The episode that earned it: a
  command `description` truncated at a `#` surfaced as `sk-no-description` — a statement true of the
  string `lint` held and false of the file on disk — so the author either distrusts the checker or
  edits prose that was never wrong. Three consequences bind: the diagnostic ships **with** the lossy
  transform and never after it, it runs **before** the content checks it would otherwise be mistaken
  for, and a tool that cannot prove it implements the rule does not get the rule. Severity is
  **warn**, because a deliberate comment and lost prose are byte-identical — the tool states a
  suspicion it cannot resolve. Delivered by an **anomaly sidecar**.
- [**Phantom command**](../standards/architecture/plugin-layout.md) — a non-entry-point file left
  under `commands/`, which registers as a real `/` entry that does nothing; it does not error, so
  the only thing that catches it is `sk-no-description`, and it is why shared procedure lives under
  `assets/`.
- [**Phase gate**](../standards/workflows/plan-artifacts.md) — the set of sections a spec must have
  filled before a heading counts as required, which is what makes the explicit-none rule
  stage-scoped rather than absolute. Two gates move a file (`new` into `plans/`, `promote` into
  `archive/`) and refuse with exit 2 and the missing list rather than warning; the `ready` gate is
  a derived stage that refuses nothing. All of them live once in `schema.json`, read by both
  `promote` and `validate`.
- [**`[P]` marker**](../standards/workflows/task-execution.md) — the opt-in flag set on a task when
  the tasks are written, declaring it may run concurrently with its group; honoured only when
  `specs.py parallel` proves the group's `files:` sets disjoint, and never inferred while building.
- [**Plugin config**](../standards/workflows/plugin-configuration.md) — `.claude/quenching.json`, the
  single file a target repository uses to declare anything to this plugin: `backend`, `specsBranch`,
  `worktreeSetup` and `azureStates`. It replaced `specs/config.json`, whose home stopped working once
  a repository could have no `specs/` folder at all. Absence yields the documented defaults, never a
  null and never a refusal — except `azureStates`, which has no default because the project's own
  process defines the states, and whose absence refuses instead of guessing; every other way it can
  be wrong comes back as a field for `doctor` to judge.
- [**Probe**](../standards/architecture/align-surface.md) — the opening run of a front's own
  verifier (`okf-validate.py`, `specs.py doctor`, `skills.py doctor`) whose exit code decides
  whether an align inventories anything at all, making a no-op align cost a couple of tool calls;
  the same programs run again as the closing verification.
- [**Projection / storage**](../standards/architecture/spec-backend.md) — the pair that decides
  whether a backend may map a canonical field onto a native construct. A **projection** is written
  from the document on every write and never read back, which makes it duplicated truth however
  cheap it is; **storage** is a value something actually reads, which makes the native copy the
  only one. The test is one question — *does anything read the native value back?* — and it admits
  exactly two remedies: retire the mapping, or make a read consult it. The issue title took the
  second (stored without `title:`, reassembled on read, so a web-UI edit now renames the spec); the
  `## Tasks`→sub-issue mapping took the first. A mapping also needs the native value to be **the
  same fact**: an issue's `created_at` is when the ISSUE was made, so the capture date has no
  faithful counterpart and stays in the document. A field with no honest native copy is not
  duplicated truth — it is the only copy. A third case is neither of the two: **rendering** carries
  state the document already *derives* — never a canonical field of its own — onto a native
  surface, recalculated from scratch on every write and never read back, admitted only when it
  also costs no extra call and is discardable without loss. The `spec:` labels a `github` or
  `azure-boards` backend reconciles onto its own issue or work item — one per frontmatter record
  present, plus one for the derived `executing` stage — are the example this repository has.
- [**Prose fan-out**](../standards/quality/computed-fact-prose-fanout.md) — the set of prose sites
  a fact a tool computes ages the moment it changes — a schema key, a surface's command count — and
  which every checker in this repo is blind to by construction: the selftest proves the key *works*, `specs.py validate` reads records rather
  than descriptions of them, and `stale-doc` only fires where a doc's `resource:` happens to name
  the schema file. Measured twice on one branch: **one field added → four sites stale** across four homes, and **one
  command retired → ten sites stale** across four files, with every checker green in both. Found by
  grepping the record's **spelled-out** form (`merge: {strategy`), never its name, and fixed in the
  task that adds the key. Historical mentions are correct as written, which is why this stays a
  human sweep rather than a check — the same mention/use judgment
  [prose-sweeps.md](../standards/quality/prose-sweeps.md) already establishes is invisible to a
  regex, reached from the opposite direction: that one is the sweep you ran, this one the sweep you
  never ran.
- [**Promote**](../standards/workflows/plan-lifecycle.md) — the gated `git mv` that moves a spec
  from `plans/` to `archive/` without renaming it, stamping `outcome: done | abandoned`. Under v3
  it is the ONE hop a spec ever makes: the `backlog/` → `ready/` promote is retired, and the human
  OK it used to carry is the **Approved record** instead. Promoting as `done` refuses
  while `- [ ]` boxes remain unless forced; `abandoned` is always allowed.
- [**Refinement record**](../standards/workflows/plan-artifacts.md) — the `refined: {mode, date}`
  entry a spec's **frontmatter** gains once it has been interrogated, whose absence raises the
  non-gating `sp-unrefined` warning.
- [**Resource glob set**](../standards/quality/bundle-verification.md) — the format of an OKF
  doc's `resource:`, a plugin convention rather than an OKF rule: a **comma-separated** list of
  repo-root-relative paths and globs using `*`/`**` **only**, matched **segment-wise everywhere**
  including the `:(glob)` pathspec handed to `git log`, since plain `fnmatch` and git's default
  wildmatch both let `*` cross a `/` and would silently widen every shallow scope. Anything else
  (braces, character classes, `?`) is classified `unknown` and never reported as a violation. It
  says what the doc *governs* — which is why it replaced the `file:line` anchor doctrine once
  named, and why it is also the input `stale-doc` needs.
- [**Retired (reserved artifact)**](../standards/architecture/retiring-a-reserved-artifact.md) — a
  reserved filename nothing produces or checks any more, but which **keeps** its slot in the
  validator's `RESERVED` set and its skip in the `PreToolUse` hard block. Deliberately not
  **unreserved**: dropping the reservation too would send every surviving instance down the
  concept-doc path, turning it into a `no-frontmatter`/`missing-type` ERROR in target repos that
  changed nothing. `docs/log.md` is the first artifact retired this way.
- [**Routed command**](../standards/automation/skills.md) — a command something reaches **without a
  human typing its name**, whether by a spoken trigger or by another command's body naming it; its
  `description` stays resident in every session's context and is charged against the
  **Always-on ceiling**. The half of the test that is mechanical is not a judgement call:
  `skills.py lint` derives the name-reachable set from the command bodies, so classify against the
  instrument. The complement is a **Typed-only command**, and the criterion is a floor rather than a
  quota — on a small surface it may admit nobody.
- [**Rules/rationale markers**](../standards/automation/context-discipline.md) — the pair of HTML
  comments, `<!-- rules -->` and `<!-- rationale -->`, that split a normative section's binding half
  from the measurement and history behind it, so `skills.py read --rules-only` can return the first
  without the second. **A marker, never a heuristic**: a model deciding per read which sentences
  bind is non-deterministic and fails *silently*. Compaction here is **relocation, never deletion**
  — the rationale stays on disk and stays contract, only its position moves. A missing marker
  degrades to the whole section and **says so**, never to emptiness. A marker's reach ends at the
  next heading, so a section with sub-sections is marked **per sub-section**.
- [**Scope ladder**](../standards/automation/hooks.md) — the four rungs a hook may be installed at,
  narrowest first: a command's own frontmatter `hooks:` block (fires only while that command runs),
  a `settings.json` hook with an event + `matcher`, a gated wide event, and an unmatched
  session-wide hook — the top rung, and a finding (`sk-hook-unmatched`) unless the reason nothing
  narrower suffices is stated where it is wired. `skills.py` holds rung 1 and rung 2 to the same
  checks from one implementation.
- [**Section boundary**](../standards/automation/context-discipline.md) — the moment a `## N.`
  section's last task commits with another section still ahead: a clean point for a build to
  **offer** to stop, because the resumption trail (`## Handoff`, `git log`, the recorded commit
  subjects) is already maintained for other reasons, which is what makes the cut nearly free. The
  trigger is **that event, never a window size** — a threshold invented before it is measured fixes
  the answer. It offers and never imposes, never ends a run itself, and writes no new state.
- [**Section reader**](../standards/automation/context-discipline.md) — the verb that resolves the
  `§X` address the prose was already writing: `skills.py read <path> --sections "§A"` over free
  markdown, `specs.py section <slug> "A,B"` over a spec's fourteen canonical headings. Both take a
  **list**, because turns are the other factor of the **Context integral** and N sections fetched
  over N turns can lose to reading the whole file. A section runs to the next heading of the same
  level or shallower, a fenced block is never read as a heading, and a name that resolves to
  nothing is a **refusal that names it**, never an empty answer. Both prove the rule against the
  same **Canonical set**, `SECTION_CASES` — which pins the *sectioning* rule the two answer
  identically, and therefore not the ladder below, a CLI-argument rule only the first has.
  **They take that list differently, deliberately.** `skills.py` resolves each value whole before
  reading it as a list, so a heading carrying its own comma — `## What crosses, what stays` — is
  cited by its full title; `specs.py` splits unconditionally, which is unreachable there because
  the fourteen canonical headings carry no comma and it refuses any name outside them.
- [**Report mold**](../standards/architecture/report-mold.md) — a seção única que possui a forma em
  que **todos** os comandos de uma frente imprimem seu relatório, citada por cada corpo, que declara
  só o próprio delta. Três bandas fixas (cabeçalho · corpo · próximo passo), blocos declarados fixos
  ou opcionais, um conjunto ordenado de colunas do qual cada comando toma um subconjunto, e um bloco
  de próximo passo executável como impresso. É **literal** — carrega o bloco renderizado, não uma
  descrição dele. Mora dentro de um arquivo que os corpos já carregam, para não custar uma chamada
  de ferramenta a mais; o custo em caracteres é medido e declarado, nunca estimado. Distinto de
  **Shared mold**, que governa chaves de frontmatter e não saída.
- [**Shared mold**](../standards/architecture/shared-mold-keys.md) — a frontmatter key block owned
  once and cited by several commands, so each mints a doc from the same stamp instead of restating
  it (`docs-add/homes.md` §The frontmatter stamp, cited by four). Because a mold is a *fill-in
  invitation*, a key only one writer may legitimately set stays **out** of it and lives with that
  writer's own contract — an annotation inside the mold is not equivalent, as the `resource:`
  precedent showed. The test is not "may this be absent?" but "may this citer write it at all?".
- [**Spec backend**](../standards/architecture/spec-backend.md) — where a repository's specs
  actually live: markdown files on a dedicated branch, GitHub issues, or Azure Boards work items,
  declared by `backend` in [the plugin config](../standards/workflows/plugin-configuration.md).
  Every backend implements **five primitives over the canonical document** — never one method per
  CLI verb — so the fourteen sections, the frontmatter records and the derived stages are shared
  code and cannot diverge between targets. The selected backend is the sole source of truth: there
  is no shadow local store, and a declared-but-unimplemented backend refuses rather than falling
  back to `files`.
- [**Typed-only command**](../standards/automation/skills.md) — a command carrying
  `disable-model-invocation: true`, reached only by a human typing it; its `description` leaves
  every session's context and `skills.py budget` charges it **0**. Residency and content are
  independent axes, so the description **keeps all three parts at full length** — the human picking
  it out of the `/` menu is now its only reader, and has no routing to fall back on. Measured, not
  assumed: the field also makes the command unreachable **by name** through the Skill tool, so
  putting it on a stage another body invokes leaves that stage silently inert (`sk-inert-stage`,
  error). The complement is a **Routed command**.
- [**Verification policy**](../standards/workflows/task-execution.md) — the per-spec declaration
  (`per-task`, `per-section`, `end-of-plan`) written at creation that decides when a task's
  `verify:` command runs, so execution never guesses and never asks mid-task.
- [**Version lockstep**](../standards/ci-cd/versioning-release.md) — the six version strings a
  release must bump together, split into two halves read by two independent consumers: the
  `plugin.json` `version` + `VERSION` pair Claude Code compares to decide an upgrade fires, and the
  `VERSION` constant in each of the three shipped tools, which answers `--version` and identifies
  any **legacy copy** a target still carries under `.claude/hooks/` from before resolution went
  plugin-first. Since nothing installs a tool any more, **no automated check asserts the six
  agree** — the whole lockstep is discipline, read back by hand at conclude. Distinct from the
  **Canonical case list**, which is the lockstep unit for the
  three tools' *parser behaviour* rather than their version strings.
- [**Worktree setup**](../standards/workflows/worktree-setup.md) — the single key `worktreeSetup`
  in `.claude/quenching.json`, holding a command `/specs:execute` runs once inside a newly created
  worktree so a repo with installed dependencies gets a usable tree rather than one that breaks at
  the first `verify:`. `specs.py` reads it and never executes it. Declaring nothing is the normal
  case and never a finding; the two that are — `sp-config-unknown-key` and `sp-config-unparseable`
  — exist only so a mistyped key cannot fail silently. Its consent is the isolation offer itself:
  the command is shown verbatim in the plan block, and choosing Worktree is the OK for it.
- [**Withdrawn contract residue**](../standards/quality/withdrawn-contract-residue.md) — the prose
  still asserting a contract a change **removed**, and the sibling of **Prose fan-out**
  ([computed-fact-prose-fanout.md](../standards/quality/computed-fact-prose-fanout.md)) for the case
  where nothing computes the fact: with no value to spell out, each site wrote the rule in its own
  words, so no grep finds the set. The mitigation is upstream — a spec's `## Impact` names the
  **class** of documents asserting the contract and derives the file list mechanically, because
  enumerating instances under-counts a class that quietly gained a member. Measured five times on
  one branch withdrawing the installed-tool contract: three caught in execution, two only at the
  branch review, and one of those in a file `## Impact` **had** named and half-covered — which is
  why naming the file is not enough, and the reviewer's question is *what did this make false?*
  rather than *which files changed?*

## How to enrich

Add a term whenever a repo-specific word, acronym, or piece of jargon surfaces that a
newcomer would not know. Three ways in:

- **Automatically, as a tail of a capture.** The `quenching` knowledge skills
  (`quenching-docs-learn`, `quenching-docs-add`, `quenching-docs-import-memory`) each check, at
  the end of a capture, whether the new concept introduced a term that belongs here, and
  add or update the entry — linking it to the concept doc just written.
- **On demand, one term at a time.** Run `quenching-docs-define` to add or refine a single
  entry (inserted in alphabetical position, MERGE — never clobbering a filled definition).
- **In bulk, across the whole bundle.** Run `quenching-docs-glossary-backfill` to sweep every doc
  already in `docs/` for repo-specific terms that were never fed into the glossary and
  backfill them in one pass.

Keep entries honest: define the term as **this repo** uses it, not the dictionary sense,
and let the linked doc carry the depth.
