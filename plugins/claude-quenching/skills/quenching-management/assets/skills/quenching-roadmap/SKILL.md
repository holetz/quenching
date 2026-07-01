---
name: quenching-roadmap
description: >-
  PRODUCES a SEQUENCED, actionable roadmap of "how to get the most out of the
  knowledge-management method IN THIS REPO" — reads the derived shape (Step 1),
  the repo profile (repo-profiles.md), and the report scorecard, and proposes the
  INVESTMENT ORDER in the METHOD/structure: invest first in X, then Y, then Z,
  ordered by leverage × cost × prerequisite (map/CLAUDE.md and boundaries before
  hooks; boundaries before skills; trigger before payload). It is read-only and
  PROPOSITIONAL: never installs or decides CONTENT (does not say what to write in
  VISION/memory) — only sequences WHICH artifacts of the package to install first
  and WHICH triggers to wire first. Use when the user asks "where do I start?",
  "what's the installation order?", "what to install first in .claude/?", "how to
  get the most out of the method in this repo?", "build an adoption roadmap",
  "sequence the gaps from the report", or when preparing a greenfield repo from
  scratch for Claude Code.
when_to_use: >-
  generate a sequenced adoption roadmap (invest first in X, then Y) of the
  knowledge structure/method for THIS repo, ordered by leverage×cost×prerequisite
  — proposes the installation order, never the content; ideal for a greenfield
  repo or to sequence the report.
allowed-tools: Read, Grep, Glob, Bash
context: fork
agent: quenching-auditor
---

# Adoption roadmap — "invest first in…" sequenced (proposes, does not install)

> **Payload of the [`quenching-management`](../../../SKILL.md) method.**
> Materializes the block **"For THIS repo, invest first in…"** of Step 4 as
> a **SEQUENCED installable roadmap** — the other half of what the profile
> taxonomy ([`repo-profiles.md`](../../../references/repo-profiles.md)) leaves open.
> Generic and portable: adapt prefix/language to the conventions of the repo
> where it is installed. Runs in **clean context** (`context: fork` + `agent:
> quenching-auditor`) to scan without flooding the main thread.

## What this skill is (and is NOT) — boundary

- **It is** a **sequencer**: reads the derived shape + profile + scorecard and
  proposes the **INVESTMENT ORDER in the METHOD/structure** — *which artifact of
  the package to install first, which trigger to wire first* —, ordered by
  **leverage × cost × prerequisite**.
- **Does NOT install.** It is **read-only and propositional**: produces the
  roadmap; installation follows item by item with OK through Steps 5-7 of the
  method (operating model: *audit-by-default + install-with-confirmation*). By
  reading-and-proposing (no side-effect), it **keeps auto-triggering by
  description** (dim 9: read-only is born as a skill with a trigger; if it ever
  gains a side-effect, then `disable-model-invocation: true`).
- **Does NOT decide CONTENT.** It sequences *which dimensions/payloads/triggers*
  the repo should **install first** — never *what to write* in VISION, memory, or
  boundaries. "Install the map (dim 1) before hooks" is **method**; "your VISION
  is X" would be **content** — and content is only Step 6 (proposes the home, not
  the text). This is the boundary the method does not cross; the roadmap respects
  it by construction.
- **Does NOT replace** `quenching-reaudit` (which re-runs the audit and produces
  the scorecard) or the report (Step 4). It **consumes** their output and
  **sequences it**. Without a fresh scorecard, it derives the minimum itself
  (Step 1) and continues.
- **Is RE-RUNNABLE on cadence** (trigger (2) of Step 8 — model release/periodic
  review). The **profile of a repo is live** (greenfield→mature, lib→service,
  data-pipeline→MLOps), so the order it proposed **ages** with the shape. Run
  again with **today's** shape, it **re-derives the profile + re-sequences** the
  roadmap — *"given how the repo has evolved since the last audit, now invest
  in…"*. Being read-only, just **re-invoke it**: no new artifact to install.

