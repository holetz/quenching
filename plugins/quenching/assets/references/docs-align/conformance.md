# Conformance — the exact checks

The single source for what "OKF-conformant" means in this plugin. The executable
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py` implements **exactly** these checks; the
skills apply the same rules by hand when they cannot shell out, and their self-check steps
**cite this file** rather than restating the rules. Severities: **ERROR** fails
conformance (validator exit 1); **WARN** is a recommendation (exit 0 unless
`warnAsError`).

## File classification (by basename)

<!-- rules -->

| Basename | Kind | Checked as |
| --- | --- | --- |
| `index.md` | reserved listing | `check_index` |
| `log.md` | reserved, **retired** | nothing — recognized, never judged (see below) |
| `CLAUDE.md`, `AGENTS.md` | harness pointer | **exempt** (skipped; honesty checked by `/quenching:docs:harness`, not the validator) |
| `QUENCHING.md` | operator manual (plugin payload) | **exempt** (skipped; installed and refreshed by the front's align — `/quenching:docs:align` for `docs/`, not authored knowledge) |
| `README.md` | migration nudge | WARN "convert to index.md" |
| any other `*.md` | concept doc | `check_concept` |

## Concept docs (`check_concept`)

<!-- rules -->

- **ERROR `no-frontmatter`** — no `---` YAML block at the top.
- **ERROR `broken-frontmatter`** — opens `---` but never closes.
- **ERROR `missing-type`** — frontmatter has no non-empty `type`.
- **WARN `missing-<field>`** — a recommended field is absent: `title`, `description`,
  `resource`, `timestamp`.

## `index.md` (`check_index`)

<!-- rules -->

- **ERROR `index-has-type`** — carries a concept `type` (an index is a listing, not a concept).
- **Non-root** `index.md`:
  - **ERROR `index-has-frontmatter`** — carries **any** frontmatter (must be a bare listing).
- **Root** `index.md` (at the bundle root):
  - **WARN `root-no-okf-version`** — does not declare `okf_version`.
  - **WARN `root-okf-version-mismatch`** — declares a version other than `0.1`.
  - **WARN `root-extra-keys`** — carries keys other than `okf_version`.

## `log.md` (retired — no checks)

<!-- rules -->

No codes. The validator recognizes the name, emits nothing about the file, and never blocks a
write to it under `hardBlock`. **The reservation is what makes that true**, and it is load-bearing
in a way the silence hides: drop `log.md` from the validator's `RESERVED` tuple and every log
surviving in an already-aligned bundle falls through to `check_concept` — `missing-type` at ERROR,
and denied writes under the hard gate. Retired is not unreserved. `okf-validate.py selftest` holds
the line with a fixture bundle carrying two surviving logs.

## Bundle level

<!-- rules -->

- **WARN `bundle-no-index`** — the bundle root has no `index.md`.

## Structural integrity (whole-tree — CLI + `Stop` only)

<!-- rules -->

Deterministic directory/index checks the validator runs over the **whole tree** (not on a
single-file `PostToolUse`). All **WARN** — OKF says a consumer MUST tolerate broken links and
MAY synthesize a missing `index.md`, so these never fail conformance; the **skills treat them
as must-fix** in their own verify gate (a bundle `/quenching:docs:align` leaves behind has none). Dirs whose
name starts with `_` or `.`, and asset dirs (`img/`, `assets/`, `static/`, `node_modules/`,
`__pycache__/`, …), are pruned from this walk.

- **WARN `dir-no-index`** — a directory directly holds ≥1 concept doc but has no `index.md`
  listing (the concrete "índice faltando": a subject folder like `standards/code/` with docs and
  no front door). Every folder that holds knowledge gets a regenerated `index.md`.
- **WARN `index-broken-link`** — an `index.md` links to a `.md` file or subfolder that does not
  exist on disk (a "lying index"). Only **within-bundle** links written in the bundle's own form
  are judged; external URLs, anchors, non-`.md` assets, `../`-climbs that leave the bundle, and
  repo-absolute `/…` links (e.g. `/.claude/…`) are ignored, never false-flagged.
- **WARN `index-orphan`** — a concept doc that **no** `.md` in the bundle links to (unlisted / not
  reachable by browsing). The fix is to add it to its folder's `index.md` (or the derived
  standards zone). Link language/wording is **not** machine-checked — the English-slug rule is a
  skill-applied convention (the validator cannot reliably detect a document's natural language).
- **WARN `glossary-broken-link`** — the same link rule applied to `knowledge/glossary.md`, whose
  links **are** its content: an entry pointing at a deleted doc is a dead lookup. It needs its own
  code because `index-broken-link` is only ever judged on an `index.md`, and the glossary is a
  concept doc. Same resolver, so the two never diverge on what a link means.

## Resource integrity (per-doc — every mode)

<!-- rules -->

A doc that is provably **lying about itself**. These join the structural set the skills treat as
**must-fix** in their verify gate, for the same reason: `WARN` because OKF does not govern
`resource` at all, blocking because the plugin does.

- **WARN `resource-unresolved`** — a path- or glob-shaped `resource` entry matching nothing on
  disk, reported **per entry** so a comma-separated list names which one is broken. A `uri` entry
  is never resolved, and an entry carrying glob syntax the validator does not implement (braces,
  character classes, `?`) is classified `unknown` and **never reported** — only `*` and `**` are
  implemented, and flagging syntax nobody writes would make the must-fix set unusable.
- **WARN `resource-self`** — the doc's own path falls inside the scope its `resource` declares.
  Such a doc governs nothing and is eternally fresh, which silently disables `stale-doc` for it.
  Matching is **segment-wise**: a single `*` does not cross a `/`, so `docs/*` does not contain
  `docs/standards/x.md`.
  - **The bundle-aggregate exemption.** An entry whose scope contains the bundle **root** is an
    aggregate, not a mistake, and never raises this. `knowledge/glossary.md` really does govern
    the whole bundle, so `resource: docs/**` is truthful and narrowing it would be the
    fabrication. This is `TYPES_WITHOUT_RESOURCE` generalized — one exemption mechanism, not two.

## Staleness (CLI only — advisory, never blocking)

<!-- rules -->

- **WARN `stale-doc`** — the doc's `timestamp` predates the last commit touching the code its
  `resource` globs name (`git log -1 --format=%cI` with explicit **`:(glob)`** pathspec magic, so
  a single `*` does not cross a `/` here either).

**It is advisory and is NOT part of any verify gate.** The integrity codes describe a doc that is
provably wrong; a stale-looking doc may be perfectly correct, because code moves under a rule that
did not change. Every mature bundle carries some, so treating it as must-fix would make the
must-fix set unusable.

It runs in **CLI mode only** — never `PostToolUse`, never `Stop`: it shells out to `git` once per
doc, which is fine on demand and unacceptable under the `Stop` deadline. A tree that is not a git
checkout **skips it silently** rather than reporting a finding it cannot compute.

## Running it

<!-- rules -->

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py <repo>/docs        # human report; exit 0/1
python3 ${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py <repo>/docs --json # machine-readable findings
```

As a hook (stdin JSON): **PostToolUse**/**Stop** PROPOSE fixes via `additionalContext`;
opt-in **PreToolUse** (`hardBlock: true`) denies writing an `index.md` with a `type` or a
concept doc with no `type`. Config block `okfValidate` in `hooks-config.json`
(`docsDir`/`warnAsError`/`blockOnFail`/`hardBlock`/`deadlineMs`).

## Verify gate (Step 5 of /quenching:docs:align)

<!-- rules -->

A bundle is **aligned** when `okf-validate.py <docs>` exits 0 **and** the structural-integrity and
resource-integrity WARNs are all cleared — **zero** `dir-no-index`, `index-broken-link`,
`index-orphan`, `glossary-broken-link`, `resource-unresolved`, `resource-self`. (These are WARN,
so they do not fail exit-0; the skill reads them from `--json` and treats them as blocking.)
**`stale-doc` is excluded from this gate** — it is advisory, reported and never blocking, and a
bundle carrying one is still aligned.
Beyond that, the skill also confirms the method-level completeness the validator can't see:
applicable homes present, each standards subject's **coverage/deferral ledger** filled (every
candidate present or listed), and the GENERATED zones matching disk — `standards/index.md`'s
"Current docs" tables and `backlog/index.md`'s task listing (each rebuilt exclusively from
the frontmatter on disk).
