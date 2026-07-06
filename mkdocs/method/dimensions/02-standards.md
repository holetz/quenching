# Dimension 2 · Standards

The standards layer is the **current, versioned source of truth** — how the system
should be built and why, the contract the whole team and the agent share. Its canonical
home is `docs/standards/`, segmented by subject.

> **Canonical home — `docs/standards/` · Fixed (canonical).** Variant names like
> `docs/arquitetura/` or loose markdown at the `docs/` root are migration candidates; the
> repo converges to the canonical tree with your OK. See
> [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

An agent is only as reliable as the written record it can reconstruct behavior from. The
test that matters is the **rebuild test**: could a fresh agent reproduce the intended
behavior *from the doc alone*, without asking a human? That only works if a standard
carries both the **requirement** (what applies) and the **decision** (why, and the
alternatives) — a requirements-only doc regenerates different behavior every time.

This is why the layer is **docs-as-code**: versioned, reviewed, and treated as part of the
system, not a wiki off to the side
([Docs as Code](https://www.writethedocs.org/guide/docs-as-code/)). And it is why the
method enforces a **canonical taxonomy** of homes. The Diátaxis and Divio frameworks show
that documentation fails when distinct purposes — reference, explanation, how-to,
direction — share a home; separating them by function is what keeps each fact findable
([Diátaxis](https://diataxis.fr/),
[The Divio Documentation System](https://docs.divio.com/documentation-system/)). The
method's twist: the *home* is chosen by **subject** (every repo gets the same tree of the
same names), and the *content inside* follows Diátaxis. Convergence beats per-repo
invention — someone moving between repos sees a literally identical tree instead of
re-mapping it each time.

## What "good" looks like

- Subfolders by subject; an `INDEX.md` **in sync** with what exists on disk (it is a
  *derived* artifact, regenerated between markers, not hand-written).
- **Full mandatory OKF frontmatter** on every standard — `title` / `summary` /
  `audience` / `authority` / `source` / `maintainer` / `updated` **and** the OKF pair
  `type: standard` / `resource:` (the repo scope it governs, derived from the doc's
  `file:line` anchors); one standard per file; English kebab-case names.
- The standards home is a **conformant OKF bundle**: identity is the file path,
  `INDEX.md` plays the OKF `index.md` role, and a root `log.md` records the bundle's
  change history (date-grouped, newest-first).
- Each subject is **broken out one concept per file** by considering a **candidate
  sub-standards catalog** (a *consideration* checklist, not a blind generate list) — a
  subject is "done" only when every candidate is generated *or* explicitly deferred,
  never a monolith bundling many.
- A current standard is **de-facto proven**, anchored in `file:line`; an external best
  practice the repo does not yet follow is a *proposal* (`authority: background`), never
  stated as current.
- Binaries (slides, PDFs) reached through a `.md` sidecar — the agent reads the extract,
  never the binary.

## How it drifts

- **The index lies** — cites a doc that doesn't exist, or omits a new one.
- **Variant / two-homes** — `docs/arquitetura/` instead of `standards/`, or both coexisting.
- **No canonical segmentation** — loose technical markdown at the `docs/` root.
- **Mixed quadrants** — direction or an open decision living inside a standard.
- **Monolith / silent partial coverage** — one doc bundling many distinct standards
  (imports + lint + logging…), or a practised convention neither broken out nor deferred.
- **Mandatory-incomplete / OKF-non-conformant** — a standard missing a mandatory key, or
  missing `type:` / `resource:`.
- **Stated as current without a `file:line` anchor** — a best practice promoted to contract
  without proof the repo follows it.

## How the method closes the gap

It maps each section to its canonical home, proposes the variant migration (with OK),
installs only the homes that apply, and regenerates `INDEX.md` from disk. Each writer stamps
the **full mandatory OKF frontmatter** and evaluates its subject's **candidate sub-standards**
— generating each applicable one as its own file, recording the rest as deferrals in the
subject README ledger. The payload is the `quenching-docs` and `quenching-standards` skills
(the latter fans out one `quenching-writer` per subject) plus the `docs/` scaffold — see
[Bundled artifacts](../../plugin/artifacts.md).
The full canonical tree is the shipped
[`docs-taxonomy.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/docs-taxonomy.md).

## Sources

- [Diátaxis — A systematic framework for technical documentation](https://diataxis.fr/) — accessed 2026-06-28
- [The Divio Documentation System](https://docs.divio.com/documentation-system/) — accessed 2026-06-28
- [Docs as Code — Write the Docs](https://www.writethedocs.org/guide/docs-as-code/) — accessed 2026-06-28
- [Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic · accessed 2026-06-28
