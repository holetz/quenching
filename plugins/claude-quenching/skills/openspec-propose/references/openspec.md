# OpenSpec facts — layout, artifact graph, formats, CLI surface

The shared factual reference for the six `openspec-*` skills. **This file is the single owner
of the OpenSpec facts** — the `openspec/` layout, the spec-driven artifact graph, the spec and
delta formats, the CLI surface, store selection, and `config.yaml` — and every `openspec-*`
skill cites these sections instead of restating them. The OKF bridge (what durable knowledge
crosses from a change into `docs/` and how) lives with `openspec-archive-change`
([../../openspec-archive-change/references/distill.md](../../openspec-archive-change/references/distill.md)).

Everything here describes **OpenSpec 1.6.0** (`@fission-ai/openspec` on npm, Node ≥ 20.19.0;
upstream: [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)). The skills are
CLI-driven on purpose: they ask the CLI for state (`--json`) and instructions instead of
assuming paths or schemas, so they survive upstream upgrades and custom schemas unchanged.

## The `openspec/` layout

`openspec init` scaffolds, at the target repo's root (never inside `docs/`):

```
openspec/
  config.yaml            # schema selection + optional project context and per-artifact rules
  specs/                 # MAIN SPECS — source of truth for CURRENT behavior, by capability
    <capability>/spec.md
  changes/               # active changes, one folder per change
    <change-name>/
      .openspec.yaml     # change metadata (schema, created) — moves with the change
      proposal.md        # what & why
      design.md          # how
      specs/<capability>/spec.md   # DELTA specs — what this change ADDs/MODIFIes/REMOVEs
      tasks.md           # implementation checklist (- [ ] / - [x])
    archive/             # completed changes, moved here as YYYY-MM-DD-<change-name>/
```

`openspec-backlog` adds a sibling `openspec/backlog/` (the **task inbox** — one `type: task`
file per parked task). It is **quenching-managed**: the OpenSpec CLI (`init`, `status`,
`validate`, `doctor`) neither creates nor reads it and ignores unrecognized subfolders under
`openspec/`. It is **not** part of the OKF `docs/` bundle, so `okf-validate.py` does not scan it.

Two spec stores, one truth rule: `openspec/specs/` holds the **current** behavior of each
capability (updated only by syncing a delta); `openspec/changes/<name>/specs/` holds the
**proposed delta**. Never edit main specs directly to plan a change — plan in the delta,
sync on completion.

## The spec-driven artifact graph

The default schema (`schema: spec-driven` in `config.yaml`) builds artifacts in dependency
order; `openspec status --change "<name>" --json` reports the live graph:

```
proposal ──▶ specs (deltas) ──▶ design ──▶ tasks
```

- `applyRequires` — the artifact IDs that must be `done` before implementation (typically
  `["tasks"]`).
- `artifacts[]` — each with `status` (`done` / `ready` / `blocked`) and its dependencies.
- `planningHome`, `changeRoot`, `artifactPaths`, `actionContext` — resolved paths and scope.
  **Always use these instead of assuming repo-local paths.** `artifactPaths.<id>.existingOutputPaths`
  lists the concrete files on disk (glob-expanded); `resolvedOutputPath` may still be a glob
  pattern for glob artifacts — never write to it directly.

Custom schemas swap the graph; the skills must not branch on hardcoded artifact names.

## Spec format (main specs and deltas)

A capability spec is requirements + scenarios:

```markdown
## Requirements

### Requirement: <name>
The system SHALL <behavior>.

#### Scenario: <case>
- **WHEN** <condition>
- **THEN** <outcome>
```

A **delta spec** (inside a change) declares intent against the main spec with four section
kinds — `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`,
`## RENAMED Requirements` (`- FROM:`/`- TO:` lines). A delta is *intent, not wholesale
replacement*: a MODIFIED block may carry only the new scenario, and syncing preserves
everything the delta does not mention.

## CLI surface

| Command | Use |
| --- | --- |
| `openspec new change "<name>"` | scaffold a change (kebab-case name) in the resolved planning home |
| `openspec status --change "<name>" --json` | artifact graph, statuses, resolved paths |
| `openspec instructions <artifact-id> --change "<name>" --json` | `context`, `rules`, `template`, `instruction`, `resolvedOutputPath`, `dependencies` for authoring one artifact |
| `openspec instructions apply --change "<name>" --json` | `contextFiles`, task progress, dynamic instruction, `state` (`blocked` / `all_done` / ready) |
| `openspec list --json` | active changes with schema, status, `lastModified` |
| `openspec show` / `validate` / `archive` / `doctor` / `context` | inspection and maintenance |
| `openspec store list --json` | registered standalone stores (see below) |

In `instructions` output, `context` and `rules` are **constraints for the authoring agent,
never content for the file** — do not copy `<context>`/`<rules>`/`<project_context>` blocks
into any artifact.

## Store selection

If the user names a store (a store is a standalone OpenSpec repo registered on this machine)
or the work lives in one, run `openspec store list --json` to discover registered store ids,
then pass `--store <id>` on the commands that read or write specs and changes (`new change`,
`status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`). Other
commands do not take the flag. Hints printed by commands already carry the flag; keep it on
follow-ups. Without a store, commands act on the nearest local `openspec/` root.

## `config.yaml`

- `schema:` — the workflow schema (default `spec-driven`).
- `context:` (optional) — project background shown to the agent when creating artifacts
  (tech stack, conventions, domain).
- `rules:` (optional) — extra per-artifact rules (`proposal:`, `tasks:`, …).

In a repo carrying an OKF bundle, keep `context:` a **thin pointer** to `docs/` (e.g. "read
docs/standards/ and knowledge/glossary.md first") rather than restating the bundle — the
same move-don't-copy doctrine `quenching-harness` applies to `CLAUDE.md`.

## Boundary: `openspec/` vs the OKF `docs/` bundle

These stores answer different questions and **must not duplicate content**:

- `openspec/specs/` — **what the product currently does**, capability by capability
  (Requirement/Scenario). Owned by the OpenSpec cycle; updated only via delta sync.
- `openspec/backlog/` — the **task inbox** that **seeds** changes: a quenching-managed peer of
  `specs/` and `changes/` (see the task lifecycle in the backlog mold and `backlog/index.md`),
  owned by `openspec-backlog`/`openspec-backlog-triage`, outside the OKF `docs/` bundle.
- `docs/standards/` — **how WE build** (binding contracts: naming, architecture, code);
  `docs/knowledge/` — generic understanding. A decision's rationale + considered alternatives
  live in a change's `design.md` while it is active and distill to a `standard`
  (`authority`-graded) at archive time — there is no separate ADR home.

A behavior statement belongs in a spec; a build-rule belongs in `standards/`; what a change
*taught us* crosses to `docs/` only through the archive-time distillation
([distill.md](../../openspec-archive-change/references/distill.md)) — never by bulk copy.
