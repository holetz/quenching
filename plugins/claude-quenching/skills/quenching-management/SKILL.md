---
name: quenching-management
description: >-
  PORTABLE, SELF-CONTAINED method + installer for knowledge management on the
  Claude Code surface of ANY repository. Derives the target repo's shape,
  confronts it with an adaptable template of dimensions (map/CLAUDE.md,
  standards, vision, backlog, ADR, skills, sub-agents,
  hooks, commands, memory, catalog, boundary doctrine, conventions,
  guardrails, MCP), produces a prioritized gap report and, WITH CONFIRMATION,
  INSTALLS the own artifacts it carries (skills, sub-agents, hooks, doc
  skeletons, frontmatter templates — in `assets/`) into the target's
  `.claude/`/`docs/`, also flagging which pre-existing skills/artifacts become
  DEPRECABLE because they are covered by the package. Does not depend on any
  external skill. Use WHENEVER the user asks to "organize/audit the repo's
  knowledge base", "install the knowledge base for Claude Code", "prepare a
  repo from scratch for Claude", "review the docs/skills/hooks/agents/CLAUDE.md",
  "see what's missing from the knowledge base", "apply the knowledge management
  method", "organize the .claude/ structure" — or when they describe
  mess/gaps in the knowledge surface (docs, skills, rules, memory, agents,
  hooks, MCP).
when_to_use: >-
  audit, install and organize a repo's knowledge base for effective use with
  Claude Code (CLAUDE.md, docs, skills, agents, hooks, commands, memory,
  boundaries, MCP) — portable, without depending on external skills.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# Knowledge management — portable method + installer (Claude Code)

> **Way back:** plugin overview & full method docs →
> [../../README.md](../../README.md). This file is the **agent's roadmap** (the 8
> steps); the detail for each step is in [references/](references/README.md).

**Self-contained** and **portable** method that organizes the **knowledge
surface** of any repository for effective use with Claude Code. Reads the
target repo, **derives its current shape**, confronts it with an **adaptable
template** of dimensions, delivers a **prioritized gap report** and, **with
confirmation**, **installs the own artifacts** this package carries.

> **Self-contained (core principle):** everything the method needs to
> **audit and install** lives **inside this skill**, in [assets/](assets/) —
> owner skills, sub-agents, hooks, doc skeletons and frontmatter templates.
> **Nothing** here references a skill, an agent or a specific path from another
> repo. When applied, the method **stamps** those artifacts into the target's
> `.claude/`/`docs/`. Payload manifest:
> [assets/README.md](assets/README.md).

## Operation model: installer + knowledge generator

`audit-by-default + install-with-confirmation`. The method **always** delivers
the report first. Installation is an **explicit second step**, item-by-item,
with the user's OK, and **always uses the package's artifacts** (`assets/`),
not the repo's. Where the repo **already has** an artifact doing the same job,
the method **does not duplicate silently**: it **installs the package's one**
(the single, versioned, evolved source here) and **flags the pre-existing one
as DEPRECABLE** in the report, leaving removal as the user's decision. See
[references/installation.md](references/installation.md).

**Beyond structure, the method GENERATES knowledge** — it is **intrusive where
there are gaps**, bringing the repo to the exact canonical harness, in **three
regimes by dimension type** (single source:
[references/module-contract.md](references/module-contract.md) part 3):

- **Derived-content** (dim 2 standards, incl. dim 13's writes in the standards
  home) — the method **mines the repo and WRITES the standard itself**, running
  the [quenching-writer](assets/agents/quenching-writer.md) fan-out as
  **method-run sub-agents** (not only installing them for the maintainer to run
  later). Every `current` rule is anchored at `file:line`; anything not
  de-facto-proven enters as `authority: background` (a proposal, never asserted
  current). This transcribes what the code already does — **description, not
  direction**.
- **Human-direction** (dim 3 vision, 10 memory, 12 boundary) — the method
  **DRAFTS** the text from observable signals (git history, README/goals,
  backlog/ADR) and writes it labeled `authority: background` + a "DRAFT — pending
  human ratification" banner. It **never** asserts direction as ratified truth; a
  **human ratification gate** promotes it (Step 6).
