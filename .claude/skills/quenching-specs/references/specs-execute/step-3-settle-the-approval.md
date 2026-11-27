# /quenching-specs execute — 3. Settle the approval, off the state step 2 already read

Loaded only when this step runs; the flow index is [execute.md](.claude/skills/quenching-specs/references/execute.md).

**Load the stage ladder first** — what the derived stage names and means:

```text
components_read(verb="read", path=".agents/quenching/references/specs-develop/spec-driven.md", sections=["§Derived stages"])
```

The `specs_read(verb="status")` payload is **already in hand** from step 2 — do not read it again.
From it: the derived stage, the section states, task progress, the blocked tasks, the recorded
subjects, and **`verification`** — the spec's declared policy, which decides when the suite runs.
Whether a task goes to an executor sub-agent stays the two conditions
of [execution-delegation.md](.agents/quenching/references/specs-execute/execution-delegation.md)
§Delegating an executor, at every level.

- **`approved` unset** → ask for it inline, in one question showing what the spec commits to, and
  on a yes stamp it `by=human` (`specs_write(verb="record", spec=<id>, name="approved")`, which writes the date
  and `by=human`). **Never refuse over it.** A no ends the run cleanly. **Under `autonomous`, `approved`
  unset is a real block**: never ask, never stamp — return `STATE: blocked` with `NOTE: needs-human:
  approval is develop's`.
- **`next` reports `write_section`** → the ready gate is not met. Name the missing or malformed
  sections and route to `/quenching-specs develop <id>`, then stop.
- **Every task already `- [x]`** → say so and offer to chain into `/quenching-specs conclude` (step 7).
- **`[!]` blocked tasks** → name them and their reasons up front. They were tried and stopped, not
  skipped.

Mention any open `specs_read(verb="validate")` warning **once** — `sp-unrefined` (nobody has interrogated
this spec), `sp-impact-uncovered` (a declared standard no task writes) — and offer
`/quenching-specs develop`. Never gate on it: the ready gate is a floor, not a verdict.

**Done when:** the state is in hand, `approved` is settled, and any warning has been surfaced once.
