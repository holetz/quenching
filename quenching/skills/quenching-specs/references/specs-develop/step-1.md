### 1. Resolve the spec, and announce where it lives
Take the id from the input, infer it from the conversation, or run `specs_read(verb="list")` and ask
on a decision sheet (most recently modified as option A, recommended). Announce it and how to
override. Two matches for one id is exit 2 — report both paths and stop, never guess which was
meant. An archived spec has nothing to develop: say so and stop.

**Announce the spec's URL in the backend along with it** — the `path` field of the
`specs_read(verb="status", spec=<id>)` payload step 2 takes in this same call (the card's URL when
one exists, else the spec's file location on the `quenching` branch), stated before anything is
read and repeated in the report (step 8).
**Done when:** one spec is resolved and its URL or location has been announced.
