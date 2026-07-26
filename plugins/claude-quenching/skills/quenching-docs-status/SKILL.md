---
name: quenching-docs-status
description: >-
  Reads the WHOLE docs/ front and reports where the OKF bundle stands — every conformance finding
  in the validator's own codes, plus the bundle's DENSITY (homes scaffolded vs. empty, concept
  docs per home, glossary term count) — writing absolutely nothing. Use when the user asks "what's
  the status of the docs", "how healthy is the knowledge base", "show me the docs dashboard",
  "what would /docs:align do", "is the bundle conformant", "is the glossary keeping up", or asks
  for a preview before authorizing a sweep. Every finding carries the same code `okf-validate.py`
  produces and the command that closes it, so the report doubles as an honest dry run of
  /docs:align and /docs:align-and-update — with none of their writes. Density figures carry NO
  finding code, so an empty bundle stops reading as a healthy one. Not for: fixing what it finds →
  quenching-docs-align; pulling content in and looping → quenching-docs-align-and-update; the
  specs/ front → quenching-specs-status.
when_to_use: >-
  answering "where does the docs front stand" without writing anything, and previewing what a
  sweep would do before authorizing it. Fixing structure is quenching-docs-align; pulling content
  in and looping is quenching-docs-align-and-update.
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*)
user-invocable: false
effort: low
---

# quenching-docs-status — read the bundle, change nothing

The **read-only** view of the `docs/` front. Every other skill here either fixes something
(`quenching-docs-align`), drives something (`quenching-docs-align-and-update`), or acts on one
item a human named. This one only looks — and because it looks at exactly what those sweeps look
at, it is also their honest preview: the plan you would be authorizing, before you authorize it.

It exists because structural conformance is compatible with a knowledge base that knows nothing.
`okf-validate.py` can return exit 0 on a bundle of empty homes and a placeholder glossary, and
until this skill there was no way to learn what `/docs:align` would do except to invoke the
invasive skill and read the plan from inside it.

The conformance codes and their severities live in
[../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md);
the opportunity → skill routing in
[../quenching-docs-align-and-update/references/cycle.md](../quenching-docs-align-and-update/references/cycle.md);
the homes and the insert procedure in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md).
All three are **cited, never restated** — this skill owns no contract of its own, which is the
point: a status view that disagreed with the sweep would be worse than none.

## Doctrine

- **Zero writes, no exceptions.** No stamp, no index regeneration, no `docs/log.md` entry, not
  even a marker file. A status read that changed the thing it read would break its own contract
  and make the preview a lie. The `allowed-tools` above carry no `Write` or `Edit` — that is the
  enforcement, not a promise.
- **Report in the validator's vocabulary.** Every finding carries the code
  [conformance.md](../quenching-docs-align/references/conformance.md) defines and the command that
  closes it. Never invent a code, never soften one, and never report a finding the sweep would not
  raise — the value is that the two agree.
- **Density is reported, never coded as a finding.** Empty homes, thin homes, and a one-entry
  glossary appear as a **table of figures with no code**. Reporting every empty home as a defect
  is permanent noise in a repo that legitimately has no `mlops/`; not reporting it loses the
  signal that motivated the skill. Figures inform; codes accumulate.
- **Distinguish "would fix" from "would only report".** Split the output the way the sweeps split
  it: what `/docs:align` fixes on one OK, what `/docs:align-and-update` then drives, and what
  neither closes because it needs a human. A reader must be able to tell what a sweep would
  actually do to their repo.
- **Cheap by construction.** One `okf-validate.py --json` over the bundle, one glob, and reads of
  the few files the report names. Never fan out sub-agents: the validator already answers in one
  call what a sub-agent would be sent to re-derive.
- **Never judge, never rank, never infer.** An empty home is not a defect, an unlinked glossary
  entry is a valid permanent state, and `stale-doc` is an advisory age — never a verdict that a
  doc is wrong.

## Workflow (one read, one report)

