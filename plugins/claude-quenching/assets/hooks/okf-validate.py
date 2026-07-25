#!/usr/bin/env python3
"""okf-validate.py — self-contained OKF v0.1 conformance checker for a docs/ bundle.

Payload of the `claude-quenching` plugin. Generic, portable, ZERO dependencies
(a minimal frontmatter parser — no PyYAML). It is the **executable enforcement**
that keeps a target repo's `docs/` bundle aligned to the Open Knowledge Format
after `quenching-docs-align` has installed it: the skills call it, the verification step calls
it, and it wires into the target's `.claude/settings.json` as a hook so future edits
stay conformant.

TWO ENTRY MODES
---------------
1. **CLI**  `okf-validate.py <bundle-or-docs-dir> [--json] [--listing-root]`
   Validates the whole bundle rooted at the given directory (walks every `.md`),
   prints a human report, and exits **0** when there are no errors, **1** otherwise.
   This is what `quenching-docs-align`/`quenching-docs-add` invoke and what the plugin's own
   verification runs over `assets/docs/`.
   `--listing-root` validates a quenching-managed tree that is **not** an OKF bundle
   root — today that means `specs/backlog/`. The scanned directory's `index.md` is
   then held to the plain-listing rule (frontmatter-free, ERROR if it carries any)
   instead of the bundle-root rule (`okf_version` expected), and the `bundle-no-index`
   SHOULD is dropped. Everything else — concept docs need a non-empty `type`, no index
   carries a `type`, links resolve, nothing is orphaned — applies unchanged. This is
   what lets the backlog skills replace a prose self-check with a real check.

2. **HOOK**  (no path arg → reads the hook JSON on stdin)
   Dispatches on `hook_event_name`:
   - **PostToolUse** (matcher `Write|Edit`): validates the single touched
     `docs/**` file and, on a finding, **PROPOSES** the fix via
     `additionalContext` (exit 0). With `blockOnFail: true` it escalates to
     `decision: block` (the reason is fed back to Claude). It also touches the
     **dirty marker** (a stamp file in the system temp dir) so the Stop sweep
     knows the bundle changed this session.
   - **Stop**: with `stopScan: "dirty"` (the default), exits immediately when
     the dirty marker is absent — a turn that touched no `docs/**` file costs
     one stat, not a full-bundle scan. When the marker is present (or
     `stopScan: "always"`), validates the whole bundle in a SINGLE read pass
     and PROPOSES residual gaps (`additionalContext`, exit 0); the marker is
     cleared after any completed scan and kept when the deadline aborts one.
     Honors `stop_hook_active` to avoid loops.
   - **PreToolUse** (matcher `Write|Edit`, OPT-IN via `hardBlock: true`): inspects
     the *pending* `tool_input.content` and **BLOCKS** (`permissionDecision: deny`)
     only the two hard violations — writing an `index.md` that carries a concept
     `type`, or writing a concept doc with no non-empty `type`. This is the single
     hard gate; everything else proposes. Off by default (proposes, never blocks).

THE CONFORMANCE CORE (single source — mirrored in the skills' `references/conformance.md`)
-----------------------------------------------------------------------------------------
Reserved filenames: `index.md` (a listing), `log.md` (a change history).
Exempt (skipped): `CLAUDE.md`/`AGENTS.md` (harness pointers, never OKF concepts) and
`QUENCHING.md` (the operator manual the aligns install beside each front — a payload
file, not authored knowledge).
`README.md` in the bundle → WARN (OKF-strict converts it to `index.md`).
- Every **non-reserved** `.md`  → MUST have parseable YAML frontmatter (ERROR if
  absent/broken) with a **non-empty `type`** (ERROR if missing/empty). Recommended
  fields (`title`/`description`/`resource`/`timestamp`) missing → WARN.
- Every **`index.md`**          → MUST NOT carry a concept `type` (ERROR). A
  **non-root** `index.md` MUST carry no frontmatter at all (ERROR). The **root**
  `index.md` (at the bundle root) MAY carry frontmatter but only `okf_version`
  (other keys → WARN); it SHOULD declare `okf_version: "0.1"` (missing/other value → WARN).
- Every **`log.md`**            → entries under `## YYYY-MM-DD` headings, newest
  first (no date heading → WARN; ascending order → WARN); a `type` here → ERROR.

STRUCTURAL INTEGRITY (whole-tree only — CLI + Stop; all WARN, OKF-tolerant)
- **`dir-no-index`**      a directory holds concept docs but has no `index.md` listing.
- **`index-broken-link`** an `index.md` links to a `.md`/dir that does not exist on disk.
- **`index-orphan`**      a concept doc nothing links to (unlisted / not discoverable).
These stay WARN by design (OKF says consumers MUST tolerate broken links and MAY
synthesize a missing index); the `quenching-docs-align`/`quenching-docs-add` skills treat them as must-fix
in their own verify gate. `_`-prefixed, dot, and asset dirs are pruned from the whole
bundle walk (they hold private/raw sidecar content, never OKF concepts), and every
whole-tree check consumes ONE shared read pass over the tree (`_build_corpus`).

Config (`hooks-config.json` + `hooks-config.local.json`, block `okfValidate`):
  enabled, docsDir, warnAsError, blockOnFail, hardBlock, deadlineMs, stopScan.
An empty/absent config uses the defaults below; `enabled: false` makes the hook inert.

Trust note: hook config is executable code with shell privileges. This script reads
the touched path/content and prints; the only thing it ever writes is the dirty-marker
stamp file in the system temp dir. Version and review it like infra.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile
import time

VERSION = "1.1.0"  # kept in lockstep with the plugin VERSION file (and specs.py)

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "okf"
RESERVED = ("index.md", "log.md")
# Navigation/payload files — never OKF concepts, never required to carry a `type`.
# `CLAUDE.md`/`AGENTS.md` are agent-pointers auto-loaded by the harness; `QUENCHING.md`
# is the operator manual the `claude-quenching` aligns install beside each front they
# own (`docs/`, `specs/`, `.claude/`). Skip all three.
EXEMPT = ("CLAUDE.md", "AGENTS.md", "QUENCHING.md")
RECOMMENDED = ("title", "description", "resource", "timestamp")
# Types for which `resource` is deliberately absent, so its WARN would be permanent noise.
# A `task` is parked work — nothing is built yet to point at (the backlog task mold omits
# the key on purpose). Every other type anchors to code, an asset, or a URI.
TYPES_WITHOUT_RESOURCE = ("task",)
DATE_HEADING = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\b")
# Directories that never need an `index.md` and hold no OKF concepts: `_`-prefixed
# private/raw sidecar folders (`_curadoria/`, `_azimutt/`), dotfolders, and common
# asset dirs. Pruned from the structural walk (dir-index / broken-link / orphan).
ASSET_DIRS = ("img", "imgs", "images", "assets", "static", "media", "node_modules", "__pycache__")
# Markdown inline-link target: capture what sits between `](` and the closing `)`.
LINK_RE = re.compile(r"\]\(([^)]+)\)")

DEFAULTS: dict = {
    "enabled": True,
    "docsDir": "docs",          # bundle root, relative to the project root
    "warnAsError": False,       # CLI: treat warnings as failures (exit 1)
    "blockOnFail": False,       # PostToolUse/Stop: escalate proposal to decision:block
    "hardBlock": False,         # PreToolUse: enable the hard deny gate (off = propose-only)
    "deadlineMs": 4000,
    "stopScan": "dirty",        # Stop: "dirty" = scan only after a docs/** edit; "always" = every turn
    "ignoreGlobs": [],          # docsDir-relative dir-prefix/fnmatch globs pruned from every scan
}


# --------------------------------------------------------------------------- #
# config + IO
# --------------------------------------------------------------------------- #
def _load_config() -> dict:
    cfg = dict(DEFAULTS)
    for name in ("hooks-config.json", "hooks-config.local.json"):
        path = os.path.join(HERE, name)
        if not pathlib.Path(path).exists():
            continue
        try:
            with pathlib.Path(path).open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        cfg.update(data.get("okfValidate") or {})
    return cfg


def _read_stdin() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (OSError, json.JSONDecodeError):
        return {}


def _project_dir(data: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()


# --------------------------------------------------------------------------- #
# dirty marker — the only thing this script ever writes (a stamp in tempdir)
# --------------------------------------------------------------------------- #
def _marker_path(project: str) -> str:
    digest = hashlib.sha1(os.path.abspath(project).encode("utf-8")).hexdigest()[:12]
    return os.path.join(tempfile.gettempdir(), f"okf-dirty-{digest}")


def _touch_marker(project: str) -> None:
    try:
        pathlib.Path(_marker_path(project)).touch()
    except OSError:
        pass  # marker is an optimization; never fail the hook over it


def _clear_marker(project: str) -> None:
    try:
        os.remove(_marker_path(project))
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# minimal frontmatter parser (no external deps)
# --------------------------------------------------------------------------- #
def parse_frontmatter(text: str):
    """Return (fm, has_block, well_formed).

    fm          -- dict of the top-level `key: value` pairs (values as strings,
                   surrounding quotes stripped). Empty dict when there is no block.
    has_block   -- True if the file opens with a `---` fence.
    well_formed -- True if the opening fence has a matching closing `---`.
    Nested/complex YAML is not modeled — only the top-level scalar keys the
    conformance core inspects (`type`, `okf_version`, the recommended fields).
    """
    if not text.startswith("---"):
        return {}, False, True
    lines = text.splitlines()
    # first line is the opening fence (--- possibly with trailing spaces)
    if lines[0].strip() != "---":
        return {}, False, True
    close = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close = i
            break
    if close is None:
        return {}, True, False  # opened a fence, never closed → malformed
    fm: dict = {}
    for raw in lines[1:close]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1] in (" ", "\t"):  # nested value — skip (top-level keys only)
            continue
        if ":" not in raw:
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        fm[key] = val
    return fm, True, True


def _nonempty(fm: dict, key: str) -> bool:
    return bool(str(fm.get(key, "")).strip())


# --------------------------------------------------------------------------- #
# the conformance core — one function per file kind, returns (severity, code, msg)
# --------------------------------------------------------------------------- #
def check_concept(text: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    fm, has_block, well_formed = parse_frontmatter(text)
    if not has_block:
        out.append(("ERROR", "no-frontmatter",
                    "concept doc has no YAML frontmatter (needs a `---` block with a non-empty `type`)"))
        return out
    if not well_formed:
        out.append(("ERROR", "broken-frontmatter",
                    "frontmatter opens with `---` but never closes"))
        return out
    if not _nonempty(fm, "type"):
        out.append(("ERROR", "missing-type",
                    "frontmatter has no non-empty `type` (OKF requires it on every concept doc)"))
    recommended = RECOMMENDED
    if str(fm.get("type", "")).strip() in TYPES_WITHOUT_RESOURCE:
        recommended = tuple(k for k in RECOMMENDED if k != "resource")
    for key in recommended:
        if not _nonempty(fm, key):
            out.append(("WARN", f"missing-{key}",
                        f"recommended field `{key}` is absent (OKF recommends it)"))
    return out


def check_index(text: str, is_root: bool) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    fm, has_block, well_formed = parse_frontmatter(text)
    if has_block and not well_formed:
        out.append(("ERROR", "broken-frontmatter", "frontmatter opens with `---` but never closes"))
        return out
    if _nonempty(fm, "type"):
        out.append(("ERROR", "index-has-type",
                    "`index.md` is a reserved listing and must not carry a concept `type`"))
    if is_root:
        if not has_block:
            out.append(("WARN", "root-no-okf-version",
                        "root `index.md` should declare `okf_version: \"0.1\"`"))
        else:
            ver = str(fm.get("okf_version", "")).strip()
            if not ver:
                out.append(("WARN", "root-no-okf-version",
                            "root `index.md` frontmatter should declare `okf_version`"))
            elif ver != "0.1":
                out.append(("WARN", "root-okf-version-mismatch",
                            f"root `index.md` declares okf_version `{ver}` (this plugin targets 0.1)"))
            extra = [k for k in fm if k != "okf_version"]
            if extra:
                out.append(("WARN", "root-extra-keys",
                            f"root `index.md` frontmatter should carry only `okf_version` (found: {', '.join(extra)})"))
    else:
        if has_block:
            out.append(("ERROR", "index-has-frontmatter",
                        "a non-root `index.md` must have no frontmatter (it is a listing, not a concept)"))
    return out


def check_log(text: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    fm, has_block, _ = parse_frontmatter(text)
    if _nonempty(fm, "type"):
        out.append(("ERROR", "log-has-type", "`log.md` is a reserved change history and must not carry a `type`"))
    dates: list[str] = []
    for line in text.splitlines():
        m = DATE_HEADING.match(line)
        if m:
            dates.append(m.group(1))
    body = text.split("---", 2)[-1] if has_block else text
    if body.strip() and not dates:
        out.append(("WARN", "log-no-date-heading",
                    "`log.md` has content but no `## YYYY-MM-DD` heading (expected date-grouped entries)"))
    if dates and dates != sorted(dates, reverse=True):
        out.append(("WARN", "log-not-newest-first",
                    "`log.md` date headings are not in newest-first order"))
    return out


# --------------------------------------------------------------------------- #
# single-pass corpus — every whole-tree consumer reads each file exactly once
# --------------------------------------------------------------------------- #
def _is_skipped_dir(name: str) -> bool:
    """A directory pruned from the bundle walk: dotfolder, `_`-prefixed
    private/raw sidecar (`_curadoria/`), `.git`, or a known asset dir."""
    return (name.startswith(".") or name.startswith("_") or name in ASSET_DIRS)


def _is_ignored_path(rel_path: str, patterns: tuple[str, ...]) -> bool:
    """`rel_path` is bundle-relative, forward-slash. A pattern matches as a
    dir-prefix (`rel_path == pattern` or `rel_path` starts with `pattern + "/"`)
    or, failing that, as an `fnmatch` glob — per `ignoreGlobs` in hooks-config.json
    (regenerable/vendored trees like the gitignored mirrors under
    `reference/repositories/` are not authored OKF knowledge)."""
    for pat in patterns:
        pat = str(pat).strip("/")
        if not pat:
            continue
        if rel_path == pat or rel_path.startswith(pat + "/"):
            return True
        if fnmatch.fnmatch(rel_path, pat):
            return True
    return False


def _build_corpus(bundle_root: str, deadline: float | None = None,
                   ignore_globs: tuple[str, ...] = ()):
    """One `os.walk` over the bundle (skipped/ignored dirs pruned), each `.md`
    read ONCE.

    Returns `{abspath: text}` — text is None for an unreadable file — or **None**
    when `deadline` (a `time.monotonic()` instant) expires mid-walk, so hook mode
    can abort silently instead of delaying the turn. CLI mode passes no deadline.
    Both the per-file conformance checks and the structural-integrity pass consume
    this dict; nothing whole-tree reads from disk after it is built.
    """
    corpus: dict[str, str | None] = {}
    root = os.path.abspath(bundle_root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        rel_dir = "" if rel_dir == "." else rel_dir
        dirnames[:] = [
            d for d in dirnames
            if not _is_skipped_dir(d)
            and not _is_ignored_path(f"{rel_dir}/{d}" if rel_dir else d, ignore_globs)
        ]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            if deadline is not None and time.monotonic() > deadline:
                return None
            ap = os.path.join(dirpath, fn)
            try:
                corpus[ap] = pathlib.Path(ap).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                corpus[ap] = None
    return corpus


# --------------------------------------------------------------------------- #
# structural integrity — directory/index checks (whole-tree only)
# --------------------------------------------------------------------------- #


def _strip_noise(text: str) -> str:
    """Remove HTML comments, fenced blocks, and inline code before link extraction
    so example links (e.g. inside the standards `<!-- GENERATED -->` mold) are not
    mistaken for real listing entries."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def _link_targets(text: str) -> list[str]:
    """Return the raw target of every markdown inline link, noise stripped."""
    out: list[str] = []
    for m in LINK_RE.finditer(_strip_noise(text)):
        raw = m.group(1).strip()
        raw = raw.split()[0] if raw.split() else ""   # drop an optional "title"
        raw = raw.strip("<>")
        if raw:
            out.append(raw)
    return out


