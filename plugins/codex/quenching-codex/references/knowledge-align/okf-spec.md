# OKF v0.1 — normative rules (condensed)

The **Open Knowledge Format** models a body of knowledge as a **bundle**: a directory tree
of markdown **concept documents**, plus reserved listing/history files. Source:
`GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md`. This file condenses the normative rules
the plugin enforces; [conformance.md](../../references/knowledge-align/conformance.md) turns them into checks.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## Reserved filenames

- **`index.md`** — a directory **listing** (progressive disclosure). It MUST NOT be used for
  a concept document.
- **`log.md`** — an **update history**. Also reserved. OKF v0.1 keeps it; the OKF-strict
  profile **retires** it (§Reserved filenames) without unreserving it.
- Every **other** `.md` file is a **concept document**.

## Frontmatter

- **Required:** `type` — a short string naming the kind of concept. **Non-empty on every
  concept doc.**
- **Recommended (priority order):** `title` (display name) · `description` (one-sentence
  summary) · `resource` (URI uniquely identifying the underlying asset) · `tags` (YAML list)
  · `timestamp` (ISO 8601 of last change).
- Producers **MAY** add any additional keys (this plugin's `audience`/`authority`/`source`/
  `maintainer`/`source_uri` are such extra keys). `source_uri` is written by `quenching-knowledge-import`
  alone; its contract — the exact-URI value, and why it is separate from
  the authorial prose in `source` — is owned by
  [sources.md](../../references/knowledge-import/sources.md) §Attribution.

## Concept `type`

- Type values are **not** registered centrally. Producers **SHOULD** pick descriptive,
  self-explanatory values; consumers **MUST** tolerate unknown types gracefully.
- This plugin fixes a **descriptive vocabulary** per home (`standard`, `system`, `schema`,
  `table`, `vision`, `documentation`, `concept`, `external`,
  `sidecar`) so the surface is uniform and greppable.

## Normative rules

**MUST**
- Reserved filenames MUST NOT be used for concept documents.
- Every non-reserved `.md` MUST contain **parseable YAML frontmatter**.
- Every frontmatter block MUST contain a **non-empty `type`**.
- Consumers MUST tolerate broken links and unknown types.

**SHOULD**
- Favor **structural markdown** — headings, lists, tables.
- `type` values SHOULD be descriptive and self-explanatory.
- Reserved filenames SHOULD be used where applicable (an `index.md` for a directory listing,
  a `log.md` for history).
- Index entries SHOULD include the linked concept's `description`.
- Citations SHOULD be listed under a `# Citations` heading.

**MAY**
- A bundle MAY declare the OKF version via `okf_version: "0.1"`.
- `index.md` / `log.md` MAY appear at any level; a consumer MAY synthesize `index.md` on the fly.

## Links

Two forms: **absolute (bundle-relative)** beginning with `/` (relative to the bundle root),
and **relative** markdown paths. Links assert a relationship; the specific meaning comes from
the surrounding prose.

## Bundle & conformance

```
bundle/
├── index.md   (optional)
├── log.md     (optional)
├── <concept>.md
└── <subdir>/ …
```

A bundle **conforms** if: (1) every non-reserved `.md` has parseable YAML frontmatter,
(2) every frontmatter has a non-empty `type`, (3) reserved filenames follow their structures.
Consumers SHOULD NOT reject a bundle for missing optional fields, unknown types, unknown
keys, broken links, or a missing `index.md`.

## What this plugin adds on top (OKF-strict profile)

OKF is permissive; this plugin narrows it into a portable **signature** (all still
OKF-valid — additive keys, descriptive types, reserved-file structures):

1. **`index.md` carries no frontmatter** — except the **root** `docs/index.md`, which carries
   **only** `okf_version: "0.1"`.
2. **`type` is mandatory and drawn from the fixed vocabulary** per home (see
   [taxonomy.md](../../references/knowledge-align/taxonomy.md)).
3. **`resource` is derived, never invented** — for standards a comma-separated **glob set** of
   what the doc governs (`*`/`**` only, repo-root-relative); for catalog/reference the asset URI.
   Empty is disallowed, and so is self-pointing (`resource-self`) — except a **bundle-level
   aggregate** whose scope contains the bundle root, which `glossary.md` legitimately
   is. A glob states what the doc governs and is the input the staleness check reads; a
   `file:line` states only where a rule happens to be written today.
4. **`log.md` is retired** — nothing in this plugin creates one, appends to one, or checks
   one. It stays a **reserved** name all the same: a log left over from an earlier alignment
   is still recognized, so it is never read as a malformed concept doc and never blocked.
   Unreserving it is a different and much worse change than retiring it — see
   `docs/standards/architecture/retiring-a-reserved-artifact.md`. Provenance that used to
   land here now lands in the archived spec's `## Outcome`.
5. **Links:** relative within a home, absolute `/docs/...` across homes.
6. **Canonical English structure** — folder names **and concept-doc file slugs**, keys, enum
   values, and the `type` vocabulary. Frontmatter is English; **body prose MAY follow the repo's
   language**. Identifier-derived slugs (catalog tables/schemas, repo names)
   stay **verbatim** — the slug is the greppable key to the asset.
   *(`standards/agents/communication.md` is the owner of that language rule for a bundle that has
   one. Every **normative** statement of it in this plugin was collapsed into a citation; the
   boundary reminders that survive do so by decision, under
   `standards/architecture/plugin-layout.md` §A boundary reminder is not a restatement. This one
   stays self-contained deliberately: a format spec is what other implementers read to build
   against, and one that defers to a doc living inside a particular repo's bundle stops being
   self-describing.)*
7. **Harness files** `AGENTS.md`/`AGENTS.md` are navigation pointers, **not** OKF concepts —
   exempt from the `type` requirement. The validator skips them entirely; the `quenching-components-harness-align`
   skill keeps them thin and honest.
8. **Every knowledge-holding folder has an `index.md`, and listings do not lie.** The validator
   flags (WARN) a folder of concept docs with no `index.md`, a listing link to a nonexistent
   file, and a concept doc nothing links to. Still OKF-valid (these are SHOULDs the plugin
   surfaces; a consumer may ignore them).
