# 1. Entry map — CLAUDE.md

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** routing "what do I, the agent, do now / which file contains what". It is **always-loaded** (enters context at every session start, before the first message) — consumes **fixed** context budget. Its counterpart is **on-demand** (skills, subfolder sub-CLAUDE.md, `docs/`): only loaded when relevant.

- **How "good" looks:** root is a **map**, not a contract; within the repo's line ceiling (a hook validates — the package loads one: [../../assets/hooks/validate-claude-md.py](../../assets/hooks/validate-claude-md.py)); chains sub-CLAUDE.md by scope; every link resolves; short directive + link to the current/active detail, never the full detail.

  - **Pruning criterion (per line, verifiable):** *"if I remove this line, would Claude make a mistake?"* — if not, **cut** or **convert**: mandatory rule → hook (dim 8); procedure "when I do X, I follow Y" → skill (dim 6); detail that changes often → link.
  - **Always-loaded × on-demand boundary (decides the home):** only what applies **broadly** goes in CLAUDE.md; domain/flow knowledge only-sometimes-relevant goes to **skills** (loaded on demand, without bloating every conversation).
  - **`@import` does NOT save context** — it is expanded inline and counts against the budget equally; it only serves human maintenance of the file.
  - **The "common commands" the map documents are invocations of `scripts/`** — build/deploy/checks/dev that the agent cannot guess. CLAUDE.md cites the **single execution convention** (e.g., `python -m scripts.<package>.<module>`) + link to the `scripts/` map; the canonical home of those executables (organization by purpose, README-map) is dim 8 / [../scripts-taxonomy.md](../scripts-taxonomy.md), not CLAUDE.md.

  | Belongs in CLAUDE.md (✅) | Does NOT belong (❌) |
  | --- | --- |
  | commands Claude cannot guess | what Claude infers from reading the code |
  | style rules that differ from the default | standard language conventions |
  | test/runner instructions | detailed API doc (link instead) |
  | repo etiquette (branch/PR) | info that changes frequently |
  | **project-specific** architecture decisions | long explanation/tutorial |
  | environment quirks (env vars) | file-by-file description |
  | non-obvious gotchas | obvious practice ("write clean code") |

- **Detection:** `find . -name CLAUDE.md`; read root; check ceiling hook and whether it points to an existing script; run the pruning criterion line-by-line (item **1b** in [../detection-and-smells.md](../detection-and-smells.md)).

- **Smells:**
  - above the repo's ceiling; became a **contract** (long normative rule instead of a link); broken link; outdated tech stack.
  - **orphan sub-CLAUDE.md** (exists but the root doesn't point to it) or **pointed to but nonexistent**.
  - **rule that survives the pruning criterion** — a line that, if removed, would not change behavior (model default, style already in the linter, obvious practice).
  - **mandatory rule in prose that should be a hook** — guidance ≠ enforcement (CLAUDE.md is a guide, not enforcement).
  - **context rot / fossil** — a directive describing a **replaced** pattern (the standards changed and the map didn't follow), poisoning the context loaded in every session.

- **Remediation:** trim to a map; break into sub-file; fix/retarget link; **prune** the line that doesn't pass the criterion; **convert** mandatory rule to hook (dim 8) or long procedure to skill (dim 6); **update** the fossil to point to the current/active pattern.

- **Payload:** skill-template [../../assets/skills/quenching-map/](../../assets/skills/quenching-map/) (hygiene/pruning/chaining of CLAUDE.md) + hook [../../assets/hooks/validate-claude-md.py](../../assets/hooks/validate-claude-md.py) (line ceiling) + template [../../assets/templates/claude/claude-md.md](../../assets/templates/claude/claude-md.md).