- **Structural** (dim 1 CLAUDE.md map file, dim 11 catalog) — install / migrate /
  re-stamp / regenerate only; catalog generators are repo-specific, the map stays
  a thin pointer.

The invariant is **not** "never content" — it is **never assert DIRECTION as
ratified truth**. Derived description the method writes; direction it only drafts
for the human to ratify.

The confirmation contract has **two modes**, recorded in the target's install
manifest and granted/revoked only by the human
([references/lifecycle.md](references/lifecycle.md) §3): **`advise`** (default —
everything above, per-item OK) and **`managed`** (explicit opt-in — a standing
consent for the maintenance loop to apply, without per-item re-confirmation,
**only** the bounded reconcile classes: upgrade of an already-approved
artifact, re-wiring of a rotted one, manifest hygiene — every apply
audit-trailed and git-reversible). Human-direction drafts (Step 6),
deletions/renames and first installs of new payloads **never** enter `managed`.

> **Why self-contained (not delegation):** a previous version of this method
> *delegated* editing to skills that had to pre-exist in the repo. This made it
> **coupled** — only worked where those skills already existed. The current model
> carries the capabilities inside itself: runs on a repo from scratch, is the
> **single source** of the artifacts it installs **and the engine that generates
> the derived content**, and keeps them coherent via its own evolution loop,
> maintained outside the shipped package.

## Opening protocol — one-line self-introduction (before Step 1)

