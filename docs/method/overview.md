# quenching-management

> **START HERE (human entry).** This README is the **START-HERE** for anyone
> arriving at the folder: what the skill is, how to trigger it and which path to
> follow. If you want the **system design** (how the 15 dimensions, payloads,
> hooks, 8 steps and the two evolution agents connect), go to
> [ARCHITECTURE.md](architecture.md). The **instructions the agent executes**
> when the skill fires are in [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md) — read it to *execute*; read
> README + ARCHITECTURE to *understand and decide*.

**Portable, self-contained method + installer for knowledge management on the
Claude Code surface of any repository.** Audits what the target repo already has
(`CLAUDE.md`, `docs/`, skills, sub-agents, hooks, commands, memory, catalog,
MCP), confronts it with a template of 15 dimensions, delivers a **prioritized
gap report** and — **with confirmation, item-by-item** — **installs the own
artifacts it carries** ([assets/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/)) into the target's `.claude/`/`docs/`.

### Three reading doors

| You want… | Open | For whom |
| --- | --- | --- |
| Understand, decide, trigger | **this README** | human (start-here) |
| See the whole system in one diagram | [ARCHITECTURE.md](architecture.md) | human |
| Execute the audit (8 steps) | [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md) | agent |

---

## What it is (one sentence per idea)

- **Self-contained:** everything the method needs to audit and install lives
  **inside the skill**, in [assets/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/) (template-skills, sub-agents,
  hooks, `docs/` skeletons, frontmatter templates). Does not depend on any
  external skill — runs on a repo from scratch.
- **Portable:** does not impose a foreign structure. First **derives the target
  repo's shape** (language, prefix taxonomy, where each layer lives) and adapts
  artifacts to it. **Where the repo already has a convention, the repo's
  convention wins** — the only exception is the `docs/` name tree, which is a
  **prescriptive canonical taxonomy** (the repo converges to it, with OK).
- **Pure installer, not delegator:** where the repo already has an artifact doing
  the same job, the method **installs the package's one** (the single, versioned,
  evolved source here) and **flags the pre-existing one as DEPRECABLE** — never
  duplicates silently, never removes without OK.
- **Diagnosis-first:** always delivers the report first; installation is an
  **explicit second step** with the user's OK.

### Two different things that live in this folder

