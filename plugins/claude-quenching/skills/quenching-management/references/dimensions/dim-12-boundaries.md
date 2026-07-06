# 12. Boundary doctrine — transversal *(method core)*

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** the rule that **separates all the artifacts above** — map × current/active × direction × decision × description — so that each piece of information has a unique home.

- **How "good" looks:** boundary declared and **consistent** between the root CLAUDE.md, the standards index, and the domain doctrine (if any); no information duplicated in two artifacts; the «X defines Y» rule respected.

  **Quadrant test (Diátaxis — two axes: action/cognition × acquisition/application → four types):** each artifact serves **one** purpose.

  | Artifact | Diátaxis type (typical) |
  | --- | --- |
  | CLAUDE.md | *map/reference* ("what do I do now / which file contains what") |
  | standards | *current/active reference* ("how it is today") |
  | ADR | *explanation* ("why we decided, alternatives") |
  | backlog | *how-to of pending work* |
  | VISION | *explanation of direction* |

  - Verifiable criterion: **"if this artifact serves two different purposes, it has two homes, not one."**

  **Behavior × world-state axis (interop contract):** CLAUDE.md/AGENTS.md/skills say **how the agent behaves** (this repo); `docs/` + `docs/catalog/` + memory say **what exists / what was learned** (world-state). Each artifact stays on one side; the behavior side **links** to the world-state side ("see the catalog at `docs/catalog/`"), never inlines it. On the interop surface, be **prescriptive about the contract** (frontmatter/labels) and **permissive about consumption** — a partial or agent-generated doc is tolerated, never hard-failed for a missing optional field.

- **Detection:** (1) confront root CLAUDE.md × standards index × domain doctrine against each other — the **boundary table** must say the same thing in all three; (2) **quadrant test per artifact**: classify each doc into a single Diátaxis type and flag what migrated quadrant (explanation/rationale inside the CLAUDE.md-map; current/active standard reference inside an ADR; direction/aspiration inside the standards); (3) look for the same rule written in two places with divergent wording (DRY/single-source-of-truth). Detail in [../detection-and-smells.md](../detection-and-smells.md).

- **Smells:** same info in two places (and diverging); current/active standard living in VISION/ADR (or vice versa); behavioral guardrail copied in prose in CLAUDE.md instead of linked; **cross-quadrant artifact** — CLAUDE.md accumulating explanation that belongs in the standards, ADR carrying reference of "how it is today", VISION becoming a task list (how-to/backlog); the boundary table present in one artifact and **absent or divergent** in the others; **behavior × world-state mixed** — agent operating rules inside catalog/docs pages, or a world-state inventory (tables, systems, domain facts) pasted into CLAUDE.md/skills instead of linked.

- **Remediation:** choose the canonical home **by quadrant** (one purpose → one home), leave **only a link** in the others; the method **drafts** the rearrangement (which home is canonical, what becomes a link) as a labeled proposal the human **ratifies**.

- **Payload:** **direction-draft discipline** [../../assets/agents/quenching-direction.md](../../assets/agents/quenching-direction.md) (boundary mode) — **This is the method's exclusive value** (confronting the artifacts against each other); it **drafts** the boundary rearrangement as a labeled, ratification-gated proposal, never ratifying it alone. The *application* of the rearrangement uses the templates that own the touched artifacts (moving a standard from VISION to the standards = `quenching-docs` at the writing end).