def _resolve_link(target: str, file_dir: str, root: str):
    """Resolve a WITHIN-BUNDLE markdown/dir link to (abspath, kind) or None to skip.

    kind is 'md' (a `.md` page) or 'dir' (a folder listing). Returns None — never
    flagged — for anything OKF does not govern: external URLs, anchors, mailto/tel,
    non-markdown assets (`.png`/`.pdf`/…), links that escape the bundle root
    (repo files, `../..` climbs), and repo-absolute `/…` links not written in the
    bundle's own form (`/docs/…` or `/<home>/…`). We only police the bundle's own
    link graph, so a legitimate reference to a repo file outside `docs/` is not a
    false "broken link".
    """
    t = target.split("#", 1)[0].strip()
    if not t:
        return None
    low = t.lower()
    if "://" in t or low.startswith(("mailto:", "tel:")):
        return None
    if t.startswith("/"):
        rest = t[1:]
        first, _, tail = rest.partition("/")
        if first == os.path.basename(root):          # `/docs/…` — this plugin's bundle-absolute form
            rest = tail
        elif not os.path.isdir(os.path.join(root, first)):
            return None                              # repo-absolute `/…` (e.g. `/.claude/…`) — not bundle-governed
        path = os.path.normpath(os.path.join(root, rest)) if rest else root
    else:
        path = os.path.normpath(os.path.join(file_dir, t))
    try:                                             # a link that climbs out of the bundle is not ours to police
        if os.path.commonpath([os.path.abspath(path), os.path.abspath(root)]) != os.path.abspath(root):
            return None
    except ValueError:
        return None
    if t.endswith("/"):
        return (path, "dir")
    if low.endswith(".md"):
        return (path, "md")
    if os.path.splitext(os.path.basename(t))[1] == "":   # extensionless → a directory listing
        return (path, "dir")
    return None                                      # some other asset — not our concern


