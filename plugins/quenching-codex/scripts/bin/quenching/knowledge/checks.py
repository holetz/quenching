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
  comment rule and the canonical case list are `/docs/standards/code/frontmatter-parser.md`.

  The set it reports SHRANK when the three parsers collapsed into
  `quenching.common.frontmatter`: that parser reads inline lists, block lists, block
  records, flow maps and block scalars, none of which this checker's own copy could read,
  so the `indented-continuation` it used to raise on each of them is gone. Nothing became
  invisible — it stopped denouncing forms it can now read.
"""
from __future__ import annotations

from quenching.common.frontmatter import frontmatter_anomalies, frontmatter_block, parse_frontmatter
from quenching.knowledge.schema import (
    LEGACY_HOMES,
    LEGACY_QUADRANTS,
    RECOMMENDED,
    TYPES_WITHOUT_RESOURCE,
    _nonempty,
)


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


# --------------------------------------------------------------------------- #
# PRE-RENAME LAYOUT DEBT (whole-bundle; ERROR — decided in ## Open Decisions,
# task renomear-docs-para-knowledge 2.1: the PreToolUse hard block never reads
# these findings, so `error` cannot deny a write)
#
# Each function below checks exactly one site and is idempotent — a migrated
# site simply stops appearing in its input. Unlike `check_concept`/`check_index`,
# these return complete (severity, rel, code, msg) tuples instead of leaving
# `rel` to the caller: a single call can name more than one site (`okf-legacy-home`
# on both `knowledge/` and `reference/`) or a site the caller has no single path
# for (`okf-legacy-glossary` on however many nested `glossary.md` exist).
# --------------------------------------------------------------------------- #
def check_legacy_root(legacy_root_rels: list[str]) -> list[tuple[str, str, str, str]]:
    """`okf-legacy-root` — call only once the new root is already known absent (the
    `no-bundle` branch); fires once per pre-rename sibling present beside it. There is more
    than one: the root has been renamed twice, and a target may sit at either former name."""
    return [("ERROR", rel, "okf-legacy-root",
             f"`{rel}` is a pre-rename bundle root — migrate it to the OKF root (`docs/`)")
            for rel in legacy_root_rels]


def check_okf_signature(has_root_index: bool, has_okf_version: bool,
                        root_rel: str) -> list[tuple[str, str, str, str]]:
    """`not-an-okf-bundle` — the directory exists but never claims to be a bundle. The
    signature is the root `index.md` carrying `okf_version`; nothing else in the tree can
    stand in for it, because every other file is exactly what is in question.

    This check earns its place from the root's own name. While the root was dotted, no
    repository had one by accident and pointing the validator at a non-bundle was operator
    error. `docs/` is the commonest documentation folder in existence, so the same mistake is
    now the default case — and without this gate it answers with one ERROR per file."""
    if has_root_index and has_okf_version:
        return []
    missing = "has no `index.md`" if not has_root_index else "`index.md` declares no `okf_version`"
    return [("ERROR", root_rel, "not-an-okf-bundle",
             f"`{root_rel}/` {missing} — it is a directory, not an OKF bundle; "
             f"`quenching-knowledge-align` converts one, and per-file OKF findings are "
             f"withheld until it does")]


def check_legacy_home(root_entries: set[str]) -> list[tuple[str, str, str, str]]:
    """`okf-legacy-home` — a pre-rename home (`knowledge/`, `reference/`) sits at the
    bundle root instead of its OKF name (`concepts/`, `external/`)."""
    return [
        ("ERROR", f"{old}/", "okf-legacy-home", f"`{old}/` is the pre-rename home — rename it to `{new}/`")
        for old, new in LEGACY_HOMES.items() if old in root_entries
    ]


def check_legacy_doc_quadrant(quadrant_entries: set[str]) -> list[tuple[str, str, str, str]]:
    """`okf-legacy-doc-quadrant` — a pre-rename Diátaxis quadrant under `documentation/`."""
    return [
        ("ERROR", f"documentation/{old}/", "okf-legacy-doc-quadrant",
         f"`documentation/{old}/` is the pre-rename Diátaxis name — rename it to `documentation/{new}/`")
        for old, new in LEGACY_QUADRANTS.items() if old in quadrant_entries
    ]


def check_legacy_glossary(glossary_rels: list[str], canonical: str,
                          generated: set[str] | None = None) -> list[tuple[str, str, str, str]]:
    """`okf-legacy-glossary` — a `glossary.md` sitting inside a home instead of at the
    bundle root, where the OKF contract pins it. A generated documentation projection is the
    one intentional nested copy: it is a published route, not a second canonical glossary."""
    generated = generated or set()
    return [
        ("ERROR", rel, "okf-legacy-glossary",
         f"`{rel}` — the glossary lives at the bundle root (`{canonical}`), not inside a home")
        for rel in glossary_rels if rel != canonical and rel not in generated
    ]
