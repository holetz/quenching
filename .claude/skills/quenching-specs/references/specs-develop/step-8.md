### 8. Close on a recommendation, and report
The re-derived stage came back in step 7's call. Compare it with
where the pass expected to land: a divergence is named and the pass re-enters at step 3 with a pass
derived from the real stage. **The re-entry is narrated, never offered.**

**No size check runs before approval.** Do not run `specs_read(verb="estimate")`, and
never ask, block or recommend decomposition over a token budget: a declared-reading estimate is not
a build's context, and a worker over its size estimate finishes the spec anyway.

Close according to the track — §Approval owns the screen:

- **Simple track** — no screen. With `ready` now **proved** by step 7's payload and `approved`
  unset, stamp it here: `specs_write(verb="record", spec=<id>, name="approved", by="session")`, which writes the date. **`by:`
  is never omitted** — a record with no `by:` reads as `human`, so leaving it off silently claims a
  human this pass never had. When the invocation says `autonomous`, stamp
  `by="orchestrator-forced"` instead. That is the only path that writes this value, and only
  after step 7 proved `ready`.
- **Complex track** — ONE closing decision sheet that **recommends** rather than defaulting to
  approve. Judge what the pass produced against §Refine's three signals and lead with the move they
  argue for, as option A (recommended), carrying the signal in its own text: approve, refine (with
  the lens the signal names), or stop. Choosing refine IS the OK to restamp `complexity` if the depth
  grew; apply both and re-enter at step 3. A pass where refine already ran recommends approving and
  names what the argument settled — never the refine the human already took.

**A refine re-enters the pass; it never restarts it.** What compose already wrote stays written —
the refine buys the argument the first pass did not have, over the artifact it drafted.

**The screen belongs to whoever holds the human.** Running standalone, present it. Running as a
sub-agent under a conductor, present nothing: return the screen's content and let the conductor
present it — a sub-agent never talks to the human, on any track.

Then report:

**When this run's input carried `autonomous`, skip the read below and the mold with it** — a conductor presents the report, not this run; return the content in the fixed shape the caller specified. Otherwise:

```text
components_read(verb="read", path=".agents/quenching/references/specs-develop/report-mold.md", sections=["§The report mold"], rules_only=true)
```

Emit §The report mold. The single-spec header line carries the stage **after** the pass; two body
blocks:

1. **The pass** — fixed. The spec's URL in the backend, repeated from step 1 off the same `path`
   field and never re-fetched; **the stages that ran, in order, and whether refine ran or was left
   to the close's recommendation**; the track and what it changed about who answered; how many
   questions were asked and answered, and how many answers the pass gave from evidence with an
   assumption named; **what refine overturned**, if anything; **an `approved` stamped
   `by: session`, `by: human` or `by: orchestrator-forced` on its own line**; the sections edited;
   whether surface refinement ran and, when it did, its group's task count; the records stamped; the routed offers and
   whether each was taken; the stage before and after, and whether it landed where the pass expected.
2. **Parked into `## Discoveries`** — optional, and every line **quoted**.

Print §The session-size line before the block — `components_read(verb="session_context")`, read once; exit 1 turns the `→` line into a recommendation to run the next stage **in a new session**, exit 0 and 2 leave it an offer.

Close on §The next-step block — `/quenching-git branch <id>` once `approved` is stamped, naming it
the natural moment to isolate before `/quenching-specs execute <id>` writes any code;
`/quenching-specs develop <id>` again to refine a spec that is already `ready`; or
`/quenching-specs execute <id>` to carry it to the end task by task.

**Isolation is named, never taken** — `/quenching-git branch <id>` appears once, in the next-step
block, and is never asked as a question mid-pass.
**Done when:** the pass closed or re-entered, and the summary is shown.
