# Architecture of the `quenching-management` skill — how the pieces connect

> **You are on a HUMAN overview page.** Entry point:
> [README.md](overview.md) (what it is, how to trigger it, the scenarios). This
> page is the **system map** — how the parts fit together. The **instructions
> the agent executes** are in [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md); the **detail** of each
> piece, in [references/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/README.md) and [assets/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md).

This page exists to answer, in one place, **what is being implemented and how
it operates as a system** — without needing to reconstruct the design by opening
twelve files. It **references** the spec; it does not rewrite it (each concept
has **one unique home** — this page links to it).

---

## Two machines in the same folder

The skill is, in fact, **two mechanisms** that share the same artifacts:

1. **Apply the method** to a target repo — audit its knowledge surface and
   install what's missing. This is what fires when someone asks "organize the
   repo's knowledge". Roadmap: the **8 steps** of [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md).
2. **Evolve the method itself** — improve the dimensions, smells and payloads
   over time. This is what two sub-agents do, with a traceable log. Lives in
   [evolution/](../evolving/index.md).

The "Two different things that live in this folder" table in [README.md](overview.md)
details who triggers which. Below, the design of each.

---

## Machine 1 — apply the method (the audit/install flow)

The flow is a **single line of 8 steps** (defined in [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md)). Each
step consults a reference piece and/or produces/consumes an artifact:

```
                                 [ target repo ]
                                       │
 Step 1  derive the shape  ............│..........  read-only; discovers language,
          (+ note the profile)         │             taxonomy, where each layer lives
                                       ▼
 Step 2  inventory 15 dimensions ......│..........  detection-and-smells.md (the greps)
                                       │             dimensions-template.md (what to measure)
                                       ▼
 Step 3  score: Present/Partial/......│..........  4 states + file:line evidence
          Drifted/Absent              │
                                       ▼
 Step 4  prioritized report ...........│..........  report-format.md (the skeleton)
          + modulate emphasis by profile│            repo-profiles.md (signals → emphasis)
                                       │             quenching-roadmap (sequenced order)
                                       ▼
 Step 5  propose → INSTALL with OK ....│..........  installation.md (gap → payload)
          (item-by-item)               │             assets/ (the stamped payloads)
                                       ▼
 Step 6  items without payload → propose│..........  dims 3 (direction) · 10 (memory) · 12
          (human content decision)     │             (boundaries): only text, never applies
                                       ▼
 Step 7  flag deprecables .............│..........  what the package payload replaces
                                       ▼
 Step 8  maintenance cycle ............│..........  3 triggers (PR · release · command)
          (the base is alive)          │             + orchestration contract of links
                                       ▼
                        [ .claude/ + docs/ of target, alive ]
```

**The axis that ties everything together:** *audit-by-default + install-with-confirmation*.
The report always comes **first** (Steps 1-4); installation (Steps 5-7) is an
explicit second step, **item-by-item, with OK**; Step 8 ensures the base
**doesn't rot** afterwards.

---

## The 15 dimensions and the artifacts that fill them

The **15 dimensions** ([references/dimensions-template.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md))
are the coverage checklist: each has purpose · "good" · detection · smells ·
remediation · **payload**. The payload is the artifact from [assets/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md)
that the method **installs** to close the gap. The map below shows **which piece
addresses which dimension** (detail and install-in: [assets/README.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md)
and [references/installation.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/installation.md)):

| Dimension | Piece that addresses it | Type |
| --- | --- | --- |
| 1 · CLAUDE.md / context budget | `assets/skills/quenching-map/` + hook `validate-claude-md.py` | skill + hook |
| 2 · normative reference & `docs/` | `assets/skills/quenching-docs/`, `quenching-standards/`, `quenching-announcement/` + scaffold `assets/docs/` ([docs-taxonomy.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/docs-taxonomy.md)) | skills + skeleton |
| 3 · direction / VISION | — (only proposes; human content) | Step 6 |
| 4 · backlog | scaffold `assets/docs/backlog/` | skeleton |
| 5 · ADR / decisions | scaffold `assets/docs/decisions/` | skeleton |
| 6 · skills | `assets/skills/quenching-skills/` (+ recognizes domain artifact) | skill |
| 7 · sub-agents | `assets/agents/{quenching-auditor,quenching-writer}.md` | sub-agents |
| 8 · hooks (+ `scripts/` home) | the 6 hooks from [assets/hooks/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/hooks/) (see below) + scaffold `assets/scripts/` ([scripts-taxonomy.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/scripts-taxonomy.md): hook calls script) | hooks + skeleton |
| 9 · commands | `assets/commands/quenching-reaudit/` (composable command, installs as skill) | skill |
| 10 · memory | — (only proposes; human content) | Step 6 |
| 11 · catalog / domain | scaffold `assets/docs/catalog/` + templates | skeleton |
| 12 · boundary doctrine | — (only proposes the home; human content) | Step 6 |
| 13 · conventions | `assets/skills/quenching-map/` + frontmatter templates | skill |
| 14 · guardrails | `assets/skills/quenching-guardrails/` + enforcement hook `protect-generated.py` | skill + hook |
| 15 · MCP | `assets/skills/quenching-config/` | skill |

