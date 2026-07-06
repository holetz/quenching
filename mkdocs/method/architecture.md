# Architecture — how the tool works

This is the Technical guide's reference on **how the parts fit together as a
system**: how the skill turns "organize this repo's knowledge" into a concrete
audit and a set of installed artifacts. For *why the harness is the work*, see the
[Context](../context/index.md) movement; for *what it measures*, see
[The 15 dimensions](dimensions/index.md); for *how you run it step by step*, see the
[8-step workflow](../plugin/workflow.md).

The page answers one question — **how the parts fit together as a system** — and
then hands each part to its own page. It does not restate them.

## What the skill does

The plugin ships one skill, `quenching-management`. Point it at a repository and
it does two things, in order: it **audits** the repo's knowledge surface against a
fixed checklist, then — only with your confirmation — it **installs** the artifacts
that close the gaps. The instructions the agent follows live in
[`SKILL.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md);
the per-piece detail lives in
[`references/`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/README.md)
and the installable payloads in
[`assets/`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md).

## The governing axis — audit by default, install with confirmation

Everything hangs off one axis: **the report always comes first; installation is a
separate, explicit, item-by-item step.** The audit is read-only and complete (it
scores every dimension); installation only happens after you say yes, one artifact
at a time, and it never removes anything you already have without an OK.

```
   [ target repo ]
         │
         ▼
   ┌───────────────┐   read-only — derive the repo's shape, score all 15
   │     AUDIT     │   dimensions Present / Partial / Drifted / Absent,
   └───────────────┘   with file:line evidence
         │
         ▼
   ┌───────────────┐   prioritized gaps, deprecables, and an install plan —
   │    REPORT     │   emphasis tuned to the repo's profile
   └───────────────┘
         │  (your OK, item by item)
         ▼
   ┌───────────────┐   stamp the package payloads into .claude/ and docs/,
   │    INSTALL    │   adapted to the repo; three dimensions are proposed,
   └───────────────┘   never written (human content)
         │
         ▼
   ┌───────────────┐   hooks, a re-audit command and sub-agents keep the
   │  MAINTENANCE  │   surface fresh between audits
   └───────────────┘
         │
         ▼
   [ a living .claude/ + docs/ ]
```

The prose form of these stages — the 8 steps and the three usage scenarios — is
the [workflow page](../plugin/workflow.md). This page stays at the level of *which
parts exist and how they relate*.

## Fixed vs. adaptive — what converges, what the repo keeps

The method is **portable**: it does not impose a foreign structure. But "portable"
does not mean "anything goes" — some things **adapt to the repo** and some things
the repo **converges toward**. Keeping this line clear is what stops the method
from either fighting the repo or letting every repo drift into its own shape. Every
dimension page tags its canonical home **Fixed** or **Adaptive** using exactly this
distinction.

**Adaptive — the repo's own convention wins.** The method derives these in Step 1
and bends its artifacts to fit:

- the **naming/prefix** of skills and agents, and the language of **product code
  and human-only material** (docstrings, `presentations/`, `communications/`,
  `audience: human` guides);
- **where** a layer physically lives (the exact path of the CLAUDE.md(s), the
  `.claude/` location);
- **which** homes actually apply — a repo with no data gets no `catalog/`;
- the **priority and emphasis** ordering, tuned to the repo's profile.

**Fixed — canonical, the repo converges with your OK.** These are prescriptive so
that anyone moving between repos sees the *same* tree of the *same* names instead
of re-learning each one:

- the `docs/` home tree — `standards/`, `decisions/`, `vision/`, `backlog/`,
  `guides/`, `reference/`, `catalog/`, `communications/`, `presentations/`
  (single source:
  [`docs-taxonomy.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/docs-taxonomy.md));
- the `scripts/` purpose tree — `ci/`, `checks/`, `<gen>/`, `maintenance/`, `dev/`
  (single source:
  [`scripts-taxonomy.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/scripts-taxonomy.md));
- **English kebab-case** folder names; the four scoring states; the *"X defines Y"*
  rule (a generated artifact is never hand-edited);
- the **agent-facing knowledge surface is English** — `docs/standards/**`, every
  `CLAUDE.md`, the `.claude/` skills/agents/hooks, and all frontmatter keys+enums —
  so the surface stays uniform and cross-repo greppable (only `audience: human`
  material and the product code keep the repo's own language).

Variant names — `docs/arquitetura/`, `docs/adr/`, a single `VISION.md` — are
**migration candidates**, proposed for convergence and never renamed or deleted
without your confirmation.

## The four kinds of pieces

Read top to bottom, the system is just four kinds of parts, each with its own home:

- **Dimensions** — the coverage checklist the audit scores. What each one is, why
  it belongs, and how it drifts is on its own page under
  [The 15 dimensions](dimensions/index.md).
- **Payloads** — the artifacts the method installs to close a gap (skills, hooks,
  sub-agents, `docs/`/`scripts/` scaffolds, templates). The full manifest is
  [Bundled artifacts](../plugin/artifacts.md).
- **Hooks** — the subset of payloads that keep the surface fresh *between* audits.
  Most observe or propose; one always blocks. The table of all six lives in
  [Bundled artifacts](../plugin/artifacts.md).
- **Orchestration** — the contract that lets these compose without runaway: a
  **hook** observes/proposes (at most blocks), a **command or skill** applies *with
  your OK*, a **sub-agent** returns a condensed summary. The link that mutates the
  base always has a human in the loop; the runtime caps sub-agent recursion. The
  step-by-step form is Step 8 of the [workflow](../plugin/workflow.md).

## A living method

The skill describes only the **present** — the system as it is today. Its history
(how it got here) and the eval harness that gates rule changes are **maintainer
tooling of this repo, never shipped or installed**, so they are out of scope here.
Contributors: see
[CONTRIBUTING.md](https://github.com/holetz/claude-quenching/blob/main/CONTRIBUTING.md).
