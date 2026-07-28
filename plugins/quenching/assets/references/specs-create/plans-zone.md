# The `specs/plans/index.md` GENERATED zone + the on-write check

`specs/plans/` is a spec's whole active life — a quenching-managed sibling of `archive/`,
**outside** the OKF `docs/` bundle. Because it is outside the bundle, the OKF hook (configured with
`docsDir: docs`) never fires on it and the OKF insert procedure in
[`docs-add/homes.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md) does **not** own
its listing zone. This file is the single owner of that zone's contract, of the front's own
on-write check, and of how every `/specs:*` command resolves its tools. The log entry a command
appends still lands in the bundle's `docs/log.md` (the bundle log records the cross-boundary
event).

## The GENERATED zone — owned by `specs.py plans reindex`

`plans/index.md` carries a **GENERATED zone** between `<!-- BEGIN GENERATED -->` /
`<!-- END GENERATED -->`. No command regenerates it by hand — they call the tool, which owns the
format:

```bash
specs.py plans reindex          # resolve the script per §Resolving the tool below
```

`reindex` rebuilds the zone **deterministically from `plans/*.md`**, anchoring on the existing
markers (or installing them when absent — that is how `sp-no-generated-zone` is repaired), and
never touching the fixed prose outside them. What the tool produces, in order:

- a summary line — `**N specs** · a executing · b approved · c ready · …`, listing only the stages
  that have members;
- one `### <Stage>` section per **derived stage**, most advanced first, each a
  `Spec | Title | Since` table sorted by filename, so the newest work in a stage reads last.

The grouping key is the **derived stage**, not a declared field: it comes from the spec's section
presence and frontmatter, exactly as `specs.py status` reports it. That is what makes the listing
impossible to falsify — a spec cannot appear as `ready` without actually carrying the ten sections.

With no specs at all, the zone is a single `_(no specs captured — …)_` line. Because the render is
deterministic, `reindex` reports `changed: false` when the zone already matches disk — a command
reads that JSON to know whether it wrote anything. **Never hand-edit inside the markers**, and
never add frontmatter to `plans/index.md`: it is a reserved, frontmatter-free listing, the same
rule an OKF `index.md` follows.

## The on-write check — run the validator, do not re-implement it

`specs/` sits outside the `docs/` bundle, so the OKF `PostToolUse`/`Stop` hook (docs-scoped by
config) never fires on it. `okf-validate.py` takes its root as an argument, and every rule the
listing needs is already in its conformance core, so a command that wrote here closes with the real
check:

```bash
okf-validate.py specs/plans --listing-root
```

`--listing-root` says "this tree is a quenching-managed listing, not an OKF bundle root": the
`index.md` is held to the plain-listing rule (frontmatter-free — ERROR if it carries any) instead
of the bundle-root rule that expects `okf_version`, and the `bundle-no-index` SHOULD is dropped.
The link checks apply unchanged — every index link resolving (`index-broken-link`), nothing on disk
the zone forgot to list (`index-orphan`).

**It checks the listing and nothing else.** A spec carries `slug`/`title`/`verification` and
deliberately **no OKF `type:`**; `specs.py validate` is its contract, and stamping an OKF type on a
spec to satisfy a validator that does not model it would be the second source of truth this front
exists to avoid.

**Exit 0 with no `index-broken-link` / `index-orphan` finding is the pass condition** — exit 0
alone does not prove the WARN-level structural checks clear, so read the findings.

## Resolving the tool

All three tools — `specs.py`, `skills.py` and `okf-validate.py` — resolve by the same fallback: the
plugin path (`${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py`,
`${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py`,
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py`)
first, then a copy installed into the target's `.claude/hooks/`, and if neither resolves, the
declared **manual** fallback — check those same rules by hand and **say in the report that the
check was manual**, never silently skip it. `/specs:align` installs `specs.py` into a target's
`.claude/hooks/`; `/skill:align` installs `skills.py`; `/docs:align` installs `okf-validate.py`
and the hook config.

Every command branches on the **exit code** (0 ok · 1 findings · 2 refusal) and the
`--json` payload, never on prose. That contract is what lets the commands stay short: the tool
decides, the command reports.

### Write the resolved path literally on every invocation

**Never hold the interpreter and the script path in a shell variable and expand it as a command.**
This is the one shell idiom that silently breaks the resolution above:

```bash
SP="python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py"
$SP status --spec my-spec --json      # WRONG
```

Under **bash** this works, because unquoted expansion is word-split. Under **zsh** it does not:
zsh does not word-split scalars, so `$SP` is one word and the shell looks for a command whose
literal filename is `python3 /…/specs.py`. Measured 2026-07-27 — bash prints the version, zsh
answers `command not found: python3 --version`.

The failure mode is what makes it worth a rule: it is **shell-dependent and silent**. Nothing is
written, the exit status is a plain non-zero, and a command that does not read stderr closely
reports "sections written" over a file it never touched. Since a target repo's shell is whatever
the human uses, a pattern that passes on the author's bash is not evidence of anything.

Write the resolved path in full on each call:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py" status --spec my-spec --json
```

A shell **function** is the only correct abbreviation, and only *within a single `Bash` call* —
shell state does not survive between calls, so a function defined in one call is gone by the next
(measured 2026-07-27). When one call issues several invocations:

```bash
sp() { python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py" "$@"; }
sp section my-spec "Proposal" --write <<'EOF'
…
EOF
sp validate --spec my-spec --json
```

**Quote the path.** `${CLAUDE_PLUGIN_ROOT}` can contain spaces, which splits an unquoted path into
two arguments and produces the same "no such file" with a different cause.

**When several writes run in one call, chain them so a failure stops the run** — `set -e`, or
`&&` between them. A loop of independent writes where the first silently fails and the rest
proceed is how a partial spec gets reported as complete.

## Appending to the bundle log

Newest first, in the bundle's `docs/log.md` (per §Appending to `log.md` in
[`docs-add/homes.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)):
`**Creation**: [<title>](/specs/plans/<YYYY-MM-DD-slug>.md) — <one line>` for a new spec, and a
single consolidated `**Update**: [plans/](/specs/plans/index.md) — <what the sweep did>` for a
sweep. No `docs/` bundle → skip the entry; `specs/` stands on its own.
