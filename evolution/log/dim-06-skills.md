# Dimension 6 — skills

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **the skills surface: trigger/routing and toolset bloat**.

## Current state

> Active summary of each boundary in this dimension (what is valid today). Detail and rationale are in the history below.

> **Cross-note (R22, recorded in [dim-02-docs.md](dim-02-docs.md)):** the package gained the
> **generic** skill-template `assets/skills/quenching-announcement/` — generates **directed
> communications** (incident/change/deploy/migration/announcement) by reading **one
> template per channel** (`email`/`chat`/`wiki`/`markdown`) from the `docs/communications/`
> home. It is **one** generic skill that reads the templates (preferred over N skills per
> subject: subject is a value, not a capability — avoids the R4 collision and R10 bloat).
> The boundary/decision lives in dim 2 (new canonical home); only the pointer remains here
> for anyone inventorying the skills surface.

- **R4 · Trigger optimisation (sub-trigger)** — dimension 6 (Skills) stops being a
  generic "pushy description" and gains: the **description-as-routing** (3rd person,
  what-it-does + when-to-use + literal-user-phrases, chooses among 100+ skills); the
  **verifiable trigger test** (should-trigger × should-not-trigger pair; false-trigger
  × missed-fire = both a **description** problem, not an instruction one; rule "works
  via `/name` but does not auto-trigger ⇒ description is the bug"); the new smell
  **trigger collision between skills** (descriptions sharing keywords without an
  exclusion clause — latent false-trigger) treated as **cross-cutting 6b**
  (cross-artifact confrontation, dimension 12 applied to descriptions: the method
  detects, `skills-skill-creator` fixes); + `disable-model-invocation`/`paths` locks
  for side-effect/scope. Owner: `skills-skill-creator` (refines a description); the
  **collision between descriptions** stays in the method core. (round 4)

- **R33 · DOMAIN artifact guided by need (when to CREATE a repo-specific skill/sub-
  agent — INVERSE criterion of bloat)** — dim 6 (and the sub-agent side of dim 7)
  gains the doctrine + the smell of **«recurrent domain need without artifact»**: beyond
  merging/pruning (R10) and choosing the home of what already exists (R6), the method
  **recognises** when a recurrent repo need justifies **creating** a NEW artifact
  **specific to the DOMAIN** (distinct from the generic `conocimiento-*` payloads the
  package installs). The signal is a **recognisable trigger** (Step 1): (a) repeated
  multi-step manual procedure in the history — *«you paste the same playbook… for the
  third time → capture it as a skill»*; (b) recurring domain task type → **skill**
  (action or reference); (c) recurring verbose side-task (logs/runs) → **sub-agent**
  (*«route it through a subagent»*, dim 7). **CRUCIAL — the method PROPOSES the
  SKELETON (name + description-trigger + home skill×sub-agent + empty `references/`),
  the repo fills in the CONTENT** (the domain procedure is a human decision = same
  limit as Step 6 / Rev5 / R29: installs structure/method, never content/direction).
  It is **PROPOSING** (like Step 6), not installing a ready payload: the package
  **does not carry** domain skills/sub-agents (they would be coupled to a repo —
  break self-contained); it teaches to **recognise the trigger** and sketches the
  **form**. New smell in dim 6 (domain need without artifact) + remediation «propose
  the skeleton»; cross-ref on the sub-agent side of dim 7; pointer in Step 5 of
  SKILL.md and in profiles (each profile suggests WHAT TYPE of domain artifact pays
  off). **Distinct from R6** (home of what exists), **R10** (merge/prune — inverse),
  and the «outgrowth» candidate (deprecating what the model already does). No new
  payload; 15 dimensions; no change to a MEASURED detection rule by grep (the smell
  is a cross-read with Step 1) — 6b greps untouched. **`revised-by: Rev7`** (the
  smell gained the explicit counter-condition «when NOT to trigger» — observable
  recurrence ≥3 + stable procedure + leverage > cost + NOT what the model already
  does + create≠extend — poka-yoke against becoming a skill-spam generator). (round 33)

- **R10 · Consolidation / toolset bloat of the skills surface** — dimension 6 (skills)
  gains the **toolset bloat test**: the skills surface is a toolset, and *"if an
  engineer can't say with certainty which skill applies to a scenario, the agent
  won't be able to either"* — two or more skills with **overlapping functional scope**
  (they cover the same work on the same artifact) are *bloat* (an ambiguous decision
  point), whose fix is **consolidate/prune** into one skill with a parameter/mode (the
  redundant one becomes **deprecatable**), **not** pile up exclusion clauses.
  Named distinction from the neighbour smell of **trigger collision** (R4/6b):
  collision = same *keyword*, **distinct scopes** → exclusion clause (both survive);
  bloat = **scopes actually overlapping** → merge (dim 12, "if two answer the same
  question, there is a boundary violation"). New smell **toolset bloat**; remediation
  "consolidate the cluster". Complements **6b** (grep that lists *clusters of
  overlapping scope* by name/target-verb convergence, beyond the R4 keyword grep) +
  the **toolset test** as a read that decides collision × bloat. Authoring/merging
  exits `quenching-skills`; the **overlap detection and consolidation proposal** stay in
  the core (dim 12 applied to the skills surface). (round 10)

## Round and revision history

> Most recent rounds at the top. Revisions (`Rev*`) are nested under the round they refine.

### Round 33 — 2026-06-29 · boundary: DOMAIN artifact guided by need (when to CREATE a repo-specific skill/sub-agent) · **revised-by: Rev7**

- **Change:** refined **dimension 6 (skills)** in `dimensions-template.md` with a new
  facet in «What good looks like» — **«DOMAIN artifact guided by need (when to
  CREATE… — the INVERSE criterion of bloat)»** — + **a new smell** («recurrent
  domain need without artifact») and the **remediation** «PROPOSE the skeleton, leave
  the content to the repo». Cross-ref in **dim 7**'s «What good looks like» (sub-agent
  side: recurring verbose domain side-task → create own sub-agent). Pointer in **Step
  5 of SKILL.md** (block «DOMAIN artifact guided by need (propose, do not install)»)
  and in the **«How to use» section of `repo-profiles.md`** (item 5: each profile
  suggests WHAT TYPE of domain skill/sub-agent tends to pay off — MLOps→«validate
  model X», data-pipeline→«create task»/«diagnose run», service→«incident runbook»).
  The method stops only **installing fixed generic payloads** (`conocimiento-*`) and
  starts **recognising** when a **recurrent DOMAIN need** of the target justifies an
  artifact SPECIFIC to that repo (not generic from the package) and **PROPOSING its
  skeleton**. The trigger is observable in Step 1: (a) repeated multi-step manual
  procedure in the history/PRs; (b) recurring domain task type; (c) family of
  commands/runs / recurring verbose side-task. **Conceptual diff:** dim 6 had the
  **merge/prune** criterion (R10) and dim 7 had the **home-choice-of-what-exists**
  criterion (R6) — the **inverse** was missing: **when to CREATE** what is absent.
  R33 adds that axis, nailing down that **creating** here means **PROPOSING** (not
  installing), and that the proposed object is only the **form** (skeleton/frontmatter),
  never the **content** of the domain procedure. Stays at 15 dimensions; **no new
  payload**.
- **Why:** it was the **reserved** boundary in the backlog («Repo-specific
  skills/agents guided by need») and the user's literal request: «a knowledge base
  and **specific skills/agents** can help» the repo evolve. Until R32 the method only
  **installed the FIXED payloads** of the package; it was missing a recommendation/
  sketch for a DOMAIN-SPECIFIC artifact when the need justifies it. The **target repo
  is living proof**: it already has domain skills (`bundle-create-domain-task`,
  `bundle-diagnose-run`, `data-catalog`) and a sub-agent (`diagnoser-run`)
  that **came from no generic package** — they were born from the domain's need. The
  method now knows to **recognise** that trigger and **propose** the form, without
  crossing the limit (the domain procedure's content is a human decision — the limit
  that Rev5/R29 protect and that the user **agrees** not to cross). **Why dim 6 (not
  7) is the home of the axis:** the creation trigger is mainly «repeated
  procedure/task → skill» (the docs list 3 skill triggers and 1 sub-agent trigger);
  the sub-agent is the **particular case** (verbose side-task), cross-referenced in
  dim 7. **Distinct from R6** (home of what exists), **R10** (merge the overlapping —
  the inverse of creating) and the **outgrowth** candidate (deprecating what the base
  model already does on its own — pruning, not creation).
- **Sources:** [Extend Claude Code (features-overview) — Claude Code Docs](https://code.claude.com/docs/en/features-overview)
  (accessed 2026-06-29, ✅ via WebFetch) — the **«Build your setup over time»** table
  gives the **creation triggers verbatim**: *«Each feature has a recognizable trigger»*;
  *«You paste the same playbook or multi-step procedure into chat for the third time →
  Capture it as a skill»*; *«You keep typing the same prompt to start a task → Save it
  as a user-invocable skill»*; *«A side task floods your conversation with output you
  won't reference again → Route it through a subagent»*; and *«The same triggers tell
  you when to update what you already have… A workflow you keep tweaking by hand is a
  skill that needs another revision»*. The «Skill vs Subagent» tab on the same page
  distinguishes **reference skill × action skill** (*«Reference skills provide knowledge
  Claude uses throughout your session, like your API style guide. Action skills tell
  Claude to do something specific»*) and marks the sub-agent as *«specialized workers»*.
  Consolidated input: `research/01-agent-skills.md` (skills package **procedural
  knowledge and DOMAIN context**; agents vision «codifying patterns observed in
  behavior») and `research/02-subagents.md` (*«you keep spawning the same kind of
  worker with the same instructions»* → custom subagent).
- **Rejected/superseded:** discarded the **package CARRYING ready domain skills/sub-agents**
  (e.g., a `conocimiento-train-model`) — would violate portability/self-contained
  (would couple to a repo type) **and** the content limit (the domain procedure is a
  human decision); the method only **proposes the form**. Discarded **creating a
  dimension 16** «domain artifacts» — it is a facet of dim 6/7 (when to create a
  skill/sub-agent), not a new surface; 15 maintained (Simplicity First). Discarded
  **adding a measured grep in 6b** for the smell — «recurrent need without artifact»
  is a cross-read with the history/Step 1 (does not match a static-surface regex) and
  there is no Bash in context to measure; remains as a read, without touching the 6b
  greps (no MEASURED detection rule changed → harness does not run). Discarded **a
  «domain skill scaffolder» payload** — the skeleton authoring is already the job of
  the `quenching-skills` template (frontmatter/structure); R33 only connects the
  **trigger of recognising the need** to that skeleton, without a new piece. **Does
  not supersede** a prior round — opens the «create» axis (distinct from
  merge/home-choice).
- **Next candidate:** «Outgrowth detection — skill the base model has already
  superseded» (dim 6 — run the benchmark without the skill and mark as deprecatable
  the one with delta ≈ 0; the **inverse** of R33: pruning what became redundant with
  native capability, not creating what is missing) or «AGENTS.md / cross-tool
  interoperability» (dim 1/new — `AGENTS.md` as a standard, CLAUDE.md × AGENTS.md
  boundary).

#### Revision Rev7 — 2026-06-29 · narrows the R33 smell (poka-yoke against skill-spam)

- **Target:** R33 / dim 6 / the **new smell** «recurrent domain need without artifact»
  (in `references/dimensions-template.md`, dim 6, line of the «Smells» block;
  cross-ref in dim 7).
- **Critique (signal: bloat/latent false-positive, Simplicity First):** the smell was
  **too broad** — the *smell line* the auditor reads said only «repeated manual
  procedure … creation trigger, not merge trigger», **with no observable recurrence
  threshold and no explicit counter-condition**. Named real risk: the doctrine «create
  when there is a recurrent need» becomes a **skill-spam generator** — every repetition
  would recommend a new artifact, **against** the context cost that the official docs
  themselves warn about (*«every feature you add consumes context… too much adds
  noise… skills may not trigger»*). Four cases in which one should **not** create were
  not nailed into the smell line: (1) one-off/unstable (1-2x, or still-mutating
  procedure); (2) what the **base model already does on its own** (delta ≈ 0 — the
  *outgrowth* candidate, which R33 already said was distinct but the smell did not
  exclude); (3) the cheaper home (CLAUDE.md/`rules/`) that better serves a recurrent
  rule; (4) **create≠extend** — when the right action is to refine a neighbouring
  artifact (R6/R10), not spawn a new one. The «good» (line 92) had the
  structure×content limit, but **not** the when-to-trigger qualifiers; the smell line
  was the one that could produce the false-positive.
- **Refinement (surgical, 1 smell line):** added to the smell line itself the
  **explicit counter-condition «When NOT to trigger»** (poka-yoke) with the four cases
  (a)-(d) and the **observable threshold ≥3** anchored verbatim in the docs (*«you
  paste the same playbook… for the THIRD time»*), closing with the conjunctive
  condition: triggers only with **observable recurrence (≥3) + stable procedure +
  leverage (context saved > artifact cost) + no counter-condition**. **Conceptual
  diff:** the smell stopped anchoring in «repeated by hand» (judgment, any N) and
  started requiring **countable recurrence + stability + net leverage**, with
  **explicit exclusion** of what the model already does (does not collide with the
  *outgrowth* candidate — guarantees that R33 never recommends creating the redundant)
  and of what should be **extended** (not created). Does NOT advance a boundary: the
  R33 facet/remediation and the 6b greps remain intact; only the smell's *trigger
  condition* became skill-spam-proof. Self-contained invariant preserved (the cited
  doc is an official Anthropic source, not a repo coupling).
- **Sources:** [Extend Claude Code (features-overview) — Claude Code Docs](https://code.claude.com/docs/en/features-overview)
  (accessed 2026-06-29, ✅ via WebFetch) — **verbatim:** *«Every feature you add
  consumes some of Claude's context. Too much can fill up your context window, but it
  can also add noise that makes Claude less effective; skills may not trigger
  correctly, or Claude may lose track of your conventions.»* (cost→do-not-create);
  *«You paste the same playbook or multi-step procedure into chat for the third time →
  Capture it as a skill»* (threshold ≥3, observable); *«Claude gets a convention or
  command wrong twice → Add it to CLAUDE.md»* (cheaper home for recurrent rule,
  counter-condition c); *«A workflow you keep tweaking by hand is a skill that needs
  another revision»* (extend, not create — counter-condition d). Same source R33 cited
  — refines the reading of it, does not introduce a new source that overrules it.
- **Effect:** the R33 smell became **narrow and skill-spam-proof** — only triggers when
  creating REALLY pays off; the explicit counter-condition prevents the false-positive
  (one-off, native capability, cheaper home, artifact to extend) without rewriting the
  doctrine or touching a MEASURED rule. The smell remains a **cross-read with Step 1**
  (no measured grep) — consistent with R33.

### Round 10 — 2026-06-29 · boundary: Consolidation / toolset bloat of the skills surface

- **Change:** refined **dimension 6 (skills)** in `dimensions-template.md` and renamed/
  complemented cross-cutting item **6b** in `detection-and-smells.md` (from "Trigger
  collision" to "Trigger collision **+ toolset bloat**"). The "What good looks like"
  had the trigger test (R4) and the non-collision rule, but treated **every** dispute
  between skills as a **description** problem (exclusion clause). It now gains the
  **toolset bloat test**: the skills surface **is** a toolset, and the official
  criterion applies: *"if an engineer can't say with certainty which skill applies to
  a scenario, the agent won't be able to either"*. Skills with **overlapping functional
  scope** (they cover the same work on the same artifact — e.g., three distinct skills
  that audit/check the same CLAUDE.md) are *bloat*: an ambiguous decision point. The
  healthy target is **few powerful skills** (one with a parameter/mode), not many
  specialised ones that overlap. The evolution **names the distinction** from the
  neighbour smell: **trigger collision** = same *keyword*, **distinct scopes** → fix =
  **exclusion clause** (both survive); **bloat** = **scopes actually overlapping** →
  fix = **consolidate/prune** (merge into one skill, the redundant one becomes
  **deprecatable** — dim 12, "if two answer the same question, there is a boundary
  violation"). New smell **toolset bloat** in dim 6; remediation "consolidate the
  cluster, do not pile up exclusion clauses". In `detection-and-smells.md`, the **6b**
  gains a second grep that **lists bloat candidates** (clusters of skills whose
  name/target-verb converges on the same noun — drift/link/enhance/sync of
  `claude-md`; `plan-*`; `bundle-*`) beyond the R4 keyword grep, and the **toolset
  test** as a read that decides collision × bloat. Conceptual diff: dimension 6 stops
  treating skill-dispute only as "weak description" and starts separating **disambiguate**
  (description) from **consolidate** (structure), with an overlap-scope detector —
  dim 12 applied to the skills surface itself. Stays at 15 dimensions.
- **Why:** it was the **next candidate** pointed out explicitly by R9 and the last
  highest-value axis still open in the most anchored catalogue (`08-writing-tools-for-agents.md`,
  10 confirmed sources) — the **only** angle of skills that R4 (trigger) **did not**
  cover: R4 fixes the description when scopes are distinct, but had no way to flag two
  skills that **do the same work** (where the fix is *merge*, not *disambiguate*). The
  repo **lives** by this: it has ~30 skills and a real cluster around "CLAUDE.md" (R4
  already cited `claude-md-drift-audit` · `claude-md-link-check` · `skills-claude-md-enhancer` ·
  `sync-claude-md`) — **consolidation** candidates, not just exclusion clause candidates;
  the method now flags them with a verifiable criterion (the toolset test) instead of
  impression. The package itself practises the principle: it carries **few**
  non-overlapping-scope `conocimiento-*` templates instead of one skill per artifact.
- **Sources:** [Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  (accessed 2026-06-29, ✅ verified by WebFetch) — states **verbatim** *"One of the
  most common failure modes we see is bloated tool sets that cover too much
  functionality or lead to ambiguous decision points about which tool to use"*; *"If
  a human engineer can't definitively say which tool should be used in a given
  situation, an AI agent can't be expected to do better"*; and *"Curating a minimal
  viable set of tools … can also lead to more reliable maintenance and pruning of
  context over long interactions"*. Catalogue: `research/08-writing-tools-for-agents.md`
  (consolidation as 3rd principle: "few powerful tools" × "one tool per action =
  toolset bloat"; the **toolset bloat test** as a dim 6/12 boundary criterion — "if
  two artifacts answer the same question, there is a boundary violation"; 10 confirmed
  sources in the anti-hallucination check).
- **Rejected/superseded:** discarded **creating a new dimension** "toolset efficiency"
  — it is a refinement of existing dim 6; the axis enters as a complement to **6b**
  (like 7b/8b/9b), keeping 15 dimensions (Simplicity First). Discarded importing the
  **API toolset loading mechanisms** (`defer_loading`/Tool Search ~55k→500 tokens,
  Programmatic Tool Calling, `response_format` CONCISE/DETAILED, `token-efficient-tools`
  header) into the template — they are platform *tool use* config, not the `.claude/`
  skills surface the method audits; they live only in the catalogue. Discarded
  importing the **"40% completion time reduction"** number from the test-agent that
  rewrites descriptions — it is an empirical result from a multi-agent system, not a
  verifiable surface criterion; the template uses only the **toolset test** (no magic
  number). Discarded opening the **actionable error** axis (dim 14/8 — hook/audit
  failure messages as guardrails) from the same catalogue in this round: it is its own
  boundary, would dilute the single evolution — enters as **next candidate**. Discarded
  touching **dim 12** directly: the bloat **is** dim 12 applied to the skills surface,
  but the operational refinement (smell + grep + test) fits better in dim 6, where the
  auditor already looks; dim 12 is only cited as the boundary principle the fix invokes.
- **Next candidate:** "Actionable error / failure messages as guardrail" (dim 14/8 —
  catalogue `08-writing-tools-for-agents.md`: hooks/audit scripts return actionable
  error instead of opaque code, avoiding self-correction loops) or "Normative reference
  completeness / reconstruction test" (dim 2 — reopen with the right source, R2
  deferred due to `mischaracterised` attribution).

### Round 4 — 2026-06-28 · boundary: Trigger optimisation (sub-trigger)

- **Change:** refined **dimension 6 (Skills)** in `dimensions-template.md` and in
  `detection-and-smells.md`. The "What good looks like" moves from "pushy description"
  to **description-as-routing**: 3rd person, what-it-does + when-to-use + **literal
  phrases the user would type**, with a **verifiable trigger test** (should-trigger ×
  should-not-trigger pair — wrong firing on *should-not* = false-trigger; silence on
  *should* = missed-fire; **both = description problem, not instruction**, with the
  rule "if it works via `/name` but does not auto-trigger, the body is right and the
  description is the bug"), plus `disable-model-invocation` (side effect) /
  `user-invocable: false` (background) / `paths` (scope) locks. New smell: **trigger
  collision** — two or more descriptions sharing the same keywords without an
  exclusion clause (latent false-trigger). In `detection-and-smells.md`: vague-description
  / 1st-2nd-person / side-effect-without-lock greps in dimension 6, and a cross-cutting
  item **6b (trigger collision)** with a keyword loop that lists skills competing for
  the same term + the should/should-not routine (read, no grep). Conceptual diff:
  dimension 6 stops being "strong description" and gains a **nameable test
  (should/should-not pair)** and a **detector of collision between skills** — and the
  collision is classified as **dimension 12 applied to descriptions** (method core
  detects; `skills-skill-creator` fixes each description).
- **Why:** the repo has **~30 skills** and several share strong keywords —
  4+ skills carry "CLAUDE.md" in description/`when_to_use` (`claude-md-drift-audit`,
  `claude-md-link-check`, `skills-claude-md-enhancer` + the owner `sync-claude-md`),
  plus `plan-*` and `bundle-*` clusters. Trigger collision is therefore a **real and
  measurable risk** that the owner `skills-skill-creator` (which refines **one** skill
  at a time) does not see: it is a cross-artifact confrontation, close to the core.
  The template previously only said "pushy description / two skills competing for the
  trigger" without a verifiable criterion or triage command.
- **Sources:** [Skill authoring best practices — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
  (accessed 2026-06-28) — confirms **"The description is critical for skill selection:
  Claude uses it to choose the right Skill from potentially 100+ available Skills"**,
  **"Always write in third person"** (1st/2nd person causes *discovery problems*),
  **"Be specific and include key terms… what the Skill does and specific
  triggers/contexts"**, **"Build evaluations first"** (evaluation-driven development;
  verifiable `expected_behavior`), and **"The 'name' and 'description'… are
  particularly critical. Claude uses these when deciding whether to trigger the
  Skill"**; [Improving skill-creator — Claude Blog](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)
  (accessed 2026-06-28) — description tuning **"suggests edits that cut both false
  positives and false negatives"** and the empirical result **"improved triggering on
  5 out of 6 public skills"**. Catalogue: `research/13-skill-description-evals.md`
  (should-trigger/should-not pair, 3 runs ≥2/3, 60/40 split, explicit exclusion
  clause) and `01-agent-skills.md`.
- **Rejected/superseded:** discarded **importing the full skill-creator algorithm**
  (generate ~20 synthetic prompts, 3 runs each, 60/40 train/held-out split, 5
  iterations) as a method step — it is the product of the owner skill
  `skills-skill-creator` (Simplicity First; the method **detects** the collision and
  weak trigger, it does not run the eval harness). The 60/40 and ≥2/3 numbers live
  only in the catalogue, not in the template — the official source (skill-creator
  blog, ⚠️ verified by WebFetch) **does not** publish those numbers in its own docs
  (they come from dated community coverage in the catalogue); the template anchors
  only what the official docs state (3rd person, key terms, evaluation-first,
  false-positive/false-negative). Discarded creating a **new dimension** for trigger
  — it is a refinement of existing dimension 6, not a new surface; the **collision
  between skills** enters as cross-cutting 6b instead of becoming its own dimension,
  to avoid inflating the count (stays at 15 dimensions).
- **Next candidate:** "Skills vs sub-agents vs commands — selection guide"
  (dim 6/7/9 — catalogue `02-subagents.md`/`05-slash-commands.md`/`09-building-effective-agents.md`)
  or "Progressive disclosure / context budget" (sharper size criterion for
  SKILL.md/CLAUDE.md — catalogue `07-context-engineering.md`).