def validate_structure(bundle_root: str, corpus: dict) -> list[tuple[str, str, str, str]]:
    """Whole-tree structural checks (all WARN — OKF tolerates missing indexes and
    broken links, so these are recommendations the skills fix, not hard failures):
      - `dir-no-index`      a folder holds concept docs but has no `index.md`.
      - `index-broken-link` an `index.md` links to a file/dir that does not exist.
      - `index-orphan`      a concept doc no `.md` in the bundle links to (unlisted).
    Consumes the `_build_corpus` dict — no disk reads of its own.
    """
    findings: list[tuple[str, str, str, str]] = []
    root = os.path.abspath(bundle_root)
    concept_md: list[str] = []   # abspath of every non-reserved concept doc
    index_md: list[str] = []     # abspath of every index.md
    indexed_dirs: set[str] = set()
    concept_dirs: set[str] = set()

    for ap in corpus:
        fn = os.path.basename(ap)
        if fn == "index.md":
            index_md.append(ap)
            indexed_dirs.add(os.path.dirname(ap))
        elif fn in RESERVED or fn in EXEMPT or fn == "README.md":
            continue
        else:
            concept_md.append(ap)
            concept_dirs.add(os.path.dirname(ap))

    for dirpath in sorted(concept_dirs - indexed_dirs):
        if os.path.abspath(dirpath) != root:
            rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
            findings.append(("WARN", rel + "/", "dir-no-index",
                             "directory holds concept docs but has no `index.md` listing"))

    # inbound-link corpus: any `.md` may make a concept doc discoverable
    linked: set[str] = set()
    for ap, text in corpus.items():
        if text is None:
            continue
        fdir = os.path.dirname(ap)
        for tgt in _link_targets(text):
            res = _resolve_link(tgt, fdir, root)
            if not res:
                continue
            path, kind = res
            if kind == "md" and os.path.normpath(path) != os.path.normpath(ap):
                linked.add(os.path.normpath(path))
            elif kind == "dir":
                linked.add(os.path.normpath(os.path.join(path, "index.md")))

    # broken links — only judged on `index.md` (the reserved listings)
    for ap in sorted(index_md):
        text = corpus.get(ap)
        if text is None:
            continue
        fdir = os.path.dirname(ap)
        rel = os.path.relpath(ap, root).replace(os.sep, "/")
        seen: set[str] = set()
        for tgt in _link_targets(text):
            res = _resolve_link(tgt, fdir, root)
            if not res or tgt in seen:
                continue
            seen.add(tgt)
            path, kind = res
            if kind == "md" and not os.path.isfile(path):
                findings.append(("WARN", rel, "index-broken-link",
                                 f"listing links to `{tgt}` but no such file exists"))
            elif kind == "dir" and not os.path.isdir(path):
                findings.append(("WARN", rel, "index-broken-link",
                                 f"listing links to `{tgt}` but no such directory exists"))

    # orphans — a concept doc nothing links to (not reachable from any listing/doc)
    for ap in sorted(concept_md):
        if os.path.normpath(ap) not in linked:
            rel = os.path.relpath(ap, root).replace(os.sep, "/")
            findings.append(("WARN", rel, "index-orphan",
                             "concept doc is not linked from any index.md or sibling doc "
                             "(unlisted — regenerate the folder's index.md)"))
    return findings


