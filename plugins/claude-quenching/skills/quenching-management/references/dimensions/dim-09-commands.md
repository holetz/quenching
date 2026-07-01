# 9. Commands — .claude/commands/

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

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

  **Executable of a command/skill → the right `scripts/`:** a command/skill that **runs code** carries its internal `scripts/` (Agent Skills: *«`scripts/` for executables»*) for what is **specific to it**; what is a **repo executable** (build/checks/maintenance that other surfaces also invoke) lives in the **repo-level `scripts/`** (dim 8 / [../scripts-taxonomy.md](../scripts-taxonomy.md)), not buried inside a skill.

- **Detection:** `ls .claude/commands/`; cross-reference with existing skills; apply the migration criterion and check for basename collision between subfolders; check which read-only composable commands are **improperly gated** by `disable-model-invocation` and the **list weight** in the budget (item **9b** in [../detection-and-smells.md](../detection-and-smells.md)).

- **Smells:**
  - orphan command (corresponding skill removed); command that diverges from the skill it should mirror.
  - **migratable legacy command** — lives in `.claude/commands/` but passes the migration criterion (would gain auto-trigger / >50 lines / references files / is multi-repo).
  - **basename collision** — two `.md` with the same name in different `commands/` subfolders collide (the subfolder appears in the description but **does not** change the name — ambiguous `/name`).
  - **silent shadowing** — custom command with the same name as a *bundled skill* (e.g.: `code-review`/`verify`) shadows it without warning (`slash_commands` lists the name only once).
  - **gated-composable** — read-only step that should be chainable by the model but has `disable-model-invocation: true` (disappears from the `SlashCommand`/Skill tool, becomes only a manual shortcut).
  - **auto-invocable side-effect** — the inverse: deploy/commit/send command **without** the flag (the model can trigger a destructive action on its own — *"You don't want Claude deciding to deploy"*).
  - **inflated list/budget exceeded** — many long descriptions exceed the ~1% and `/doctor` reports **truncated/dropped** descriptions, blinding the routing (links to dim 1).

- **Remediation:** remove orphan; resync with skill; **migrate legacy command → skill** (`.claude/skills/<name>/SKILL.md` with description-trigger from dim 6; the command is removed or becomes a thin redirect); rename to resolve basename collision/shadowing.

- **Payload:** skill-template [../../assets/skills/quenching-skills/](../../assets/skills/quenching-skills/) (authoring/migration command→skill) + **ready command-skill** [../../assets/commands/quenching-reaudit/](../../assets/commands/quenching-reaudit/).
  - The package **carries** the first command (not just detecting absence): the on-demand re-audit (trigger (3) of Step 8), installed in `.claude/skills/<prefix>-reauditar/` as a **skill** (doctrine "command is born a skill" by construction: **reads and proposes**, so maintains auto-trigger; uses `context: fork` + `agent: quenching-auditor` to sweep in a clean context).
  - It is also the **example of a composable command**: read-only and auto-invocable (**without** `disable-model-invocation`), so Claude itself can **chain it** in a larger flow (e.g.: `/<prefix>-reauditar <dimension>` as a workflow step), not just the user.
  - *Exception:* the **legacy-command × skill × hook choice** (should it auto-trigger? should it be deterministic?) is the dim 12 boundary applied to mechanisms (mirrors 7b/8b) — the core **decides the home**; authoring comes from the `quenching-skills` template.
