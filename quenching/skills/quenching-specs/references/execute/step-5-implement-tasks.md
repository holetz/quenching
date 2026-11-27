# /quenching-specs execute — 5. Implement tasks — loop until done or blocked

Loaded only when this step runs; the flow index is [execute.md](.agents/skills/quenching-specs/references/execute.md).

Ask the tool for the next task; **never pick one by reading the file**:
```text
specs_read(verb="next", spec=<id>)
```
It returns that task's `verify`, `files`, `pattern` and `parallel`, plus the spec's `verification`
policy, and it **skips `[!]` blocked tasks** (`action: "blocked"` once every remaining task is).

Then, for that task:

a. **Show what is being worked on** — the ID, its declared `files:` and its `verify:`.

b. **Write the code**, minimal and scoped to the declared files (a task tagged `[fix-preexistente]` declares its own, see 5i). A task that declares `files:` and writes nothing under `/docs/` **may** go to an executor sub-agent: read [step-5b-delegate-an-executor.md](.agents/skills/quenching-specs/references/execute/step-5b-delegate-an-executor.md) whole before dispatching, and not otherwise.

c. **Write only the `/docs/` this task names.** Run it from [step-5c-docs-this-task-names.md](.agents/skills/quenching-specs/references/execute/step-5c-docs-this-task-names.md) — read that file whole when this sub-step runs, and not before.

d–e. **On the first pass, load the rules the chain runs under, self-review the diff, then verify, stage, commit and tick the spec task as ONE chained operation.** Run it from [step-5de-verify-commit.md](.agents/skills/quenching-specs/references/execute/step-5de-verify-commit.md) — read that file whole when this sub-step runs, and not before.

f. **Read the chain's tail, and act on which link broke** — per §The commit, already loaded in
   5d: `verify:`/staging failed → nothing ticked, nothing committed; fix and retry, or block it
   when attempts stop converging. The commit failed → report with the task still unchecked. The
   spec tick failed after a successful commit → preserve the commit and retry only the remote
   write. The recorded subject or sha drifted → report it as a finding and write nothing further.

g. **Run and report the declared hook for this event, and move on.** Run it from [step-5g-after-task-hook.md](.agents/skills/quenching-specs/references/execute/step-5g-after-task-hook.md) — read that file whole when this sub-step runs, and not before.

h. **At a section boundary, keep the task commits and continue.** The branch is at a clean,
   independently anchored boundary; another section may still be ahead. **No session-size read runs
   here and the boundary is never a question:** do not measure the context, print a budget or offer
   a new session. Stop only when the workflow reaches a question that requires a human answer, or
   under the pause conditions below. See
   [execution-cadence.md](.agents/quenching/references/specs-execute/execution-cadence.md)
   §The section boundary.

i. **A red that is not this spec's has its own route, never a dismissal.** Run it from [step-5i-preexisting-red.md](.agents/skills/quenching-specs/references/execute/step-5i-preexisting-red.md) — read that file whole when this sub-step runs, and not before.

**Pause if:** a task is unclear; implementation reveals a design problem (→ `/quenching-specs develop`); a
task contradicts a `/docs/standards/` contract (surface it and let the human pick — revise the
standard via `/quenching-knowledge add`, or the spec via `/quenching-specs develop`); attempts stop converging; or the user
interrupts.

**Under `autonomous`, the pause is the real block**, the closed list of
`/docs/standards/workflows/task-execution.md` §After approval, the executor decides, records and stops
only on a real block: attempts stop converging; a standard contradiction the evidence does not
settle; a new grant, a changed frontmatter key or a lowered bar; an undeclared irreversible, merge, push or deploy
action; a required proof that cannot run; `approved` absent. A proof the spec requires that cannot
run for a missing environment variable, credential or service is a real block — never skipped in silence,
never marked as passed. An uncontained pre-existing red (5i) is that real block: capture the spec, name
it in `needs-human:` and stop. Anything else the evidence or the recorded intent answers is decided and
recorded as one line, `specs_write(verb="discover", spec=<id>, text="decision: <what> — <evidence or criterion>")`; a
`decision:` line is not a Handoff event.

**Done when:** every task is `- [x]` or `- [!]`, or the run pauses with the reason stated.
