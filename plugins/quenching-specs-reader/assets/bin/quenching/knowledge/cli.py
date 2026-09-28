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

`validate`, `doctor`, `status`, `project`, `nav` and `site-source` are the verbs `main` routes. The `hook` verb (`quenching.knowledge.hook.run_hook`,
answering the plugin's self-installed `PostToolUse`/`Stop`/`PreToolUse` wiring) was retired along
with that wiring — this pillar no longer answers a hook event at all.

`selftest` IS NOT HERE. The canonical frontmatter cases and the two retirement fixtures are
tests and migrate to `tests/` in task 6.3, which is also where the intercept that kept a bare
subcommand from being scanned as a path went; whether the verb survives is 6.3's to decide,
and re-adding it is one branch in `main`.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import sys
from pathlib import Path

from quenching.common.frontmatter import parse_frontmatter
from quenching.common.output import FINDINGS, OK, REFUSAL, emit
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


def _rooted(root: str, path: str) -> str:
    """Resolve a pillar-relative path under the caller's repository root."""
    return os.path.normpath(path if os.path.isabs(path) else os.path.join(root, path))


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


HOMES = ("standards", "vision", "tutorials", "how-to", "explanation", "project",
         "concepts", "external", "catalog")
EXEMPT_DENSITY_NAMES = {"index.md", "log.md", "CLAUDE.md", "AGENTS.md"}


def _knowledge_findings(findings: list[tuple[str, str, str, str]] | None) -> list[dict]:
    return [{"severity": severity.lower(), "path": path, "code": code, "message": message}
            for severity, path, code, message in (findings or [])]


def _density(bundle_root: str) -> dict:
    """Return the status figures without turning any figure into a finding."""
    root = Path(bundle_root)
    docs = [path for path in root.rglob("*.md")
            if not any(part.startswith((".", "_")) for part in path.relative_to(root).parts)]
    concept_docs = [path for path in docs if path.name not in EXEMPT_DENSITY_NAMES]
    per_home = {home: 0 for home in HOMES if (root / home).is_dir()}
    for path in concept_docs:
        relative = path.relative_to(root).parts
        if relative and relative[0] in per_home:
            per_home[relative[0]] += 1
    glossary_terms = 0
    glossary = root / "glossary.md"
    if glossary.is_file():
        in_terms = False
        for line in glossary.read_text(encoding="utf-8").splitlines():
            if line.strip().casefold() == "## terms":
                in_terms = True
            elif in_terms and line.startswith("## "):
                break
            elif in_terms and line.lstrip().startswith(("- ", "* ")):
                glossary_terms += 1
    standards = root / "standards"
    subjects = sorted(path.name for path in standards.iterdir()
                      if path.is_dir()) if standards.is_dir() else []
    timestamps = []
    for path in concept_docs:
        try:
            timestamp = parse_frontmatter(path.read_text(encoding="utf-8")).get("timestamp")
        except (OSError, UnicodeDecodeError):
            timestamp = None
        if timestamp:
            timestamps.append(str(timestamp))
    logs = sorted(str(path.relative_to(root)) for path in docs if path.name == "log.md")
    return {
        "conceptDocs": {"total": len(concept_docs), "perHome": per_home},
        "glossary": {"terms": glossary_terms},
        "standards": {"subjects": len(subjects), "withDocs": sum(
            any(child.is_file() and child.suffix == ".md" and child.name not in EXEMPT_DENSITY_NAMES
                for child in (standards / subject).iterdir())
            for subject in subjects)},
        "lastActivity": max(timestamps) if timestamps else None,
        "retiredLogs": {"count": len(logs), "paths": logs},
    }


def _surface_payload(bundle_root: str, *, density: bool = False) -> dict:
    if not os.path.isdir(bundle_root):
        return {"root": bundle_root, "applicable": False, "state": "missing",
                "findings": [], "errors": 0, "warnings": 0, "ok": True,
                **({"density": {}} if density else {})}
    findings = _knowledge_findings(validate_tree(bundle_root))
    payload = {
        "root": bundle_root,
        "applicable": True,
        "state": "conformant" if not findings else "findings",
        "findings": findings,
        "errors": sum(item["severity"] == "error" for item in findings),
        "warnings": sum(item["severity"] == "warn" for item in findings),
        "ok": not findings,
    }
    if density:
        payload["density"] = _density(bundle_root)
    return payload


def _knowledge_args(argv: list[str], prog: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("bundle", nargs="?", default="docs")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def _run_doctor(argv: list[str]) -> int:
    args = _knowledge_args(argv, "cq knowledge doctor")
    payload = _surface_payload(_rooted(args.root, args.bundle))
    if not payload["applicable"]:
        payload["message"] = "knowledge bundle is not installed; run knowledge align to install it"
    emit(args.json, payload,
         f"knowledge doctor — {payload['root']} ({len(payload['findings'])} finding(s))")
    return 0 if payload["ok"] else FINDINGS


def _run_status(argv: list[str]) -> int:
    args = _knowledge_args(argv, "cq knowledge status")
    payload = _surface_payload(_rooted(args.root, args.bundle), density=True)
    payload["findingCodes"] = dict(sorted(Counter(item["code"] for item in payload["findings"]).items()))
    emit(args.json, payload,
         f"knowledge status — {payload['root']} ({payload['density'].get('conceptDocs', {}).get('total', 0)} document(s))")
    return 0 if payload["ok"] else FINDINGS


def run_cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="cq knowledge validate",
        description="validate the OKF bundle without writing it",
    )
    parser.add_argument("bundle", nargs="?", default="docs")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--activity", action="store_true", help="report activity instead of findings")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    cfg = _load_config(_project_dir())
    as_json = args.json
    target = _rooted(args.root, args.bundle)
    ignore_globs = tuple(cfg.get("ignoreGlobs") or ())
    # The figure is its OWN output, never a section of the report. `stale-doc` was retired
    # because the comparison cannot support a verdict; printing the numbers beside findings
    # would rebuild the verdict out of adjacency. It also exits 0 whatever it prints — there
    # is no interval that is a failure.
    if args.activity:
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
    parser = argparse.ArgumentParser(prog="cq knowledge project")
    parser.add_argument("bundle", nargs="?", default="docs")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--snippet", default=DEFAULT_SNIPPET)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the deterministic projection")
    mode.add_argument("--check", action="store_true", help="check without writing (the default)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    bundle = Path(_rooted(args.root, args.bundle))
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
    parser = argparse.ArgumentParser(prog="cq knowledge nav")
    parser.add_argument("bundle", nargs="?", default="docs")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--config", default="zensical.toml",
                        help="root zensical.toml whose nav is generated (default: zensical.toml)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the generated nav")
    mode.add_argument("--check", action="store_true", help="check without writing (the default)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    from quenching.knowledge.nav import generate

    bundle = _rooted(args.root, args.bundle)
    config = _rooted(args.root, args.config)
    if not os.path.isdir(bundle):
        payload = {"ok": False, "code": "nav-no-bundle",
                   "message": f"{bundle} is not a directory"}
        print(json.dumps(payload, indent=2) if args.json else f"error: {payload['message']}",
              file=None if args.json else sys.stderr)
        return FINDINGS

    current, desired = generate(bundle, config)
    if not current:
        payload = {"ok": False, "code": "nav-config-unreadable",
                   "message": f"{config} is missing or unreadable"}
        print(json.dumps(payload, indent=2) if args.json else f"error: {payload['message']}",
              file=None if args.json else sys.stderr)
        return FINDINGS

    stale = current != desired
    if stale and args.write:
        with open(config, "w", encoding="utf-8") as handle:
            handle.write(desired)
    payload = {"ok": not stale or args.write,
               "mode": "write" if args.write else "check",
               "config": config, "bundle": bundle,
               "changed": bool(stale and args.write),
               "findings": ([] if not stale or args.write else
                            [{"path": config, "code": "site-nav-stale",
                              "message": "the nav does not match the bundle tree — "
                                         "run `cq knowledge nav --write`"}])}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.write:
        print(f"knowledge nav — {'rewrote' if stale else 'already current:'} {config}")
    else:
        print(f"knowledge nav — {'STALE' if stale else 'current'}: {config}")
    return FINDINGS if payload["findings"] else OK


def run_site_source(argv: list[str]) -> int:
    """Stage or verify the small, explicit source tree used by Zensical."""
    parser = argparse.ArgumentParser(prog="cq knowledge site-source")
    parser.add_argument("bundle", nargs="?", default="docs")
    parser.add_argument("destination", nargs="?", default="site-source")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="replace the generated source tree")
    mode.add_argument("--check", action="store_true", help="check without writing (the default)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    bundle = _rooted(args.root, args.bundle)
    destination = _rooted(args.root, args.destination)

    try:
        if args.write:
            payload = stage_site_source(bundle, destination)
            payload["mode"] = "write"
            errors: list[dict] = []
        else:
            payload, errors = site_source_findings(bundle, destination)
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
            print(f"  [ERROR] {finding.get('path', destination)}: "
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
    parser = argparse.ArgumentParser(
        prog="cq knowledge",
        description="the OKF bundle — validate and stage documentation surfaces",
    )
    parser.add_argument("--root", help="repository root (default: current directory)")
    parser.add_argument("--version", action="version", version=f"cq knowledge {VERSION}")
    parser.add_argument("verb", nargs="?", choices=("validate", "doctor", "status", "project", "nav", "site-source"),
                        help="the knowledge operation")
    parser.add_argument("rest", nargs=argparse.REMAINDER,
                        help="the operation's bundle and options")
    args = parser.parse_args(argv)
    if not args.verb:
        parser.print_help(sys.stderr)
        return REFUSAL
    rest = list(args.rest)
    if args.root:
        rest = ["--root", args.root] + rest
    dispatch = {"validate": run_cli, "doctor": _run_doctor, "status": _run_status,
                "project": run_project,
                "nav": run_nav, "site-source": run_site_source}
    return dispatch[args.verb](rest)
