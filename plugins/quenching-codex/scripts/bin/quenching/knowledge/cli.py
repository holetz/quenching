"""CLI mode, and the pillar's entry point.

Moved verbatim out of the pre-refactor OKF validator script.

CLI  `validate [<bundle-or-docs-dir>] [--json]`
   Validates the whole bundle rooted at the given directory (walks every `.md`),
   prints a human report, and exits **0** when there are no errors, **1** otherwise.
   This is what `quenching:knowledge:align`/`quenching:knowledge:add` invoke and what the plugin's own
   verification runs over `assets/knowledge/`.
   This checker validates OKF bundles and nothing else. The `specs/` front is owned
   end-to-end by the specs pillar's `validate`, which holds a spec to its own contract
   (canonical heading set, stage gates, filename conformance, slug identity) — a contract
   that has no `type:` in it. Pointing this checker at a spec tree would report defects the
   specs front forbids fixing.

CLI  `project [<bundle-dir>] [--write|--check|--json]`
   Checks or materializes the deterministic documentation projection of the canonical glossary.
   `--write` is the explicit mutation mode; the default is a read-only projection gate.

CLI  `site-source [<bundle-dir>] [<destination>] [--write|--check|--json]`
   Materializes or verifies the bounded tree that Zensical may read. Raw `catalog/` and
   `external/` homes are never copied into it.

`validate`, `project`, `nav` and `site-source` are the verbs `main` routes. The `hook` verb (`quenching.knowledge.hook.run_hook`,
answering the plugin's self-installed `PostToolUse`/`Stop`/`PreToolUse` wiring) was retired along
with that wiring — this pillar no longer answers a hook event at all.

`selftest` IS NOT HERE. The canonical frontmatter cases and the two retirement fixtures are
tests and migrate to `tests/` in task 6.3, which is also where the intercept that kept a bare
subcommand from being scanned as a path went; whether the verb survives is 6.3's to decide,
and re-adding it is one branch in `main`.
"""
from __future__ import annotations

import json
import os
import sys

from quenching.common.output import FINDINGS, OK, REFUSAL
from quenching.common.version import VERSION
from quenching.knowledge.config import _load_config, _project_dir
from quenching.knowledge.render import _render_activity, _render_text, _split
from quenching.knowledge.projection import (
    DEFAULT_SNIPPET,
    projection_findings,
    write_projection,
)
from quenching.knowledge.site_source import site_source_findings, stage_site_source
from quenching.knowledge.stale import resource_activity
from quenching.knowledge.validate import _build_corpus, validate_tree


USAGE = ("usage: cq knowledge {validate|project|nav|site-source} [<bundle-dir>] [options]   "
         "(default bundle-dir: docs)")


def _activity_rows(bundle_root: str, ignore_globs: tuple[str, ...]) -> list[tuple[str, dict]]:
    """`(relative path, activity)` for every doc in the bundle that has something to measure."""
    rows = []
    corpus = _build_corpus(bundle_root, None, ignore_globs) or {}
    for path in sorted(corpus):
        text = corpus[path]
        if text is None or not path.endswith(".md"):
            continue
        activity = resource_activity(text, bundle_root)
        if activity is not None:
            rows.append((os.path.relpath(path, bundle_root).replace(os.sep, "/"), activity))
    return rows


def run_cli(argv: list[str]) -> int:
    cfg = _load_config(_project_dir())
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("-")]
    target = paths[0] if paths else "docs"
    ignore_globs = tuple(cfg.get("ignoreGlobs") or ())
    # The figure is its OWN output, never a section of the report. `stale-doc` was retired
    # because the comparison cannot support a verdict; printing the numbers beside findings
    # would rebuild the verdict out of adjacency. It also exits 0 whatever it prints — there
    # is no interval that is a failure.
    if "--activity" in argv:
        rows = _activity_rows(target, ignore_globs)
        if as_json:
            print(json.dumps([dict(activity, path=rel) for rel, activity in rows], indent=2))
        else:
            print(_render_activity(rows, target))
        return OK
    # no deadline in CLI mode — always a full scan
    findings = validate_tree(target, ignore_globs=ignore_globs)
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


def run_project(argv: list[str]) -> int:
    """Materialize or verify the glossary's abbreviation snippet without importing Zensical.

    `--plan`, `--config` and `--route` are gone with the derived glossary route they served: the
    canonical glossary is staged as `glossary.md` in `site-source`, and no second editable copy
    exists.
    """
    import argparse

    parser = argparse.ArgumentParser(prog="cq knowledge project")
    parser.add_argument("bundle", nargs="?", default="docs")
    parser.add_argument("--snippet", default=DEFAULT_SNIPPET)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the deterministic projection")
    mode.add_argument("--check", action="store_true", help="check without writing (the default)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    from pathlib import Path

    bundle = Path(args.bundle)
    if args.write:
        written = write_projection(bundle, args.snippet)
        payload = dict(written)
        errors: list[dict] = []
        if not written.get("skipped"):
            checked, errors = projection_findings(bundle, args.snippet)
            payload.update(checked)
        payload["mode"] = "write"
    else:
        payload, errors = projection_findings(bundle, args.snippet)
        payload["mode"] = "check"
    payload["findings"] = errors
    payload["ok"] = not errors
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"knowledge projection — {payload.get('mode')} ({len(errors)} error(s))")
        for error in errors:
            print(f"  [ERROR] {error['path']}: {error['message']} ({error['code']})")
        if not errors:
            print("  OK — glossary projection is current.")
    return FINDINGS if errors else OK


