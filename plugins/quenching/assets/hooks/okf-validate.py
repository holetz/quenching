#!/usr/bin/env python3
"""okf-validate.py — self-contained OKF v0.1 conformance checker for a docs/ bundle.

Payload of the `quenching` plugin. Generic, portable, ZERO dependencies
(a minimal frontmatter parser — no PyYAML). It is the **executable enforcement**
that keeps a target repo's `docs/` bundle aligned to the Open Knowledge Format
after `quenching-docs-align` has installed it: the skills call it, the verification step calls
it, and it wires into the target's `.claude/settings.json` as a hook so future edits
stay conformant.

TWO ENTRY MODES
---------------
1. **CLI**  `okf-validate.py <bundle-or-docs-dir> [--json]`
   Validates the whole bundle rooted at the given directory (walks every `.md`),
   prints a human report, and exits **0** when there are no errors, **1** otherwise.
   This is what `quenching-docs-align`/`quenching-docs-add` invoke and what the plugin's own
   verification runs over `assets/docs/`.
   This checker validates OKF bundles and nothing else. The `specs/` front is owned
   end-to-end by `specs.py validate`, which holds a spec to its own contract (canonical
   heading set, stage gates, filename conformance, slug identity) — a contract that has
   no `type:` in it. Pointing this checker at a spec tree would report defects the specs
   front forbids fixing.

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
Reserved filenames: `index.md` (a listing), `log.md` (a retired change history).
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
- Every **`log.md`**            → **retired**. Nothing produces it and nothing checks
  it, but the name stays reserved and stays out of the hard block, so a log surviving
  in an already-aligned bundle is recognized rather than read as a malformed concept
  doc. Retired is not unknown.

PARSE HONESTY (per-doc; WARN — this checker naming its own misread)
- **`okf-frontmatter-unparsed`** the frontmatter held something this parser could not
  represent faithfully: a stripped trailing comment, an unterminated quote, an indented
  continuation read as empty, or a duplicate top-level key that silently last-wins. It
  reports a suspicion it cannot resolve rather than letting the consequence surface as a
  content finding (`missing-type`, a missing recommended field). The YAML subset, the
  comment rule and the canonical case list are `docs/standards/code/frontmatter-parsing.md`;
  `selftest` runs that list.

RESOURCE INTEGRITY (per-doc; WARN — a doc that is provably lying about itself)
- **`resource-unresolved`** a path- or glob-shaped `resource` entry matching nothing
  on disk. `uri` entries are never resolved, and an entry carrying glob syntax this
  validator does not implement is classified `unknown` and never reported.
- **`resource-self`** the doc's own path falls inside the scope its `resource`
  declares. Such a doc governs nothing and is eternally fresh, which is what makes
  the rule load-bearing rather than cosmetic.

STRUCTURAL INTEGRITY (whole-tree only — CLI + Stop; all WARN, OKF-tolerant)
- **`dir-no-index`**      a directory holds concept docs but has no `index.md` listing.
- **`index-broken-link`** an `index.md` links to a `.md`/dir that does not exist on disk.
- **`index-orphan`**      a concept doc nothing links to (unlisted / not discoverable).
- **`glossary-broken-link`** the same link rule applied to `knowledge/glossary.md`,
  whose links ARE its content — a dead entry is a dead lookup, and `index-broken-link`
  never reached it because the glossary is a concept doc, not an `index.md`.
These stay WARN by design (OKF says consumers MUST tolerate broken links and MAY
synthesize a missing index); the `quenching-docs-align`/`quenching-docs-add` skills treat them as must-fix
in their own verify gate. `_`-prefixed, dot, and asset dirs are pruned from the whole
bundle walk (they hold private/raw sidecar content, never OKF concepts), and every
whole-tree check consumes ONE shared read pass over the tree (`_build_corpus`).

STALENESS (CLI only — advisory, never blocking)
- **`stale-doc`** the doc's `timestamp` predates the last commit touching the code its
  `resource` globs name (`git log -1 --format=%cI`, explicit `:(glob)` pathspec magic).
  It is **advisory and part of no verify gate**: unlike the integrity codes, a
  stale-looking doc may be perfectly correct, because code moves under a rule that did
  not change. It runs in CLI mode only — never `PostToolUse`, never `Stop` — since it
  shells out once per doc, and a tree that is not a git checkout skips it silently.

Config (`hooks-config.json` + `hooks-config.local.json`, block `okfValidate`):
  enabled, docsDir, warnAsError, blockOnFail, hardBlock, deadlineMs, stopScan.
An empty/absent config uses the defaults below; `enabled: false` makes the hook inert.

Trust note: hook config is executable code with shell privileges. This script reads
the touched path/content and prints; the only thing it ever writes is the dirty-marker
stamp file in the system temp dir. In **CLI mode only** it additionally shells out to
`git log`/`git rev-parse` (read-only, timeout-bounded) for `stale-doc`; the hook paths
never spawn a subprocess. Version and review it like infra.
"""
from __future__ import annotations

