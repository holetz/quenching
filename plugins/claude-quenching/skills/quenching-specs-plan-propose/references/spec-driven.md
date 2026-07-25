# Spec-driven facts — layout, plan artifact graph, the `specs.py` tool

The shared factual reference for the eleven `quenching-specs-*` skills. **This file is the single
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
    .specs.json          # plan metadata (schema, name, title, created, backlogTask)
    proposal.md          # what & why (+ the ## Impact scope)
    design.md            # how — OPTIONAL, delete if the plan needs none
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
proposal ──▶ design (optional) ──▶ tasks     applyRequires: [tasks]
```

- `proposal.md` — required, no dependencies.
- `design.md` — **optional**; depends on `proposal`. Absent is a valid state.
- `tasks.md` — required; depends on `proposal`. `applyRequires: [tasks]` gates implementation.

`specs.py status --plan <n> --json` reports each artifact's `state` (`done` / `ready` /
`blocked`), the task progress, `applyReady`, and the resolved file paths — **use these, never
assume paths**. `specs.py next --plan <n>` collapses the graph to the single next action, so a
skill never infers state from prose.

## Artifact formats

- **`proposal.md`** — `## Why`, `## What Changes`, `## Impact`. `## Impact` is **declared scope
  for human review**: the `docs/` paths the plan intends to create or change and any product
  code it touches. **Prose, not a machine contract** — nothing parses it.
- **`design.md`** — `## Context`, `## Decisions`, `## Risks`. Optional.
- **`tasks.md`** — checkboxes `- [ ] <id> <text>` grouped under `## N. <Section>` headings.
  `specs.py task --plan <n> --check <id>` flips a box mechanically (no string surgery); the
  standards docs a plan writes appear here as checklist items.

Templates live in `assets/specs/templates/{proposal,design,tasks}.md` and are stamped by
`specs.py new`. There is **no `spec.md` template and no delta format** — those are gone.

## The `specs.py` tool surface

Uniform contract: `--json` on every subcommand; strict exit codes — **0** ok · **1** findings ·
**2** refusal. A skill branches on the exit code and the JSON, never on prose.

| Command | Use |
| --- | --- |
| `specs.py new <name> [--title T] [--backlog-task SLUG]` | scaffold a plan folder + filled templates + `.specs.json` |
| `specs.py list [--json]` | active plans, task progress, `lastModified` |
| `specs.py status --plan <n> [--json]` | the artifact graph — `done`/`ready`/`blocked`, `applyReady`, resolved paths |
| `specs.py next --plan <n> [--json]` | THE single next action (write X · implement task Y · ready to archive) |
| `specs.py task --plan <n> --check ID \| --uncheck ID` | flip a `tasks.md` checkbox mechanically |
| `specs.py backlog reindex` | regenerate the `backlog/index.md` GENERATED zone from frontmatter |
| `specs.py validate [--plan <n>]` | required artifacts present, `tasks.md` parseable, kebab-case names |
| `specs.py archive <n> [--dry-run] [--force]` | move to `specs/archive/YYYY-MM-DD-<n>/`; **exit 2** on open tasks without `--force` |
| `specs.py doctor` | workspace shape; remedies **declared** for the skill to apply |

There is no `init` (scaffold is an asset copy — the skill's job), no `store`, no `profiles`,
no telemetry, and no delta parser.

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
