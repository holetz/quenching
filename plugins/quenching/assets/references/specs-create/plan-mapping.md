# Mapping a Claude Code plan onto a spec's canonical sections

Read only on the plan-file path of `/quenching:specs:create`, inside step 3 — the sentence path never
carries a plan file to map.

## The mapping

A Claude Code plan is prose with loose headings, and they may be in any language
(`## Context` / `## Contexto`) — **match on meaning, never on the literal string.**

| Native plan part | Canonical section |
| --- | --- |
| context, background, the problem, why now | `## Problem` |
| the goal, what it changes | `## Proposal` |
| non-goals, "fora de escopo", what it will not do | `## Out of Scope` |
| declared scope, files and docs it will touch | `## Impact` |
| acceptance criteria, how to confirm it worked | `## Validation` |
| decisions, chosen approach, architecture, "Decisões" | `## Design` |
| approaches weighed and dropped | `## Alternatives Considered` |
| open questions, "a decidir", unresolved choices | `## Open Decisions` |
| risks, trade-offs, "Riscos" | `## Risks` |
| phases, steps, numbered work, "Etapas" | `## Tasks` (`- [ ]` under `### N. <Section>`) |
| a verification / testing section | `## Tasks` (trailing verification items) |

A plan that carries none of the middle rows produces a spec with `## Problem` and `## Proposal`
and stops. **There is no rule that a converted plan must reach the ready gate**;
`/quenching:specs:develop` takes it the rest of the way.
