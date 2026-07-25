# The sweep contract — shared by every align

The plugin has **three** aligns, one per front: `quenching-docs-align` (`docs/`), `quenching-specs-align`
(`specs/`), and `quenching-skill-align` (`.claude/`). They converge different artifacts, but
they are the *same kind of operation* — a read-only inventory, ONE plan, one OK, apply, verify —
and everything about **how** that operation behaves is identical across the three. So it lives
here, once, and each align cites this file instead of restating it. Only a front's own deltas
(what it inventories, which findings it produces, what its verifier is) stay in its `SKILL.md`
and its own `references/`.

This is the sweep-side peer of
[`../../quenching-align-and-update-all/references/convergence.md`](../../quenching-align-and-update-all/references/convergence.md),
which owns the conductor side (authorization, convergence, anti-spin). Where the two touch —
a cycle-authorized run — this file defers to that one.

## 1. Convergence, not accommodation

Every aligned repo ends with the **same shape**. A variant the repo happens to use —
`docs/arquitetura/`, a change folder named `AddAuth/`, a skill called `helper2` — is a
**non-convergence smell**: a migration candidate, never a local convention to preserve. The
plugin's names win, because the whole value of the three fronts is that a human or an agent
landing in any adopting repo finds the same tree.

The counterweight is **evidence-gating**, not tolerance: a front only scaffolds what the repo
gives it grounds to scaffold (a repo with no data gets no `catalog/`), and what cannot be
grounded is a **recorded deferral**, never a silent skip and never an invention.

## 2. Force with ONE confirmation

Present the **complete** plan; a single OK executes the whole batch. Partial adjustments →
re-plan and re-present. A rejected plan applies **nothing** — not the uncontroversial parts,
not "just the safe ones".

**Exception — code-coupled items.** Any rename or edit whose blast radius reaches **product
code** (a path constant, an import, a docstring, a branch name, a CI job, a script) is a
**distinct** confirmation item, with its scope shown, and is **never** folded into the batch OK.

**Exception — cycle-authorized runs.** Invoked by a conductor under the cycle-authorization
contract
([convergence.md](../../quenching-align-and-update-all/references/convergence.md)
§cycle-authorization), the plan is presented as **narration, not a gate**. The narration is not
optional — the user watching the session still sees the full plan table and simply types
nothing. A code-coupled item still confirms on its own, **always**; no authorization from any
conductor ever absorbs one.

## 3. The blast-radius sweep

Before any rename enters the plan, its blast radius is known. The procedure is the same on all
three fronts:

**Two repo scans total, never two per rename.** Build ONE alternation of every planned old name
and run it twice — `git grep -n -E "(name-a|name-b|name-c)"` for tracked files, and
`grep -rn --no-ignore -E "(name-a|name-b|name-c)"` so gitignored surfaces are never skipped. The
matched text attributes each hit back to its rename, so a set of k renames costs **2** scans, not
2k. Quote for the shell; escape regex metacharacters in a slug.

**Classify each hit yourself.** A hit **inside** the front being aligned is workspace-internal
and rides the batch OK; a hit **outside** it makes that rename code-coupled per §2. This
judgment is never delegated — only the mechanical bucketing of a large hit list may go to one
read-only `Task` sub-agent (`model: haiku`, `effort: low`) returning `rename → [file:line, …]`,
and only **after** the two scans have already run. A sub-agent that re-runs the scanning has
saved nothing.

**A name with no hits is still renamed** — the sweep converges names, and an unreferenced
variant is the easiest case, not an exemption.

## 4. MERGE, never clobber; never delete on a guess

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

## 5. Align conformance; report the cycle

A sweep fixes **structure**. It does not make the decisions that structure exists to serve.

A complete-but-unarchived change, a stale change, an untriaged task, a coverage deferral, a
skill nobody has said is obsolete — these are **cycle actions**, not conformance defects, and
each is reported with the skill that owns it. The sweep never archives, never ranks, never
proposes, never abandons.

This is the plugin's **anti-fabrication boundary**, and it is why the aligns are safe to run on
a repo nobody has read: a sweep closes only what it can close deterministically from what the
repo already contains. Everything requiring a human to state something new is **surfaced**.

## 6. End honest

Every align ends with its front's own verifier, then a report that names what it did **and** what
it deliberately did not close, each with the command that closes it. Residue reported plainly
beats a clean-looking run that quietly dropped something.

| Front | Align | Verifier |
| --- | --- | --- |
| `docs/` | `quenching-docs-align` | `okf-validate.py <docs-dir>` — exit 0 **and** no `dir-no-index` / `index-broken-link` / `index-orphan` (they are WARN; read the findings) |
| `specs/` | `quenching-specs-align` | `specs.py doctor` + `specs.py validate`, plus `okf-validate.py specs/backlog --listing-root` for the inbox |
| `.claude/` | `quenching-skill-align` | the registry's GENERATED zone matching `.claude/skills/` exactly, and every wrapper resolving |
