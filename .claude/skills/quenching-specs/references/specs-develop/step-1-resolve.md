### 1. Resolve the spec, and announce where it lives
**Resolve the tool first.** Resolve `cq` (`components_read(verb="read")` is the section reader every `§X` citation in this flow resolves through)
per
[align/tool-resolution.md](.agents/quenching/references/align/tool-resolution.md)
§Resolving the tool, §Write the resolved path literally on every invocation; branch on the **exit
code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose.

**The batching contract for this step and the next:**

| Where | The bounded read(s) |
| --- | --- |
| steps 1+2 | `specs_read(verb="status", spec=<id>)`, which also carries the `path` step 1 announces, the recorded depth, and the `sections`/`ready` map compose drives off. Only an ID that must be *chosen* splits this: `specs_read(verb="list")` runs first, because the question depends on its output |

Take the id from the input, infer it from the conversation, or run `specs_read(verb="list")` and ask
on a decision sheet (most recently modified as option A, recommended). Announce it and how to
override. Two matches for one id is exit 2 — report both paths and stop, never guess which was
meant. An archived spec has nothing to develop: say so and stop.

**Announce the spec's URL in the backend along with it** — the `path` field of the
`specs_read(verb="status", spec=<id>)` payload step 2 takes in this same call (the card's URL when
one exists, else the spec's file location on the `quenching` branch), stated before anything is
read and repeated in the report (step 8).
**Done when:** one spec is resolved and its URL or location has been announced.
