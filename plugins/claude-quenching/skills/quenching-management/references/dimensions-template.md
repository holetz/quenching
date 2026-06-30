# Adaptable knowledge management template — the dimensions

> **Back path:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> human overview & architecture: the project docs site ·
> [README.md](README.md) (`references/` index).

> **ADAPTABLE — read this first.** This template **does not impose a foreign
> structure**. The method first **derives** the conventions from the target repo (Step 1
> of [SKILL.md](../SKILL.md): locates CLAUDE.md, discovers where each knowledge layer
> lives, inventories `.claude/`, reads the language/taxonomy) and only then
> confronts the dimensions below. **Where the repo already has its own convention, the
> repo's convention wins** — with **one exception**: the **names of `docs/` homes**
> (dim 2/3/5/11) are a **prescriptive canonical taxonomy**
> ([docs-taxonomy.md](docs-taxonomy.md)); there the repo **converges to the canonical name**
> (the variant name is deprecatable, **with OK** — never renamed without confirmation), not
> preserved as-is. The 15 dimensions are a **coverage checklist** (what a Claude Code-ready
> repo typically needs), not a rigid mold. In a greenfield repo, they become the roadmap to
> **install** the structure (stamping payloads from [../assets/](../assets/)); in an existing
> repo, they become the roadmap to **audit** what's there and **install** what's missing.

Each dimension has 6 fields:

- **Purpose** — what this artifact is for.
- **How "good" looks** — the healthy state (the audit target).
- **Detection** — where to look (operational detail, adaptive + bash, in [detection-and-smells.md](detection-and-smells.md)).
- **Smells** — signals of Partial/Drifted/Absent.
- **Remediation** — the concrete action.
- **Payload** — the artifact **from the package** ([../assets/](../assets/)) that the method **installs** to fill the gap; `—` = no payload, the method only proposes (human content decision).

> **`docs/` names are CANONICAL (dim 2/3/5/11), other paths are examples.**
> The `docs/` tree (`standards/`, `decisions/`, `vision/`, `backlog/`, `guides/`,
> `reference/`, `catalog/`, `communications/`, `presentations/`) is a **prescriptive
> canonical taxonomy** — single source in [docs-taxonomy.md](docs-taxonomy.md). In a
> repo with variant names (`docs/arquitetura/`, `docs/adr/`, `VISION.md`), the method
> **maps variant→canonical and PROPOSES the migration** (with OK), not preserving the
> repo's name. Paths **outside** `docs/` (`.claude/`, root) and the rule *«X defines Y»*
> (canonical source generates the artifact, the generated one is never hand-edited) are
> examples — derive/swap for the concrete pair of the repo in Step 1.

---

## 1. Entry map — CLAUDE.md

- **Purpose:** routing "what do I, the agent, do now / which file contains what". It is **always-loaded** (enters context at every session start, before the first message) — consumes **fixed** context budget. Its counterpart is **on-demand** (skills, subfolder sub-CLAUDE.md, `docs/`): only loaded when relevant.

- **How "good" looks:** root is a **map**, not a contract; within the repo's line ceiling (a hook validates — the package loads one: [../assets/hooks/validate-claude-md.py](../assets/hooks/validate-claude-md.py)); chains sub-CLAUDE.md by scope; every link resolves; short directive + link to the current/active detail, never the full detail.

  - **Pruning criterion (per line, verifiable):** *"if I remove this line, would Claude make a mistake?"* — if not, **cut** or **convert**: mandatory rule → hook (dim 8); procedure "when I do X, I follow Y" → skill (dim 6); detail that changes often → link.
  - **Always-loaded × on-demand boundary (decides the home):** only what applies **broadly** goes in CLAUDE.md; domain/flow knowledge only-sometimes-relevant goes to **skills** (loaded on demand, without bloating every conversation).
  - **`@import` does NOT save context** — it is expanded inline and counts against the budget equally; it only serves human maintenance of the file.
  - **The "common commands" the map documents are invocations of `scripts/`** — build/deploy/checks/dev that the agent cannot guess. CLAUDE.md cites the **single execution convention** (e.g., `python -m scripts.<package>.<module>`) + link to the `scripts/` map; the canonical home of those executables (organization by purpose, README-map) is dim 8 / [scripts-taxonomy.md](scripts-taxonomy.md), not CLAUDE.md.

  | Belongs in CLAUDE.md (✅) | Does NOT belong (❌) |
  | --- | --- |
  | commands Claude cannot guess | what Claude infers from reading the code |
  | style rules that differ from the default | standard language conventions |
  | test/runner instructions | detailed API doc (link instead) |
  | repo etiquette (branch/PR) | info that changes frequently |
  | **project-specific** architecture decisions | long explanation/tutorial |
  | environment quirks (env vars) | file-by-file description |
  | non-obvious gotchas | obvious practice ("write clean code") |

- **Detection:** `find . -name CLAUDE.md`; read root; check ceiling hook and whether it points to an existing script; run the pruning criterion line-by-line (item **1b** in [detection-and-smells.md](detection-and-smells.md)).