import fnmatch
import glob
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time

VERSION = "4.8.0"  # kept in lockstep with the plugin VERSION file (and specs.py)

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "okf"
# `log.md` is RETIRED, not unreserved: it keeps its slot here (and its skip in the
# PreToolUse hard block) so a log surviving in an already-aligned bundle stays
# recognized. Drop it from this tuple and every such file falls through to the
# concept-doc path — `missing-type` at ERROR, and denied writes under `hardBlock`.
RESERVED = ("index.md", "log.md")
# The bundle's one fixed concept doc, at a path the OKF contract pins. Its links are
# its content, so it is link-checked alongside the reserved listings.
GLOSSARY_REL = "knowledge/glossary.md"
# Navigation/payload files — never OKF concepts, never required to carry a `type`.
# `CLAUDE.md`/`AGENTS.md` are agent-pointers auto-loaded by the harness; `QUENCHING.md`
# is the operator manual the `quenching` aligns install beside each front they
# own (`docs/`, `specs/`, `.claude/`). Skip all three.
EXEMPT = ("CLAUDE.md", "AGENTS.md", "QUENCHING.md")
RECOMMENDED = ("title", "description", "resource", "timestamp")
# Types for which `resource` is deliberately absent, so its WARN would be permanent noise.
# A `task` is parked work — nothing is built yet to point at (the backlog task mold omits
# the key on purpose). Every other type anchors to code, an asset, or a URI.
# The sibling case — a doc that HAS a resource whose honest scope is the whole bundle — is
# handled by the bundle-aggregate exemption in `check_resource`, the same mechanism
# generalized rather than a second one.
TYPES_WITHOUT_RESOURCE = ("task",)
# Glob metacharacters `parse_resource` does not implement. An entry carrying one is
# classified `unknown` and never reported as a violation — see `parse_resource`.
UNSUPPORTED_GLOB_CHARS = ("{", "}", "[", "]", "?")
# `resource` kinds resolved against the checkout. `uri` points outside it and `unknown`
# carries syntax this validator does not implement, so neither is ever judged. Defined
# ONCE: every consumer must agree on which kinds it may judge, or a kind added later is
# silently in-scope for one check and out-of-scope for another.
RESOLVABLE_KINDS = ("path", "glob")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Seconds `stale-doc` waits on one `git log`. CLI-only, but a pathological repo must
# not hang an operator's sweep; a timeout yields no finding rather than a wrong one.
GIT_TIMEOUT_S = 10
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
# --------------------------------------------------------------------------- #
# The YAML comment rule — one rule, three copies
#
# `docs/standards/code/frontmatter-parsing.md` owns the rule, the canonical case
# list and the lockstep obligation. `skills.py` and `specs.py` carry the same
# functions; each installs standalone into a target's `.claude/hooks/`, so none may
# import the others. EDIT ALL THREE, OR NONE — `CANONICAL_CASES` below is what makes
# a drifted parser fail its OWN selftest on a row the other two still pass.
#
# This checker stripped no comment at all until now, which made it the one tool that
# could not truncate. It gains the rule ONLY together with the diagnostic below:
# adding prose loss to a hook that fires on every `docs/**` write in every target
# repo, without the means to say when it happened, is the one shape ruled out.
# --------------------------------------------------------------------------- #
def _frontmatter_body(text: str) -> list[str] | None:
    """The lines between the leading `---` fences; `None` when the block never
    closes or there is none."""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None


def _indented_run(body: list[str], start: int) -> tuple[list[str], int]:
    """The blank-or-indented lines beginning at `start` with trailing blanks dropped,
    and the index of the first line that is neither — i.e. everything belonging to
    the value above, and where the next top-level key begins."""
    run: list[str] = []
    j = start
    while j < len(body) and (not body[j].strip() or body[j][:1] in (" ", "\t")):
        run.append(body[j])
        j += 1
    while run and not run[-1].strip():
        run.pop()
    return run, j


def _quote_end(val: str) -> int | None:
    """Index just past the closing quote of a quoted scalar; `0` when the value is
    not quoted, `None` when the quote never closes.

    A quote opens a scalar only in the first position — mid-value it is an ordinary
    character, which is why `at the first '#'` is a plain scalar and its `#` is not
    inside quotes."""
    if not val or val[0] not in ("'", '"'):
        return 0
    quote, i = val[0], 1
    while i < len(val):
        if quote == '"' and val[i] == "\\":
            i += 2
            continue
        if val[i] == quote:
            if quote == "'" and val[i + 1:i + 2] == "'":   # YAML doubles a literal '
                i += 2
                continue
            return i + 1
        i += 1
    return None