def run_nav(argv: list[str]) -> int:
    """Generate the site `nav` from the bundle tree, or prove the one on disk is current.

    `--check` is the gate `site-nav-stale` reads: it is a byte comparison, because the generator
    is idempotent by construction. Anything it would change is a diff, never a judgement call."""
    import argparse

    parser = argparse.ArgumentParser(prog="cq knowledge nav")
    parser.add_argument("bundle", nargs="?", default="docs")
    parser.add_argument("--config", default="zensical.toml",
                        help="root zensical.toml whose nav is generated (default: zensical.toml)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the generated nav")
    mode.add_argument("--check", action="store_true", help="check without writing (the default)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    from quenching.knowledge.nav import generate

    if not os.path.isdir(args.bundle):
        payload = {"ok": False, "code": "nav-no-bundle",
                   "message": f"{args.bundle} is not a directory"}
        print(json.dumps(payload, indent=2) if args.json else f"error: {payload['message']}",
              file=None if args.json else sys.stderr)
        return FINDINGS

    current, desired = generate(args.bundle, args.config)
    if not current:
        payload = {"ok": False, "code": "nav-config-unreadable",
                   "message": f"{args.config} is missing or unreadable"}
        print(json.dumps(payload, indent=2) if args.json else f"error: {payload['message']}",
              file=None if args.json else sys.stderr)
        return FINDINGS

    stale = current != desired
    if stale and args.write:
        with open(args.config, "w", encoding="utf-8") as handle:
            handle.write(desired)
    payload = {"ok": not stale or args.write,
               "mode": "write" if args.write else "check",
               "config": args.config, "bundle": args.bundle,
               "changed": bool(stale and args.write),
               "findings": ([] if not stale or args.write else
                            [{"path": args.config, "code": "site-nav-stale",
                              "message": "the nav does not match the bundle tree — "
                                         "run `cq knowledge nav --write`"}])}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.write:
        print(f"knowledge nav — {'rewrote' if stale else 'already current:'} {args.config}")
    else:
        print(f"knowledge nav — {'STALE' if stale else 'current'}: {args.config}")
    return FINDINGS if payload["findings"] else OK


def run_site_source(argv: list[str]) -> int:
    """Stage or verify the small, explicit source tree used by Zensical."""
    import argparse

    parser = argparse.ArgumentParser(prog="cq knowledge site-source")
    parser.add_argument("bundle", nargs="?", default="docs")
    parser.add_argument("destination", nargs="?", default="site-source")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="replace the generated source tree")
    mode.add_argument("--check", action="store_true", help="check without writing (the default)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.write:
            payload = stage_site_source(args.bundle, args.destination)
            payload["mode"] = "write"
            errors: list[dict] = []
        else:
            payload, errors = site_source_findings(args.bundle, args.destination)
            payload["mode"] = "check"
        payload["findings"] = errors
        payload["ok"] = not errors
    except (OSError, ValueError) as exc:
        payload = {"ok": False, "mode": "write" if args.write else "check",
                   "findings": [{"code": "site-source-error", "message": str(exc)}]}

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        state = "OK" if payload["ok"] else "FINDINGS"
        print(f"knowledge site source — {state} ({payload.get('files', 0)} files)")
        for finding in payload["findings"]:
            print(f"  [ERROR] {finding.get('path', args.destination)}: "
                  f"{finding['message']} ({finding['code']})")
    return FINDINGS if payload["findings"] else OK


def main(argv: list[str]) -> int:
    """The pillar's whole entry: the declared token chooses the mode.

    THE MODE IS A VERB, NOT A HEURISTIC. The pre-refactor OKF validator script decided its mode by
    looking at the world: no `argv` **and** a non-tty stdin meant "hook". That test does not survive
    a pillar prefix, and it should not: it misfires under CI, under a subprocess, and under any
    redirection, silently and with no way to override it. `main` routes the DECLARED token —
    `validate` to `run_cli`, `project` to `run_project`, `nav` to `run_nav`, and nothing else now
    that `hook` is retired — and nothing in this
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
    if verb == "project":
        return run_project(argv[1:])
    if verb == "nav":
        return run_nav(argv[1:])
    if verb == "site-source":
        return run_site_source(argv[1:])
    print(USAGE, file=sys.stderr)
    return REFUSAL
