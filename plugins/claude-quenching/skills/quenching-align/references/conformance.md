# Conformance — the exact checks

The single source for what "OKF-conformant" means in this plugin. The executable
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py` implements **exactly** these checks; the
skills apply the same rules by hand when they cannot shell out, and their self-check steps
**cite this file** rather than restating the rules. Severities: **ERROR** fails
conformance (validator exit 1); **WARN** is a recommendation (exit 0 unless
`warnAsError`).

## File classification (by basename)

| Basename | Kind | Checked as |
| --- | --- | --- |
| `index.md` | reserved listing | `check_index` |
| `log.md` | reserved history | `check_log` |
| `CLAUDE.md`, `AGENTS.md` | harness pointer | **exempt** (skipped; honesty checked by `quenching-harness`, not the validator) |
| `README.md` | migration nudge | WARN "convert to index.md" |
| any other `*.md` | concept doc | `check_concept` |

## Concept docs (`check_concept`)

- **ERROR `no-frontmatter`** — no `---` YAML block at the top.
- **ERROR `broken-frontmatter`** — opens `---` but never closes.
- **ERROR `missing-type`** — frontmatter has no non-empty `type`.
- **WARN `missing-<field>`** — a recommended field is absent: `title`, `description`,
  `resource`, `timestamp`.

## `index.md` (`check_index`)

- **ERROR `index-has-type`** — carries a concept `type` (an index is a listing, not a concept).
- **Non-root** `index.md`:
  - **ERROR `index-has-frontmatter`** — carries **any** frontmatter (must be a bare listing).
- **Root** `index.md` (at the bundle root):
  - **WARN `root-no-okf-version`** — does not declare `okf_version`.
  - **WARN `root-okf-version-mismatch`** — declares a version other than `0.1`.
  - **WARN `root-extra-keys`** — carries keys other than `okf_version`.

## `log.md` (`check_log`)

- **ERROR `log-has-type`** — carries a concept `type`.
- **WARN `log-no-date-heading`** — has content but no `## YYYY-MM-DD` heading.
- **WARN `log-not-newest-first`** — date headings are not in descending order.

## Bundle level

- **WARN `bundle-no-index`** — the bundle root has no `index.md`.

## Structural integrity (whole-tree — CLI + `Stop` only)

Deterministic directory/index checks the validator runs over the **whole tree** (not on a
single-file `PostToolUse`). All **WARN** — OKF says a consumer MUST tolerate broken links and
MAY synthesize a missing `index.md`, so these never fail conformance; the **skills treat them
as must-fix** in their own verify gate (a bundle `quenching-align` leaves behind has none). Dirs whose
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

## Running it

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py <repo>/docs        # human report; exit 0/1
python3 ${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py <repo>/docs --json # machine-readable findings
```

As a hook (stdin JSON): **PostToolUse**/**Stop** PROPOSE fixes via `additionalContext`;
opt-in **PreToolUse** (`hardBlock: true`) denies writing an `index.md` with a `type` or a
concept doc with no `type`. Config block `okfValidate` in `hooks-config.json`
(`docsDir`/`warnAsError`/`blockOnFail`/`hardBlock`/`deadlineMs`).

## Verify gate (Step 5 of quenching-align)

A bundle is **aligned** when `okf-validate.py <docs>` exits 0 **and** the structural-integrity
WARNs are all cleared — **zero** `dir-no-index`, `index-broken-link`, `index-orphan`. (These are
WARN, so they do not fail exit-0; the skill reads them from `--json` and treats them as blocking.)
Beyond that, the skill also confirms the method-level completeness the validator can't see:
applicable homes present, each standards subject's **coverage/deferral ledger** filled (every
candidate present or listed), and `standards/index.md`'s GENERATED zone matching disk.
