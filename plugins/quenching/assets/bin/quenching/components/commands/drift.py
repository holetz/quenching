"""drift — the installed copies against the plugin that ships them.

Moved verbatim out of `skills.py`.

Each of the three tools is COPIED into a target's `.claude/hooks/` by its own align, and that
offer is the only moment a version is ever compared. A repo that installed once and never
aligned again keeps whatever it got, indefinitely, and nothing says so. This subcommand is what
notices — without an align, and without writing.

It MUST run from the plugin's own copy. An installed copy's `VERSION` is the stale number under
test, so answering from it would report "all current" in exactly the case this exists to catch.
An unresolvable plugin root is a refusal (exit 2), never a guess.
"""
from __future__ import annotations

import json
import os
import re

from quenching.common.io import read_text
from quenching.common.output import exit_for, finding
from quenching.components.surface import HOOKS_DIR

PLUGIN_VERSION_FILE = "VERSION"

# The three tools a target repo may still carry a LEGACY copy of, each with the path it
# ships at and the align that offers to remove one. Nothing else under `.claude/hooks/`
# is this subcommand's business — a target's own scripts live there too, and auditing
# them would be a different claim.
#
# All three resolve plugin-first with no fallback and no manual rung
# (align/tool-resolution.md §Resolving the tool) — the plugin's own `hooks/hooks.json`
# wires `okf-validate.py`, and `specs.py`/`skills.py` are invoked by their literal plugin
# path. A copy under `.claude/hooks/` is therefore never executed by anything this plugin
# runs, regardless of version: it is dead weight to offer for removal, not a stale
# dependency to offer for overwrite.
INSTALLED_TOOLS = (
    {"tool": "okf-validate.py", "ships": "assets/hooks/okf-validate.py", "align": "/docs:align"},
    {"tool": "specs.py", "ships": "assets/bin/specs.py", "align": "/specs:align"},
    {"tool": "skills.py", "ships": "assets/bin/skills.py", "align": "/skill:align"},
)

# Each tool declares `VERSION = "x.y.z"` at module level, in lockstep with the plugin's
# VERSION file. Reading the constant — rather than running the script for `--version` —
# keeps this a READ: `drift` is called from probes, and a probe that executes whatever
# sits in a target's `.claude/hooks/` is a different and much larger claim than one that
# reads three lines. A copy too old to declare one reads `unreadable`, which carries the
# same call to action as `behind`.
VERSION_CONSTANT_RE = re.compile(r'^VERSION\s*=\s*["\']([^"\']+)["\']', re.M)


def read_tool_version(path: str) -> str | None:
    text = read_text(path)
    if text is None:
        return None
    m = VERSION_CONSTANT_RE.search(text)
    return m.group(1).strip() if m else None


def _version_key(v: str) -> tuple | None:
    """`4.2.0` -> (4, 2, 0). Anything not purely numeric-dotted returns None, and an
    unorderable pair is reported as `unreadable` rather than ordered on a guess."""
    parts = v.split(".")
    if not all(p.isdigit() for p in parts):
        return None
    return tuple(int(p) for p in parts)


def compare_versions(installed: str | None, shipped: str) -> str:
    """`current` · `behind` · `ahead` · `unreadable`, for a copy that IS on disk —
    `absent` is the caller's, because "no file" and "a file I could not read" are
    different facts and only one of them is a repo that thinks it is protected.

    Both directions are reported because both are silent. Resolution is plugin-only
    (align/tool-resolution.md §Resolving the tool) while every align deliberately leaves a NEWER
    installed copy alone — so an `ahead` copy is code that is never executed and never
    repaired, and both halves of that are correct behaviour saying nothing."""
    if installed is None:
        return "unreadable"
    a, b = _version_key(installed), _version_key(shipped)
    if a is None or b is None:
        return "unreadable"
    return "current" if a == b else ("behind" if a < b else "ahead")


def drift_rows(root: str, plugin_root: str, shipped: str) -> list[dict]:
    """One row per tool. `executes` is the copy a command actually runs: resolution is
    plugin-first with no fallback and no manual rung, so it is always the plugin's —
    which is exactly what makes ANY row that is not `absent` a legacy copy worth
    reporting, regardless of its version."""
    rows = []
    for spec in INSTALLED_TOOLS:
        installed_path = os.path.join(root, HOOKS_DIR, spec["tool"])
        present = os.path.isfile(installed_path)
        installed = read_tool_version(installed_path) if present else None
        # the SHIPPED tool's own constant, not the plugin's VERSION file: it is what a
        # legacy copy was installed from, so it is what one is compared against for the
        # report. The two agreeing is the lockstep's business, checked elsewhere.
        tool_shipped = read_tool_version(os.path.join(plugin_root, spec["ships"])) or shipped
        rows.append({
            "tool": spec["tool"],
            "align": spec["align"],
            "installedPath": installed_path if present else None,
            "installed": installed,
            "shipped": tool_shipped,
            "status": "absent" if not present else compare_versions(installed, tool_shipped),
            "executes": "plugin",
        })
    return rows


