---
title: <short title of the standard>
summary: <one sentence — WHAT this standard covers; the "Covers" cell the derived INDEX renders>
audience: both          # both (human+LLM) | agent (LLM-first/normative) — standards are an agent-facing surface; enum values CANONICAL English, never localized
authority: current      # current (de-facto proven contract, edit only via owning skill) | background (proposal/gap, not yet followed) — enum values CANONICAL English, never localized
source: <author/origin>  # who produced it — person, team, external standard
maintainer: <owner>      # who keeps this standard alive (may = source)
updated: <YYYY-MM-DD>    # exact date of last revision (provenance; "drifted" if very old vs. what it describes)
type: standard           # OKF concept type — non-empty on every standard (subject is carried by the path = OKF identity)
resource: <repo scope this standard governs — path / glob / FQN of the code it describes, derived from the doc's file:line anchors>
---

<standard body.>

# NOTE (knowledge-management method template — do not copy this note into the doc):
#
# This is the MANDATORY frontmatter for a `docs/standards/**` doc — every field
# above is required (unlike the generic `docs-front.md`, where the OKF pair and the
# provenance keys are only recommended). The standards home is a **conformant OKF
# bundle** (additive), so it carries the OKF pair on TOP of the method's labels:
#
#  • type — the OKF concept type. `standard` on every doc; non-empty always. It is a
#    routing/filtering string, not a controlled OKF vocabulary. The **subject** is not
#    in `type` — it is carried by the file PATH (`code/imports.md`), which is the OKF
#    concept identity.
#  • resource — the OKF field for "the underlying asset the concept describes": here,
#    the **repo scope the standard governs** — a path, glob, or FQN (e.g. `src/`,
#    `**/*.py`, `pyproject.toml`, a module FQN). **Derived from the doc's `file:line`
#    anchors, never invented.** An empty or self-pointing `resource` is conformance
#    theater (disallowed) — a standard that governs nothing is not a standard. Each
#    sub-standard governs one concrete scope, so `resource` is naturally derivable.
#  • title/summary/audience/authority/source/maintainer/updated — same meaning as the
#    generic `docs-front.md`, here ALL mandatory. `summary` is the deterministic
#    source the derived `INDEX.md` renders in its "Covers" column.
#
# MERGE, NEVER CLOBBER. Stamping this header onto a doc that already has frontmatter
# fills a MISSING mandatory key without overwriting a filled one; a legacy `status:`
# and keys other tools own (OKF consumers, AGENTS.md tooling, site generators)
# survive as extra keys. `authority:` (current × background) — NOT `status:` — is the
# method's authority axis; enum values stay canonical English (`authority: current`,
# never `vigente`).
#
# Bundle-level OKF constructs at the standards ROOT (not per doc):
#  • INDEX.md — plays the OKF `index.md` role (the bundle's index / front-door;
#    DERIVED from disk between the BEGIN/END GENERATED markers).
#  • log.md — the OKF change log: date-grouped entries, NEWEST FIRST, recording the
#    bundle's history. Optional in OKF; the method establishes/appends it as the
#    standards layer is built.
