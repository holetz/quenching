---
title: catalog/ — data / domain catalog
audience: both
authority: current
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `catalog/` — data / domain catalog

Navigable map of the **data we touch** — internal and from **external systems**
(PostgreSQL, SQL Server, Databricks/Unity Catalog, BigQuery…). Exists to
**orient an LLM**: understand what each table means, **how to access** the source
system, **which scripts** build it (or relate to it), and **where to find more**
when the catalog is not enough.

Boundary: `catalog/` = "the **data** we produce/consume" — distinct from
`reference/` (facts about external tools/libs/regulations) and from `standards/`
(our code/process contracts). The modeling that underpins the data (grain,
key, joins) lives in `standards/data-modeling/`; table/column naming in
`standards/naming/`.

## Hierarchy: system → catalog → schema → table

The catalog is organized into **four levels**, mirroring how data actually
lives in the systems:

```
catalog/
  <system>/                       # physical origin — README.md = HOW TO ACCESS + where the scripts are
    README.md                     # system card (type, connection, secret, scripts) — mold system.md
    <catalog>/                    # catalog (UC) / database (postgres, sqlserver) / project (bigquery)
      <schema>.md                 # CONSOLIDATED schema index (one line per table) — mold schema.md
      <schema>/
        <table>.md                # DETAILED page (grain, key, columns, scripts) — mold table.md
```

- **system** — the physical origin: `databricks-prod`, `postgres-crm`,
  `sqlserver-core`. The folder name is the stable system alias; the **type** and
  **access** live in its `README.md`.
- **catalog** — the top-level container within the system: *catalog* in Unity
  Catalog, *database* in PostgreSQL/SQL Server, *project* in BigQuery.
- **schema** — the table grouping (schema/owner).
- **table** — the table/view/function.

> The `<system>/<catalog>/<schema>/<table>` segments use the **real names**
> of the systems (do not translate) — only the names of the **canonical homes** in
> `docs/` are English kebab-case.

## Two levels of detail: detailed × consolidated

We do not always have table and column descriptions. The catalog supports **two
granularities** — choose based on available information, **do not force** the
detailed one:

| Mode | Artifact | When to use | What it carries |
|---|---|---|---|
| **Consolidated** | `<schema>.md` (index) | the origin **does not expose** column/table descriptions, or the schema is large and only a map is needed | one line per table: name + FQN + short grain/observation. **No** columns. |
| **Detailed** | `<schema>/<table>.md` | we have descriptions (from UC, origin dictionary, or curation) and the table is actually queried | grain, key, **columns** (type + description), build scripts, related, curated observation. |

Rule: **promote** a table from consolidated to a detailed page when
descriptions appear or when it starts being queried frequently; **do not**
create an empty detailed page just to fill the tree — a columns page without
descriptions is noise, keep it in consolidated.

## System access + where the scripts are

Each `<system>/README.md` (method mold `system.md`) is the **entry point**
of the system and answers:

- **type** — `postgres` | `sqlserver` | `databricks-uc` | `bigquery` | … (defines
  the driver/client).
- **how to access** — host/port/database, mechanism (JDBC, SQL warehouse, Spark
  Connect…) and the **secret reference** (secret scope, vault, env var) —
  **never** the credential itself.
- **scripts** — where the scripts that **build/transform** the tables in this
  system live (repo, folder) and how a table points to its script.
- **available granularity** — do we have column descriptions? (decides detailed ×
  consolidated).
- **owner/contact** and **where to find more**.

In the detailed table page, the **Build** section links the script(s) that
materialize the table and **Related** points to lineage/neighboring scripts — this
is how the LLM jumps from the *data* to the *code that produces it*.

## Generated × curated ("X defines Y" rule)

When an official source describes the tables (Unity Catalog, bundle manifest,
origin dictionary), the content is **AUTO-GENERATED** and **never edited by hand** —
every `<!-- AUTO-GENERATED -->` block is overwritten on the next generation. **Curation**
(grain/usage observation, column descriptions missing from the origin, the system
access card, script links) is **versioned separately** and **survives** regeneration.
Curation written inside the generated block is lost on the next build.

A system **without a generator** (e.g.: a PostgreSQL without a dictionary) has
**fully curated** pages — without the `<!-- AUTO-GENERATED -->` marker, editable
freely.

## Molds

The molds for these pages are **method templates** (applied by the `quenching-docs`
skill), not files in this directory:

| Mold | Becomes | Role |
|---|---|---|
| `system.md` | `<system>/README.md` | system access card + where the scripts are |
| `schema.md` | `<system>/<catalog>/<schema>.md` | consolidated index (one line per table) |
| `table.md` | `<system>/<catalog>/<schema>/<table>.md` | detailed page (grain, key, columns, scripts) |

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