**Always open the dialogue with a single-line self-introduction** that states
**who this method is and its current version**, then the report-first promise.
Read the version from the **bundled `VERSION` file shipped at the plugin root**
— `${CLAUDE_PLUGIN_ROOT}/VERSION` (or `../../VERSION` relative to this file); it
holds the current version string (a **dev build is the short commit hash**, kept
fresh by the repo's version-stamp hook). If the file is absent or unreadable,
introduce **without** a version — never block on it.

Keep it to **one line**, e.g.:

> 🔥 **quenching-management** `v<version>` — portable knowledge-base audit +
> installer for the Claude Code surface. I audit first and report; nothing is
> installed without your item-by-item OK.

The greeting **does not** change the operation model: the report still comes
first (Step 4), installation stays explicit and item-by-item (Steps 5-7).

## Steps

### 1. Derive the current shape of the target repo (read-only, adaptable)

Before confronting with the template, **learn the repo's own conventions** —
the template adapts to them, not the other way around. **Do not assume paths**;
discover:

- Locate the `CLAUDE.md`(s) (root and sub) and read the root one: what
  boundary doctrine (map × current × vision × adr) is already
  crystallized?
- Discover where (if they exist) the **knowledge layers** live: standards,
  vision, backlog, ADR, catalog. Use
  the adaptive globs from [references/detection-and-smells.md](references/detection-and-smells.md)
  — they **derive** the real path, do not assume `docs/arquitetura/` etc.
- Inventory what already exists in `.claude/` (skills, agents, hooks, commands)
  and the naming language/taxonomy the repo uses.

Summarize in 1-2 lines the **derived shape** (language, prefix taxonomy,
current boundary doctrine, where each layer lives). **Where the repo already
has a convention, the repo's convention wins** — the method adapts the
names/paths of the artifacts it installs to fit it. **Also note the profile
signals** that will modulate the report's emphasis (Step 4): monorepo/large
codebase, already populated `.claude/` surface × repo from scratch, many
external services, PRs/conventions in rotation — each weighs which
dimensions/triggers/payloads yield **more** for **this** repo.

### 2. Inventory each dimension

Run the adaptive globs/greps from
[references/detection-and-smells.md](references/detection-and-smells.md) (via `Bash`
read-only, `Glob`/`Grep`) and collect evidence per dimension. The 15 dimensions
and what each covers — with the **package artifact** that addresses it — are indexed in
[references/dimensions-template.md](references/dimensions-template.md) (one file per
dimension under `references/dimensions/`; open only the one you are scoring).

> **Optional fan-out (clean context):** for large repos, delegate the scan
> to the read-only sub-agent the package carries
> ([assets/agents/quenching-auditor.md](assets/agents/quenching-auditor.md)) —
> it runs in its own window (`Read/Grep/Glob`, cheap model, `permissionMode:
> plan`) and returns only condensed evidence, without flooding the main context.

### 3. Score each dimension

Assign one of four states, **citing `file:line`** as evidence
(concrete evidence, never impression):

- **Present** — exists and is healthy.
- **Partial** — exists, but incomplete.
- **Drifted** — exists, but lies / is outdated (index cites non-existent file,
  broken link, completed item still in tree, etc.).
- **Absent** — does not exist and **should**, given the derived repo shape.

### 4. Produce the prioritized gap report

Use the skeleton from [references/report-format.md](references/report-format.md):
scorecard per dimension → prioritized gaps (P1/P2/…) → **deprecable
skills/artifacts** → installation plan. Priority = severity (drifted/broken
> absent > partial) × cost × whether there's a ready payload in the package
(installable = cheaper, moves up the queue) **× profile-weight** (below).

#### Emphasis modulation by repo profile (fit-to-repo guidance)

The 15 dimensions are a **uniform coverage checklist** — but two repos don't
need the same investment. Confronting **every** repo with **all** dimensions at
equal weight ignores the derived shape from Step 1 and what the repo actually
**needs**. So the report doesn't treat gaps as a flat list: it **modulates
emphasis** by the **derived profile** (shape + need), because
*"you don't need to configure everything upfront — each feature has a
recognizable trigger… start with CLAUDE.md… and add the others as the triggers
appear"* and because *"every feature you add consumes context; too many can
fill the window, but also add noise… skills may not trigger, Claude may lose
sight of your conventions"*. Investing in a dimension the repo **doesn't show
a trigger for** is the same waste as omitting one it does show.

Modulation is a **profile-weight** applied to prioritization, **not** a filter
that hides dimensions: every dimension stays in the scorecard (full coverage),
but the P1/P2/… queue and installation plan gain a **"For THIS repo, invest
first in…"** block with 2-4 dimensions/triggers/payloads of **highest
leverage** given the derived shape, **with the observed trigger's justification**
(`file:line` or the Step 1 fact that evidences it). Profile signals → emphasis
(examples, not exhaustive):

- **monorepo / large codebase** → dim 1 (per-scope sub-CLAUDE.md, `paths`
  rules), fan-out to auditor sub-agent, rollout plugin — *"a second repository
  needs the same setup → package it as a plugin"*.
- **already populated skills/agents/hooks surface** → dims 6/7/8 (bloat,
  trigger, wiring) rise; repo **without** `.claude/` yet → dim 1 + dim 2
  first, hooks **later** (*"start with CLAUDE.md"*).
- **many external services / data outside the repo** → dim 15 (MCP) rises.
- **high convention rotation / frequent PRs** → trigger (1) of Step 8
  (PR hook) and dim 14 (guardrails) rise.
- **repo from scratch** → emphasis shifts from *which* dimensions to the
  **order that unlocks them**; the **canonical sequence** (foundation → skills
  → MCP → hooks → plugin) has a unique home in the "Base-Order" of
  `quenching-roadmap` (below), which the report fires instead of re-writing the
  order here.

The named profile catalog (observable signals → recommended emphasis) is in
[references/repo-profiles.md](references/repo-profiles.md) — a **free example
guide, not an enum**: a repo matches several profiles or none (emphases add
up), it's a prioritization heuristic, never a gate.

When the "invest first in…" block needs to become an **actionable sequence**
("invest first in X, **then** Y, **then** Z") — greenfield/from-scratch repo or
many gaps without order —, the package carries the **read-only** payload
[assets/skills/quenching-roadmap/](assets/skills/quenching-roadmap/SKILL.md):
it reads the derived shape + profile + scorecard and **PROPOSES** the **order
of investment in the METHOD/structure** (which artifact to install first, which
trigger to wire first) by **leverage × cost × prerequisite** (map/dim 1 and
boundaries/dim 12 before hooks; observed trigger before payload). Proposes the
**order**, **never the content**; installation follows item-by-item with OK
(Step 5).

> **This is PROPOSING/PRIORITIZING, not IMPOSING or defining content.** Modulation
> reorders and **recommends where the method yields more** for **this** repo —
> **probabilistic** guidance about the METHOD itself (which dimension/trigger/
> payload to invest in), not enforcement or **content/direction** decisions
> (direction is only **drafted** in Step 6 and **ratified by the human**, never
> decided by the method). Profile-weight **does not invent a gap** (it
> comes from Step 3 evidence), **does not hide** any from the scorecard, and
> **does not decide** what the repo's memory/VISION/boundary should say. Modulating
> the method's emphasis ≠ defining the repo's content: the first is "for you, it's
> worth sharpening dim 6"; the second would be "your VISION is X" — only the first
> is the method's work. The recommendation is **always** anchored in an
> **observed** trigger (Step 1/3), never in the curator's preference.

### 5. Propose — and, with confirmation, install from the package

For each gap, point to the **package artifact** that resolves it
([references/installation.md](references/installation.md)). Only after the user's
OK, **item-by-item**:

- **Install** the payload from [assets/](assets/) into the target's destination
  (adapting name/path to the derived shape) — copy a skill-template to
  `.claude/skills/<name>/`, a sub-agent to `.claude/agents/`, a hook to
  `.claude/hooks/` + entry in `settings.json`, a doc skeleton to the right
  layer, a frontmatter template where missing.
- **Adapt** the installed artifact to the repo's conventions (prefixes, paths) —
  the package is the starting point, not a rigid mold. Payloads are **authored
  in English**, and the **agent-facing knowledge surface stays English on
  install** — do **not** translate bodies, titles or section headings. The
  dividing line is the **`audience:` axis**: `agent`/`both` docs (all
  `docs/standards/**`, every `CLAUDE.md`, the `.claude/` skills/agents/hooks, and
  all frontmatter keys+enums) stay English so the surface is uniform, stable and
  cross-repo greppable; **`audience: human`** material (`presentations/`,
  `communications/`, human-only `guides/`) **may** follow the repo's own language.
  The target's **product code, docstrings and business content are never touched**
  — they stay the repo's business. (Structural identifiers — canonical `docs/`
  folder names and frontmatter keys — were already English by taxonomy; this rule
  now covers the prose around them too.)
