---
type: standard
title: Reading a canonical set
description: How the shipped tools consume a declared set — slice it by declared membership and never by position, because an ordinal index is a claim about the set's shape that nothing re-checks when the set grows; and why a byte-for-byte lockstep check proves the copies agree but never that the code reading them still means the same thing, so a membership invariant is owed its own assertion
resource: plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/specs/templates/spec.md
tags: [code, parsing, contracts, schema, lockstep, selftest]
timestamp: 2026-07-29
audience: both
authority: current
source: add-eli5-section-to-specs spec — the branch review found `specs.py new` had silently stopped stamping `## Problem` after `## Overview` was added ahead of it; both halves of this rule are the fix and the assertion that now guards it
maintainer: quenching
---

# Reading a canonical set

A **canonical set** is an ordered contract declared in one place and read in many:
`schema.json`'s `sections` array, its `phases[].entryGate`, the frontmatter record vocabulary.
The declaration carries both a membership (*which* headings) and an order (*in what sequence*).
Code that consumes it must be explicit about which of the two it is relying on — because the two
change independently, and only one of them is ever re-checked.

This standard governs the **consumption** side. The parsing of frontmatter itself is
[frontmatter-parsing.md](frontmatter-parsing.md); the section contract being declared is
[../workflows/plan-artifacts.md](../workflows/plan-artifacts.md).

## Slice by membership, never by position

**An ordinal index into a canonical set is a claim about that set's shape.** `lines[:i]` where
`i` is "the second `## ` heading" is really the claim *"the capture gate is exactly the first
heading"* — written in a form that cannot be checked, and that nothing re-derives when the set
grows.

The failure is silent by construction. Adding a heading is a legal, declared change to the set;
the positional reader keeps running, keeps returning a plausible slice, and simply means
something else than it did. Nothing errors, because nothing was ever asserted.

Read the declaration instead. When `specs.py` needs the headings that capture stamps, it asks
`phase_spec("plans")["entryGate"]` rather than counting to two:

```python
# wrong — an ordinal standing in for a membership rule
for i, line in enumerate(lines):
    if is_h2(line):
        seen += 1
        if seen == 2:              # "## Problem is first" — unstated, unchecked
            return "".join(lines[:i])

# right — the gate is declared; read the gate
gate = phase_spec("plans", schema).get("entryGate", [])
return preamble + "\n\n".join(section_guidance(h, text) for h in gate)
```

**Order may still be consumed as order** — `sorted(sections, key=order)` renders the canonical
sequence, and that is the declaration doing its job. What is forbidden is using a *position* to
answer a question about *membership*.

## A lockstep check does not cover the code over it

Several artifacts here are duplicated on purpose: `specs.py` embeds `schema.json` and
`templates/spec.md` as constants, because an installed copy under a target's `.claude/hooks/`
has no adjacent assets. `selftest` compares each pair byte-for-byte.

**That check proves the copies agree. It cannot prove the code reading them still means the same
thing** — and the two failures look identical from outside, which is what makes this worth
writing down. When `## Overview` was added to the template, both copies were edited together and
the lockstep check passed, correctly. Meanwhile the slicer over them had quietly changed meaning:
every spec `new` created lost `## Problem` and gained an empty `## Overview`, failing its own
entry gate from the moment it existed. The green selftest was reporting on a different question
than the one that had broken.

**So: a duplicate-detector is not coverage.** When a tool derives behaviour from a canonical set,
assert the derived behaviour against the declaration, not just the declaration against its copy:

- the assertion is about **output**, not about equality of inputs — *what `new` stamps*, not
  *whether the template matches*;
- state it against the declaration so it survives the next member added, rather than pinning the
  current answer;
- put it where the frontmatter cases already sit — **before** the early return for an installed
  copy — since a copy with no adjacent assets is exactly where drift goes unnoticed.

`specs.py selftest` now carries that assertion as `sp-capture-gate-missing` and
`sp-capture-extra-heading`: the capture form must contain every entry-gate heading and no other.
Neither code belongs to the `/specs:align` sweep vocabulary — like `sp-template-drift`, they are
selftest findings about the tool, not findings about a workspace.

## When the set grows

Adding a member to a canonical set is a **lockstep edit** across every place the set is declared
or counted — enumerated for the section contract in
[../workflows/plan-artifacts.md](../workflows/plan-artifacts.md), and released under
[../ci-cd/versioning-release.md](../ci-cd/versioning-release.md).

Two things are worth checking by grep rather than by memory, because both were missed the one
time this happened:

1. **Prose that counts the set.** "the thirteen canonical sections" is a fact with a number in
   it, and it appears in tool docstrings, user-facing error messages, the operator manual that
   installs into every adopting repo, and the command bodies that cite the contract. A rename
   that stops at the schema leaves the tool telling users a number it no longer implements.
2. **Positional readers.** Every ordinal index into the set, per §Slice by membership above.
