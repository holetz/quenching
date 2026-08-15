"""CLI mode, and the pillar's entry point.

Moved verbatim out of the pre-refactor OKF validator script.

CLI  `validate [<bundle-or-docs-dir>] [--json]`
   Validates the whole bundle rooted at the given directory (walks every `.md`),
   prints a human report, and exits **0** when there are no errors, **1** otherwise.
   This is what `quenching-knowledge-align`/`quenching-knowledge-add` invoke and what the plugin's own
   verification runs over `assets/knowledge/`.
   This checker validates OKF bundles and nothing else. The `specs/` front is owned
   end-to-end by the specs pillar's `validate`, which holds a spec to its own contract
   (canonical heading set, stage gates, filename conformance, slug identity) — a contract
   that has no `type:` in it. Pointing this checker at a spec tree would report defects the
   specs front forbids fixing.

`validate` is the only verb `main` routes. The `hook` verb (`quenching.knowledge.hook.run_hook`,
answering the plugin's self-installed `PostToolUse`/`Stop`/`PreToolUse` wiring) was retired along
with that wiring — this pillar no longer answers a hook event at all.

`selftest` IS NOT HERE. The canonical frontmatter cases and the two retirement fixtures are
tests and migrate to `tests/` in task 6.3, which is also where the intercept that kept a bare
subcommand from being scanned as a path went; whether the verb survives is 6.3's to decide,
and re-adding it is one branch in `main`.
"""
from __future__ import annotations

import json
import sys

from quenching.common.output import FINDINGS, OK, REFUSAL
from quenching.common.version import VERSION
from quenching.knowledge.config import _load_config, _project_dir
from quenching.knowledge.render import _render_text, _split
from quenching.knowledge.validate import validate_tree


USAGE = ("usage: cq knowledge validate [<bundle-dir>] [--json]   "
         "(default bundle-dir: .knowledge)")


def run_cli(argv: list[str]) -> int:
    cfg = _load_config(_project_dir())
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("-")]
    target = paths[0] if paths else ".knowledge"
    ignore_globs = tuple(cfg.get("ignoreGlobs") or ())
    # no deadline in CLI mode — always a full scan
    # `with_stale` only here: CLI is the one mode that may shell out to git per doc
    findings = validate_tree(target, ignore_globs=ignore_globs, with_stale=True)
    if as_json:
        print(json.dumps([
            {"severity": s, "path": r, "code": c, "message": m} for s, r, c, m in findings
        ], indent=2))
    else:
        print(_render_text(findings, target))
    errors, warns = _split(findings)
    if errors:
        return FINDINGS
    if warns and cfg.get("warnAsError"):
        return FINDINGS
    return OK


def main(argv: list[str]) -> int:
    """The pillar's whole entry: the declared token chooses the mode.

    THE MODE IS A VERB, NOT A HEURISTIC. The pre-refactor OKF validator script decided its mode by
    looking at the world: no `argv` **and** a non-tty stdin meant "hook". That test does not survive
    a pillar prefix, and it should not: it misfires under CI, under a subprocess, and under any
    redirection, silently and with no way to override it. `main` routes the DECLARED token —
    `validate` to `run_cli`, and nothing else now that `hook` is retired — and nothing in this
    pillar calls `isatty`. Any argv that is not the verb was once read as a bundle path, which the
    spec's `## Out of Scope` rules out by name, so a token that is not a verb is a usage refusal.

    THE VALIDATOR STILL HAS NO REFUSAL STEP. The pre-refactor OKF validator script never had one — not one
    `return 2` in its 1,372 lines — and inventing one would be a behaviour change dressed as
    a move. A bundle root that is not a directory is still a `no-bundle` ERROR finding
    exiting `FINDINGS`, exactly as it always did. The `REFUSAL` below is the ROUTER's, on a
    word that names no verb, and it can only be reached before any bundle is read."""
    if "--version" in argv:
        # `cq knowledge`, not the pre-refactor validator's filename: task 10.1 deleted that file,
        # so the stamp was naming an artifact the repo no longer ships. `citation-check.sh` cannot
        # see it — its dead patterns match the script names WITH their extension, and this string
        # carries none.
        print(f"cq knowledge {VERSION}")
        return OK
    verb = argv[0] if argv else ""
    if verb == "validate":
        return run_cli(argv[1:])
    print(USAGE, file=sys.stderr)
    return REFUSAL
