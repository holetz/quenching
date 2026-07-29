---
slug: notice-installed-tool-version-drift
title: Nothing notices an installed tool copy falling behind the plugin
verification: per-section
priority: {level: 5, criticality: high, date: 2026-07-28}
branch: {base: main, work: plan/notice-installed-tool-version-drift}
---

# Nothing notices an installed tool copy falling behind the plugin

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

Each front's align **offers** to install or upgrade its tool into a target's `.claude/hooks/` —
`/docs:align` step 6 for `okf-validate.py`, `/specs:align` for `specs.py`, `/skill:align` for
`skills.py`. The offer is the only moment the version is ever compared, so a repo that installed
once and never ran an align again keeps running whatever it got, indefinitely, and nothing says so.

This repo is the standing example. While concluding `instrument-and-extend-skill-front`,
`.claude/hooks/specs.py --version` answered **1.0.0** against a plugin shipping **4.1.0** — three
major versions behind, and behind enough that its `status` subcommand still took `--plan` where the
current one takes `--spec`. The conclude run had to fall back to the plugin's own copy to proceed.
`okf-validate.py` is in the same state. The repository that *authors* these tools has been running
years-old copies of two of them, and no check anywhere noticed.

The cost is not merely staleness: a stale copy answers a different CLI contract, so a command that
resolves the installed copy first (which the documented fallback tells it to do) branches on a
payload shape that no longer exists.

**What makes this a spec.** The fix is not "run the aligns" — that closes today's instance and
restores the same silence tomorrow. Something must *notice*: a drift check that is cheap enough to
run without an align, reporting the installed version against the shipped one for all three tools.

Discovered and confirmed live during `instrument-and-extend-skill-front`'s conclude, 2026-07-28.

## Discoveries

- Confirmed again 2026-07-28 during an /align run, with a SECOND silent failure mode this Problem does not cover: the installed okf-validate.py and specs.py were 1.0.0 against a plugin at 4.2.0, but .claude/settings.json carried NO hooks block at all — the scripts sat on disk with nothing invoking them, so deleting all three changed no behaviour, which is precisely why nobody noticed. A drift check that only compares --version would have caught 1.0.0-vs-4.2.0 and still missed that the hook was inert. Whatever notices drift should also answer 'is this tool actually wired?' (for okf-validate.py: a hooks block in settings.json referencing it — one cheap JSON read). Note too that /docs:align's install is step 5, 'pass 1 only, offered', so on this repo the offer never fired at all.
- Drift is silent in BOTH directions, and the reverse case is invisible to a --version comparison alone: every command resolves the plugin path FIRST and the installed copy only as fallback (plans-zone.md 'Resolving the tool'), while each align refuses to overwrite a NEWER installed copy — so a repo whose .claude/hooks/ copy is ahead of the loaded plugin runs the older plugin code silently, and the align reports nothing because leaving the newer copy alone is its correct behaviour. Whatever notices drift should report the comparison in both directions and name which copy the commands will actually execute.
