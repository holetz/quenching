# Spec-driven facts — layout, plan artifact graph, the `specs.py` tool

The shared factual reference for the thirteen `quenching-specs-*` skills. **This file is the single
owner of the spec-driven facts** — the `specs/` layout, the plan artifact graph, the artifact
formats, and the `specs.py` tool surface — and every `quenching-specs-*` skill cites these
sections instead of restating them. The OKF bridge (what durable knowledge crosses from a plan
into `docs/` and how) lives with `quenching-specs-plan-archive`
([../../quenching-specs-plan-archive/references/distill.md](../../quenching-specs-plan-archive/references/distill.md)).

This front is **entirely native** — no external CLI, no Node runtime, no `config.yaml`, no main
spec store, no delta format. A **plan** writes straight into the OKF `docs/` bundle (a decision
into `docs/standards/`, an understanding into `docs/knowledge/`), isolated on a branch while it
is built, and archived when done. The tool that gives the LLM deterministic rails is
`assets/bin/specs.py` — a stdlib-only Python script in the same mold as `okf-validate.py`.

## The `specs/` layout

The front lives at the target repo root (never inside `docs/`):

```
specs/
  <plan-name>/           # an active plan, one folder per plan
    .specs.json          # metadata: schema, name, title, created, backlogTask,
                         #   verification policy, refined record, per-task attempts
    proposal.md          # what & why (+ the ## Impact scope)
    design.md            # how — always present; empty sections answered `- none — <reason>`
    tasks.md             # implementation checklist (- [ ] / - [x])
  archive/               # completed/abandoned plans, moved here as YYYY-MM-DD-<name>/
  backlog/               # the TASK INBOX — one `type: task` file per parked task
    index.md
    <task-slug>.md
```

`backlog/` is a **quenching-managed** sibling of the plan folders and `archive/`. It is **not**
part of the OKF `docs/` bundle, so `okf-validate.py` does not scan it (it is checked with
`--listing-root`; see
[backlog-zone.md](../../quenching-specs-backlog-add/references/backlog-zone.md)).

There is **one truth**, not two: a plan does not edit a separate "main spec" store — it writes
the durable rule directly into `docs/standards/`, honestly `authority`-graded. There is no
delta, because there is no other copy for a delta to bridge to; isolation-while-building is what
a **branch or worktree** provides (offered by `quenching-specs-plan-apply`), with real merge,
history, and reversion — not a markdown reimplementation of one.

## The plan artifact graph

Three artifacts in dependency order (`specs/schema.json`, read by `specs.py status`):

```
proposal ──▶ design ──▶ tasks     applyRequires: [tasks]
```

- `proposal.md` — required, no dependencies.
- `design.md` — **required as a section set, not as a dependency**; depends on `proposal`. The
  file is always present and an empty section is answered `- none — <reason>`; but `applyRequires`
  deliberately excludes it, so a bare scaffold is *reported* (`sp-design-scaffold`, warn), never
  blocking. Promoting it to a dependency would strand every plan authored before the rule.
- `tasks.md` — required; depends on `proposal`. `applyRequires: [tasks]` gates implementation.

**What `applyReady` does and does not guarantee.** It guarantees `proposal.md` and `tasks.md`
exist with real content and at least one parseable checkbox. It does **not** guarantee the plan
was refined, that `design.md` was filled, or that the declared `## Impact` is covered — those are
warnings (`sp-unrefined`, `sp-design-scaffold`, `sp-impact-uncovered`), surfaced by
`specs.py validate` and `/specs:status`, because a sweep never blocks on a judgment call.

`specs.py status --plan <n> --json` reports each artifact's `state` (`done` / `ready` /
`blocked`), the task progress, `applyReady`, and the resolved file paths — **use these, never
assume paths**. `specs.py next --plan <n>` collapses the graph to the single next action, so a
skill never infers state from prose.

## Artifact formats

Every section below is **required-with-explicit-fallback**: the heading always exists, and an
empty one is answered `- none` (`- none — <reason>` in `design.md`). An omission and a null are
different facts, and an absent heading cannot tell them apart.

- **`proposal.md`** — `## Why`, `## What Changes`, `## Out of Scope`, `## Validation`,
  `## Impact`.
- **`design.md`** — `## Context`, `## Decisions`, `## Alternatives Considered`,
  `## Open Decisions`, `## Risks`.
- **`tasks.md`** — checkboxes `- [ ] <id> <text>` grouped under `## N. <Section>` headings.
  `specs.py task --plan <n> --check <id>` flips a box mechanically (no string surgery); the
  standards docs a plan writes appear here as checklist items.

**`## Impact` is the proposal's one parsed contract.** It carries three sub-headings and exactly
one is machine-checked — `### Standards this plan will write into docs/standards/` (a bold line
with the same text is accepted for older plans). `parse_impact_standards()` reads the
`docs/standards/**.md` paths bulleted under it, and `specs.py validate` emits `sp-impact-uncovered`
(warn) for any that no `tasks.md` item names. The sibling sub-headings — a background standard the
plan *may* resolve, the product code it touches — are deliberately **not** parsed, because they
name paths the plan never promised to write. A proposal without the heading declares nothing and
is never flagged; the check is opt-in by writing it. The per-section authoring doctrine lives in
[artifacts.md](artifacts.md).