> **Three dimensions never install (3 · 10 · 12)** — they are **human content
> decisions**. The method only **proposes** the text/diff; the repo writes it.
> This is the limit "modulate the METHOD, never define the CONTENT".

---

## The 6 hooks — what keeps the base fresh between audits

Dimension 8 installs hooks that provide **automatic freshness** (Step 8). Most
**observe/propose**, one **always blocks**, one **can block if configured** —
the *guidance* (probabilistic) × *enforcement* (deterministic) distinction is
central:

| Hook | Event | Role | Blocks? |
| --- | --- | --- | --- |
| `propose-knowledge-delta.py` | `Stop` | proposes CLAUDE.md/memory delta at end of turn | no |
| `reinject-conventions.py` | `SessionStart` (compact/clear/resume) | re-injects conventions that `/compact` would erase | no |
| `audit-config-change.py` | `ConfigChange` | records who/when changed the surface (append-only) | no |
| `propose-docs-home.py` | `PostToolUse` (Write\|Edit) | proposes the canonical home for a doc written outside it | no |
| `protect-generated.py` | `PreToolUse` (Write\|Edit) | **BLOCKS** editing of generated target artifacts | **yes** |
| `run-validation.py` | `Stop` | at end of turn **CALLS the target's validation script** (`scripts/checks`/`ci`) on altered files and proposes the result | optional (`blockOnFail`) |

Detail of wiring (each hook only runs if **wired** in `settings.json`) and
output semantics: [references/installation.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/installation.md) and dim 8
in [references/dimensions-template.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md).

---

## The orchestration contract — how the links compose

The Step 8 pieces don't live in isolation; they **chain** under a contract
(detail in the "Orchestration contract of links" subsection of
[SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md)):

- **Hook** = automatic trigger that **OBSERVES / PROPOSES / at most BLOCKS** —
  never mutates the base alone.
- **Command / skill** = on-demand step that **APPLIES, with OK** — the only link
  that changes the base.
- **Sub-agent** = isolated context that returns **condensed summary** — never
  floods the main context.

The barrier against "chaining too much" is **double**: human (the link that
mutates always has OK) and deterministic (the runtime caps sub-agent recursion).

---

## Machine 2 — evolving the method itself

The method is **alive**. Two complementary sub-agents maintain it, and **every**
move is logged to avoid re-attacking the same problem:

```
        evolution/README.md  (spine: anchor-state · exclusion · backlog · queue)
                  │
   ┌──────────────┴───────────────┐
   ▼                              ▼
 quenching-evolutionist          quenching-reviewer
 ADVANCES the frontier (R*)    REFINES what exists (Rev*)
 increments current-round      does not increment (last-revision)
   │                              │
   └──────────────┬───────────────┘
                  ▼
        evolution/log/<context>.md  (detail per dimension/topic)
                  ▲
                  │
        evolution/research/  (input: official sources + eval fixtures)
```

- [`quenching-evolutionist`](https://github.com/israelholetz/claude-quenching/blob/main/.claude/agents/quenching-evolutionist.md) — one
  **new** improvement per round (`R*`), on a topic not yet addressed.
- [`quenching-reviewer`](https://github.com/israelholetz/claude-quenching/blob/main/.claude/agents/quenching-reviewer.md) — one **revision** per
  invocation (`Rev*`): sharpens, merges, prunes or supersedes a made definition.

**The eval-harness** connects the two machines: before closing a round that
changes a detection rule, the evolutionist runs **fixtures** (sample repos with
planted gaps) and measures hit rate, **false-negative** (the most important
metric) and cost — so the new rule only enters if it **adds signal**. Fixtures
and measures in [evolution/research/](../evolving/index.md) (catalog
`14-eval-fixtures.md`). The complete doctrine lives in the "Evaluation of the
audit itself" section of [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md).

> **Why the active spec doesn't tell history:** the method pages
> (SKILL.md/references/assets) describe **only the present**. The *how it was ×
> how it is* (rounds, revisions, superseded decisions) lives **only** in
> [evolution/](../evolving/index.md). That's why you won't see "before/now" or
> round tags here — only the system as it is today.

---

## Where to read what (depth index)

| I want… | Go to |
| --- | --- |
| Understand what it is and how to trigger | [README.md](overview.md) — the human entry |
| See the whole system at once | **this page** |
| Execute the audit (the 8 steps) | [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md) |
| Detail of each dimension / smell / detection | [references/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/README.md) |
| What each payload installs | [assets/README.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md) |
| How the method was evolving (history) | [evolution/](../evolving/index.md) |
