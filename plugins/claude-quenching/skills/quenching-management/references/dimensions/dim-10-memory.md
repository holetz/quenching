# 10. Memory — memory directory + index (Auto Memory)

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** what the **agent** discovered during work (build commands, debug insights, project context/constraints, user preferences) — durable between sessions, **machine-local**, auditable via `/memory`. It is the counterpart of CLAUDE.md: this is what *any team member needs to know* (versioned); Auto Memory is what *the agent learned* (local).

- **How "good" looks:** the index (`MEMORY.md`) has **one line < ~150 characters per memory** (title + hook + link), **within the load ceiling** — only the first **200 lines / 25 KB** enter the session (what exceeds this does not load); detail goes to **topic files** (not loaded at startup, read on demand). Each memory named by the **type** the repo adopts as prefix (derive them — e.g.: `user_`/`feedback_`/`project_`/`reference_`); entry **dated and with provenance**; without duplicating what already lives in the repo (code/CLAUDE.md/standards → reference by link/`@path`, not copy). Structurally this **is already an OKF-style bundle** (one concept per `.md`, identity-by-path, `MEMORY.md` ≙ `index.md`): keep each entry's **type non-empty** (the prefix/`metadata.type` ≙ OKF `type`) and dates exact ISO (≙ `timestamp`) — the harness owns the format; the equivalence is what makes the memory directory readable by any bundle consumer, no format change required.

- **Detection:** read the project's memory directory index (path in the session context); cross-reference index × `.md` files alongside (`/memory` lists the loaded ones). Run the **hygiene checklist** (below). The method may **draft** candidate entries as labeled drafts, but **never ratifies/commits** memory — that stays the `/memory` flow / the human.

- **Smells (hygiene checklist — 6 verifiable):**

  | # | Smell | What it is |
  | --- | --- | --- |
  | 1 | **index orphan** | topic file without a line in the index (invisible to loading); or index >200 lines/25 KB (the tail never loads) |
  | 2 | **duplicates the repo** | the entry repeats something already in code/CLAUDE.md/standards instead of linking to it (dim 12 applied to memory) |
  | 3 | **vague temporal reference** | "recently"/"last time"/"today" instead of an **exact date** |
  | 4 | **silent conflict** | two contradictory entries, invisible *last-write-wins* (one marked "WRONG/CORRECTED/superseded" that should be **pruned**, not accumulated) |
  | 5 | **degraded freshness** | expired/obsolete fact that poisons future context (*context poisoning by staleness*) |
  | 6 | **wrong type/scope** | team-convention living in Auto Memory (should be CLAUDE.md/standards) or agent-learning in prose in CLAUDE.md (should be Auto Memory); type prefix swapped vs. the content |

- **Remediation:** the method **points out** the divergence (which smell, which `file:line`) and may **draft** a candidate entry as a labeled `background` draft; **committing/pruning** memory is the `/memory` flow / human, **not** an unratified method write. For smell (2), remediation is replacing the copy with a link/`@path` (dim 12).

- **Payload:** **direction-draft discipline** [../../assets/agents/quenching-direction.md](../../assets/agents/quenching-direction.md) (memory mode) — drafts candidate entries as **labeled drafts** the human ratifies via `/memory`; **never ratifies memory as fact**. Entry template [../../assets/templates/memory/memory.md](../../assets/templates/memory/memory.md) for the format.
