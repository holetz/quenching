---
type: standard
title: A `__file__`-relative path encodes a depth, and packaging changes it
description: Every `__file__`-relative expression silently encodes how deep its module sits; moving a script into a package re-evaluates it somewhere else without erroring, and the two instances this repo measured failed in opposite directions — one turned a lockstep check off and exited 0, the other made a subcommand refuse forever
resource: plugins/quenching/assets/bin/quenching/specs/schema.py, plugins/quenching/tests/test_specs_assets.py
tags: [code, packaging, paths, verification, refactoring]
timestamp: 2026-08-11
audience: both
authority: current
source: modularizar-specs-knowledge-components spec — both instances measured while cutting four standalone scripts into one package (tasks 3.x and 4.2), and the silent-green one turned into an assertion by task 6.3 (`tests/test_specs_assets.py`)
maintainer: quenching
---

# A `__file__`-relative path encodes a depth, and packaging changes it

`os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "x")` is not a path. It is a
**path plus an assumption about where this file sits**, and the assumption is the part no reader
sees. Move the file one directory deeper and the expression still evaluates, still returns a
string, still raises nothing — and now names somewhere else.

That makes it the one construct that a pure move breaks. Turning a set of standalone scripts into
a package is otherwise a mechanical operation: imports change, behaviour does not. Every
`__file__`-relative expression is an exception, and it is an exception that announces itself only
if something downstream happens to be looking.

## The two instances, and why they matter more together than apart

Both were found cutting the same four scripts into one package. They break the same rule and
present as **opposite symptoms**, which is why neither one teaches the lesson alone.

**Silent, and green.** The specs pillar resolves its embedded assets with
`ASSET_DIR = join(HERE, "..", "specs")` — correct from `assets/bin/`, one level short from
`quenching/specs/schema.py`. Nothing raised. The consumer was `cmd_selftest`'s lockstep between
the embedded `schema.json` / `templates/spec.md` constants and the files on disk, and when it found
**neither** asset it answered `skipped: true` and **exit 0**, with the message *"no adjacent assets
to compare (installed copy)"*. That skip was written for a real case — an installed copy has no
assets beside it — and a wrong path arrives at that branch identically. So a resolution bug did not
report a resolution bug: it **switched the lockstep off and passed**.

**Loud, and total.** The components pillar's `resolve_plugin_root` seeded its search at
`dirname(abspath(__file__))` and walked up `range(4)`. From `assets/bin/` that reached the plugin
root; from `quenching/components/commands/` it is three packages deeper and four hops never arrive.
The verb would have refused (exit 2) on every invocation, in every repo, forever. That module has
since been retired with its subcommand, so the instance survives here as measurement rather than as
live code — which is the only reason it is worth writing down: it is the *pair* that is instructive.

**And the same expression can be neither.** `HERE = dirname(abspath(__file__))` in the pre-refactor
OKF validator was computed on every import and read by nobody across 1,372 lines. The identical
line is load-bearing in one file, dead in another, and only its consumers say which — so a sweep
that treats the expression as a syntactic pattern will both miss the live ones and migrate the dead
ones.

## The rule

**When a module moves, every `__file__`-relative expression in it is re-derived and asserted, never
observed.** Enumerate them, resolve each one, and assert the resolved path points at something real.

**A check that passes is not the assertion.** This is the whole content of the first instance: the
existing check could not distinguish *"the assets are not here, which is fine"* from *"the assets
are not where I looked, which is a bug"*, and a construct that cannot tell those apart returns no
verdict either way — see [../quality/surface-verification.md](../quality/surface-verification.md)
§The five preconditions a check must satisfy. The repair is to assert the resolution itself:
`tests/test_specs_assets.py::test_the_assets_are_found_at_all` is that former skip turned into a
failing assertion, so the lockstep can no longer be switched off by a path that stops resolving.

**Prefer an expression with no hop count when the anchor is nameable.** `..`-counting is what
encodes the depth; a search that stops at a named marker, or a constant derived once at the package
root and imported, moves without being edited.

## Where this sits

This is [../quality/parse-honesty.md](../quality/parse-honesty.md)'s failure at the filesystem
layer: there a tool reported confidently about a string it never held; here it reports confidently
about a directory it never found. Both are cases of a step that **cannot fail** standing in for one
that was supposed to be able to.
