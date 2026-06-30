# Dimension 2 — normative reference & `docs/` structure

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **the current layer and the `docs/` baseline (taxonomy → label → consumption → cross-repo installation)**.

## Current state

> Current summary of each boundary in this dimension (what is in effect today). Detail and rationale are in the history below.

- **R24 · PARALLEL builder/updater of the `standards/` layer (fan-out by topic + deterministic index)**
  — dim 2 stops only loading the **empty skeleton** of `standards/` (`assets/docs/standards/*/README.md`)
  + the single-doc authoring skill (`quenching-docs`) and gains the tool that **actively builds/updates
  the entire layer** from the repo + references, in **parallel**. Two new payloads: **(1) worker**
  `assets/agents/quenching-writer.md` — `sonnet` sub-agent, one per topic (of the 9 canonical ones), own
  context, runs in parallel; **mines the repo** (Read/Grep/Glob) for the de-facto = **`current` anchored at
  `file:line`**, **researches external references** (WebSearch/WebFetch), writes/updates
  `docs/standards/<topic>/<standard>.md` (BUILD/UPDATE/Drifted) following the `quenching-docs` discipline,
  and returns **only the condensed summary** (R9). **(2) orchestrator** `assets/skills/quenching-standards/SKILL.md`
  — entry point that **derives the topics that apply** (completeness of what fits), does a **fan-out of one
  worker per topic IN PARALLEL** (one message, multiple invocations; concerns that cross-reference each other
  stay sequential in the orchestrator), collects the summaries, exposes gaps as PROPOSED items, and **regenerates
  `INDEX.md` DETERMINISTICALLY from disk** (scans `standards/**/*.md`, reads `title:`/`updated:`/`status:`,
  reconstructs the list between `<!-- BEGIN/END GENERATED -->` preserving the authored preamble). **Two
  INVARIANTS:** anti-fabrication (a best-practice the repo does NOT implement becomes a **PROPOSAL/GAP**
  `authority: background`, never `current` — avoids capability/outcome hallucination) and **rebuild test**
  (Augment Code "rebuild test": a complete doc carries both **requirement** [what] **AND** **decision**
  [why + alternatives]; requirement-only regenerates different behavior each time). **Anti-bloat boundary:**
  `quenching-docs` = ONE doc; `quenching-standards` = ORCHESTRATES the entire layer in parallel + index —
  COMPOSES, does not duplicate. **Index = DERIVED artifact** (rule «X defines Y»; structural drift impossible
  by construction). This is a **facet of dim 2** (new payload, not a new dimension) — **15 dimensions
  maintained**. Materializes two backlog candidates (deterministic index + completeness/rebuild test) and
  **resolves the review item** "rebuild test source attributed incorrectly" (correct attribution = Augment
  Code, cited). New smells (2b/dim 2): `current` standard WITHOUT `file:line` anchor · index edited by hand
  diverging from disk · `standards/` layer with only an empty skeleton. (round 24)

- **R22 · Home for DIRECTED COMMUNICATION in the `docs/` taxonomy (`communications/`) + generic skill by channel**
  — the canonical `docs/` taxonomy gains a **9th home**, `communications/`, for **directed/outbound
  communication** (incident/change/deploy/downtime/migration/announcement to an audience):
  `templates/` (one template **per channel** — `email`/`chat`/`wiki`/`markdown`, capturing the real difference
  of each channel: subject line in email, edit-the-original-message in chat, properties table in wiki) +
  `archive/` (issued communications, dated). It is **a new home** (does not extend `presentations/`:
  a communication is **text read directly**, not a binary via sidecar; nor `guides/`/`decisions/`/`standards/`)
  and sits **outside the four Diátaxis types** (its own text form — a message to an audience), like
  `presentations/`. `audience: human`/`authority: background` (a record, never a contract; whatever becomes
  a rule **distills into `standards/`**). The package carries the **STRUCTURE** (home + per-channel templates
  with `<...>` placeholders + skill); the **CONTENT** (real scopes/audiences/statuses, each communication)
  belongs to the repo — same structure-not-content installer boundary as Rev4 (`guides/`). Generic skill
  payload `assets/skills/quenching-announcement/` that, given a channel+subject, **reads the template for the
  requested channel and fills it in** (one generic skill that reads templates, **not** one per subject). This
  is a **facet of dim 2** (new canonical home), with a cross-note in dim 6 (new skill) — **15 dimensions
  maintained**. The pre-existing `docs-announcement` skill in the repo is **DEPRECATABLE** (the generic payload
  becomes the single source). New smells (2b, **greps PENDING measurement vs. fixtures** — no Bash):
  communication outside its home · channel without a template · communication without a scannable header ·
  communication marked current · communication skill coupled to one repo. (round 22)

- **Rev4 · `guides/` = home for guides + HOW to organize; onboarding is NOT prescribed (refines Rev3)** — two
  adjustments to Rev3: (1) the skill **stops prescribing** any onboarding guide — it does not bundle an
  `onboarding.md` nor reserve a home; the REPO decides whether it wants the guide (onboarding stays as an
  **illustrative example** in the spec, never a fixed artifact); (2) `guides/` now declares **how to store**
  the guides — **preferably in a folder/subfolder structure by topic/area (subject-first), defined by
  the repo**. **Reconciliation with Rev3:** Rev3 pruned the `onboarding/` SUBFOLDER because it was a
  **prescribed** **audience** silo — that does **not** prohibit subfolders in general; subfolders by
  **topic** created by the repo are **encouraged**. The distinction is made explicit (folder organization: yes;
  reserving a folder by audience: no). Propagated to `references/docs-taxonomy.md` (tree + `guides/` section),
  `assets/docs/guides/README.md` (section "How to organize"), and `assets/README.md` (inventory: `guides/`
  is README only). **Orphan to remove:** `assets/docs/guides/onboarding.md` (created by Rev3, now reverted).
  (revision Rev4)

- **Rev3 · `onboarding` is a guide, not a silo (prunes `guides/onboarding/`)** — `revised-by: Rev4`
  (the part "becomes the file `onboarding.md`" was **reverted** — the skill does not prescribe the guide;
  see Rev4 above). The thesis that **remains** from Rev3: the only subfolder in the canonical tree that was
  organized by **audience** (not by topic) was eliminated — there is no `guides/onboarding/` silo. Original
  reason: user pointer + contradiction with the rule "home = topic" (subject-first) + bloat. (revision Rev3,
  refined by Rev4)

- **Rev1 · CANONICAL taxonomy of `docs/` (PRESCRIPTIVE thesis — supersedes R16)** — the
  current thesis on the docs topic **was inverted**: the skill defines a **canonical `docs/` taxonomy with
  fixed names** (`standards/` · `decisions/` · `vision/` · `backlog/` · `guides/` · `reference/` ·
  `catalog/` · `presentations/`, with subfolders by topic), and **the repo converges to the skill** — not
  the skill to the repo. Where R16 said "the repo's convention wins; recognizable by function, not by name;
  record the mapping, do NOT rename", the rule now is: **every repo CONVERGES to the SAME tree with identical
  names**; a variant name (`arquitetura/`/`adr/`/single `VISION.md`/`patterns/`) is a
  **non-convergence smell**, a candidate for **migration** to the canonical. Portability is **stronger**
  (a human/agent moving between repos sees the tree literally identical). **Safety is preserved**: the
  skill **PROPOSES the migration** and flags the variant as **DEPRECATABLE**, **never renames/deletes without
  approval** (Step 5 confirmation + deprecation doctrine maintained). The canonical tree specification lives
  in its own file — **[../references/docs-taxonomy.md](../../plugins/claude-quenching/skills/quenching-management/references/docs-taxonomy.md)**
  (purpose/Diátaxis/`audience`/`authority`/boundaries per home + migration doctrine); dim 2 was made
  **lean** (short directive + link, Simplicity First — previously bloated by R13-R16). Dim 3 (direction
  becomes a segmented `vision/` folder) and dim 5 (`decisions/` canonical, formerly `adr/`) adjusted; Step 0
  and detection block 2b derive against canonical names and detect variants as migration candidates;
  `installation.md` became "converge-to-canonical". Language: folder names in **English kebab-case**,
  index **`INDEX.md`**. **Canonical scaffold MATERIALIZED in `assets/docs/` by Rev2** (the full tree of
  README per home/subfolder, with `audience`/`authority` frontmatter, now mirrors `docs-taxonomy.md`;
  see Rev2 below). 15 dimensions maintained. (revision Rev1)

- **Rev2 · Materialization of the canonical scaffold in `assets/docs/`** — the taxonomy that Rev1 fixed as
  **prose/definition** (`references/docs-taxonomy.md`) was turned into a **real installable scaffold**: each
  home and subfolder in the canonical tree received its own `README.md`, aimed at the **reader of the final
  repo** (copy-pasteable almost verbatim), with minimal `audience`/`authority` frontmatter labeling the home
  and the visible list of subfolders inside it. The tree created: `standards/` (README + `INDEX.md` +
  9 subtopics `architecture/code/naming/data-modeling/ci-cd/workflows/mlops/quality/platform`),
  `decisions/`, `vision/` (README + `_area.md` shell for area segmentation), `backlog/` (updated
  to canonical name), `guides/` (README only — **Rev3 pruned the `onboarding/` silo**; **Rev4 un-prescribed
  `onboarding.md` and established "the repo organizes, preferably in subfolders by topic"**, see below),
  `reference/{tools,libraries,regulations}/`, `catalog/`,
  `presentations/{slides,diagrams,reports}/`; top-level `README.md` trimmed to a slim manifest (table
  home→purpose→link, points to `references/docs-taxonomy.md` as spec). `_sidecar.md` pointed to
  `presentations/`+`reference/regulations/` and distillation corrected to `standards/`. `assets/README.md`
  (inventory) rewritten for the new tree. The legacy skeletons (`arquitetura/INDICE.md`, `adr/README.md`,
  `VISION.md`) became **orphans to remove** by the orchestrator. `references/` and `SKILL.md` untouched.
  (revision Rev2)

