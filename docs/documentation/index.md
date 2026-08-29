<div class="q-hero" markdown>
<p class="q-hero__eyebrow">quenching · a Claude Code plugin</p>

# Every repository, the same shape { .q-hero__title }

Point quenching at a repository and its knowledge, its plans and its automation each converge
onto one canonical, verifiable structure — probed first, planned once, changed only on your OK.
{ .q-hero__tag }

[Get started](tutorials/getting-started.md){ .md-button .md-button--primary }
[Understand the model](explanation/operating-model.md){ .md-button }
</div>

In metallurgy, *quenching* is the rapid cooling that fixes a metal's structure and makes it hard.
This plugin does that to a repository: whatever loose shape your knowledge base, your plans and
your `.claude/` automation have today, one pass fixes each of them into a canonical structure —
and keeps it hard against drift, because every front ships a verifier that can prove the shape
before anyone touches a file.

## Choose your path

<div class="grid cards" markdown>

-   :material-rocket: **Get it running**

    ---

    From install to your first verified alignment, in a handful of commands.

    [:octicons-arrow-right-24: Getting started](tutorials/getting-started.md)

-   :material-wrench: **Do a task**

    ---

    Adopt quenching in a repo, drive one spec to merge, publish a docs site.

    [:octicons-arrow-right-24: How-to guides](how-to/index.md)

-   :material-lightbulb: **Understand why**

    ---

    The three fronts, the OKF bundle, and the provider-owned spec lifecycle.

    [:octicons-arrow-right-24: Concepts](explanation/index.md)

-   :material-book-open-variant: **Look it up**

    ---

    All thirty-eight commands, the local automation registry, the glossary.

    [:octicons-arrow-right-24: Reference](reference/index.md)

</div>

## The problem

A repository that grows with AI agents accumulates three kinds of drift at once. Knowledge
scatters across READMEs, wikis and chat threads, so every session re-derives what the last one
already learned. Plans live in prose nobody can verify, so "done" is an opinion. And the
`.claude/` automation surface grows one ad-hoc command at a time, until no two repositories —
and no two commands — look alike.

Each kind of drift makes the next one worse: an agent without durable knowledge writes vaguer
plans, and vaguer plans produce automation nobody dares to reorganize.

## The solution

quenching acts on the three surfaces where that drift lives, with **the same interface on each**:
every front has exactly ONE `align` command that probes first — a clean front costs a couple of
tool calls and stops there — then presents one consolidated plan and waits for one OK before
writing anything.

| Surface | What converges | The one align |
| --- | --- | --- |
| `/docs/` | a canonical **OKF bundle** — standards, concepts, glossary, docs site | `/quenching:knowledge:align` |
| Specs | a provider-owned plan cycle on **GitHub issues or Azure Boards** | cycle and status commands |
| `.claude/` | one file per entry point, every description audited | `/quenching:components:align` |
| *(git)* | nothing — a pillar that answers questions, converges no tree | *(none, by design)* |

One more command, `/quenching:align`, conducts all three fronts in dependency order on a single
OK. Read [the operating model](explanation/operating-model.md) and you know the whole plugin.

## Quick start

```bash
claude --plugin-dir ./plugins/quenching   # load the plugin into Claude Code
cq --version                              # 6.3.0 — the bundled CLI answers
```

Then, inside the session, ask for a read-only status before you change anything:

```text
/quenching:knowledge:status
```

The full path — install, probe, first alignment — is the
[getting-started tutorial](tutorials/getting-started.md).

## TL;DR for agents

!!! abstract "TL;DR for agents"
    - Contract: three fronts (`knowledge`, `specs`, `components`) + a `git` pillar; ONE align
      per front, probe-first; `/quenching:align` conducts all three on one OK.
    - Rails: `cq` CLI — `cq knowledge`, `cq specs`, `cq components`, `cq git`; uniform `--json`;
      exit codes `0` ok · `1` findings · `2` refusal.
    - Invariants: nothing is written before a human OK; blast radius reaching product code
      confirms on its own; a probe that finds nothing ends the run.
    - Canonical anchors: [#the-problem](#the-problem), [#the-solution](#the-solution),
      [#quick-start](#quick-start); command catalog at [reference/commands.md](reference/commands.md).
