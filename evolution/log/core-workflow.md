# Method core + evolution workflow

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **the base skeleton, the application workflow (Steps 1-N), and the self-evaluation cycle (eval of the audit itself) — cross-cutting all dimensions**. It also stores **structural refactors** (premise changes that apply to all rounds and do not consume `current-round`).

## Structural refactors (premise — do not consume `current-round`)

### 2026-06-28 · self-contained / portable

> This is not an evolution round (does not consume `current-round`); it is a
> **premise** change that applies to all future rounds. Recorded here because
> it redefines what the method is.

- **What:** the method stopped being an **auditor that delegates** to skills/agents
  that needed to **pre-exist in this repo** (coupled) and became a **self-contained
  and portable installer**: it carries all the artifacts it creates in
  [../assets/](../../plugins/claude-quenching/skills/quenching-management/assets/) (5 skill-templates `knowledge-*`, sub-agents
  `auditor-`/`quenching-evolutionist`, CLAUDE.md hooks, doc skeletons,
  frontmatter templates) and **installs** them in the target repo, adapting to the
  derived shape.
- **Decoupling:** removed all references to paths in this repo
  (`docs/arquitetura/`, `docs/VISION.md`, `safra`, «Python defines YAML» →
  generalized) and to external skills (`sync-claude-md`, `docs-backlog`,
  `skills-skill-creator`, `update-config`, `karpathy-guidelines`, etc. → each
  capability became a `knowledge-*` payload in the package). `references/delegation.md`
  → `references/installation.md` (gap → payload + **deprecation** doctrine for
  what the repo already had). Detection (`detection-and-smells.md`) gained **Step 0** which
  **derives** the target's paths instead of assuming them.
- **Model:** *pure installer* — the package payload is the **single source of truth**; when
  the repo already has an equivalent, the method **installs the one from the package** and **marks the
  pre-existing one as deprecatable** (never removes without OK).
- **Invariant for the evolutionist:** every future round preserves
  self-containment and portability; the content sharpened across dimensions (R0-R6)
  remains — only the "Owner" field became "Payload".

### 2026-06-29 · log by context + reviewer agent

> Premise change about **how the method maintains itself**: the monolithic log
> `EVOLUTION.md` (>1,500 lines) was split into a **spine/index** + **one file
> per context** (this `evolution/` folder), and the evolution cycle gained a
> **second agent**.

- **What:** the verbose detail of rounds was moved out of `EVOLUTION.md` and routed by
  dimension/theme to `evolution/<context>.md` (map in [README.md](README.md)). The
  spine [../README.md](../README.md) was left with only the anchor state, the exclusion
  index (one line per round), the advancement backlog, and the **review queue**.
- **Second agent:** in addition to the `quenching-evolutionist` (advances the frontier),
  the package now carries the `quenching-reviewer` (critiques and refines what was already done).
  Introduces the `Rev*` ID and the `last-revision` anchor; the reviewer does **not** increment
  `current-round`.