- **R13 · Standard segmentation taxonomy for `docs/` (portable baseline across repos)** — dimension 2
  stops **deriving the `docs/` structure ad-hoc per repo** and gains a **portable baseline taxonomy**:
  new skeleton-payload [assets/docs/README.md](../../plugins/claude-quenching/skills/quenching-management/assets/docs/README.md) that provides **named and
  stable homes** for the technical layers already audited (`arquitetura/`=dim 2 ·
  `adr/`=dim 5 · `VISION`=dim 3 · `backlog/`=dim 4 · `catalogo_dados/`/`dominio/`=dim 11) **plus a named
  slot for human-nature material** (`apresentacoes/`/`diagramas/`/`normativos/`:
  slides, source diagrams, regulatory PDFs) — material that belongs in `docs/` but **not** in the
  normative layer. Gain: **humans and LLMs** find each thing in the same place **in any repo**
  where the method was applied (derive-before-scanning), instead of a form re-invented per repo;
  the **repo's convention wins** when it exists (Step 1 adapts names), and the baseline becomes a
  **completeness reference** (*does the repo cover the sections that apply to it?*, not a blind checklist).
  The "What good looks like" for dim 2 incorporates the taxonomy + the **README (humans) × CLAUDE.md/AGENTS.md
  (agents)** separation as the same boundary (dim 12) at the top of the repo. New smells: **`docs/` without
  baseline segmentation** (technical markdown loose at the root, the agent scans everything) and **human
  material leaking into the technical layer** (slides/diagrams/PDFs in `arquitetura/` or at the root, without
  a slot, polluting the current reference). New cross-cutting block **2b** in `detection-and-smells.md`
  (greps that only list candidates: missing baseline sections via Step 0 · loose technical markdown at the
  `docs/` root · human binary outside its slot) + the read "named homes or loose markdown?".
  **Surgical scope:** the human slot is **only named** — *how* the LLM consumes that material without
  ingesting binary noise (sidecar/extract, provenance frontmatter, audience segmentation) is the next
  method facet, not this round. Core (the baseline and the docs boundary stay in the method; authoring/editing
  each doc comes from `quenching-docs`). (round 13)

- **R14 · Segmentation of `docs/` by audience (human × LLM) with provenance frontmatter** — dimension 2
  stops having **only** the taxonomy/homes from R13 (*where* each thing lives) and gains the **per-file/
  per-folder label** (*for whom* and *from where*): new payload [assets/frontmatter/docs-front.md](../../plugins/claude-quenching/skills/quenching-management/assets/frontmatter/docs-front.md)
  gives each doc — or each homogeneous folder, via its `README`/index — a minimal **audience**
  frontmatter header (`audience: both` human+LLM · `agent` LLM-first/normative · `human` human-only/background)
  and **authority + provenance** (`authority: current` source-of-truth/contract × `background` background/
  history; `source`/`maintainer`/`updated`). Practical gain: the **agent** knows what to **consume as truth**
  (agent/current) × what is **human background** (human/background — do not ingest/cite as contract),
  and the **human** knows what to **edit freely** (background) × what is a **contract** (current, edited only
  by the owning skill). This is the README-humans × CLAUDE.md/AGENTS.md separation (dim 12) applied at the
  **file level**; the human slot from R13 starts as `audience: human`/`authority: background` (the LLM reads
  only the sidecar, not the binary). `updated` becomes the provenance anchor (old date vs. the described
  standard = fossil candidate, crosses with dim 1/context rot). New smells: **doc without declared audience/
  authority** (the agent cannot tell whether it is truth-to-consume or human-background-only; the human cannot
  tell whether it is editable or a contract) and **human material marked as current** (slide/PDF/draft without
  `authority: background` that the agent cites as a contract). Block **2b** gains a grep that **only lists
  candidates** (`.md` doc in `docs/` without `audience`/`authority` in the frontmatter — not a smell if the
  **folder** already labels via README/index) + the read "consume as truth × human background".
  **Surgical scope:** only the **label** — *how* to populate the human slot without ingesting binary noise
  (sidecar/text extract) is the next facet, **not** this round. Core (the label and the docs boundary stay
  in the method; authoring/editing each doc comes from `quenching-docs`). (round 14)

- **R15 · Human-nature material without ingesting binary noise (sidecar/extract)** — dimension 2
  stops **only naming** the human slot (R13) and **labeling** it (R14) and gains **how the LLM consumes
  it without ingesting the binary**: new payload [assets/docs/_sidecar.md](../../plugins/claude-quenching/skills/quenching-management/assets/docs/_sidecar.md) — a
  **`.md` extract alongside the binary** (slide/PDF/diagram) that carries the **smallest high-signal set**
  (navigable summary + key points + `binary:` pointer to the source by path/URL), inherits the provenance
  from R14 (starts as `audience: agent`/`authority: background`), and the agent **references** the source
  without **opening** it. Official dated rationale: the PDF is processed by **vision** (each page becomes an
  image; ~1,500–3,000 tokens of text **+** image cost per page; the full-vision mode reaches ~7,000 tokens for
  3 pages vs. ~1,000 text-only = ~7x) — so the binary is many tokens of **low signal**, and the text extract
  is the "smallest set of high-signal tokens" + **structured note-taking** (external text re-read on demand,
  not the binary in the window). **Extract vs. index-only rule:** *extract* (1 sidecar per file) material
  whose **content governs a technical decision** (a regulation that underpins a rule, a slide that defines a
  domain concept, a diagram of the flow the code follows); *index only* (1 `README`/manifest of the **folder** —
  name + 1 line + path) material that is purely a human reference file — **do not extract for extraction's
  sake** (an orphan sidecar no one consults is also context rot). Dim 2 ("What good looks like"/Detection/
  Smells/Remediation/Payload) and the baseline
  [assets/docs/README.md](../../plugins/claude-quenching/skills/quenching-management/assets/docs/README.md) (resolves the "how" that R13 deferred) are sharpened; block
  **2b** gains greps that **only list candidates** (binary in the human slot without a `.md` alongside it **nor**
  cited in a folder index; sidecar without `binary:`/`source`/`updated`; sidecar marked `authority:
  current`) + the read "extract sufficient or would the agent have to ingest the binary?". New smells:
  **binary without sidecar/extract**, **sidecar without provenance**, and **sidecar marked as current**
  (an extract of human material is never a contract; content that became current **distills into `arquitetura/`**).
  Core (the slot, the label, and now the consumption stay in the method; authoring/editing each sidecar
  comes from `quenching-docs`). 15 dimensions maintained. (round 15)

- **R16 · Cross-repo portability of the `docs/` baseline (derive-before-install and adapt)** —
  `superseded-by: Rev1` (the thesis "the repo's form wins / recognizable by function, not by name /
  record the mapping, do not rename" was **inverted** to the prescriptive canonical taxonomy; see Rev1
  at the top of the Current state). Historical text of R16 preserved below. — dimension 2
  and the installation flow gain the **procedure that makes the baseline a repeatable and adaptable
  standard ACROSS REPOSITORIES** (the R13 taxonomy + the R14 audience/provenance labels + the R15 sidecars),
  installable **deterministically** without becoming a blind imposition. New section
  **«Cross-repo installation of the `docs/` baseline — derive-before-install»** in
  [references/installation.md](../../plugins/claude-quenching/skills/quenching-management/references/installation.md), a **4-step procedure**: (a) **Step 0
  derives** the sections the repo already has (non-empty variables: `$ARCH_DIR`/`$VISION`/`$BACKLOG`/`$ADR`/
  `$DOMAIN` + human slot); (b) each section is **mapped to the baseline home by FUNCTION** (`docs/standards/`
  →`arquitetura/`; `docs/decisions/`→`adr/`; `ROADMAP.md`→`VISION`) and the **repo's form WINS** (records
  the mapping, **does not rename** the folder — the standard is recognizable by function, not by canonical
  name); (c) installs **only the absent slots that apply** (completeness of what **fits**, not a blind
  checklist); (d) **preserves** what exists and marks **deprecatable** what duplicates a home (signals, does
  not remove). The core — *standard ACROSS repositories* — is the **recognizable function** of each home
  (purpose/audience) present in all repos, not the identical folder name; it is the principle already in
  the method ("derive the target repo's form, the repo's convention wins", Step 1) **applied to the SET**
  of `docs/`. **Deterministic** (same inputs→same result, without re-deriving the tree by hand per repo) **≠
  automatic** (each item still goes through Step 5 confirmation). Dim 2 ("What good looks like"/Smells/
  Remediation) is sharpened and block **2b** gains greps that **only list candidates** (`NO-HOME` — section
  with no corresponding home; `TWO-HOMES` — two sections for the same layer = baseline blindly stamped,
  duplicating the local convention) + the read "maps by function or blindly stamped?". New smells:
  **baseline installed blindly overriding local convention** (renamed/duplicated the existing section) and
  **repo section with no home mapping** (technical folder that does not match any named home — home to add or
  material in the wrong quadrant). Core (portability and the docs boundary stay in the method; authoring/
  editing each doc comes from `quenching-docs`). **CLOSES the docs topic** (R13 taxonomy
  → R14 label → R15 consumption → **R16 cross-repo installation**). 15 dimensions maintained. (round 16)

## History of rounds and revisions

> Most recent rounds at the top. Revisions (`Rev*`) appear here under the round they refine.

### Round 24 — 2026-06-29 · boundary: PARALLEL builder/updater of the `standards/` layer (fan-out by topic: mines the repo + researches references → writes/updates each standard + regenerates the index deterministically)

> Numbering note: the boundary was labeled "R23" in the operator's request, but the `current-round` anchor was
> already marking **23** (consumed by the PostToolUse `propose-docs-home.py`, dim 8). To preserve the invariant
> "never re-attacks/collides with what has already been done" and the monotonic increment of `current-round`,
> this round is recorded as **R24**. The content follows the operator's request in full.

