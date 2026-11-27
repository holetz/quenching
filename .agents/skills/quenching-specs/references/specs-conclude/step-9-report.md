# /quenching-specs conclude — step 9: Report

**When this run's input carried `autonomous`, skip the read below and the mold with it** — a conductor presents the report, not this run; return the content in the fixed shape the caller specified. Otherwise:

```text
components_read(verb="read", path=".agents/quenching/references/specs-develop/report-mold.md", sections=["§The report mold"], rules_only=true)
```

Emit §The report mold. The single-spec header line carries the locator, its phase (`plans` until the
post-merge close, `archive` after it) and the outcome; three
body blocks:

1. **At close** — fixed. Task progress, `reviewed` / `branch` as they now stand, and — for an
   abandonment — that nothing was adopted and what became of the branch.
2. **The review** — fixed. What it found and what was done about it, the docs written in step 3 and
   step 5, **what the sweep captured in step 6** — the ids it opened and the candidate it declined,
   with the reason — and what the pre-merge gate returned. §Quoting a tool's own output governs the gate's
   result, which means **a check that came back inconclusive is named as such, never counted as
   passed**. Close the block with one line on **target acceptance** — whether the change was
   exercised where it lands, apart from the local gate: `Target acceptance: verified (<what ran,
   where>)`, `not performed (<why>)` or `n/a (<why nothing lands outside the gate>)`. A green gate
   proves this checkout, never a deployed target, a real session or the provider, so it never
   stands in for `verified`.
3. **Unresolved `## Discoveries`** — optional, each line named. They are
   `/quenching-specs develop`'s discoveries stage to close, and they are easiest to lose at exactly
   this moment.

Print §The session-size line before the block — `components_read(verb="session_context")`, read once; exit 1 turns the `→` line into a recommendation to run that handoff **in a new session**, exit 0 and 2 leave it an offer.

Close on §The next-step block, its recommended line naming step 7's handoff — `/quenching-git pr-create`
or `/quenching-git merge`, whichever was recommended, or `/quenching-specs develop <id>` when
block 3 has rows and that needs settling first.
