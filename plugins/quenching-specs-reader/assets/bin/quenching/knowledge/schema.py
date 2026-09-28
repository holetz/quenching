"""The OKF conformance vocabulary — the reserved names, the exempt ones, the recommended
fields, and the two glob tables every check agrees on.

Moved verbatim out of the pre-refactor OKF validator script, with TWO adjustments: `VERSION` is
imported from `quenching.common.version` rather than declared a second time, and `HERE`
is gone — it was dead in the original, computed at import and read by nothing.

THE CONFORMANCE CORE (single source — mirrored in the skills' `references/conformance.md`)
-----------------------------------------------------------------------------------------
Reserved filenames: `index.md` (a listing), `log.md` (a retired change history).
Exempt (skipped): harness pointer files (never OKF concepts).
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

The bundle root is the fixed `/docs/` convention — no knob names it, and no config moves it.
"""
from __future__ import annotations

import re

from quenching.common.git import COMMAND_TIMEOUT_S

# `log.md` is RETIRED, not unreserved: it keeps its slot here (and its skip in the
# PreToolUse hard block) so a log surviving in an already-aligned bundle stays
# recognized. Drop it from this tuple and every such file falls through to the
# concept-doc path — `missing-type` at ERROR, and denied writes under `hardBlock`.
RESERVED = ("index.md", "log.md")
# The bundle's one fixed concept doc, at a path the OKF contract pins. Its links are
# its content, so it is link-checked alongside the reserved listings.
GLOSSARY_REL = "glossary.md"
# Navigation/payload files — never OKF concepts, never required to carry a `type`.
# Both supported harness names can survive in one repository. Split the first literal so the
# Codex translation keeps the other harness pointer exempt as well.
CLAUDE_HARNESS = "CLAUDE" + ".md"
EXEMPT = (CLAUDE_HARNESS, "AGENTS.md")
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
GIT_TIMEOUT_S = COMMAND_TIMEOUT_S
# Directories that never need an `index.md` and hold no OKF concepts: `_`-prefixed
# private/raw sidecar folders (`_curadoria/`, `_azimutt/`), dotfolders, and common
# asset dirs. Pruned from the structural walk (dir-index / broken-link / orphan).
ASSET_DIRS = ("img", "imgs", "images", "assets", "static", "media", "node_modules", "__pycache__")
# Markdown inline-link target: capture what sits between `](` and the closing `)`.
LINK_RE = re.compile(r"\]\(([^)]+)\)")
# Pre-rename layout `okf-legacy-*` recognizes as migration debt — never a current OKF
# name, only ever compared against to find a target that has not run `knowledge:align` yet.
# Every root this plugin has declared before the current one, oldest first. `.docs` was the
# first; `.knowledge` replaced it; `.knowledge` was itself retired once a measured Zensical
# constraint (a dot-prefixed `docs_dir` renders zero pages) forced the root to lose its dot.
# Order carries no meaning — each is detected independently, on its own site.
LEGACY_ROOT_NAMES = (".docs", ".knowledge")
# Findings that judge a file **as an OKF concept doc**. Suppressed wholesale when the root
# carries no OKF signature: a directory that never claimed to be a bundle must say so once,
# not once per file it happens to contain. This is what keeps a target repo's ordinary
# `docs/` — the commonest folder name there is, and the same name as the OKF root since the
# dot came off — from reporting one ERROR per document.
CONCEPT_DOC_CODES = (
    "no-frontmatter", "broken-frontmatter", "missing-type", "okf-frontmatter-unparsed",
    "index-has-type", "index-has-frontmatter",
    "missing-title", "missing-description", "missing-resource", "missing-timestamp",
)
LEGACY_HOMES = {"knowledge": "concepts", "reference": "external"}
LEGACY_QUADRANTS = {"getting-started": "tutorials", "concepts": "explanation"}


def _nonempty(fm: dict, key: str) -> bool:
    return bool(str(fm.get(key, "")).strip())
