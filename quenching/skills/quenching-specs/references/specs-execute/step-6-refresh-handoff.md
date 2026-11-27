# /quenching-specs execute — 6. Refresh `## Handoff` on four events, never on judgment

Loaded only when this step runs; the flow index is [execute.md](.agents/skills/quenching-specs/references/execute.md).

Rewrite the **relevant block** of `## Handoff` to the state of play a fresh executor would need
**and cannot derive** — on exactly four events:

- the run **pauses**;
- a task is written **blocked**;
- a **discovery** is recorded;
- the run's **last commit** lands.

`## Handoff` is a small evergreen **global block** plus one block per `## Tasks` `### N.` section.
A rewrite touches ONE of the two — never both, never a closed section's:

```text
specs_write(verb="section_write", spec=<id>, heading="Handoff", scope="global", body=<body>)    # the evergreen block
specs_write(verb="section_write", spec=<id>, heading="Handoff", scope="current", body=<body>)   # the block of the open section
```

Everything a resumed run *can* derive — which tasks are done, which commit carried each — is
already in `git log` and in the `subjects` `status` returns; the Handoff is not the resumption
trail. The global block plus the current section's block are sent with every task, so keep both
small. `scope="current"` always resolves to whichever section still has open work.

**Not after every committed task, and not on a judgment call either** —
[execution-cadence.md](.agents/quenching/references/specs-execute/execution-cadence.md) §The
Handoff cadence.

**Done when:** the global block and the current section's `## Handoff` block describe the tree as
it stands after the run's last commit.