- The method **edits the target's `.claude/`/`docs/` directly**, but **only**
  what the approved item asks; keeps generated artifacts intact (`*.job.yml`,
  manifests, AUTO-GENERATED catalog or equivalent).
- **Record every installed item in the install manifest**
  (`.claude/quenching-manifest.json` — template in `assets/templates/claude/`,
  doctrine in [references/lifecycle.md](references/lifecycle.md) §1): payload
  id, package version, destination, and each deliberate **adaptation** — the
  receipt that lets the maintenance loop later tell *upgradable* from
  *intentionally adapted* instead of guessing.
- **Generate the derived standards content (dim 2) — a second phase, with its own
  grant.** Installing the scaffold is **not** the end for the standards layer:
  once its structure is approved, the method **populates it itself** — it fans out
  the [quenching-writer](assets/agents/quenching-writer.md) discipline as
  **method-run sub-agents, one per applicable subject** (the
  [quenching-standards](assets/skills/quenching-standards/SKILL.md) orchestration,
  run **inline** — not merely installed for the maintainer to run later), each
  mining the repo and **writing its standard** — every writer **evaluates its
  candidate sub-standards** (generate each applicable concept as its own file,
  record the rest as deferrals). It fires **after the report and an
  enumerated generate-grant** (the report lists every absent/empty subject to fill,
  each with its `file:line` anchor; **one OK** authorizes generating them all —
  [references/lifecycle.md](references/lifecycle.md) §3 `generate-derived`), never
  as part of the cheap read-only audit. Rails: `current` is anchored at
  `file:line`, unproven → `authority: background`; the writer writes **only under
  `docs/standards/`**; an **existing authored body is merged/enriched, never
  overwritten** (rewriting a body is a **per-doc OK**); **adversarial review is
  mandatory** before merge and **one subject is generated first to calibrate**.
  This is the inverse of the DOMAIN-artifact callout below (which proposes a
  skeleton only): the standards layer is the **portable** layer the method fully
  populates.
