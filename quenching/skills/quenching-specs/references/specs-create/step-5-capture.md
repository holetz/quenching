# /quenching-specs create — step 5, capture in ONE call

Resolve the tool per
[align/tool-resolution.md](.agents/quenching/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.
The layout, the thirteen canonical sections, the gates and the front's on-write check live in
[specs-develop/spec-driven.md](.agents/quenching/references/specs-develop/spec-driven.md)
§The thirteen sections §The gates and the stage-scoped explicit-none rule; the `cq specs` surface
lives in [specs-surface.md](.agents/quenching/references/specs-develop/specs-surface.md)
§The `.agents/quenching/bin/cq specs` tool surface.

Write `## Problem` — the problem or opportunity in the source's own framing, two sentences on the
sentence path.

**Plan-source path:** additionally write every section the plan actually supports, its own
entry of `sections` in the same call. Where the plan was
silent on a section you are writing others around, write `- none — <what the source did not
record>`. Never fabricate.

Everything step 4 resolved and everything above go in **one** `specs_write(verb="create")`, then the closing
`validate`:

```text
specs_write(verb="create", name="<title>", subject=<key>, type=<key>,
             tags="<subject's fixed tags>,<confirmed catalog tags>", complexity=<level>,
             sections=[{"heading": "Problem", "body": "<two sentences, or what the source supports>"},
                       {"heading": "<Heading>", "body": "<plan-source path only: every other section the plan actually supports>"}])
specs_read(verb="validate", spec=<id>)   # <id>: the `id` the create returned
```

`subject`/`type`/`tags` only where step 4 resolved one; `tags`, when present, carries the **whole**
list — the subject's own fixed tags are folded in by the tool, never lost.

**Refusals, all before anything is written:** `sp-bad-complexity` means step 4's computed level
is wrong — recompute and retry the same call. `sp-stray-heading` (`source: stream`)
or `sp-write-duplicate-heading` means `sections` is malformed — fix it and retry the same call,
never split it into smaller ones. `sp-no-subject`/`sp-subject-unknown`/`sp-type-unknown`
means step 4's own resolution disagrees with the target's declared config RIGHT NOW (a race, or a
stale read) — re-run `specs_read(verb="config")` and redo step 4 rather than retrying blind.
`sp-az-workitemtype-only-answer` means the target still declares the retired
`azurePlacement.workItemType` with no `workItemTypes` catalog resolving one — name the finding and
its remedy verbatim, and stop; migrating the target's config is not this command's call to make.
Any other backend failure (`sp-backend-unavailable`, `sp-worktree-unusable`,
`sp-worktree-failed`) is reported verbatim, with the finding's own declared remedy and nothing
invented beside it.
**A failure after the issue was created** (a refusal carrying `issue`/`url`, or any `new` that
died past its POST) is never retried blind: search the target by exact title first
(`specs_read(verb="list")`, matched on the title), and finish or reuse the issue that exists instead
of running `new` again — a blind retry duplicates it.

The closing `specs_read(verb="validate", spec=<id>)` is the whole check — its own finding, if any, is named
verbatim in step 6, never swallowed.
