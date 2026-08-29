---
type: standard
title: A conditional projection's guard must fail loudly, and must not name a field the contract can drop
description: A projection that falls back to "store it whole" when its shape check refuses is invisible on the way down — so the guard must be asserted against the shape the contract writes TODAY, and a contract change that removes a frontmatter key has to be traced into every guard that named it, because the failure is a silent loss of a capability rather than an error anyone sees
resource: plugins/quenching/assets/bin/quenching/specs/backends/hybrid.py
tags: [code, projections, guards, contract-change, silent-failure]
timestamp: 2026-08-23
audience: both
authority: current
source: abandonar-slug-por-id-nativo (issue 989), branch review — `hybrid_title_split` still required `slug` as the frontmatter's first key after the contract dropped it, so every newly captured spec fell to the store-it-whole fallback and the native title mapping stopped applying, with no test red and nothing printed
maintainer: quenching
---

# A conditional projection's guard fails loudly, or it does not fail at all

A **projection** splits a value out of a document so a native surface can hold it — the issue title
carrying a spec's `title:`, rather than the body carrying it twice. A projection that cannot prove
the document is in the exact shape it knows how to reassemble must refuse, and the refusal is
normally a **fallback**: store the document whole, unprojected, which is always correct.

That fallback is what makes the guard dangerous. Correct-but-degraded produces no exception, no
finding and no failing test. The capability is simply gone, on every document, from the commit that
broke the guard onward.

## The guard names the shape the contract writes today

A shape check that enumerates frontmatter keys is **coupled to the contract**, and a contract is a
thing that changes. Measured on this repository: `hybrid_title_split` required the first two keys to
be `["slug", "title"]`. When `slug:` left the frontmatter, the check went on passing its own
assertions — it was still a true statement about documents nobody writes any more — and returned
`None` for every spec captured afterwards. The native title mapping, the one native value in the
system that something reads back, silently stopped applying. No test covered the new template
against the guard, because each was correct in isolation.

**So: removing a field from a contract is not done when the writers stop writing it.** It is done
when every reader that named the field has been traced, including the ones that only *mention* it
inside a condition. Grep the field name, not the field's use.

## A tolerant reader obliges a tolerant guard

Where the contract change is deliberately *not* migrated — the old documents stay as they are and
the reader accepts both forms — the projection guard must accept both forms too. A reader that
tolerates the legacy shape while the writer's guard recognises only the new one is worse than a
clean break: the legacy documents keep reading fine and quietly **degrade on their next write**, one
at a time, as each falls to the fallback. The migration nobody authorised happens anyway, spread
across months of unrelated edits.

The inverse function is bound by the same rule. Where the guard cuts a value from an offset that
depends on which shape matched, the reassembly must re-derive that same offset rather than assume
one, or the round trip reorders every legacy document on the first write that touches it.

## Assert the projection, not only its parts

A round-trip case over a hand-written fixture proves `split` and `join` invert each other. It does
not prove either one still **applies** to what the tool writes, because a fixture is a document the
test authored. The assertion that catches this is the one that feeds the guard **the artifact the
product actually produces** — the template, the capture form, the create path's own output — and
asserts that the projection took, not merely that it round-tripped when it did.

See [/docs/standards/code/superseded-format-recognition.md](superseded-format-recognition.md)
for the sibling rule about recognisers: a new pattern is asserted against the OLD form, because a
pattern that describes the new one often matches the old one whole. This standard is the other
direction — a guard that describes the OLD form goes on being true while it stops being relevant.
