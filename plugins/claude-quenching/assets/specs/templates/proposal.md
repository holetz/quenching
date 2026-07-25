# <TITLE>

## Why

<!-- The problem or opportunity this plan answers. Why now? -->

## What Changes

<!-- The change at a high level, in bullet points. -->

## Out of Scope

<!-- What this plan deliberately does NOT do, and why it was ruled out.

     An empty section is written as an explicit `- none` — NEVER omitted. "We drew the
     boundary and nothing fell outside it" and "nobody ever drew the boundary" are
     different answers, and an absent section cannot tell them apart. -->

## Validation

<!-- How anyone confirms this plan actually worked: the commands to run and the output
     they must produce, the fixtures to check, the invariants that must still hold
     afterwards. Same rule — an empty section is written as `- none`, which is a claim
     that the plan is unverifiable by construction. Make it on purpose or fill it in. -->

## Impact

<!-- Declared scope for human review.

     The `### Standards this plan will write into docs/standards/` sub-heading below is
     PARSED by `specs.py validate`: every `docs/standards/**.md` path bulleted under it
     must be named by a `tasks.md` item, or validate emits `sp-impact-uncovered` (warn).
     Keep that heading text verbatim — it is the anchor. A `**Standards this plan will
     write into ...**` bold line is accepted too, for plans written before this format.

     Example of a parsed bullet:
       - `docs/standards/naming/command-surface.md` — the bijection rule for wrappers

     The other sub-headings are prose for the reader and are deliberately NOT parsed:
     they name paths the plan does not promise to write. -->

### Standards this plan will write into docs/standards/

- `<docs/standards/subject/concept.md>` — <the rule it states>

### Standards at `authority: background` this plan may resolve

- <path, or `none`>

### Product code this plan expects to touch

- `<path>` — <why>
