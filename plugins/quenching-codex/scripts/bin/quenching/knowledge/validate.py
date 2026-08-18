"""The three entry points every caller validates through — one file, one text, one tree.

Moved verbatim out of the pre-refactor OKF validator script. This is the dispatch that decides
which conformance function a filename earns: exempt harness pointers, the reserved
`index.md`, the retired `log.md`, the migration `README.md`, and everything else as a
concept doc.
"""
from __future__ import annotations

import os
import pathlib

from quenching.knowledge.checks import (
    check_concept,
    check_index,
    check_legacy_doc_quadrant,
    check_legacy_glossary,
    check_legacy_home,
    check_legacy_root,
)
from quenching.knowledge.corpus import _build_corpus
from quenching.knowledge.resource import check_resource
from quenching.knowledge.schema import EXEMPT, GLOSSARY_REL, LEGACY_ROOT_NAME
from quenching.knowledge.stale import check_stale
from quenching.knowledge.structure import validate_generated_listing, validate_structure


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
        legacy_root = os.path.join(os.path.dirname(bundle_root) or ".", LEGACY_ROOT_NAME)
        legacy = check_legacy_root(os.path.isdir(legacy_root), legacy_root)
        return legacy or [("ERROR", str(bundle_root), "no-bundle", "bundle root is not a directory")]
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
    # pre-rename layout debt — each site independent and idempotent (## Design §A migração
    # detecta por estrutura, sítio a sítio — nunca por versão)
    root_entries = {p.name for p in root.iterdir() if p.is_dir()}
    findings.extend(check_legacy_home(root_entries))
    doc_dir = root / "documentation"
    if doc_dir.is_dir():
        quadrant_entries = {p.name for p in doc_dir.iterdir() if p.is_dir()}
        findings.extend(check_legacy_doc_quadrant(quadrant_entries))
    glossary_rels = sorted({
        os.path.relpath(p, bundle_root).replace(os.sep, "/")
        for p in corpus if os.path.basename(p) == "glossary.md"
    })
    findings.extend(check_legacy_glossary(glossary_rels, GLOSSARY_REL))
    # whole-tree structural integrity (missing/broken/orphaned listings)
    findings.extend(validate_structure(bundle_root, corpus))
    # the one listing derived from disk, checked against it
    findings.extend(validate_generated_listing(bundle_root, corpus))
    return findings
