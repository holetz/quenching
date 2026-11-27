### 2. Read the spec's STATE — not its body
```text
specs_read(verb="status", spec=<id>)   # stage, section states, ready map, records, tasks, gate, path
```
**This is the same call as step 1** — §The batching contract's first row. The id either came in
the input or was inferred, and the payload answers both steps at once.

**The payload also carries the depth on record and the gap.** `records.priority.complexity` is the depth
last recorded; absent, or no `priority` record at all, reads as `high`
([spec-driven.md](.agents/quenching/references/specs-develop/spec-driven.md) §The scale). So does
`ready: {ok, missing, malformed}`, which is the list compose owes.

That is the whole of this step. **No section body is pulled here.**
**Done when:** the spec's stage, section states, ready map, records, gate, backend URL and recorded depth
are in hand.