- **Smells:**
  - above the repo's ceiling; became a **contract** (long normative rule instead of a link); broken link; outdated tech stack.
  - **orphan sub-CLAUDE.md** (exists but the root doesn't point to it) or **pointed to but nonexistent**.
  - **rule that survives the pruning criterion** — a line that, if removed, would not change behavior (model default, style already in the linter, obvious practice).
  - **mandatory rule in prose that should be a hook** — guidance ≠ enforcement (CLAUDE.md is a guide, not enforcement).
  - **context rot / fossil** — a directive describing a **replaced** pattern (the normative reference changed and the map didn't follow), poisoning the context loaded in every session.

- **Remediation:** trim to a map; break into sub-file; fix/retarget link; **prune** the line that doesn't pass the criterion; **convert** mandatory rule to hook (dim 8) or long procedure to skill (dim 6); **update** the fossil to point to the current/active pattern.

- **Payload:** skill-template [../assets/skills/quenching-map/](../assets/skills/quenching-map/) (hygiene/pruning/chaining of CLAUDE.md) + hook [../assets/hooks/validate-claude-md.py](../assets/hooks/validate-claude-md.py) (line ceiling) + template [../assets/templates/claude/claude-md.md](../assets/templates/claude/claude-md.md).

## 2. Normative reference — the current/active standards layer (`docs/standards/`)

> The complete `docs/` tree (all homes + subfolders, purpose, Diátaxis,
> `audience`/`authority`, boundaries) is the **prescriptive canonical taxonomy** — single
> source in [docs-taxonomy.md](docs-taxonomy.md). This dimension gives the short directive +
> the smells; **do not copy the tree** (Simplicity First) — link.

- **Purpose:** the **current/active** standard/contract (how it should be and why), versioned — the shared source of truth. Canonical home **`docs/standards/`** (subfolders by subject: `architecture/`, `code/`, `naming/`, `data-modeling/`, `ci-cd/`, `workflows/`, `mlops/`, `quality/`, `platform/`). It is **one home** of the taxonomy, not the whole `docs/`.

- **How "good" looks:**
  - subfolders by subject; **`INDEX.md`** in sync (lists exactly the docs that exist); minimal frontmatter (`title`/`updated`/`status: current`/`audience`/`authority`); **one standard per file**; names in **English kebab-case**.
  - **Home = subject** (subject-first); **content inside the home = Diátaxis** (reference/explanation here).
  - **Canonical convergence:** the skill defines the taxonomy; the repo **converges to it** — every repo in the **SAME tree of identical names**, so someone moving between repos sees the tree **literally identical** (instead of re-mapping "by function"). Variant name (`docs/arquitetura/`, `docs/adr/`) is a **non-convergence smell** → migration candidate, not a convention to preserve.
  - **Variant migration (deterministic, safe):** map variant→canonical, **flag as DEPRECATABLE** and **PROPOSE** — **never rename/delete without OK** (Step 5 confirmation + deprecation doctrine).
  - **Label + binary by sidecar:** `audience: both`/`agent` · `authority: current`/`background`; the LLM reads the `.md` extract, never the `.pdf`/`.pptx` — part of the taxonomy (see [docs-taxonomy.md](docs-taxonomy.md)).
  - **Complete for agent = passes the reconstruction test** (Augment Code "rebuild test"): a new agent reconstructs the behavior **solely from the doc**, without asking the human. For this, the standard carries the **requirement** (*what* applies) **AND** the **decision** (*why* + alternatives; a requirements-only doc regenerates different behavior every time).
  - **Current/active is de-facto proven, anchored in `file:line`** — external best practice the repo does NOT follow is a **PROPOSAL/GAP** (`authority: background`), never stated as current/active.
  - **`INDEX.md` is a DERIVED artifact** — regenerated from disk between `<!-- BEGIN/END GENERATED -->` markers (rule «X defines Y»), not hand-written; structural drift becomes impossible by construction.

- **Detection:** derive against the **canonical names** first (Step 0); cross-reference the `INDEX.md` list with actual files; `grep` for pointers to old paths; detect variant names (`arquitetura/`/`adr/`/`VISION.md`); check for missing canonical homes; check audience+provenance label per doc/folder; check `.md` sidecar next to each binary and that no sidecar has `authority: current` — item **2b** in [detection-and-smells.md](detection-and-smells.md).

- **Smells:**
  - **index lies** (cites nonexistent doc / missing new doc); **index hand-edited diverging from disk** (should be regenerated between `<!-- BEGIN/END GENERATED -->`); standard without short directive in CLAUDE.md; direction or open-decision mixed in here; doc without frontmatter.
  - **non-converged variant name** — `docs/arquitetura/`, `docs/adr/`, single `VISION.md`, `docs/patterns/` as a silo = migration candidate (not "repo convention that wins").
  - **`docs/` without canonical segmentation** — loose technical markdown at the root of `docs/`, without named homes (the agent sweeps everything).
  - **TWO-HOMES** — `docs/arquitetura/` AND `docs/standards/` coexisting, or `adr/` AND `decisions/`: single-home violation (dim 12), one migrates to the other.
  - **human material leaking into the technical layer** — slides/diagrams/PDFs in `standards/` or at the root, without the `presentations/`/`reference/` home.
  - **doc without declared audience/authority**; **human/external material marked as current/active** (slide/PDF/standard without `authority: background` cited as a contract).
  - **binary without sidecar/extract** (the agent would ingest the binary, ~7x tokens, low signal); **sidecar without provenance or marked as current/active**.
  - **repo section without canonical home** (`NO-HOME`) — technical folder that doesn't match any home (home to be added, or material in the wrong quadrant).
  - **directed communication outside its home** — incident/change/deploy notice loose at the root, in `guides/`/`standards/`, without the `communications/` home; **channel without template** (`communications/templates/<channel>.md` absent, form becomes ad-hoc); **communication without a scannable header** (without scope/status/impact/audience/validity/action/last-updated); **communication marked as current/active** (should be `authority: background`; what became a rule **distills to `standards/`**).
  - **standard stated as `current/active` WITHOUT `file:line` anchor** — external best practice promoted to contract without proof the repo follows it (capability/outcome hallucination risk).
  - **`standards/` layer with only an empty skeleton** — homes exist but were never populated from the repo.

- **Remediation:** sync `INDEX.md`/pointers; move direction→`vision/` or decision→`decisions/`; **install the canonical taxonomy** (procedure in [installation.md](installation.md)): map each section to the **canonical** home by function, **propose the variant migration** (deprecatable, with OK), install only the absent homes **that apply**, move each material to the right home (technical→`standards/`/subject; human→`presentations/`; external→`reference/`); **label** each doc/folder with audience+provenance; **create the sidecar/extract** next to each consulted binary — or, for reference-only material, **a folder index**, without extracting for the sake of it.

- **Payload:** (the canonical tree is specified in [docs-taxonomy.md](docs-taxonomy.md))

  - **authoring/editing ONE doc** → skill-template [../assets/skills/quenching-docs/](../assets/skills/quenching-docs/) (docs-as-code: authoring + index sync) + **canonical taxonomy skeleton** [../assets/docs/](../assets/docs/) (second agent scaffold) + **audience+provenance frontmatter** [../assets/templates/docs/docs-front.md](../assets/templates/docs/docs-front.md) + **sidecar/extract** [../assets/templates/docs/sidecar.md](../assets/templates/docs/sidecar.md).
  - **building/updating the ENTIRE `standards/` layer** (≠ authoring ONE doc) → **orchestrating skill** [../assets/skills/quenching-standards/](../assets/skills/quenching-standards/) + **parallel worker** [../assets/agents/quenching-writer.md](../assets/agents/quenching-writer.md): fan-out of one `quenching-writer` per subject in parallel (each one mines the de-facto = `current/active` anchored in `file:line` + external research, gap = **PROPOSAL**, never current/active) and **deterministically regenerates `INDEX.md` from disk** (between markers). Composes with `quenching-docs`, does not duplicate.
  - **directed communication** (`communications/` home) → **skeleton** [../assets/docs/communications/](../assets/docs/communications/) (`README` + `templates/` per channel `email`/`chat`/`wiki`/`markdown` + `archive/`) + **generic skill** [../assets/skills/quenching-announcement/](../assets/skills/quenching-announcement/) that reads the requested channel template and fills it in (not one per subject).
  - **runtime enforcement** (crosses dim 8) → **PostToolUse hook** [../assets/hooks/propose-docs-home.py](../assets/hooks/propose-docs-home.py): when touching a file under `docs/`, **proposes** the absent canonical home/slot reusing the criteria from block 2b.

## 3. Direction — `docs/vision/`

- **Purpose:** where the platform is headed (target state, "what and why"), without a timeline. Canonical home **`docs/vision/`** — folder **segmented by area** (one shell per pillar), not a single `VISION.md`.

- **How "good" looks:** one shell per area/pillar (starts empty + comment declaring the pillar); stable pillars; **no milestones/dates/ordering** (direction has no deadline); explicit non-goals. Single `VISION.md` at root/`docs/` is a variant name (migration candidate to `docs/vision/`).

- **Detection:** read the shells under `vision/`; look for dates/milestones/ordering; detect single `VISION.md`/`ROADMAP.md` as a variant to migrate.

- **Smells:** dates/milestones infiltrated; became a backlog (task list); outdated vs. reality (what's already current/active still appears as a target); **single `VISION.md`** instead of the segmented folder (variant).

- **Remediation:** remove deadlines; move "what's still missing" → `backlog/`; distill what became reality → `standards/`; segment single `VISION.md` into shells by pillar under `vision/` (propose, with OK).

- **Payload:** — (no content payload; the method **only proposes** the diff). The `vision/` skeleton (empty shells by pillar) is part of the canonical scaffold [../assets/docs/](../assets/docs/), materialized by the second agent. Specification: [docs-taxonomy.md](docs-taxonomy.md).

## 4. What's missing — backlog

- **Purpose:** trackable items of what's still missing, by pillar/area.

- **How "good" looks:** tree by pillar; completed item **leaves the tree** (history stays in git); reference to direction (e.g. `vision_refs`) pointing to the VISION section; no deadline/ordering.

- **Detection:** locate the backlog tree; check items whose work has already been done.

- **Smells:** completed items accumulating; deadlines/ordering; duplicates an ADR; no reference to direction.

- **Remediation:** remove completed item; create missing item with reference to direction.

- **Payload:** skill-template [../assets/skills/quenching-docs/](../assets/skills/quenching-docs/) (covers backlog) + skeleton [../assets/docs/backlog/](../assets/docs/backlog/) + template [../assets/templates/docs/backlog/backlog-item.md](../assets/templates/docs/backlog/backlog-item.md).

## 5. Open decisions — `docs/decisions/`

- **Purpose:** decision **not yet implemented**, under debate, with weighed alternatives. Canonical home **`docs/decisions/`** — MADR recommends **verbatim** *"Create folder `docs/decisions`"*.

- **How "good" looks:** one `NNNN-slug/` folder per ADR under `decisions/`; **removed + distilled** to `standards/` upon implementation; a "Distilled" ledger preserved; references (`sdd_slug`/`vision_refs`) in the frontmatter. `docs/adr/` is a variant name (migration candidate to `docs/decisions/`).

- **Detection:** read the README/index of `decisions/` + the folders; cross-reference ADRs marked as implemented with the ledger; detect `docs/adr/` as a variant to migrate.

- **Smells:** already-implemented ADR that didn't leave the tree; **current/active** decision stalled as an ADR; unresolvable ADR number; "how" (implementation) inside the ADR; **`docs/adr/`** instead of `docs/decisions/` (variant), or both coexisting (`TWO-HOMES`).

- **Remediation:** distill→`standards/` and remove; update the ledger; migrate `docs/adr/` → `docs/decisions/` (propose, with OK).

- **Payload:** skill-template [../assets/skills/quenching-docs/](../assets/skills/quenching-docs/) (covers ADR/decision) + `decisions/` skeleton from canonical scaffold [../assets/docs/](../assets/docs/) (second agent) + template [../assets/templates/docs/decisions/adr.md](../assets/templates/docs/decisions/adr.md). Specification: [docs-taxonomy.md](docs-taxonomy.md).

## 6. Skills — .claude/skills/

- **Purpose:** actionable capabilities with description-based trigger (progressive disclosure). The `description` (+`when_to_use`) is **routing code**, not prose: it is the only text always visible to the model and what it uses to choose the right skill among 100+ available.

- **How "good" looks:**

  **Healthy skill form:**
  - thematic prefix consistent with the repo's taxonomy; `name` = folder name.
  - description **in third person**, specific: what-it-does + when-to-use + **literal phrases the user would type** (and variants), which **distinguishes** it from neighboring skills in close domains.
  - SKILL.md <500 lines, detail pushed to `references/`.
  - side-effect skill (deploy/commit/send) uses `disable-model-invocation: true`; background-advisory skill uses `user-invocable: false`; `paths` restricts auto-trigger to the right scope.

  **Trigger test (verifiable):** for each skill, 3-5 requests that **should** trigger (should-trigger) × 3-5 *tricky* ones that **should not** (same keywords, require another skill).
  - wrong trigger on should-nots = **false-trigger**; silence on should-triggers = **missed-fire**.
  - **both are description problems, not instruction problems**: if the skill works when invoked via `/name` but doesn't trigger on its own, the body is correct and the **description is the bug**.

  **Trigger collision × toolset bloat** (≠ — different fix; see block 6b):

  | | Trigger collision | Toolset bloat |
  | --- | --- | --- |
  | What it is | same *keyword*, **different scopes** | **scopes that actually overlap** (cover the same work on the same artifact) |
  | Symptom | latent false-trigger (the model picks the wrong one) | ambiguous decision point that even the engineer can't resolve |
  | Fix | **exclusion clause** in the description (both survive) | **consolidate/prune** (merge into one; the other becomes deprecatable — dim 12) |

  - The toolset test: *"if an engineer can't say with certainty which skill applies to a scenario, the agent won't be able to either"*. The healthy target is **few powerful skills** (one that does the whole job with a parameter/mode), not many specialized overlapping ones. Multiplying exclusion clauses where the right move is to merge only delays the bloat.

  **When to CREATE a repo-specific skill/sub-agent (INVERSE criterion of bloat):** bloat and home-choice (dim 7) decide when to **merge/prune/move** what exists; the opposite is missing — when a recurring **domain** need justifies a NEW artifact (distinct from the generic `quenching-*` payloads). The signal is a **recognizable trigger** observable in Step 1 (*«every feature has a recognizable trigger»*):

  | Trigger | Home |
  | --- | --- |
  | **repeated multi-step manual procedure** — *«you paste the same playbook… for the third time → capture it as a skill»*, *«a workflow you keep tweaking by hand is a skill»* | **action skill** |
  | **recurring domain task type** (train/validate model X, create a domain task) | **action skill** (or **reference skill** if it's recurring knowledge — *«reference skills provide knowledge… like your API style guide»*) |
  | **recurring verbose side-task** (sweeping/diagnosing logs/runs, dependency audit) — *«a side task floods your conversation with output you won't reference again → route it through a subagent»* | **sub-agent** (dim 7) |

  - **CRUCIAL — the method PROPOSES the SKELETON, the repo fills in the CONTENT.** The content of the domain procedure (what to train, which contract to validate, how to diagnose) is a **human decision** (same limit as Step 6: installs structure/method, never content/direction). The method **recognizes the need** (cites the trigger `file:line`/fact from Step 1) and **proposes the skeleton/frontmatter** (name/description-trigger from dim 6 + home from dim 7 + empty `references/`/`scripts/`), **never the step-by-step**.
  - It is **PROPOSING** (like Step 6), not installing a ready payload: the package **does not carry** domain skills (they would couple to a repo — breaking self-contained); it **teaches how to recognize** the trigger and **sketches the form**. Distinct from the generic payload (which it **installs** because it's portable — `quenching-map/docs/skills/…`) and from home/merging of what already exists: here is **creating** what's missing, and only **proposing**.

- **Detection:** `find .claude/skills -name SKILL.md`; read frontmatters; measure size; **group descriptions by shared keyword** to find trigger collisions **and clusters of overlapping scope** (bloat); cross-reference with Step 1 looking for **recurring domain need WITHOUT artifact** (manual procedure repeated in history/commits, recurring task type, family of commands/runs) — command in [detection-and-smells.md](detection-and-smells.md).

- **Smells:**
  - weak/vague description (sub-trigger — "helps with X"); description in first/second person ("I can…/You can…"); only what-it-does without when-to-use or user-phrase; gigantic SKILL.md; skill without prefix or with wrong prefix; `name` ≠ folder.
  - **trigger collision** — two+ descriptions with the same keywords without a separating clause (latent false-trigger).
  - **toolset bloat** — two+ skills with **overlapping functional scope** (do the same work on the same artifact), an ambiguous decision point (≠ collision: here the scopes overlap, not just the keywords).
  - side-effect skill **without** `disable-model-invocation`.
  - **recurring domain need without artifact** — multi-step domain procedure **observably repeated** (the doc fixes the threshold: *«you paste the same playbook… for the THIRD time»* — ≥3 occurrences in history/PRs/commits, **not** 1-2x nor judgment), with **stable procedure** (not a workflow in flux), without a dedicated skill/sub-agent to capture it.

  **When NOT to trigger (poka-yoke against skill-spam — every extra artifact HAS A COST:** *«every feature you add consumes context… too many adds noise… skills may not trigger, Claude may lose sight of your conventions»*):

  | # | Counter-condition | Why |
  | --- | --- | --- |
  | a | **one-off / unstable** — happened 1-2x, or the procedure still changes every time | no stable form to capture |
  | b | **the base model already does it alone** — native capability (delta ≈ 0) | creating only wastes routing tokens; this is pruning (candidate *outgrowth*), **not** creation |
  | c | **a cheaper home works** — recurring rule the model gets wrong | fits in CLAUDE.md/`rules/` (*«gets a convention/command wrong twice → CLAUDE.md»*), not in a skill |
  | d | **an artifact to EXTEND already exists** | *«a workflow you keep tweaking by hand = a skill that needs another revision»* (extend/sharpen what exists), **not** create (create≠extend) |

  Only trigger with observable recurrence (≥3) **+** stable procedure **+** leverage (context saved > artifact cost) **+** none of the counter-conditions above.

- **Remediation:**
  - **weak description / trigger collision:** reinforce with literal phrases + explicit **exclusion clause** (resolves false-trigger without over-narrowing); break into `references/`; rename; run description evals.
  - **bloat:** **consolidate** the cluster into one skill (the winner gains a parameter/mode; the redundant ones become **deprecatable** — dim 12, "if two answer the same question, there's a boundary violation"), **do not** multiply exclusion clauses.
  - **domain need without artifact:** **PROPOSE the skeleton** (name + description-trigger + skill×sub-agent home by dim 7 + empty `references/`/`scripts/`), leaving the **procedure content for the repo to fill in** (human decision — Step 6); never install a ready domain payload (there isn't one — it would be coupling).

- **Payload:** skill-template [../assets/skills/quenching-skills/](../assets/skills/quenching-skills/) (authoring/editing/evals/description optimization for skill **and** agent) + template [../assets/templates/claude/skill.md](../assets/templates/claude/skill.md). *Exception:* the **trigger collision** and **overlapping-scope bloat** between skills are cross-artifact confrontation — core of this method (dim 12 applied to the skill surface): it **detects** the collision/overlap and **proposes the consolidation**; editing each description (or the merge) is work for the `quenching-skills` skill-template.

## 7. Sub-agents — .claude/agents/

- **Purpose:** isolated work that keeps the parent's context clean — runs in its **own context window** and returns **only the condensed result**. Home of **verbose/disposable** work: the sweep/log/dependency scan happens in isolation and the parent receives the summary, not the dump.

- **How "good" looks:**

  **Healthy sub-agent form:**
  - complete frontmatter (`name`/`description`/`tools`/`model`); body = role + inputs + numbered steps + **explicit return format**.
  - `tools` **minimal and always declared** (allowlist via `tools`, or denylist via `disallowedTools`); invoked by a sibling skill.
  - read-only audit profile = Explore-like: `tools: Read, Grep, Glob`, cheap model (`haiku`), `permissionMode: plan` (built-ins Explore/Plan **skip CLAUDE.md** to reduce sweep cost — weighs on dim 1 budget). The package carries a mold for this profile: [../assets/agents/quenching-auditor.md](../assets/agents/quenching-auditor.md).

  **Return contract (what makes the "explicit format" *good*)** — the sub-agent runs in its own window *precisely so* the parent receives **only the high signal**:
  - (a) **condensed summary** (target ~1-2k tokens) only with high-entropy fields for the parent's next step, **never the dump** of consumed context;
  - (b) **semantic identifiers** the parent understands — `file:line`, slug, dimension name — and not opaque IDs/UUID/hash (the official doc shows that resolving cryptic IDs to interpretable language **reduces hallucination** in retrieval);
  - (c) optionally a verbosity axis (summary × detail-on-demand) for the parent to control cost.
  - **Violation detector (by proportion):** if the return is order-of-magnitude close to the **context it consumed** (returned nearly everything it read), the isolation was breached — it became a read proxy, not a condensing worker.

  **Choice criterion (sub-agent × skill × command × hook)** — aligned with dim 12 (each purpose → one home):

  | Home | When |
  | --- | --- |
  | **sub-agent** | the intermediate output would *flood* the main context with non-re-referenced results (deep search, log, dep audit), **or** the same worker is repeatedly spawned with the same instructions |
  | **skill** | the procedure must *happen in the main thread* so the operator **sees and directs each step** |
  | **command** | it's just a manual invocation shortcut |
  | **hook** | the action must be guaranteed **deterministically** (enforcement, not judgment — dim 8) |

  **When to CREATE a domain-specific sub-agent** (sub-agent side of the dim 6 criterion):
  - **Trigger:** a **recurring verbose domain side-task** — diagnosing job logs/runs, sweeping a family of artifacts, dependency audit (*«a side task floods your conversation… → route it through a subagent»*; *«you keep spawning the same kind of worker with the same instructions»*).
  - **The method proposes the skeleton** (frontmatter + minimal `tools` + condensed return contract); the repo fills in the **content** (human decision, Step 6).
  - The package **does not carry** ready domain sub-agents (they break self-contained), only the generic read-only mold above.

- **Detection:** `ls .claude/agents/`; read frontmatters and bodies; verify that **every** agent declares `tools`/`disallowedTools` (item **7b** in [detection-and-smells.md](detection-and-smells.md)).

- **Smells:**
  - agent without defined return format.
  - **flooding return** — task instruction that tells it to return what it read ("return the file contents", "the entire log", without ceiling/summary) or whose observed return is close in size to the consumed context (does not condense — breaks isolation).
  - **opaque identifier in the return** — summary with UUID/hash/internal ID instead of `file:line`/slug/name (degrades parent precision).
  - **missing `tools`** — without the field, the sub-agent **inherits all tools** from the parent session (breaks least-privilege: a read-only audit agent gets `Edit`/`Write`/`Bash`/MCP); overly broad `tools`.
  - orphan (no skill/flow triggers it); missing `model` where it matters (cheap audit demands `haiku`).
  - **flow in the wrong home** — sub-agent for a step the operator needs to direct (should be skill), or skill that dumps verbose disposable output in the main context (should be sub-agent).

- **Remediation:** fix the **return contract** (condensed high-entropy summary + semantic identifiers `file:line`, never the dump); **declare minimal `tools`** (or `disallowedTools` for read-only); give `model`/`permissionMode` to the audit profile; connect to a skill; move the flow to the right home by the choice criterion above.

- **Payload:** skill-template [../assets/skills/quenching-skills/](../assets/skills/quenching-skills/) (same authoring discipline) + mold [../assets/agents/quenching-auditor.md](../assets/agents/quenching-auditor.md) + template [../assets/templates/claude/agent.md](../assets/templates/claude/agent.md). *Exception:* the **home choice** (skill, sub-agent, command, or hook?) is cross-artifact confrontation — method core (dim 12 applied to mechanisms): it **decides the home** and authoring comes from the `quenching-skills`/`quenching-config` templates.

## 8. Hooks — .claude/settings.json + .claude/hooks/

- **Purpose:** **deterministic** automation (validate/audit) in the session lifecycle. Home of what **needs** to happen (enforcement), contrasted with CLAUDE.md (probabilistic guidance the model can ignore) — `«deterministic limits are more reliable than probabilistic guardrails»`.

- **How "good" looks:**

  **Basic hygiene:** declared in `settings.json`; scripts in `.claude/hooks/`; idempotent; sensible `timeout` (below ~500 ms on the critical path); explicit criterion/ceiling; shared committed config, per-dev override in `*.local.json`.

  **Output semantics (most common error):**

  | Output | Effect |
  | --- | --- |
  | **exit 2** | **blocks**; the message in `stderr` is returned to the model as feedback |
  | **exit 1** | **only warns, does NOT block** (the dangerous action still executes) |
  | **exit 0 + JSON** in stdout | rich decisions |
  | exit 2 **+** JSON | **do not combine** — the harness ignores stdout when exit is 2 |

  - **Stop hook:** check the `stop_hook_active` field in the input JSON and exit early if `true` (the harness cuts after **8** consecutive blocks — without this, a loop).

  **Three lifecycle hooks (keep the knowledge surface alive):**

  | Hook | Event/matcher | Does | Output |
  | --- | --- | --- | --- |
  | **compact-survival** | `SessionStart` matcher `compact` (and ideally `clear`/`resume`; **not** `startup` — there the doc says to use native CLAUDE.md) | re-injects conventions/FQNs/guardrails after compaction (stdout becomes context; otherwise `/compact` loses them). **Good = reads from a derived source of the target** (conventions file or head of root CLAUDE.md), **never** a hardcoded list | exit 0 |
  | **evolutionary** | `Stop` (receives `transcript_path` at end of turn) | **proposes deltas** to CLAUDE.md/memory «while the exposed gap is still fresh» (auto-evolution, without force-editing). **Propose ≠ block:** returns via `hookSpecificOutput.additionalContext` (continues the conversation for Claude to report/act), **never** `decision: block` nor `exit 2` (those would force the turn not to finish) | exit 0 |
  | **audit-trail** | `ConfigChange` (matchers `user_settings`/`project_settings`/`local_settings`/`policy_settings`/`skills`) | change trail on the surface itself (new skill / `settings.json` modified doesn't go unnoticed). **OBSERVES, does not block** (though `ConfigChange` *can* block via `exit 2`/`decision: block`, except `policy_settings`). Stdout **does not** become context (goes to debug log) → writes to a **log file derived from the target**, **append-only and metadata-only** (timestamp/source/file/session — **never the content**, which may contain secrets) | exit 0 always |

  **Audit by TOOL EVENT (distinct from the 3 lifecycle ones, which trigger by *moment*):**

  | Hook | Matcher | Does | Can block? | Output |
  | --- | --- | --- | --- | --- |
  | **PostToolUse** | `Write\|Edit` | looks at the **touched file** (`tool_input.file_path`); when it falls under `docs/`, **PROPOSES** the taxonomy fix (dim 2) reusing **the same criteria from block 2b** — VARIANT/TWO-HOMES/NO-HOME/NO-SIDECAR/NO-LABEL (invents no new smell) | **No** — *«PostToolUse hooks cannot undo actions since the tool has already executed»*; «Can block? No» | exit 0; proposal via **JSON `additionalContext`** (stdout does not become context), never `decision: block` (only *ends the turn*, without undoing) |
  | **PreToolUse** | `Write\|Edit` | runs **before** the tool; when the destination matches a GENERATED artifact of the target (`protectedGlobs`, derived from target, never hardcoded paths — empty list ⇒ inert), **BLOCKS** — protect GENERATED YAML/manifests, AUTO-GENERATED catalog, lockfiles (rule «X defines Y» enforced by code). Crosses dim 14 | **Yes** — «Can block? Yes» / *«Blocks the tool call»* | modern form `hookSpecificOutput.permissionDecision: "deny"` + `permissionDecisionReason` with **exit 0** (wins **even** in `bypassPermissions`/`--dangerously-skip-permissions` — *«PreToolUse hooks fire before any permission-mode check»*); legacy `exit 2` + reason in `stderr`. **Do not mix** — *«Claude Code ignores JSON when you exit 2»* |

  - **The PreToolUse reason is ACTIONABLE (dim 14):** it says **WHICH** source-of-truth generates the artifact and tells you to edit the source (*«Claude receives it as feedback so it can adjust»*) — without this the agent blindly retries editing the generated artifact (loop). Latency ceiling: only matches the path string (`fnmatch`), no I/O.

  **Wiring — a hook only RUNS if it's wired:** copying the script to `.claude/hooks/` **is not enough** — *«a script file alone does nothing»*. Only triggers with the **corresponding entry** in `settings.json`, canonical structure `Event → matcher-group (`matcher`) → `hooks`:[ {`type`:`command`,`command`,`timeout`} ]`.
  - Installing the fragment ([../assets/hooks/settings.snippet.json](../assets/hooks/settings.snippet.json)) is **MERGING, never overwriting**: arrays per **event/matcher concatenate** (adds the package's group; same matcher ⇒ appends to `hooks[]`), preserving what the target already wired.
  - `command` uses the placeholder **`${CLAUDE_PROJECT_DIR}`** (never the machine's absolute path) and the script is **executable** (`chmod +x`).

  **Scope, precedence & trust:**
  - **Managed > CLI > Local > Project > User**.
  - home of hooks the **team** should have = `.claude/settings.json` (**checked-in**); per-machine override = `.claude/settings.local.json` (**gitignored**).
  - `.claude/settings.json` loads **only from the start directory** (does not inherit from parents — in a monorepo, each start-subfolder needs its own).
  - hook config **is executable code** with shell privileges — version and review as infra, never run destructive logic in `SessionStart`.

  **Canonical home for executable logic — `scripts/` (the hook is THIN and CALLS the script):**
  the reusable deterministic logic the surface invokes does not live **inline** in the
  hook's `command` nor scattered loose — it lives in **`scripts/`**, organized **by
  PURPOSE** (`ci/`/`<gen>`/`checks/`/`maintenance/`/`dev/`), with a README-map and a
  single execution convention. The official doc fixes the form: *«This example uses a
  separate script file that the hook calls»* + *«use… `${CLAUDE_PROJECT_DIR}` to
  reference scripts»*. The **hook is the thin trigger** (stdin-JSON→exit-code adapter);
  the **business rule** (validate/generate/check) is a **called `scripts/…`** — the
  payload [run-validation.py](../assets/hooks/run-validation.py) (Stop) **is** that
  thin trigger: it invokes the target's `validateScript` (home `scripts/checks`/`ci`) on
  the changed files, without reimplementing the validation. This is
  the same home that (a) the **"common commands" of CLAUDE.md** (dim 1) invoke, (b)
  commands/skills (dim 9) load, (c) CI runs. The complete tree, the boundaries
  (`scripts/` of repo × `.claude/hooks/*` × `scripts/` internal to skill × `src/`), the
  CI scope of each purpose, and the organization doctrine are the **prescriptive canonical
  taxonomy** — single source in [scripts-taxonomy.md](scripts-taxonomy.md);
  **do not copy the tree** (Simplicity First) — link.

- **Detection:** read `.claude/settings.json`; `ls .claude/hooks/`; verify the **1:1 wiring** (every script has an entry / every entry points to an existing script, in the right event/matcher — orphan × dangling); check the **presence** of the three lifecycle hooks and the **output semantics** of blocking ones; locate the repo-level `scripts/`, verify **organization by purpose** (subfolders `ci`/`checks`/`maintenance`/`dev`), the **README-map vs. disk**, and that each `command`/command/CI invoking `scripts/<…>` points to an **existing** module (item **8b** in [detection-and-smells.md](detection-and-smells.md)).

- **Smells:**
  - hook referencing absent script; validation without ceiling/criterion; hook that edits a generated artifact (violates the «X defines Y» rule); missing timeout.
  - **orphan hook** — script present in `.claude/hooks/` **without** an entry in `settings.json` (inert: never triggers — e.g.: `protect-generated.py` copied but not wired, and the generated artifact remains editable).
  - **dangling hook** — entry in `settings.json` pointing to a **nonexistent** script (the `command` lies, fails on every trigger).
  - **wrong event/matcher** — right script in the wrong event (blocking placed in `PostToolUse`, which doesn't block; `compact`-survival wired to `startup` instead of `compact`).
  - **snippet overwriting instead of merging** — clobbers the array of an event the target already had (loses the pre-existing hook, instead of **concatenating**).
  - **`exit 1` in a blocking hook** (thinks it warns but the dangerous command still executes — should be `exit 2`).
  - **Stop hook without `stop_hook_active`** (loop until the 8-block cap); slow hook on the critical path (>500 ms).
  - **absence of lifecycle hooks** — without `SessionStart compact` the `/compact` deletes conventions/guardrails; without evolutionary `Stop` the surface doesn't self-correct; without `ConfigChange` there is no audit-trail.
  - **editable generated artifact without deterministic guard** — the repo has an artifact "generated by CI, never hand-edited" (`*.job.yml`/manifests/AUTO-GENERATED catalog/lockfile) but **nothing protects it by code** (only the CLAUDE.md guidance, which the model can ignore): missing the **PreToolUse** that BLOCKS Write/Edit on the generated artifact — deterministic enforcement × probabilistic guardrail (crosses dim 14).
  - sensitive/destructive logic in `SessionStart` (pre-trust vector).

  **Smells of the `scripts/` home (the executable logic invoked by the surface — crosses dim 1/9; doctrine in [scripts-taxonomy.md](scripts-taxonomy.md)):**
  - **deterministic logic embedded in the hook that should be a script** — the hook's `command` carries the **business rule** inline (multi-line validation/build), or a `.claude/hooks/<x>.py` **reimplements** what a `scripts/checks|ci/<x>` already does, instead of the hook **calling** the script (*«a separate script file that the hook calls»*). The rule should live in `scripts/`; the hook is the thin trigger.
  - **script referenced by hook/command/CI that doesn't exist** — the `command` of a hook (or a command/skill, or CI) invokes `scripts/<…>` that **doesn't exist** (mirrors the HOOK-DANGLING, now on the script target side).
  - **scripts loose at the root / single bag without purpose** — executables at the repo root or all in a flat `scripts/` without a purpose subfolder (`ci`/`checks`/`maintenance`/`dev`) — invisible to audit, no CI-scope boundary (uninsolated `dev/` enters product lint; destructive operational isn't flags-off).
  - **`scripts/README.md` that lies vs. disk** — the map (module → what-it-does → input) cites nonexistent module or omits new module (should be derivable from disk, like `standards/` `INDEX.md`); or **divergent execution convention** (CLAUDE.md says `python -m scripts.X`, README says another form).
  - **repo executable in the wrong home** — repo utility buried in the **internal `scripts/`** of a skill and re-called from outside it (should be promoted to repo-level `scripts/`); or product script dropped in `dev/` (escapes lint).

- **Remediation:** fix path; provide criterion; **wire the orphan hook** (merge the `settings.snippet.json` entry at the right event/matcher, without clobber) or **remove the dangling entry**; swap `exit 1`→`exit 2` in the blocking hook; add the `stop_hook_active` guard; **install** the lifecycle hooks (copy the script **AND** merge the wiring in `settings.json` for the right scope); remove broken hook. The evolutionary Stop hook **proposes**, does not impose. For `scripts/`: **extract** the inline business rule from the hook to a called `scripts/…`; **organize** the loose-at-root/single-bag into purpose subfolders (propose the move, with OK — install the scaffold from [../assets/scripts/](../assets/scripts/) where the home is missing); **sync** the README-map with disk; create the module a hook/command/CI invokes but doesn't exist (or fix the invocation).

- **Payload:** skill-template [../assets/skills/quenching-config/](../assets/skills/quenching-config/) (settings.json/hooks/permissions/env/MCP) + ready hooks [../assets/hooks/](../assets/hooks/) with their `hooks-config.json`. The package **carries** (not just detects absence):

  | Hook payload | Step 8 | What it does (summary) |
  | --- | --- | --- |
  | [validate-claude-md.py](../assets/hooks/validate-claude-md.py) | — | CLAUDE.md line ceiling |
  | [propose-knowledge-delta.py](../assets/hooks/propose-knowledge-delta.py) (Stop) | **automatic freshness** | reads the transcript at **end** of turn, **PROPOSES** deltas via `additionalContext`, **exit 0 always**, `stop_hook_active` guard, latency ceiling |
  | [reinject-conventions.py](../assets/hooks/reinject-conventions.py) (SessionStart) | **compact-survival** | on restart (matcher `compact`/`clear`/`resume`) **re-injects** the stable layer that `/compact` would erase, reading from a **source derived from the target** (`conventionsFile` or head of root CLAUDE.md, **never** a fixed list from the package), stdout-becomes-context, exit 0, latency ceiling; does not cover `startup` (there the doc recommends native CLAUDE.md) |
  | [audit-config-change.py](../assets/hooks/audit-config-change.py) (ConfigChange) | **audit-trail** | records in a **log derived from the target** (append-only, metadata-only — timestamp/source/file/session, **never the content** which may contain secrets) who/when/what changed (settings/skills), covering the 5 sources (`user_settings`/`project_settings`/`local_settings`/`policy_settings`/`skills`), **exit 0 always** (OBSERVES, never blocks), stdout-does-not-become-context |
  | [propose-docs-home.py](../assets/hooks/propose-docs-home.py) (PostToolUse) | **`docs/` coverage** | triggered by **tool event**: on `Write`/`Edit` under `docs/`, checks the **touched file** (`tool_input.file_path`) against the taxonomy (dim 2) reusing **the criteria from block 2b** (VARIANT/TWO-HOMES/NO-HOME/NO-SIDECAR/NO-LABEL) and **PROPOSES** the home/slot via `additionalContext`, **exit 0 always** («Can block? No»), actionable error (says WHICH home/slot is missing + exact canonical name), latency ceiling |
  | [protect-generated.py](../assets/hooks/protect-generated.py) (PreToolUse) | **generated artifact protection** | the only **enforcement** payload (crosses dim 14): runs **before** `Write`/`Edit` and, when the destination matches `protectedGlobs` (**derived from target**, never paths from this repo — empty list ⇒ inert), **BLOCKS** via `permissionDecision: "deny"` + `permissionDecisionReason` (exit 0; legacy `exit 2`+stderr via `denyMode`), **actionable** reason naming the source-of-truth (rule «X defines Y») |
  | [run-validation.py](../assets/hooks/run-validation.py) (Stop) | **validation before finishing** (THIN hook that CALLS the script — crosses `scripts/`) | at **end of turn**, invokes the **validator derived from the target** (`validateScript`/`validateCmd`, in home `scripts/checks`/`ci` — **empty ⇒ inert**, never a hardcoded trio) on the **changed files** (`git status --porcelain`, filtered by `includeGlobs`). The **rule lives in `scripts/`**, the hook is the thin trigger. Default **PROPOSES** the result via `additionalContext` (**exit 0** — `ruff --fix`/`format` mutate **code**, not the knowledge base ⇒ informs, does not block); `blockOnFail` mode (OFF by default) uses `decision: block`/`reason` for «mandatory/never skip» (*«the `reason` is fed back to Claude so it keeps working»*). `stop_hook_active` guard, latency ceiling. **Documented example for Python repo:** the script runs `ruff check --fix` + `ruff format` + `pyright` (a Go repo would wire `go vet`/`gofmt`) |

  The **three** lifecycle ones are complementary (one **proposes** new delta at end of turn, another **re-injects** what exists on restart, the third **records** the change). PostToolUse and PreToolUse are also complementary: **PostToolUse PROPOSES *after***, **PreToolUse BLOCKS *before***. Wire via [../assets/hooks/settings.snippet.json](../assets/hooks/settings.snippet.json).

  For the **`scripts/` home** (the executable logic that hooks call): **organization scaffold** [../assets/scripts/](../assets/scripts/) — README-map template + skeleton of purpose subfolders (`ci`/`checks`/`maintenance`/`dev`) with `<...>` placeholders, **no concrete scripts** (the package carries the STRUCTURE, not the executables — those would be coupled to a repo). Canonical spec: [scripts-taxonomy.md](scripts-taxonomy.md).

## 9. Commands — .claude/commands/

- **Purpose:** shortcuts/entries for flows (often mirroring a skill) — invocable **by the user** (`/name`) **and**, when the model is authorized, **by Claude itself** during the conversation (the programmatic invocation tool — `SlashCommand` in the SDK / currently the *Skill tool*). So a command is not just a user shortcut: it is a **composable building block** that a skill / sub-agent / method step can **chain** into a larger flow.

- **How "good" looks:**

  **Legacy × recommended:**

  | Format | `/name`? | Auto-trigger by description? | Support directory |
  | --- | --- | --- | --- |
  | `.claude/commands/<name>.md` (**legacy**) | yes | no | no |
  | `.claude/skills/<name>/SKILL.md` (**recommended**) | yes | **yes** (the `description`/dim 6 becomes the trigger) | `references/`/`scripts/`/`assets/` without bloating the body |

  - Healthy state: **every new command is born a skill**; a `.md` in `commands/` only remains a legacy command when it is a pure **manual** shortcut (side-effect/timing the operator wants to control — and the skill-equivalent would use `disable-model-invocation: true`); each command has a corresponding live skill/flow; minimal frontmatter (`description`/`allowed-tools`; `argument-hint` if using `$ARGUMENTS`/`$0`/`$1`).

  **Command→skill migration criterion (verifiable):** migrate when the command
  - (a) would benefit from **auto-trigger** (the user forgets to invoke it via `/name`), **or**
  - (b) references external files / exceeded ~50 lines (needs `references/`), **or**
  - (c) was copied to multiple repos (becomes a portable skill, Agent Skills open standard).
  - Stays a command only if it is exclusively a manual-side-effect-shortcut.

  **Composability (building block, not just user shortcut):** Claude can **execute** a custom command during the conversation via the programmatic tool (`SlashCommand`/Skill tool — *"A few built-in commands are also available through the Skill tool"*), so a step in a larger flow can be triggered as `/<prefix>-<step> <scope>` instead of repeated prose (e.g.: the Step 8 re-audit as `/<prefix>-reaudit <dimension>`).
  - **The trigger for composability is the `description`** — *"Claude uses this to decide when to apply the skill"*: the same `description`/dim 6 that drives auto-trigger makes the model choose to **compose** the command; weak description ⇒ the building block stays inert (links to dim 6).

  **Exposure control:** `disable-model-invocation: true` **removes the command from the programmatic invocation tool** (*"Description not in context"*, *"blocks programmatic invocation"*, *"removes the skill from Claude's context entirely"*) — so **only** the manual side-effect shortcut (deploy/commit/send) should have it; a **read-only step that SHOULD be composable but is gated** with the flag is a smell (disappears from the tool).

  **Description list character budget (links to dim 1):** the descriptions available to the tool enter a **budget = ~1% of the context window** (adjustable via `skillListingBudgetFraction` / `SLASH_COMMAND_TOOL_CHAR_BUDGET`); if exceeded, *"descriptions for the skills you invoke least are dropped first"* — an inflated command costs context and may have its description **truncated** (each entry is already capped at 1,536 chars), losing routing keywords; `/doctor` reports overflow and `name-only` in `skillOverrides` frees budget.

  **Boundary of the chainable flow step:** **composable command** when the model invokes it programmatically as a reusable block (same instruction, chainable, with `argument-hint`); **skill** when the procedure must happen in the main thread so the operator **sees and directs** each step; **sub-agent** when it needs **isolated context** (the output would flood the parent). Since new command already is born a skill, the concrete form is a **composable skill** (auto-invocable, without `disable-model-invocation`) — the Step 8 re-audit is exactly this case.

  **Executable of a command/skill → the right `scripts/`:** a command/skill that **runs code** carries its internal `scripts/` (Agent Skills: *«`scripts/` for executables»*) for what is **specific to it**; what is a **repo executable** (build/checks/maintenance that other surfaces also invoke) lives in the **repo-level `scripts/`** (dim 8 / [scripts-taxonomy.md](scripts-taxonomy.md)), not buried inside a skill.

- **Detection:** `ls .claude/commands/`; cross-reference with existing skills; apply the migration criterion and check for basename collision between subfolders; check which read-only composable commands are **improperly gated** by `disable-model-invocation` and the **list weight** in the budget (item **9b** in [detection-and-smells.md](detection-and-smells.md)).

- **Smells:**
  - orphan command (corresponding skill removed); command that diverges from the skill it should mirror.
  - **migratable legacy command** — lives in `.claude/commands/` but passes the migration criterion (would gain auto-trigger / >50 lines / references files / is multi-repo).
  - **basename collision** — two `.md` with the same name in different `commands/` subfolders collide (the subfolder appears in the description but **does not** change the name — ambiguous `/name`).
  - **silent shadowing** — custom command with the same name as a *bundled skill* (e.g.: `code-review`/`verify`) shadows it without warning (`slash_commands` lists the name only once).
  - **gated-composable** — read-only step that should be chainable by the model but has `disable-model-invocation: true` (disappears from the `SlashCommand`/Skill tool, becomes only a manual shortcut).
  - **auto-invocable side-effect** — the inverse: deploy/commit/send command **without** the flag (the model can trigger a destructive action on its own — *"You don't want Claude deciding to deploy"*).
  - **inflated list/budget exceeded** — many long descriptions exceed the ~1% and `/doctor` reports **truncated/dropped** descriptions, blinding the routing (links to dim 1).

- **Remediation:** remove orphan; resync with skill; **migrate legacy command → skill** (`.claude/skills/<name>/SKILL.md` with description-trigger from dim 6; the command is removed or becomes a thin redirect); rename to resolve basename collision/shadowing.

- **Payload:** skill-template [../assets/skills/quenching-skills/](../assets/skills/quenching-skills/) (authoring/migration command→skill) + **ready command-skill** [../assets/commands/quenching-reaudit/](../assets/commands/quenching-reaudit/).
  - The package **carries** the first command (not just detecting absence): the on-demand re-audit (trigger (3) of Step 8), installed in `.claude/skills/<prefix>-reauditar/` as a **skill** (doctrine "command is born a skill" by construction: **reads and proposes**, so maintains auto-trigger; uses `context: fork` + `agent: quenching-auditor` to sweep in a clean context).
  - It is also the **example of a composable command**: read-only and auto-invocable (**without** `disable-model-invocation`), so Claude itself can **chain it** in a larger flow (e.g.: `/<prefix>-reauditar <dimension>` as a workflow step), not just the user.
  - *Exception:* the **legacy-command × skill × hook choice** (should it auto-trigger? should it be deterministic?) is the dim 12 boundary applied to mechanisms (mirrors 7b/8b) — the core **decides the home**; authoring comes from the `quenching-skills` template.

## 10. Memory — memory directory + index (Auto Memory)

- **Purpose:** what the **agent** discovered during work (build commands, debug insights, project context/constraints, user preferences) — durable between sessions, **machine-local**, auditable via `/memory`. It is the counterpart of CLAUDE.md: this is what *any team member needs to know* (versioned); Auto Memory is what *the agent learned* (local).

- **How "good" looks:** the index (`MEMORY.md`) has **one line < ~150 characters per memory** (title + hook + link), **within the load ceiling** — only the first **200 lines / 25 KB** enter the session (what exceeds this does not load); detail goes to **topic files** (not loaded at startup, read on demand). Each memory named by the **type** the repo adopts as prefix (derive them — e.g.: `user_`/`feedback_`/`project_`/`reference_`); entry **dated and with provenance**; without duplicating what already lives in the repo (code/CLAUDE.md/normative reference → reference by link/`@path`, not copy).

- **Detection:** read the project's memory directory index (path in the session context); cross-reference index × `.md` files alongside (`/memory` lists the loaded ones). Run the **hygiene checklist** (below). Writing is out of scope — the method **only signals**.

- **Smells (hygiene checklist — 6 verifiable):**

  | # | Smell | What it is |
  | --- | --- | --- |
  | 1 | **index orphan** | topic file without a line in the index (invisible to loading); or index >200 lines/25 KB (the tail never loads) |
  | 2 | **duplicates the repo** | the entry repeats something already in code/CLAUDE.md/normative reference instead of linking to it (dim 12 applied to memory) |
  | 3 | **vague temporal reference** | "recently"/"last time"/"today" instead of an **exact date** |
  | 4 | **silent conflict** | two contradictory entries, invisible *last-write-wins* (one marked "WRONG/CORRECTED/superseded" that should be **pruned**, not accumulated) |
  | 5 | **degraded freshness** | expired/obsolete fact that poisons future context (*context poisoning by staleness*) |
  | 6 | **wrong type/scope** | team-convention living in Auto Memory (should be CLAUDE.md/normative reference) or agent-learning in prose in CLAUDE.md (should be Auto Memory); type prefix swapped vs. the content |

- **Remediation:** the method **points out** the divergence (which smell, which `file:line`); writing/pruning memory is for the memory flow (`/memory`), **not** this method. For smell (2), remediation is replacing the copy with a link/`@path` (dim 12).

- **Payload:** — (no payload; the method only signals, **does not write memory**). There is an entry template [../assets/templates/memory/memory.md](../assets/templates/memory/memory.md) for when the user **will** write, but installing it is not a method action.

## 11. Data / domain catalog — `docs/catalog/`

- **Purpose:** table/model metadata (generated) + editorial curation (versioned); how skills consume the domain. Canonical home **`docs/catalog/`** (`docs/catalogo_dados/`/`docs/dominio/` are variants). Only applies to repos with explicit data/domain.

- **How "good" looks:** AUTO-GENERATED and curation **separated** (generated never hand-edited — same «X defines Y» rule); curation versioned separately; one doctrine governs domain consumption by skills.

- **Detection:** locate the catalog/domain (if any); check for manual editing in the AUTO-GENERATED block.

- **Smells:** curation written inside the generated block (will be overwritten); catalog outdated vs. the manifest/source; domain without consumption mapping.

- **Remediation:** move curation to the versioned area; regenerate via the correct generator.

- **Payload:** skill-template [../assets/skills/quenching-docs/](../assets/skills/quenching-docs/) (covers the domain/consumption doctrine). *Catalog generators are repo-specific — the method does not carry them; it only signals the generated×curation separation.*

## 12. Boundary doctrine — transversal *(method core)*

- **Purpose:** the rule that **separates all the artifacts above** — map × current/active × direction × decision × description — so that each piece of information has a unique home.

- **How "good" looks:** boundary declared and **consistent** between the root CLAUDE.md, the normative reference index, and the domain doctrine (if any); no information duplicated in two artifacts; the «X defines Y» rule respected.

  **Quadrant test (Diátaxis — two axes: action/cognition × acquisition/application → four types):** each artifact serves **one** purpose.

  | Artifact | Diátaxis type (typical) |
  | --- | --- |
  | CLAUDE.md | *map/reference* ("what do I do now / which file contains what") |
  | normative reference | *current/active reference* ("how it is today") |
  | ADR | *explanation* ("why we decided, alternatives") |
  | backlog | *how-to of pending work* |
  | VISION | *explanation of direction* |

  - Verifiable criterion: **"if this artifact serves two different purposes, it has two homes, not one."**

- **Detection:** (1) confront root CLAUDE.md × normative index × domain doctrine against each other — the **boundary table** must say the same thing in all three; (2) **quadrant test per artifact**: classify each doc into a single Diátaxis type and flag what migrated quadrant (explanation/rationale inside the CLAUDE.md-map; current/active standard reference inside an ADR; direction/aspiration inside the normative reference); (3) look for the same rule written in two places with divergent wording (DRY/single-source-of-truth). Detail in [detection-and-smells.md](detection-and-smells.md).

- **Smells:** same info in two places (and diverging); current/active standard living in VISION/ADR (or vice versa); behavioral guardrail copied in prose in CLAUDE.md instead of linked; **cross-quadrant artifact** — CLAUDE.md accumulating explanation that belongs in the normative reference, ADR carrying reference of "how it is today", VISION becoming a task list (how-to/backlog); the boundary table present in one artifact and **absent or divergent** in the others.

- **Remediation:** choose the canonical home **by quadrant** (one purpose → one home), leave **only a link** in the others; the method **proposes** the rearrangement.

- **Payload:** — **This is the only structural dimension without a payload; it is the method's exclusive value** (confronting the artifacts against each other). The *application* of the rearrangement uses the templates that own the touched artifacts (moving a standard from VISION to the normative reference = `quenching-docs` at the writing end).

## 13. Derived conventions — code + naming

- **Purpose:** the house rules the repo already follows (imports, language, naming, the «X defines Y» rule, pins, etc.).

- **How "good" looks:** conventions **explicit and unique**, each with an owning doc in the normative reference; CLAUDE.md cites them with a short directive + link.

- **Detection:** read the code/naming docs from the normative reference; cross-reference with what CLAUDE.md cites.

- **Smells:** convention practiced but not written; two docs with the same convention diverging; convention cited in CLAUDE.md without a current/active doc behind it.

- **Remediation:** write/unify the convention in the owning doc.

- **Payload:** skill-template [../assets/skills/quenching-docs/](../assets/skills/quenching-docs/).

## 14. Behavioral guardrails — how the LLM should code

- **Purpose:** how the LLM should behave when coding (think-before-coding, simplicity, surgical, goal-driven) — assisted-coding guardrails. **Two targets:** (a) the LLM's behavior *in the target repo* (the guardrails skill cited by CLAUDE.md) and (b) the **quality of the executable artifacts themselves** that this surface exposes to the agent — hooks, audit scripts, skill tools — which speak to the agent **through their failure messages**.

- **How "good" looks:**
  - a guardrails skill present and **cited** (not copied) by the root CLAUDE.md.
  - **Actionable error (the agent speaks to the tool through failure):** every hook/script/tool the agent can trigger returns, on failure, a message that says **what is wrong and how to fix it** — not an opaque code or raw stack trace. Official source: *«you can prompt-engineer your error responses to communicate specific, actionable improvements, instead of opaque error codes or tracebacks»* — a well-written response **guides the agent** to the correct input (e.g.: *"Dimension 'ADR' not found: `docs/adr/` absent or empty — create the folder or run the package skeleton"*, not `KeyError: 'ADR'`).
  - **Poka-yoke (prevent the error before it happens):** *«change the arguments so that it is harder to make a mistake»* — the **parameter** design, not just the message, controls the error rate (canonical: switching a **relative to absolute** filepath eliminated an entire class of errors). Verifiable test: *for each plausible invalid input to a hook/script, does the failure message allow the agent to self-correct without blindly retrying?* If not, the opaque error becomes an **expensive retry loop**.
  - **Deterministic enforcement > probabilistic guardrail (third thread, crosses dim 8):** where the doctrine wants to **guarantee** an invariant — above all, **keeping generated artifacts intact** (rule «X defines Y») — prose guidance in CLAUDE.md **is not enough** (the model can ignore it). The good approach is a **guardrail by code**: a **PreToolUse hook** that **blocks** editing of the generated artifact **before** it occurs (`permissionDecision: "deny"` with actionable reason pointing to the source-of-truth), `«deterministic limits are more reliable than probabilistic guardrails»`. The protected list is **derived from the target** (`protectedGlobs`), never fixed paths.

- **Detection:** look for a behavioral guardrails skill; verify the citation (not the copy) in CLAUDE.md. Inspect the **executable hooks/scripts** the package installs (and the repo's pre-existing ones) for actionable failure messages vs. raw tracebacks / `exit` without explanatory stderr (item **14b** in [detection-and-smells.md](detection-and-smells.md)).

- **Smells:**
  - guardrail duplicated in prose in CLAUDE.md instead of linked; guardrail absent in a repo that codes heavily.
  - **opaque error** — audit hook/script that fails with raw stack trace, numeric code, or `exit 2` without stderr saying **how to fix** (leaves the agent in a blind self-correction loop).
  - **error-prone parameter** — tool/script that accepts a relative path / ambiguous format where an absolute / fixed format would eliminate the error class (poka-yoke not applied).

- **Remediation:** replace the copy with a link; ensure the citation; install the skill if absent. For executables: **rewrite the failure message** to point to the concrete fix (what's missing + the action); **harden the parameter** (absolute > relative, enum > free string) to make the error impossible. The hooks the package carries should already be born with this pattern.

- **Payload:** skill-template [../assets/skills/quenching-guardrails/](../assets/skills/quenching-guardrails/) (4 generic directives; the repo cites, does not copy) + **PreToolUse enforcement hook** [../assets/hooks/protect-generated.py](../assets/hooks/protect-generated.py).
  - The hook is the **by-code guardrail** that **blocks** editing of generated artifacts (`protectedGlobs` derived from target; `permissionDecision: "deny"` + actionable reason pointing to the source-of-truth; wins even in `bypassPermissions`) — the invariant "keep generated artifacts intact" imposed deterministically (full mechanics in dim 8).
  - *The quality of failure messages from installed hooks/scripts is the package's responsibility* — the payloads in [../assets/hooks/](../assets/hooks/) must emit actionable errors by construction; where the repo has its own hook/script with an opaque error, the method **signals** (does not rewrite the repo's script without OK).

## 15. External integration — MCP servers (.mcp.json)

- **Purpose:** the **external integration surface** the Claude Code agent can access in the session (tools, databases, APIs via Model Context Protocol). It is the only dimension of **dependency that lives outside the repo** but affects what the agent can do inside it.

- **How "good" looks:** servers the team should have stay in **`project` scope** (`.mcp.json` at the root, versioned and reviewed as infra code); secrets via `${VAR}`-expansion, **never hardcoded** in `env`/`headers`; minimal OAuth scope per server; the root CLAUDE.md declares **which** servers are expected and in which scope; in a corporate context there is a `managed-mcp.json` with an allowlist by `serverUrl`/`serverCommand` (not by `serverName`, which the user chooses).

- **Detection:** look for `.mcp.json` at the root; cross-reference with what CLAUDE.md documents and with the servers actually connected (`claude mcp list` / `/mcp`, outside of read-only — ask the user). Active server in the session **without** a versioned `project` entry = undeclared dependency (lives in `local`/`user` scope, invisible to the repo).

- **Smells:** MCP server connected but absent from `.mcp.json` (phantom dependency in `local`/`user` scope); credential/literal token in `env`/`headers` of the versioned `.mcp.json`; server that consumes external content (issues, web, messages, user data) **not** flagged as a prompt-injection vector in CLAUDE.md; corporate allowlist based only on `serverName`; `.mcp.json` edited without review (it is infra code).

- **Remediation:** promote expected server to `project` scope and version it; replace literal secret with `${VAR}`; declare expected servers in the root CLAUDE.md; flag external-content servers as injection vectors. The method **detects and proposes**; editing `.mcp.json`/secrets is a team decision.

- **Payload:** skill-template [../assets/skills/quenching-config/](../assets/skills/quenching-config/) (session configuration/`settings.json`/`.mcp.json`); the boundary/scope doctrine is signaled by the method core.

---

## How the method scores (summary)

For each dimension, assign **Present / Partial / Drifted / Absent** with evidence
`file:line`. The operational rule for the four states and the adaptive globs/greps
per dimension are in [detection-and-smells.md](detection-and-smells.md). The final report
follows [report-format.md](report-format.md); the gap → payload map and the deprecation
doctrine are in [installation.md](installation.md).