- **Change:** dim 2 gains the tool that **actively builds/updates the entire `standards/` layer**
  from the repo + references, in **parallel** — until now it only loaded the **empty skeleton** of
  `standards/` (READMEs per subtopic, Rev2) + the single-doc authoring skill (`quenching-docs`). Two
  new payloads: **(1)** sub-agent **`assets/agents/quenching-writer.md`** (modeled after
  `quenching-auditor.md`, same return discipline): worker per TOPIC, `model: sonnet`, `tools: Read,
  Grep, Glob, Edit, Write, WebSearch, WebFetch`; receives ONE of the 9 canonical topics + repo root + the
  taxonomy + the frontmatter template; **mines the repo** for the de-facto = `current` anchored at
  `file:line`, returns **"does not apply"** when the topic does not fit, **researches external references**,
  **writes/updates** `docs/standards/<topic>/<standard>.md` (BUILD/UPDATE/Drifted, minimal frontmatter),
  follows the anti-fabrication INVARIANT (unimplemented best-practice → PROPOSAL/GAP, never current) and
  the completeness criterion of the **rebuild test** (requirement × decision), never edits generated content,
  and returns **only the condensed summary** (R9). **(2)** orchestrator skill **`assets/skills/quenching-standards/SKILL.md`**
  (modeled after `quenching-docs/SKILL.md`): derives the topics that apply, **fan-out of one
  `quenching-writer` per topic IN PARALLEL** (one message with multiple invocations; concerns that cross-reference
  stay sequential in the orchestrator; each worker returns only the summary; parallelism ≈ 15× tokens ⇒ slice
  first on large repo), optional quality step (adversarial review in fresh context checking the anti-fabrication
  invariant), collects returns, exposes gaps as PROPOSED items, and **regenerates `INDEX.md`
  DETERMINISTICALLY from disk** (scans `standards/**/*.md`, reads `title:`/`updated:`/`status:`, reconstructs
  the list between `<!-- BEGIN/END GENERATED -->` preserving the authored preamble; order by topic-subfolder +
  `order:` override). Explicit anti-bloat boundary vs. `quenching-docs` (ONE doc × entire layer;
  COMPOSES, does not duplicate). **Wiring:** `dimensions-template.md` (dim 2 — Payload gains the
  orchestrator+worker pair; "What good looks like" gains rebuild test + requirement×decision + derived index;
  Smells gains 3 new ones), `installation.md` (gap→payload line), `assets/README.md` (2 inventory lines),
  `assets/docs/standards/INDEX.md` (BEGIN/END GENERATED markers + note "do not edit the generated zone"). This
  is a **facet of dim 2** (new payload) — **15 dimensions maintained**.
- **Why:** the `standards/` skeleton (Rev2) + single-doc authoring (`quenching-docs`) left a gap: **nothing
  built/updated the entire layer from the repo**, in parallel, with a synchronized index. The backlog
  candidates "deterministic index generation/synchronization" and "completeness of the normative reference /
  rebuild test" were exactly that, and the review queue asked for the **correct source** of the rebuild test
  (Augment Code, not the SDD paper). Materializing the three at once is coherent: the parallel builder needs
  the completeness criterion (rebuild test) to know when a standard is ready, and the deterministic index to
  close the loop without drift. The fan-out by topic is the case recommended by the official docs (independent
  topics, lead spins up subagents in parallel), with the embedded caveats (condensed summary, 15× tokens,
  slice large repo, shared concerns → sequential). The anti-fabrication invariant anchors the real risk of
  asserting behavior the code does not have (MIRAGE-Bench: capability/outcome hallucination); the deterministic
  index anchors itself in generators that derive navigation from the file structure (Sphinx toctree,
  mkdocs-awesome-nav, Diátaxis "structure mirrors the product").
