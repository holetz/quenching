---
name: quenching-docs
description: >-
  Creates and edits the versioned knowledge documentation of a repo — current
  normative reference (architecture/standards), backlog, ADRs, direction, and
  domain doctrine — keeping each artifact in a single Diátaxis quadrant and
  synchronizing the index and pointers. Use when the user asks to "document a
  standard/convention", "create/edit an architecture doc", "update the index",
  "add a backlog item", "remove a completed backlog item", "write an ADR",
  "distill an implemented ADR", "record a domain decision", or when the index
  is lying / a current standard is in the wrong place.
when_to_use: >-
  authoring/editing versioned docs (current architecture, backlog, ADR, direction,
  domain) with index synchronization and quadrant boundary.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Knowledge documentation — docs-as-code

> Skill-template of the `quenching-management` method. Generic and portable:
> fix the real paths of the layers (normative reference, backlog, ADR, direction)
> as derived in the repo where it is installed — the names below are examples.

## One purpose per artifact (Diátaxis quadrant)

Each doc serves **one** type; "if it serves two purposes, it has two homes":

- **Normative reference** (architecture/standards) = *current reference* — "how it
  is today", versioned. One standard per file; frontmatter (`title`/`updated`/
  `status: current`); kebab-case without accents. **Index in sync** (lists exactly
  the files that exist).
- **Direction (VISION)** = *explanation of direction* — "where it is going",
  **without deadline/milestone/order**; explicit non-goals.
- **Backlog** = *how-to of pending work* — trackable items; completed item **leaves
  the tree** (history stays in git); reference to direction in frontmatter.
- **ADR** = *explanation of an open decision* — weighed alternatives; when
  implemented, **distill to the normative reference and leave** the tree (ledger of
  "Distilled" items is preserved).
- **Domain** — doctrine of how skills/agents consume the domain.

## Procedure

1. **Identify the quadrant** of what is being written; choose the canonical home.
   Content that migrated quadrant (rationale in the map, direction in the normative
   reference, task list in VISION) goes back to the right home, leaving **only a
   link** in the others.
2. **Write** with minimal frontmatter and one standard/decision/item per file.
3. **Synchronize the index and pointers** whenever creating/moving/removing —
   a lying index is Drifted (misleads the agent).
4. **Do not duplicate** (semantic DRY): the same rule does not live in two places;
   CLAUDE.md **cites** it with short-directive + link, does not copy it.
5. **Do not edit generated artifacts** (AUTO-GENERATED catalog, manifests) —
   respect the "X defines Y" rule of the repo; curation goes in a separate
   versioned area.

The doc molds (ADR/backlog/page frontmatter, plus sidecar, catalog, and vision)
live in `assets/templates/docs/` of the method package — this skill applies them.
