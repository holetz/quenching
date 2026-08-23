---
name: quenching-knowledge-status
description: "Read the whole `docs` front and report where the OKF bundle stands — writes nothing. Triggers on \"what's the status of the docs\", \"how healthy is the knowledge base\", \"is the bundle conformant\"."
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/status.md -->


# quenching-knowledge-status — read the bundle, change nothing

**Input**: `$ARGUMENTS` (optionally a home or path to focus; omit to read the whole bundle).

The **read-only** view of the `docs` front. Every other skill here either fixes something
(`quenching-knowledge-align`) or acts on one
item a human named. This one only looks — and because it looks at exactly what those sweeps look
at, it is also their honest preview: the plan you would be authorizing, before you authorize it.

It exists because structural conformance is compatible with a knowledge base that knows nothing.
`cq knowledge validate` can return exit 0 on a bundle of empty homes and a placeholder glossary, and
until this skill there was no way to learn what `quenching-knowledge-align` would do except to invoke the
invasive skill and read the plan from inside it.

The conformance codes and their severities live in
[knowledge-align/conformance.md](../../references/knowledge-align/conformance.md);
the finding → owning-command routing in
[knowledge-align/cycle.md](../../references/knowledge-align/cycle.md);
the homes and the insert procedure in
[knowledge-add/homes.md](../../references/knowledge-add/homes.md).
All three are **cited, never restated** — this skill owns no contract of its own, which is the
point: a status view that disagreed with the sweep would be worse than none.

## Doctrine

- **Zero writes, no exceptions.** No stamp, no index regeneration, not even a marker file. A
  status read that changed the thing it read would break its own contract and make the preview
  a lie.
- **Report in the validator's vocabulary.** Every finding carries the code
  [conformance.md](../../references/knowledge-align/conformance.md) defines and the command that
  closes it. Never invent a code, never soften one, and never report a finding the sweep would not
  raise — the value is that the two agree.
- **Density is reported, never coded as a finding.** Empty homes, thin homes, and a one-entry
  glossary appear as a **table of figures with no code**. Reporting every empty home as a defect
  is permanent noise in a repo that legitimately has no `mlops/`; not reporting it loses the
  signal that motivated the skill. Figures inform; codes accumulate.
- **Distinguish "would fix" from "would only report".** Split the output the way the sweeps split
  it: what `quenching-knowledge-align` fixes on one OK, what its later stages then drive, and what neither
  closes because it needs a human. A reader must be able to tell what a sweep would
  actually do to their repo.
- **Cheap by construction.** One `cq knowledge validate --json` over the bundle, one glob, and reads of
  the few files the report names. Never fan out sub-agents: the validator already answers in one
  call what a sub-agent would be sent to re-derive.
- **Never judge, never rank, never infer.** An empty home is not a defect, an unlinked glossary
  entry is a valid permanent state, and `stale-doc` is an advisory age — never a verdict that a
  doc is wrong.

## Workflow (one read, one report)

### 1. Resolve the bundle
Resolve the bundle at its fixed root `/.knowledge/` at the repo root — the root is never read from
config. Resolve `cq knowledge` per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool. Invoke via `python3`/`py`; branch on the **exit code** and the `--json`,
never on prose.

**No bundle at all** is a complete, valid answer: report that `/.knowledge/` is absent and that
`quenching-knowledge-align` would install it, then stop. A `/.knowledge/` that exists without an `okf_version` root
`index.md` is an un-installed tree, not a broken bundle — say which.
**Done when:** the bundle root and the checker are resolved, or their absence recorded.

### 2. Collect (read-only)
- `cq knowledge validate /.knowledge --json` — every conformance finding, with `stale-doc` included, since
  this is CLI mode (per [conformance.md](../../references/knowledge-align/conformance.md)
  §Staleness, it never runs in the hook path).
- `Glob` `/.knowledge/**/*.md` for the density counts, and read `/.knowledge/index.md`, each home's `index.md`,
  and `/.knowledge/glossary.md`.
- `Glob` `~/.codex/projects/<cwd>/memory/*.md` and read the root `AGENTS.md`/`AGENTS.md` size —
  the two out-of-band stores whose content the cycle would pull in.
- Note whether a **retired `log.md`** is still present anywhere in the bundle (`Glob`
  `/.knowledge/**/log.md`) — a figure for §5, never a finding.

Nothing here writes. If the checker is unavailable, collect what the frontmatter supports and mark
every conformance row as unverified rather than reporting a clean bundle.
**Done when:** every source is read and nothing has been written.

### 3. Classify against the sweeps' own codes
Map each finding onto a code from
[conformance.md](../../references/knowledge-align/conformance.md), and route it with
[cycle.md](../../references/knowledge-align/cycle.md)'s routing table — which
already says, per row, whether the align auto-closes it. Contribute no code and no routing of your
own: a row the table does not cover is reported under "closed by neither" with the reason, never
invented into a fix.

