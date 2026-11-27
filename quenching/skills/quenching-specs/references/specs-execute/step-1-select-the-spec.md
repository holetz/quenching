# /quenching-specs execute — 1. Select the spec

Loaded only when this step runs; the flow index is [execute.md](.agents/skills/quenching-specs/references/execute.md).

An ID was given → use it. Otherwise infer from the conversation, auto-select when exactly one spec
is under way, or run `specs_read(verb="list")` and pick on a decision sheet ([questions.md](.agents/quenching/references/specs-develop/questions.md) §The four shared mechanics §1). Announce
"Building spec: `<id>`" and how to override. A sub-agent does not ask: return `STATE: blocked` with `NOTE: needs-human:` carrying the decision sheet.

**Done when:** one spec is resolved.