- **Verify every apply against canon (the gate).** An install, migration or
  re-stamp is **not "done"** until you **re-run that dimension's own detection on
  the just-written output** and it comes back **clean**. A non-empty result — a
  mandatory-incomplete / OKF-non-conformant standard, a variant folder left
  un-migrated, a missing front-door, an `INDEX.md` without
  `<!-- BEGIN/END GENERATED -->` or out of sync with disk — means the apply is
  **incomplete**: loop on the missed items or
  **flag it loudly**, never report success. *"Applied"* is a claim that must
  **pass its own greps**, not an assumed side effect — this is what stops an
  install reporting success while the output stayed non-canonical. The
  per-dimension contract is [references/module-contract.md](references/module-contract.md)
  (part 4, the verify gate); human-direction dims 3/10/12 verify the **labeled
  DRAFT** (`authority: background` + banner), never a `current` claim (Step 6).

> **Reference sections by ROLE, not by title.** Agent-facing headings stay
> English (above), but a repo may still **rename or reorder** them to fit its own
> outline — so any method doctrine or hook payload that keys on a CLAUDE.md
> section still matches it by **role** or a language-neutral signal (e.g. the
> changed files a validation hook reads via `git status`), **never** by a brittle
> literal heading string.

> **DOMAIN artifact guided by need (propose, not install).** Beyond the generic
> `knowledge-*` payloads the package **installs** (portable), the method
> **recognizes** when a **recurring domain need** of the target justifies a
> **skill/sub-agent OWNED by that repo** — a repeated multi-step manual
> procedure in its history, a type of domain task that recurs, or a family of
> commands/runs (trigger observed in Step 1; criterion in **dim 6/7** of the
> template). Here the method **PROPOSES the skeleton** (name + trigger-description
> + skill×sub-agent home + empty `references/`) and **leaves the CONTENT of the
> domain procedure for the repo to fill in** (human decision, like Step 6).
> The package **does not carry** ready domain skills/sub-agents — they would be
> coupled to a repo, breaking self-containment; it teaches how to **recognize the
> trigger** and sketches the **form**, never the content.

### 6. Human-direction dimensions → draft, label, and let the human ratify

Three dimensions encode **direction/judgment**, not derivable description: **3
(vision)**, **10 (memory)** and **12 (boundary doctrine)**. For them the method
**drafts** the content from **observable signals** (git history, README/goals,
the backlog/ADR trail, the boundary already crystallized in CLAUDE.md) using the
[direction-draft discipline](assets/agents/quenching-direction.md), and **writes
the draft into the canonical home** clearly **labeled as a draft** — an
`authority: background` doc in `vision/`, a plainly-marked draft entry for
memory/boundary — with a **"DRAFT — pending human ratification" banner** at the
top. For boundaries it also drafts **which is the canonical home and what becomes
just a link** in the other artifacts.

It **never** marks any of this `current` and **never asserts the direction as
ratified truth**: a **human ratification gate** stands between the draft and any
authoritative status. This is the **inverse** of the derived-content regime
(Step 5) — there the method writes `current` because it transcribes proven
de-facto reality; here it can only **seed a draft**, because *where the project is
going* and *what the team's boundary doctrine is* are human calls the code cannot
prove. An evidence-seeded draft is a strong starting point, **not** a decision.
The `draft-direction` consent class **never** enters `managed` and **always**
requires the ratification gate ([references/lifecycle.md](references/lifecycle.md)
§3) — **even a bulk generate-grant does not cover it** (that grant is scoped to
derived standards content only).

