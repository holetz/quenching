---
type: standard
title: Mutation-checking a test
description: A test that has never been observed to fail is untested — the mutation pass that earns the claim, one mutation per rule the fixture exists to prove, why the pass is run once at authoring rather than wired into CI, and the graduation gate the repo's new tests/ suite has not yet cleared
resource: plugins/quenching/tests/**
tags: [quality, testing, mutation, verification]
timestamp: 2026-08-27
audience: both
authority: background
source: improve-command-from-session plan — the mutation pass was run against the session tool's (pre-refactor) selftest at task 2.1 and recorded in that spec's `## Discoveries`; a second pass, over the routing rules only, ran against the components tool's (pre-refactor) selftest during route-commands-without-always-on-descriptions (7 mutations, 2026-08-02) — a third, over its `--sections` ladder, ran during skills-py-sections-comma-split-bug (3 mutations, 2026-08-05 — two killed, one recorded equivalent), and contributed the both-modes and equivalent-mutant rules; reframed by modularizar-specs-knowledge-components task 9.3 once tests/ replaced the four `selftest` subcommands this file used to govern (its own §Testes closed the loop the historical passes below could only gesture at — the `-k backend`/`-k parse`/`-k command`/`-k config` verify: lines of that spec's sections 3–5 collected ZERO tests and exited 0, the exact failure mode `test_discovery_is_not_empty` now asserts against); §The third pass added by make-named-by-bodies-scale-with-the-surface-it-was-built-for task 1.2 (2026-08-17), the first pass run against `tests/` rather than a retired selftest — it re-ran the seven mutations of §The second pass and found five of them no longer killed by anything, which is a measurement of the replacement suite and not of the rewrite it was run beside; §The fourth pass (2026-08-27, same seven, seven killed) closes that gap with `tests/test_lint_inert_stage.py`, the successor fixture the third pass named as missing, added by the same spec's task 1.2
maintainer: quenching
---

# Mutation-checking a test

Every module `tests/` covers is exercised by `python3 -m unittest discover -s tests`, which
CLAUDE.md's verification block leans on. A test is the cheapest verification the repo has — and
the easiest to write so that it can never fail.

**A test that passed the first time it was run has proved nothing yet.** It has demonstrated that
some code returns some value; it has not demonstrated that the value is *checked*. A fixture list
that is iterated but never compared, an assertion on a field the parser always populates, a case
appended to the corpus but never reached, a `-k` selector that collects zero cases and exits 0 —
each passes exactly as loudly as a real check.

## The rule

Before a test is claimed as verification, **break the thing it exists to prove and watch it
fail.** One mutation per rule, applied to the code under test, reverted after.

The pass is done **once, at authoring**, by the human or agent writing the test. It is not wired
into CI and there is no mutation-testing dependency — the suite is `unittest`, stdlib-only, and
adding a mutation-testing tool to prove tests that already assert against the interpreter would
cost more than the tests do. What survives the pass is not tooling but a claim in the commit that
wrote it.

## What a mutation is worth

A mutation earns its place when it is **a rule the fixture exists to prove**, not an arbitrary edit.
Deleting a whole function proves nothing: everything fails, and a selftest that catches a deleted
function may still miss every subtle case. The useful mutation inverts one decision.

The pass over the pre-refactor session tool's selftest (its `selftest` subcommand, 15 fixture records) ran four:

| Mutation | Rule it attacks | Result |
| --- | --- | --- |
| stop excluding `isMeta: true` turns | the harness's own echo of a command body is not a human correction | 2 assertions fail |
| read only the bare-string form of a user turn | a human turn arrives as text **blocks** in a list | 1 assertion fails |
| count `Edit`/`Write` against a file as a read | reads and writes are different facts | 2 assertions fail |
| drop the `uuid` dedup | one turn replayed is not two turns | 1 assertion fails |

Each mutation failing **one or two** assertions rather than all fifteen is itself the signal worth
reading: it means the assertions are discriminating between rules instead of all riding on one
happy path. A mutation that fails every assertion, or none, is a fixture that needs work.

The third row is the one that justifies the whole practice. Counting writes as reads is not a
hypothetical: it shipped once, and reported 51 edits as `redundant read x72` — a confident,
plausible, entirely wrong finding, against a run whose honest redundant-read count was **0**. The
selftest that now holds that line was written *after* the bug, which is the ordinary case; the
mutation pass is what confirms the line is actually held rather than merely intended.

Three rules about how the pass itself is run, each learned by a pass that would otherwise have
reported something it had not measured:

**Run every mutation in every mode the check will be trusted in.** A tool with a `--json` arm and a
human arm has two code paths, and a pass that exercises one grades one. Measured on
the pre-refactor components tool's `--sections` ladder (2026-08-05, three mutations): the new case shadowed an outer
variable inside `cmd_selftest`, and `selftest --json` exited **0** while plain `selftest` — the form
this repo's own `CLAUDE.md` verification block runs — raised `TypeError` after printing its case
count. Only the mutation pass, run in both modes, separated them. The same shape governs any
`verify:` line: one written solely over `--json` cannot observe the branch a human reads.

**A survivor that is provably equivalent is recorded, not chased.** The same pass mutated
`if got or "," not in value` to `if got:` and nothing failed — correctly, because `split(",")` over
a comma-free value returns that value, so the two forms have identical output for every input. An
equivalent mutant is a fact about the mutation, never a gap in the fixture; write down *why* it
cannot be killed, and leave the clause if it earns its place as a statement of the contract. Hunting
it produces assertions that test the code's shape instead of its rules.

**Establish the before-state with `git diff`, never with a copy of the tool run from elsewhere.**
The same pass tried to prove an untouched file by comparing case counts against a copy of the base
under `/tmp`, and got 12 against 20 — pure artefact: `find_surface_root` resolved a different
`schema.json` from outside the plugin tree. A shipped tool run outside its own tree silently grades
something else.

## The second pass — the pre-refactor components tool, and why it counts as partial

Run 2026-08-02 for `route-commands-without-always-on-descriptions`, against the rules that spec
added: the residency predicate `budget` and `lint` both read from, and the set of commands a
conductor reaches by name, derived from the bodies. Seven mutations, seven observed failures:

| Mutation | Rule it attacks | Result |
| --- | --- | --- |
| `description_is_resident` → always `True` | prose routing does not reach a typed-only command | `/docs:typed-only-bare`: expected `[]`, got `sk-no-boundary`, `sk-trigger-position` |
| `description_is_resident` → always `False` | …and it *does* reach a resident one | `/docs:routed-bare`: expected both codes, got `[]` |
| drop the leading-slash exclusion | `/prefix:name` is a citation aimed at a human, not a hand-off | `/docs:stage-cited` wrongly flagged `sk-inert-stage` |
| drop the Skill-tool arm | the unprefixed slash form near "Skill tool" is also a hand-off | `/docs:stage-handed` not flagged |
| drop the registry arm | the bare registry form is the hand-off | `/docs:stage-inert` not flagged |
| drop the self-reference guard | a command cannot conduct itself | `/docs:typed-only-bare` wrongly flagged |
| ungate `sk-inert-stage` from the caller set | typed-only is legitimate when nobody names it | **crash** — `TypeError: 'NoneType' object is not iterable` |

Six of the seven land the way the section above says a useful mutation lands: one named fixture
case, expected and actual code lists printed side by side. **The seventh does not, and naming that
is worth more than counting it.** It failed by raising, so what caught it was Python, not the
corpus. A crash proves the mutated path is reached; it does not prove the fixture discriminates —
the same mutation in a tool that tolerated the bad value would have survived silently. Read
strictly, this is six mutations that earned the claim and one that only looks like it did.

**And it covers the new rules only.** That selftest also carried fixtures for the two
description caps, body length, step criteria, tool scoping, the hook codes and the citation form,
and none of those was mutated. Adding a rule with a mutation beside it is the practice working; it
is not the same as having checked the tool.

## The third pass — the same seven, re-run after the corpus that killed them was retired

Run 2026-08-17 for `make-named-by-bodies-scale-with-the-surface-it-was-built-for`, which rewrote
`named_by_bodies` from a regex-per-target-name inner loop to one generic-shape scan per body
followed by set membership. The seven mutations of §The second pass were repeated verbatim against
the rewrite, in **both** modes — `python3 -m unittest discover -s tests -p "test_golden.py"`, which
is `--json` only, and the human `cq --root . components lint` arm.

**Two were killed. Five survived.**

| Mutation | Predicate moved? | `--json` | human |
| --- | --- | --- | --- |
| `description_is_resident` → always `True` | no | survived | survived |
| `description_is_resident` → always `False` | no | survived | survived |
| drop the leading-slash exclusion | yes | **killed** | **killed** (+2/−1 findings) |
| drop the Skill-tool arm | yes | survived | survived |
| drop the registry arm | yes | survived | survived |
| drop the self-reference guard | yes | survived | survived |
| ungate `sk-inert-stage` from the caller set | no | **killed** | **killed** (−11 findings) |

**"Predicate moved?" is the column that makes the result readable**, and it was added because
without it a survivor cannot be told from a no-op edit. It records whether the mutation changed
`named_by_bodies`'s own `dict[str, set[str]]` return over the real 34-command surface. Three
survivors — the two arms and the self-reference guard — **did** change it. The predicate returned
different data and every check in the repo reported the same bytes as before. That is a fixture
gap, not an equivalent mutant in the sense of §What a mutation is worth: an equivalent mutant
cannot be killed by any input, while these three are killed by inputs that used to exist.

**Why they used to exist and no longer do.** The seven were originally killed by the pre-refactor
components tool's own `selftest`, whose corpus was five synthetic cases written to discriminate
exactly these rules — `/docs:typed-only-bare`, `/docs:routed-bare`, `/docs:stage-cited`,
`/docs:stage-handed`, `/docs:stage-inert`. That subcommand was retired and the golden suite
replaced it, and a golden captures the **real** plugin surface. On that surface no command carrying
`disable-model-invocation: true` is reached by name from any body, so `sk-inert-stage` — the only
finding `named_by_bodies` can produce — never fires, and a mutation that merely widens or narrows
the caller set changes nothing anyone can observe. The two that survive without moving the
predicate fail for the sibling reason: the real surface raises neither `sk-no-boundary` nor
`sk-trigger-position`, so flipping the residency gate has no finding to add or remove.

The two kills are the mirror image, and confirm the reading. Dropping the leading-slash exclusion
*adds* a command-like caller to the caller set, which is enough to make `sk-inert-stage` fire where it did
not; ungating `sk-inert-stage` fires it for every `disable-model-invocation` command outright. Both
push the real surface across a threshold. Nothing that stays on this side of it is observable.

**What this pass proves about the rewrite is therefore nothing, and the rewrite was proved another
way** — worth stating because a green suite beside a rewrite reads like evidence. Equivalence was
established directly instead: the pre-change `named_by_bodies` was loaded from
`git show <base>:…lint.py` into a separate module and its return compared with `==` against the new
one over the real corpus and over a 10× synthetic copy. Identical on both. That comparison, not
this pass, is what holds the semantics.

**This is the failure mode of §Graduation gate arriving on schedule.** That section already said
the historical passes "remain here as the record of the practice … not as coverage of code that no
longer ships". This pass is the first to *measure* the consequence: re-running a retired pass
against the suite that replaced it grades the suite, and the suite has no witness for five of the
seven rules. Closing that needs a fixture that discriminates them — the successor to those five
synthetic cases — which no test file in `tests/` currently carries.

## The fourth pass — the same seven again, over the fixture that replaces the retired corpus

Run 2026-08-27, closing the gap §The third pass measured. `tests/test_lint_inert_stage.py` is the
successor to the five synthetic `/docs:*` cases: a five-command corpus built to sit ON the
threshold the real surface stays clear of, where each arm of `named_by_bodies` and each direction
of the residency gate is observable alone. The seven mutations were repeated verbatim against the
same rewrite, in both modes — `python3 -m unittest discover -s tests` and the human
`cq --root . components lint` arm.

**Seven killed, none survived.**

| Mutation | Suite | Human arm |
| --- | --- | --- |
| `description_is_resident` → always `True` | **killed** | +1 finding |
| `description_is_resident` → always `False` | **killed** | unchanged |
| drop the leading-slash exclusion | **killed** | +1 finding, exit 1 |
| drop the Skill-tool arm | **killed** | unchanged |
| drop the registry arm | **killed** | unchanged |
| drop the self-reference guard | **killed** | unchanged |
| ungate `sk-inert-stage` from the caller set | **killed** | −6 findings, exit 1 |

**Four of the seven still move nothing on the real surface** — the human column is the same six
findings — which is the third pass's finding restated, not withdrawn: the real corpus cannot
witness these rules, and a fixture is the only thing that can. What changed is that the suite now
carries one.

**The pass found a defect in the fixture, not in the code, and that is the result worth keeping.**
The first draft wrapped its registry citation onto a line under a "Skill tool" mention, and
`SKILL_TOOL_WINDOW` reads a line together with its neighbours — so both arms answered for the same
name and `drop the registry arm` survived a suite that was otherwise green. A fixture where two
rules cover for each other reads exactly like one where each is witnessed. Only the mutation
separated them; the assertion count did not change between the two drafts.

## Where this sits

This is the authoring-time complement to the two verification gates already written:
[bundle-verification.md](bundle-verification.md) decides *which invariants are owed a deterministic
check at all*, and [surface-verification.md](surface-verification.md) covers what only a fresh
process can prove. This standard governs neither of those — it asks the narrower question of
whether a check that exists is load-bearing.

It shares a premise with [parse-honesty.md](parse-honesty.md): both refuse to let a tool's silence
read as a clean result. There, a parse failure is named rather than reported as a content gap; here,
a test that cannot fail is named rather than counted as coverage.

**The repo now has a test framework, and the failure mode this standard names already found it
once.** `python3 -m unittest discover -s tests` replaced the four `selftest` subcommands the
passes below were run against; `test_suite.py`'s `test_discovery_is_not_empty` exists specifically
because a `-k` selector that collects zero cases exits 0 and reads exactly like a pass — which is
what this repo's own `-k backend` / `-k parse` / `-k command` / `-k config` `verify:` lines did
across several tasks before the suite existed to catch it, discovered only by comparing against an
independent proof (a byte-identical move, a side-by-side comparison against the tool being
extracted). The failure this standard exists to name is not hypothetical here — it already
happened, more than once, in this repo's own build.

## Graduation gate

`authority: background`, and the gate is explicit. Two properties of the suite itself are
mutation-proved by construction: `test_no_external_imports` is checked with a negative control (a
planted `import requests` fails it), and `test_discovery_is_not_empty` is what the empty-collection
failure mode above is now asserted against. Individual test files carry their own measured
negative controls where a false-green was found — `test_specs_assets.py`'s `ASSET_DIR`-pointed-at-
nothing case (1 failure + 3 errors, zero skips), the golden suite's `declock()` neutralising a
time-derived field — but no systematic mutation pass has been run **rule by rule** across the
whole suite the way the historical passes below covered the pre-refactor session and components tools' selftests.

Three passes exist against the retired selftests: the pre-refactor session tool's whole selftest (four mutations,
2026-07-29), the pre-refactor components tool's **newest rules only** (seven, 2026-08-02), and its
`--sections` ladder (three, 2026-08-05 — two killed, one equivalent). They remain here as the
record of the practice and as fixtures the new suite's own `tests/test_*.py` equivalents should be
held to the same way, not as coverage of code that no longer ships.

A fourth ran against `tests/` itself (§The third pass, seven mutations, 2026-08-17 — two killed,
five survived) and is the first measurement of how far short the replacement falls: five of the
seven rules the retired selftest discriminated have no witness in the suite that succeeded it. It
moves the gate no closer, and it names precisely what closing it would cost.

A fifth paid that cost for those seven rules alone (§The fourth pass, 2026-08-27 — seven killed,
none survived, over the new `tests/test_lint_inert_stage.py`). It closes the hole the fourth
measured and **still does not move this gate**: the rules now witnessed are the routing and
`named_by_bodies` rules of one module, and the gate asks for a pass rule by rule across the whole
suite. Reading a fixture that covers seven rules as coverage of the suite is the arithmetic this
section exists to refuse.

This becomes `authority: current` when a pass of the shape above has been run, rule by rule,
against `tests/`'s own corpus and the result recorded — not before. Booking partial coverage as
though it closes the gap is the same dishonesty the standard asks its own mutations to refuse.
