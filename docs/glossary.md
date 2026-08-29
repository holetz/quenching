---
type: concept
title: Glossary
description: The repo's single A–Z lookup of terms, acronyms, and domain vocabulary — one entry per term, each linking to its full concept doc when one exists.
resource: /docs/**
tags: [glossary, vocabulary, terminology]
timestamp: 2026-08-25
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
**search this file first** (Ctrl-F, or `grep -i '<term>' /docs/glossary.md`). A
matching entry gives the local meaning and, when linked, points to the doc that explains
it in full. No entry means the term is not yet defined — capture it (see *How to enrich*).

**This file is the ONE deliberate exception to "one concept per file."** A glossary is
inherently a multi-term aggregate — a flat bullet list, not a concept doc per term. It is
also the one exception to an `index.md`'s "only list what exists" rule: an **unlinked**
entry (a term with no concept doc yet) is a normal, permanent, valid state, not a defect.
Keep the list **alphabetically sorted by Term**, keep each definition to a single
sentence, and **link out** rather than explaining in full here.

## Terms

- [**Advisory finding**](standards/quality/bundle-verification.md) — a WARN the commands' verify
  gate does **not** treat as blocking, reported so a human can look and never so a run stops. The
  category is currently **empty**: its only member, `stale-doc`, was retired on 2026-08-27 and its
  measurement became a figure with no code beside it (§Resource activity). Everything the validator
  emits is now in the WARN-but-must-fix set (`dir-no-index`, `index-broken-link`, `index-orphan`,
  `glossary-broken-link`, `resource-unresolved`, `resource-self`). The category stays named because
  the distinction is real and the next check that cannot tell "wrong" from "worth a look" belongs
  here or nowhere — and because 50 of 95 docs raising the one member is how it emptied: an advisory
  nobody reads is worse than no advisory.
- [**Agent-choice catalogue**](standards/workflows/agent-choice-catalogues.md) — the shared
  shape `subjects`, `tagCatalog` and `workItemTypes` all follow in `.claude/quenching.json`: an
  abstract key mapping to a `description` an agent reads to PROPOSE a choice, which a human then
  CONFIRMS — never silently picked.
- [**Always-on metadata**](standards/automation/skills.md) — the frontmatter
  `description` of every command, resident in every session's context before anything fires and
  therefore the only surface cost paid whether or not a command runs.
- [**Anchorless strategy**](standards/workflows/plan-git-record.md) — a merge strategy that
  produces **no merge commit** — `fast-forward` and `rebase` — so the **Merge record** has nothing
  to name and carries an explicit none instead of a fabricated pointer. Under both, the per-section
  commits land on the base directly and their subjects resolve there, which is why a merge pointer
  would add nothing rather than being merely unavailable. `cq specs validate` reports the mismatch
  in **both** directions (`sp-bad-merge`): an anchorless strategy carrying a real subject, and a
  merge-producing strategy carrying an explicit none.
- [**Anomaly sidecar**](standards/quality/parse-honesty.md) — a *second* function reporting what
  a parse could not represent faithfully, placed beside the parser rather than folded into its
  return. `frontmatter_anomalies(text)` re-reads the frontmatter block and names each unfaithful
  read — a stripped comment, an unterminated quote, an indented form the tool does not read, a
  last-winning duplicate key — while `parse_frontmatter` keeps returning a bare dict. The shape is
  the whole point: a `(value, understood)` return would force all nine call sites to decide what an
  un-understood input means, including mid-cycle ones (`status`, `next`, `triage`) that today refuse
  nothing. Every entry is a suspicion the tool **cannot** resolve, never a proven violation, which
  is why callers surface them at warn.
- [**Approved record**](standards/workflows/plan-lifecycle.md) — the `approved: {date, by}`
  frontmatter entry recording that a spec may be built, and on whose authority: `by: human` is a
  person's word (the fact the retired `backlog/` → `ready/` `git mv` carried), `by: low-gear` is the
  `low` level of the gears scale authorizing the mode and the develop pass stamping on it. Absent
  `by:` reads as `human`; `execute` asks inline and stamps `by: human` rather than refusing an
  unapproved spec.
- [**Batching contract**](standards/automation/context-discipline.md) — a named block in a
  command body naming which of its consecutive tool calls are ONE call, so the batching rule is
  checkable against the body instead of re-judged every run. Calls split only where the next
  command's *input* depends on the previous one's output; splitting for tidiness, or to report
  progress between two commands, buys nothing and is paid by every turn after it. It is the first
  of the two rules on the **Context integral**'s third axis, emit fewer turns per unit of work;
  `/quenching:specs:develop` carries the standing example, with three such points.
- [**Blocked task marker**](standards/workflows/task-execution.md) — the `- [!] <id> <title> —
  blocked: <reason>` line implementation writes when attempts stop converging, replacing the
  earlier hidden attempt counter; `cq specs next` skips it and the reason stays legible to whoever
  unblocks it.
- [**Boundary reminder**](standards/architecture/plugin-layout.md) — a one-clause line that
  states the *edge* of a rule the citing place already owns, seen from the other side (`/quenching:knowledge:add`
  saying a heading is canonical English while the body prose follows whatever language the repo
  declared), as opposed to a restatement, which repeats a fact the citing place neither owns nor
  can change. Note the paraphrase: writing the clause verbatim here would make this entry one more
  member of the census it describes — see
  [prose-sweeps.md](standards/quality/prose-sweeps.md) §*Write the mention as a placeholder*. It is legitimate
  by the **ownership test** and stays legitimate only under the **verifiable guardrail** — one
  clause, no fact the owner states, and never a narrowing; the third is what caught
  `assets/README.md` scoping the language rule to `audience: human` docs for weeks.
- [**Branch record**](standards/workflows/plan-git-record.md) — the `branch: {base, work}`
  frontmatter entry stamped by `/quenching:specs:execute` once the work ref is resolved, write-once —
  for **any** branch that is not the repo's base (the one it cut and the one a human already had
  open alike), and for work done in place, where `work` equals `base`. `work` is derivable while
  the branch is checked out; **`base` is not** — after the merge, git cannot say what the branch
  was cut from, which is the whole reason the record exists and why it is captured while still
  true. **The record is never the signal**: anything asking whether a spec is in flight asks git
  whether the ref is alive — the record's `work`, falling back to `plan/<id>-<handle>` — since a human may
  cut a branch with no record and a record outlives the branch it names. **`work == base` is the
  one exception**, and only because that ref cannot die: the base is alive in every repository, so
  liveness would answer *yes, in flight* forever, and the record has to be read instead.
- [**Bundle density**](standards/quality/bundle-verification.md) — the figures `/quenching:knowledge:status`
  prints alongside conformance (concept docs per home, empty homes shown as `0`, glossary size,
  which `standards/` subjects hold anything), carrying **no finding code** by design: coding them
  would make permanent noise of a repo that legitimately has no `mlops/`, omitting them would hide
  a bundle passing every check while knowing nothing. A figure informs without accumulating as a
  defect to chase.
- [**Bundle root**](standards/architecture/bundle-root.md) — the fixed `/docs/` location of a
  target's OKF bundle, and `/.specs/` for a files-backend specs workspace, a convention no
  configuration file names because an LLM executor runs command bodies literally and a root it
  must resolve from config is a root it can resolve wrong.
- **Cache trap** (`plugins/quenching/assets/references/components-command-new/capabilities.md`) — the standing
  cost of an inline `model:`/`effort:` pin in a command's frontmatter: the pin is part of the
  session's prompt-cache key, so changing it makes the next request recompute every input token.
  A sub-agent's pin is cache-safe because it carries its own context; an orchestrator's is not,
  which is why five `effort: low`/`medium` pins were dropped rather than kept for their tier.
- [**Canonical case list**](standards/code/frontmatter-parser.md) — the twelve frontmatter rows
  the one shared `common/frontmatter.py` parser must decide correctly, held in
  `tests/test_frontmatter.py`'s `CANONICAL_CASES` and run by the test suite. It used to be the
  **lockstep unit** standing in for a shared module three self-contained scripts could not have,
  each duplicating the table byte-identically and running it in its own `selftest` — a parser that
  drifted failed its OWN selftest on a row the other two still passed. One parser now reads every
  form the table's three predecessors read between them, so the list is what its tests hold it to,
  not what keeps three copies from disagreeing.
- [**Canonical set**](standards/code/canonical-set-parsing.md) — an ordered contract declared in
  one place and read in many: `schema.json`'s `sections` array, its `phases[].entryGate`, the
  frontmatter record vocabulary. Each declares **both** a membership (which members) and an order
  (in what sequence), and the two change independently — so code that consumes one must slice by
  declared membership and never by an ordinal position, which is an unchecked claim about the set's
  shape that keeps returning a plausible answer once the set grows. Distinct from the
  [Canonical case list](standards/code/frontmatter-parser.md), which is one specific lockstep
  unit rather than the general shape.
- [**Cosmetic handle**](standards/architecture/spec-backend.md) — the kebab-case tail beside a
  spec's native ID in a git name: `plan/974-citacao-pendurada`. **Only the number resolves
  anything.** The handle is derived from the title on every use and never parsed back, which is
  exactly what keeps it from becoming the second answer to "which spec is this" that the slug was.
  `cq specs export` names its dump files the same way, so a spec's branch and its rescue copy
  cannot disagree about what to call it.
- **Compose** (`plugins/quenching/assets/references/specs-develop/questions.md`) — the monotonic
  half of a `/quenching:specs:develop` pass: it takes a spec from wherever its derived stage leaves
  it to a closed ten-section ready set, filling what is absent and sharpening what is thin, and it
  never overturns what a human settled. Overturning is **Refine**'s. It replaced the `shape`
  and `gate` banks, which were one operation split by an edit whose only job was to move a derived
  stage.
- [**Commit record**](standards/workflows/plan-git-record.md) — the `subject: <line>` field on a
  completed task line, written mechanically by `cq specs task --check --subject`, that links the
  checkbox to the commit implementing it by naming that commit's **subject** and resolving with
  `git log --grep --fixed-strings`. Because a subject is known *before* the commit exists, the box
  is ticked into the commit it describes and no bookkeeping commit follows it — the same inversion
  that lets `merge: {strategy, subject}` be stamped on the work branch and the merge be the last
  action of `/quenching:specs:conclude`. Nothing is inscribed into the message as a trailer: the recorded
  subject is whatever the target repo's own convention produced. A spec built before this change
  carries `commit: <sha>` and resolves by sha; both forms are read forever and neither is
  backfilled. Squashed to one commit per **Section boundary**, every task the section held is
  re-stamped onto that one surviving commit's subject — the anchor narrows to section granularity,
  never loses resolvability.
- **Contaminating block** (`plugins/quenching/assets/references/specs-fanout/fanout.md`) — a block
  whose pending decision changes the specs *after* it in a queue, as opposed to a **local** one that
  stops only its own spec. The classification is the executor's to declare, because only it knows
  what the decision touches: a local block marks `[!]` and the queue moves on, a contaminating one
  stops the run and asks. A red declared gate stops the queue whichever was declared, and the
  blocked spec leaves the branch's `quenching-specs:` mark so the pull request never implies it
  carries what it does not.
- [**Context (components)**](standards/naming/command-surface.md) — one of the four sibling
  contexts under the `components` front — `command/`, `agent/`, `hook/`, `harness/` — each named
  for the artifact it mints, none a sub-type of another. A front-level verb sits at the front's own
  root (`/quenching:components:align`); an artifact-level verb sits under its context
  (`/quenching:components:command:new`).
- [**Context integral**](standards/automation/context-discipline.md) — a run's true cost,
  `tokens × turns remaining`, not `tokens`: every turn re-sends the whole conversation, so a block
  loaded once is paid once for each turn that follows it. It has exactly two factors, and three ways
  to reach them — **open less**, **run for less time**, and **emit fewer turns per unit of work** —
  and a proposal that does none of the three is not an optimisation. Because it is quadratic in the
  turn count, shortening the window beats shortening the reads.
- **cq** (`plugins/quenching/assets/references/align/tool-resolution.md`) — the plugin's one entry
  point, `${CLAUDE_PLUGIN_ROOT}/assets/bin/cq`, replacing the four self-contained scripts each
  front used to ship separately. Invoked as `cq <pilar> <subcomando>…` — `cq knowledge …`,
  `cq specs …`, `cq components …` — one command per front. **Two doors, one file:** `bin/cq`, a
  shim in the directory Claude Code appends to `PATH`, is what lets a body write the name bare; the
  plugin path is what it falls to wherever the PATH does not hold — including work on the quenching
  repository itself, where that entry names the *installed* checkout.
- [**Declared root / resolved root**](standards/architecture/spec-backend.md) — the pair the
  shared layer of `cq specs` must never confuse. The **declared** root is the configuration entry
  (`--root`, `SPECS_ROOT`, the default) — not an address: under an external backend it points at
  nothing, and under `files` with the specs worktree in use it points at the directory the backend
  does not write to. The **resolved** root is where documents actually land, known only to the
  backend that stored them. Shared code deriving a path from the declared one is the single cause
  behind a destination check that could not see the destination, a diagnostic reporting a workspace
  nobody has, and a `root` payload field naming a folder that does not exist.
- [**Dependency map**](standards/automation/dependency-sweep.md) — the table the **Dependency
  sweep** returns, written by the orchestrator into `### Mapa de dependências` under the spec's own
  `## Design` and **dated**: it names every file the proposal's area touches or is touched by, and
  what breaks or goes orphaned if it changes. It lives on the spec — not in the session's context —
  so the banks that follow read it for free instead of re-sweeping, and so the human sees it on the
  issue. The date exists because a spec whose scope changed afterwards is never re-swept, and
  without it the map would age in silence.
- [**Dependency sweep**](standards/automation/dependency-sweep.md) — the read-only sub-agent read
  `/quenching:specs:develop` runs **before** the bank asks, so the right question has something to
  be answered with; it fires on selecting the *shape* bank, and on the first entry into the
  *adversarial* bank for a spec that was born `proposed` and never swept. Each spec is swept **at
  most once**, and never for having crossed a `complexity` level — a spec looks small exactly as
  long as nobody has read its dependencies. It runs under the **widest** tool profile of the
  command's three sub-agents (everything but `Edit`, `Write`, `NotebookEdit` and `Agent`, with
  `Bash`), because the deliverable is the aggregate a `grep`/`gh`/`cq` produces. It returns the
  **Dependency map** and touches nothing.
- [**Derived stage**](standards/workflows/plan-lifecycle.md) — a spec's position in its life
  (`captured` → `proposed` → `designed` → `refined` → `ready` → `approved` → `executing`),
  COMPUTED from which headings are filled and which records frontmatter carries rather than
  declared in a field, so it regresses on its own when a section empties instead of going stale;
  resolution is last-match-wins, which is why `executing` sorts last.
- [**Empty-response honesty**](standards/quality/empty-response-honesty.md) — the obligation to
  separate, in an empty payload coming back from a third-party process, the answer that **never
  arrived** from the one that legitimately **holds nothing**: an exit 2 refusal at the reading choke
  point where a measured structural discriminant exists (for `gh`, zero pages `[]` against one empty
  page `[[]]`), a `warn` finding plus one line on `stderr` where there is only corroborated
  suspicion, and the guard on the caller and never on the shared transport, whose empty response may
  be the correct one (a DELETE 204). It is **Parse honesty**'s sibling one level down: that one
  governs the lossy transform, this one the payload that arrived.
- [**Entry point**](standards/naming/command-surface.md) — one `commands/<path>.md` file, whose
  path IS its identity (`commands/knowledge/add.md` → `/quenching:knowledge:add`); since Claude
  Code merged commands into skills there is no second file to mirror, so there is nothing an entry
  point can drift from.
- **Esqueleto publicado** *(published skeleton)* — the OKF bundle the plugin SHIPS, at
  `plugins/quenching/assets/knowledge/`: index files plus a single leaf standard
  (`standards/agents/communication.md`). It is scaffolding a target fills in, never this
  repository's own library — so it is **not** the same thing as this repo's `/docs/` bundle,
  and the gap between them is what makes a citation resolve here and nowhere else. The prose the
  plugin ships is read against the skeleton, which is why `citation-check.sh`'s half 3 measures
  shipped markdown links against it rather than against this checkout
  (`/docs/standards/quality/citation-verification.md` §Half 3).
- **Fan-out floor** (`plugins/quenching/assets/references/specs-fanout/fanout.md`) —
  `fanoutMinComplexity`, the `.claude/quenching.json` key §The entry contract measures a
  candidate's `priority.complexity` against: below it, a spec joins the defining regime; at or
  above it, the spec must already be `ready`/`approved` to join the building regime. Declared,
  read through `cq specs config --json`, default `medium` — the same line the gears scale draws
  between the one level that interrupts nobody and every level that asks, because a fan-out buys the
  drafting and never the judgment.
- **Gear** — the execution mode of one lifecycle stage in `/quenching:specs:cycle`: in-session, in
  a sub-agent, or skipped, set by the ONE gears plan the command derives from
  `priority.complexity`. By extension, "the `low` gear" names the whole plan a *level* derives, not
  a fourth mode. A level also reaches **inside** a stage, twice: it decides whether
  `/quenching:specs:develop` answers its own questions from evidence (`low`) or asks a human (every
  level above it), and whether that pass **refines** without being asked to (`high`, `xhigh`) or only
  recommends it (`medium`). Under `low` it also has the pass stamp `approved` itself. Governs ONE spec — conducting N of them is the
  [spec queue](standards/workflows/spec-queue.md)'s subject, though both fan-out entries read the
  scale to know which spec is stamped unasked. The contract lives in the plugin's own
  `specs-cycle/gears.md` reference (§The scale) — retired with `automation/orchestration-gears.md`
  (marchas-do-orquestrador-vivem-no-plugin, 2026-08-11)
- [**Generated listing**](standards/architecture/generated-listings.md) — a file, or a marked
  zone inside one, that a command rebuilds from what a directory holds. Always a **second source**
  of a fact the disk already carries, so it earns its keep only where nothing else derives that
  fact **and** a checker can decide its freshness — staleness being its only failure mode, and a
  silent one. The decision criterion is asked before any code: does a command already answer the
  same question on demand? Yes → the listing is duplication and its checker is pure cost; no → the
  listing IS the source and a checker is mandatory. The `/docs/` bundle's `index.md` files are the
  bounding counterexample: nothing else enumerates the bundle, so they keep their checks; the
  retired `/.specs/plans/index.md` duplicated `cq specs list` and went with its four `sp-*` codes.
- [**Handler ladder**](standards/automation/hooks.md) — the ordering a hook's handler is chosen
  from, cheapest first: a deterministic `command` script (zero tokens on no-match), then a `prompt`
  handler (one cheap judgment per firing), then an `agent` handler — which on a per-tool-call event
  is an LLM toll booth on every operation (`sk-hook-llm-frequent`). Climbed only when the rung
  below cannot express the check.
- [**Integration branch**](standards/git/branching.md) — under the develop/main flow, `develop`:
  where every `plan/<id>-<handle>` merges at conclude. It accumulates as many specs as it likes with
  nothing published; it only becomes public once the **Publication branch** takes its deliberate
  merge. See that entry for the other half of the pair — and for the note that this repository
  no longer runs the flow both halves describe.
- [**Language declaration**](standards/agents/communication.md) — the single line on a repo's
  **root** harness file naming one BCP-47 tag (`Language: pt-BR — the contract is …`), which governs
  the **conversation** band alone — answers, questions and reports. Durable artifacts are canonical
  English whatever the tag says, because they outlive the conversation and travel between repos. It carries a value and a citation
  and nothing else: never a paraphrase of the rule it cites, and never a second configuration key.
  Only the root file counts, because only that one is in context at session start — the property the
  form was chosen for. **Silence is not a default of `en`**; a repo that declares nothing is under no
  constraint, and adoption is opt-in per repo. Nothing machine-checks it, so `/quenching:components:harness:align` classing
  the line **KEEP** is the only thing between it and a silent deletion.
- [**Merge record**](standards/workflows/plan-git-record.md) — the
  `merge: {strategy, subject, pr}` frontmatter entry stamped by `/quenching:specs:conclude`, write-once,
  **on the work branch before the merge** — which is what makes the merge that command's last
  action and leaves nothing to be committed to the base after it. The strategy was a human choice
  and the subject names the merge commit it is about to produce; recording both is what tells a
  future reader whether the per-section subjects still resolve from the base. An **anchorless
  strategy** carries an explicit none here. `pr` exists only on the **pull-request route** and
  names the pull request the merge went through — absent on every local conclusion, and refused
  under `fast-forward`, which `gh pr merge` cannot perform (`sp-merge-pr-no-route`).
- [**Moment**](standards/workflows/plan-artifacts.md) — the point on a spec's timeline a canonical
  section is read at, and the axis that replaced an `audience` field nobody read: `decision` (the
  human, weighing whether to build), `build` (the executor, at step 4 of `/quenching:specs:execute`), `close`
  (`/quenching:specs:conclude`, at archive time). One value per section, declared in `schema.json` and in
  `cq specs`'s `DEFAULT_SCHEMA`, and **resolved rather than enumerated** — `cq specs section <id>
  --moment build` returns the six an executor needs, so a command body names the moment instead of
  repeating a heading list that can drift from the schema. `## Discoveries` carries no moment at
  all: captured indiscriminately while building, it is resolved by `/quenching:specs:develop`'s triage sweep
  on its own schedule. The axis replaced a human/agent binary that was **prose nobody applied** —
  measured, that binary cut 14% and named the wrong sections, leaving `## Out of Scope` invisible to
  the one reader it exists to constrain.
- [**Moment**](standards/workflows/plan-artifacts.md) — the point on a spec's timeline a canonical
  section is read at, one value per section: `decision` (the human, weighing whether to build),
  `build` (the executor), `close` (`/quenching:specs:conclude`). Declared in `schema.json` and `DEFAULT_SCHEMA`
  and **resolved rather than enumerated** — `cq specs section <id> --moment build` returns the six
  an executor needs, so a body names the moment instead of a heading list that can drift. Replaced
  an `audience` field nobody read; `## Discoveries` carries no moment at all.
- [**Origin key** (`source_uri`)](standards/quality/bundle-verification.md) — the frontmatter key
  holding the **exact** URI or path of the source unit an imported doc was minted from, written by
  `/quenching:knowledge:import` and by no other command; a doc with no external origin simply does not have it.
  Single-valued, one line, no prose — that is what makes finding the doc that already covers a unit
  an equality test (`grep -rn 'source_uri: <uri>'`) instead of the model recognising prose it wrote
  itself. Distinct from `source:`, which stays prose about who originated a rule. Nothing checks the
  value: truthfulness is decidable only against the source at the instant it was read, and a unit
  collapsed from several seeds carries only one origin — both recorded as **accepted gaps**.
- [**Package**](standards/architecture/plugin-layout.md) — the Python package under
  `plugins/quenching/assets/bin/quenching/`, the directory that replaced the four self-contained
  scripts the plugin used to ship. Split into `common/`, `specs/`, `knowledge/` and `components/`,
  with no file too large to be read whole in one tool call; `cq` is the only entry point that
  exposes it.
- [**Parked follow-up**](standards/workflows/plan-lifecycle.md) — an out-of-scope finding a
  definition pass records as ONE line of `## Discoveries` on the spec it is developing, instead of
  minting a spec for it. Parking is free by construction: `## Discoveries` appears in no stage rule,
  so filling it moves no derived state. Turning one into a file belongs to `/quenching:specs:conclude`'s
  harvest, which runs once the parent's fate is known — and a line another open spec already covers
  never becomes a file at all, resolving as `dismissed: already covered by {id}`.
- [**Parse honesty**](standards/quality/parse-honesty.md) — the obligation that a verifier names
  its own parse failure rather than reporting it as a content gap. The episode that earned it: a
  command `description` truncated at a `#` surfaced as `sk-no-description` — a statement true of the
  string `lint` held and false of the file on disk — so the author either distrusts the checker or
  edits prose that was never wrong. Three consequences bind: the diagnostic ships **with** the lossy
  transform and never after it, it runs **before** the content checks it would otherwise be mistaken
  for, and a tool that cannot prove it implements the rule does not get the rule. Severity is
  **warn**, because a deliberate comment and lost prose are byte-identical — the tool states a
  suspicion it cannot resolve. Delivered by an **anomaly sidecar**.
- [**Payload**](standards/architecture/plugin-layout.md) — everything the plugin carries for use
  **inside a target repo**, as opposed to a fact about this repo. Two disjoint halves: the
  *installed* payload an align copies whole or per insert (`assets/docs/` `assets/specs/`
  `assets/claude/` `assets/templates/`), and the *read* payload a command loads at runtime by
  `${CLAUDE_PLUGIN_ROOT}` and never installs (`assets/references/`). Both are payload because
  neither is graded against this repo — which is what decides reference over standard
  (§A contract a command reads at runtime is a reference, not a standard). Not to be confused with
  the **JSON payload** a `cq` verb emits, the unrelated sense used of tool output.
- [**Priced**](standards/quality/finding-remedy-applicability.md) — the boolean field
  `sk-unscoped-bash` carries in the JSON: the command body opens a line with the literal marker
  `**Why \`Bash\` is unrestricted here.**`, outside a fence, or it does not. It states **presence**,
  never quality — nothing reads the reason, judges whether it is a good one or measures its length,
  because a predicate that did would be inventing a verdict about prose that only matched a pattern.
  The finding is reported in both cases: the grant is still the turn's whole shell, and what the
  marker buys is a reader able to tell a deliberate grant from one nobody examined. It exists
  because the earlier remedy advised declaring the reason in the body while the check read only
  `allowed-tools` — the conclusion it did not observe (§The second site).
- [**Provider ID**](standards/architecture/spec-backend.md) — the tracker's own identifier for
  a spec — a GitHub issue number, an Azure Boards work-item ID — and **the spec's whole identity**.
  The canonical document does not mirror it, and resolution is exact: the ID exists or it is
  `sp-unknown-id`, with no title match and no approximate rung. That exactness is what retired
  `sp-ambiguous-slug` by construction, since two specs cannot share one. Measured at the moment it
  replaced the slug: a direct read costs 0.39 s / 7.7 KB against 3.81 s to find the same document
  by sweeping the tracker.
- [**Publication branch**](standards/git/branching.md) — under the develop/main flow, `main`:
  the one branch that takes the deliberate `develop → main` merge, the one moment the version
  lockstep moves and a tag is created. It never accumulates specs in integration — that is the
  **integration branch** (`develop`), which `plan/<id>-<handle>` is cut from and merges back into.
  The trigger to publish is the maintainer's demand, never a cadence, and the route is always a
  local merge. *Both halves of this pair describe a flow this repository retired: `branching.md`
  §The single branch now declares `main` alone, and every PR merges into it.*
- [**Phantom command**](standards/architecture/plugin-layout.md) — a non-entry-point file left
  under `commands/`, which registers as a real `/` entry that does nothing; it does not error, so
  the only thing that catches it is `sk-no-description`, and it is why shared procedure lives under
  `assets/`.
- [**Phase gate**](standards/workflows/plan-artifacts.md) — the set of sections a spec must have
  filled before a heading counts as required, which is what makes the explicit-none rule
  stage-scoped rather than absolute. Two gates move a file (`new` into `plans/`, `promote` into
  `archive/`) and refuse with exit 2 and the missing list rather than warning; the `ready` gate is
  a derived stage that refuses nothing. All of them live once in `schema.json`, read by both
  `promote` and `validate`.
- [**`[P]` marker**](standards/workflows/task-execution.md) — the opt-in flag set on a task when
  the tasks are written, declaring it may run concurrently with its group; honoured only when
  `cq specs parallel` proves the group's `files:` sets disjoint, and never inferred while building.
- [**Pillar**](standards/naming/command-surface.md) — one of the three axes `cq` routes:
  `specs`, `knowledge` and `components`, passed as the first argument (`cq <pilar>
  <subcomando>…`). It is the single vocabulary of the fronts' axis, replacing the names `docs` /
  `specs` / `skill` that competed before the merge into one package.
- [**Plugin config**](standards/workflows/plugin-configuration.md) — `.claude/quenching.json`, the
  single file a target repository uses to declare anything to this plugin: `backend`, `specsBranch`,
  `worktreeSetup`, `azureStates`, `azurePlacement`,
  `azureColumns`, `subjects`, `tagCatalog` and `workItemTypes`. It replaced `/.specs/config.json`,
  whose home stopped working once a repository could have no `/.specs/` folder at all. Absence
  yields the documented defaults, never a null and never a refusal — except `azureStates` and
  `azurePlacement.areaPath`, neither of which has a default because the project itself defines
  them, and whose absence refuses instead of guessing; every other way it can be wrong comes back
  as a field for `doctor` to judge.
- [**PR record**](standards/workflows/plan-git-record.md) — the `pr: {number, url, date}`
  frontmatter entry stamped by `/quenching:specs:conclude` the moment `gh pr create` returns, on the
  PR route only, and **write-many** where the other git records are write-once: a PR may be closed
  and reopened, or force-pushed to a fresh number, and each is a new fact rather than a
  falsification of the old one. It is not `merge.pr`, which is stamped only once the merge is
  about to happen — under `/quenching:specs:cycle`'s **minimal gear** the PR route deliberately
  stops at the open PR and leaves the merge to human review, so `merge` never lands and this is the
  spec's only record of the pull request. On backend `github` it is also what makes the branch
  visible on the issue: the PR body's `Refs #<issue>` line populates the Development panel at no
  extra call, which a branch alone cannot do (`createLinkedBranch` only ever creates a NEW branch).
- [**Probe**](standards/architecture/align-surface.md) — the opening run of a front's own
  verifier (`cq knowledge validate`, `cq specs doctor`, `cq components doctor`) whose exit code
  decides whether an align inventories anything at all, making a no-op align cost a couple of tool
  calls; the same programs run again as the closing verification.
- [**Projection / storage**](standards/architecture/spec-backend.md) — the pair that decides
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
- [**Prose fan-out**](standards/quality/computed-fact-prose-fanout.md) — the set of prose sites
  a fact a tool computes ages the moment it changes — a schema key, a surface's command count — and
  which every checker in this repo is blind to by construction: the selftest proves the key *works*, `cq specs validate` reads records rather
  than descriptions of them, and resource activity only speaks where a doc's `resource:` happens to name
  the schema file, which is now a figure rather than a check. Measured twice on one branch: **one field added → four sites stale** across four homes, and **one
  command retired → ten sites stale** across four files, with every checker green in both. Found by
  grepping the record's **spelled-out** form (`merge: {strategy`), never its name, and fixed in the
  task that adds the key. Historical mentions are correct as written, which is why this stays a
  human sweep rather than a check — the same mention/use judgment
  [prose-sweeps.md](standards/quality/prose-sweeps.md) already establishes is invisible to a
  regex, reached from the opposite direction: that one is the sweep you ran, this one the sweep you
  never ran.
- [**Promote**](standards/workflows/plan-lifecycle.md) — the gated `git mv` that moves a spec
  from `plans/` to `archive/` without renaming it, stamping `outcome: done | abandoned`. Under v3
  it is the ONE hop a spec ever makes: the `backlog/` → `ready/` promote is retired, and the human
  OK it used to carry is the **Approved record** instead. Promoting as `done` refuses
  while `- [ ]` boxes remain unless forced; `abandoned` is always allowed.
- **Recursive return** (`plugins/quenching/assets/references/specs-fanout/fanout.md`) — a fan-out
  run absorbing the specs it promoted out of `## Discoveries`, in one of three forms: no recursion,
  one generation, or an unbounded fixpoint. All three are always presented in the authorization
  plan, with the chosen one and the human's stopping criterion. What bounds the third is the entry
  contract, not a counter: a promoted spec at or above the fan-out floor (`fanoutMinComplexity`,
  default `medium`) needs `ready`/`approved`, and therefore never enters a return on its own.
- **Refine** (`plugins/quenching/assets/references/specs-develop/questions.md`) — the
  non-monotonic half of a `/quenching:specs:develop` pass, and the only operation licensed to
  overturn what the spec already says, the `## Proposal` included. Runs **after** **Compose**, over
  a whole spec, which is what makes *is this worth building?* answerable
  rather than rhetorical. `high` and `xhigh` run it on their own authority; `medium` only recommends
  it at the close; `low` never refines, and asking for one raises the level first. It replaced the
  `adversarial` bank, which sat before the gate and was unreachable in practice.
- [**Refinement record**](standards/workflows/plan-artifacts.md) — the `refined: {mode, date}`
  entry a spec's **frontmatter** gains once it has been interrogated, whose absence raises the
  non-gating `sp-unrefined` warning.
- [**Remedy**](standards/quality/finding-remedy-applicability.md) — the `remedy` field every
  verifier finding carries, and the contract it takes on: naming an action the surface that emitted
  the finding actually offers. A remedy that describes the desired state, or an action the same CLI
  refuses, spends the trust of the whole output — not just that of the item carrying it.
- [**Reserved tag prefix**](standards/architecture/spec-backend.md) — `spec:`, the half of a
  tracker's native tag surface (`github` issue labels, `azure-boards` `System.Tags`) that belongs
  to the TOOL rather than to the document, and the rule that lets **storage** and **rendering**
  share one field without either reading the other's writes as the spec's own content. A write
  hands the surface the union — the spec's declared `tags` plus the freshly derived `spec:` set —
  and `declared_tags` filters the reserved names back out on every read, alongside the second
  reserved name, `azurePlacement.discoveryTag`. A spec may not declare a tag under the prefix, for
  the same reason it may not declare the discovery tag: the next write recomputes it anyway. It is
  also what keeps `tagCatalog` honest — a catalogue that never lists a reserved name is complete,
  not lacking.
- [**Resource glob set**](standards/quality/bundle-verification.md) — the format of an OKF
  doc's `resource:`, a plugin convention rather than an OKF rule: a **comma-separated** list of
  repo-root-relative paths and globs using `*`/`**` **only**, matched **segment-wise everywhere**
  including the `:(glob)` pathspec handed to `git log`, since plain `fnmatch` and git's default
  wildmatch both let `*` cross a `/` and would silently widen every shallow scope. Anything else
  (braces, character classes, `?`) is classified `unknown` and never reported as a violation. It
  says what the doc *governs* — which is why it replaced the `file:line` anchor doctrine once
  named, and why it is also the input the resource-activity figure needs.
- [**Retired (reserved artifact)**](standards/architecture/retiring-a-reserved-artifact.md) — a
  reserved filename nothing produces or checks any more, but which **keeps** its slot in the
  validator's `RESERVED` set and its skip in the `PreToolUse` hard block. Deliberately not
  **unreserved**: dropping the reservation too would send every surviving instance down the
  concept-doc path, turning it into a `no-frontmatter`/`missing-type` ERROR in target repos that
  changed nothing. `/docs/log.md` is the first artifact retired this way.
- [**Retiring a standard**](standards/workflows/retiring-a-standard.md) — removing a bundle
  standard rather than deprecating it — `git rm` is the verb, the inheriting doc carries the
  `retired with <doc> (<spec>, <data>)` stamp, the citation sweep is human with the branch review
  as its net, and the GENERATED listing row goes in the same commit; distinct from the reserved
  artifact, which KEEPS its slot when retired.
- [**Routed command**](standards/automation/skills.md) — a command something reaches **without a
  human typing its name**, whether by a spoken trigger or by another command's body naming it; its
  `description` stays resident in every session's context and is charged against the
  **Always-on ceiling**. The half of the test that is mechanical is not a judgement call:
  `cq components lint` derives the name-reachable set from the command bodies, so classify against the
  instrument. The complement is a **Typed-only command**, and the criterion is a floor rather than a
  quota — on a small surface it may admit nobody.
- [**Rules/rationale markers**](standards/automation/context-discipline.md) — the pair of HTML
  comments, `<!-- rules -->` and `<!-- rationale -->`, that split a normative section's binding half
  from the measurement and history behind it, so `cq components read --rules-only` can return the first
  without the second. **A marker, never a heuristic**: a model deciding per read which sentences
  bind is non-deterministic and fails *silently*. Compaction here is **relocation, never deletion**
  — the rationale stays on disk and stays contract, only its position moves. A missing marker
  degrades to the whole section and **says so**, never to emptiness. A marker's reach ends at the
  next heading, so a section with sub-sections is marked **per sub-section**.
- [**Scope ladder**](standards/automation/hooks.md) — the four rungs a hook may be installed at,
  narrowest first: a command's own frontmatter `hooks:` block (fires only while that command runs),
  a `settings.json` hook with an event + `matcher`, a gated wide event, and an unmatched
  session-wide hook — the top rung, and a finding (`sk-hook-unmatched`) unless the reason nothing
  narrower suffices is stated where it is wired. `cq components` holds rung 1 and rung 2 to the same
  checks from one implementation.
- [**Section boundary**](standards/automation/context-discipline.md) — the moment a `## N.`
  section's last task commits with none of its tasks blocked: the section's own per-task commits
  squash into one (execution.md §The section squash) before a build **offers** to stop — a clean
  point, because the resumption trail (`##
  Handoff`, `git log`, the recorded commit subjects) is already maintained for other reasons, which
  is what makes the cut nearly free. The trigger is **that event, never a window size** — a
  threshold invented before it is measured fixes the answer. It offers and never imposes, never
  ends a run itself, and writes no new state.
- [**Section reader**](standards/automation/context-discipline.md) — the verb that resolves the
  `§X` address the prose was already writing: `cq components read <path> --sections "§A"` over free
  markdown, `cq specs section <id> "A,B"` over a spec's fourteen canonical headings. Both take a
  **list**, because turns are the other factor of the **Context integral** and N sections fetched
  over N turns can lose to reading the whole file. A section runs to the next heading of the same
  level or shallower, a fenced block is never read as a heading, and a name that resolves to
  nothing is a **refusal that names it**, never an empty answer. Both prove the rule against the
  same **Canonical set**, `SECTION_CASES` — which pins the *sectioning* rule the two answer
  identically, and therefore not the ladder below, a CLI-argument rule only the first has.
  `cq specs section --write` is plural on the same terms, and its delimiter is the reader's **own
  output**: bodies arrive on stdin under the `## <Heading>` lines the plural read prints, so the
  pair round-trips and no second grammar was invented to say where one body ends. A write side that
  goes plural inherits the read side's format rather than inventing a separator; the headings named
  on the command line stay required as the guard, and a set that disagrees with the stream refuses
  before writing any of them.
  **They take that list differently, deliberately.** `cq components` resolves each value whole before
  reading it as a list, so a heading carrying its own comma — `## What crosses, what stays` — is
  cited by its full title; `cq specs` splits unconditionally, which is unreachable there because
  the fourteen canonical headings carry no comma and it refuses any name outside them.
- [**Section squash**](standards/workflows/task-execution.md) — the local `git reset --soft`
  plus recommit that collapses a `## N.` section's own per-task commits into one, at that
  section's own **Section boundary**, provided none of its tasks is `[!]`. Its target is a **sha
  captured when the section opened** — derived from the first task's own anchor on a run that
  resumed mid-section, and never a branch name, whose tip can move under the run — and
  `git merge-base --is-ancestor` runs before the reset, refusing any target not ancestral to
  `HEAD`. The per-task chain that
  verifies, ticks and commits stays exactly what it always was — this is what buys resumability
  *while the section runs*; the squash only ever reaches back into commits its own section just
  made, never a prior section's or anything already shared, which is the narrow, explicit exception
  to "never rewrite an earlier commit." Every task the section held is re-stamped onto the
  surviving commit's subject (or sha) in the same step — the **Commit record**'s granularity
  narrows to the section, never loses resolvability. Distinct from the squash-**merge** strategy
  `/quenching:specs:conclude` offers, which is a different mechanism at a different moment.
- [**Report mold**](standards/architecture/report-mold.md) — the single section that owns the shape
  **every** command of a front prints its report in, cited by each body, which declares only its own
  delta. Three fixed bands (header · body · next step), blocks declared fixed or optional, an
  ordered set of columns each command takes a subset of, and a next-step block executable as
  printed. It is **literal** — it carries the rendered block, not a description of one. It lives
  inside a file the bodies already load, so it costs no extra tool call; the cost in characters is
  measured and declared, never estimated. Distinct from **Shared mold**, which governs frontmatter
  keys and not output.
- [**Self-matching guard**](standards/quality/self-matching-guards.md) — a structural checker
  whose own finding text names the construct it forbids, so a substring scan reports the checker as
  the violation. Measured here on the first run of `announcement_failures()`, which flagged
  `selftest` for the call quoted in its own remedy string. The fix is **parsing** the construct
  (`ast`, a real tokenizer) so prose about a call is invisible by construction — never excluding
  the checker, and never splitting the string to hide it.
- [**Shared mold**](standards/architecture/shared-mold-keys.md) — a frontmatter key block owned
  once and cited by several commands, so each mints a doc from the same stamp instead of restating
  it (`docs-add/homes.md` §The frontmatter stamp, cited by four). Because a mold is a *fill-in
  invitation*, a key only one writer may legitimately set stays **out** of it and lives with that
  writer's own contract — an annotation inside the mold is not equivalent, as the `resource:`
  precedent showed. The test is not "may this be absent?" but "may this citer write it at all?".
- [**Spec backend**](standards/architecture/spec-backend.md) — where a repository's specs
  actually live: markdown files on a dedicated branch, GitHub issues, or Azure Boards work items,
  declared by `backend` in [the plugin config](standards/workflows/plugin-configuration.md).
  Every backend implements **five primitives over the canonical document** — never one method per
  CLI verb — so the fourteen sections, the frontmatter records and the derived stages are shared
  code and cannot diverge between targets. The selected backend is the sole source of truth: there
  is no shadow local store, and a declared-but-unimplemented backend refuses rather than falling
  back to `files`.
- [**Spec queue**](standards/workflows/spec-queue.md) — building N specs **serially** over a
  single isolation — one branch, one pull request, no chaining — rather than concurrently, because
  the specs' declared files collide at a density the doc measures. Serializing buys a second
  property outright: spec N's gate runs over the result of 1..N−1. Its counterpart, defining N
  specs, fans out for real and is a **batch**, never a queue — nothing it runs takes a branch.
- [**Typed-only command**](standards/automation/skills.md) — a command carrying
  `disable-model-invocation: true`, reached only by a human typing it; its `description` leaves
  every session's context. Residency and content are
  independent axes, so the description **keeps all three parts at full length** — the human picking
  it out of the `/` menu is now its only reader, and has no routing to fall back on. Measured, not
  assumed: the field also makes the command unreachable **by name** through the Skill tool, so
  putting it on a stage another body invokes leaves that stage silently inert (`sk-inert-stage`,
  error). The complement is a **Routed command**.
- [**Verification policy**](standards/workflows/task-execution.md) — the per-spec declaration
  (`per-task`, `per-section`, `end-of-plan`) written at creation that decides when a task's
  `verify:` command runs, so execution never guesses and never asks mid-task.
- [**Version lockstep**](standards/ci-cd/versioning-release.md) — the four version strings a
  release must bump together, split into two halves read by two independent consumers: the
  `plugin.json` `version` + `VERSION` pair Claude Code compares to decide an upgrade fires, and the
  one shared `VERSION` constant every pillar's `--version` reads. Since nothing installs a tool any
  more, **no automated check asserts the four agree** — the whole lockstep is discipline, read back
  by hand at conclude. Distinct from the **Canonical case list**, which is the lockstep unit for the
  parser's *behaviour* rather than a version string.
- [**Worktree setup**](standards/workflows/worktree-setup.md) — the single key `worktreeSetup`
  in `.claude/quenching.json`, holding a command `/quenching:specs:execute` runs once inside a newly created
  worktree so a repo with installed dependencies gets a usable tree rather than one that breaks at
  the first `verify:`. `cq specs` reads it and never executes it. Declaring nothing is the normal
  case and never a finding; the two that are — `sp-config-unknown-key` and `sp-config-unparseable`
  — exist only so a mistyped key cannot fail silently. Its consent is the isolation offer itself:
  the command is shown verbatim in the plan block, and choosing Worktree is the OK for it.
- [**Withdrawn contract residue**](standards/quality/withdrawn-contract-residue.md) — the prose
  still asserting a contract a change **removed**, and the sibling of **Prose fan-out**
  ([computed-fact-prose-fanout.md](standards/quality/computed-fact-prose-fanout.md)) for the case
  where nothing computes the fact: with no value to spell out, each site wrote the rule in its own
  words, so no grep finds the set. The mitigation is upstream — a spec's `## Impact` names the
  **class** of documents asserting the contract and derives the file list mechanically, because
  enumerating instances under-counts a class that quietly gained a member. Measured five times on
  one branch withdrawing the installed-tool contract: three caught in execution, two only at the
  branch review, and one of those in a file `## Impact` **had** named and half-covered — which is
  why naming the file is not enough, and the reviewer's question is *what did this make false?*
  rather than *which files changed?*
- [**Zensical**](external/tools/zensical-measured-behaviour.md) — the static site generator the
  Material for MkDocs team now ships, and the one this plugin's `documentation/` site layer stamps
  and verifies since spec 1003: it reads a `mkdocs.yml` natively but runs **no MkDocs plugin at
  all**, so the nav moved from `.pages` sidecars into an explicit `nav` list in `zensical.toml`.

## How to enrich

Add a term whenever a repo-specific word, acronym, or piece of jargon surfaces that a
newcomer would not know. Three ways in:

- **Automatically, as a tail of a capture.** The `quenching` knowledge skills
  (`quenching:knowledge:learn`, `quenching:knowledge:add`, `quenching:knowledge:import-memory`) each check, at
  the end of a capture, whether the new concept introduced a term that belongs here, and
  add or update the entry — linking it to the concept doc just written.
- **On demand, one term at a time.** Run `quenching:knowledge:define` to add or refine a single
  entry (inserted in alphabetical position, MERGE — never clobbering a filled definition).
- **In bulk, across the whole bundle.** Run `quenching:knowledge:glossary-backfill` to sweep every doc
  already in `/docs/` for repo-specific terms that were never fed into the glossary and
  backfill them in one pass.

Keep entries honest: define the term as **this repo** uses it, not the dictionary sense,
and let the linked doc carry the depth.