def drift_findings(rows: list[dict]) -> list[dict]:
    """One finding per row carrying a legacy copy, each naming the align that offers to
    remove it. `absent` is the expected, unreported state for all three tools now:
    resolution is plugin-first with no fallback and no manual rung
    (align/tool-resolution.md §Resolving the tool), so a copy under `.claude/hooks/` is
    never executed by anything this plugin runs — a stale one is dead weight to remove,
    not a dependency to overwrite, and its version only explains what kind of debris it
    is."""
    out: list[dict] = []
    for r in rows:
        tool, align = r["tool"], r["align"]
        if r["status"] == "behind":
            out.append(finding(
                "sk-tool-behind", "warn",
                f"{HOOKS_DIR}/{tool} is a legacy copy ({r['installed']}, the plugin ships "
                f"{r['shipped']}) — nothing executes it, since resolution is plugin-first "
                "with no fallback",
                tool=tool, installed=r["installed"], shipped=r["shipped"],
                remedy=f"{align} offers to remove it"))
        elif r["status"] == "ahead":
            out.append(finding(
                "sk-tool-ahead", "warn",
                f"{HOOKS_DIR}/{tool} is a legacy copy ({r['installed']}, ahead of the plugin's "
                f"{r['shipped']}) — nothing executes it, since resolution is plugin-first "
                "with no fallback",
                tool=tool, installed=r["installed"], shipped=r["shipped"],
                remedy=f"{align} offers to remove it"))
        elif r["status"] == "unreadable":
            out.append(finding(
                "sk-tool-unreadable", "warn",
                f"{HOOKS_DIR}/{tool} declares no `VERSION = \"…\"` — a legacy copy too old or "
                "edited in place to identify, and unexecuted either way",
                tool=tool, remedy=f"{align} offers to remove it"))
    return out


def resolve_plugin_root(arg: str | None) -> str | None:
    """`--plugin-root` when given, else the plugin checkout this script runs from.

    A plugin holds `VERSION` beside `assets/`, so walking up from `assets/bin/skills.py`
    finds it in two hops. A copy installed at `.claude/hooks/skills.py` has no such
    parent — which is the case that must refuse rather than answer."""
    if arg:
        candidates = [arg]
    else:
        candidates, d = [], os.path.dirname(os.path.abspath(__file__))
        # THE SEED, AND THE ONLY LINE THE MOVE CHANGED. The walk above used to start from
        # `assets/bin/skills.py`'s own directory; this module sits three packages deeper
        # (`quenching/components/commands/`), so the three hops below put the walk back
        # where it has always started. The `range(4)` that follows is untouched.
        for _ in range(3):
            d = os.path.dirname(d)
        for _ in range(4):
            candidates.append(d)
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    for c in candidates:
        if (os.path.isfile(os.path.join(c, PLUGIN_VERSION_FILE))
                and os.path.isdir(os.path.join(c, "assets"))):
            return os.path.abspath(c)
    return None


def _drift_refusal(args, given: str | None) -> int:
    """Exit 2 — the refusal branch of the 0 ok / 1 findings / 2 refusal contract. A
    caller that cannot tell "no drift" from "could not look" would report the silence
    this whole subcommand exists to break."""
    if given:
        message = (f"--plugin-root {given} holds no {PLUGIN_VERSION_FILE} beside an "
                   f"assets/ directory — it is not a plugin checkout")
    else:
        message = ("cannot resolve the plugin this script ships with — `drift` must run "
                   "from the plugin's own copy, because an installed copy would answer "
                   "from the same stale VERSION it is being asked about")
    remedy = ("run `python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py drift`, or pass "
              "--plugin-root <the plugin checkout>")
    if args.json:
        print(json.dumps({"ok": False, "refused": message, "remedy": remedy},
                         indent=2, ensure_ascii=False))
    else:
        print("skills drift — refused")
        print(f"  {message}")
        print(f"  remedy: {remedy}")
    return 2


def cmd_drift(args, root: str) -> int:
    given = getattr(args, "plugin_root", None)
    plugin_root = resolve_plugin_root(given)
    if plugin_root is None:
        return _drift_refusal(args, given)
    shipped = (read_text(os.path.join(plugin_root, PLUGIN_VERSION_FILE)) or "").strip()
    rows = drift_rows(root, plugin_root, shipped)
    findings = drift_findings(rows)
    payload = {"root": root, "pluginRoot": plugin_root, "shipped": shipped, "tools": rows}
    if args.json:
        print(json.dumps({"ok": not findings, **payload, "findings": findings},
                         indent=2, ensure_ascii=False))
        return exit_for(findings)
    print(f"skills drift — {root} against plugin {shipped} ({plugin_root})")
    for r in rows:
        print(f"  {r['status']:<10} {r['tool']:<18} installed "
              f"{r['installed'] or '-':<8} shipped {r['shipped']:<8} "
              f"executes: {r['executes']}")
    for f in findings:
        print(f"  [{f['severity']:<5}] {f['message']}  ({f['code']})")
        print(f"          remedy: {f['remedy']}")
    if not findings:
        print("  OK — no legacy copy found.")
    return exit_for(findings)