def validate_file(path: str, bundle_root: str,
                  listing_root: bool = False) -> list[tuple[str, str, str, str]]:
    """Return findings for one file as (severity, rel, code, message). Reads the
    file itself — the single-file entry point (PostToolUse); whole-tree callers
    go through `_build_corpus` + `_validate_text` instead."""
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [("ERROR", os.path.basename(path), "unreadable", f"cannot read file: {exc}")]
    return _validate_text(path, text, bundle_root, listing_root)


def _validate_text(path: str, text: str, bundle_root: str,
                   listing_root: bool = False) -> list[tuple[str, str, str, str]]:
    """Findings for one file whose text is already in hand (no disk read).

    `listing_root` marks a scan whose root is NOT an OKF bundle root (a
    quenching-managed sub-tree such as `specs/backlog/`): its `index.md` is a plain
    listing like any other, so the bundle-root exemption never applies."""
    rel = os.path.relpath(path, bundle_root).replace(os.sep, "/")
    base = os.path.basename(path)
    if base in EXEMPT:
        raw = []
    elif base == "index.md":
        is_root = (not listing_root) and \
            os.path.dirname(os.path.abspath(path)) == os.path.abspath(bundle_root)
        raw = check_index(text, is_root)
    elif base == "log.md":
        raw = check_log(text)
    elif base == "README.md":
        # OKF-strict uses `index.md` as the reserved listing; a README in the bundle
        # is a migration nudge, not a hard failure (OKF does not reserve README).
        raw = [("WARN", "readme-not-index",
                "OKF-strict uses `index.md` as the reserved listing — convert this README.md to index.md")]
    elif base.endswith(".md"):
        raw = check_concept(text)
    else:
        raw = []
    return [(sev, rel, code, msg) for (sev, code, msg) in raw]