### 7. Flag what became deprecable

When installing a package artifact that covers something already present in the
repo, list the pre-existing one in the **"Deprecable"** section of the report:
what it did, which package artifact replaces it, and what the user gains by
removing it (a single source instead of two). **Never remove** the old
skill/artifact without explicit OK.

### 8. Establish the recurring maintenance cycle (the base is alive)

Auditing **once** (Steps 1-7) leaves the base fresh **today** — but it
**rots** as the code, models and team change (*context rot*, dimension 1). So
the method doesn't end with the report: it **installs the recurring operational
loop** that keeps the surface fresh, with **three documented triggers**
(drift-event × cadence) and the **right home** for each one (dimension 12
applied to maintenance):

- **On event, in the PR (drift trigger):** treat editing CLAUDE.md/docs
  like any other doc change — *"treat CLAUDE.md edits like any other
  documentation change so conventions track the code"*. The home is a **PR
  hook** that, when touching the knowledge surface, **re-runs detection of the
  touched scope and PROPOSES** (does not block) the gaps — continuous audit
  (dim 8) + actionable error (dim 14). It is the recurrent backlog item of
  the target repo's dim 4.
- **On cadence, at model release (review trigger):** revisit after a new
  model — *"instructions that worked around an older model's limitation may
  become overhead once a newer model handles the case on its own"*. Crosses
  with *outgrowth detection* (skill/rule the base model already does on its
  own ⇒ deprecable) and the dim 1 pruning criterion. **But what rots is not
  only the base's CONTENT — it's also the EMPHASIS/PROFILE** (dimension 1,
  *context rot*, applied to Step 4 prioritization): *"keep the files current
  as the codebase and models change"* — and *"the same triggers tell you when
  to update what you already have"*. **A repo's profile is ALIVE:** a
  greenfield becomes mature, a lib gains a service, a data-pipeline incorporates
  MLOps — and when the shape changes, the recommended emphasis (Step 4) and the
  roadmap order (`quenching-roadmap`) **no longer fit**. So this trigger
  **re-runs profile derivation (Step 1) + emphasis modulation (Step 4) + the
  roadmap** against today's state, not just prune individual rules: it delivers
  *"given how the repo HAS EVOLVED since the last audit, now invest in…"* —
  re-prioritizing **which dimensions/payloads** to invest in, **never**
  rewriting content (VISION/memory; only Step 6 proposes the home). The
  `quenching-roadmap`, being **read-only and re-runnable**, is the very
  input to **re-sequence** at each release/review — no new artifact needed,
  just **fire it again** with the current shape.
- **On demand, by command (manual trigger):** a **`/<re-audit>` command**
  fires the re-examination when the operator wants — re-runs Steps 1-7 (or
  the scope the argument requests) and, for large repos, delegates to the
  **auditor sub-agent in clean context**
  ([assets/agents/quenching-auditor.md](assets/agents/quenching-auditor.md)).
  Because it's a manual-work-shortcut (not a side-effect), it is born as a
  **skill** with description trigger (dim 9: new command is born a skill), not
  a legacy command. With an install manifest present, it also runs the
  **reconcile scope**: classifies every installed artifact
  (Current/Upgradable/Adapted/Rotted/Orphaned) against the package and applies
  the outcome per the consent mode
  ([references/lifecycle.md](references/lifecycle.md) §2-3) — this is how the
  **installed harness itself evolves**, not just the docs it audits.

The **automatic freshness signal** between audits is the **evolutionary Stop
hook** (dim 8: reads the transcript at the end of the turn and proposes deltas
"while the gap is fresh") together with, where there is telemetry, the
`skill_activated`/`invocation_trigger` from OTel — *"which tells you what to
consolidate or retire"* (skill never fired = pruning candidate, dim 6). **This
section is the cycle's backbone**; the concrete payloads (the PR hook, the
`/<re-audit>` command, the ready Stop hook) are installable via Steps 5-7 and
mature in subsequent rounds — here lives **when, why and in which home** each
one runs, not the script.

