---
title: <extract of a name — e.g.: "Risk Committee Presentation 2026-Q2">
audience: agent          # the sidecar is what the LLM consumes; the binary source is `human`
authority: background    # extract of human material: background, not a current contract
source: <author/origin of the binary — person, team, external standard>
maintainer: <who keeps the binary source alive>
updated: <YYYY-MM-DD>    # date of the binary source (provenance; "drifted" if the extract aged vs. the source)
binary: ./<source-file.pptx|pdf|drawio>   # PATH/URL of the binary source — the agent does NOT need to open it
pages: <N>             # number of pages/slides in the source (signals the avoided cost; see note)
---

# <material title>

> **Sidecar** (textual extract alongside the binary). The LLM reads **this `.md`**,
> not the `binary:` above. The source remains for the human; only the **high-signal
> content** that an agent needs to answer/reason about it lives here.

## Summary (2-5 lines)

<what the material says, in navigable prose — not "this is a slide about X", but the
content: the thesis, the decision, the key number.>

## Key points (bullets)

- <fact/decision/definition extracted, with reference to the source — e.g.: "slide 4: …">
- <…>

## When the agent should open the `binary:` (rare)

<what **only** exists in the source and was not extracted — e.g.: "the full flow
diagram (page 7) was not transcribed; open the binary if you need the arrows".
Generally leave empty: the extract is sufficient.>

# NOTE (knowledge-management method template — do not copy this note into the sidecar):
#
# This is the SIDECAR/EXTRACT standard for human/external material consumed via
# extract: `presentations/` (slides/diagrams/reports) and `reference/regulations/`
# (normative PDFs). Solves "how the LLM consumes slides/diagrams/PDFs without
# ingesting the BINARY".
#
# WHY the binary is expensive noise (official, dated source):
#   • PDF is processed via VISION: "each page of the document into an image"; each
#     page costs 1,500–3,000 TEXT tokens **plus** the IMAGE cost per page. In the
#     official example (Bedrock), full vision mode uses ~7,000 tokens for a 3-page
#     PDF vs. ~1,000 in text-only mode — ~7x.
#     [docs.claude.com/.../pdf-support, accessed 2026-06-29]
#   • The textual extract is the "smallest high-signal set": the smallest set of
#     highly relevant tokens. The binary is the opposite — many low-signal tokens
#     per token (the visual frame of the slide, the PDF chrome).
#     [anthropic.com/.../effective-context-engineering-for-ai-agents, 2025-09-29]
#   • This is structured note-taking: knowledge becomes an external text file,
#     re-read on demand, instead of loading the binary into the window. (idem)
#
# EXTRACT vs. INDEX-ONLY (decision rule):
#   • EXTRACT (this sidecar, 1 per binary) — when the CONTENT of the material is
#     queried by the agent (a standard that governs a rule; a slide that defines
#     a domain concept; a diagram that explains a flow the code follows).
#   • INDEX-ONLY (one README/MANIFEST per folder, 1 per folder — not 1 per
#     file) — when the material is just a HUMAN REFERENCE ARCHIVE that the agent
#     does not need to read (old minutes, event decks, regulatory originals already
#     distilled in the technical layer). The index lists name + 1 line + binary path;
#     the agent knows it exists, without extraction cost.
#   • Golden rule: extract what governs a technical decision; index the rest. Do not
#     extract binaries just to extract (Simplicity First) — an orphaned extract no
#     one consults is also context rot.
#
# PROVENANCE (docs-front.md, co-located):
#   • The sidecar is born `authority: background` (it is human background, not a
#     contract) and `audience: agent` (the LLM consumes the EXTRACT; the binary
#     source is `human`).
#   • `binary:` points to the source by path/URL — the agent references it,
#     does not open it.
#   • `updated`/`source` inherit from the binary; an extract with `updated` much
#     earlier than the source = stale sidecar (re-extract) — same fossil anchor as
#     dim 2.
#
# BOUNDARY (dim 12): the sidecar is NOT the normative layer. If the content of the
# material BECAME a current contract, it is distilled into `standards/`
# (audience: both / authority: current) and the sidecar is no longer the truth —
# it becomes just a historical pointer. A sidecar with `authority: current` is the
# smell "human material marked as current" from dim 2.