def validate_tree(bundle_root: str, deadline: float | None = None,
                   ignore_globs: tuple[str, ...] = (),
                   listing_root: bool = False):
    """Validate the whole bundle from ONE read pass. Returns the findings list,
    or **None** when `deadline` (a `time.monotonic()` instant) expired mid-walk —
    hook mode aborts silently; CLI mode passes no deadline.

    `listing_root=True` scans a quenching-managed sub-tree (`specs/backlog/`) rather
    than an OKF bundle root: the root `index.md` is held to the plain-listing rule and
    the `bundle-no-index` SHOULD is dropped."""
    findings: list[tuple[str, str, str, str]] = []
    root = pathlib.Path(bundle_root)
    if not root.is_dir():
        return [("ERROR", str(bundle_root), "no-bundle", "bundle root is not a directory")]
    corpus = _build_corpus(bundle_root, deadline, ignore_globs)
    if corpus is None:
        return None
    for path in sorted(corpus):
        text = corpus[path]
        if text is None:
            findings.append(("ERROR", os.path.basename(path), "unreadable", "cannot read file"))
        else:
            findings.extend(_validate_text(path, text, bundle_root, listing_root))
    # bundle-level SHOULDs — a listing-root sub-tree is not a bundle and owes none of them
    if not listing_root and not (root / "index.md").exists():
        findings.append(("WARN", "index.md", "bundle-no-index", "bundle root has no `index.md`"))
    # whole-tree structural integrity (missing/broken/orphaned listings)
    findings.extend(validate_structure(bundle_root, corpus))
    return findings


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #
def _split(findings):
    errors = [f for f in findings if f[0] == "ERROR"]
    warns = [f for f in findings if f[0] == "WARN"]
    return errors, warns


