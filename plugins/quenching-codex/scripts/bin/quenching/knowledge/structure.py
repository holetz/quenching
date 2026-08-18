"""Structural integrity — the bundle's own link graph, and the one listing derived from disk.

Moved verbatim out of the pre-refactor OKF validator script, then widened once: the module used to
declare itself the link graph alone, and `generated-listing-drift` is not a link check but an
equality between two texts. The scope is stated as it now is rather than left saying something
false (`validar-a-zona-generated-contra-o-disco`, `## Open Decisions`).

STRUCTURAL INTEGRITY (whole-tree only — CLI + Stop; all WARN, OKF-tolerant)
- **`dir-no-index`**      a directory holds concept docs but has no `index.md` listing.
- **`index-broken-link`** an `index.md` links to a `.md`/dir that does not exist on disk.
- **`index-orphan`**      a concept doc nothing links to (unlisted / not discoverable).
- **`glossary-broken-link`** the same link rule applied to `glossary.md`,
  whose links ARE its content — a dead entry is a dead lookup, and `index-broken-link`
  never reached it because the glossary is a concept doc, not an `index.md`.
- **`generated-listing-missing`** a `standards/**` doc no row inside the `<!-- BEGIN GENERATED -->`
  zone of `standards/index.md` links. `index-orphan` does not reach it: any sibling doc citing it
  disarms that check, and a doc outside the listing is still unreachable by navigation.
- **`generated-listing-drift`** a row inside that zone whose description no longer equals the
  `description:` of the doc it links.
These stay WARN by design (OKF says consumers MUST tolerate broken links and MAY
synthesize a missing index); the `quenching-knowledge-align`/`quenching-knowledge-add` skills treat them as must-fix
in their own verify gate.
"""
from __future__ import annotations

import os
import re

from quenching.common.frontmatter import parse_frontmatter
from quenching.knowledge.resource import _is_uri
from quenching.knowledge.schema import EXEMPT, GLOSSARY_REL, LINK_RE, RESERVED

# The bundle's one generated listing. Pinned to this path rather than discovered, because it is the
# only `<!-- BEGIN GENERATED -->` zone that exists: a second one is speculative generalization for a
# population of one (`standards/architecture/generated-listings.md`).
GENERATED_LISTING_REL = "standards/index.md"

# The zone is what sits AFTER the opening comment closes, so the row mold inside that comment —
# a real markdown link to `code/imports.md` — can never be read as a listed row.
GENERATED_ZONE_RE = re.compile(
    r"<!--\s*BEGIN GENERATED\b.*?-->(?P<zone>.*?)<!--\s*END GENERATED\s*-->", re.DOTALL)

# `| [imports.md](code/imports.md) | <the doc's description> |` — a table row whose first cell holds
# a link. The `| Doc | Covers |` header and the `| --- | --- |` separator carry none and never match.
# The **closing** pipe is optional because GFM makes it optional, and this bundle's own zone already
# holds a row written without one — requiring it dropped that row from the parse and reported the
# doc it lists as unlisted, which is the false positive a membership check can least afford.
GENERATED_ROW_RE = re.compile(r"^\|[^|\n]*\[[^\]]*\]\(([^)\n]+)\)[^|\n]*\|([^|\n]*)\|?\s*$",
                              re.MULTILINE)


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
    bundle's own form (`/.knowledge/…` or `/<home>/…`). We only police the bundle's own
    link graph, so a legitimate reference to a repo file outside `/.knowledge/` is not a
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
        if first == os.path.basename(root):          # `/.knowledge/…` — this plugin's bundle-absolute form
            rest = tail
        elif not os.path.isdir(os.path.join(root, first)):
            return None                              # repo-absolute `/…` (e.g. `/.agents/…`) — not bundle-governed
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
      - `glossary-broken-link` the same link rule on `glossary.md`.
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


def _squash_ws(text: str) -> str:
    """Whitespace-insensitive form of a description. A table cell is one line and a YAML
    scalar may be wrapped across several, so comparing them byte-for-byte would report a
    line break as drift; every other difference still counts."""
    return " ".join(text.split())


def validate_generated_listing(bundle_root: str, corpus: dict) -> list[tuple[str, str, str, str]]:
    """The `<!-- BEGIN GENERATED -->` zone of `standards/index.md` against the docs on disk
    (both WARN, same class and same gate as the codes above):
      - `generated-listing-missing` a `standards/**` doc no row in the zone links.
      - `generated-listing-drift`   a row whose description no longer equals the doc's own.
    Consumes the `_build_corpus` dict — no disk reads of its own. Both findings are reported
    against the listing, because the listing is the file either one is fixed in.
    """
    root = os.path.abspath(bundle_root)
    listing = os.path.join(root, *GENERATED_LISTING_REL.split("/"))
    text = corpus.get(listing)
    if text is None:
        return []
    zone = GENERATED_ZONE_RE.search(text)
    if zone is None:
        return []

    findings: list[tuple[str, str, str, str]] = []
    subject_root = os.path.dirname(listing)
    listed: dict[str, str] = {}
    for target, cell in GENERATED_ROW_RE.findall(zone.group("zone")):
        res = _resolve_link(target.strip(), subject_root, root)
        if res and res[1] == "md":
            listed.setdefault(os.path.normpath(res[0]), cell)

    for ap in sorted(corpus):
        fn = os.path.basename(ap)
        if fn in RESERVED or fn in EXEMPT or fn == "README.md":
            continue
        if not ap.startswith(subject_root + os.sep):
            continue
        if os.path.normpath(ap) not in listed:
            rel = os.path.relpath(ap, root).replace(os.sep, "/")
            findings.append(("WARN", GENERATED_LISTING_REL, "generated-listing-missing",
                             f"`{rel}` is on disk but no row inside the GENERATED zone links it "
                             "(regenerate the zone)"))

    for ap, cell in sorted(listed.items()):
        doc = corpus.get(ap)
        if doc is None:
            continue          # a row pointing at nothing on disk is `index-broken-link`'s finding
        described = _squash_ws(str(parse_frontmatter(doc).get("description") or ""))
        if not described:
            continue          # no `description:` to compare against — `missing-description`'s
        if _squash_ws(cell) != described:
            rel = os.path.relpath(ap, root).replace(os.sep, "/")
            findings.append(("WARN", GENERATED_LISTING_REL, "generated-listing-drift",
                             f"the row for `{rel}` no longer matches that doc's frontmatter "
                             "`description` (regenerate the zone)"))
    return findings