def _split_comment(val: str) -> tuple[str, str]:
    """Split a scalar into (value, comment).

    A `#` opens a comment only when it is the first character of the value or is
    preceded by whitespace, and never inside a quoted scalar.

    An unterminated quote strips nothing: the scalar's extent is unknowable, so the
    value is kept verbatim and `frontmatter_anomalies` reports it rather than the
    parser guessing a boundary."""
    start = _quote_end(val)
    if start is None:
        return val, ""
    for i in range(start, len(val)):
        if val[i] == "#" and (i == 0 or val[i - 1] in " \t"):
            return val[:i].rstrip(), val[i:]
    return val, ""


# The block-scalar indicator. `skills.py` compiles the same pattern to READ these;
# this checker does not read them, so it uses the pattern to NAME them instead.
BLOCK_SCALAR_RE = re.compile(r"^([|>])(?:[+-]?)(?:\d*)\s*$")


def frontmatter_anomalies(text: str) -> list[dict]:
    """What the frontmatter parse could not represent faithfully.

    A SIDECAR: `parse_frontmatter` keeps its `(fm, has_block, well_formed)` shape, so
    none of its call sites change.

    Every entry is a suspicion this checker cannot resolve, never a proven violation:
    a stripped comment and lost prose are byte-identical, and nothing here guarantees
    Claude Code's own loader resolves a duplicate key the way this one does. Reported
    at WARN — see `docs/standards/quality/parse-honesty.md`.

    This parser reads top-level scalars ONLY, so ANY indented run under an empty value
    is `indented-continuation` here — a block list is as unreadable to it as prose. The
    other two tools exempt the forms they genuinely read."""
    body = _frontmatter_body(text)
    if body is None:
        return []
    out: list[dict] = []
    seen: set[str] = set()
    j = 0
    while j < len(body):
        raw = body[j]
        if (not raw.strip() or raw.lstrip().startswith("#")
                or raw[:1] in (" ", "\t") or ":" not in raw):
            j += 1
            continue
        key, _, val = raw.partition(":")
        key, val = key.strip(), val.strip()
        run, k = _indented_run(body, j + 1)

        if key in seen:
            out.append(_anomaly(key, "duplicate-key",
                                f"`{key}` is set more than once and the last one silently wins; "
                                "nothing guarantees another parser resolves it the same way"))
        seen.add(key)

        value, comment = _split_comment(val)
        if comment:
            out.append(_anomaly(key, "comment-stripped",
                                f"`{comment}` was read as a comment and removed from `{key}` — "
                                "a stripped comment and lost prose are byte-identical"))
        elif _quote_end(val) is None:
            out.append(_anomaly(key, "unterminated-quote",
                                f"`{key}` opens a quote that never closes, so the scalar's "
                                "extent is unknowable; nothing was stripped"))
        # A block scalar is the one unread form that does NOT come back empty: this
        # parser keeps the bare `|`/`>` indicator as the value, which is a guess rather
        # than a read, so the emptiness test below would never see it. `skills.py` DOES
        # read block scalars and stays silent — the per-tool carve-out the standard
        # allows (§The canonical case list), not a disagreement on a row.
        if BLOCK_SCALAR_RE.match(value) and run:
            out.append(_anomaly(key, "indented-continuation",
                                f"`{key}` opens a block scalar this parser does not read — the "
                                f"`{value}` indicator was kept as the value and the lines beneath "
                                "it were dropped"))
        elif value == "" and run:
            out.append(_anomaly(key, "indented-continuation",
                                f"`{key}` has no inline value and the lines beneath it are in "
                                "no form this parser reads — it was read as empty"))
        j = k
    return out


def _anomaly(key: str, kind: str, detail: str) -> dict:
    return {"key": key, "kind": kind, "detail": detail}


# The canonical case list from `docs/standards/code/frontmatter-parsing.md`. It is
# duplicated VERBATIM in skills.py and specs.py and is the lockstep unit for all
# three: adding a row means adding it in three places, and a parser that drifts fails
# here on a row the other two still pass.
#   (label, frontmatter body, expected `title`, expected anomaly kinds)
CANONICAL_CASES = [
    ("plain",                 "title: a plain value",              "a plain value",              ()),
    ("comment-after-space",   "title: a value # a note",           "a value",                    ("comment-stripped",)),
    ("hash-after-quote-char", "title: truncates at the first '#'", "truncates at the first '#'", ()),
    ("hash-in-backticks",     "title: the `#` character",          "the `#` character",          ()),
    ("hash-no-space",         "title: C#",                         "C#",                         ()),
    ("double-quoted-hash",    'title: "quoted # inside"',          "quoted # inside",            ()),
    ("single-quoted-hash",    "title: 'single # inside'",          "single # inside",            ()),
    ("quoted-then-comment",   'title: "quoted" # a note',          "quoted",                     ("comment-stripped",)),
    ("comment-only",          "title: # a note",                   "",                           ("comment-stripped",)),
    ("unterminated-quote",    'title: "unterminated',              '"unterminated',              ("unterminated-quote",)),
    ("duplicate-key",         "title: first\ntitle: second",       "second",                     ("duplicate-key",)),
    ("indented-continuation", "title:\n  a wrapped prose line",    "",                           ("indented-continuation",)),
]