def _render_text(findings, bundle_root: str) -> str:
    errors, warns = _split(findings)
    lines = [f"OKF conformance — {bundle_root} (okf-validate v{VERSION})",
             f"  {len(errors)} error(s), {len(warns)} warning(s)"]
    for sev, rel, code, msg in errors + warns:
        lines.append(f"  [{sev:<5}] {rel}: {msg}  ({code})")
    if not findings:
        lines.append("  OK — bundle conforms.")
    return "\n".join(lines)


def _render_proposal(findings) -> str:
    errors, warns = _split(findings)
    shown = (errors + warns)[:20]
    body = "\n".join(f"  - [{sev}] {rel}: {msg}" for sev, rel, code, msg in shown)
    return (f"[{TAG}] OKF conformance findings ({len(errors)} error(s), {len(warns)} warning(s)):\n"
            f"{body}\n"
            "Fix with the `quenching-docs-align` / `quenching-docs-add` skill (stamp `type`, keep `index.md` a "
            "frontmatter-free listing, format `log.md` as `## YYYY-MM-DD` newest-first).")


# --------------------------------------------------------------------------- #
# hook outputs
# --------------------------------------------------------------------------- #
def _emit_additional_context(event: str, text: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def _emit_block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))


def _emit_deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def _under_docs(rel: str, docs_dir: str) -> bool:
    return rel == docs_dir or rel.startswith(docs_dir.rstrip("/") + "/")


