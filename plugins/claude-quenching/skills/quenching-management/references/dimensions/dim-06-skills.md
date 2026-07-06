# 6. Skills — .claude/skills/

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

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

  - **CRUCIAL — the method PROPOSES the SKELETON, the repo fills in the CONTENT.** The content of the domain procedure (what to train, which contract to validate, how to diagnose) is left for the **repo to fill** — a **portability boundary** (the package can't carry a repo-coupled domain procedure without breaking self-containment), **distinct** from the derived standards content the method *does* generate. The method **recognizes the need** (cites the trigger `file:line`/fact from Step 1) and **proposes the skeleton/frontmatter** (name/description-trigger from dim 6 + home from dim 7 + empty `references/`/`scripts/`), **never the step-by-step**.
  - It is **PROPOSING** (like Step 6), not installing a ready payload: the package **does not carry** domain skills (they would couple to a repo — breaking self-contained); it **teaches how to recognize** the trigger and **sketches the form**. Distinct from the generic payload (which it **installs** because it's portable — `quenching-map/docs/skills/…`) and from home/merging of what already exists: here is **creating** what's missing, and only **proposing**.

- **Detection:** `find .claude/skills -name SKILL.md`; read frontmatters; measure size; **group descriptions by shared keyword** to find trigger collisions **and clusters of overlapping scope** (bloat); cross-reference with Step 1 looking for **recurring domain need WITHOUT artifact** (manual procedure repeated in history/commits, recurring task type, family of commands/runs) — command in [../detection-and-smells.md](../detection-and-smells.md).

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

- **Payload:** skill-template [../../assets/skills/quenching-skills/](../../assets/skills/quenching-skills/) (authoring/editing/evals/description optimization for skill **and** agent) + template [../../assets/templates/claude/skill.md](../../assets/templates/claude/skill.md). *Exception:* the **trigger collision** and **overlapping-scope bloat** between skills are cross-artifact confrontation — core of this method (dim 12 applied to the skill surface): it **detects** the collision/overlap and **proposes the consolidation**; editing each description (or the merge) is work for the `quenching-skills` skill-template.
