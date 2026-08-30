---
type: standard
title: Empty-response honesty
description: An empty response from a third-party transport is two states — one that never arrived and one that legitimately has nothing — and only one of them can be proved; the rule to refuse at the choke point where the proof is structural, to warn where there is only corroborated suspicion, and to never let the diagnostic refuse
resource: plugins/quenching/assets/bin/quenching/specs/backends/**, plugins/quenching/assets/bin/quenching/specs/commands/doctor.py
tags: [quality, verification, backends, findings, severity, transport]
timestamp: 2026-08-17
audience: both
authority: current
source: spec falha-de-leitura-do-backend-vira-front-vazio (tasks 1.1-3.2) — proved by the guards in github.py and by the tests in test_specs_backends.py and test_specs_doctor.py
maintainer: quenching
---

# Empty-response honesty

**A third-party process that exits 0 and returns nothing did not say "there is nothing" — it said
nothing.** The two sentences are indistinguishable to whoever reads the return value, and it is that
indistinction that turns a transport failure into a fact: the listing comes back empty, the command
answers `{"ok": true, "count": 0}` with exit 0, and every downstream consumer concludes the front is
empty.

This contract is the sibling of [parse-honesty.md](parse-honesty.md), one level below. That one
governs a **lossy transform** inside the process; this one governs the **payload that arrived** from
outside it. Neither reaches the other: a parser that is honest about what it read may still be
reading an empty that never happened.

## The rule

> A reader that accepts an empty payload from an external process MUST separate the shape that
> **proves** a failure from the shape that merely **suggests** one, and treat the two differently:
> a refusal with exit 2 where there is proof, a `warn` finding plus one line on `stderr` where there
> is suspicion, and never silence for either.

Three consequences, in the order they bind.

### 1. The proof is structural, and it comes from a versioned measurement

The separation exists only where the transport has a shape a legitimate response never takes.
Measured on `gh 2.97.0 (2026-07-31)`, `gh api --paginate --slurp` over an issue listing:

| What comes back | What it is | What to do |
| --- | --- | --- |
| `None` — exited 0 and printed nothing | a response that **never arrived** | refuse, exit 2 |
| `[]` — zero pages | a response that **never happened** | refuse, exit 2 |
| `[[]]` — one page, empty | a genuinely empty front | proceed |
| `[[…], […]]` | healthy | proceed |

`[[]]` versus `[]` is the entire discriminant, and it is a property of `gh`'s `--slurp`, not of the
API. That is why the **measured version travels inside the refusal's message**: a future `gh` that
changes the shape has to break legibly, and not in silence.

**Where there is no structural discriminant, there is no refusal.** `azure.py` already wrote that
half for its own transport: in a WIQL query, zero matches and a macro that did not resolve are
byte-identical — exit 0, empty stdout, empty stderr — so refusing on empty there would refuse the
ordinary "there are no specs yet" case as often as it would catch the failure. Inventing a
discriminant the measurement does not support is worse than having none.

### 2. The guard belongs to the CALLER, never to the shared transport

The function that runs the process is shared by reads and writes, and an empty response is the
**right** response for some of them: a DELETE whose legitimate response is 204 No Content prints
nothing, and `null` there is correct. A guard on empty stdout inside the executor would break that
call silently — and the executor is exactly the obvious place someone would put it.

**Only the caller knows which shape it asked for.** It asserts that shape at the choke point every
read passes through, which makes every verb inherit the guard for free — including a verb written
tomorrow, whose author need not know the rule exists. It is the same shape
[`code/root-override-validation.md`](../code/root-override-validation.md) §One refusal idiom, one
message, two call sites already fixes: **message and remedy written once beside the predicate, and
cited** by each call site, never drafted again.

### 3. The suspicion is said out loud, in both placements, and the diagnostic completes

The shape that cannot be proved still deserves to be said, because staying silent about it is the
original defect reappearing one step further on. It needs **corroboration that costs no new round
trip** — a number the same call already paid for. With no corroboration available, there is no
warning: an absent counter is never read as zero.

The two placements are the ones in
[`unproven-capability-warning.md`](unproven-capability-warning.md) §Two placements, and **both ship
or the answer is incomplete**: a `warn` finding in the front's own verifier, and one line on
`stderr`, once per process. `stderr` and never `stdout` — every caller branches on the `--json`
payload, and a warning printed into it breaks the parse it exists to inform.

**The gloss "the line lands on the writes and never on the reads", from that same standard, does not
apply here, and the exception is declared rather than assumed.** It is justified there because "a
read of an unproven backend loses nothing — it returns wrong data or a refusal, and both are visible
immediately". In an empty read the wrong data is precisely what is **not** visible: it reads as a
fact. The underlying rule does not change — the line lands where the loss would happen; here that is
the read.

**The verifier never refuses.** The same evidence that is exit 2 at the read choke point becomes a
finding in `doctor`, with the refusal's own message and remedy cited rather than recomposed. That
holds even for refusals that have nothing to do with emptiness: a 503 in the middle of the
diagnostic also becomes a finding, because a diagnostic that aborts is exactly what you cannot have
at the moment somebody went to ask what is wrong.

## Not applicable is not skipped

The same honesty applies when a conducted workflow reports a front with no work. **Not applicable**
means its applicability probe found neither a declared root nor the conventional signal that would
invite adoption; report that state with the one-line invitation to declare the front. **Skipped**
means the front was in scope but the request explicitly excluded it, or an earlier dependency
failure prevented reaching it; report the reason. A present front that probes clean is neither: it
is **conformant**. Never use *skipped* to hide an absent front, and never turn *not applicable* into
a plan item.

**The suspicion's severity is `warn`, and the reason is the one in
[parse-honesty.md](parse-honesty.md) §Severity: warn, and why not error**: a repository that adopted
the backend over an existing tracker and has not created a single spec yet **is** that state,
exactly, and it is legitimate. Erroring there would fail conformant repositories.

## The wording is the discriminant the code does not have

Narrowing the trigger does not separate the two states — they are the same observation. What
separates them is the warning **stating the number and the expected reading**, so that whoever is in
the legitimate state recognises themselves in it: *"N open issues and not one of them carries a spec
marker; if no spec has been created here yet, this is expected"*. A warning that does not say that
teaches its reader to ignore it, and an ignored warning is the same thing as silence.

## The test proves the branch; the premise is measured

A test that mocks the transport into returning empty stdout proves the guard exists — and does
**not** prove that a healthy response never comes out that way. That premise is a measurement, with
a date and a version, and it lives in the spec's `## Validation` as a manual command, never as a
suite assertion. [`selftest-mutation.md`](selftest-mutation.md) §The rule closes the pair: break the
guard and watch the test fail, one mutation per rule, reverted afterwards.

## Where this applies

Any reader in this repository that accepts a payload from a third-party process whose exit code does
not distinguish "empty" from "did not answer" — the `github` and `azure-boards` backends today, and
any transport a future backend adds. It does **not** apply to a read whose empty response is
unambiguous: an empty directory under the `files` backend has no process and no exit code to
interpret, and there empty means empty.
