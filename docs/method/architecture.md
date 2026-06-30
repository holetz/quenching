# Architecture of the `quenching-management` skill — how the pieces connect

This page is the **system map** — how the parts fit together. For what the skill
is, start with the [Home page](../index.md); for how to trigger it and the
scenarios it covers, see the [8-step workflow](workflow.md). The instructions the
agent executes are in
[SKILL.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md), with per-piece detail in
[references/](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/README.md) and [assets/](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md).

This page exists to answer, in one place, **what is being implemented and how
it operates as a system** — without needing to reconstruct the design by opening
twelve files. It **references** the spec; it does not rewrite it (each concept
has **one unique home** — this page links to it).

---

## What the skill does

The skill **applies the method** to a target repo — it audits the repo's
knowledge surface and installs what's missing. This is what fires when someone
asks "organize the repo's knowledge". Roadmap: the **8 steps** of
[SKILL.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md),
designed below.

> The method is also a **living method** — its dimensions, smells and payloads
> are improved over time. That work is **maintainer tooling of the development
> repo, never shipped or installed**, so it is out of scope for this page;
> contributors see [CONTRIBUTING.md](https://github.com/holetz/claude-quenching/blob/main/CONTRIBUTING.md).

---

## The audit/install flow

The flow is a **single line of 8 steps** (defined in [SKILL.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md)). Each
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

The **15 dimensions** ([references/dimensions-template.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md))
are the coverage checklist: each has purpose · "good" · detection · smells ·
remediation · **payload**. The payload is the artifact from [assets/](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md)
that the method **installs** to close the gap. The map below shows **which piece
addresses which dimension** (detail and install-in: [assets/README.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md)
and [references/installation.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/installation.md)):

| Dimension | Piece that addresses it | Type |
| --- | --- | --- |
| 1 · CLAUDE.md / context budget | `assets/skills/quenching-map/` + hook `validate-claude-md.py` | skill + hook |
| 2 · normative reference & `docs/` | `assets/skills/quenching-docs/`, `quenching-standards/`, `quenching-announcement/` + scaffold `assets/docs/` ([docs-taxonomy.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/docs-taxonomy.md)) | skills + skeleton |
| 3 · direction / VISION | — (only proposes; human content) | Step 6 |
| 4 · backlog | scaffold `assets/docs/backlog/` | skeleton |
| 5 · ADR / decisions | scaffold `assets/docs/decisions/` | skeleton |
| 6 · skills | `assets/skills/quenching-skills/` (+ recognizes domain artifact) | skill |
| 7 · sub-agents | `assets/agents/{quenching-auditor,quenching-writer}.md` | sub-agents |
| 8 · hooks (+ `scripts/` home) | the 6 hooks from [assets/hooks/](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/hooks/) (see below) + scaffold `assets/scripts/` ([scripts-taxonomy.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/scripts-taxonomy.md): hook calls script) | hooks + skeleton |
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
output semantics: [references/installation.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/installation.md) and dim 8
in [references/dimensions-template.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md).

---

## The orchestration contract — how the links compose

The Step 8 pieces don't live in isolation; they **chain** under a contract
(detail in the "Orchestration contract of links" subsection of
[SKILL.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md)):

- **Hook** = automatic trigger that **OBSERVES / PROPOSES / at most BLOCKS** —
  never mutates the base alone.
- **Command / skill** = on-demand step that **APPLIES, with OK** — the only link
  that changes the base.
- **Sub-agent** = isolated context that returns **condensed summary** — never
  floods the main context.

The barrier against "chaining too much" is **double**: human (the link that
mutates always has OK) and deterministic (the runtime caps sub-agent recursion).

---

## Why the active spec describes only the present

The method pages (SKILL.md / references / assets) describe **only the present** —
the system as it is today. The method is nonetheless a **living method**: its
*history* (how it got here — rounds, revisions, superseded decisions) and the
**eval-harness** that gates rule changes (fixtures with planted gaps, measuring
hit rate, false-negative and cost) live **outside the shipped package**, in the
development repo's maintainer tooling. None of that is shipped or installed into a
target repo. Contributors: see [CONTRIBUTING.md](https://github.com/holetz/claude-quenching/blob/main/CONTRIBUTING.md). That is why
you won't find "before/now" or round tags anywhere in the method spec.

---

## Where to read what (depth index)

| I want… | Go to |
| --- | --- |
| Understand what it is | [Home](../index.md) |
| Know how to trigger it and the scenarios | [The 8-step workflow](workflow.md) |
| See the whole system at once | **this page** |
| See how the repository is laid out | [Repository layout](layout.md) |
| Execute the audit (the 8 steps) | [SKILL.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md) |
| Detail of each dimension / smell / detection | [references/](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/README.md) |
| What each payload installs | [assets/README.md](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md) |
| Contribute to the method itself | [CONTRIBUTING.md](https://github.com/holetz/claude-quenching/blob/main/CONTRIBUTING.md) |