def canonical_case_failures() -> list[str]:
    """Run `CANONICAL_CASES` against this tool's own parser and sidecar."""
    out = []
    for label, fm, want_value, want_kinds in CANONICAL_CASES:
        text = f"---\n{fm}\n---\n\nbody\n"
        got_value = parse_frontmatter(text)[0].get("title", "<missing>")
        got_kinds = tuple(sorted(a["kind"] for a in frontmatter_anomalies(text)))
        if got_value != want_value:
            out.append(f"{label}: title expected {want_value!r}, got {got_value!r}")
        if got_kinds != tuple(sorted(want_kinds)):
            out.append(f"{label}: anomalies expected {sorted(want_kinds)}, got {list(got_kinds)}")
    return out


def parse_frontmatter(text: str):
    """Return (fm, has_block, well_formed).

    fm          -- dict of the top-level `key: value` pairs (values as strings,
                   comments stripped per the rule above, surrounding quotes stripped).
                   Empty dict when there is no block.
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
    body = _frontmatter_body(text)
    if body is None:
        return {}, True, False  # opened a fence, never closed → malformed
    fm: dict = {}
    for raw in body:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1] in (" ", "\t"):  # nested value — skip (top-level keys only)
            continue
        if ":" not in raw:
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = _split_comment(val.strip())[0]
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        fm[key] = val
    return fm, True, True


def _nonempty(fm: dict, key: str) -> bool:
    return bool(str(fm.get(key, "")).strip())


def _is_uri(value: str) -> bool:
    """True for a scheme-bearing target (`https://…`, `mailto:…`) — something that
    points outside the checkout and is never resolved against disk."""
    return "://" in value or value.lower().startswith(("mailto:", "tel:"))


def parse_resource(value: str) -> list[tuple[str, str]]:
    """Split a `resource` value into `(entry, kind)` pairs, in written order.

    A comma-separated list of globs and paths is a *plugin convention*, not an OKF
    rule — three of the five real values in this repo's own bundle are lists and
    nothing documented the format, so it is parsed here and stated in
    `docs/standards/quality/bundle-verification.md`.

    kind is one of:
      `path`    a plain repo-root-relative path.
      `glob`    a path carrying `*` / `**`, the only two wildcards implemented.
      `uri`     a scheme-bearing target — outside the checkout, never resolved.
      `unknown` carries glob syntax this validator does not implement (braces,
                character classes, `?`). Reported as unknown, NEVER as a
                violation: no observed value uses them, and guessing at syntax
                nobody writes would turn a WARN into noise.
    """
    out: list[tuple[str, str]] = []
    for raw in str(value or "").split(","):
        entry = raw.strip()
        if entry:
            out.append((entry, _resource_kind(entry)))
    return out


def _resource_kind(entry: str) -> str:
    if _is_uri(entry):
        return "uri"
    if any(ch in entry for ch in UNSUPPORTED_GLOB_CHARS):
        return "unknown"
    return "glob" if "*" in entry else "path"


def _project_root(bundle_root: str) -> str:
    """The checkout root a `resource` entry is written relative to — the bundle's
    parent. Every observed value is repo-root-relative (`docs/**`,
    `plugins/…/SKILL.md`), including in the shipped skeleton, where the bundle sits
    at `assets/docs` and `docs/**` still resolves to that bundle."""
    return os.path.dirname(os.path.abspath(bundle_root))


def _resource_resolves(entry: str, kind: str, project_root: str) -> bool:
    """True when the entry matches at least one path in the checkout.

    Stops at the FIRST hit (`iglob`, not `glob`): answering "does this resolve?"
    runs on every concept doc in the hook path, and materializing every match of a
    `docs/**` would walk the whole tree once per doc under the Stop deadline.
    `glob.escape` covers a checkout whose own path contains a glob metacharacter.
    """
    if kind == "glob":
        pattern = os.path.join(glob.escape(project_root), entry)
        return next(glob.iglob(pattern, recursive=True), None) is not None
    return os.path.exists(os.path.join(project_root, entry))


_GIT_CHECKOUT: dict[str, bool] = {}


def _is_git_checkout(project_root: str) -> bool:
    """Whether `project_root` sits inside a git work tree. Cached per process, so a
    whole-tree sweep asks once per bundle rather than once per doc — a repo that is
    not a checkout would otherwise pay one failed subprocess per concept doc."""
    key = os.path.abspath(project_root)
    if key not in _GIT_CHECKOUT:
        try:
            proc = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                                  cwd=key, capture_output=True, text=True,
                                  timeout=GIT_TIMEOUT_S)
            _GIT_CHECKOUT[key] = proc.returncode == 0 and proc.stdout.strip() == "true"
        except (OSError, subprocess.SubprocessError):
            _GIT_CHECKOUT[key] = False
    return _GIT_CHECKOUT[key]


def _git_last_commit_date(entries: list[str], project_root: str) -> str | None:
    """Newest committer date (`YYYY-MM-DD`) across the entry globs, or None when
    the answer cannot be trusted — not a git checkout, git absent, no commit
    touching the scope, or the call timed out.

    Pathspecs carry explicit **`:(glob)`** magic. Git's default wildmatch lets a
    single `*` cross a slash, so a naive `src/*` silently widens to everything
    under `src/` and reports a perfectly current doc as stale; `:(glob)` gives the
    same segment-wise semantics `_glob_contains` implements for `resource-self`,
    so one glob means one thing across the whole checker. The fixture's
    `shallow.md` pins this: it is silent under `:(glob)` and a false positive
    without it.
    """
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--"] + [f":(glob){e}" for e in entries],
            cwd=project_root, capture_output=True, text=True, timeout=GIT_TIMEOUT_S,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()[:10] or None


def check_stale(text: str, bundle_root: str) -> list[tuple[str, str, str]]:
    """`stale-doc` — the doc's `timestamp` predates the last commit touching the
    code its `resource` governs.

    **Advisory, and never must-fix.** Unlike the integrity codes, a stale-looking
    doc may be perfectly correct: code moves under a rule that did not change.
    Conflating the two would make the must-fix set unusable, since every mature
    bundle carries some legitimately stale-looking doc.

    Bundle-aggregate entries are excluded on the same mechanism as `resource-self`:
    a scope containing the whole bundle contains the doc, so it is touched whenever
    the doc itself is, and would report fresh forever.
    """
    fm, _, _ = parse_frontmatter(text)
    if not _nonempty(fm, "resource") or not _nonempty(fm, "timestamp"):
        return []
    stamped = str(fm["timestamp"]).strip()[:10]
    if not ISO_DATE.match(stamped):
        return []          # a non-ISO timestamp is `missing-timestamp`'s business, not ours
    project_root = _project_root(bundle_root)
    if not _is_git_checkout(project_root):
        return []          # no history to compare against — skip silently, never report
    bundle_rel = _rel_to_project(bundle_root, project_root)
    entries = [e for e, kind in parse_resource(fm["resource"])
               if kind in RESOLVABLE_KINDS and not _is_bundle_aggregate(e, kind, bundle_rel)]
    if not entries:
        return []
    last = _git_last_commit_date(entries, project_root)
    if last and last > stamped:
        return [("WARN", "stale-doc",
                 f"`timestamp` {stamped} predates the last commit touching its `resource` "
                 f"({last}) — the doc may no longer describe what it governs")]
    return []


def _glob_contains(pattern: str, rel_path: str) -> bool:
    """Segment-wise match of a `*`/`**` glob against a forward-slash relative path.

    `fnmatch` is deliberately NOT used for this: its `*` also matches `/`, so
    `docs/*` would claim to contain `docs/standards/x.md` and raise a false
    `resource-self` — and since the skills treat every WARN as must-fix, a false
    positive here costs more than a missed one. `*` matches inside one segment;
    `**` matches any number of segments, including none.
    """
    pat = [p for p in pattern.strip("/").split("/") if p]
    parts = [p for p in rel_path.strip("/").split("/") if p]

    def walk(pi: int, si: int) -> bool:
        while pi < len(pat):
            if pat[pi] == "**":
                if pi + 1 == len(pat):
                    return True                     # a trailing `**` swallows the rest
                return any(walk(pi + 1, k) for k in range(si, len(parts) + 1))
            if si >= len(parts) or not fnmatch.fnmatch(parts[si], pat[pi]):
                return False
            pi += 1
            si += 1
        return si == len(parts)

    return walk(0, 0)


def _entry_contains(entry: str, kind: str, rel_doc: str) -> bool:
    """True when `rel_doc` falls inside the scope the entry declares."""
    if kind == "glob":
        return _glob_contains(entry, rel_doc)
    ent = entry.strip("/")
    return rel_doc == ent or rel_doc.startswith(ent + "/")


def _rel_to_project(target: str, project_root: str) -> str:
    """`target` as a forward-slash path relative to the checkout root."""
    return os.path.relpath(os.path.abspath(target), project_root).replace(os.sep, "/")


def _is_bundle_aggregate(entry: str, kind: str, bundle_rel: str) -> bool:
    """True when the entry's scope covers the whole bundle rather than merely this doc.

    Both `resource-self` and `stale-doc` exempt these, for the same reason: a scope
    containing the bundle root contains every doc in it, so it is touched whenever the
    doc itself is. Named once so the two checks cannot drift on what "aggregate" means.
    """
    return _entry_contains(entry, kind, bundle_rel)


def check_resource(text: str, path: str, bundle_root: str) -> list[tuple[str, str, str]]:
    """`resource` integrity for one concept doc, as (severity, code, message).

    `uri` and `unknown` entries are skipped rather than reported: neither can be
    resolved against the checkout, and flagging a glob syntax this validator never
    implemented would be exactly the noise `parse_resource` classifies it to avoid.

    **The bundle-aggregate exemption.** An entry whose scope contains the bundle
    ROOT is an aggregate, not a mistake, and never raises `resource-self`. This is
    `TYPES_WITHOUT_RESOURCE` generalized — from "types with nothing to point at" to
    "docs whose honest scope is bundle-wide" — so the front keeps ONE exemption
    mechanism rather than two. `knowledge/glossary.md` really does govern the whole
    bundle, so `resource: docs/**` is truthful and inventing a narrower scope to
    silence the check would be the fabrication. The discrimination is mechanical
    and needs no hardcoded path: a scope containing the bundle root contains every
    doc in it, while a narrower scope that still contains the doc
    (`docs/standards/**` on a standards doc) stays a real finding.
    """
    fm, _, _ = parse_frontmatter(text)
    if not _nonempty(fm, "resource"):
        return []          # absent, empty, or unparseable frontmatter — nothing to resolve
    project_root = _project_root(bundle_root)
    rel_doc = _rel_to_project(path, project_root)
    bundle_rel = _rel_to_project(bundle_root, project_root)
    out: list[tuple[str, str, str]] = []
    for entry, kind in parse_resource(fm["resource"]):
        if kind not in RESOLVABLE_KINDS:
            continue
        if not _resource_resolves(entry, kind, project_root):
            out.append(("WARN", "resource-unresolved",
                        f"`resource` entry `{entry}` matches nothing on disk"))
        elif _entry_contains(entry, kind, rel_doc) and \
                not _is_bundle_aggregate(entry, kind, bundle_rel):
            out.append(("WARN", "resource-self",
                        f"`resource` entry `{entry}` contains this doc — a doc that points at "
                        "itself governs nothing and is eternally fresh"))
    return out


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
    # BEFORE the content checks, so a misread is never presented as a content gap: a
    # value this parser could not represent used to surface as `missing-type` or a
    # missing recommended field, naming the absence rather than the misread.
    for a in frontmatter_anomalies(text):
        out.append(("WARN", "okf-frontmatter-unparsed", f"`{a['key']}`: {a['detail']}"))
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
    # A residual angle bracket means a template placeholder — `[<Term>](<path>.md)` in
    # the glossary mold's own instructions. `_link_targets` already strips the markdown
    # `[x](<url>)` wrapper, so anything still carrying `<`/`>` is a slot, not a path
    # (both are illegal in a Windows filename and unused in this bundle's conventions).
    # Caught here, at the one resolver both link codes share, so neither can drift:
    # `_strip_noise` cannot remove it, since its inline-code regex is newline-excluding
    # and the mold wraps that code span across two lines.
    if "<" in t or ">" in t:
        return None
    low = t.lower()
    if _is_uri(t):
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
      - `glossary-broken-link` the same link rule on `knowledge/glossary.md`.
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

    # broken links — the reserved listings, plus the fixed glossary under its own code.
    # The glossary is the one concept doc whose links ARE its content: an entry
    # pointing at a doc that no longer exists is a dead lookup, not a stale prose
    # reference, and `index-broken-link` never reached it because it is not an
    # `index.md`. Same rule, same helpers, different code — never a second walker.
    link_checked = [(ap, "index-broken-link", "listing") for ap in index_md]
    glossary = os.path.join(root, *GLOSSARY_REL.split("/"))
    if glossary in corpus:
        link_checked.append((glossary, "glossary-broken-link", "glossary entry"))
    for ap, code, noun in sorted(link_checked):
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
                findings.append(("WARN", rel, code,
                                 f"{noun} links to `{tgt}` but no such file exists"))
            elif kind == "dir" and not os.path.isdir(path):
                findings.append(("WARN", rel, code,
                                 f"{noun} links to `{tgt}` but no such directory exists"))

    # orphans — a concept doc nothing links to (not reachable from any listing/doc)
    for ap in sorted(concept_md):
        if os.path.normpath(ap) not in linked:
            rel = os.path.relpath(ap, root).replace(os.sep, "/")
            findings.append(("WARN", rel, "index-orphan",
                             "concept doc is not linked from any index.md or sibling doc "
                             "(unlisted — regenerate the folder's index.md)"))
    return findings


def validate_file(path: str, bundle_root: str) -> list[tuple[str, str, str, str]]:
    """Return findings for one file as (severity, rel, code, message). Reads the
    file itself — the single-file entry point (PostToolUse); whole-tree callers
    go through `_build_corpus` + `_validate_text` instead."""
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [("ERROR", os.path.basename(path), "unreadable", f"cannot read file: {exc}")]
    return _validate_text(path, text, bundle_root)


def _validate_text(path: str, text: str, bundle_root: str,
                   with_stale: bool = False) -> list[tuple[str, str, str, str]]:
    """Findings for one file whose text is already in hand (no disk read).

    `with_stale` enables `stale-doc`, and **defaults to off**: it shells out to
    `git log` once per doc, which is fine for an on-demand sweep and unacceptable
    under the hook path's 4-second Stop deadline. Only `run_cli` turns it on, so a
    new hook caller cannot acquire it by forgetting to opt out."""
    rel = os.path.relpath(path, bundle_root).replace(os.sep, "/")
    base = os.path.basename(path)
    if base in EXEMPT:
        raw = []
    elif base == "index.md":
        is_root = os.path.dirname(os.path.abspath(path)) == os.path.abspath(bundle_root)
        raw = check_index(text, is_root)
    elif base == "log.md":
        raw = []  # retired: reserved, recognized, never judged — see THE CONFORMANCE CORE
    elif base == "README.md":
        # OKF-strict uses `index.md` as the reserved listing; a README in the bundle
        # is a migration nudge, not a hard failure (OKF does not reserve README).
        raw = [("WARN", "readme-not-index",
                "OKF-strict uses `index.md` as the reserved listing — convert this README.md to index.md")]
    elif base.endswith(".md"):
        raw = check_concept(text) + check_resource(text, path, bundle_root)
        if with_stale:
            raw += check_stale(text, bundle_root)
    else:
        raw = []
    return [(sev, rel, code, msg) for (sev, code, msg) in raw]


def validate_tree(bundle_root: str, deadline: float | None = None,
                   ignore_globs: tuple[str, ...] = (),
                   with_stale: bool = False):
    """Validate the whole bundle from ONE read pass. Returns the findings list,
    or **None** when `deadline` (a `time.monotonic()` instant) expired mid-walk —
    hook mode aborts silently; CLI mode passes no deadline."""
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
            findings.extend(_validate_text(path, text, bundle_root, with_stale))
    # bundle-level SHOULDs
    if not (root / "index.md").exists():
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
            "frontmatter-free listing).")


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


def hard_block_exempt(base: str) -> bool:
    """Filenames the PreToolUse hard gate never denies: the harness pointers, the
    retired `log.md`, and the migration README. A named predicate rather than an
    inline condition so `selftest` can assert the retirement without standing up a
    hook invocation — `run_hook` reads its config from disk beside this script, so a
    subprocess would return early on `hardBlock` being off and prove nothing."""
    return base in EXEMPT or base in ("log.md", "README.md")


def _under_docs(rel: str, docs_dir: str) -> bool:
    return rel == docs_dir or rel.startswith(docs_dir.rstrip("/") + "/")


def _docs_relpath(rel: str, docs_dir: str) -> str:
    """`rel` is project-relative (already confirmed `_under_docs`); returns the
    path relative to the bundle root instead, for `_is_ignored_path`."""
    return rel[len(docs_dir):].lstrip("/")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# the retirement fixture — `log.md` lost its checker, never its reservation
#
# With `check_log` gone, nothing in this file would notice if `log.md` also fell
# out of `RESERVED` or out of the hard gate's skip list, and the damage would not
# announce itself: every log surviving in an already-aligned bundle would quietly
# start reporting `missing-type` at ERROR and, under `hardBlock`, become unwritable.
# So the fixture validates a real bundle holding the worst log this tool ever
# accepted — a `type` in its frontmatter, date headings in ascending order, the
# three things the retired codes used to fire on — and demands silence about it.
# --------------------------------------------------------------------------- #
RETIRED_LOG_FIXTURE = {
    # both shapes a surviving log actually takes, because they fail differently: the
    # typed one is what `log-has-type` used to catch, and the bare one is the one that
    # falls to `missing-type` at ERROR — the failure `## Design` of the retiring spec
    # names — if the dispatch branch is ever dropped.
    "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n\n- [Log](log.md)\n'
                "- [Standards](standards/index.md)\n",
    "log.md": ("---\ntype: standard\n---\n\n"
               "## 2026-01-01\n\n- typed, and oldest first\n\n"
               "## 2026-07-28\n\n- newest last\n"),
    "standards/index.md": "# Standards\n\n- [Log](log.md)\n",
    "standards/log.md": "# Log\n\n- an entry under no date heading at all\n",
}


def retired_log_failures() -> list[str]:
    """Prove the retirement in all three places it has to hold at once."""
    out: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for relpath, text in RETIRED_LOG_FIXTURE.items():
            path = os.path.join(tmp, *relpath.split("/"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pathlib.Path(path).write_text(text, encoding="utf-8")
        findings = validate_tree(tmp)
    judged = sorted(f"{rel}:{sev}/{code}" for sev, rel, code, msg in findings
                    if os.path.basename(rel) == "log.md")
    if judged:
        out.append(f"retired-log: a populated `log.md` was judged: {judged}")
    # anything else here means the fixture drifted, not that the retirement broke —
    # without this the two logs could go silent for the wrong reason and still pass
    rest = sorted(f"{rel}:{code}" for sev, rel, code, msg in findings
                  if os.path.basename(rel) != "log.md")
    if rest:
        out.append(f"retired-log: the fixture bundle is not otherwise clean: {rest}")
    if "log.md" not in RESERVED:
        out.append("retired-log: `log.md` left RESERVED — every surviving log becomes a concept doc")
    if not hard_block_exempt("log.md"):
        out.append("retired-log: `log.md` left the PreToolUse skip — writes to it would be denied")
    return out


# --------------------------------------------------------------------------- #
# the retired `--listing-root` mode
# --------------------------------------------------------------------------- #
# `plans/index.md` was retired whole, and with it the only caller of the mode that
# scanned a non-bundle tree. The mode's failure is the mirror of the log's: re-adding
# it is a one-line change that nothing else complains about, and the tree it used to
# skip would go silently unjudged again. So the fixture is a tree the OLD mode
# validated CLEAN — a spec beside a plain listing — and demands the checker judge it
# now, because a bundle is the only thing this tool validates.
RETIRED_LISTING_ROOT_FIXTURE = {
    "index.md": "# Plans\n\n- [a spec](2026-07-28-a-spec.md)\n",
    "2026-07-28-a-spec.md": ("---\nslug: a-spec\ntitle: A spec\n"
                             "verification: per-section\n---\n\n# A spec\n"),
}


def retired_listing_root_failures() -> list[str]:
    """Prove the mode is gone, and that retiring it did not touch the reservation.

    NOTE on the third assertion. The spec that ordered this retirement asserts
    `index.md` is in `hard_block_exempt()`; it never was, and must not be. `log.md` is
    exempt because a retired artifact is judged by nothing, but `index.md` is still
    *produced* by the bundle, and denying an `index.md` that carries a concept `type`
    is the PreToolUse gate's whole job. Exempting it is the mutation this line catches."""
    out: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for relpath, text in RETIRED_LISTING_ROOT_FIXTURE.items():
            pathlib.Path(os.path.join(tmp, relpath)).write_text(text, encoding="utf-8")
        findings = validate_tree(tmp)
    codes = {code for sev, rel, code, msg in findings if rel == "2026-07-28-a-spec.md"}
    if "missing-type" not in codes:
        out.append("retired-listing-root: a spec file went unjudged — the `_is_spec_file` "
                   f"skip is back (codes: {sorted(codes)})")
    # the parameter is the mode; a caller cannot reach a mode the signature cannot express
    params = validate_tree.__code__.co_varnames[:validate_tree.__code__.co_argcount]
    if "listing_root" in params:
        out.append("retired-listing-root: `validate_tree` still takes `listing_root`")
    if "index.md" not in RESERVED:
        out.append("retired-listing-root: `index.md` left RESERVED — retiring a mode is "
                   "never unreserving a name")
    if hard_block_exempt("index.md"):
        out.append("retired-listing-root: `index.md` entered the PreToolUse skip — a typed "
                   "index.md would stop being denied")
    return out


