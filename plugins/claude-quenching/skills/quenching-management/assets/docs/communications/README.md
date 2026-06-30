---
title: communications/ — directed communication (outbound)
audience: human
authority: background
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `communications/` — directed communication

**Announcements to an audience**: *outbound* messages directed at an audience
(business, team, stakeholders) — incident, change, deploy, downtime/maintenance,
migration, news, status update. They are **scannable** (the reader decides in
seconds whether it matters), **dated**, and **archivable**.

Boundary: `communications/` = "**messages we send to an audience**"
(transient, dated) — distinct from `guides/` (how-to: "how do I do X"), from
`decisions/` (ADR: "why we decided"), from `standards/` (current contract), and
from `presentations/` (visual **binary** deliverable, read via sidecar —
a communication is **text**, read directly). A communication that becomes a
permanent rule **distills into `standards/`**; the communication itself stays in
`archive/` as a historical record.

## Scannable header (invariant)

Every communication opens with a **fixed header** of high-signal fields, followed by
a **summary (one sentence)** + short description. The reader decides **by reading
only the header** whether to continue:

- **Scope** — the affected area/system (`<scope>`).
- **Status** — `<open | in progress | resolved | monitoring | informational>`.
- **Impact** — `<high | medium | low>`.
- **Audience** — who is affected (areas/squads/systems).
- **Active period** — when it started / when it ends (if resolved).
- **Action required** — `<yes — what | no — informational only>`.
- **Last updated** — `<YYYY-MM-DD — author>`.

## Structure × content

The skeleton ships the **structure** — the home, one **template per channel**, and the
header form. **Which** communications exist and **with what values** is this repo's
decision (the skeleton does not ship any ready-made communication).

## Subfolders

| Subfolder | What lives there |
| --- | --- |
| [templates/](templates/README.md) | one **template per channel** (email/chat/wiki/markdown) — fill in per communication |
| [archive/](archive/README.md) | **concrete communications already issued**, dated — the repo creates these |

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`. Generating a communication from these
> templates is the job of the `<prefix>-announcement` skill._
