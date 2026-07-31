# How a `/specs:*` command resolves its tools, and where the front records itself

`specs/plans/` is a spec's whole active life — a quenching-managed sibling of `archive/`,
**outside** the OKF `docs/` bundle. Because it is outside the bundle, the OKF hook (configured with
`docsDir: docs`) never fires on it, and the OKF insert procedure in
[`docs-add/homes.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md) owns nothing here.
This file is the single owner of how every `/specs:*` command resolves its tools. A `/specs:*`
command writes nothing into the bundle at all — see §The `specs/` front records itself.

## The folder is the listing

`plans/` carries **no index file**. `specs.py list` and `specs.py status` derive what the folder
holds — slugs, derived stages, task progress — by reading it on demand, so there is nothing to
regenerate after a write and nothing that can fall out of date.

`plans/index.md` is a **retired artifact**: it once carried a GENERATED zone rebuilt by a
`specs.py plans reindex` subcommand, and both are gone. No command creates, seeds, refreshes or
validates one, and a copy surviving in a target repo is left exactly as found — neither refreshed
nor deleted, per
[`retiring-a-reserved-artifact.md`](/docs/standards/architecture/retiring-a-reserved-artifact.md)
§The consequence for disposition. The rule that decided it is
[`generated-listings.md`](/docs/standards/architecture/generated-listings.md): a generated listing
only pays for itself when a program can prove it is fresh, and this one duplicated a fact
`specs.py list` already derived.

**The on-write check is `specs.py validate`** — the spec's own contract, and the whole of it. The
OKF validator is never pointed at `specs/`: a spec carries `slug`/`title`/`verification` and
deliberately **no OKF `type:`**, so stamping one to satisfy a validator that does not model it
would be the second source of truth this front exists to avoid.

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

## The `specs/` front records itself

A new spec and a sweep over `plans/` write **nothing** into the `docs/` bundle. They used to
append to `docs/log.md`; that log is retired, and the `specs/` front never needed it — a spec's
own frontmatter records (`priority`, `refined`, `approved`, `branch`, `reviewed`, `merge`,
`outcome`) narrate its history in the file a reader already has open, and what the folder holds is
derived from disk on demand (§The folder is the listing). Nothing here is a cross-front event, so
nothing here is the bundle's business.