Templates live in `assets/specs/templates/{proposal,design,tasks}.md` and are stamped by
`specs.py new` — with the same content embedded as fallbacks in `specs.py` itself, so an installed
copy under a target's `.claude/hooks/` with no adjacent assets stamps the identical files. **Edit
both or neither.** There is **no `spec.md` template and no delta format** — those are gone.

## The `specs.py` tool surface

Uniform contract: `--json` on every subcommand; strict exit codes — **0** ok · **1** findings ·
**2** refusal. A skill branches on the exit code and the JSON, never on prose.

| Command | Use |
| --- | --- |
| `specs.py new <name> [--title T] [--backlog-task SLUG] [--verification P]` | scaffold a plan folder + filled templates + `.specs.json` (`P` = `per-task`/`per-section`/`end-of-plan`) |
| `specs.py list [--json]` | active plans, task progress, `lastModified` |
| `specs.py status --plan <n> [--json]` | the artifact graph — `done`/`ready`/`blocked`, `applyReady`, resolved paths, `verification`, `refined`, `tasks.blocked` |
| `specs.py next --plan <n> [--json]` | THE single next action (write X · implement task Y · **blocked** · ready to archive), carrying the task's `verify`/`files`/`pattern`/`parallel` and the plan's policy |
| `specs.py task --plan <n> --check ID \| --uncheck ID` | flip a `tasks.md` checkbox mechanically |
| `specs.py task --plan <n> --attempt ID [--error MSG]` | record a failed attempt against the five-attempt budget |
| `specs.py task --plan <n> --reset-attempts ID` | clear a task's attempt state so `next` offers it again |
| `specs.py parallel --plan <n> [--json]` | verify each `[P]` group's `files:` sets are disjoint — **exit 1** when any group is ineligible |
| `specs.py backlog reindex` | regenerate the `backlog/index.md` GENERATED zone from frontmatter |
| `specs.py validate [--plan <n>]` | required artifacts present, `tasks.md` parseable, kebab-case names, and the four warnings below |
| `specs.py archive <n> [--dry-run] [--force]` | move to `specs/archive/YYYY-MM-DD-<n>/`; **exit 2** on open tasks without `--force` |
| `specs.py doctor` | workspace shape; remedies **declared** for the skill to apply |

There is no `init` (scaffold is an asset copy — the skill's job), no `store`, no `profiles`,
no telemetry, and no delta parser.

`specs.py next` walks `proposal` → `design` → `tasks` → each open task → archive. It names
`design.md` only while it is a bare scaffold **and** `tasks.md` is still unwritten: an absent
`design.md` is a legacy plan and is left alone, and once the checklist exists the plan has moved
past the design phase, so the scaffold becomes a `validate` warning rather than a next action.

### The `sp-*` warnings `validate` adds beyond structure

None of these is an error and none affects `applyReady` — they surface in `/specs:status` so a
human can judge, which is the front's rule for anything that is a judgment call.

| Code | Fires when |
| --- | --- |
| `sp-design-scaffold` | `design.md` exists but is still the shipped scaffold (an ABSENT one is never flagged) |
| `sp-impact-uncovered` | a `docs/standards/**.md` path declared under `## Impact`'s parsed sub-heading that no `tasks.md` item names |
| `sp-unrefined` | a plan with a `tasks.md` and no `refined` record in `.specs.json` (see `quenching-specs-plan-refine`) |
| `sp-empty-proposal` | `proposal.md` is still the unfilled template |

### Resolving the tool

Each `quenching-specs-*` skill resolves the script by the same fallback the backlog zone uses
([backlog-zone.md](../../quenching-specs-backlog-add/references/backlog-zone.md)): the plugin
path `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then a copy installed into the target's
`.claude/hooks/specs.py`, and if neither resolves, the declared manual check — do the same rule
by hand and **say in the report that the check was manual**, never silently skip it. Invoke with
`python3` or `py` (`allowed-tools: Bash(python3:*), Bash(py:*)`).

## Boundary: `specs/` vs the OKF `docs/` bundle

**This section is the single normative owner of the boundary.** Everywhere it comes up —
`quenching-specs-align`'s conformance codes, `distill.md`'s what-crosses table, `homes.md`'s
task-vs-vision tie-breaker, the `QUENCHING.md` operator manuals — cites it.

- `specs/<plan>/` — **the in-flight unit of work**: a plan's why, design, and task checklist
  while it is being built. Owned by the plan skills; leaves the tree at archive time.
- `specs/backlog/` — the **task inbox** that **seeds** plans: a quenching-managed peer of the
  plan folders, owned by `quenching-specs-backlog-add`/`quenching-specs-backlog-triage`, outside
  the OKF `docs/` bundle.
- `docs/standards/` — **how WE build** (binding contracts: naming, architecture, code);
  `docs/knowledge/` — generic understanding. A plan writes its durable rule **directly** into
  `docs/standards/` (`authority`-graded), and the archive-time distillation
  ([distill.md](../../quenching-specs-plan-archive/references/distill.md)) routes any remaining
  by-products (a term, an understanding, a follow-up task) — never by bulk copy.

The plan **is** the change: what it proves out lands in `docs/` as it is built, honestly graded
(`authority: background` for an agreed-but-unproven rule, `current` for one the plan implemented
and proved). There is no second store for it to duplicate.
