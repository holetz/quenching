---
type: standard
title: Warning about an unproven capability
description: Where a caveat about a capability that ships without end-to-end proof belongs — the two failure shapes that decide it, the standing fact as a verifier finding and the moment-of-risk line once per process on stderr, why a per-operation warning is a permanent context tax and silence is not the alternative, and the one edit that retires both together
resource: plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/assets/bin/quenching/components/**, plugins/quenching/assets/bin/quenching/knowledge/**
tags: [quality, verification, findings, warnings, unproven, context]
timestamp: 2026-08-10
audience: both
authority: current
source: configurable-spec-backend plan — the `azure-boards` arm of task 6.3, generalised at conclude from the decision `## Open Decisions` deferred to that task; the example block updated by provar-e-posicionar-o-backend-azure-boards (task 7.2), the first real retirement the mechanism this standard describes has been through
maintainer: quenching
---

# Warning about an unproven capability

A capability sometimes ships correct-by-construction and unproven-in-practice: the interface is
asserted, the refusals are asserted, and it has never once been run against a real target. This
standard is where the caveat about it goes.

It is not about bugs. A known bug is a finding or a fix. This is the narrower case where **nothing
is known to be wrong and nothing has been observed to be right**, and the tool must say so without
becoming unusable.

## The two failure shapes decide the placement

The wrong question is "how loud should the warning be". The right one is **how the unproven paths
fail**, because that is what says whether a human will find out on their own:

- Some fail **loudly**. A wrong identifier makes the vendor's API answer with an error and the
  transport turns it into a refusal. Nobody needs to be warned about those — they announce
  themselves at exactly the right moment.
- Some fail **quietly**. A parse that extracts no ids returns an empty collection that reads as
  legitimately empty; a write that fails halfway leaves items behind on somebody's real system.
  These are the ones a caveat exists for.

A capability whose unproven paths all fail loudly needs no warning at all.

## Two placements, and each carries a different half

| The caveat is… | It belongs in… | Because |
| --- | --- | --- |
| a standing fact about the **configuration**, unchanged between calls | the front's own verifier, as a `warn` finding | it is what a human is already asking when they run the verifier: what is wrong with this setup |
| a fact about **this call's risk**, at the moment the risk is taken | **one** line on `stderr`, once per process, before the first operation that can lose something | it has to arrive where the loss would happen, and nowhere else |

Both halves ship, or the answer is incomplete. The finding alone is silent to anyone who never runs
the verifier; the line alone leaves nothing to find when a human goes looking for what is wrong.

**The line lands on the writes and never on the reads.** In a build loop reads outnumber writes by
an order of magnitude, and a read of an unproven backend loses nothing — it returns wrong data or it
returns a refusal, and both are visible immediately. A write is where a half-succeeded operation
leaves debris nobody sees.

**`stderr`, never `stdout`.** Every caller of these tools branches on the `--json` payload, so a
warning printed into it breaks the parse it exists to inform.

## Per-operation is a permanent tax, and silence is not the alternative

A line on every call is the honest-looking default and the wrong one. The fact never changes between
calls, so re-stating it charges every agent session for a constant — the same cost
[skills.md](../automation/skills.md) prices for a description that is always
resident, paid here in output instead. An agent that reads the same sentence forty times in a build
loop has been taxed thirty-nine times for nothing.

That argument does not license silence. Silence is what makes the quiet failure shape above quiet
*twice*: once in the failure and once in the absence of any record that the path was never proved.
**Once per process, before the first write** is the smallest thing that is not silence.

## Naming the unproven set once retires it in one edit

Which capabilities are unproven is **one named collection**, kept where both halves read it rather
than inside the implementation being warned about:

```python
UNPROVED_BACKENDS = ()
```

The moment a real target exercises it end to end, the collection loses a name, and the verifier
finding and the write-time line go quiet **together**. A caveat spelled out separately in each place
gets retired in one place and survives in the other — which is worse than either, because a tool
that warns about a capability it has since proved teaches its readers to ignore its warnings.

**This is not the hypothetical case — `azure-boards` was the one name this tuple carried, and
`provar-e-posicionar-o-backend-azure-boards` (task 7.1) is the edit that retired it.** §6 of that
plan ran the backend end to end against a real Azure DevOps project (org `unicredbr`, team
"Diretoria Risco"): `new --subject`, every `section --write`, `record`, `task --check`, `status`,
`show` and `promote --outcome done`, each compared against `files` for the same state and
matching, the board's own column tracked through every transition against the declared de-para.
The one edit — the tuple losing its one name — is what took the `doctor` finding and the
`announce_unproved` stderr line quiet together, exactly as this section describes.

The other half of that discipline is that a shipped-unproven capability is stated as such in the
standard that governs it, not only in the tool. See
[spec-backend.md](../architecture/spec-backend.md) §What this standard does not yet cover — a
contract to meet is not a report of one met.
