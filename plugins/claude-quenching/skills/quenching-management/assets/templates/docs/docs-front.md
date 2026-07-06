---
title: <short title of the doc>
summary: <one sentence — WHAT this doc covers; the "Covers" cell the derived INDEX renders>
audience: both          # both (human+LLM) | agent (LLM-first/normative) | human (human-only/background) — enum values are CANONICAL English, never localized (cross-repo greppable)
authority: current      # current (source-of-truth/contract, edit only via owning skill) | background (background/historical, human edits freely) — enum values CANONICAL English, never localized
source: <author/origin>  # who produced it — person, team, external standard (e.g.: "Risk Board", "Res. 4.966 BACEN")
maintainer: <owner>      # who keeps this doc alive (may = source)
updated: <YYYY-MM-DD>   # exact date of last revision (provenance; "drifted" if very old vs. what it describes)
---

<doc body.>

# NOTE (knowledge-management method template — do not copy this note into the doc):
#
# This is the minimum AUDIENCE + PROVENANCE header per file in `docs/`.
# It labels EACH doc with two questions that the agent and human ask in
# opposite ways, and the provenance that makes trust verifiable:
#
#  • audience — who this doc speaks to FIRST.
#      both   → human and LLM consume it (the majority of the current technical layer).
#      agent  → LLM-first: contract/standard written for the agent to follow
#               literally (specs, FQNs, generated rules) — the human reads it,
#               but the audience is the agent.
#      human  → human-only / background material: the LLM does NOT ingest the
#               binary/noise (slides, diagrams, PDFs of the human slot); it
#               consumes only the sidecar.
#  • authority — is the doc SOURCE-OF-TRUTH or BACKGROUND?
#      current    → contract/normative: the agent trusts it, and edits go through
#                   the owning skill (`quenching-docs`), never silently by hand.
#      background → background/historical (draft, presentation, old decision): the
#                   human edits freely; the agent does NOT treat it as current truth.
#  • source/maintainer/updated — provenance: where it came from, who maintains it,
#    when. A very old `updated` vs. the described standard = fossil candidate (dim 2).
#  • summary — one sentence: WHAT the doc covers. It is the deterministic source the
#    derived INDEX renders in its "Covers" column (title = short name; summary =
#    the covers-directive). Recommended for any doc that appears in a generated index.
#
#  • contract: title/audience/authority are REQUIRED; summary/source/maintainer/updated
#    are RECOMMENDED (priority order). `authority:` (current × background) — NOT a
#    `status:` (current/draft) — is this method's authority axis; a legacy `status:`
#    is preserved as an extra key, never newly stamped. Stamping this header onto a
#    doc that already has frontmatter MERGES — never drop keys you do not own; a
#    legacy `status:` and fields from other tools (AGENTS.md tooling, OKF consumers,
#    site generators) coexist as extra keys.
#
# Boundary rule: audience+authority tell the agent what to CONSUME as
# truth (agent/current) × what is human BACKGROUND (human/background) — and tell
# the human what can be edited freely (background) × what is a contract (current).
# This is the README-humans × CLAUDE.md/AGENTS.md separation (dim 12) carried down
# to file level. Can live in the FOLDER (one `README`/index labels the entire section)
# instead of repeating in each file, when the section is homogeneous.