def _docs_relpath(rel: str, docs_dir: str) -> str:
    """`rel` is project-relative (already confirmed `_under_docs`); returns the
    path relative to the bundle root instead, for `_is_ignored_path`."""
    return rel[len(docs_dir):].lstrip("/")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def run_cli(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"okf-validate {VERSION}")
        return 0
    cfg = _load_config()
    as_json = "--json" in argv
    listing_root = "--listing-root" in argv
    paths = [a for a in argv if not a.startswith("-")]
    target = paths[0] if paths else cfg.get("docsDir", "docs")
    ignore_globs = tuple(cfg.get("ignoreGlobs") or ())
    # no deadline in CLI mode — always a full scan
    findings = validate_tree(target, ignore_globs=ignore_globs, listing_root=listing_root)
    if as_json:
        print(json.dumps([
            {"severity": s, "path": r, "code": c, "message": m} for s, r, c, m in findings
        ], indent=2))
    else:
        print(_render_text(findings, target))
    errors, warns = _split(findings)
    if errors:
        return 1
    if warns and cfg.get("warnAsError"):
        return 1
    return 0


# --------------------------------------------------------------------------- #
# HOOK
# --------------------------------------------------------------------------- #
def run_hook() -> int:
    cfg = _load_config()
    if cfg.get("enabled") is False:
        return 0
    data = _read_stdin()
    event = data.get("hook_event_name") or ""
    docs_dir = str(cfg.get("docsDir", "docs")).replace("\\", "/").strip("/")
    project = _project_dir(data)
    bundle_root = os.path.join(project, docs_dir)
    started = time.monotonic()
    deadline = float(cfg.get("deadlineMs", DEFAULTS["deadlineMs"])) / 1000.0
    ignore_globs = tuple(cfg.get("ignoreGlobs") or ())

    if event == "PreToolUse":
        if not cfg.get("hardBlock"):
            return 0  # hard gate opt-in; default is propose-only (PostToolUse handles it)
        tool_input = data.get("tool_input") or {}
        file_path = tool_input.get("file_path") or ""
        content = tool_input.get("content")
        if content is None:  # Edit gives no full content → cannot judge pre-write; let it through
            return 0
        rel = os.path.relpath(os.path.abspath(file_path), os.path.abspath(project)).replace(os.sep, "/")
        if not file_path.endswith(".md") or not _under_docs(rel, docs_dir):
            return 0
        if _is_ignored_path(_docs_relpath(rel, docs_dir), ignore_globs):
            return 0  # regenerable/vendored path (ignoreGlobs) — not authored OKF knowledge
        base = os.path.basename(file_path)
        if base in EXEMPT or base in ("log.md", "README.md"):
            return 0  # harness/reserved/migration files — never hard-blocked
        if base == "index.md":
            fm, _, _ = parse_frontmatter(content)
            if _nonempty(fm, "type"):
                _emit_deny(f"[{TAG}] `index.md` is a reserved OKF listing — it must not carry a concept "
                           "`type`. Move that content into a concept doc and keep the index a link listing.")
                return 0
        else:
            fm, has_block, well_formed = parse_frontmatter(content)
            if not has_block or not well_formed or not _nonempty(fm, "type"):
                _emit_deny(f"[{TAG}] this concept doc needs parseable frontmatter with a non-empty `type` "
                           "(OKF requirement). Add the `type` before writing, or use `quenching-docs-add`.")
                return 0
        return 0

    if event == "PostToolUse":
        tool_input = data.get("tool_input") or {}
        file_path = tool_input.get("file_path") or ""
        if not file_path.endswith(".md"):
            return 0
        rel = os.path.relpath(os.path.abspath(file_path), os.path.abspath(project)).replace(os.sep, "/")
        if not _under_docs(rel, docs_dir):
            return 0
        if _is_ignored_path(_docs_relpath(rel, docs_dir), ignore_globs):
            return 0  # regenerable/vendored path (ignoreGlobs) — not authored OKF knowledge
        _touch_marker(project)  # bundle changed — arm the Stop sweep for this session
        findings = validate_file(file_path, bundle_root)
        errors, warns = _split(findings)
        report = [f for f in findings if f[0] == "ERROR" or (f[0] == "WARN" and cfg.get("warnAsError"))]
        if not report:
            return 0
        if errors and cfg.get("blockOnFail"):
            _emit_block(_render_proposal(findings))
        else:
            _emit_additional_context("PostToolUse", _render_proposal(findings))
        return 0

    if event == "Stop":
        if data.get("stop_hook_active"):
            return 0
        if str(cfg.get("stopScan", "dirty")) != "always" and not os.path.exists(_marker_path(project)):
            return 0  # no docs/** edit since the last completed scan — 1 stat, no walk
        findings = validate_tree(bundle_root, deadline=started + deadline, ignore_globs=ignore_globs)
        if findings is None:
            return 0  # deadline expired mid-walk — abort silently, KEEP the marker for next turn
        _clear_marker(project)  # scan completed; a fixing edit re-arms the marker via PostToolUse
        errors, warns = _split(findings)
        report = [f for f in findings if f[0] == "ERROR" or (f[0] == "WARN" and cfg.get("warnAsError"))]
        if not report:
            return 0
        if errors and cfg.get("blockOnFail"):
            _emit_block(_render_proposal(findings))
        else:
            _emit_additional_context("Stop", _render_proposal(findings))
        return 0

    return 0


def main() -> int:
    argv = sys.argv[1:]
    # A path/flag argument OR a tty means CLI mode; otherwise read the hook JSON on stdin.
    if argv or sys.stdin.isatty():
        return run_cli(argv)
    return run_hook()


if __name__ == "__main__":
    sys.exit(main())