## Why SEQUENCE (and not just list)

The official docs say that you don't configure everything at once — *"You don't
need to configure everything up front. Each feature has a recognizable trigger,
and most teams add them in roughly this order"* — and that excess **costs**:
*"Every feature you add consumes some of Claude's context. Too much can fill up
your context window, but it can also add noise that makes Claude less effective;
skills may not trigger correctly, or Claude may lose track of your conventions"*.
Installing everything at once is the anti-pattern; the roadmap **staggers** the
adoption in the order each piece **unlocks** the next and by the trigger the repo
**actually shows**.

## Base-order (the CANONICAL adoption sequence)

> **Unique home of the adoption sequence.** This "Base-order" is the **single
> source** of the order in which the method is adopted. Step 4 of the parent
> SKILL.md and the *greenfield* profile of
> [`repo-profiles.md`](../../../references/repo-profiles.md) **point here** instead
> of re-writing the sequence — so it does not drift. Whoever reorders a layer
> edits **here**.

Anchored on the *"Build your setup over time"* table (trigger → what to add) +
the principle *"start with CLAUDE.md… then add other extensions as specific
triggers come up"*. The **layers** (each unlocks the next):

1. **Foundation — map + boundaries (dim 1, 12; then 2).** CLAUDE.md is what Claude
   sees in every session (*"persistent context loaded every conversation"*) and
   the boundary doctrine is what prevents duplication in the other artifacts.
   Install **first** the lean map/CLAUDE.md + boundary doctrine + standards
   layer (`standards/`) — *trigger from the docs: "Claude gets a convention
   or command wrong twice → add it to CLAUDE.md"*. **Prerequisite for almost
   everything:** skills, hooks, and sub-agents will hang from this skeleton.
2. **On-demand knowledge — skills (dim 6, 7).** When there is a playbook/reference
   that repeats (*"You paste the same playbook… for the third time → capture it
   as a skill"*), and **after** the foundation exists (the skill references the
   boundaries/standards). Sub-agent enters when *"a side task floods your
   conversation with output you won't reference again → route it through a
   subagent"*.
