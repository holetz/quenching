# Verification layer for the docs/ front

## Why

`okf-validate.py` returns exit 0 on this repository's own bundle — a bundle holding 33 markdown
files, of which 21 are `index.md`, 2 are `log.md` and 1 is `QUENCHING.md`. Five are concept docs,
and `knowledge/glossary.md` still carries the shipped seed placeholder as its only entry, in a repo
that coined *OKF*, *front*, *home*, *mold*, *harness*, *blast radius*, *fixpoint*,
*cycle-authorization* and *GENERATED zone*. Structural conformance is currently compatible with a
knowledge base that knows nothing, and nothing in the front reports that.

The gap is not doctrine. The glossary tail step is specified in six places — `homes.md`
§Enriching the glossary, `quenching-docs-add`, `quenching-docs-learn`,
`quenching-docs-import-memory`, `quenching-docs-define`, and `quenching-specs-plan-archive`'s
`distill.md` — and produced zero entries across two real distillation runs. An invariant written
six times and executed zero times is the argument for a deterministic rail rather than a seventh
restatement. The same holds for `resource:`: four skills forbid inventing one, and the validator
never checks that it points at anything. The repo's own seed, `knowledge/glossary.md`, ships
`resource: docs/**` — self-pointing, which the doctrine explicitly disallows.

The `specs/` front already has its read-only counterpart in `quenching-specs-status`, described as
"the front's only read-only view … doubles as an honest dry run before the OK". The `docs/` front
has none, so the only way to learn what `/docs:align` would do is to invoke the invasive skill and
read the plan from inside it.

## What Changes

- A new read-only skill `quenching-docs-status` and its mirrored wrapper `/docs:status` report the
  whole `docs/` front without writing anything, splitting findings into what `/docs:align` fixes,
  what `/docs:align-and-update` drives, and what neither closes.
- That report carries **bundle density** alongside conformance: homes scaffolded vs. empty, concept
  docs per home, glossary term count — so an empty bundle stops reading as a healthy one.
- `okf-validate.py` gains three checks: `resource-unresolved` (a path- or glob-shaped `resource`
  matching nothing on disk), `resource-self` (a `resource` whose scope contains the doc itself),
  and `glossary-broken-link` (the `index-broken-link` rule applied to `knowledge/glossary.md`).
- `okf-validate.py` gains a `stale-doc` WARN: the doc's `timestamp` is older than the last commit
  touching the paths its `resource` globs name.
- The shipped seed `assets/docs/knowledge/glossary.md` stops violating the anti-self-pointing rule
  it is meant to demonstrate.
- The skill/wrapper bijection recorded in `docs/standards/naming/command-surface.md` moves from
  27 ↔ 27 to its true current count plus this plan's addition.

## Out of Scope

- **The `authority: superseded` enum, `superseded_by:`, and a `/docs:deprecate` skill.** The
  `**Deprecation**` log prefix is reserved in four places and never written by any `docs-*` skill,
  and the enum has no state for a retired standard. Real, but it changes a contract that touches
  every mold, the validator, `taxonomy.md` and all three `QUENCHING.md` manuals — a different blast
  radius from this plan, which only observes. It is Plan B.
- **Provenance and idempotent re-ingestion for `quenching-docs-import`** (`source_uri` + content
  hash so a changed source is detectable). Deferred because the import path shows no evidence of
  having run on this repo; optimizing an unexercised path is speculation.
- **Inverting the harness default toward `AGENTS.md`** now that it is a Linux Foundation open spec
  with 60k+ adopting repos, while `assets/templates/harness/` ships only `claude-root.md` and
  `claude-subfolder.md`. Well-founded but independent — it blocks nothing here. Routed to
  `specs/backlog/`.
- **Cross-document contradiction detection between two `standards/` docs.** Needs a semantic pass,
  not a deterministic check, so it does not belong in a validator-centred plan.
- **A retrieval/query skill over the bundle.** Grep over a bundle with a greppable `type` already
  answers it; a second read path would age without earning its keep.

## Validation

- `python3 plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/docs`
  → `0 error(s), 0 warning(s)`, including the corrected glossary seed.
- `python3 plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/specs/backlog --listing-root`
  → `0 error(s), 0 warning(s)` (the new checks must not regress the backlog listing root).
- The four new finding codes each fire on a purpose-built fixture and stay silent on the shipped
  skeleton: a doc with `resource:` naming a nonexistent path, a doc whose `resource` glob contains
  itself, a `glossary.md` linking a deleted doc, and a doc whose `timestamp` predates the last
  commit touching its `resource` globs.
- `--json` output remains parseable and every new finding carries a code, a severity and a path;
  no existing code changes severity.
- Version lockstep holds: `cat VERSION`, `specs.py --version` and `okf-validate.py --version` agree.
- `/docs:status` run against this repository writes nothing — verified by a clean `git status` after
  the run — and reports the five concept docs, the empty homes, and the one-entry glossary.
- Every wrapper resolves to a skill and every skill to a wrapper (the bijection), and the three
  `QUENCHING.md` manuals enumerate the new command.

## Impact

### Standards this plan will write into docs/standards/

- `docs/standards/quality/bundle-verification.md` — what the `docs/` front machine-checks versus
  what it leaves to a skill's prose self-check, and the rule that an invariant restated in more
  than two skills is owed a deterministic check rather than a third restatement

### Standards at `authority: background` this plan may resolve

- none — no `authority: background` standard currently governs the `docs/` front's verification.

### Product code this plan expects to touch

- `plugins/claude-quenching/assets/hooks/okf-validate.py` — the four new checks, their codes, and
  the `--version` bump
- `plugins/claude-quenching/assets/docs/knowledge/glossary.md` — the self-pointing `resource:` in
  the shipped seed
- `plugins/claude-quenching/skills/quenching-docs-align/references/conformance.md` — the finding
  codes are owned here and cited by every skill's self-check
- `plugins/claude-quenching/skills/quenching-docs-status/` and
  `plugins/claude-quenching/commands/docs/status.md` — the new skill and its mirrored wrapper
- `plugins/claude-quenching/assets/docs/QUENCHING.md`, `assets/specs/QUENCHING.md`,
  `assets/claude/QUENCHING.md` — all three enumerate the command surface
- `plugins/claude-quenching/VERSION`, `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `assets/bin/specs.py` — the release lockstep quartet
- `CLAUDE.md`, `plugins/claude-quenching/README.md` — the skill count and the 27 ↔ 27 bijection
