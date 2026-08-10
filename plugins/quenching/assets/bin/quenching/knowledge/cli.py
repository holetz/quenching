"""CLI mode, and the pillar's entry point.

Moved verbatim out of `assets/hooks/okf-validate.py`, with two changes stated below.

CLI  `<bundle-or-docs-dir> [--json]`
   Validates the whole bundle rooted at the given directory (walks every `.md`),
   prints a human report, and exits **0** when there are no errors, **1** otherwise.
   This is what `quenching-docs-align`/`quenching-docs-add` invoke and what the plugin's own
   verification runs over `assets/docs/`.
   This checker validates OKF bundles and nothing else. The `specs/` front is owned
   end-to-end by the specs pillar's `validate`, which holds a spec to its own contract
   (canonical heading set, stage gates, filename conformance, slug identity) — a contract
   that has no `type:` in it. Pointing this checker at a spec tree would report defects the
   specs front forbids fixing.

THE MODE IS A VERB, NOT A HEURISTIC — the one behaviour change
--------------------------------------------------------------
`okf-validate.py` decided its mode by looking at the world: no `argv` **and** a non-tty
stdin meant "hook". That test does not survive a pillar prefix, and it should not: it
misfires under CI, under a subprocess, and under any redirection, silently and with no
way to override it. `main` here routes the DECLARED token `hook` to `quenching.knowledge.hook.run_hook`
and everything else to `run_cli`. Nothing in this pillar calls `isatty`.

Task 5.3 mounts `cq knowledge …` on the two functions this module exposes — `run_cli(argv)`
and, re-exported for it, `run_hook()` — or on `main(argv)` directly, which already spells the
routing as one token.

`selftest` IS NOT HERE. The canonical frontmatter cases and the two retirement fixtures are
tests and migrate to `tests/` in task 6.3, which is also where the intercept that kept a bare
subcommand from being scanned as a path went; whether the verb survives is 6.3's to decide,
and re-adding it is one branch in `run_cli`.
"""
from __future__ import annotations

import json

from quenching.common.output import FINDINGS, OK
from quenching.common.version import VERSION
from quenching.knowledge.config import _load_config, _project_dir
from quenching.knowledge.hook import run_hook
from quenching.knowledge.render import _render_text, _split
from quenching.knowledge.validate import validate_tree


def run_cli(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"okf-validate {VERSION}")
        return OK
    cfg = _load_config(_project_dir({}))
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("-")]
    target = paths[0] if paths else ".docs"
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
    """The pillar's whole entry: one declared token chooses the mode.

    There is no REFUSAL step. `okf-validate.py` never had one — not one `return 2` in its
    1,372 lines — and inventing one here would be a behaviour change dressed as a move. A
    bundle root that is not a directory is a `no-bundle` ERROR finding and exits `FINDINGS`,
    exactly as it always did."""
    if argv and argv[0] == "hook":
        return run_hook()
    return run_cli(argv)
