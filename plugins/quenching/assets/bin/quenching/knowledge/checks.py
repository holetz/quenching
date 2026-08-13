"""The conformance core — one function per file kind, returning (severity, code, msg).

Moved verbatim out of the pre-refactor OKF validator script. The ONE mechanical change is the
frontmatter call shape: `parse_frontmatter` now returns the bare dict, and the two bits
these checks also need — does the file open a `---` fence, does that fence close — come
from the `frontmatter_block` sidecar beside it.

PARSE HONESTY (per-doc; WARN — this checker naming its own misread)
- **`okf-frontmatter-unparsed`** the frontmatter held something the parser could not
  represent faithfully: a stripped trailing comment, an unterminated quote, an indented
  continuation read as empty, or a duplicate top-level key that silently last-wins. It
  reports a suspicion it cannot resolve rather than letting the consequence surface as a
  content finding (`missing-type`, a missing recommended field). The YAML subset, the
  comment rule and the canonical case list are `/.knowledge/standards/code/frontmatter-parser.md`.

  The set it reports SHRANK when the three parsers collapsed into
  `quenching.common.frontmatter`: that parser reads inline lists, block lists, block
  records, flow maps and block scalars, none of which this checker's own copy could read,
  so the `indented-continuation` it used to raise on each of them is gone. Nothing became
  invisible — it stopped denouncing forms it can now read.
"""
from __future__ import annotations

from quenching.common.frontmatter import frontmatter_anomalies, frontmatter_block, parse_frontmatter
from quenching.knowledge.schema import RECOMMENDED, TYPES_WITHOUT_RESOURCE, _nonempty


def check_concept(text: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    fm = parse_frontmatter(text)
    has_block, well_formed = frontmatter_block(text)
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
    fm = parse_frontmatter(text)
    has_block, well_formed = frontmatter_block(text)
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