3. **External connections — MCP (dim 15).** Only when there is data/systems outside
   the repo (*"You keep copying data from a browser tab Claude can't see → connect
   that system as an MCP server"*). Without an external service, **do not** install:
   it would be noise.
4. **Automation — hooks (dim 8, 14).** **Last** among the structural layers
   (*"You want something to happen every time without asking → write a hook"*):
   automatic freshness (Stop), compact-survival (SessionStart), audit-trail
   (ConfigChange), docs coverage (PostToolUse), generated-artifact enforcement
   (PreToolUse). Hooks **wired** on an already-stable skeleton have value; wired
   on emptiness only generate noise. **Prerequisite:** the foundation (1) must
   exist, otherwise the hook has nothing to anchor to.
5. **Distribution — plugin (at scale).** When *"a second repository needs the same
   setup → package it as a plugin"* (monorepo/org). This is the **last** stage:
   packaging what has already proven value in one repo.

> **The order is by PREREQUISITE, not by absolute importance.** Hooks come last
> not because they are less valuable, but because they depend on a stable
> foundation to not become noise. An **observed** trigger can move a layer up
> (e.g., a repo full of generated artifacts → the PreToolUse enforcement moves up,
> even being "a hook").

## Procedure

1. **Read the inputs (read-only).** If a fresh scorecard is in context, use it.
   Otherwise, derive the minimum: the CLAUDE.md(s), the layers (`standards/`/
   vision/backlog/decisions/catalog), the `.claude/` inventory, and the
   **profile signals** (Step 1 of the method +
   [`repo-profiles.md`](../../../references/repo-profiles.md)). The adaptive
   globs/greps live in `references/detection-and-smells.md` of the parent skill.

2. **Match the repo with 0-N profiles** (from `repo-profiles.md`, **free examples,
   not an enum**). Emphases **add up**. **Greenfield/repo from scratch** (no
   `.claude/`, scorecard almost all Absent) is the case where the SEQUENCE matters
   **most** — *"start with CLAUDE.md… then add other extensions as triggers come
   up"*: the foundation (layer 1) unlocks everything, hooks come **later**.

3. **Score each gap on three axes** (not by impression):
   - **Leverage** = how much the gap, when resolved, **unlocks or multiplies** the
     others (map/boundaries leverage all skills/hooks; a niche hook leverages
     little) **and** the **profile weight** (the trigger the repo actually shows
     weighs more — `file:line` from Step 1).
   - **Cost** = context/effort to install and maintain (CLAUDE.md always loaded
     costs per request; hook costs zero until it returns output; skill costs the
     description).
   - **Prerequisite** = what must exist **before** (the Base-order above):
     CLAUDE.md/dim 1 before hooks; boundaries (dim 12) before skills that cite
     them; the **observed trigger** before the payload that serves it.

4. **Sequence in waves (Now / Later / When-the-trigger-appears).** Order by
   **prerequisite first**, then **leverage ÷ cost**. Each item carries: **the
   package payload** that serves it (from `references/installation.md`), **the
   dimension**, and the **observed trigger** that justifies it (`file:line`/fact).
   An item **without an observed trigger** goes to *When-the-trigger-appears*
   (not *Now*) — do not install anticipating noise.

5. **Mark prerequisites as edges.** Wave 2 declares what from Wave 1 must be done
   (e.g., "wire the Stop hook **after** the CLAUDE.md/map is in place"). The
   roadmap is an **installation DAG**, not a flat list.

6. **Do NOT decide content or install.** Each wave is a **proposal**: the actual
   installation follows Steps 5-7 of the method, item by item with OK. Dimensions
   3/10/12 (vision/memory/boundaries) enter the roadmap only as *"propose the
   home"* (Step 6) — never *what to write*.

## Return format (sequenced roadmap, short — the fork condenses)

- **Shape + profile:** 1-2 lines (layers/language/taxonomy + the 0-N profiles
  that matched, each with the observed signal).
- **Roadmap in waves** — each item: `order · dimension · package payload ·
  observed trigger (file:line) · prerequisite`:
  - **Now (foundation that unlocks):** the minimum that makes the rest cheap —
    generally dim 1 (map/CLAUDE.md) + dim 12 (boundaries) + dim 2 (standards),
    in that order.
  - **Later (when the foundation settles):** skills/sub-agents for what repeats;
    MCP if there is an external system; freshness/enforcement hooks **wired** on
    the base.
  - **When the trigger appears:** what does **not** have a trigger today (plugin
    if a 2nd repo appears; MCP if external data appears; niche hook) — installing
    before would be noise.
- **Prerequisite edges:** the dependencies between waves (X before Y).
- **Outside the roadmap (Step 6 only):** dim 3/10/12 as "propose the home",
  never the content.

Do not dump the raw scan into the parent context — only the roadmap + the edges
that support the order (dim 7 return contract).

## Guardrails

- **Proposes the ORDER, never the CONTENT.** Sequences *which method
  artifacts/triggers* to install first; never *what* VISION/memory/boundary
  should say.
- **Read-only.** Does not install, does not edit `.claude/`/`docs/` of the target,
  does not write memory — installation is Steps 5-7, with OK.
- **Every order anchored on an observed trigger** (`file:line`/fact from Step 1) —
  never on curator preference. No trigger → *When-the-trigger-appears*, not *Now*.
- **Profiles are free examples, not a gate:** match with several/none; emphases
  add up and reorder, never hide a dimension from the scorecard.
- **Do not install in advance** — *"too much… adds noise that makes Claude less
  effective"*. Hook/MCP/sub-agent without a trigger goes to
  *When-the-trigger-appears*.
