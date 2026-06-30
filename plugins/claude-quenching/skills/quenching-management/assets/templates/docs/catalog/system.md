---
title: <system alias> — access card
audience: both
authority: current
type: <postgres | sqlserver | databricks-uc | bigquery | ...>
source: <where metadata comes from — UC, origin dictionary, curation>
maintainer: <team/person owning the access>
updated: <YYYY-MM-DD>
---

# `<system alias>` — `<type>`

> **SYSTEM mold** (becomes `<system>/README.md`). Entry point: the LLM reads
> **this card** before touching any table in this system — how to connect,
> where the scripts are, and what catalog granularity exists.

## Access

- **Type:** `<postgres | sqlserver | databricks-uc | bigquery>`
- **Endpoint:** `<host:port>` · **catalog/database:** `<name>`
- **Mechanism:** `<JDBC | SQL warehouse | Spark Connect | native client>` —
  `<connection string/template, WITHOUT secrets>`
- **Credential:** reference to `<secret scope / vault / env var>` — **never** paste
  the password/token here.
- **Network:** `<requires VPN? whitelisted IP? maintenance window? notes>`

## Build scripts

- **Where they live:** `<repo/folder>` — scripts that build/transform the tables
  in this system.
- **How a table points to its script:** `<convention — e.g.: the table page links
  the path in the "Build" section>`.
- **Related pipelines/jobs:** `<DAGs, jobs, schedules that touch this system>`.

## This system's catalog

- **Available granularity:** `<detailed (column descriptions available) | consolidated
  (no descriptions)>` — decides whether tables become detailed pages or stay in the
  consolidated index.
- **Catalogs/databases:** `<list>` → each has its `<schema>.md` (consolidated)
  and/or `<schema>/<table>.md` (detailed).

## Where to find more

- `<links — standards/data-modeling, origin dictionary, access runbook, system owner>`.
