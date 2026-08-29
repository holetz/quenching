---
type: external
title: Azure DevOps CLI measured behaviour
description: Measured facts about `az boards` / `az devops` and the Azure Boards work item as a store — the WIQL macro that resolves to an indistinguishable empty answer, the project name the field compares against, the column that rewrites the state, the two ceilings a description travels under, the marker form `System.Description` does not strip, the identity `--assigned-to` accepts, and the one resource with a batch form
resource: plugins/quenching/assets/bin/quenching/specs/**
tags: [azure-devops, azure-boards, cli, wiql, work-item, tooling]
timestamp: 2026-08-11
audience: both
authority: background
source: provar-e-posicionar-o-backend-azure-boards spec §6 — measured against org `unicredbr`, team "Diretoria Risco", with `az` 2.89.0 and the `azure-devops` extension 1.0.6, on Linux
maintainer: quenching
---

# Azure DevOps CLI measured behaviour

Facts about **how `az boards` / `az devops` and an Azure Boards work item actually behave** when a
tool treats the work item as a document store. External tool behaviour, not our contract — the
interface we hold every backend to is
[standards/architecture/spec-backend.md](../../standards/architecture/spec-backend.md), and what a
target repository declares to reach this backend is
[standards/workflows/plugin-configuration.md](../../standards/workflows/plugin-configuration.md).

Everything below was measured against a real project, not read from documentation: `az` 2.89.0 with
the `azure-devops` extension 1.0.6, org `unicredbr`, team "Diretoria Risco", Agile-derived process.
Each row cost a live call, and several contradict what the CLI's own help implies. A version bump
on either component invalidates this page rather than extending it.

## Querying

**`@project` in a WIQL clause resolves to nothing, and says so in a way nothing can read.** A query
carrying `[System.TeamProject] = @project` exits **0** with byte-empty stdout *and* byte-empty
stderr — identical, byte for byte, to a query that legitimately matches zero work items. There is
no signal at the transport layer to tell the two apart, so a refusal keyed on emptiness would
refuse the ordinary "nothing here yet" case exactly as often as the fault. Name the project
literally.

**`[System.TeamProject]` compares against the project's NAME, never its GUID.** A GUID in that
clause answers `sp-az-api-error` ("not found in hierarchy") on every listing — and a human's own
`az devops configure --defaults project=…` legitimately holds either shape, because `--project`
routing accepts both. `az devops project show --project <name-or-guid>` accepts either as input and
always returns the name, which makes it the one call that normalises this.

**A WIQL query returns ids and nothing else.** `System.Description` is never in the answer,
whatever the `SELECT` names — the fields have to be fetched separately.

## Reading in bulk

**`az boards work-item show` has no batch form; the REST resource does.** `az devops invoke --area
wit --resource workitemsbatch --http-method POST --in-file <json>` takes up to **200** ids per call
with an explicit field list, turning a listing of N specs from 1 + N calls into 1 + ⌈N/200⌉. It is
also the only call measured to return `System.Description` for many items at once.

## The column, the state, and the board

**The board column and `System.State` are NOT independent fields.** Writing the Kanban column
silently rewrites `System.State` to whatever the process's `allowedMappings` names for that column
— on this process, the `incoming` column (`Backlog`) only ever resolves to `New`, and the
`outgoing` one (`Concluído`) only ever to `Closed`. Applying a desired state and a desired column as
two writes means the second one undoes the first: the column is what a write actually controls, and
the state is a resolved consequence of it.

**The column field is `WEF_<guid>_Kanban.Column`, and the guid is per TEAM.** It cannot be
constructed — it has to be found. A team has several boards (this one has six: Stories, OKR,
Releases, Funcionalidades, Iniciativas, Épicos), each reachable through `az devops invoke --area
work --resource boards`; the right one is the board whose `allowedMappings` names the work item
type being written, and its `fields.columnField.referenceName` is the field. `User Story` resolves
to the "Stories" board here.

## `System.Description` as a document store

**It strips HTML comments, in every position tried.** `<!-- … -->` does not survive a write, so a
comment is unusable as an invisible marker on this field. A `<div style="display:none">…</div>`
does survive, renders invisibly, and comes back in the raw value — with two cosmetic mutations the
reader has to tolerate: the `style` attribute gains a trailing `;` and the element's text gains a
trailing space.

**Its real ceiling is 1,048,576 characters.** Above it, `az` answers
`TF401262: … exceeds the maximum allowed length of 1048576`. The limit is not published anywhere
`az` prints, and it is far above any document this store realistically holds.

**A literal `--description <text>` argument hits Linux before it hits Azure.** `az` raises `OSError`
building its own argv above roughly 128,000 characters — `MAX_ARG_STRLEN`, a per-argument kernel
limit that has nothing to do with the work item. `--fields System.Description=@<path>` reads the
value from disk instead and has no ceiling of its own, which leaves the 1 MiB above as the only
real one.

**The `@file` mechanism strips every trailing newline, unconditionally and in both directions.**
`"x\n"`, `"x\n\n\n"` and `"x"` all read back as `"x"`, so whether a document ended in a newline
cannot survive the round trip and cannot be preserved by writing more of them.

## Identity and creation

**`--assigned-to` refuses a display name outright** (`is an unknown identity`) and resolves only a
UPN. Reading the field back yields an identity **object**, never a plain string — `displayName` and
`uniqueName` among its keys — and only `uniqueName` is a value that can be written again.

**`az boards work-item create` has no `--state` flag.** Only `update` does. A new item is born in
whatever state its type defaults to (typically `New`).

## Tags

**`System.Tags` is a single `; `-joined string**, read and written as one value — there is no
per-tag operation, so any write of the field is a full replacement of the set.