def run_selftest(as_json: bool) -> int:
    """The canonical frontmatter cases plus the retirement fixtures, run against this
    checker's own parser and its own tree walk.

    The other two tools already had a `selftest`; this one had none, and it is the
    tool with the widest blast radius — a hook firing on every `docs/**` write in
    every target repo. A rule it cannot prove it implements is a rule it should not
    have been given."""
    failures = (canonical_case_failures() + retired_log_failures()
                + retired_listing_root_failures())
    cases = len(CANONICAL_CASES) + 2
    if as_json:
        print(json.dumps({"ok": not failures, "cases": cases,
                          "failures": failures}, indent=2, ensure_ascii=False))
    else:
        print(f"okf-validate selftest — {len(CANONICAL_CASES)} canonical frontmatter case(s) "
              "+ the retired-log and retired-listing-root fixtures")
        for f in failures:
            print(f"  FAIL {f}")
        print(f"  {'PASS' if not failures else str(len(failures)) + ' FAILED'}")
    return 1 if failures else 0


def run_cli(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"okf-validate {VERSION}")
        return 0
    cfg = _load_config()
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("-")]
    # intercepted before the target resolves — this CLI reads its first positional as
    # a directory, so a bare subcommand would otherwise be scanned as a path
    if paths and paths[0] == "selftest":
        return run_selftest(as_json)
    target = paths[0] if paths else cfg.get("docsDir", "docs")
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
        if hard_block_exempt(base):
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
