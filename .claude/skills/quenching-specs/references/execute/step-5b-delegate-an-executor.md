# /quenching-specs execute — step 5 b (delegating)

Loaded only when task 5b is dispatched to an executor sub-agent, together with the step 5 loop in [step-5-implement-tasks.md](.claude/skills/quenching-specs/references/execute/step-5-implement-tasks.md); the flow index is [execute.md](.claude/skills/quenching-specs/references/execute.md).

A task that declares `files:` and writes nothing under `/docs/` **may** go to an executor sub-agent under
[execution-delegation.md](.agents/quenching/references/specs-execute/execution-delegation.md)
§Delegating an executor; when it is, load the rules that bound it before dispatching:

```text
components_read(verb="read", path=".agents/quenching/references/specs-execute/execution-delegation.md", sections=["§Delegating an executor"])
```

**The `haiku` rung is per task.** For the `Task` executor, `specs_read(verb="estimate", spec=<id>,
task=<task-id>)` reporting `smallTierEligible: true` admits a `haiku` pin for one
attempt, under §Delegating an executor; anything else pins the session model.