### 1. Resolve the bundle
Resolve the `docs/` root at the repo root (or `docsDir` from `.claude/hooks/hooks-config.json`
when a target has customized it). Resolve `okf-validate.py`: the plugin's own
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py` first, then the target's
`.claude/hooks/okf-validate.py`, else report that neither is present and fall back to reading
frontmatter directly — **saying so in the report**, because an unverified read is a weaker claim.
Invoke via `python3`/`py`; branch on the **exit code** and the `--json`, never on prose.

**No bundle at all** is a complete, valid answer: report that `docs/` is absent and that
`/docs:align` would install it, then stop. A `docs/` that exists without an `okf_version` root
`index.md` is an un-installed tree, not a broken bundle — say which.
**Done when:** the bundle root and the checker are resolved, or their absence recorded.

### 2. Collect (read-only)
- `okf-validate.py <docs> --json` — every conformance finding, with `stale-doc` included, since
  this is CLI mode (per [conformance.md](../quenching-docs-align/references/conformance.md)
  §Staleness, it never runs in the hook path).
- `Glob` `docs/**/*.md` for the density counts, and read `docs/index.md`, each home's `index.md`,
  and `docs/knowledge/glossary.md`.
- `Glob` `~/.claude/projects/<cwd>/memory/*.md` and read the root `CLAUDE.md`/`AGENTS.md` size —
  the two out-of-band stores whose content the cycle would pull in.
- Read `docs/log.md`'s newest heading for the bundle's last activity date.

Nothing here writes. If the checker is unavailable, collect what the frontmatter supports and mark
every conformance row as unverified rather than reporting a clean bundle.
**Done when:** every source is read and nothing has been written.

### 3. Classify against the sweeps' own codes
Map each finding onto a code from
[conformance.md](../quenching-docs-align/references/conformance.md), and route it with
[cycle.md](../quenching-docs-align-and-update/references/cycle.md)'s opportunity table — which
already says, per row, whether the cycle auto-closes it. Contribute no code and no routing of your
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
   the root `index.md`), the checker's version and exit code verbatim, and the newest `log.md`
   date as the bundle's last activity.
2. **Density** — the table §5 defines. It comes *before* the findings, because a bundle with no
   findings and no content is the case this skill exists to make visible.
3. **Would be fixed by `/docs:align`** — the codes
   [cycle.md](../quenching-docs-align-and-update/references/cycle.md)'s table marks auto-closed by
   the align stage (`dir-no-index`, `index-broken-link`, `index-orphan`, un-stamped or mis-stamped
   frontmatter, variant folder names, prefix-clusters, non-English slugs), with counts. Name which
   would be **code-coupled** — a rename whose blast radius reaches product code — and so would
   confirm on its own. State plainly that this list is what a single OK would authorize.
4. **Would then be driven by `/docs:align-and-update`** — the content the cycle's later stages pull
   in: undrained `~/.claude` memory files (count), durable knowledge still inlined in the harness,
   and terms in the bundle absent from the glossary. These are the rows the table marks auto-closed
   by `quenching-docs-import-memory`, `quenching-docs-harness` and
   `quenching-docs-glossary-backfill`.
5. **Closed by neither** — every row the table marks **No**, each with the command that closes it:
   `resource-unresolved` and `resource-self` (→ `quenching-docs-add` to restamp, because only a
   human knows what a doc now governs), `glossary-broken-link` (→ `quenching-docs-define`, since
   the backfill stage adds missing terms and never prunes a dead one), `stale-doc` (advisory, with
   its age), coverage-ledger deferrals, and anything a human has not yet stated. Say plainly that
   `stale-doc` gates nothing, so a reader never mistakes an advisory for a blocker.

Close with the single most useful next command for this repo's actual state, and nothing else — no
plan, no offer to fix, no "shall I". A status read ends by handing control back.

**A section with nothing in it is reported as empty, never omitted** — "`/docs:align` would change
nothing" is the most valuable line this skill can print, and dropping the heading hides it.
**Done when:** all five sections are reported and no file has changed.

### 5. The density table — figures, not findings

Conformance says the bundle is *well-formed*. Density says whether it *knows anything*. A bundle
can pass every check while holding six scaffolded homes, five concept docs and a placeholder
glossary — the exact state that motivated this skill — and nothing in the front reported it.

Report it as one table, and give **no row a finding code**:

| Figure | How it is counted |
| --- | --- |
| Concept docs, total | `.md` files that are not `index.md`, `log.md`, or an EXEMPT basename (`CLAUDE.md`, `AGENTS.md`, `QUENCHING.md`) |
| Concept docs **per home** | the same count, grouped by top-level home, with **installed-but-empty homes shown as `0`** — never omitted, since the zero is the signal |
| Glossary terms | entries under `## Terms` in `knowledge/glossary.md`; note separately when the shipped **seed placeholder** is still the only one |
| Unlinked glossary entries | terms with no concept doc yet — a **valid permanent state**, reported as a figure and never as a defect |
| Standards subjects | subject subfolders under `standards/`, and how many hold at least one doc |
| Last activity | the newest `## YYYY-MM-DD` heading in `docs/log.md` |

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

- Never write, anywhere, for any reason — not a stamp, not an index, not a log line, not a marker.
  If something looks wrong enough to fix, name the command that fixes it and stop.
- Never report a finding with a code the validator does not define, and never state a finding the
  sweep would not raise.
- Never give a density figure a finding code, and never present an empty home as a defect.
- Never call `stale-doc` a violation, and never fold it into the must-fix set — it is advisory,
  and a bundle carrying one is still aligned.
- Never report a bundle as conformant on a run where the checker could not be resolved.
- Never fan out sub-agents, and never hand this SKILL.md `context: fork` when it is invoked as a
  sweep's preview — the report has to land in the conversation where the OK will be given.