| | **Apply** the method | **Evolve** the method |
| --- | --- | --- |
| What | audit/install the knowledge base of a **target repo** | improve the **skill itself** (dimensions, smells, payloads) |
| Who | this skill, Steps 1-8 of [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md) | sub-agents [`evolutionist`](https://github.com/israelholetz/claude-quenching/blob/main/.claude/agents/quenching-evolutionist.md) / [`reviewer`](https://github.com/israelholetz/claude-quenching/blob/main/.claude/agents/quenching-reviewer.md) |
| Trigger | "organize the repo's knowledge", "install the base", "audit" | "evolve/critique/refine the knowledge method" |
| Record | gap report (ephemeral) | log in [evolution/](../evolving/index.md) (spine [evolution/README.md](../evolving/index.md) + [evolution/log/](../evolving/index.md)) |

The **three scenarios below are all about _applying_.** Method evolution has
its own section at the end.

---

## How to trigger

The method fires by description when you ask to **organize/audit the repo's
knowledge**, **install the knowledge base for Claude Code**, **prepare a repo
from scratch for Claude**, **review docs/skills/hooks/agents/CLAUDE.md**,
**see what's missing from the base**, or describe a mess/gap in the knowledge
surface. Can also be invoked by name (`/quenching-management`).

The flow is always the same (detail in [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md), Steps 1-8); what
changes by scenario is **where the roadmap weighs**:

1. **Derive the shape** of the target repo (read-only).
2. **Inventory** each of the 15 dimensions with the adaptive globs from
   [references/detection-and-smells.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/detection-and-smells.md).
3. **Score** each dimension: **Present · Partial · Drifted · Absent**, always
   with `file:line` evidence.
4. **Prioritized report** in the format from
   [references/report-format.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/report-format.md).
5. **Propose → install with confirmation** the package payload
   ([references/installation.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/installation.md)).
6. Items **without payload** (direction, memory, boundaries) → the method
   **only proposes**.
7. **Flag deprecables**.
8. **Establish the recurring maintenance cycle** (the base is alive).

---

## Scenario A — new repo (from scratch)

Almost everything is **Absent**; the method becomes the **roadmap to install the
structure**.

1. Ask to **"prepare this repo for Claude Code"** / **"install the knowledge
   base"**.
2. The method derives the little that exists (language, any initial `CLAUDE.md`)
   and presents the report with almost all dimensions as gaps.
3. Confirm installation **item-by-item**. Typically in this order of value:
   - **CLAUDE.md** as map + ceiling hook
     ([assets/hooks/validate-claude-md.py](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/hooks/validate-claude-md.py));
   - **canonical `docs/` taxonomy** ([assets/docs/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/docs/):
     `standards/`, `decisions/`, `vision/`, `backlog/`, `guides/`, `reference/`,
     `catalog/`, `communications/`, `presentations/`) — **only the homes that
     apply** (repo without data doesn't get `catalog/`);
   - **knowledge template-skills** ([assets/skills/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/skills/)) and
     **sub-agents** ([assets/agents/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/agents/));
   - **lifecycle hooks** and the **re-audit command**
     ([assets/commands/quenching-reaudit/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/commands/quenching-reaudit/)).
4. Each installed artifact is **adapted** to the repo's language/prefix — the
   payload is the starting point, not a rigid mold.
5. **Human content is not installed:** direction (`docs/vision/`), memory and
   the boundary doctrine the method **only proposes** — you write.

Result: a coherent `.claude/`/`docs/` and the **recurrent cycle** already wired
(Scenario C applies for future rounds).

---

## Scenario B — existing repo (audit, install what's missing, deprecate)

The most common case. The method **measures what's there** and installs **only
the gaps**.

1. Ask to **"audit/organize the repo's knowledge"** or **"see what's missing
   from the base"**. For large repos, it can delegate the scan to the read-only
   sub-agent [assets/agents/quenching-auditor.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/agents/quenching-auditor.md)
   (clean context, cheap model).
2. Read the **scorecard per dimension** + the **prioritized gaps** (P1/P2/…).
   Priority combines severity (`drifted`/broken > absent > partial) × cost ×
   whether there's a ready payload.
3. Pay attention to two sections of the report:
   - **Deprecables** — skills/agents/hooks the repo already had and that a
     package payload now covers. The method **installs the single source** and
     lists the old one; removal is **your decision** (and if the repo's one is
     better adapted, it offers **keeping yours** and discarding the payload).
   - **`docs/` variant names** (`docs/arquitetura/` → `standards/`,
     `docs/adr/` → `decisions/`, single `VISION.md` → `vision/`,
     `docs/catalogo_dados/` → `catalog/`): the method **proposes migration to
     the canonical name** — converge, not preserve — always with OK.
4. Confirm installation **item-by-item**. **Generated** repo artifacts
   (`*.job.yml`, manifests, AUTO-GENERATED catalog, lockfiles) are **never
   touched** — the repo's "X defines Y" rule is respected.

---

## Scenario C — repo that already applied (maintenance and structure evolution)

Auditing **once** leaves the base fresh **today** — but it **rots** as the
code, models and team change (*context rot*). So the method **doesn't end with
the report**: it installs (Step 8) the **recurring operational loop** that keeps
the surface alive, with **three triggers** and the **right home** for each. In
a repo that already applied the structure, maintenance is **operating those
triggers**, not re-installing:

- **On event, in the PR (drift trigger):** touching `CLAUDE.md`/`docs/` is a
  doc change like any other. A **PR hook** re-runs detection of the touched
  scope and **PROPOSES** (does not block) the gaps — it is the recurrent backlog
  item of dim 4.
- **On cadence, at model release (review trigger):** revisit the base when
  switching models — an instruction that existed to work around an older model's
  limitation may become **overhead** (skill/rule the model already does on its
  own ⇒ deprecable).
- **On demand, by command (manual trigger):** the **`/<prefix>-reaudit` command**
  ([assets/commands/quenching-reaudit/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/commands/quenching-reaudit/))
  fires the re-examination (Steps 1-7, or the scope the argument requests) and,
  in large repos, delegates to the auditor sub-agent in clean context.

**Automatic freshness between audits** comes from hooks installable by the
method:

| Hook | Event | What it does |
| --- | --- | --- |
| [propose-knowledge-delta.py](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/hooks/propose-knowledge-delta.py) | `Stop` | reads the transcript at the end of the turn and **proposes** CLAUDE.md/memory deltas "while the gap is still fresh" (exit 0, never blocks) |
| [reinject-conventions.py](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/hooks/reinject-conventions.py) | `SessionStart` (`compact`/`clear`/`resume`) | **re-injects** conventions/FQNs/guardrails that `/compact` would erase (reads from target-derived source) |
| [audit-config-change.py](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/hooks/audit-config-change.py) | `ConfigChange` | **records** who/when/what changed on the surface (metadata only, append-only) |
| [propose-docs-home.py](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/hooks/propose-docs-home.py) | `PostToolUse` (`Write\|Edit`) | when a doc is written outside the canonical home, **proposes** the right home |
| [protect-generated.py](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/hooks/protect-generated.py) | `PreToolUse` (`Write\|Edit`) | **BLOCKS** editing of generated target artifacts (`protectedGlobs` derived from target) |

**Typical maintenance:** run the re-audit command periodically (or when the
PR/Stop hook signals), treat the report as in Scenario B (install what remained
Absent, fix Drifted, migrate variants, deprecate what's left), and rely on the
hooks for freshness between rounds.

---

## Folder map

| Path | What it is |
| --- | --- |
| [ARCHITECTURE.md](architecture.md) | **single system view** (human): how dimensions ↔ payloads ↔ hooks ↔ 8 steps ↔ evolution agents ↔ eval connect |
| [SKILL.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md) | **operational instructions** the agent loads when firing (Steps 1-8) |
| [references/README.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/README.md) | **index of `references/`** — what each file is, when to open it, how they chain |
| [references/dimensions-template.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md) | the **15 dimensions** (purpose · "good" · detection · smells · remediation · payload + absorbed doctrine) |
| [references/docs-taxonomy.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/docs-taxonomy.md) | the **canonical `docs/` taxonomy** (single source of home names) |
| [references/detection-and-smells.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/detection-and-smells.md) | the detection **cookbook**: adaptive globs/greps per dimension + the rule of 4 states |
| [references/repo-profiles.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/repo-profiles.md) | catalog of **repo profiles** (signals → emphasis) that Step 4 consults |
| [references/report-format.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/report-format.md) | skeleton of the **report** (scorecard · gaps · deprecables · plan) |
| [references/installation.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/installation.md) | **gap → payload** map + **deprecation** doctrine and `docs/` convergence |
| [assets/](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/) | **installable payloads** (skills, agents, hooks, `docs/` skeletons, frontmatter) — see [assets/README.md](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md) |
| [evolution/](../evolving/index.md) | **method evolution**: spine/index in [evolution/README.md](../evolving/index.md) (anchor-state, exclusion, backlog, review queue), per-context detail in [evolution/log/](../evolving/index.md), research input in [evolution/research/](../evolving/index.md) |

---

## Evolving the method itself (≠ applying it)

The method is **alive**. Don't edit it by hand outside the flow below — that
breaks the log that prevents re-attacking the same problem. Two complementary
sub-agents maintain it:

- [quenching-evolutionist](https://github.com/israelholetz/claude-quenching/blob/main/.claude/agents/quenching-evolutionist.md) —
  **advances the frontier**: one new improvement per round (`R*`), on a topic
  not yet addressed. Trigger: *"evolve the knowledge method"*, *"run an
  evolution round"*.
- [quenching-reviewer](https://github.com/israelholetz/claude-quenching/blob/main/.claude/agents/quenching-reviewer.md) — **critiques and refines
  what already exists**: one revision per invocation (`Rev*`), sharpens/merges/
  prunes/supersedes a made definition. Trigger: *"critique/review/refine the
  method"*, *"go back to a round"*.

Both read the next action in the spine [evolution/README.md](../evolving/index.md)
and write the detail in the right context file in [evolution/log/](../evolving/index.md)
(ID conventions and routing in [evolution/log/README.md](../evolving/index.md)).
Before closing a round that changes a detection rule, the evolutionist runs a
**fixtures harness** with planted gaps (hit rate, false-negative, cost) — application
to a real repo (Steps 1-8) **does not** run this harness.
