# Specs execution — delegation and parallelism

This file owns the bounded delegation, parallelism and knowledge-boundary rules used by the
execution loop. The verify/commit mechanics and the handoff cadence live in focused siblings.

## Declared versus emergent `knowledge/`

<!-- rules -->

A task writes a `docs/standards/` doc **only when the task itself names it** — the path bulleted
under `## Impact`'s parsed `### Standards this spec will write into docs/standards/` sub-heading,
and named by that task. That doc is part of the task's deliverable: it is written before the
commit, reviewed in the same diff, and stamped `authority` honestly — `current` when the task
actually proved the rule, `background` when it is agreed but not yet proven.

Everything else the work reveals — a gotcha, a second-order consequence, a rule nobody had thought
of — costs **one line and no authoring**:

```bash
cq specs discover "<id>" "<what was found, one line>"
```

It is captured **indiscriminately**. The lines are resolved by `/quenching:specs:develop`'s
discoveries stage, and the doc an emergent finding deserves is written by
`/quenching:specs:conclude` at distillation.

A task that writes into `knowledge/` is not delegated — §Delegating an executor.

## Delegating an executor — permitted, and bounded

<!-- rules -->

A per-task executor sub-agent (`Task`) is **permitted** when both hold:

- the task declares `files:` — the sub-agent gets a bounded scope, not the whole repo;
- the task writes nothing under `knowledge/`.

Pin it to the session model. **Never `haiku`** — it is writing production code, and the model
policy for that is the same one that protects `/quenching:knowledge:import-memory`'s classifiers.

**The orchestrator keeps, without exception:** spec selection, the isolation offer, every
confirmation, every `cq specs task --check` flip, every `cq specs task --block` marker, every
`docs/standards/` write, every `cq specs discover` line, the commit, and the decision to pause. The
sub-agent writes code inside its declared files and reports back — it never talks to the human and
never touches the spec's bookkeeping.

### The cost of delegating, and when it inverts

<!-- rules -->

**Permitted is not free, and the account runs the other way more often than it looks.**

- **Delegate by file, or by section of tasks — never task by task.** One sub-agent that owns six
  tasks over one file reads it once; six sub-agents read it six times.
- **Run the four-item self-review INSIDE the sub-agent**, and have it return a verdict. A
  sub-agent that hands its diff back for review puts the diff into the long context, which is the
  cost the delegation was for.
- **Where the tasks are small and the shared file is large, keep the work.** Reading once and
  re-reading from cache is the cheaper arm, and the loop is allowed to say so.

The delegation is a `Task`, not `context: fork` — §Tooling asides.

### Parallelism must be earned

<!-- rules -->

Two tasks run concurrently **only** when all three hold:

1. a `[P]` marker was set on both **at definition time** — never inferred while executing;
2. their declared `files:` sets are **provably disjoint** (`cq specs` checks this mechanically —
   see §The `[P]` check);
3. neither writes into `knowledge/`.

Serial is the default and needs no marker. Without proven file disjunction, parallel execution
trades wall-clock for merge conflicts and loses on both.

### The `[P]` check

<!-- rules -->

```bash
cq specs parallel --spec "<id>" [--json]
```

Reports each `[P]` group and whether it is `eligible`. Exit **0** when every marked group is
eligible, **1** when any group overlaps or lacks `files:`. **Branch on that, never on judgment**:
a group reported ineligible runs serially, and the reason is stated in the report rather than
argued about.

