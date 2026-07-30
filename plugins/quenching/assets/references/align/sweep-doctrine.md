# The sweep contract — shared by every align

The plugin has **three** aligns, one per front: `/docs:align` (`docs/`), `/specs:align`
(`specs/`), and `/skill:align` (`.claude/`) — plus `/align`, which conducts all three. They
converge different artifacts, but they are the *same kind of operation* — a probe, a read-only
inventory, ONE plan, one OK, apply, verify — and everything about **how** that operation behaves is
identical across them. So it lives here, once, and each align cites this file instead of restating
it. Only a front's own deltas (what it inventories, which findings it produces, what its verifier
is) stay in its command body and its own `references/`.

This file is **self-contained**: an align reads it and needs nothing else. Its conductor-side
peer — authorization across a whole run, convergence to a fixpoint, the anti-spin guards — is its
sibling
[`convergence.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md), and the one
place the two touch (a cycle-authorized run) is stated here in full at §3 rather than deferred. A
reference that sends a reader to another reference makes the second one mandatory, which is the
opposite of what the loading hierarchy is for.

## Contents

- [1. Probe before the inventory](#1-probe-before-the-inventory)
- [2. Convergence, not accommodation](#2-convergence-not-accommodation)
- [3. Force with ONE confirmation](#3-force-with-one-confirmation)
- [4. The blast-radius sweep](#4-the-blast-radius-sweep)
- [5. MERGE, never clobber; never delete on a guess](#5-merge-never-clobber-never-delete-on-a-guess)
- [6. Align conformance; report the cycle](#6-align-conformance-report-the-cycle)
- [7. End honest](#7-end-honest)

## 1. Probe before the inventory

**Nothing is inventoried until the front's own verifier has said there is work.** Every align opens
by running the programs in §7's table — the same ones it will close with — and branches on their
exit codes before reading anything else:

| Probe result | What the align does |
| --- | --- |
| exit 0, no findings at all | **STOP.** Report "`<front>` conformant, N items, nothing to align" and end. No inventory, no plan, no confirmation. |
| exit 0, findings are all ones the front only **reports** (§6) | STOP the same way, then list them with the command that closes each. Structure is conformant; the residue is the cycle's. |
| exit 1 or 2 | Run the full inventory and continue. |

The probe and the final verification are the **same programs run twice** — which is why this costs
a couple of tool calls rather than a second contract to maintain. An align that applied anything
re-runs them afterwards and reports what they say (§7); the probe never substitutes for that.

**This is load-bearing, not an optimization.** An align that is expensive on a clean repo is an
align nobody runs as the repo grows — which is exactly when drift accumulates. Making the no-op
case cost a couple of tool calls is what permits an align to carry its front's content stages at
all, instead of those stages needing a separate command nobody invokes.

It also inverts the order these sweeps used to run in, where a full read-only inventory was paid
for before anything knew whether there was work — even though the verifier reads the same files and
already answers the question with an exit code.

**A stage the probe cannot price is offered, never run to find out.** Some content work has no
cheap signal — a whole-bundle glossary sweep is the standing example. Such a stage is gated on a
proxy the align can read for free (a count against a count) and **offered** with what it would
cost, never entered automatically. Guessing costs the user the very expense this section exists to
avoid.

## 2. Convergence, not accommodation

Every aligned repo ends with the **same shape**. A variant the repo happens to use —
`docs/arquitetura/`, a change folder named `AddAuth/`, a skill called `helper2` — is a
**non-convergence smell**: a migration candidate, never a local convention to preserve. The
plugin's names win, because the whole value of the three fronts is that a human or an agent
landing in any adopting repo finds the same tree.

The counterweight is **evidence-gating**, not tolerance: a front only scaffolds what the repo
gives it grounds to scaffold (a repo with no data gets no `catalog/`), and what cannot be
grounded is a **recorded deferral**, never a silent skip and never an invention.

## 3. Force with ONE confirmation

Present the **complete** plan; a single OK executes the whole batch. Partial adjustments →
re-plan and re-present. A rejected plan applies **nothing** — not the uncontroversial parts,
not "just the safe ones".

**Exception — code-coupled items.** Any rename or edit whose blast radius reaches **product
code** (a path constant, an import, a docstring, a branch name, a CI job, a script) is a
**distinct** confirmation item, with its scope shown, and is **never** folded into the batch OK.

**Exception — cycle-authorized runs.** When a conductor invokes this align as a stage, the human
already gave ONE confirmation at run start that authorizes the whole run. The align's own plan is
then presented as **narration, not a gate**: the narration is not optional — the user watching the
session still sees the full plan table and simply types nothing.

That authorization covers every routine write a stage performs — frontmatter stamps, new concept
docs, index/log/glossary entries, routine renames, variant migrations and the deletions they
require, structural repairs — **as long as it touches no product code**. It covers nothing else.
Two classes still gate individually, exactly as when the align runs standalone, and after the
run-start OK they are the only possible stops:

1. **Code-coupled items** — the exception above, unchanged. No authorization from any conductor
   ever absorbs one.
2. **Irreversible cycle actions** — an action that discards or relocates a record of work rather
   than reshaping it (archiving a plan, removing a captured spec). An align never performs one; it
   reports them (§6), and the conductor gates each on its own.

## 4. The blast-radius sweep

Before any rename enters the plan, its blast radius is known. The procedure is the same on all
three fronts:

**Two repo scans total, never two per rename.** Build ONE alternation of every planned old name
and run it twice — `git grep -n -E "(name-a|name-b|name-c)"` for tracked files, and
`grep -rn --no-ignore -E "(name-a|name-b|name-c)"` so gitignored surfaces are never skipped. The
matched text attributes each hit back to its rename, so a set of k renames costs **2** scans, not
2k. Quote for the shell; escape regex metacharacters in a slug.

**Classify each hit yourself.** A hit **inside** the front being aligned is workspace-internal
and rides the batch OK; a hit **outside** it makes that rename code-coupled per §3. This
judgment is never delegated — only the mechanical bucketing of a large hit list may go to one
read-only `Task` sub-agent (`model: haiku`, `effort: low`) returning `rename → [file:line, …]`,
and only **after** the two scans have already run. A sub-agent that re-runs the scanning has
saved nothing.

**A name with no hits is still renamed** — the sweep converges names, and an unreferenced
variant is the easiest case, not an exemption.

## 5. MERGE, never clobber; never delete on a guess

- **Stamps and frontmatter MERGE.** Fill what is missing; preserve what is filled, including
  third-party keys the plugin does not own (a legacy `status:`, a site generator's field, an
  OKF consumer's extension).
- **Bodies are preserved.** A sweep changes names, placement, listings, and conformance
  metadata. Authored prose is not a sweep's to rewrite.
- **Deletion needs a human's word.** A file the sweep believes is obsolete, superseded, or a
  duplicate is **kept and reported** with the observed reason. The only deletions a sweep
  performs unasked are the ones a *migration it is already applying* requires — moving a file
  leaves no copy behind.
- **Anything unclassifiable is kept and reported.** An unroutable item is a finding, never a
  reason to guess a destination.

## 6. Align conformance; report the cycle

A sweep fixes **structure**. It does not make the decisions that structure exists to serve.

A complete-but-unarchived change, a stale change, an untriaged task, a coverage deferral, a
skill nobody has said is obsolete — these are **cycle actions**, not conformance defects, and
each is reported with the skill that owns it. The sweep never archives, never ranks, never
proposes, never abandons.

This is the plugin's **anti-fabrication boundary**, and it is why the aligns are safe to run on
a repo nobody has read: a sweep closes only what it can close deterministically from what the
repo already contains. Everything requiring a human to state something new is **surfaced**.

## 7. End honest

Every align ends with its front's own verifier, then a report that names what it did **and** what
it deliberately did not close, each with the command that closes it. Residue reported plainly
beats a clean-looking run that quietly dropped something.

| Front | Align | Verifier |
| --- | --- | --- |
| `docs/` | `/docs:align` | `okf-validate.py <docs-dir>` — exit 0 **and** no `dir-no-index` / `index-broken-link` / `index-orphan` (they are WARN; read the findings) |
| `specs/` | `/specs:align` | `specs.py doctor` + `specs.py validate` — the whole condition; the OKF validator is never pointed at `specs/` |
| `.claude/` | `/skill:align` | `skills.py lint` + `skills.py doctor`, plus `skills.py registry reindex` reporting `changed: false` for the zone |

Each front's verifier is now a **program**, and that is the point: a rule whose only check is a
sentence decays, because nothing fails when it is broken. All three read the same contract —
`--json` on every subcommand and exit **0** ok · **1** findings · **2** refusal — so an align
branches on data it did not have to interpret. Warnings are reported and never set the exit code;
an align that ends on exit 0 with warnings names each one by its code rather than implying the
front is clean.