#### Orchestration contract of links (hook → command → sub-agent → skill)

The cycle's pieces don't live in isolation: they **compose** into a flow (*"ask
Claude to use subagents in sequence… each subagent completes its task and returns
results to Claude, which then passes relevant context to the next"*). The method
doesn't improvise this composition — it operates under a **per-link contract**,
which is dimension 6 applied to the **running flow** (not to the static home
choice of authorship) and the boundary *workflow (predefined code path) × agent
(LLM drives)* applied to maintenance:

- **Hook = automatic trigger that OBSERVES / PROPOSES / at most BLOCKS — never
  mutates the base alone.** Fires by event, without request; reads and returns
  proposal (`additionalContext`) or deterministic record/veto. Proposing ≠
  applying: consistent with "the method **drafts** but never **ratifies**
  direction" (Step 6), only PreToolUse/*enforcement* decides, and only about
  generated artifacts.
- **Command/skill = on-demand step that APPLIES, with OK.** The operator (or
  the model, via composability) fires; only here does the base change,
  **item-by-item with confirmation** (operation model). It is the link that
  closes what the hook only proposed.
- **Sub-agent = isolated context that returns CONDENSED SUMMARY.** *"The
  subagent does that work in its own context and returns only the summary"* — the
  scan link (re-audit of large repo) runs in a clean window and comes back
  **condensed** to the loop, never dump.

> **Anti-pattern — chaining too much (Simplicity First).** A hook that invokes
> a command that triggers a cascade of sub-agents **without a human barrier**
> violates the contract: *"add multi-step agentic systems only when simpler
> solutions fall short"* and *"agents pause for human feedback at checkpoints"*.
> The barrier is double: **human** (the link that mutates the base always has OK
> — the hook proposes, the human confirms) and **deterministic** (the runtime
> itself caps the recursion — *"a subagent at depth five… can't spawn further.
> The limit is fixed"*). Always distinguish the **enforcement** link
> (deterministic: blocking hook, depth cap) from the **guidance** link
> (probabilistic: proposing hook, judgment skill) — dims 1/8/14. **End-to-end,
> Step 8 closes like this:** automatic freshness = hooks that OBSERVE/PROPOSE;
> re-examination = composable command + sub-agent in clean context; **base
> evolution = only in the link with confirmation.**

## References

- [references/README.md](references/README.md) — **folder index**: what each
  file is, when to open it and how they chain (start here to navigate).
- [references/dimensions-template.md](references/dimensions-template.md) — the
  adaptable template: the **index** of the 15 dimensions (one file each under
  `references/dimensions/`, with purpose / "good" / detection / smells / remediation /
  **package artifact**) plus the transversal doctrine.
- [references/docs-taxonomy.md](references/docs-taxonomy.md) — the **canonical
  `docs/` taxonomy** (single source of the tree + boundaries + variant migration).
- [references/scripts-taxonomy.md](references/scripts-taxonomy.md) — the
  **canonical `scripts/` taxonomy** (home of executable logic: purpose subfolders
  + README-map + the thin-hook-calls-script boundary × skill-internal × repo).
- [references/detection-and-smells.md](references/detection-and-smells.md) — the
  detection **cookbook**: the **adaptive** globs/greps per dimension (derive
  the target's path) + the rule of 4 states; doctrine lives in the dimensions.
- [references/installation.md](references/installation.md) — gap → package payload
  map + the **deprecation** doctrine for what the repo already had.
- [references/lifecycle.md](references/lifecycle.md) — the **conduction layer**:
  install manifest (receipt), reconcile/upgrade classes, consent modes
  (`advise` × `managed`) and distribution channels (stamp × plugin rollout).
- [references/repo-profiles.md](references/repo-profiles.md) — lightweight and
  **non-closed** catalog of repo profiles (signals → emphasis) that Step 4
  consults when modulating priority (fit-to-repo guidance).
- [references/report-format.md](references/report-format.md) — audit
  report skeleton (scorecard · gaps · deprecables · installation plan).
- [assets/README.md](assets/README.md) — installable payloads manifest.