- **Why:** the single file was growing fast and becoming difficult to read and
  **revisit**; and there was no first-class path to return to a definition and improve it
  (only the evolutionist's `supersedes Round N` hatch). The split applies the method itself
  (smallest high-signal set + just-in-time retrieval) and the reviewer closes the
  critique↔advancement cycle.

## Current state

> Current summary of each frontier in this dimension (what is in effect today). The detail and rationale are in the history below.

- **R0 · initial skeleton** — 14 dimensions, audit+apply-with-confirmation workflow,
  delegation map, report format, self-evolving agent. (base state)

- **R34 · Eval of PRESCRIPTION (planted profile → expected emphasis), not just detection** — **EXTENDS R12**
  (does not redo it). Through R33 the «Eval of the audit itself» section (R12) only covered **DETECTION** — a fixture with
  a **planted gap** → signaled in the right dimension, false-negative as the key metric. The fit-to-repo layer (R29-R32)
  introduced a **different** output type: a **RECOMMENDATION/PRESCRIPTION of method**
  (the emphasis of the «For THIS repo, invest first in…» block, the roadmap order). A **wrong** recommendation is a
  failure mode the detection harness **does not measure** — a repo with a marked shape (e.g., MLOps) can receive
  **flat** or **biased** emphasis and no fixture would catch it. R34 extends the eval doctrine with the **prescription
  dimension**, in the same fixture form (planted **profile** → **expected** emphasis as ground truth — *«each
  evaluation prompt should be paired with a verifiable response or outcome»*): two new measures mirroring
  detection — **prescription-hit** (did the recommended emphasis match the planted profile, anchored in a
  `file:line` trigger?) and **prescription-false-negative** (flat emphasis on a repo with a marked shape — the most
  important one, mirroring «false-negative > false-positive»; it is the R29 smell turned into a metric). **Profile
  fixtures designed** (5, alongside the detection ones in [../research/14-eval-fixtures.md](../research/14-eval-fixtures.md)):
  `pre-mlops-marked` (→ dim 8/14; dim 3/10 only «propose the home»), `pre-greenfield-empty` (→ the base-Order of the
  roadmap), `pre-lib-pure` (→ lean dim 1 + dim 2 + dim 6), `pre-monorepo` (→ dim 1 per-directory + fan-out +
  plugin), `pre-form-ambiguous` (→ **flat emphasis is CORRECT**). **Dual poka-yoke:** (a) tests **METHOD, never
  CONTENT** (no ground truth for VISION/memory — Step 6/Rev5 boundary); (b) **ambiguous shape → flat emphasis
  is a HIT, not a false-negative** — strong emphasis there is the **prescription-false-positive** (over-prescription,
  mirrors Rev7/«overreliance on certain contexts»). **Bash measurement PENDING** (design, like R22-R29). 15
  dimensions; **no new payload**; no MEASURED detection rule changed (the eval doctrine is not surface grep)
  → harness does not run in this round. SKILL.md ~408 (<500). (round 34 · **reviewed-by: Rev8** —
  fit-to-repo layer coherence capstone R29-R34: audited end-to-end and cohesive; only finding closed — the
  closure of the DETECTION subsection pointed only to the `research/` directory, now points to the concrete catalog
  `14-eval-fixtures.md` that R34 established as the shared home for detection + prescription, symmetric with the
  prescription subsection)

- **R32 · Loop in the target that RE-MODULATES emphasis/profile by cadence (the profile is alive)** — **extends** trigger
  (2) of Step 8 (R17 — model/cadence release) to **close the PROFILE axis** that R29/R30/R31 opened. Through
  R31, Step 8 only handled the **CONTENT** freshness of the base (what rots is the rule/instruction); the EMPHASIS
  derived from the profile (Step 4, R29) and the roadmap ORDER (R31) remained **static** — nothing triggered their
  re-derivation when the repo's shape changed. R32 records the **doctrine that emphasis/profile IS PART of what
  rots** (*context rot* from dim 1 applied to prioritization, not just to the base): **the profile of a repo is ALIVE** —
  greenfield→mature, lib→service, data-pipeline→MLOps —, so the recommended emphasis and roadmap sequence
  **stop fitting** when the repo evolves. Trigger (2) now **re-runs the profile derivation (Step 1) +
  emphasis modulation (Step 4) + roadmap (R31)** against the current state, delivering *«given how the repo
  has evolved since the last audit, now invest in…»* — this is how the skill provides "context on how the repo
  can evolve". **NO new payload:** the R31 `quenching-roadmap`, being **read-only and re-runnable**, is already
  the instrument to **re-sequence** on each release — simply **re-invoke it** with the current shape (one line in its
  «What this skill is» records that). **Respects the limit (Rev5):** re-modulating EMPHASIS/order re-prioritizes *which
  dimensions/payloads* to invest in, **never** rewrites content (VISION/memory; only Step 6 proposes the home).
  **EXTENDS** R17 (does not redo it) and **completes** the R29/R30/R31 profile axis. 15 dimensions maintained; no
  detection rule changed → harness does not run. SKILL.md ~366 (<500). (round 32)

- **R31 · Sequenced adoption roadmap payload (`quenching-roadmap`)** — materializes the **other half**
  of the candidate that R29/R30 left open: through R30 the method had the *method* of modulating emphasis (Step 4) +
  the profile catalog (R30), but the package **did not carry an artifact** that produced, for the target, a **sequenced and
  actionable roadmap**. R31 creates the payload [../assets/skills/quenching-roadmap/SKILL.md](../../plugins/claude-quenching/skills/quenching-management/assets/skills/quenching-roadmap/SKILL.md)
  — an **orchestrating, read-only, and propositional** skill-template that reads the **derived shape** (Step 1) + the **profile**
  ([../references/repo-profiles.md](../../plugins/claude-quenching/skills/quenching-management/references/repo-profiles.md)) + the report **scoreboard** and **PRODUCES** a
  roadmap in **waves** ("invest first in X, **then** Y, **then** Z"), ordered by **leverage ×
  cost × prerequisite** (map/dim 1 + boundaries/dim 12 before hooks; boundaries before skills that
  cite them; **observed trigger** before payload). Shape copied from the existing pair orchestrator (`quenching-standards`)
  + read-only-with-fork (`quenching-reaudit`): frontmatter `context: fork` + `agent: quenching-auditor`
  (reuses the R9 auditor, does **not** create a new sub-agent — Simplicity First) + `allowed-tools: Read, Grep,
  Glob, Bash`; **auto-trigger by description** because it is read-only (R18/R8 doctrine — read-only is born as a skill with
  trigger; if it gains a side effect, then `disable-model-invocation: true`). **CRUCIAL — proposes the ORDER, NEVER
  the CONTENT:** sequences *which method artifacts/triggers* to install first, never *what* the VISION/
  memory/boundary should say (limit that Rev5 just protected) — the «boundary» section and «Guardrails» of the
  payload record that explicitly, and dim 3/10/12 are included only as «propose the home» (Step 6). **Roadmap is a PROPOSAL:**
  read-only, does not install — installation follows item-by-item with OK (Steps 5-7, operation model). It is an **installation DAG**
  (prerequisite edges between waves), not a flat list. Propagated to three minimum points:
  `installation.md` (gap→payload line: "does not know where to start / in what order"), `assets/README.md`
  (inventory) and **short pointer** in Step 4 of SKILL.md (after the mention of `repo-profiles.md`, linking the
  «invest first in…» block to the payload that sequences it). **No new dimension** (it is a workflow payload, not an artifact
  to audit — 15 maintained); **no detection rule changed** → harness does not run. SKILL.md ~352 lines (<500).
  **Does not supersede** previous round — **completes** R30 (the payload part it reserved). **Pre-existing `docs-*`/`knowledge-*`
  in the repo NOT deprecated** (no equivalent: no skill in the repo produces a sequenced adoption roadmap for the method). (round 31 · **reviewed-by: Rev6** — the «Canonical base-Order» of the adoption sequence,
  which had been re-written in three homes — roadmap payload, greenfield profile, and Step 4 — and was already diverging in
  the foundation description, became the **single home** in the base-Order of `quenching-roadmap`; the other two points
  now **point** to it instead of repeating it, killing the drift)

- **R30 · Lightweight and non-closed taxonomy of repo profiles (catalog of signals → emphasis)** — **formalizes** what
  R29 left as loose examples: creates [../references/repo-profiles.md](../../plugins/claude-quenching/skills/quenching-management/references/repo-profiles.md), a
  **named catalog** of archetypes that Step 4 consults when modulating emphasis (MLOps/model-heavy ·
  data-pipeline/ETL · library/SDK · runtime service/app · monorepo/large codebase · multi-contributor
  cross-tool · mature `.claude/` · greenfield/repo from scratch). Each profile = **observable signals in Step 1**
  (file/structure/dependency) → **EMPHASES** (which dimensions and which Step 8 triggers matter most).
  **CRUCIAL — free examples guide, not an enum** (R29 already rejected closed enum): a repo matches **several
  profiles or none** (emphases **sum**), it is a prioritization heuristic, **never a gate** — full scoreboard coverage
  intact. The catalog **reuses** the profile signals that R29 already had Step 1 note (invents no new observation). **Short**
  pointer from Step 4 + References list in SKILL.md (slim maintained) + note in `report-format.md`. Explicit boundary recorded
  in the file itself: does NOT become dim 16/knob, does NOT decide content (only weighs which METHOD dimension to invest in),
  does NOT filter the scoreboard, and — distinct from the `docs/` taxonomy — does NOT prescribe names to the repo (profiles are
  examples, not canonical names). **No new payload**
  (the sequenced **roadmap payload** is reserved for R31, deliberately NOT built here to avoid
  collision); no detection rule changed → harness does not run. Possible future smell ("report without emphasis
  in a repo with a marked profile", already recorded by R29) remains PENDING measurement. (round 30 ·
  **reviewed-by: Rev5** — narrowed the MLOps profile emphasis to not prescribe content: dim 3/10
  were removed from the «invest in» list, the dense direction/memory of a model repo only weighs **proposing the home** via Step 6,
  eliminating the contradiction with the catalog's own «Boundary»; SKILL.md/report-format.md audited
  and intact)

- **R29 · Emphasis prescription guided by repo profile (fit-to-repo guidance)** — the **report**
  (Step 4) stops confronting EVERY repo with all 15 dimensions at **uniform weight** and starts **modulating the
  emphasis** by the **profile derived** in Step 1 (shape + need). Step 4 gains the subsection
  **«Emphasis modulation by repo profile»** + a **profile-weight** in the priority formula
  (severity × cost × ready-payload **× profile-weight**), materialized in `report-format.md` as the
  section **«For THIS repo, invest first in…»** (2-4 dimensions/triggers/payloads of highest leverage, each
  one **anchored in an observed trigger** — `file:line`/fact from Step 1). Profile signals → emphasis
  (examples, not exhaustive): monorepo/large codebase → dim 1 + fan-out + rollout plugin; populated
  `.claude/` surface → dims 6/7/8 (R10/R4/R26) rise, repo from scratch → dim 1 + dim 2 first and hooks **after**
  (*«start with CLAUDE.md»*); many external services → dim 15; PRs/conventions in flux → trigger (1)
  of Step 8 + dim 14; repo from scratch → emphasis becomes the **installation sequence** (map+boundaries first).
  **IT IS PROPOSING/PRIORITIZING about the METHOD ITSELF (probabilistic guidance: which dimension/trigger/payload to invest in),
  NOT imposing content nor deciding the repo's direction** — the profile-weight **reorders** but **does not hide** a dimension
  from the scoreboard (full coverage intact), **does not invent** a gap (it comes from the Step 3 evidence) and **does not
  decide** what the repo's memory/VISION/boundary should say (that follows only in Step 6). **Modulating the method's emphasis ≠ defining the repo's content**
  (the boundary the limit prohibits): "for you, it is more valuable to sharpen dim 6" (method) × "your VISION is X" (content)
  — only the first is the method's work; the recommendation is **always** anchored in an **observed** trigger, never in the
  curator's preference. SKILL.md ~310 lines (<500); 15
  dimensions maintained; **no new payload** (it is workflow/report doctrine); **no detection rule changed**
  (greps/smells/«good» criteria intact) → harness does not run. **Distinct** from R17 (which LISTS the 3 loop triggers
  without weighting which matter most per repo) and from the Outgrowth/Plugin backlog (R29 prioritizes the diagnostic emphasis;
  those are specific pruning/distribution mechanisms). (round 29)

- **R28 · Orchestration contract of the cycle's links (hook → command → sub-agent → skill)** — closes
  Step 8 (R17) **end-to-end**: through R27 the PARTS of the cycle existed in isolation (loop R17; composable command payload R18/R27;
  5 hook payloads R19-R25; wiring R26), but the **doctrine of how they COMPOSE into a running flow** was missing.
  Step 8 of `SKILL.md` gains the subsection **«Orchestration contract of the links»** which names the **contract per link** —
  **dim 6 applied to the RUNNING FLOW** (not to the static home choice of authorship, which is R6) and the
  *workflow (predefined code path) × agent (the LLM drives)* boundary applied to maintenance: **hook**
  = automatic trigger that OBSERVES/PROPOSES/at-most-BLOCKS,
  **never mutates the base on its own** (propose ≠ apply; consistent with "the method never writes memory nor decides
  the direction" from Step 6; only PreToolUse/R25 *decides*, and only about generated content); **command/skill**
  = on-demand step that **APPLIES, with OK** (item-by-item, the link that closes what the hook only proposed; can be triggered by
  the model via R27 composability); **sub-agent** = isolated context that returns a **CONDENSED SUMMARY**
  (*«the subagent does that work in its own context and returns only the summary»*, R9, never a dump). The
  **anti-pattern = chaining too much** (hook → command → cascade of sub-agents **without a human barrier**) under
  Simplicity First, with **dual barrier**: human (the link that mutates always has OK) and **deterministic** (the
  runtime caps recursion — *«a subagent at depth five… can't spawn further. The limit is fixed»*),
  distinguishing enforcement (deterministic) × guidance (probabilistic) of dims 1/8/14. Closes the cycle:
  automatic freshness = hooks that OBSERVE/PROPOSE; re-examination = composable command + sub-agent in clean context;
  **base evolution = only in the link with confirmation**. **Distinct from R6** (STATIC home choice at authorship)
  and from **R17** (the loop spine — *which* triggers, in *which* home): R28 is the **composition contract at RUNTIME**
  that connects the parts. SKILL.md ~286 lines (<500); 15 dimensions maintained; **no new payload** (it is workflow doctrine); no detection rule changed (harness does not run). (round 28)

- **R17 · Recurring maintenance cycle as a first-class operational workflow** — the **application
  workflow** gains **Step 8 "Establish the recurring maintenance cycle (the base is alive)"**:
  auditing once (Steps 1-7) leaves the base fresh **today**, but it rots (*context rot*) with
  code/model/team changes. The method now **installs the recurring operational loop** that keeps it
  fresh, with **three documented triggers** (drift-event × cadence) and the **right home** for
  each (dim 12 applied to maintenance): (1) **by event, on PR** — treat CLAUDE.md/docs edits
  like any doc change (PR hook that re-runs detection on the touched scope and **proposes**, does not
  block — dim 8 + dim 14; recurring backlog item of the target's dim 4). (2) **By cadence, on
  model release** — revisit instructions that became overhead with a newer model (crosses
  *outgrowth detection* + dim 1 pruning). (3) **On demand, by command** — a `/<re-audit>` that
  re-runs Steps 1-7 (or the argument's scope) and delegates to the **auditor sub-agent in clean context**
  for large repos; being a manual-work shortcut (not a side effect), it is born as a **skill** (dim 9), not
  a legacy command. **Automatic freshness** between audits = **evolutionary Stop hook** (dim 8) + OTel
  telemetry `skill_activated`/`invocation_trigger` (skill never triggered = deprecation candidate, dim 6). The section is
  the **cycle spine**: defines **when/why/in which home** each trigger runs; the **concrete payloads**
  (PR hook, `/<re-audit>` command, ready Stop hook) are installable via Steps
  5-7 and mature in subsequent rounds. No new payload in this round (it is workflow doctrine);
  **does not** touch any detection rule (does not run the harness). Crosses core + dim 8/9 (transforms the
  detection-only of R7/R8 into an operational cycle). **Supersedes the R8 rejection** ("discarded the quarterly
  `/insights`→`/audit-claude-md` loop as a method step") — R8 was right not to put a
  concrete step in that round, but the axis was the right boundary; now it enters as a cycle doctrine
  anchored in the official source. (round 17)

- **R12 · Agent-guided evaluation cycle (eval of the audit itself)** — the method's **evolution
  workflow** (the "Method evolution" section of `SKILL.md`) gains the step **"Eval of the audit itself"**:
  the method **is an agent tool**, and agent tools are evaluated against
  **realistic tasks**, not by inspection. Before closing a round that changes a detection rule
  (smell/grep/«good» criterion), the evolutionist runs a **minimal harness of 3-5
  fixtures** — small sample repos each with a **known planted gap** (repo without
  CLAUDE.md · skill without frontmatter · ADR implemented but not removed · two overlapping-scope skills · boundary
  dimension without a single home) — and measures **three** things (not just pass/fail):
  **hit rate by dimension** (was the planted gap signaled in the right dimension, with
  `file:line`?), **false-negative rate** — the metric that matters most: did any real gap
  slip through? (worse than a false-positive: the base looks audited and is not) — and **token cost per dimension**
  (dimension consuming too much → push to the auditor sub-agent). The **reading of the
  numbers** (not the impression) decides whether the new rule added signal or just noise/cost; the test of a
  new rule is "catches the planted gap **without** triggering on clean fixtures". Fixtures and measures live in
  `research/`; **applying to a real repo (Steps 1-7) does NOT run the harness** — it belongs only to
  *skill development*. No new payload (it is workflow doctrine, not an installable artifact).
  **Supersedes the R0 rejection** ("discarded creating `evals/` now — qualitative output, no verifiable criterion"):
  the official source now **gives** the verifiable criterion (realistic tasks + runtime/tool-calls/tokens/errors metrics +
  false-negative as missed-fire), and the harness stays minimal
  (no heavy `evals/` folder). Core of the method (eval of the curator itself); fixture authorship
  is future development work, outside the round. (round 12)

## Round and revision history

> Most recent rounds at the top. Revisions (`Rev*`) appear here under the round they refine.

### Round 34 — 2026-06-29 · frontier: Eval of PRESCRIPTION (planted profile → expected emphasis), not just detection · **reviewed-by: Rev8**

- **Change:** the **«Eval of the audit itself»** section of `SKILL.md` gained the subsection **«Eval of PRESCRIPTION
  (not just detection)»** (~25 lines) + a new fixtures file
  [../research/14-eval-fixtures.md](../research/14-eval-fixtures.md). Through R33, the R12 harness only
  measured **DETECTION**: fixture with **planted gap** → signaled in the right dimension, with **false-negative**
  as the key metric. The *fit-to-repo* layer (R29 modulates emphasis; R30 names profiles; R31 sequences the roadmap;
  R32 re-modulates by cadence; R33 proposes domain artifact) introduced a **different** output type — a
  **METHOD RECOMMENDATION** (the emphasis of the «For THIS repo, invest first in…» block; the roadmap order) —
  that the detection harness **does not evaluate**. R34 extends the eval concept to treat **prescription as detection is treated**:
  a **planted PROFILE fixture** (marked shape — MLOps · greenfield · lib · monorepo)
  carries the **EXPECTED emphasis/roadmap** as ground truth, and the test is whether the method **recommends the expected result**.
  **Two new measures**, mirroring detection: **prescription-hit** (did the recommended emphasis match the
  planted profile, anchored in a `file:line` trigger?) and **prescription-false-negative** (flat **emphasis**
  on a **marked-shape** repo — the most important one, mirroring «false-negative > false-positive» from detection;
  it is the R29 smell «flat emphasis on a marked-shape repo» **turned into a metric**). **Five profile fixtures
  designed** in `14-eval-fixtures.md` (which also gives a **concrete home** to R12's detection fixtures, previously
  only described in prose): `pre-mlops-marked` (ml/pins/slices signals → expected emphasis dim 8/14; dim 3/10 only
  «propose the home», consistent with Rev5), `pre-greenfield-empty` (no `.claude/` → the **base-Order** of
  `quenching-roadmap`, foundation before hooks), `pre-lib-pure` (`src-layout`/API → lean dim 1 + dim 2 +
  dim 6), `pre-monorepo` (multiple packages → dim 1 per-directory + fan-out + plugin) and
  `pre-form-ambiguous` (neutral shape → **flat emphasis is the expected result**). **Conceptual diff:** R12 gave the eval of
  DETECTION (gap → finding); R34 gives the eval of PRESCRIPTION (profile → recommendation), with the same fixture format
  (realistic input **paired with a verifiable expected result**). **Bash measurement PENDING** — harness design,
  consistent with R22/R23/R25/R26/R27/R28/R29. SKILL.md ~408 lines (<500); 15 dimensions; **no new payload**
  (it is evolution workflow doctrine, not an artifact to audit); **no MEASURED detection rule changed by
  grep** (the eval doctrine is not a surface regex) → the detection harness does not run in this round.
- **Why:** it was the **evaluation gap** of the fit-to-repo layer. R29-R33 made the method **RECOMMEND** (not just
  detect): modulate emphasis, name profiles, sequence the roadmap, propose domain artifact — but the only quantitative
  feedback loop of the method (R12) only knew how to measure whether the **gap** was found. A **wrong** emphasis (an
  MLOps repo coming out with flat emphasis, or a neutral repo receiving aggressive prescription) **would pass without any
  fixture catching it** — exactly the type of silent regression that R12 combats in detection («the base looks
  audited and is not»), now applied to recommendation («the recommendation looks made and is not»). The
  official source gives the fixture form directly: *«Each evaluation prompt should be paired with a verifiable response
  or outcome»* + *«Your verifier can be as simple as an exact string comparison between ground truth and sampled
  responses»* — that is, a fixture is a **realistic input paired with the expected result**, and this holds
  for prescription (planted profile → expected emphasis) just as well as for detection (planted gap → expected
  finding). The **poka-yoke** comes from the same source and from R29/Rev7: the fixture tests only the **method
  recommendation** (there is no content ground truth — Step 6/Rev5 limit), and **ambiguous shape → flat emphasis is a HIT**; without the
  `pre-form-ambiguous` fixture, the harness would reward always-prescribing (over-prescription), the opposite of the care of
  Rev7 against skill-spam — *«watch for unexpected trajectories or overreliance on certain contexts»*.
- **Sources:** [Writing effective tools for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim** *«Each evaluation prompt should be paired with a
  verifiable response or outcome»* and *«Your verifier can be as simple as an exact string comparison between
  ground truth and sampled responses»* (anchors: fixture = realistic input **paired with a verifiable expected result**
  — holds for prescription just like detection; it is the SAME source as R12, now extended with the
  *paired verifiable outcome* sentence that R12 had not cited) + *«Prompts should be inspired by real-world uses and be
  based on realistic data sources and services»* (profile fixtures are repos of realistic shape).
  [Equipping agents for the real world with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim** *«Identify specific gaps in your agents' capabilities by
  running them on representative tasks»* + *«iterate based on observations: watch for unexpected trajectories or
  overreliance on certain contexts»* (anchors the poka-yoke against over-prescription: ambiguous shape → flat emphasis is
  correct, strong emphasis is the *overreliance*). Both were already the sources of R12 — R34 **reuses** and sharpens the
  reading (does not supersede R12).
- **Rejected/superseded:** discarded **running the measurement now** — no Bash in context; the harness remains in
  **design/PENDING**, like the entire R22-R29 series. Discarded **transforming the profile into a rigid evaluable GATE**
  (exact match/fixed emphasis order) — repo-profiles.md mandates **summing** emphases of matching profiles, so the
  verifier checks **contains the expected**, not **equal to the expected** (an exact match would fail a
  correct recommendation that cites one extra item; and would harden the profile into something that R29/R30 explicitly kept as
  **free examples, not an enum**). Discarded **testing CONTENT** (ground truth of VISION/memory) — it is the limit that
  Rev5 protected; the fixture only has **method** ground truth (which dimension/payload). Discarded **creating a
  dimension 16 «eval»** — it is doctrine of the **evolution workflow** (the «Method evolution» section of SKILL.md), not
  an artifact to audit in the target repo; 15 dimensions maintained, same home as R12 (dim 12: one purpose → one home).
  Discarded **a new payload** (eval skill/sub-agent) — eval is skill development, not something to install in the target;
  the `quenching-auditor` (R9) is already the scanning agent when the harness runs.
  Discarded **omitting the ambiguous-shape fixture** — without it the harness could not distinguish over-prescription from
  a hit, and would reward always-prescribing. **EXTENDS R12** (does not supersede or redo it): R12 remains the eval of
  detection; R34 adds the prescription axis to the same harness.
- **Next candidate:** «Prescription eval actually run (measure against the 5 profile fixtures when Bash is available)»
  goes in the **Review queue** (not a frontier advancement — it is measuring what R34 designed). Frontier
  advancements still open: «Hook by event applied to `.claude/` (the config surface)», «Outgrowth detection»,
  «AGENTS.md / cross-tool interoperability», «Plugin/internal marketplace as rollout vehicle».

#### Revision Rev8 — 2026-06-29 · CAPSTONE of fit-to-repo layer coherence (R29-R34/Rev5-Rev7) + closes the orphan detection-fixtures pointer — sharpens R34/R12

- **Target:** R34 / the «Eval of the audit itself» section (R12) of `SKILL.md`, **closure of the DETECTION subsection**
  (the line that said where the fixtures live).
- **End-to-end audit (CAPSTONE — 4 axes scanned, finding in only one):**
  1. **Cohesive SKILL.md (411 lines, <500):** Step 4 (R29 modulation + R30 repo-profiles / R31 roadmap pointers) →
     Step 5 (R33 domain artifact) → Step 8 (R32 live profile + R28 orchestration contract) → Eval section
     (R12 detection + R34 prescription) read as **one** method. The Step 4 pointers to `repo-profiles.md`,
     `quenching-roadmap`, and `report-format.md` resolve; the «base-Order» has a single home (Rev6) and the other two
     points defer. **One single asymmetric pointer found** (below).
  2. **Consistent `EVOLUTION.md` spine:** exclusion index lists R29-R34; context index with
     core=R0/R12/R17/R28/R29/R30/R31/R32/R34 + Rev5/Rev6 and dim-06=R4/R10/R33 + Rev7 in the right homes; anchor
     `current-round: 34`/`last-evolution`=R34/`last-revision`=Rev7 correct; backlog removed done candidates
     (taxonomy R30, roadmap payload R31, loop R32, domain artifact R33) and keeps open ones (hook `.claude/`,
     outgrowth, AGENTS.md, plugin/marketplace). **Intact.**
  3. **Method×content limit intact end-to-end:** no point in the new layer (profiles, roadmap, domain
     artifact, eval) reintroduced CONTENT prescription. Rev5 fixed the MLOps profile (dim 3/10 only «propose the home»);
     R31/R32/R33/R34 all repeat the limit (roadmap «proposes the ORDER, never the content»; domain «proposes the skeleton,
     the repo fills it»; eval «tests METHOD, never CONTENT — no VISION/memory ground truth»). **No new breach.**
  4. **Review queue updated:** measurement PENDINGS (flat emphasis smell R29, profile fixtures R34,
     + the older R22/R23/R25/R26/R27/R28) are all recorded as Bash PENDING, **no measurement number invented**.
     Rev7 (R33 smell) recorded as cross-reading, outside the grep list. **Intact.**
- **Critique (orphan/asymmetric pointer — citable evidence):** the **prescription** subsection (R34) points to
  the concrete fixture [../research/14-eval-fixtures.md](../research/14-eval-fixtures.md) (SKILL.md:388-389), and
  the R34 log states that file «also gives a **concrete home** to R12's DETECTION fixtures» — but the
  **detection** subsection (R12) still closed by pointing only to the **directory** `research/` (SKILL.md:358-360), not to the
  file. Confirmed by reading: `research/14-eval-fixtures.md:32-43` contains the table of R12's 5 detection fixtures
  (`det-no-claudemd`/`det-skill-no-frontmatter`/`det-adr-implemented`/`det-skills-overlapping`/
  `det-boundary-two-homes`). Both sides of the same harness cited different homes for fixtures that **live
  in the same file** — a reader of the detection prose would land in a directory, not in the real catalog.
- **Refinement (surgical, 1 line):** the closure of the detection subsection now names the concrete catalog —
  `research/14-eval-fixtures.md` («detection **and** prescription in the same home») — instead of the generic directory,
  closing the asymmetry with the prescription subsection. **Conceptual diff:** generic pointer (directory) →
  concrete pointer (the file that R34 established as the shared home for both fixture types). Does NOT advance
  the frontier; no MEASURED detection rule changed; self-contained invariant preserved (the pointer is internal
  to the package, `research/`).
- **Sources:** none reopened — it is internal coherence (pointer × existing file), not a superseded source.
- **Effect:** the Eval section of SKILL.md is **symmetric** — detection and prescription point to the **same concrete home**
  of fixtures, without the reader of R12's prose landing in a vague directory. The fit-to-repo layer (R29-R34 + Rev5-Rev7)
  is **audited end-to-end and cohesive**; the only seam finding was closed. R34 marked `reviewed-by: Rev8`.

### Round 32 — 2026-06-29 · frontier: Loop in the target that RE-MODULATES emphasis/profile by cadence (the profile is alive)

- **Change:** **trigger (2) of Step 8** of `SKILL.md` («by cadence, on model release») was
  **expanded** to close the PROFILE axis. Through R31 this trigger only mandated revisiting/pruning the **CONTENT** of the base
  (the rule that became overhead with a newer model); the **emphasis** derived from the profile (Step 4, R29) and the **order**
  of the roadmap (R31) remained **static** — nothing triggered their re-derivation when the repo's shape changed. The
  trigger now records the **doctrine that emphasis/profile IS PART of what rots** (*context rot* from dim 1
  applied to **prioritization**, not just to the text of the base): **«the profile of a repo is ALIVE»** (greenfield→mature,
  lib→service, data-pipeline→MLOps), and when the shape changes the recommended emphasis and the roadmap sequence
  **stop fitting**. Therefore the trigger now **re-runs the profile derivation (Step 1) + the emphasis
  modulation (Step 4) + the roadmap (R31)** against the current state — delivering *«given how the repo HAS EVOLVED since
  the last audit, now invest in…»*. **Minimal propagation (1 line):** the payload
  [../assets/skills/quenching-roadmap/SKILL.md](../../plugins/claude-quenching/skills/quenching-management/assets/skills/quenching-roadmap/SKILL.md) gained, in
  the «What this skill is» section, a bullet **«Is RE-RUNNABLE by cadence»** declaring it the instrument to
  re-sequence on each release (read-only ⇒ simply re-invoke it). **Conceptual diff:** R29 gave *how* to modulate
  emphasis, R30 gave the *vocabulary* (profiles), R31 gave the *artifact* (roadmap) — R32 gives the **trigger that RE-RUNS them
  when the repo evolves**, making profile/emphasis part of the maintenance cycle (R17/Step 8), not a
  one-time diagnosis. **No new dimension** (15 maintained); **no new payload** (the `quenching-roadmap`
  is already read-only and re-runnable — Simplicity First mandated extending, not creating); **no detection rule
  changed** → harness does not run. SKILL.md ~366 lines (<500).
- **Why:** it was the candidate **«Loop in the target that RE-MODULATES emphasis by profile»** explicitly reserved
  by R29/R30/R31 (and listed in the spine's backlog). The **meta-gap**: after R29/R30/R31, the method already
  *knew* how to modulate emphasis (Step 4), *named* the profiles (R30), and *carried* the roadmap (R31) — but the profile
  was treated as **static**: derived once, in Step 1, and never re-derived. A repo that was greenfield becomes mature;
  a lib gains a service; a data-pipeline incorporates MLOps — and at that point the recommended emphasis
  and roadmap order **age**, but **nothing re-triggered them**. The user's literal request («the skill
  could provide context on how the repository can evolve») is resolved exactly here: the repo's evolution now
  **re-modulates** the recommendation. The official source gives the principle in two places: (a) *«A few ways
  to keep the files current as the codebase and models change»* + *«Revisit after major model releases:
  instructions that worked around an older model's limitation may become overhead»* — the right setup **changes with
  the shape and the model**, it is not fixed; (b) *«The same triggers tell you when to update what you already have. A
  repeated mistake or a recurring review comment is a CLAUDE.md edit… A workflow you keep tweaking by hand is a
  skill that needs another revision»* — the same triggers that **build** the setup say when to **re-evaluate it**.
  Therefore: the cadence trigger that R17 already had for content applies equally to **emphasis/profile**. **Why
  WITHOUT a new payload (Simplicity First):** the R31 `quenching-roadmap` is **read-only and re-runnable** — it
  reads today's **shape** + profile + scoreboard and produces the order; re-running it on an evolved repo **already**
  re-derives the profile and re-sequences. Creating a «diff mode since the last round» would be a speculative knob (the current shape already
  reflects the evolution; the comparison with the previous audit is the operator's reading, not state to persist in the
  skill). **Why it does NOT violate the method×content limit (that Rev5 protected):** re-modulating EMPHASIS/order
  re-prioritizes *which dimensions/payloads/triggers* to invest in now (probabilistic guidance about the METHOD),
  **never** rewrites VISION/memory — dim 3/10/12 remain only «propose the home» (Step 6). «The repo became a service →
  now dim 15/MCP weighs more» is **method**; «your VISION is now X» would be **content** — only the first is
  the method's work.
- **Sources:** [Set up Claude Code in a monorepo or large codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim**: *«A few ways to keep the files current as the codebase
  and models change»* + *«Revisit after major model releases: instructions that worked around an older model's
  limitation may become overhead once a newer model handles the case on its own. For example, a rule that
  forces single-file refactors can be deleted once the limitation is gone»* (anchors "the setup changes with shape/
  model" and the cadence trigger). [Extend Claude Code (features-overview) — Claude Code Docs](https://code.claude.com/docs/en/features-overview)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim** (*«Build your setup over time»* section): *«The same
  triggers tell you when to update what you already have. A repeated mistake or a recurring review comment is a
  CLAUDE.md edit, not a one-off correction in chat. A workflow you keep tweaking by hand is a skill that needs
  another revision»* (anchors "the same triggers that build the setup say when to re-evaluate it" ⇒ emphasis/roadmap
  are re-evaluable by the same cadence) + the cost of excess (*«Every feature you add consumes
  some of Claude's context… can also add noise»*) that justifies re-prioritizing instead of just accumulating.
- **Rejected/superseded:** discarded **creating a new payload** (or a «diff mode since the last round» in
  `quenching-roadmap`) — the R31 payload is already read-only and re-runnable; re-invoking it with the current shape already
  re-derives the profile and re-sequences. A diff-mode would persist the previous audit's state in the skill (speculative
  knob) with no gain: today's shape is already the reflection of the evolution, and the comparison with the past audit is
  the operator's reading. Discarded **duplicating/redoing the Step 8 loop** — R17 is already the cycle spine and R28 the
  orchestration contract; R32 only **extends** trigger (2) with the profile axis, does not create a trigger nor rewrites the
  section. Discarded **turning profile into persisted state** (e.g., writing the derived profile to a target file to compare) —
  it would become an artifact to maintain that could go stale; on-the-fly **re-derivation** (read-only)
  is cheaper and never lies. Discarded **prescribing content** under the pretext of «the repo evolved, so your
  VISION should say Y» — it is the limit that Rev5 protected; R32 re-prioritizes only the METHOD emphasis. Discarded
  **adding a smell/grep** — no Bash available and the boundary is cadence/prioritization doctrine, not a detection rule; the
  «flat emphasis» smell (R29) remains PENDING in the Queue. Discarded **attacking the candidate «skills/agents
  specific to the repo guided by need»** — reserved for the next advancement round, not touched here.
  **EXTENDS** R17 (does not supersede or redo it); **completes** the R29/R30/R31 profile axis.
- **Next candidate:** «Recommendation of SPECIFIC skills/agents for the repo guided by need» — from
  the derived profile (R30) and the roadmap (R31), the method would suggest **which** niche skills/sub-agents the
  target repo would benefit from HAVING (proposes the NEED for a specific artifact guided by an observed signal,
  does not install the generic ones from the package). Caution about the limit: proposing *what type of method artifact* helps
  (structure) ≠ writing its *content*. **Reserved — not attacked in this round.**

### Round 31 — 2026-06-29 · frontier: Sequenced adoption roadmap payload (`quenching-roadmap`)

- **Change:** created the payload [../assets/skills/quenching-roadmap/SKILL.md](../../plugins/claude-quenching/skills/quenching-management/assets/skills/quenching-roadmap/SKILL.md) —
  an **orchestrating, read-only, and propositional** skill-template that **PRODUCES**, for the target repo, a **SEQUENCED and actionable**
  adoption roadmap of the method ("invest first in X, **then** Y, **then** Z"). Reads three
  inputs — the **derived shape** (Step 1), the **profile** ([../references/repo-profiles.md](../../plugins/claude-quenching/skills/quenching-management/references/repo-profiles.md),
  R30), and the report **scoreboard** — and orders them by **leverage × cost × prerequisite** in **waves**
  (*Now — foundation that unlocks · Then — when the foundation settles · When-the-trigger-appears*). The
  **canonical base-Order** (5 layers, each unlocking the next): (1) map/CLAUDE.md foundation (dim 1) +
  boundaries (dim 12) + standards (dim 2); (2) skills/sub-agents for what repeats (dim 6/7); (3) MCP if there is
  an external system (dim 15); (4) freshness/enforcement hooks **wired** on the already stable base (dim 8/14); (5)
  plugin when a 2nd repo appears. Each roadmap item carries **dimension · package payload · observed trigger
  (`file:line`) · prerequisite** — it is an **installation DAG** (X-before-Y edges), not a flat list.
  **Shape/frontmatter** copied from the existing pair: orchestrator like `quenching-standards` + read-only-
  with-fork like `quenching-reaudit` — `context: fork` + `agent: quenching-auditor` (scans in **clean
  context**, **reusing** the R9 auditor — does not create a new sub-agent, Simplicity First), `allowed-tools:
  Read, Grep, Glob, Bash`, and **auto-trigger by description** (read-only ⇒ born as a skill with trigger, R18/R8 doctrine).
  **Conceptual diff:** R29 gave the *method* of modulating emphasis (the «invest first in…» block), R30 gave
  the *vocabulary* (profile catalog), and R31 gives the **artifact that CARRIES** the ready roadmap for the target — the
  payload half that R30 explicitly reserved. Propagated to 3 minimum points: `installation.md` (gap→payload
  line "does not know where to start/in what order"), `assets/README.md` (inventory) and **short pointer**
  in Step 4 of SKILL.md. **No new dimension** (15 maintained — it is a workflow payload, not an artifact to audit);
  **no detection rule changed** → harness does not run. SKILL.md ~352 lines (<500); detail in the payload
  (progressive disclosure).
- **Why:** it was the **other half** of the candidate «Lightweight profile taxonomy + roadmap payload» that R29 opened
  and R30 split (R30 did the taxonomy; reserved the payload for R31). The **meta-gap**: after R29/R30 the method
  already *knew* how to modulate emphasis and *named* the profiles, but the package **carried nothing that produced, for the
  target, a sequenced roadmap** — the user with a scoreboard full of Absents (greenfield) still had no idea
  **where to start or in what order**. The official source **gives** both the principle (*«you don't need to configure
  everything up front… most teams add them in roughly this order»*, *«start with CLAUDE.md… then add other
  extensions as triggers come up»*) and the **sequence itself** (the *«Build your setup over time»* table:
  trigger → CLAUDE.md → user-invokable skill → skill-playbook → MCP → code intelligence → subagent → hook →
  plugin) and the **cost of installing everything at once** (*«Every feature you add consumes some of Claude's context.
  Too much can fill up your context window, but it can also add noise… skills may not trigger correctly, or
  Claude may lose track of your conventions»*). The roadmap anchors the base-Order in these facts: hooks **last**
  among structural layers (depend on a stable foundation so as not to become noise), MCP only with observed external system,
  plugin only with 2nd repo. **Why it does NOT violate the "installs structure, never content" limit (that Rev5
  just protected):** the roadmap proposes the **ORDER of investment in the METHOD/structure** (which package artifact to install first,
  which trigger to enable first), **never the CONTENT** (does not say what to write in the VISION/
  memory/boundary); the «boundary» section and «Guardrails» of the payload record that explicitly, and dim 3/10/12
  are included only as «propose the home» (Step 6). And **respects the installation doctrine**: roadmap is a **PROPOSAL**
  (read-only, reads-and-proposes), installation continues item-by-item with OK (Steps 5-7) — being propositional, it **maintains
  auto-trigger by description** (R18/R8), and runs in **clean context** (fork on the auditor, R9).
- **Sources:** [Extend Claude Code (features-overview) — Claude Code Docs](https://code.claude.com/docs/en/features-overview)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim** from the *«Build your setup over time»* table: *«You don't
  need to configure everything up front. Each feature has a recognizable trigger, and most teams add them in
  roughly this order»* + the trigger→add sequence (*«Claude gets a convention or command wrong twice → Add it to
  CLAUDE.md»*; *«You paste the same playbook or multi-step procedure into chat for the third time → Capture it
  as a skill»*; *«You keep copying data from a browser tab Claude can't see → Connect that system as an MCP
  server»*; *«A side task floods your conversation with output you won't reference again → Route it through a
  subagent»*; *«You want something to happen every time without asking → Write a hook»*; *«A second repository
  needs the same setup → Package it as a plugin»*); greenfield intro *«New to Claude Code? Start with CLAUDE.md
  for project conventions, then add other extensions as specific triggers come up»*; and the **cost of excess**
  (*«Understand context costs»* section): *«Every feature you add consumes some of Claude's context. Too much can
  fill up your context window, but it can also add noise that makes Claude less effective; skills may not trigger
  correctly, or Claude may lose track of your conventions»*; + the *«Context cost by feature»* table
  (CLAUDE.md costs per request, hook costs zero until returning output, skill costs the description) which anchors the
  **cost** axis of the scoring. Shape/frontmatter copied from existing payloads `quenching-standards` (parallel orchestrator)
  and `quenching-reaudit` (read-only + `context: fork` + `agent: quenching-auditor` + auto-trigger).
- **Rejected/superseded:** discarded **creating a new sub-agent "planner/roadmapper"** — the R9 auditor
  (`quenching-auditor`) already scans in clean context and is the `context: fork` agent; reusing it is Simplicity
  First (do not add a piece to the surface). Discarded **making the roadmap INSTALL** (side effect) — it would become the
  link that mutates the base without OK, violating the operation model (installing is Steps 5-7, with confirmation); keeping it
  **read-only** preserves auto-trigger by description (R18). Discarded **prescribing CONTENT** ("start by writing your VISION like this")
  — it is the limit the user does not cross and that Rev5 protected; the roadmap sequences only
  *which method artifacts/triggers* to install first, and dim 3/10/12 are included only as «propose the home». Discarded
  **rigid/fixed numeric order** (hardcoded weights per dimension) — the sequence is by **prerequisite + observed trigger**,
  not a formula that would mask the why; an observed trigger can move up a layer (e.g.: repo full of generated content → PreToolUse
  enforcement rises). Discarded **a new dimension 16 "roadmap"** — it is a workflow application payload (materializes Step 4/8),
  not an artifact to audit; 15 dimensions maintained. Discarded
  **deprecating a `docs-*`/`knowledge-*` skill from the repo** — there is no equivalent (no skill in the repo produces
  a sequenced adoption roadmap for the method), so no deprecation is forced. Discarded **adding a smell/grep** —
  no Bash available and the boundary is payload/prioritization doctrine, not a detection rule; nothing new in the harness.
  **Does not supersede** previous round — **completes** R30 (the payload part it explicitly reserved).
- **Next candidate:** "Loop in the target that RE-MODULATES emphasis by profile" (cadence/(2) trigger/model
  release in Step 8 re-weights the profile — a rule that became overhead is de-prioritized in the emphasis, not just pruned;
  crosses Outgrowth detection; now with the roadmap as an input to re-sequence); or "skills/agents specific to
  the repo guided by need" — both **reserved, not attacked in this round**.

#### Revision Rev6 — 2026-06-29 · merges the «adoption order» into a single home (the sequence had 3 homes and was already diverging) — sharpens R31

- **Target:** R31 / the **«Canonical base-Order» of adoption** (foundation/CLAUDE.md → skills → MCP → hooks →
  plugin), which R31 recorded in the payload [../assets/skills/quenching-roadmap/SKILL.md](../../plugins/claude-quenching/skills/quenching-management/assets/skills/quenching-roadmap/SKILL.md)
  but which remained **rewritten in independent prose** in two more places: the *greenfield* profile in
  `references/repo-profiles.md` and the «repo from scratch» bullet in Step 4 of `SKILL.md`.
- **Critique (DRY / two-homes + contradiction already materialized, citable evidence):** the same
  adoption sequence lived in **three** homes with its own prose → inevitable drift (axis 1 of the request).
  And the drift **had already begun** in the *foundation*: the roadmap said «map + boundaries (dim 1, 12; **then**
  2)» (`quenching-roadmap/SKILL.md:80`); the greenfield profile said «**dim 1 + dim 2 + dim 12 first**»
  (together, without the «then 2» — `repo-profiles.md:105`); and Step 4 said only «map + boundaries first»
  (omitting dim 2 — `SKILL.md:151`). Three conflicting descriptions of the **same** layer 1 — exactly the
  DRY smell the request asked to kill before moving on.
- **Refinement (conceptual diff — merge into single home + pointers):** I chose the **«base-Order» of
  `quenching-roadmap` as the SINGLE SOURCE** of the sequence (it is the payload that *produces and maintains* the
  re-runnable roadmap of R32 — the natural home). (1) The base-Order gained a header note «**Single home of the
  adoption sequence** — Step 4 and the greenfield profile point here; whoever re-orders a layer edits
  HERE». (2) The **greenfield** profile stopped **rewriting** the sequence: it now only **signals** that this is
  the case where order matters most (scoreboard almost entirely Absent) and **points** to the base-Order; it only preserves
  the rule that does not duplicate any order («do not install hook/MCP/sub-agent without the trigger»). (3) The
  «repo from scratch» bullet in Step 4 stopped asserting a **partial/divergent** foundation composition («map +
  boundaries first», without standards) and now **defers** to the base-Order (which the report already triggers). The
  layer 1 contradiction dies: there is **one** definition of the foundation (1+12, then 2), in the other two places
  only pointers.
- **Boundary roadmap × dim 4 backlog × Step 8 loop (axis 2 — audited, already clear, not touched):** the three
  ideas **do not** overlap and the distinction is already written — *roadmap* = order of **METHOD/structure ADOPTION**
  (which package artifact to install first: `quenching-roadmap` «What this skill is»/«boundary»); *dim 4 backlog* = **PRODUCT**
  work of the repo (item missing in the target repo, home `docs/backlog/` in `installation.md:18`); *Step 8 loop* =
  **recurring freshness** (re-running the audit by trigger, R17/R28/R32). The roadmap «proposes the ORDER, never the content»
  (payload Guardrails) already separates method×product; R28 «base evolution = only in the link with confirmation»
  separates propose×apply. No breach → nothing to note here (do not inflate).
- **«Profile is alive» (R32) × R28 contract × Rev5 limit coherence (axis 4 — audited, intact):** the
  `quenching-roadmap` is on the **right side** — it is **read-only/propositional** (PROPOSES, does not APPLY: `allowed-tools`
  without Write/Edit, «does NOT install», Guardrails), therefore consistent with «hook/skill OBSERVES-PROPOSES, command applies with
  OK» (R28) and with «re-modulating EMPHASIS/order ≠ rewriting content» (Rev5: dim 3/10/12 only «propose the home»). The
  merge **did not** touch this axis — it only removed the textual duplication.
- **Effect:** the adoption sequence has **one single home** (base-Order of the roadmap); the other two points become
  pointers that can no longer diverge. The contradiction already existing in the foundation description (three forms of
  layer 1) was **eliminated**. Less prose to maintain, zero drift risk in the order. **Invariant preserved**
  (nothing coupled to external repo/skill; portable scoring). No detection rule changed → harness does not run.

### Round 30 — 2026-06-29 · frontier: Lightweight and non-closed taxonomy of repo profiles (catalog of signals → emphasis)

- **Change:** created the new lean reference [../references/repo-profiles.md](../../plugins/claude-quenching/skills/quenching-management/references/repo-profiles.md) —
  a **named catalog of repo profiles/archetypes**, each with (a) the **SIGNALS** that Step 1 observes
  (file/structure/dependency) and (b) the recommended **EMPHASES** (which dimensions and which Step 8 triggers matter most).
  Eight source-anchored profiles: **MLOps/model-heavy** (ml pins + model release → dim 8/trigger (2), dim 3/10, dim 14);
  **data-pipeline/ETL** (bronze/silver/gold layers +
  generated artifact → dim 11, dim 14+R25 PreToolUse protects the generated content, dim 1 source×generated); **library/SDK**
  (src-layout/public API → lean dim 1 «20-80 lines (lib)», dim 2, dim 6 style-guide-skill, code
  intelligence if typed); **runtime service/app** (entrypoint/deploy/external → dim 1 «80-200 (service)»,
  dim 15 MCP, dim 14 guardrail); **monorepo/large codebase** (multiple packages → dim 1 per-directory +
  excludes + Read deny, fan-out, per-directory skills, plugin when «stops scaling»; gotcha: settings do not
  inherit from parent); **multi-contributor cross-tool** (AGENTS.md/.cursorrules → dim 1 CLAUDE.md×AGENTS.md boundary,
  dim 12 single-home); **mature `.claude/`** (populated surface → dims 6/7/8/9 rise, bloat/wiring/budget);
  **greenfield/repo from scratch** (no `.claude/` → emphasis becomes SEQUENCE: dim 1+2+12 first, hooks AFTER).
  Linked by a **short pointer** from Step 4 of SKILL.md + line in the References list + note in
  `report-format.md` (SKILL.md slim maintained). **CRUCIAL:** the file declares, at the top and in a
  «Boundary» section, that it is a **guide of FREE examples, not an enum** — a repo matches **several profiles or none**,
  emphases **sum**, it is a prioritization heuristic, **never a gate**; full scoreboard coverage intact; every
  signal is observable in Step 1 and every recommendation is anchored in a trigger actually seen. **Conceptual
  diff:** R29 connected the derived shape to prioritization but left the signals→emphasis **scattered in prose**
  in Step 4 (loose examples); R30 **consolidates them into a queryable catalog** without becoming a rigid knob —
  formalizes the vocabulary without closing the set. **No new payload**; no detection rule changed
  (greps/smells/criteria intact) → harness does not run. SKILL.md remains <500 lines (detail moved to the
  reference, Simplicity First / progressive disclosure).
- **Why:** it was the **TAXONOMY** part of the candidate «Lightweight repo profile taxonomy + installation roadmap payload»
  that R29 left in the backlog (the other part — the **roadmap payload** — goes to R31,
  deliberately NOT built here to avoid collision). The **meta-gap**: after R29, the method already
  *modulated* emphasis, but the profile vocabulary lived **dispersed in prose** in Step 4 — without a single
  queryable place, two auditors (or the same one in different repos) rebuild the signal→emphasis mapping from scratch
  each time. A named catalog gives the shared vocabulary **without** costing the openness (the rule that R29
  defended): that is why it is **free examples**, not an enum. The official source gives both the principle of modulating by
  trigger and the concrete profiles: the trigger→add table and the cost of excess from [features-overview], and the
  entire guide from [large-codebases] (per-directory CLAUDE.md, excludes, Read deny, per-directory skills,
  plugin when layering «stops scaling», settings that do not inherit from parent). The lib×service size-guidelines
  («20-80» × «80-200») come from the catalog `04-claude-md-memory.md`, and the cross-tool profile anchors in
  `10-agents-md-interop.md`. **Why it does NOT violate the "installs structure, never content" limit:** the catalog
  weights **which METHOD dimension to invest in** (probabilistic guidance), never *what* the repo should say — the
  «Boundary» section records that explicitly (not dim 16/knob, does not decide content, does not filter the scoreboard, does not
  prescribe names to the repo — distinct from the `docs/` taxonomy, which prescribes canonical names).
- **Sources:** [Extend Claude Code (features-overview) — Claude Code Docs](https://code.claude.com/docs/en/features-overview)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim** from the *«Build your setup over time»* table (trigger→add):
  *"You don't need to configure everything up front. Each feature has a recognizable trigger"*; triggers by
  profile: *"Claude reads many files to find where a symbol is defined or used → install a code intelligence
  plugin for your language"*, *"You keep copying data from a browser tab Claude can't see → connect that
  system as an MCP server"*, *"A second repository needs the same setup → package it as a plugin"*; excess cost
  (justifies modulating): *"Every feature you add consumes some of Claude's context. Too much can fill up
  your context window, but it can also add noise that makes Claude less effective; skills may not trigger
  correctly"*; greenfield intro: *"Start with CLAUDE.md for project conventions, then add other extensions as
  specific triggers come up"*; and *"Code intelligence… Typed languages, large codebases where grep is slow or
  imprecise"*. [Set up Claude Code in a monorepo or large codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim** signals/emphases for the monorepo profile: per-directory
  CLAUDE.md, *«`claudeMdExcludes` … for directories you never work in»*, *«add `Read` deny rules in
  `permissions.deny` to block Claude from opening … generated code, and vendored dependencies»*, per-directory
  skills, *«replace many per-directory CLAUDE.md files with one set of conventions everyone installs»* (plugin
  when *«layering stops scaling»*), and the gotcha *«Project settings in `.claude/settings.json` load only from
  your starting directory and are not inherited from parent directories»*; *«Revisit after major model
  releases: instructions that worked around an older model's limitation may become overhead»* (MLOps profile).
  Catalogs: `research/04-claude-md-memory.md` (size-guidelines 20-80 lib × 80-200 service) and
  `research/10-agents-md-interop.md` (cross-tool profile / CLAUDE.md×AGENTS.md boundary). The taxonomy
  consolidates already-dated facts; no profile was invented without an anchor.
- **Rejected/superseded:** discarded **closed enum** of profiles (e.g., "every repo is A, B, or C") — R29 already
  rejected it as speculative and rigid; maintained as **free examples** (several/none, emphases sum).
  Discarded **any profile without an observable signal** (e.g., "critical/mature repo" by judgment) — every
  profile must be anchored in a file/structure/dependency signal that Step 1 sees, otherwise it becomes curator preference.
  Discarded **rigid/numeric weighting** (fixed weights per profile) — the modulation remains
  qualitative/anchored in the observed trigger, not a formula that would mask the why. Discarded **building the
  sequenced installation roadmap payload** in this round — it is the **other half** of the candidate, reserved
  for R31; building it here would collide with it. Discarded **turning profile into dimension 16 or a template knob**
  — it is an input for Step 4 (application workflow), not an artifact to audit; 15 dimensions maintained.
  Discarded **making the profile taxonomy PRESCRIPTIVE like the `docs/` one** — the `docs/` taxonomy prescribes **names**
  to the repo (converges to canonical); profiles are **method diagnosis about the repo**, not names to impose — the
  «Boundary» section records the distinction. Discarded **adding a smell/grep** — no Bash available and the boundary is prioritization
  doctrine (not a detection rule); the R29 smell ("report with flat emphasis") remains PENDING.
  **Does not supersede** previous round — **formalizes** R29 (consolidates the vocabulary that R29 left in prose), without
  reversing any of its decisions.
- **Next candidate:** "Sequenced installation roadmap payload" (R31 — materialize the «invest first in…» block as an **installable
  roadmap** in `assets/`: the order that unlocks the rest for a repo from scratch, consuming the **greenfield** profile from this
  catalog); or "Loop in the target that RE-MODULATES emphasis by profile"
  (trigger (2) of Step 8 — model release re-weights the profile, since the need changes; crosses with
  Outgrowth detection), now with the profile catalog as input.

#### Revision Rev5 — 2026-06-29 · narrows the MLOps profile emphasis (do not prescribe content) — sharpens R30

- **Target:** R30 / `references/repo-profiles.md`, **MLOps / model-heavy** profile, **Emphasis** line
  (the part that listed «**dim 3/dim 10** — model decisions become direction/learning, not inline rule»).
- **Critique (internal contradiction, citable evidence):** the R30 catalog declares, in the «Boundary» section
  (`repo-profiles.md:110`), **«Does not decide content (VISION/memory/boundary of the repo — that is only Step 6):
  the profile weighs which METHOD dimension to invest in, never *what* the repo should say»** — but the MLOps
  profile Emphasis (`repo-profiles.md:40`) **prescribed content**: the gloss *«model decisions become
  direction/learning, not inline rule»* says *what* to record in VISION/memory, not *which method dimension* to
  invest in. Cross-reinforcement: **Step 6** of `SKILL.md` reserves **dim 3 (direction/VISION)** and **dim 10
  (memory)** as **«human content decision»** — «the method **only proposes**… **never writes
  memory; never decides the direction on its own»**. And **R29 in SKILL.md did NOT list dim 3 or dim 10** among the
  emphasis examples (SKILL.md:141-151 only cites dims 1/2/6/7/8/14/15 + Step 8 triggers): it was **R30**
  that expanded the emphasis to the two content dimensions that R29 had kept out — a slip exactly
  at the boundary the user agrees to respect (installs METHOD/STRUCTURE, never CONTENT).
- **Refinement (conceptual diff):** the MLOps emphasis **no longer** lists dim 3/10 as dimensions to *invest in*;
  it recognizes that in a model repo the **direction/memory tends to be dense** (model decisions accumulate),
  but records that this only weighs **proposing the HOME** for that content (Step 6), and that the profile **does not prescribe what**
  VISION/memory should say (refers to its own «Boundary»). Core of the signal preserved: model release → re-modulate emphasis via
  **dim 8/trigger (2)**; model pins → **dim 14** guardrail. No other profile touched; SKILL.md/report-format.md already intact (audited, see below).
- **Audit of the remaining points of the critical axis (method×content limit) — intact, not touched:**
  (1) the «Emphasis modulation» of Step 4 of SKILL.md **does not hide** a dimension (blockquote
  SKILL.md:158-167: «does not hide any from the scoreboard», «does not decide what memory/VISION/boundary should
  say», «Modulating the method's emphasis ≠ defining the repo's content») — the coverage false-negative that
  R12 combats is covered; (2) the new layer **references** Step 6, does not contradict it (except the
  MLOps point above, now corrected); (3) header + «How to use» (item 4: «No profile → flat emphasis is
  correct… do not invent a profile») + «Boundary» assert **FREE examples, not an enum/gate** with sufficient
  force; (4) no bloat (SKILL.md ~336 < 500; lean reference). **Limit intact after pruning the single breach.**
- **Effect:** the catalog stops **contradicting its own «Boundary»** and re-aligns R30 with the limit that R29
  preserved — the base gains internal consistency at exactly the point (dim 3/10 = content, only Step 6 proposes)
  that the user fears seeing slip. No detection rule changed → harness does not run.

### Round 29 — 2026-06-29 · frontier: Emphasis prescription guided by repo profile (fit-to-repo guidance)

- **Change:** **Step 4** of `SKILL.md` (produce the prioritized report) gains the subsection **«Emphasis
  modulation by repo profile (fit-to-repo guidance)»** and the priority formula gains a fourth factor —
  **× profile-weight**. Through R28, the report confronted **every** repo with **all** 15 dimensions at **uniform
  weight**: Step 1 already derived the shape, but Step 4 did not use that shape to say "for THIS repo,
  it is more valuable to invest here". Now the report **modulates** the P1/P2 queue by the **derived profile**
  (shape + need) in a **«For THIS repo, invest first in…»** block with 2-4 dimensions/triggers/payloads of
  highest leverage, each one **anchored in an observed trigger** (`file:line` or Step 1 fact).
  Propagated to three points: (a) `report-format.md` — new section in the skeleton («For THIS repo, invest
  first in…», after the scoreboard) + usage note explaining the axis + the fourth factor in the priority rule;
  (b) Step 1 of `SKILL.md` — closure with "also note the profile signals that will modulate the Step 4 emphasis"
  (monorepo/large codebase · populated `.claude/` surface × repo from scratch · external services · PRs/
  conventions in flux). **Conceptual diff:** the report stops being a **flat list of uniform coverage**
  and becomes **full coverage + modulated emphasis** — every dimension remains in the scoreboard, but the queue
  and installation plan gain a weight that lifts what yields **most** for the derived shape. SKILL.md ~310
  lines (<500); **15 dimensions maintained**; **no new payload** (it is workflow/report doctrine); **no
  detection rule changed** (greps/smells/«good» criteria intact), so the **eval harness does not run**.
- **Why:** it was the frontier the user opened (verbatim of the spirit): reading the log, they saw that SEVERAL
  options were deliberately rejected so the skill **would not define content** (installs STRUCTURE/METHOD,
  never CONTENT — Rev4/R22/Step 6), and **agrees** with that limit — but wanted **beyond DEFINING the method,
  DIRECTING how to extract MAXIMUM value according to the target repo's NEEDS**. The real **meta-gap**: Step 1
  derived the shape, Step 4 ignored it in prioritization — it confronted EVERY repo with all 15 dimensions at
  **equal weight**, without saying where the method yields most. The official source **gives** the criterion: *«you don't
  need to configure everything up front — each feature has a recognizable trigger… start with CLAUDE.md and add the
  others as triggers come up»* and *«every feature you add consumes context; too much can fill the window, but also adds noise…
  skills may not trigger»*. Therefore: investing in a dimension that the repo **does not exhibit a trigger for**
  is the same waste as omitting one it does exhibit — emphasis should follow the
  **trigger that the repo actually shows**. **Why it does NOT violate the "does not define content/direction" limit:** the
  modulation is **probabilistic guidance about the METHOD itself** (which dimension/trigger/payload to invest in),
  not enforcement nor a **content** decision. Explicit distinction recorded in SKILL.md: "for you, it is more valuable
  to sharpen dim 6" (method) × "your VISION is X" (content) — only the first is the method's work. Three safeguards
  that maintain the limit: the profile-weight **does not invent a gap** (it comes from Step 3 evidence), **does not hide**
  any from the scoreboard (full coverage preserved — it is reordering, not filtering), and **does not decide** the content of
  memory/VISION/boundary (which follows only in Step 6, "never writes memory; never decides the direction"). The
  recommendation is **always** anchored in an **observed** trigger (Step 1/3), never in the curator's preference.
- **Sources:** [Extend Claude Code (features-overview) — Claude Code Docs](https://code.claude.com/docs/en/features-overview)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim** on adding features to the repo's profile/trigger
  (*«Build your setup over time»* section): *"You don't need to configure everything up front. Each feature has
  a recognizable trigger, and most teams add them in roughly this order"* (with the trigger→add table:
  *"A second repository needs the same setup → Package it as a plugin"*, *"A side task floods your conversation
  with output you won't reference again → Route it through a subagent"*, etc.); on **starting with CLAUDE.md
  and growing by trigger** (intro): *"New to Claude Code? Start with CLAUDE.md for project conventions, then add
  other extensions as specific triggers come up"*; on the **cost of excess** that justifies modulating instead of
  spreading (the *«Understand context costs»* section): *"Every feature you add consumes some of Claude's context.
  Too much can fill up your context window, but it can also add noise that makes Claude less effective; skills
  may not trigger correctly, or Claude may lose track of your conventions"*; on **scaling/packaging by
  profile** (*«Combine features»*/Plugins section): *"Use plugins when you want to reuse the same setup across
  multiple repositories"*. [Set up Claude Code in a monorepo or large codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases)
  (accessed 2026-06-29, already in the R17 log) — reinforces the axis of **need that changes with shape**: *«instructions
  that worked around an older model's limitation may become overhead once a newer model handles the case on its
  own»* (the right investment in a repo depends on what it exhibits now). Catalog: `research/04-claude-md-memory.md`
  (progressive disclosure / smallest high-signal set by need) — used as a consolidated input, the doctrine
  anchors in the official dated doc.
- **Rejected/superseded:** discarded **creating a dimension 16 "profile/fit"** — the modulation is **application
  workflow** (how Step 4 prioritizes), not an artifact to audit; keeping 15 dimensions (Simplicity First).
  Discarded **a new payload** (skill/agent "profiler") — the shape is already derived in Step 1; R29 only connects
  that derivation to the report's prioritization, no other piece needed. Discarded **filtering/hiding dimensions
  outside the profile** — it would become a coverage loss (the base would «look audited» on an omitted dimension, the
  false-negative that R12 combats); the modulation **reorders**, never hides. Discarded **a closed profile taxonomy**
  (e.g., "repo-A/B/C") — it would be a speculative and rigid knob; the derived shape is **free** and the profile signals
  are **examples**, not an enum (Simplicity First) — left as an advancement candidate for a future round, if practice shows it is worth formalizing. Discarded **letting the method RECOMMEND content** (e.g.,
  "your VISION should say X") under the pretext of "maximum value" — that would cross the limit the user
  **agrees** not to cross; R29 modulates only the METHOD emphasis (which dimension to invest in), with the
  method×content distinction recorded explicitly in SKILL.md. Discarded **adding a smell/grep** — no Bash to measure, and the
  boundary is prioritization doctrine (not a surface detection rule); a possible future smell
  ("report with flat emphasis / no profile block in a marked-shape repo") is recorded in the
  review queue as PENDING. **Does not supersede** previous round — opens a new axis (diagnostic emphasis), distinct from
  R17 (lists the loop triggers) and from the Outgrowth/Plugin backlog (pruning/distribution mechanisms).
- **Next candidate:** "Lightweight repo profile taxonomy + installation roadmap payload" (formalize the
  profile signals into a named set and materialize the «invest first in…» block as a **sequenced
  roadmap** installable in `assets/`: the order that unlocks the rest, for a repo from scratch); or "Loop
  in the target that re-modulates emphasis" (trigger (2) of Step 8 — model release — **re-weights** the profile, since
  the need changes: a rule that became overhead is de-prioritized; crosses with Outgrowth detection).

### Round 28 — 2026-06-29 · frontier: Orchestration contract of the cycle's links (hook → command → sub-agent → skill)

- **Change:** added the subsection **«Orchestration contract of the links (hook → command → sub-agent →
  skill)»** at the **end of Step 8** of `SKILL.md`. Through R27 the thematic sequence (workflow + commands + hooks,
  9 rounds) had built all the **parts** — the recurring loop (R17), the composable command payload
  (R18/R27), the five hook payloads covering the event matrix (R19-R25), the wiring doctrine (R26) —
  but they lived **in isolation**: the doctrine of **how they COMPOSE into an operational flow** in the
  target repo was missing. The subsection names the **contract per link**, which is **dim 6 applied to the RUNNING FLOW**
  (not to the static home choice of authorship, which is R6) and the
  *workflow (predefined code path) × agent (the LLM drives)* boundary applied to maintenance: (1) **hook**
  = trigger that fires automatically,
  **OBSERVES/PROPOSES** (`additionalContext`) or at most BLOCKS (PreToolUse/enforcement), but **never mutates the
  base on its own** — *propose ≠ apply*, consistent with "the method never writes memory nor decides the direction" (Step
  6); (2) **command/skill** = **on-demand** step that **APPLIES, with OK**, item-by-item (the only link that changes
  the base; can be triggered by the model via R27 composability or by the operator); (3) **sub-agent** =
  **isolated** context that returns a **CONDENSED SUMMARY** (R9), the scanning link in a clean window. The
  **anti-pattern = chaining too much** — hook → command → cascade of sub-agents **without a human barrier** — under
  Simplicity First, with **dual barrier**: **human** (the link that mutates the base always has OK; the hook proposes and the
  human confirms) and **deterministic** (the runtime caps sub-agent recursion). Stitches the
  enforcement (deterministic: hook that blocks, depth cap) × guidance (probabilistic: hook that proposes,
  skill by judgment) boundary of dims 1/8/14. **Conceptual diff:** Step 8 stops only **listing** the triggers and
  their homes (R17) and starts naming the **contract between them** when they compose in execution, closing the cycle
  end-to-end: automatic freshness = hooks that OBSERVE/PROPOSE; re-examination = composable command + sub-agent in
  clean context; **base evolution = only in the link with confirmation**. SKILL.md ~286 lines (<500); 15 dimensions
  maintained; **no new payload** (it is workflow doctrine, not an artifact); **no detection rule changed**
  (greps/smells/criteria intact), so the eval harness **does not** run. Capstone of the 10-round sequence.
- **Why:** it was the capstone frontier of the user's sequence (the user felt the method was missing the use of
  commands and hooks; the previous 9 rounds built the PARTS). The remaining **meta-gap**: all the parts were
  installable and wired, but the method did not provide doctrine on **how they chain in a composed workflow** —
  when a step fires by hook (automatic) × by command (on demand) × in sub-agent (isolated) × by skill (judgment),
  and what the contract of each link is (who only proposes, who applies, who condenses). Without this contract, the installer could assemble a cycle that **chains too much** (cascade without
  human barrier) or that **mutates the base in a hook** (violating "the method never writes memory"). The subsection
  ties the links under the method's own invariant (propose≠apply; the human confirms base evolution) and
  anchors the barrier against over-chaining in the official simplicity doctrine + the deterministic depth cap.
- **Sources:** [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim** on the composition contract in sequence (*"Chain subagents"*
  section): *"For multi-step workflows, ask Claude to use subagents in sequence. Each subagent
  completes its task and returns results to Claude, which then passes relevant context to the next subagent"*;
  on the **condensed summary** (intro): *"the subagent does that work in its own context and returns only
  the summary"*; on the **deterministic barrier against over-chaining** (*"Spawn nested subagents"* section):
  *"a subagent can spawn its own subagents… so the intermediate output never reaches your main conversation.
  Only the top-level subagent's summary returns to you"* and *"A subagent at depth five doesn't receive the
  Agent tool and can't spawn further. The limit is fixed and not configurable"*; and the **cost warning** of
  chaining many (*"Running many subagents that each return detailed results can consume significant
  context"*); on **skill × sub-agent in the flow** (*"Choose between subagents and main conversation"* section):
  *"Consider Skills instead when you want reusable prompts or workflows that run in the main conversation
  context rather than isolated subagent context"*. [Building Effective Agents — Anthropic Research](https://www.anthropic.com/research/building-effective-agents)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim** on *workflow × agent*: *"Workflows are systems
  where LLMs and tools are orchestrated through predefined code paths. Agents… are systems where LLMs
  dynamically direct their own processes and tool usage"*; on the patterns: *"Prompt chaining decomposes a
  task into a sequence of steps, where each LLM call processes the output of the previous one"* and *"In the
  orchestrator-workers workflow, a central LLM dynamically breaks down tasks, delegates them to worker LLMs,
  and synthesizes their results"*; on **Simplicity First applied to composition**: *"add multi-step agentic
  systems only when simpler solutions fall short"* and *"add complexity only when it demonstrably improves
  outcomes"*; on the **human barrier**: *"Agents can then pause for human feedback at checkpoints or when
  encountering blockers"*. Catalog: `research/09-building-effective-agents.md` (orchestrator-workers pattern
  + effort scaling rules + non-free coordination cost).
- **Rejected/superseded:** discarded **creating a new payload** (script/command that orchestrates the cascade) — the
  contract is **composition doctrine**, not another artifact; the parts already exist (R18-R27) and what was missing
  was the rule for connecting them, not another piece (Simplicity First; one surgical evolution per round).
  Discarded **reopening R6** (static home choice) — R28 does not choose the home of an artifact at authorship;
  it applies the same boundary to the **running flow** (when each link fires/applies/condenses), a distinct axis.
  Discarded **reopening R17** (the loop spine) — R17 names *which* triggers and in *which* home; R28 names the
  *contract between them* when composed. Discarded putting the contract in `dimensions-template.md` or in
  `installation.md` — the right home is **Step 8 of the application workflow** (where the cycle spine already lives,
  R17): the orchestration contract is part of the *workflow*, not an isolated dimension nor of the installation mechanics.
  Discarded **creating a dimension 16 "orchestration"** — it is an application workflow (Step), not an artifact to audit;
  keeping 15 dimensions. Discarded **adding a smell/grep** — no Bash to measure and the boundary is composition doctrine
  (not a surface detection rule); a possible future smell
  («hook that mutates the base» / «cascade without human barrier») is recorded in the Review queue as PENDING.
- **Next candidate:** "Hook by event applied to `.claude/` (the config surface), not just `docs/`"
  (advancement backlog — materializes the other cut of Step 8's trigger 1: PostToolUse that re-runs detection
  of dims 6/7/8/9 on touching `.claude/skills`/`agents`/`settings.json` and **proposes**, distinct from R21/R23/R25);
  or "Outgrowth detection — skill that the base model has already superseded" (dim 6, axis of `13-skill-description-evals.md`).

### Round 17 — 2026-06-29 · frontier: Recurring maintenance cycle as a first-class operational workflow

- **Change:** added **Step 8 — "Establish the recurring maintenance cycle (the base is alive)"**
  to the **application workflow** of `SKILL.md` (Steps 1-7 → 1-8). Through R16 the method audited
  and installed **once** (Steps 1-7) and only had a recurring loop for the *evolution of the skill itself*
  (R12); there was no doctrine for the **recurring operational loop in the target repo**. Step 8 names the
  anchor fact — the base **rots** (*context rot*, dim 1) with code/model/team changes, so
  the method needs to **install the loop that keeps it fresh**, not just the snapshot — and establishes the
  **three documented triggers** with their **home** (dim 12 applied to maintenance): **(1) by event, on
  PR** — treat CLAUDE.md/docs edits as doc changes; home = **PR hook** that re-runs detection on the touched scope
  and **proposes** (does not block) — continuous audit (dim 8) + actionable error (dim 14); it is the recurring backlog item of the target's dim 4. **(2) By cadence, on
  model release** — revisit instructions that became overhead with a newer model; crosses with
  *outgrowth detection* (rule/skill that the base model already handles on its own ⇒ deprecatable) and dim
  1 pruning. **(3) On demand, by command** — a `/<re-audit>` that re-runs Steps 1-7 (or the argument's scope)
  and, for large repos, delegates to the **auditor sub-agent in clean context**
  (`assets/agents/quenching-auditor.md`); being a manual-work shortcut (not a side effect),
  it is born as a **skill** with trigger by description (dim 9: new command is born as a skill), not a legacy command. **Automatic freshness** between audits = **evolutionary Stop hook** (dim 8: reads the transcript and proposes
  deltas «while the gap is fresh») + OTel telemetry `skill_activated`/`invocation_trigger`
  (skill never triggered = deprecation candidate, dim 6). Conceptual diff: the *application workflow* stops
  being "audit+install once" and becomes **installing the cycle** that re-fires by event, by
  cadence, and on demand — the "workflow spine" on which the subsequent rounds hang the **concrete payloads**
  (PR hook, `/<re-audit>` command, ready Stop hook, installable via Steps 5-7). The section fixes **when/why/in which home** each trigger runs, **not** the script
  (Simplicity First; payload is the work of subsequent rounds). SKILL.md ~250 lines (<500); application
  template (15 dimensions) intact — it is **workflow** evolution, not dimension evolution; **no detection rule changed**
  (greps/smells/«good» criteria intact), so the eval harness **does not** run.
- **Why:** it was the thematic frontier of the user's sequence (workflow + commands + hooks) and the
  most visible **meta-gap**: the method audits the surface of other repos with snapshot rigor,
  but provided no doctrine on **how to keep it fresh over time** — exactly what dim 1 calls
  *context rot* and what the official source addresses in a dedicated section ("keep the files current as the
  codebase and models change"). Dims 8 (R7) and 9 (R8) stopped at **detection** ("detects the absence
  and proposes") and did not bind *when* to re-examine nor *which* mechanism triggers the re-examination; Step 8
  stitches hook (automatic freshness) + command/skill (re-audit on demand) + sub-agent (clean context) into a **cycle** and gives each trigger a home via dim 12. It is the spine that was missing for
  subsequent rounds to materialize the command/hook payloads the user feels are lacking (today there is no
  `assets/commands/` and the lifecycle hooks are not ready).
- **Sources:** [Set up Claude Code in a monorepo or large codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases)
  (accessed 2026-06-29, ✅ re-verified via WebFetch) — section **"A few ways to keep the files current
  as the codebase and models change"**, **verbatim**: *"Review in pull requests: treat CLAUDE.md edits
  like any other documentation change so conventions track the code"*; *"Revisit after major model
  releases: instructions that worked around an older model's limitation may become overhead once a
  newer model handles the case on its own. For example, a rule that forces single-file refactors can
  be deleted once the limitation is gone"*; *"Add a Stop hook that proposes updates: a `Stop` hook
  receives the path to the session transcript when Claude finishes responding, so a script can review
  the session and propose CLAUDE.md updates while the gap it exposed is fresh"*. From section **"Keep
  skills discoverable"**, **verbatim** on the freshness signal via telemetry: the `skill_activated`
  event *"records every invocation… and `invocation_trigger` records whether a command, Claude, or a
  nested skill invoked it, which tells you what to consolidate or retire"*. Catalog:
  `research/05-slash-commands.md` (line 149: *"Dimension 9 — new quarterly audit step:
  Incorporate the `/insights` -> `/audit-claude-md` loop as a recurring backlog item (Dimension 4)…
  This loop closes the cycle between intent (configuration) and behavior (execution)"*; community source *"I Asked Claude Code to Audit My Own Setup"* documenting `/audit-claude-md` + `/insights`
  as a recurring loop — used only as evidence of practice, the doctrine anchors in the official doc) and
  `research/04-claude-md-memory.md` (evolutionary Stop hook + context rot + pruning criterion).
- **Rejected/superseded:** **supersedes the R8 rejection** (`dim-09-commands.md`: *"Discarded the
  quarterly `/insights`→`/audit-claude-md` loop as a method step — it is a recurring maintenance workflow
  (target-repo backlog item, dim 4), not template evolution; it stays out of this single round"*) —
  R8 was right **not** to force a concrete step into that *dimension 9* round, but the axis was the
  right boundary and remained pending; now it enters **in the right home** (core application workflow,
  not a dimension template) as **cycle doctrine** anchored in the official source, without blindly reopening dim 9. Discarded **writing the payloads** now (PR hook, `/<re-audit>` command, ready Stop hook in `assets/commands/`/`assets/hooks/`) — it is payload authorship, not doctrine evolution; the spine **anticipates them and gives the home**, the implementation goes to subsequent rounds (Simplicity First;
  one surgical evolution per round). Discarded importing the **`/insights`→`/audit-claude-md` loop
  literally** as the prescribed cycle — `/insights` is a specific feature and the pair is community practice;
  the method anchors in what the official doc publishes (PR-review + model-release + Stop hook + OTel
  telemetry) and leaves the concrete command as the portable `/<re-audit>`. Discarded **creating a dimension 16
  "maintenance"** — it is an application workflow (Steps), not an artifact to audit; keeping 15 dimensions
  (Simplicity First). Discarded putting the step in the **«Method evolution» section** (which is the
  evolution cycle of the *skill*, R12) — this is the operational cycle of the *target repo*, home = application workflow.
- **Next candidate:** "Concrete payload of the re-audit command (`assets/commands/` +
  `knowledge-*` skill with trigger)" — materialize the slot of trigger (3) of Step 8: the
  `/<re-audit>` command that fires the cycle, closing the user's gap (today there is no `assets/commands/`);
  or "Coverage hook for `docs/`/surface on PR (enforcement-proposes)" — materialize the slot of
  trigger (1) (PR hook that re-runs detection and proposes), crossing dim 8 × dim 2 with an actionable error.

### Round 12 — 2026-06-29 · frontier: Agent-guided evaluation cycle (eval of the audit itself)

- **Change:** added a new step — **"Eval of the audit itself (the curator is evaluated as a
  production tool)"** — to the **"Method evolution"** section of `SKILL.md` (not to the application template).
  Through R11 the method evolved **by inspection** (read the catalog, sharpen a dimension) without
  ever measuring whether the new rule **catches** what it claims to catch. The evolution names the anchor fact: the method
  **is an agent tool**, and agent tools are evaluated **against realistic tasks**.
  Before closing a round that changes a **detection rule** (smell/grep/«good» criterion), the
  evolutionist runs a **minimal harness of 3-5 fixtures** — small sample repos each with a **known planted gap**
  (repo without CLAUDE.md · skill without frontmatter · ADR implemented but not removed · two overlapping-scope skills · boundary
  dimension without a single home) — and measures **three
  things, not just pass/fail**: (1) **hit rate by dimension** (was the planted gap signaled in the right dimension, with `file:line`?); (2) **false-negative rate** — the metric that
  matters most: did any real gap **slip through**? A false-negative is worse than a false-positive,
  because the base **looks** audited and is not; (3) **token cost per dimension** (dimension consuming
  disproportionately → candidate to push to the auditor sub-agent). The **reading of the
  numbers** — not the impression — decides whether the new rule added **signal** or just noise/cost; the test
  of a new rule is "catches the planted gap **without** triggering on clean fixtures (no gap in that
  dimension)"; a rule that does not move any metric is a candidate to **not be included** (Simplicity First).
  Fixtures and measures live alongside the research (`research/`); **applying to a real repo (Steps
  1-7) does NOT run the harness** — it belongs only to *skill development*. Conceptual diff: the
  *evolution workflow* stops being "sharpen by inspection and record" and gains a **quantitative feedback
  loop** (hit/false-negative/cost against fixtures), mirroring the eval-driven
  development that the official doc practices for tools/skills. SKILL.md ~196 lines (<500); application template
  intact (still 15 dimensions — this is **workflow** evolution, not dimension evolution).
- **Why:** it was the **next candidate** explicitly pointed out by R11 (and by R9/R10), the last
  highest-value axis of the most-anchored catalog (`08-writing-tools-for-agents.md`, 10 confirmed sources)
  not yet attacked, reinforced by `13-skill-description-evals.md` (missed-fire =
  false-negative; benchmark with×without; blind A/B). It was the method's **meta-gap**: it audits the
  surface of **other** repos with rigor, but evolved itself with no verifiable efficacy criterion —
  exactly what the source calls an antipattern ("tools are evaluated by inspection").
  The method **lives** by this: R4-R11 added greps/criteria without ever confirming they catch the gap
  they promise; the harness closes that loop and **hardens the log itself** (a round that does not move
  any metric should not close). Treats the curator with the same rigor as a production tool.
- **Sources:** [Writing effective tools for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  (accessed 2026-06-29, ✅ re-verified via WebFetch) — *"Running an evaluation"* section: **verbatim**
  *"Start by generating lots of evaluation tasks, grounded in real world uses"* and *"Prompts should be
  inspired by real-world uses and be based on realistic data sources and services"*; the metrics list (*"Running the evaluation"* section)
  **verbatim** *"We recommend collecting other metrics
  like the total runtime of individual tool calls and tasks, the total number of tool calls, the
  total token consumption, and tool errors"*; and the agent-guided improvement loop (*"Collaborating with agents"*
  section) **verbatim** *"You can even let agents analyze your results and
  improve your tools for you… Claude is an expert at analyzing transcripts and refactoring lots of
  tools all at once"*. [Equipping agents for the real world with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
  (accessed 2026-06-29, ✅ verified via WebFetch) — *"Developing and evaluating skills"* section:
  **verbatim** *"Identify specific gaps in your agents' capabilities by running them on representative
  tasks and observing where they struggle or require additional context"* (eval-driven; "specific
  gaps"/"representative tasks" = basis of the fixture-with-planted-gap) and *"iterate based on
  observations"*. Catalog: `research/08-writing-tools-for-agents.md` (line 17 "evaluation harness with 3-5 realistic scenarios… measure hit rate, tokens, parameter error rate";
  line 235 "the curator agent must be evaluated with the same rigor as any production tool. Minimum metrics: accuracy per dimension, tokens per dimension, **false-negative rate**
  [undetected gaps]") and `research/13-skill-description-evals.md` (missed-fire vs.
  false-trigger; benchmark with×without; verifiable assertions; blind A/B; 11 confirmed sources).
- **Rejected/superseded:** **supersedes the R0 rejection** ("discarded creating `evals/` now — Simplicity
  First, the output is qualitative/consultive, no verifiable criterion"): R0 was right for the
  *bootstrap*, but the official source now **gives** the verifiable criterion (realistic tasks + runtime/tool-calls/tokens/errors metrics + false-negative as missed-fire), so the axis stops being
  an impression and becomes a measurable loop — without blindly reopening R0: the harness stays **minimal** (fixtures +
  3 measures in `research/`, **without** the heavy `evals/` folder that R0 avoided). Discarded importing the
  **"40% reduction in completion time"** attributed to an agent that rewrites descriptions — the
  re-verification via WebFetch **confirms** that number **does not appear** in the official post (it is a
  community/empirical figure); the method uses only the metrics the doc publishes verbatim (hit rate, tokens,
  false-negative). Discarded importing the **complete evals.json/grading.json/benchmark.json schema**
  (with_skill×without_skill, 60/40 split, 3 runs, 5 iterations, blind comparator) as a mandatory artifact —
  that is the mechanics of the `skill-creator` for **one** skill; here the target is the **entire curator**, and the template
  requires only the **minimal harness** (3-5 fixtures + 3 measures), not the full tooling (Simplicity
  First). Discarded putting the step in the **application template** (Steps 1-7): it would be a knob that would weigh
  in every repo audit — eval is of *skill development*, the right home = the "Method evolution" section of SKILL.md (dim 12: one purpose → one home). Discarded **writing the fixtures** now — it is payload/development
  authorship, not doctrine evolution; the workflow now **requires** them, the implementation stays outside the single round.
- **Next candidate:** "Outgrowth detection — skill that the base model has already superseded" (dim 6 —
  catalog `13-skill-description-evals.md`: benchmark without the skill, pass-rate delta ≈ 0 ⇒
  deprecatable; distinct from bloat because it is redundancy with the **model's native capability**, not with
  another skill) or "Completeness of normative reference / reconstruction test" (dim 2 — reopen with the
  right source, R2 deferred due to `mischaracterized` attribution).

### Round 0 — 2026-06-28 · frontier: initial skeleton

- **Change:** creation of the method (`SKILL.md` + 4 references + this log) and of the
  `quenching-evolutionist` agent. 14 dimensions covering the Claude
  Code surface of the repo; `audit-by-default + apply-with-confirmation` workflow routing
  to the owner skill; dimension 12 (boundaries) as the ownerless core.
- **Why:** the repo already had skills for each artifact (CLAUDE.md, architecture,
  backlog, catalog, skills), but was missing the umbrella layer that views the entire
  surface and confronts artifacts against each other.
- **Sources:** conventions derived from the repo itself (root CLAUDE.md,
  `docs/arquitetura/INDICE.md`, prefix taxonomy from `skills-skill-creator`,
  template from `.claude/agents/diagnoser-run.md` and
  `docs/realignment-refactor-main.md`). _Bootstrap round — no external research; subsequent ones require ≥1 cited external source._
- **Rejected/superseded:** discarded creating `evals/` now (Simplicity First — the
  output is qualitative/consultive, no verifiable criterion); discarded putting the
  template/log in `docs/` (would pollute the product the method audits).
- **Next candidate:** "MCP coverage" or "Boundary detection by heuristic"
  (sharpen dimension 12).
