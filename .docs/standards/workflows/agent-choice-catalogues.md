---
type: standard
title: Agent-choice catalogues
description: The one shape `subjects`, `tagCatalog` and `workItemTypes` all share — an abstract key mapping to a human-facing description an agent reads to PROPOSE and a human CONFIRMS — why the three converged on it independently, the one invariant that shape enforces on every consumer, and why a fourth catalogue should reuse it rather than invent its own review mechanism
resource: plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/commands/specs/create.md
tags: [workflows, specs, configuration, agent-choice]
timestamp: 2026-08-11
audience: both
authority: current
source: suportar-tipo-workitem-azure-por-tags plan (task 6.3) — distilled once `workItemTypes` made a third independently-arrived-at instance of the shape `subjects` and `tagCatalog` already had; the pattern was proven live (task 4.3) against a real Azure Boards project before this standard named it
maintainer: quenching
---

# Agent-choice catalogues

Three keys in `.claude/quenching.json` — `subjects`, `tagCatalog` and `workItemTypes` — look
unrelated at a glance: one links a spec to a parent Feature, one applies labels, one picks a work
item's type. They converged on the same shape anyway, and this standard names that shape once
rather than leaving it to be re-derived by whoever reads the third.

## The shape

```json
{
  "<abstract-key>": {
    "description": "<prose an AGENT reads to decide>",
    "...": "<zero or more fields the catalogue itself needs>"
  }
}
```

Every instance is a map from an **abstract key** — a short, stable name a human never has to
retype after choosing it once — to an object carrying at least a **`description`**, prose written
for a reader that is not human: `/quenching:specs:create` reads it to judge which entry the input best fits,
proposes a candidate, and a human confirms with one `AskUserQuestion`. `tagCatalog`'s shape is the
degenerate case — the object collapses to a bare string, because a tag needs nothing beyond its
own description — and it is still the same shape: a key, and prose an agent reads.

| Catalogue | Key names | Extra fields beside `description` | Read by |
| --- | --- | --- | --- |
| `subjects` | a project area (`framework`, `gold`) | `name`, `parent`, `tags` | `/quenching:specs:create`'s subject proposal, every backend's `create_spec` |
| `tagCatalog` | the tag itself | none — the value IS the description | `/quenching:specs:create`'s tag proposal |
| `workItemTypes` | a nature of work (`incidente`, `tarefa`) | `azure`, `github`, `default` | `/quenching:specs:create`'s type proposal, `cq specs new --type`, every backend's `create_spec` |

## Why three arrived at the same answer independently

`subjects` and `tagCatalog` were designed together, for the same command, so their agreement
proves less than it looks. `workItemTypes` did not start from either: it was designed to solve one
narrow problem — a spec's work item type differs by backend and should not force a second
declaration per backend — and the description-an-agent-reads shape fell out of the SAME
constraint that shaped the first two: a human maintains this file, an agent proposes from it, and
the two never see each other's work directly. Once a config value's whole purpose is to be
*chosen from*, rather than merely *applied*, this shape is closer to a physical law than a
convention.

## The one invariant every consumer must keep

**Never silently pick.** `/quenching:specs:create` proposes with `AskUserQuestion`, naming the candidate and
its description, for all three catalogues alike — never a subject, tag or type chosen without the
screen the human reads the reasoning on. A `default`/`defaultSubject` entry existing is not license
to skip the confirmation: `cq specs new` falls back to it on its own once nothing was resolved, but
the choice a human makes when authoring the spec is not the same fact as the fallback a tool
applies when nobody did, and conflating them would remove the one point a human's judgment enters.

This is also why **the description is prompt material, not documentation**
([plugin-configuration.md](plugin-configuration.md) §Three keys are prompt material argues the
review consequence in full): a vague or misleading entry does not fail loudly, it makes the agent
propose the wrong subject, tag or type, confidently, every time `/quenching:specs:create` runs against it.

## A closed set, read but never widened by this plugin

None of the three is ever written by this plugin — `.claude/quenching.json` belongs to the target
repository, and whoever maintains it there is who decides what an entry means. `subjects` and
`tagCatalog` are consulted as a **closed set**: a tag outside the declared catalogue is never
proposed, and an unresolved subject key refuses rather than inventing one. `workItemTypes` follows
the same closure at the CLI boundary — `cq specs new --type <key>` refuses (`sp-type-unknown`) for
a key the catalogue does not have — but is deliberately **not** closed at the resolution boundary
inside a backend: `resolve_work_item_type` falls through an unresolved or untranslated entry to
`AZ_SPEC_TYPE`, a floor the other two have no equivalent for, because only `azure-boards`'s create
REQUIRES an answer and has nowhere else to fall.

## A fourth catalogue

A future key that maps an abstract choice to a description an agent proposes from should reuse
this shape rather than invent a fourth review mechanism: one abstract key, a `description` an
agent reads, an `AskUserQuestion` confirmation, and a closed set at whichever boundary that
catalogue's own consumer needs one. What varies is only the extra fields the catalogue's own job
needs beside `description` — never the confirmation contract around it.
