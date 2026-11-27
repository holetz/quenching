### 4. Compose
**A recommendation rides inside the question, never in a turn before it.** Where a choice is
genuinely the human's, the recommendation and the reasoning behind it go on the **decision sheet**
([questions.md](.agents/quenching/references/specs-develop/questions.md) §The four shared mechanics §1) — option A, recommended, the reasoning in its own text — so the human answers in one word and no turn was spent setting the question up.
A sub-agent does not ask: return `STATE: blocked` with `NOTE: needs-human:` carrying the decision sheet.
**This contract stops at the edge of how questions are grouped.**
[questions.md](.agents/quenching/references/specs-develop/questions.md) §The four shared
mechanics §1 is the only authority there: a question travels with the ones whose answers cannot
change it, and alone otherwise.

Skip where the spec is already `ready`. Otherwise follow §Compose, under the four shared mechanics:
sequential to shape, grouped to close, every question carrying **an inline recommendation**, every
answer naming the section it lands in, and the stage's declared stop condition.

**The track decides who answers; §Compose is unchanged either way.** On the **simple track** and on
declared autonomy the pass answers every item **from evidence**, names the assumption inside any
answer that rests on one, records it under `### Assumptions` in `## Design` (one line, with the
section that depends on it), and parks what no evidence answers as an `## Open Decisions` line
carrying how it will be decided — it asks nothing. On the **complex track** it drafts those same
answers first and asks the human **about the draft**, in batches: one round at a time, with the
questions whose answers do not change one another, each carrying a recommendation. A question that
depends on an answer waits for the next round.

Questions must be **specific to this spec**. One that would read identically against any spec is
noise — do not ask it, and do not pad the count with it. That holds for a drafted answer too: one
that would read identically against any spec is a default, not evidence, and it is parked.

Nothing is written. Keep a running list of `(question or drafted answer, its source, target
section)`.

**The fourth execution question is asked here:** the compose set ends on `[P]`, `files:` and
`pattern:` ([questions.md](.agents/quenching/references/specs-develop/questions.md)
§Compose), and this pass asks **which tests does this task touch?** beside them, per task. Every
test whose diff the task produces belongs in its `files:` —
[artifacts.md](.agents/quenching/references/specs-develop/artifacts.md) §`## Tasks`
§Execution metadata owns the rule — and a test left out is the out-of-scope diff the verifier
charges at the door. Same moment, same evidence: the question is cheap while the task is a draft
and expensive after its commit.
**Done when:** the ready set is closed in the draft, or the user called it.