Keep the severity split the contract draws: the **must-fix** WARNs (`dir-no-index`,
`index-broken-link`, `index-orphan`, `glossary-broken-link`, `resource-unresolved`,
`resource-self`) are what a verify gate blocks on; **`stale-doc` is advisory and blocks nothing**,
so it is never reported as though it did.
**Done when:** every observation carries a code and a routing.

### 4. Report
One report, in this order:

1. **Header** — the resolved bundle root, whether it is an installed OKF bundle (`okf_version` on
   the root `index.md`), and the checker's version and exit code verbatim.
2. **Density** — the table §5 defines. It comes *before* the findings, because a bundle with no
   findings and no content is the case this skill exists to make visible.
3. **Would be fixed by `quenching-knowledge-align`** — the codes
   [cycle.md](../../references/knowledge-align/cycle.md)'s table marks auto-closed by
   stage 1 (`dir-no-index`, `index-broken-link`, `index-orphan`, un-stamped or mis-stamped
   frontmatter, variant folder names, prefix-clusters, non-English slugs), with counts. Name which
   would be **code-coupled** — a rename whose blast radius reaches product code — and so would
   confirm on its own. State plainly that this list is what a single OK would authorize.
4. **Would then be pulled in by `quenching-knowledge-align`'s later stages** — the content they carry: undrained `~/.claude` memory files (count), durable knowledge still inlined in the harness,
   and terms in the bundle absent from the glossary. These are the rows the table marks auto-closed
   by `quenching-knowledge-import-memory`, `quenching-components-harness-align` and
   `quenching-knowledge-glossary-backfill`.
5. **Closed by neither** — every row the table marks **No**, each with the command that closes it:
   `resource-unresolved` and `resource-self` (→ `quenching-knowledge-add` to restamp, because only a
   human knows what a doc now governs), `glossary-broken-link` (→ `quenching-knowledge-define`, since
   the backfill stage adds missing terms and never prunes a dead one), `stale-doc` (advisory, with
   its age), coverage-ledger deferrals, and anything a human has not yet stated. Say plainly that
   `stale-doc` gates nothing, so a reader never mistakes an advisory for a blocker.

Close with the single most useful next command for this repo's actual state, and nothing else — no
plan, no offer to fix, no "shall I". A status read ends by handing control back.

**A section with nothing in it is reported as empty, never omitted** — "`quenching-knowledge-align` would change
nothing" is the most valuable line this skill can print, and dropping the heading hides it.
**Done when:** all five sections are reported and no file has changed.

### 5. The density table — figures, not findings

Conformance says the bundle is *well-formed*. Density says whether it *knows anything*. A bundle
can pass every check while holding six scaffolded homes, five concept docs and a placeholder
glossary — the exact state that motivated this skill — and nothing in the front reported it.

Report it as one table, and give **no row a finding code**:

| Figure | How it is counted |
| --- | --- |
| Concept docs, total | `.md` files that are not `index.md`, `log.md`, or an EXEMPT basename (`AGENTS.md`, `AGENTS.md`) |
| Concept docs **per home** | the same count, grouped by top-level home, with **installed-but-empty homes shown as `0`** — never omitted, since the zero is the signal |
| Glossary terms | entries under `## Terms` in `glossary.md`; note separately when the shipped **seed placeholder** is still the only one |
| Unlinked glossary entries | terms with no concept doc yet — a **valid permanent state**, reported as a figure and never as a defect |
| Standards subjects | subject subfolders under `standards/`, and how many hold at least one doc |
| Last activity | the newest `timestamp:` across the bundle's concept docs |
| Retired `log.md` | how many survive, and where — see below |

**A surviving `log.md` is a figure, not a defect.** The artifact is retired: nothing writes one,
the validator emits no code for one, and `quenching-knowledge-align` neither creates nor deletes one. Report
that it is there, say it is retired and that keeping or deleting it is the repo's call, and stop
— inventing a code for it here would make this command disagree with the sweep, which is the one
thing it must never do. It has no owning command to name, because none of them want it.

Two rules keep this honest:

- **No figure is ever a finding.** Reporting every empty home as a defect is permanent noise in a
  repo that legitimately has no `mlops/`; not reporting it loses the signal. A figure informs
  without accumulating as something to chase. If a reader asks which empty homes *should* be
  filled, that is a judgement for a human with repo knowledge, not a row this skill emits.
- **Never infer a target.** There is no correct number of concept docs, no minimum glossary size,
  and no ratio to hit. Report the counts and stop; a bundle with four docs may be complete.

**Done when:** the table is reported with every home present, zeros included, and no row carries a
code.

## Invariants to never violate

- Never write, anywhere, for any reason — not a stamp, not an index, not a marker. If something
  looks wrong enough to fix, name the command that fixes it and stop.
- Never report a finding with a code the validator does not define, and never state a finding the
  sweep would not raise.
- Never give a density figure a finding code, and never present an empty home as a defect.
- Never call `stale-doc` a violation, and never fold it into the must-fix set — it is advisory,
  and a bundle carrying one is still aligned.
- Never report a bundle as conformant on a run where the checker could not be resolved.
- Never fan out sub-agents, and never hand this command file `context: fork` when it is invoked as a
  sweep's preview — the report has to land in the conversation where the OK will be given.