- **Sources:**
  - [Sub-agents — Claude Docs](https://code.claude.com/docs/en/sub-agents) (accessed 2026-06-29, ✅ scout
    WebFetch) — **verbatim** *"the subagent does that work in its own context and returns only the summary"* ·
    *"Research the … modules in parallel using separate subagents"* · *"Running many subagents that each
    return detailed results can consume significant context"* · *"Each subagent starts with a fresh, isolated
    context window"* (parallel fan-out, clean context, condensed return contract).
  - [How we built our multi-agent research system — Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
    (accessed 2026-06-29, ✅ scout) — **verbatim** *"the lead agent spins up 3-5 subagents in parallel rather
    than serially"* · scaling *"Simple fact-finding requires just 1 agent … direct comparisons might
    need 2-4 subagents … complex research might use more than 10"* · *"multi-agent systems use about 15× more
    tokens than chats"* · *"some domains that require all agents to share the same context … are not a good
    fit"* (effort scaling; 15× tokens; shared concerns → non-parallel).
  - [Claude Code best practices](https://code.claude.com/docs/en/best-practices) (accessed 2026-06-29, ✅
    scout) — **verbatim** *"A reviewer running in a fresh subagent context sees only the diff and the criteria
    you give it, not the reasoning that produced the change"* (adversarial review step in fresh context).
  - [Spec as the source of truth — Augment Code](https://www.augmentcode.com/guides/spec-as-source-of-truth-rebuildable-codebase)
    (pub. 2026-04-09, updated 2026-06-18; ✅ scout) — **verbatim** *"delete src/, point a fresh agent session
    at the spec, and regenerate. The divergences that surface are almost always implicit decisions"* ·
    *"A requirement says 'all API endpoints require authentication.' A decision says 'authorization failures
    return 403, not 404, to avoid enumeration attacks…'"* · *"teams routinely version the source code
    generated by agents but neglect to version the specs that produced it"* (**correct attribution** of the
    rebuild test; requirement × decision).
  - [Docs as Code — Write the Docs](https://www.writethedocs.org/guide/docs-as-code/) (accessed 2026-06-29) —
    versioned/PR-reviewed docs as code, single-source-of-truth.
  - [MIRAGE-Bench (arXiv 2507.21017)](https://arxiv.org/pdf/2507.21017) (accessed 2026-06-29) — *"Capability
    hallucination"* / *"Outcome hallucination"* (grounds the risk of asserting unimplemented behavior as
    current — the anti-fabrication invariant).
  - [Sphinx — toctree directive](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html)
    (accessed 2026-06-29) — *"Parse glob wildcards in toctree entries… matches are inserted … alphabetically"*
    · *"Document titles in the toctree will be automatically read from the title of the referenced document"*
    (index derived from disk, title read from the file).
  - [mkdocs-awesome-nav — philosophy](https://lukasgeiter.github.io/mkdocs-awesome-nav/philosophy/) (accessed
    2026-06-29) — *"The navigation is generated based on your file structure"* · *"File Structure First"*.
  - [Diátaxis — reference](https://diataxis.fr/reference/) (accessed 2026-06-29) — *"the structure of the
    documentation should mirror the structure of the product"* · *"Reference material is useful when it is
    consistent"*.
  - Catalog: `research/02-subagents.md`, `research/09-building-effective-agents.md`,
    `research/12-knowledge-architecture-external.md`.
- **Rejected/superseded:**
  - Discarded **one skill per topic** (a `quenching-standards-code`, `-naming`, …) — would multiply
    triggers (collision, dim 6/R4) and always-loaded descriptions (bloat, R10); the topic is a **parameter
    of the worker**, not a distinct capability. One orchestrator + one generic worker parameterized by topic
    covers all of them.
  - Discarded **running the fan-out always with all 9 topics** — violates completeness-of-what-fits (a repo
    without ML does not have `mlops/`) and wastes the 15× tokens. The orchestrator derives only the topics
    that apply and slices large repos.
  - Discarded **asserting an external best-practice as `current`** when the repo does not implement it —
    that is the central risk (capability/outcome hallucination); therefore the anti-fabrication INVARIANT
    mandates recording it as PROPOSAL/GAP `authority: background`, with a mandatory `file:line` anchor for
    what is current.
  - Discarded **regenerating `INDEX.md` by discarding the authored preamble** to "be deterministic" — the
    generated zone is **only the list** between `BEGIN/END GENERATED`; the preamble/line template is preserved
    (generator caveat: delimit, do not replace the prose).
  - Discarded **having the worker regenerate the index** — the index is deterministic (disk scan), done
    **once** by the orchestrator after the merge; letting each worker rewrite it would create race conditions/drift.
  - Discarded **creating dimension 16** — it is a facet of dim 2 (new payload for the `standards/` layer),
    just as sidecar (R15) and taxonomy (Rev1) were facets; 15 maintained.
  - Discarded **measuring the "standards only with README" grep vs. fixtures in this round** (wiring AND
    optional) — no Bash; the out-of-sync-index detection already exists in 2b, and the new grep would stay
    PENDING with no gain. The new smells are declared in dim 2; measurement enters the spine review queue
    alongside the others.
- **Next candidate:** **"Outgrowth detection — skill the base model has already surpassed"** (dim 6, axis of
  `13-skill-description-evals.md`: skill redundant with the model's native capability, pass-rate delta
  with×without ≈ 0 → deprecatable) · or **"Event hook applied to `.claude/` (the config surface), not just
  `docs/`"** (dim 8 — proposes quality fix for touched config, distinct from ConfigChange/R21 which records it).

#### Review item closed by R24 — "Source of 'rebuild test' attributed incorrectly"

- **Target:** dim 2 / R13 (and the same-named advancement candidate) — the catalog treated the *reconstruction test* as
  a technique from the SDD paper. **Correct attribution = Augment Code** (*"delete src/, point a fresh agent session at
  the spec, and regenerate"*; requirement × decision). R24 cites the correct source in the
  `quenching-writer` payload (Step 6), in the orchestrator, and in dim 2 ("What good looks like"). Item **closed** — removed from
  the spine review queue.

---

### Round 22 — 2026-06-29 · boundary: Home for DIRECTED COMMUNICATION in the `docs/` taxonomy (`communications/`) + generic skill by channel

- **Change:** the canonical `docs/` taxonomy gains a **new home, `communications/`** (9th home), for
  **directed/outbound communication** — messages to an audience (incident · change · deploy ·
  downtime/maintenance · migration · announcement · status update). Materialized in three
  coherent fronts (carrying forward R13/R18/R19): **(1) spec** — `references/docs-taxonomy.md` gains the home in
  the tree (`communications/` with `templates/` per channel + `archive/`), a dedicated `### communications/`
  section (purpose · Diátaxis "outside the four types" · `audience: human`/`authority: background` · invariant
  scannable header · per-channel template · boundary vs. `guides`/`decisions`/`standards`/`presentations`)
  and the line in "Boundary rules"; **(2) real scaffold** in `assets/docs/communications/` — home `README.md`,
  `templates/README.md` + **four per-channel templates** (`email.md` with key fields in the subject;
  `chat.md` Slack/Teams with "edit the original message"+pin+bold *single asterisk*; `wiki.md`
  Confluence/Notion with header as **properties table** + update history; `markdown.md`
  neutral = **default** when the channel was not specified), and `archive/README.md` (issued communication,
  `YYYY-MM-DD-<scope>-<slug>.md`, starts empty) — all generic, `<...>` placeholders, no `[DATA]`/`[BI]`/Unicred;
  top-level `assets/docs/README.md` gains the home line + the boundary; **(3) generic skill** payload
  `assets/skills/quenching-announcement/SKILL.md` that, given **channel + subject**, reads the template for the
  requested channel from `communications/templates/` (progressive disclosure — reads only the template for the
  channel) and **fills in the placeholders** without rewriting the structure. Dim 2 sharpened in `dimensions-template.md`
  (home in the canonical list + 4 new smells + Payload citing the scaffold and the skill); `installation.md`
  gains the gap→payload line; `detection-and-smells.md` (block 2b) gains the `communications/` greps
  (communication outside its home · channel without template · communication without header) + its own read +
  `communications` in the home allowlist and in the VARIANT/TWO-HOMES loop; `assets/README.md` (inventory)
  gains the two lines (skill + scaffold). **Counting decision:** it is a **facet of dim 2** (new canonical
  home in the `docs/` tree), as sidecar (R15) and taxonomy (R13/Rev1) were — **not** a dimension 16;
  cross-note in dim 6 (new skill). **15 dimensions maintained**
  (Simplicity First).
- **Why:** the `docs/` taxonomy (standards/decisions/vision/backlog/guides/reference/catalog/
  presentations) **had no home for directed communication** — an incident/change/deploy communication to an
  audience is a distinct quadrant (outbound *message*, dated, scannable), which is not a how-to (`guides/`),
  nor an ADR (`decisions/`), nor a contract (`standards/`), nor a visual binary (`presentations/`). The repo
  already had **living proof** of this (`docs-announcement`: fixed scannable header + Step 3 "adapt to the channel"
  for Slack/Teams · Email · Confluence/Notion), but as a skill coupled to the Data/BI domain of one repo. By
  the pure-installer doctrine (`references/installation.md`), the package needs to carry the **generic and
  portable** version of the artifact and flag the pre-existing one as **DEPRECATABLE** — the single source
  becomes the payload. The structure-not-content installer boundary (the same as Rev4 in `guides/`) is
  respected: the package bundles the STRUCTURE (home + empty per-channel templates + generic skill that reads
  them); the CONTENT (real scopes, status values, concrete audience, each communication) belongs to the repo.
  **Generic skill × per-subject:** the user preference and the official docs converge — one generic skill that
  **reads the per-channel templates** on demand (Agent Skills: `assets/` stores templates "used within the
  output", `references/` loads "only when referenced") is cheaper and more coherent than N per-subject skills
  (incident/deploy/migration are **values** of scope/status, not distinct capabilities; one skill per subject
  would multiply triggers and token cost with no gain — see Rejected).
- **Sources:**
  - [Agent Skills — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
    (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** *"The assets/ folder contains files not
    intended to be loaded into context, but rather used within the output Claude produces"* (the per-channel
    templates live in `assets`/scaffold, filled in the output) and *"Claude accesses these files only when
    referenced"* + *"if your task only needs the sales schema, Claude loads just that one file"* (the generic
    skill reads **only** the template for the requested channel — progressive disclosure justifies generic-that-reads-templates
    over N per-subject skills).
  - [Incident communication best practices — incident.io](https://incident.io/blog/incident-communication-best-practices)
    (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** *"External communications need a
    different tone."* (audience defines the form/tone) and *"Pre-written templates eliminate wordsmithing during
    a crisis. Decide on common language ahead of time, get it approved by leadership, and save it in your
    incident management tool."* (versioned templates, prepared ahead of time — docs-as-code for communication);
    channels used differently: *"#inc-[date]-[description] for the war room and #incident-updates as a broadcast
    channel"* and *"customers can also subscribe to status page updates via email"* (each channel has its use).
  - [Incident communication best practices — Atlassian](https://www.atlassian.com/incident-management/incident-communication)
    (accessed 2026-06-29, via WebSearch) — the "incident communication channels" section of a template lists
    **each channel and how it will be used** ("what types of incidents will be reported in each channel, which
    departments should use it"), with "templated copy to communicate… during each incident stage" (template
    per channel × per stage is established practice).
  - Catalog: `research/01-agent-skills.md` (progressive disclosure, `assets/`×`references/`),
    `research/07-context-engineering.md` (smallest high-signal set — the scannable header is the high-signal
    set the reader consumes first).
- **Rejected/superseded:**
  - Discarded **extending `presentations/`** to host communications — `presentations/` is visual binary
    consumed via **sidecar** (the LLM never opens the binary); a communication is **text read directly**,
    scannable, directed to an audience, dated-but-archivable. Mixing them would violate single-home (dim 12):
    two purposes, two homes. New home.
  - Discarded **creating dimension 16 "communication"** — it is a **facet of dim 2** (another home in the
    canonical `docs/` tree), as sidecar (R15) and taxonomy (Rev1) were facets and not new dimensions.
    Inflating the number of dimensions without gain violates Simplicity First; 15 maintained, cross-note in dim 6.
  - Discarded **one skill per subject** (incident/deploy/migration/downtime) — the user preferred the generic
    one and the research confirms: subject is a **value** (scope/status), not a capability; N per-subject skills
    multiply triggers (collision, dim 6/R4), inflate the description budget (always-loaded), and duplicate the
    header — toolset bloat (R10). One generic skill that **reads the channel template** covers all subjects
    with one parameter (channel) + values (subject).
  - Discarded **bundling concrete communications / the `[DATA]`/`[BI]` scopes from the repo** — that is
    repo content (structure-installer boundary, Rev4); the package bundles only `<...>` placeholders.
    `archive/` starts empty.
  - Discarded **removing/editing `docs-announcement` now** — deprecating is a **recommendation**, removal is the
    user's decision (deprecation doctrine, `installation.md`); the package flags it as DEPRECATABLE, does not
    delete.
  - Discarded **measuring the new 2b greps against fixtures in this round** — no Bash in context (as with
    R18/R19/R20); the `communications/` greps stay **PENDING** and enter the spine review queue
    (alongside the Rev1 greps already there).
- **Next candidate:** **"PR `docs/` coverage hook"** (dim 2 × dim 8 — taxonomy enforcement,
  now including the `communications/` home: communication loose outside its home, channel without template) · or the
  **"Deterministic index generation/synchronization for the normative layer"** (dim 2, rule «X defines Y») · or
  **"Completeness of the normative reference / rebuild test"** (dim 2, with the corrected source — Augment
  Code, `requirement` × `decision`).

### Round 16 — 2026-06-29 · boundary: Cross-repo portability of the `docs/` baseline (derive-before-install and adapt) — ~~CLOSES the docs topic~~ (superseded by Rev1)

#### Revision Rev4 — 2026-06-29 · `guides/` = home for guides + HOW to organize; onboarding is NOT prescribed (refines Rev3) · quenching-reviewer

- **Target:** the `guides/` home (defined by Rev1, materialized by Rev2, pruned by Rev3) — specifically
  **(a)** the prescription Rev3 left behind (the guide-file `guides/onboarding.md` bundled in the scaffold) and
  **(b)** the absence of guidance on **how** the repo should organize the guides.
- **Critique:** **User pointer** (verbatim, translated): *"Adjust it so it does NOT define the existence of an
  onboarding.md. The repo will decide whether it wants the guide or not. We need to indicate that guides is the place
  to store guides, and how to store them (preferably in a structure of folders and subfolders)."* Two signals:
  (1) Rev3 still **prescribed** an onboarding artifact (`onboarding.md` created in `assets/`) — but **which**
  guides exist is the REPO's decision, not the skill's (the skill is an installer of **structure**, not of
  guide **content**); (2) `guides/` stated what it is (how-to+tutorial) and what **not** to do (audience
  silo) but did **not** state **how to organize** — the positive directive was missing.
- **Refinement (conceptual diff):** **(1) Onboarding de-prescription** — the `guides/onboarding.md`
  created by Rev3 becomes an **orphan to remove**; onboarding appears only as an **illustrative example**
  of a guide (never a fixed file or home). **(2) "How to organize" is now declared** — `guides/` is the
  home for guides and the repo organizes them **preferably in folders/subfolders by topic/area**
  (subject-first), with standalone guides as a direct `.md` when appropriate. **(3) Reconciliation with Rev3**
  made explicit to avoid apparent contradiction: Rev3 pruned the `onboarding/` subfolder because it was a
  **prescribed** **audience** silo — that does **not** prohibit subfolders; subfolders by **topic** created
  by the repo are **encouraged**. Memorable rule: *folder organization by the repo = yes; reserving a folder
  by audience = no*. Changes per file: **`references/docs-taxonomy.md`** — tree: `guides/` comment changes
  from "onboarding is ONE guide: onboarding.md" to "the REPO organizes (preferably subfolders by topic);
  onboarding is just an example"; `### guides/` section gains two bullets ("How to organize — the REPO
  decides" + "subfolders by TOPIC yes, AUDIENCE silo no"), removing the `onboarding.md` prescription.
  **`assets/docs/guides/README.md`** — new section "## How to organize the guides" (prefer subfolders by
  topic; the skeleton does not bundle a ready-made guide; onboarding as example, not audience silo).
  **`assets/docs/guides/onboarding.md`** — marked **ORPHAN to remove** (reverted). **`assets/README.md`**
  — inventory line: `guides/` now "(README only)", making explicit that the repo creates/organizes the guides.
- **Effect:** (a) **correct installer boundary** — the skill installs the **structure** (`guides/` + how
  to organize), not the **content** (which guide exists); onboarding stops being a bundled artifact; (b)
  **positive directive** — `guides/` now states **how** to store (folders/subfolders by topic, by the repo),
  not only what to avoid; (c) **explicit Rev3↔Rev4 coherence** — pruning the audience silo coexists with
  encouraging topic subfolders, without apparent contradiction. Self-contained/portable invariant preserved
  (no repo-specific guide/content bundled; `<owning team>` placeholders). **Orphan to remove** by the
  orchestrator: `assets/docs/guides/onboarding.md` (the `assets/docs/guides/onboarding/` from Rev3
  remains an orphan too).

#### Revision Rev3 — 2026-06-29 · PRUNES the `guides/onboarding/` silo → `onboarding` becomes a guide (refines Rev1/Rev2) · quenching-reviewer

- **Target:** the canonical taxonomy for the docs topic (defined by Rev1, materialized by Rev2) — the
  `guides/onboarding/` home as a **subfolder/collection** inside `guides/`. Defined in
  `references/docs-taxonomy.md` (tree + `guides/` section) and mirrored in the scaffold `assets/docs/guides/`.
- **Critique:** (1) **User pointer** (verbatim, translated) — *"I believe the onboarding split is redundant.
  Almost all guides can be an onboarding. I think onboarding can be a guide, but not a collection
  of guides."* (2) **Internal contradiction with the "home = topic" (subject-first) rule** that
  `docs-taxonomy.md` itself establishes: *"homes are by topic"*. `onboarding` is a cut by **audience** (those
  joining the team), **not** a distinct topic — almost every how-to already serves as onboarding; reserving a
  subfolder by audience violates the subject-first principle. (3) **Bloat (Simplicity First)** — an entire
  folder where **a single file** suffices; `guides/onboarding/README.md` was the sole inhabitant of the silo.
- **Refinement (conceptual diff):** `onboarding/` is **demoted** from subfolder to **a guide file**
  `guides/onboarding.md`. `guides/` stops having subfolders (the home stores guides as `.md` files directly).
  The how-to ≠ reference ≠ explanation boundary remains intact. Changes per file:
  **`references/docs-taxonomy.md`** — tree: `guides/` loses the `onboarding/` line, gains the comment
  "onboarding is ONE guide: onboarding.md, not a subfolder"; the `### guides/` section swaps the bullet **"Subfolder:
  `onboarding/`"** for **"`onboarding` is ONE guide, not a subfolder"** (with the subject-first/audience rationale).
  **`assets/docs/guides/README.md`** — "## Subfolder"/table removed; replaced by a sentence
  ("no subfolders; `onboarding` is a guide — `onboarding.md`"). **`assets/docs/guides/onboarding.md` created**
  (content ported from the old `onboarding/README.md`, frontmatter `audience: both`/`authority: background`).
  **`assets/docs/guides/onboarding/README.md`** marked **ORPHAN to remove** by the orchestrator (the reviewer
  has no Bash for `rm`/`mv` on the folder). **`assets/README.md`** (inventory) — `docs/guides/` line updated
  from `(README + onboarding/)` to `(README + onboarding.md)`. `detection-and-smells.md`/`dimensions-template.md`
  **did not cite** `onboarding` (empty grep) — untouched.
- **Effect:** (a) **less bloat** — a folder silo becomes a file (the sole inhabitant no longer needs its own
  folder, Simplicity First); (b) **coherence with subject-first** — the only subfolder in the tree that was
  organized by **audience** (not by topic) was eliminated, aligning `guides/` with the "home = topic" rule
  that the spec establishes; (c) **`assets/` remains matched to the spec** (the payload mirrors the pruned
  tree). Self-contained/portable invariant preserved (no repo coupling; `<owning team>` placeholders).
  **Orphan to remove** by the orchestrator: `assets/docs/guides/onboarding/`.

#### Revision Rev2 — 2026-06-29 · MATERIALIZES the canonical scaffold in `assets/docs/` (follows Rev1) · quenching-reviewer

- **Target:** Rev1 / the canonical taxonomy for the docs topic — the **materialization** facet that Rev1
  left pending. Rev1 fixed the tree as **definition/prose** (`references/docs-taxonomy.md` + dim 2/3/5/11
  + Step 0/2b + `installation.md`) but **did not touch `assets/`**; the `assets/docs/` payload still had the
  old layout (`README.md` in bloated prose + skeletons `arquitetura/`/`adr/`/`VISION.md` = variants).
- **Critique:** **User pointer** — the taxonomy lived as **prose in a single `assets/docs/README.md`**;
  the user wants it **materialized as a real scaffold**, with a `README.md` per home/subfolder that (a) makes
  sense read IN THE FINAL REPO (text aimed at the repo reader, not meta-talk about the skill — "copy-pasteable
  almost verbatim") and (b) makes **visible which subfolders exist** inside each home ("I don't know which
  contexts we'll have inside arquitetura"). Without that, the installer would have to re-derive the tree by hand
  and the repo reader would not see the homes; `assets/` also **diverged** from `docs-taxonomy.md` (the spec
  described one tree, the payload delivered another).
- **Refinement (the tree created):** materialized **exactly** the locked tree from `docs-taxonomy.md`,
  29 files under `assets/docs/`:
  - `README.md` (top) — rewritten **slim**: manifest + short table home→purpose→link + boundary summary;
    points to `references/docs-taxonomy.md` as the spec (does not repeat the tree in prose).
  - `standards/README.md` + `standards/INDEX.md` (line template + rule "index that lies = Drifted") +
    the 9 subtopics `architecture/` (explicitly states "patterns lives here, there is no docs/patterns/"),
    `code/` (symbols), `naming/` (data), `data-modeling/`, `ci-cd/`, `workflows/`, `mlops/` (interface
    Resolution 4.966; the regulation itself → `reference/regulations/`), `quality/`, `platform/`. Each
    states that the repo maintains only the subtopics that apply and that current docs go into `INDEX.md`.
  - `decisions/README.md` (ported from the old `adr/README.md`: proposed→…→implemented(distills+exits) cycle +
    `NNNN-slug/` folder + Distilled ledger; canonical name `decisions/`).
  - `vision/README.md` (segmented by area, no deadline) + `vision/_area.md` (ONE shell template: Target state
    / Pillars / Non-goals as commented placeholders; the repo copies per area).
  - `backlog/README.md` (updated to canonical name: `vision/`/`decisions/`/`standards/`).
  - `guides/README.md` (how-to ≠ reference ≠ explanation boundary) + `guides/onboarding/README.md` (**Rev3 demoted this to the guide-file `guides/onboarding.md`** and pruned the `onboarding/` silo).
  - `reference/README.md` (external, what we consume; distinct from `standards/` and `catalog/`) +
    `tools/` + `libraries/` + `regulations/` (PDFs via `../../_sidecar.md`, never the binary).
  - `catalog/README.md` (AUTO-GENERATED × curation SEPARATED, rule «X defines Y»).
  - `presentations/README.md` (human deliverables via `../_sidecar.md`, the LLM never opens the binary) +
    `slides/` + `diagrams/` (prefer diagrams-as-code) + `reports/`.
  - Each README starts with **frontmatter** (`audience`/`authority` per the home, model
    `../frontmatter/docs-front.md`), a short body aimed at the final repo, and closes with the removable
    traceability line `> _Skeleton installed by quenching-management — spec in references/docs-taxonomy.md._`.
  - `_sidecar.md` — pointed to `presentations/`+`reference/regulations/` (formerly `apresentacoes/diagramas/normativos`)
    and distillation corrected `arquitetura/`→`standards/`.
  - `assets/README.md` (inventory) — legacy lines removed (`docs/arquitetura/INDICE.md`, `docs/VISION.md`,
    `docs/adr/README.md`); new tree lines added; "No payload" now cites `docs/vision/` + `_area.md`.
- **Effect:** (a) **visible/installable scaffold** — the installer copies the ready tree instead of re-deriving
  it; the final repo reader sees each home and its subfolders through the README itself; (b) **`assets/` matches
  the spec** — the payload stopped diverging from `docs-taxonomy.md` (the prose-vs-assets contradiction from
  Rev1 closed); (c) **less bloat at the top** — the `README.md` became a slim manifest (the heavy definition
  lives in the spec, Simplicity First). `references/` and `SKILL.md` stayed **untouched**; self-contained/
  portable invariant preserved (no coupling to a specific repo; `<owning team>` placeholders). **Orphans from
  the old layout removed** by the orchestrator (the reviewer has no Bash): `assets/docs/arquitetura/`,
  `assets/docs/adr/`, `assets/docs/VISION.md`.

#### Revision Rev1 — 2026-06-29 · SUPERSEDES R16 (and adjusts the language of R13) · quenching-reviewer

- **Target:** Round 16 (and the language of R13/R14/R15) — the ADAPTIVE thesis of the docs topic: *"the
  repo's convention wins"*, *"recognizable by function, not by name"*, *"record the mapping, do NOT rename"*.
  The topic was marked "CLOSED at R16".
- **Critique:** (1) **User pointer** (explicit trigger) — requires **canonical** names, without
  ambiguity like `arquitetura/ (or standards/)`. (2) **Internal contradiction with DRY/single-home
  (dim 12)** — the baseline itself wrote `arquitetura/ (or standards/)`, `adr/ (or decisions/)`,
  `VISION.md (or vision/)`: **two names for the same home** is exactly the `TWO-HOMES` smell that
  dim 12 condemns; the R16 thesis ("the repo's form wins") **produces** that smell. (3) **Bloat** — dim 2
  accumulated huge paragraphs from R13-R16 in the template (Simplicity First: definition that should have
  been materialized in its own file).
- **Refinement (conceptual diff):** the thesis flips from **ADAPTIVE** to **PRESCRIPTIVE**. The skill
  defines a **canonical `docs/` taxonomy with fixed names**; the repo **converges to the skill**. What
  changes from R16: stops "recording the mapping and **preserving** the repo's name" and instead "**proposes
  convergence** to the canonical name"; the variant name stops being "the repo's convention that wins" and
  becomes a **non-convergence smell** (migration candidate). **Safety is the same**: PROPOSES the
  migration, marks the variant **DEPRECATABLE**, **never renames/deletes without approval** (Step 5
  confirmation + deprecation doctrine preserved). **Portability reconciliation:** it does not die — it becomes
  **stronger**: instead of "each repo keeps its name, recognizable by function", now "every repo converges
  to the SAME tree with identical names" (human/agent sees the tree literally identical across repos).
  Changes per file: **`references/docs-taxonomy.md` created** (the single canonical specification of
  the tree — all homes + subfolders, purpose/Diátaxis/`audience`/`authority`/boundary per home +
  English-kebab-case prescriptive rule/`INDEX.md` + variant migration doctrine); **`dimensions-template.md`**
  — dim 2 **trimmed** (short directive + link to `docs-taxonomy.md`, R13-R16 prose pruned), dim 3
  (direction → segmented `vision/` folder), dim 5 (`decisions/` canonical, formerly `adr/`), dim 11 (`catalog/`),
  and the top-level notice (names in `docs/` are canonical; variant = migrate); **`detection-and-smells.md`** —
  Step 0 derives against the canonical first + VARIANT flag, block 2b rewritten ("converges to canonical
  or is a variant to migrate?"), new homes (`reference/`/`guides/`/`presentations/`) in the known-homes list,
  variant-name-not-converged smell, `TWO-HOMES` maintained; **`installation.md`** —
  section became "converge-to-canonical" (map variant→canonical, PROPOSE deprecatable migration with approval),
  gap→payload map updated, "repo's convention wins" exception **scoped** to skills/agents/hooks
  (NOT valid for `docs/` names). **`assets/` NOT touched** — patterns dissolve into
  `standards/architecture/` (there is no `patterns/` silo); 15 dimensions maintained.
- **Sources:** [MADR — adr.github.io/madr](https://adr.github.io/madr/) (accessed 2026-06-29, ✅
  verified by WebFetch) — **verbatim** *"Create folder `docs/decisions` in your project"* and
  *"Decisions are placed in the subfolder `decisions/`"* ⇒ `decisions/` is canonical, not `adr/`.
  [GitLab Docs — folder structure](https://docs.gitlab.com/development/documentation/site_architecture/folder_structure/)
  (accessed 2026-06-29, ✅ verified by WebFetch) — *"we primarily follow the structure of the GitLab
  UI or API"* and *"Put files for a specific product area into the related folder"* ⇒ homes by **topic**
  (subject-first), stable names. [Diátaxis — diataxis.fr](https://diataxis.fr/) (2026-06-29) — 4
  types: the **content inside** each home follows Diátaxis, but the **homes** are by topic.
  [AGENTS.md — Linux Foundation](https://agents.md/) (2026-06-29) — *"a predictable place… the nearest
  file"*: STABLE canonical names aid navigation by both humans and agents (portability is STRONGER
  with convergence to the same tree, not with each repo keeping its own).
- **Effect:** (a) **less noise / more determinism** — a single canonical tree replaces the ambiguous
  `name (or other-name)` (kills the `TWO-HOMES` that the baseline itself was producing); (b) **dim 2 simpler**
  — short directive + link; the heavy definition migrated to `docs-taxonomy.md` (the "better-structured
  other folder" the user requested); (c) **stronger portability** — convergence to the same tree instead
  of re-mapping by function; (d) **correct source** — `decisions/` (MADR) instead of
  `adr/`. The docs topic was **REOPENED** (no longer "closed at R16"): the **Rev2** that materializes the
  canonical scaffold in `assets/docs/` is still needed (second agent).

---

- **Change:** section **«Cross-repo installation of the `docs/` baseline — derive-before-install»** created
  in [references/installation.md](../../plugins/claude-quenching/skills/quenching-management/references/installation.md) and sharpened **dimension 2** in
  `dimensions-template.md` ("What good looks like" · Smells · Remediation) and cross-cutting block **2b** in
  `detection-and-smells.md`. R13 gave the **taxonomy/homes** of `docs/`, R14 the **audience+provenance label**
  per file, R15 the **consumption** of the human slot (sidecar); what was missing was the **procedure that
  makes this baseline a repeatable and adaptable standard ACROSS REPOSITORIES** — installable
  deterministically, without becoming a blind imposition. The evolution provides a **derive-before-install** in **4
  steps** (the repo's convention wins): (a) **Step 0 derives** the sections the repo already has (non-empty
  variables `$ARCH_DIR`/`$VISION`/`$BACKLOG`/`$ADR`/`$DOMAIN` + human slot); (b) each existing section is
  **mapped to the baseline home by FUNCTION** (`docs/standards/`→`arquitetura/`; `docs/decisions/`→`adr/`;
  `ROADMAP.md`→`VISION`) and the **repo's form WINS** — the baseline **records the mapping, does not rename**
  the folder (like AGENTS.md: *"use any headings you like"* / *"no required fields"*; the standard is
  recognizable by **function**, not by canonical name); (c) installs **only the absent slots that apply**
  (completeness of what **fits**, not a blind checklist — the slots *"layer rather than replace each
  other, so apply whichever fit your repository"*); (d) **preserves** what exists and marks **deprecatable**
  what duplicates a home (signals, does not remove). Conceptual diff: dim 2 stops having the baseline as
  a **stampable** skeleton and gains the baseline as a **derived-and-mapped** form — what makes it a
  standard across repos (humans and LLMs move between them) is not the identical folder names, it is the
  **recognizable function** of each home present in all of them; it is the principle already in the method
  ("derive the target repo's form, the repo's convention wins", Step 1) **applied to the SET** of `docs/`,
  not to one layer. Explicit distinction: **deterministic** (same inputs→same result, without re-deriving
  the tree by hand per repo) **≠ automatic** (each item still goes through Step 5 confirmation). Block **2b**
  gains greps that **only list candidates** — `NO-HOME` (section of `docs/` that does not match any named home)
  and `TWO-HOMES` (two sections for the same layer — e.g.: `arquitetura/` AND `standards/` coexisting) — + the
  read "maps by function or blindly stamped?". New smells: **baseline installed blindly overriding local
  convention** (renamed/duplicated the existing section; two homes for the same layer) and **repo section
  with no home mapping** (technical folder that does not match any home — home to add or material in the
  wrong quadrant). SKILL.md untouched (dim 2, the baseline, and the installation are `references/`); 15
  dimensions maintained. **CLOSES the docs topic** (R13 taxonomy → R14 label → R15 consumption →
  R16 cross-repo installation).
- **Why:** it was the **next candidate** pointed to explicitly by R13/R14/R15 and the core of the
  user's direction for the docs topic — *"standard ACROSS repositories"*. R13-R15 left the baseline
  **complete in content** (where it lives · for whom/from where · how the LLM reads it) but **silent on
  how to replicate it across repos without re-deriving by hand or imposing a fixed layout**. Without this
  procedure, the installation had two dead ends: stamp the skeleton blindly (overwrites local convention,
  creates two homes, breaks "the repo's convention wins") **or** re-derive the tree manually per repo
  (non-repeatable, non-standard). The derive-before-install closes this by reusing the principle the method
  already has (Step 1) and anchoring it in how the official ecosystem treats cross-repo standards: AGENTS.md is
  recognizable **by function** (no required fields, *"use any headings you like"*, proximity precedence), and
  the Claude Code monorepo docs treat configs as layers that *"layer rather than replace each other"* and
  baselines as *"one set of conventions everyone installs"* derived from a **path-to-plugin map** — not an
  imposed layout. The method **lives** by this: it already installs its own payloads by adapting to the derived
  form (Steps 1/5); R16 generalizes that discipline to the **set** of `docs/` across repos.
- **Sources:** [Set up Claude Code in a monorepo or large codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** *"Replace many per-directory CLAUDE.md
  files with one set of conventions everyone installs"* (repeatable installable baseline across scopes);
  *"Each setting below is independent. They layer rather than replace each other, so apply whichever fit
  your repository"* (install only what fits, preserve what exists — does not overwrite); *"a script that reads
  the launch directory… looks it up in a path-to-plugin map committed to the repository"* (derived and versioned
  path mapping, not imposed); the monorepo table confirms per-directory `CLAUDE.md` and derivation from the
  existing structure (*"substitute your own subsystem directory"*). [AGENTS.md — agents.md](https://agents.md/)
  (accessed 2026-06-29, ✅ re-verified by WebFetch) — **verbatim** *"Agents automatically read the
  nearest file in the directory tree, so the closest one takes precedence"* (standard recognizable by
  proximity/function, portable across repos); *"AGENTS.md is just standard Markdown. Use any headings you
  like; the agent simply parses the text you provide"* and the fact of **no required fields** (function wins
  the canonical name — basis of "maps by function, does not rename"); the migration **verbatim**
  *"Rename existing files to AGENTS.md and create symbolic links for backward compatibility"* (preserves what
  exists when adopting the standard, does not stamp over it); under the **Agentic AI Foundation / Linux Foundation**
  (standard across repos, not ad-hoc). Catalog: `research/12-knowledge-architecture-external.md`
  (AGENTS.md README-humans × agent, proximity precedence, 60,000+ repos; 3-layer architecture
  hot/skills/cold; **10 sources confirmed** in the anti-hallucination verification) and `research/10-agents-md-interop.md`
  (separation of concerns cross-tool/cross-repo).
- **Rejected/superseded:** discarded **creating a new dimension** "portability/docs installation" — it is
  a sharpening of dim 2 + the existing installation flow (portability **is** the procedure for installing
  the larger taxonomy baseline); the axis enters the "What good looks like" of dim 2, `installation.md`, and
  the **2b** grep (as in the previous cross-cutting blocks), maintaining 15 dimensions (Simplicity First).
  Discarded **generating a script/CLI installer** (name→name auto-mapper, index generator) as a mandatory
  artifact — violates "deterministic ≠ automatic": each item goes through Step 5 confirmation, and an
  installer that stamps without approval breaks "the repo's convention wins"; index generation and the coverage
  hook remain as **distinct backlog candidates**. Discarded **forcing the canonical folder name**
  (renaming `docs/standards/` to `docs/arquitetura/` on install) — that is exactly the "blind baseline" that
  the round names as a smell; the standard is recognizable by **function**, not by name (AGENTS.md *"use
  any headings you like"*). Discarded **packaging the payloads as a plugin/marketplace** now — that is the
  **distribution** axis (rollout in an org), distinct from **derive-before-install** (adapting to one repo);
  it stays as the "Internal plugin/marketplace" candidate. Discarded consuming the **PR `docs/` coverage
  hook** (taxonomy enforcement) — crosses dim 2 × dim 8 and is a distinct boundary; anticipating it would
  dilute the single evolution. Discarded **writing the real mappings** of a specific repo — that is application
  (Steps 1-5), not skill development; the procedure **models** them, the application stays outside the single
  round.
- **Next candidate:** ~~the **docs topic is closed** (R13-R16)~~ **[OVERRULED by Rev1 — the docs topic
  was REOPENED: the adaptive thesis of R16 became a prescriptive canonical taxonomy; immediate pending task =
  Rev2 materializing `assets/docs/`]**; the backlog opens new fronts —
  "Deterministic index generation/synchronization for the normative layer" (dim 2, distinct from the
  installation axis: the index as a derivable artifact from the files, rule «X defines Y») · "Completeness
  of the normative reference / rebuild test" (dim 2, reopened with the correct source — Augment Code,
  `requirement` × `decision`) · "Outgrowth detection — skill the base model has already surpassed" (dim 6,
  `13-skill-description-evals.md`) · "AGENTS.md / cross-tool interoperability" · "Internal plugin/marketplace
  as rollout vehicle for the baseline" · "PR `docs/` coverage hook" (dim 2 × dim 8).

### Round 15 — 2026-06-29 · boundary: Human-nature material without ingesting binary noise (sidecar/extract)

- **Change:** payload [assets/docs/_sidecar.md](../../plugins/claude-quenching/skills/quenching-management/assets/docs/_sidecar.md) created — the **text extract
  `.md` alongside the binary** of the human slot (slide/PDF/diagram) — and sharpened **dimension 2** in
  `dimensions-template.md` (What good looks like · Detection · Smells · Remediation · Payload), the **baseline**
  [assets/docs/README.md](../../plugins/claude-quenching/skills/quenching-management/assets/docs/README.md) (section "The human material slot" resolves the "how the
  LLM consumes" that R13 had deferred) and cross-cutting block **2b** in `detection-and-smells.md`. R13
  **named** the slot (`apresentacoes/`/`diagramas/`/`normativos/`); R14 **labeled** each doc/folder
  (`audience`/`authority`); what was missing was **how** the LLM consumes that material **without ingesting
  the binary**. The evolution provides the **sidecar/extract** pattern: a `.md` alongside the binary (1 per
  file) that carries the **smallest high-signal set** — navigable summary + key points + `binary:` pointer
  (path/URL) to the source, which the agent **references without opening**. The sidecar **inherits the
  provenance from R14** and starts as `audience: agent`/`authority: background` (the LLM reads the extract;
  the source binary is `human`). The **extract vs. index-only rule** defines when to populate: *extract* a
  sidecar when the **content governs a technical decision** (a regulation that underpins a rule, a slide that
  defines a domain concept, a diagram of the flow the code follows); *index only* (a `README`/manifest of the
  **folder** — name + 1 line + path) material that is purely a human reference file — **do not extract for
  extraction's sake** (an orphan sidecar no one consults is also context rot). Conceptual diff: dim 2 stops
  having **only** the form (taxonomy/R13) and the label (audience+provenance/R14) and gains the **consumption
  mechanism** for the human slot — the LLM now reads high-signal content in text, instead of ingesting the
  `.pdf`/`.pptx` through vision. New smells: **binary without sidecar/extract** (the agent would have to
  ingest the binary, ~7x the tokens, or ignore it), **sidecar without provenance** (`binary:`/`source`/`updated`
  absent — unverifiable), and **sidecar marked as current** (an extract of human material is never a contract;
  content that became current **distills into `arquitetura/`**). Block **2b** gains greps that **only list
  candidates** (binary in the slot without `.md` alongside it, nor cited in a folder index; sidecar without
  `binary:`; sidecar with `authority: current`). `assets/README.md` inventory and `installation.md` map updated
  (new line `docs/_sidecar.md` → dim 2, 12). SKILL.md untouched (dim 2, the baseline, and detection are
  `references/`/`assets/`); 15 dimensions maintained.
- **Why:** it was the **next candidate** pointed to explicitly by R13 and R14, and the user's explicit
  direction — the next facet of the **`docs/` structure** topic: R13 gave the taxonomy (where it lives), R14
  gave the label (for whom / from where), and what was missing was the **consumption** (how the LLM reads)
  of human-nature material. Without it, the human slot was a dead end: the method **named** and **labeled**
  the slide/PDF, but did not tell the agent **how** to use it — and the only alternative was **ingesting the
  binary**, which the official source shows is expensive **and** low-signal (vision, each page becomes an
  image, ~7x the tokens of a text extract). The sidecar closes this with the same principle that underpins all
  of dim 1/6/7 (smallest high-signal set + structured note-taking): knowledge becomes an external text file,
  re-read on demand, instead of carrying the binary in the window. The method **lives** by this — it already
  carries its own payloads as navigable text and references them; R15 generalizes the pattern to the
  human material of the target repo.
- **Sources:** [PDF support — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/pdf-support)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** *"The system converts each page of
  the document into an image. The text from each page is extracted and provided alongside each page's
  image"* (the binary is processed by vision); cost **verbatim** *"Each page typically uses 1,500-3,000
  tokens per page depending on content density"* **+** *"Since each page is converted into an image, the
  same image-based cost calculations are applied"*; the mode contrast (Bedrock) **verbatim** *"Uses
  approximately 1,000 tokens for a 3-page PDF"* (text-only) × *"Uses approximately 7,000 tokens for a
  3-page PDF"* (full vision) = ~7x; best practices **verbatim** *"Split large PDFs into chunks when
  needed"* and *"For large PDFs, consider uploading with the Files API and referencing by `file_id` to keep
  request payloads small"* (reference the source without loading it inline). [Effective context engineering
  for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  (2025-09-29, foundational source already confirmed in `research/07`) — the **smallest high-signal set** (the
  smallest set of highly relevant tokens) and **structured note-taking** (the agent writes/re-reads external
  text files as memory, instead of keeping everything in the window) = the doctrine the sidecar applies.
  Catalog: `research/07-context-engineering.md` (smallest high-signal set; structured note-taking NOTES.md;
  just-in-time retrieval — "on-demand navigation instead of pre-loading"; 9 sources confirmed in the
  anti-hallucination verification).
- **Rejected/superseded:** discarded **creating a new dimension** "sidecar/human material" — it is a
  sharpening of existing dim 2 (the sidecar **is** the consumption mechanism of the slot in the larger
  taxonomy); the axis enters the "What good looks like" of dim 2 + the grep in **2b** (as in the previous
  cross-cutting blocks), maintaining 15 dimensions (Simplicity First). Discarded **prescribing a specific
  extraction pipeline** (PyMuPDF4LLM/Docling/markitdown/community `pdf-to-markdown` skill) as mandatory —
  they are third-party tools, specific and outside the portable scope; the method defines the **artifact
  pattern** (sidecar `.md` with provenance + pointer), not the tool that generates it (authoring stays in
  `quenching-docs`; the user chooses how to extract). Discarded **having the agent open the binary via Files
  API/vision** as the standard path — that is exactly the binary noise this round avoids; the Files API
  enters only as a **rare exception** (the sidecar points to what **only** exists in the source), not as
  routine consumption. Discarded **forcing a sidecar for every binary** indiscriminately — the extract-vs-index
  rule avoids the orphan extract (context rot): material that is purely a reference file stays **index-only**
  in a folder README. Discarded **writing the real sidecares** of each piece of material now — that is
  payload/content authoring; the template **models** them and the 2b **requires** them, the application
  stays outside the single round. Discarded consuming the **cross-repo portability** facet of the baseline
  (R10 from the backlog) — that is the next distinct boundary; anticipating it would dilute the single
  evolution and violate the direction (this round **only** tackles consumption of human material without
  binary noise).
- **Next candidate:** "Cross-repo portability of the `docs/` baseline (deterministic installation/adaptation)"
  — making the R13 taxonomy + R14 labels + R15 sidecars **installable and adaptable** in a repeatable way
  across repos (standard-name → repo-name mapping, index generation, coverage hook), without re-deriving by
  hand each time — or "Outgrowth detection — skill the base model has already surpassed" (dim 6, catalog
  `13-skill-description-evals.md`).

### Round 14 — 2026-06-29 · boundary: Segmentation of `docs/` by audience (human × LLM) with provenance frontmatter

- **Change:** payload [assets/frontmatter/docs-front.md](../../plugins/claude-quenching/skills/quenching-management/assets/frontmatter/docs-front.md) created — the
  **minimal audience + provenance header per `docs/` file/folder** — and sharpened **dimension 2** in
  `dimensions-template.md` (What good looks like · Detection · smells · remediation · payload), the **baseline**
  [assets/docs/README.md](../../plugins/claude-quenching/skills/quenching-management/assets/docs/README.md) (new section "Label per file: audience + provenance")
  and cross-cutting block **2b** in `detection-and-smells.md`. R13 gave the **taxonomy/homes** (*where* each
  thing lives in `docs/`); until R13 the method **had no per-file label** that stated *for whom* and *from
  where* — the agent read everything at the same authority level, without distinguishing current-contract from
  human-background. The evolution gives each doc — or each homogeneous folder, via its `README`/index — a
  minimal **audience** frontmatter (`audience: both` human+LLM · `agent` LLM-first/normative · `human`
  human-only/background) and **authority + provenance** (`authority: current` source-of-truth/contract ×
  `background` background/history; `source`/`maintainer`/`updated`). Conceptual diff: dim 2 stops having
  **only** the form (R13 taxonomy) and gains the **semantic label per file** — the agent now knows what to
  **consume as truth** (agent/current) × what is **human background** (human/background — do not cite as
  contract), and the human knows what to **edit freely** (background) × what is a **contract** (current,
  edited only by the owning skill). This is the **README-humans × CLAUDE.md/AGENTS.md** separation (dim 12)
  applied at the **file level**; the human slot from R13 starts as `audience: human`/`authority: background`
  (the LLM reads only the sidecar). `updated` becomes the provenance anchor (old date vs. the described
  standard = fossil candidate, crosses with dim 1/context rot). New smells: **doc without declared audience/
  authority** (the agent cannot tell whether it is truth-to-consume or human-only-background; the human cannot
  tell whether it is editable or a contract) and **human material marked as current** (slide/PDF/draft without
  `authority: background` that the agent cites as a contract). Block **2b** gains a grep that **only lists
  candidates** (`.md` doc in `docs/` without `audience`/`authority` in the frontmatter — **not** a smell if the
  **folder** already labels via README/index) + the read "consume as truth × human background".
  `assets/README.md` inventory updated (new line `frontmatter/docs-front.md` → dim 2, 12). SKILL.md untouched
  (dim 2, the baseline, and detection are `references/`/`assets/`); 15 dimensions maintained.
- **Why:** it was the **next candidate** pointed to explicitly by R13 and the user's explicit direction —
  the next facet of the **`docs/` structure** topic: R13 gave the taxonomy (named homes); what was missing
  was the **per-file label** that makes the structure serve **both humans and LLMs** with opposing criteria.
  Without it, the taxonomy says *where to look* but not *what to trust*: an agent scanning `docs/` cannot
  distinguish a normative contract from a presentation slide or an old decision — and risks **citing historical
  background as current truth** (the most expensive smell, because the base *looks* authoritative). The
  audience+authority label closes this with the same principle that AGENTS.md applies at the top of the repo
  (README-humans × agent-context), just at the file level, and makes **provenance verifiable**
  (source/maintainer/updated) as MADR does for ADRs. The method **lives** by this: the package itself already
  marks its payloads (`status: current`, `updated`) — R14 generalizes that label to the entire `docs/` surface
  and extends it with the **audience** dimension.
- **Sources:** [AGENTS.md — agents.md](https://agents.md/) (accessed 2026-06-29, ✅ re-verified by
  WebFetch) — **verbatim** *"README.md files are for humans: quick starts, project descriptions, and
  contribution guidelines. AGENTS.md complements this by containing the extra, sometimes detailed context
  coding agents need"* and *"Give agents a clear, predictable place for instructions. Keep READMEs concise and
  focused on human contributors"* (the human × agent audience boundary — basis of `audience:`); proximity
  precedence *"the closest AGENTS.md to the edited file wins"* (label by proximity, portable); under the
  **Agentic AI Foundation / Linux Foundation** (versioned provenance/stewardship). [Use YAML front matter
  for metadata — MADR](https://adr.github.io/madr/decisions/0013-use-yaml-front-matter-for-meta-data.html)
  (accessed 2026-06-29, ✅ verified by WebFetch) — MADR stores **verbatim** the fields `status`,
  `decision-makers`, `date` in YAML front matter because *"Tools can handle it more easily"* and *"It shortens
  the body"* (machine-readable provenance separated from the body — direct model for `authority`/`source`/
  `updated`). [Set up Claude Code / Extend Claude Code — Claude Code Docs](https://code.claude.com/docs/en/features-overview)
  (accessed 2026-06-29 via WebFetch) — `.claude/rules/` with **`paths` frontmatter** *"only load when Claude
  works with matching files, saving context"* and *"Can be scoped to file paths"* (official precedent of
  **selecting context by file label/scope** — what `audience:` does for `docs/`). [Diátaxis](https://diataxis.fr/)
  (accessed 2026-06-29, ✅ verified by WebFetch) — *"documentation should itself be organised around the
  structures of those needs"* / *"four distinct needs"* (organize by need/audience, not just by type).
  Catalog: `research/12-knowledge-architecture-external.md` (AGENTS.md README-humans × agent;
  MADR 4.0.0 YAML front matter machine-readable status/date/decision-makers; docs-as-code single-source-of-truth;
  requirement × decision; 10 sources confirmed in the anti-hallucination verification) and
  `research/10-agents-md-interop.md` (separation of concerns cross-tool).
- **Rejected/superseded:** discarded **creating a new dimension** "docs audience/provenance" — it is a
  sharpening of existing dim 2 (the label **is** an attribute of the section in the larger taxonomy); the
  axis enters the "What good looks like" of dim 2 + the grep in **2b** (as in the previous cross-cutting blocks),
  maintaining 15 dimensions (Simplicity First). Discarded **detailing the sidecar/text extract** (how the LLM
  reads the PDF/slide from the human slot without ingesting the binary) — that is the **next explicit facet**
  of the docs topic, reserved for the next round; anticipating it would dilute the single evolution and violate
  the direction (this round **only** labels). Discarded importing the **full Structured MADR** schema (risk
  assessment, audit sections, JSON Schema, GitHub Action validator) as mandatory — that is tooling from an ADR
  extension, not the `docs/` surface that the method labels; the header stays **minimal** (audience + authority
  + 3 provenance fields). Discarded prescribing the **`.claude/rules/ paths:`** mechanism as the home of the
  label — the research confirms it has documented edge cases (`paths:` documented as failing in various configs,
  only `globs:` loads reliably; does not trigger on `Write`, only on `Read`; ignored in `~/.claude/rules/`);
  it serves as a **conceptual precedent** (select context by file scope), not as an implementation to copy.
  Discarded **making the per-file label mandatory for every doc** — it can stay at the **folder** level (a
  `README`/index labels the entire homogeneous section); the 2b only signals when **neither** the doc **nor**
  the section has a label (avoids noise in repos with uniform sections). Discarded **writing the labels into
  the skeletons** of each section (`arquitetura/INDICE.md` etc.) now — that is payload authoring; the template
  **requires** them and `docs-front.md` **models** them, the application stays outside the single round.
- **Next candidate:** "Human-nature material without ingesting binary noise (sidecar/extract)" (next facet
  of the docs topic — **how** to populate the `audience: human` slot from R13/R14: text extract/sidecar `.md`
  alongside the binary, inheriting the provenance label, for the LLM to consume without loading the `.pdf`/`.pptx`)
  or "Cross-repo portability of the `docs/` baseline (deterministic installation/adaptation)" (making the
  taxonomy + labels installable/adaptable in a repeatable way across repos).

### Round 13 — 2026-06-29 · boundary: Standard segmentation taxonomy for `docs/` (portable baseline across repos)

- **Change:** skeleton-payload [assets/docs/README.md](../../plugins/claude-quenching/skills/quenching-management/assets/docs/README.md) created — the
  **recommended starting taxonomy** for `docs/`, **portable across repositories** — and sharpened
  **dimension 2** in `dimensions-template.md` (What good looks like · smells · remediation · payload) with a
  new cross-cutting block **2b** in `detection-and-smells.md`. Until R12 the method **derived the `docs/`
  structure ad-hoc per repo** (Step 0 finds where each layer lives, but there was no **recommended baseline**
  nor pre-defined boundaries between the sections) and the package carried **disconnected** skeletons
  (`arquitetura/INDICE.md`, `VISION.md`, `backlog/`, `adr/`) without a top-level that united them. The
  evolution provides a **`docs/` skeleton** with **named and stable homes**: table of the five technical
  layers already audited (`arquitetura/`=current reference/dim 2 · `adr/`=explanation/dim 5 · `VISION`=
  direction/dim 3 · `backlog/`=pending how-to/dim 4 · `catalogo_dados/`/`dominio/`=domain reference/dim 11,
  each mapped to its Diátaxis type and to its dimension) **plus a named slot for human-nature material**
  (`apresentacoes/`/`diagramas/`/`normativos/`: slides, source diagrams, regulatory PDFs) — input that
  **belongs in `docs/`** but **not** in the normative layer (it is not "as it is today" versioned in
  markdown). The "What good looks like" for dim 2 incorporates the baseline as **completeness of what
  applies** (derive-before-scanning; *does the repo cover the sections that fit it?*, without forcing a
  section that does not apply), makes explicit that **the repo's convention wins** when it already exists
  (Step 1 adapts the names), and anchors the **README (humans) × CLAUDE.md/AGENTS.md (agents)** separation
  as the same boundary (dim 12) applied to the top of the repo. New smells: **`docs/` without baseline
  segmentation** (technical markdown loose at the root, the agent must scan everything) and **human material
  leaking into the technical layer** (human binary in `arquitetura/` or at the root, without a slot, polluting
  the current reference). Block **2b** brings greps that **only list candidates** (missing baseline sections
  via the Step 0 variables · loose technical `.md` at the `docs/` root · human binary — `.pdf/.pptx/.drawio/.png/.svg` —
  outside the slot) + the read "named homes or loose markdown?". Conceptual diff: dim 2 stops being "index in
  sync + one standard per file" (scope of **one** layer) and gains a **pre-defined and portable top-level
  `docs/` taxonomy** (scope of **all** layers + the human slot) — opening the docs surface beyond technical
  documentation, for common use by **humans and LLMs**. `assets/README.md` inventory updated. SKILL.md
  untouched (dim 2 and detection are `references/`); 15 dimensions maintained.
- **Why:** explicit user direction — the method's focus shifts to the **`docs/` structure**, with
  segmentations that are **clearer, pre-defined, and standardizable ACROSS REPOSITORIES** (a recommended
  baseline/taxonomy, not derived ad-hoc) and **broader than today** (today only technical docs: architecture/
  vision/backlog/adr/domain), because real projects carry human-nature input (presentations, diagrams,
  regulatory PDFs) that needs a predictable home. That was the structural gap: the method already had the
  **layers** (dimensions 2-5, 11) and the **boundary doctrine** (dim 12), but no **recommended top-level form**
  that positioned them in a stable and portable way — each application re-invented the tree. This round is the
  **taxonomy/baseline**; the distinct facets of the same topic (human×LLM audience with provenance frontmatter;
  how to populate the human slot without binary noise; deterministic cross-repo installation) are left for the
  following rounds — **not** anticipated here (the slot is only named).
- **Sources:** [AGENTS.md — agents.md](https://agents.md/) (accessed 2026-06-29, ✅ verified by
  WebFetch) — **verbatim** *"README.md files are for humans: quick starts, project descriptions, and
  contribution guidelines"* and *"AGENTS.md complements this by containing the extra, sometimes
  detailed context coding agents need… that might clutter a README or aren't relevant to human
  contributors"* (human × agent separation = the boundary at the top of the repo); *"Agents automatically
  read the nearest file in the directory tree, so the closest one takes precedence"* (proximity precedence,
  portable); under the **Agentic AI Foundation / Linux Foundation** since Dec/2025, 60,000+ adopting
  repos (cross-repo baseline, not ad-hoc). [Diátaxis — A systematic framework for technical
  documentation](https://diataxis.fr/) (accessed 2026-06-29, ✅ verified by WebFetch) — *"Diátaxis
  identifies four distinct needs, and four corresponding forms of documentation — tutorials, how-to
  guides, technical reference and explanation"* and *"documentation should itself be organised around
  the structures of those needs"* (organize `docs/` by type/purpose = named homes); the premise
  that mixing quadrants is the root cause of useless docs (*"There isn't one thing called
  documentation, there are four"* — Divio). [Set up Claude Code in a monorepo or large codebase —
  Claude Code Docs](https://code.claude.com/docs/en/large-codebases) (accessed 2026-06-29 via
  WebSearch) — hierarchical CLAUDE.md by directory level + `.claude/rules/` with `paths` in
  the frontmatter (segmentation by scope). Catalog: `research/12-knowledge-architecture-external.md`
  (Diátaxis/Divio: one purpose per file; docs-as-code/single-source-of-truth; 3-layer architecture
  hot/skills/cold; AGENTS.md README-humans × agents; **10 sources confirmed** in the anti-hallucination
  verification).
- **Rejected/superseded:** discarded **creating a new dimension** "docs structure" — it is a sharpening of
  existing dim 2 (normative reference **is** a section of the larger taxonomy); the axis enters the "What
  good looks like" of dim 2 + block **2b** (as with 1b/6b/7b/8b/9b/14b), maintaining 15 dimensions (Simplicity
  First). Discarded **detailing the consumption of human material** (sidecar/text extract, provenance
  frontmatter, how the LLM reads PDF/slide without ingesting the binary) — it is a distinct facet of the same
  topic, reserved for the next rounds; anticipating it would dilute the single evolution and violate the
  direction (this round **only names** the slot). Discarded **writing the skeletons for each human subfolder**
  (`apresentacoes/README.md` etc.) now — that is payload authoring; the baseline **names** them, the authoring
  stays outside the single round. Discarded importing the **L1/L2/L3 thresholds** from `ceaksan.com` (single
  `architecture.md` by project size) — the catalog verification note marks the numbers as `mischaracterized`
  (50 vs 30 files for L1); the baseline uses **homes by purpose** (Diátaxis/AGENTS.md, confirmed), not a
  file count. Discarded the **rebuild test** (SDD) as the completeness criterion for this round — the catalog
  marks the attribution of the technique as `mischaracterized` (belongs to Augment Code, not the cited paper);
  it stays for the candidate "Completeness of the normative reference / rebuild test", reopened with the
  correct source. Discarded **forcing** all sections as mandatory — the baseline is completeness **of what
  applies** (a repo without data does not need `catalogo_dados/`), not a blind checklist (the repo's
  convention wins).
- **Next candidate:** "Segmentation of `docs/` by audience (human × LLM) with provenance frontmatter"
  (next facet of the docs topic — per-file label: primary audience + origin/date/maintainer, for the agent
  to know what to consume × what is human-only) or "Human-nature material without ingesting binary noise
  (sidecar/extract)" (next facet — how to populate the slot named in R13 for agent consumption).
