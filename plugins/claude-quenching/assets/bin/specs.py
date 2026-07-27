#!/usr/bin/env python3
"""specs.py — self-contained deterministic trail for the `specs/` front.

Payload of the `claude-quenching` plugin, sibling of `assets/hooks/okf-validate.py`
and built in the same mold: stdlib-only, ZERO dependencies (its own minimal
frontmatter parser — no PyYAML), one script installed alone into a target repo.

ONE SPEC IS ONE FILE
--------------------
A spec is a single markdown file for its whole lifecycle. Phases enrich it; they
never split it. The file moves between three phase folders and is never renamed:

    specs/
      backlog/                   # DEFINITION — captured -> proposed -> designed -> refined
        index.md                 # listing with a GENERATED zone (see `backlog reindex`)
        2026-07-25-<slug>.md
      ready/                     # EXECUTION — ready to build, or building
        2026-07-14-<slug>.md
      archive/                   # done or abandoned, told apart by `outcome:` frontmatter
        2026-06-30-<slug>.md

THE FOLDER IS THE PHASE, and it is the single truth — there is no `phase:` field,
because two declared sources of one fact diverge and a folder cannot lie. The
transition is a `git mv` performed by `promote`, so `git log` narrates the lifecycle.

IDENTITY IS THE SLUG, not the path. Every command names the bare slug; this tool
resolves it to the one file whose name ends in `-<slug>.md`, wherever it sits. Two
matches is a REFUSAL (exit 2), never a guess.

THE DATE PREFIX is stamped once, at capture, and never rewritten — so the basename is
stable for the whole lifecycle, `git log --follow` reads as one history, and a plain
`ls` of any folder is chronological. A file listing IS the status view, and no file
listing reads frontmatter.

THIRTEEN CANONICAL SECTIONS, and the explicit-none rule is PHASE-SCOPED
-----------------------------------------------------------------------
`## Problem`, `## Proposal`, `## Out of Scope`, `## Impact`, `## Validation`,
`## Design`, `## Alternatives Considered`, `## Open Decisions`, `## Risks`,
`## Handoff`, `## Tasks`, `## Discoveries`, `## Outcome`.

Headings are a PARSED contract — canonical English, exactly as written. A heading
outside the set is a stray. Each canonical heading is in one of three states:

  absent               its phase was never reached — legal before its own gate
  present, empty       MALFORMED: neither an answer nor a not-yet; refuses
  present, filled      OK (`- none — <reason>` counts as filled)

A heading is required — and required to carry an explicit none — only once ITS OWN
phase gate is reached. That scoping is what keeps a captured spec four lines long
instead of a thirteen-heading skeleton, and it is what keeps the derived stage honest:
applied absolutely, a fresh spec carrying thirteen `- none` sections would derive as
`designed` and pass every gate without anyone having thought anything.

DERIVED STAGES, never declared. Computed from heading presence and frontmatter, so
they regress automatically when a section empties. Declared state is forgotten on edit.

There is NO `.specs.json`, no attempt counter, and no delta format. A blocked task is
a visible `- [!] <id> <title> — blocked: <reason>` marker in `## Tasks`.

OUTPUT CONTRACT (uniform across every subcommand)
-------------------------------------------------
`--json` on every subcommand, and STRICT exit codes so the skill branches on data:
  0  ok
  1  findings (validate/doctor found something; a spec/task was not found)
  2  refusal  (an ambiguous slug; a gate not met; archiving `done` with open tasks)

WORKSPACE RESOLUTION
  --root PATH, else $SPECS_ROOT, else the nearest `specs/` directory walking up from
  cwd (or cwd itself if it is named `specs`). `new` creates `./specs` when none exists.

ASSETS
  Schema and template load from `<script>/../specs/` when present (so editing the
  shipped `assets/specs/schema.json` / `assets/specs/templates/spec.md` changes
  behavior in the plugin), and fall back to the constants embedded below — so an
  installed copy under `.claude/hooks/` with no adjacent assets still works.
  EDIT BOTH OR NEITHER.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import sys

VERSION = "3.0.0"  # kept in lockstep with the plugin VERSION file, plugin.json, and okf-validate.py

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.normpath(os.path.join(HERE, "..", "specs"))

PHASES = ("backlog", "ready", "archive")
SPEC_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# `- [ ]` / `- [x]` / `- [!]` — the third is a BLOCKED task, visible and human-legible,
# which is what replaced v1's hidden five-attempt counter in `.specs.json`.
CHECKBOX_RE = re.compile(r"^(\s*)-\s\[( |x|X|!)\]\s+(.*)$")
CHECKBOX_LOOSE_RE = re.compile(r"^\s*-\s*\[.*?\]")   # looks like a checkbox (malformed detection)
TASK_ID_RE = re.compile(r"^(\d+(?:\.\d+)*)\b")
TASK_META_RE = re.compile(r"^\s+(files|pattern|verify)\s*:\s*(.+?)\s*$", re.IGNORECASE)
PARALLEL_RE = re.compile(r"^\[P\](?:\s|$)")
BLOCKED_REASON_RE = re.compile(r"—\s*blocked\s*:\s*(.+?)\s*$", re.IGNORECASE)

VERIFICATION_POLICIES = ("per-task", "per-section", "end-of-plan")
DEFAULT_VERIFICATION = "per-section"
OUTCOMES = ("done", "abandoned")

PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET_RE = re.compile(r"^\s*[-*+]\s")
SUBHEADING_RE = re.compile(r"^\s*(?:#{1,6}\s+|\*\*\S)")
STANDARD_PATH_RE = re.compile(r"docs/standards/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*\.md")

GEN_BEGIN = "<!-- BEGIN GENERATED"
GEN_END = "<!-- END GENERATED -->"
BACKLOG_EMPTY = ("_(no specs captured — this listing is regenerated deterministically "
                 "from `backlog/*.md`)_")

# --------------------------------------------------------------------------- #
# embedded assets (fallbacks when the sibling asset files are absent)
# Keep in lockstep with assets/specs/schema.json and assets/specs/templates/spec.md.
# --------------------------------------------------------------------------- #
DEFAULT_SCHEMA: dict = {
    "schema": "spec-lifecycle",
    "version": "2.0.0",
    "filename": {
        "pattern": r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$",
        "groups": ["date", "slug"],
        "example": "2026-07-25-session-tokens.md",
    },
    "frontmatter": {
        "required": ["slug", "title", "verification"],
        "optional": ["refined", "outcome"],
        "verification": list(VERIFICATION_POLICIES),
        "outcome": list(OUTCOMES),
    },
    "sections": [
        {"heading": "Problem", "order": 1, "group": "definition", "audience": "human"},
        {"heading": "Proposal", "order": 2, "group": "definition", "audience": "human"},
        {"heading": "Out of Scope", "order": 3, "group": "definition", "audience": "human"},
        {"heading": "Impact", "order": 4, "group": "definition", "audience": "human", "parsed": True},
        {"heading": "Validation", "order": 5, "group": "definition", "audience": "both"},
        {"heading": "Design", "order": 6, "group": "definition", "audience": "human"},
        {"heading": "Alternatives Considered", "order": 7, "group": "definition", "audience": "human"},
        {"heading": "Open Decisions", "order": 8, "group": "definition", "audience": "human"},
        {"heading": "Risks", "order": 9, "group": "definition", "audience": "human"},
        {"heading": "Handoff", "order": 10, "group": "execution", "audience": "agent"},
        {"heading": "Tasks", "order": 11, "group": "execution", "audience": "agent"},
        {"heading": "Discoveries", "order": 12, "group": "execution", "audience": "triage"},
        {"heading": "Outcome", "order": 13, "group": "archive", "audience": "human"},
    ],
    "impact": {
        "parsedSubheading": "Standards this spec will write into docs/standards/",
        "acceptedAliases": ["Standards this plan will write into docs/standards/"],
        "pathPrefix": "docs/standards/",
    },
    "phases": [
        {"id": "backlog", "folder": "backlog", "role": "definition",
         "entryGate": ["Problem"], "warnWhenEmpty": []},
        {"id": "ready", "folder": "ready", "role": "execution",
         "entryGate": ["Problem", "Proposal", "Out of Scope", "Impact", "Validation",
                       "Design", "Alternatives Considered", "Open Decisions", "Risks", "Tasks"],
         "warnWhenEmpty": ["Handoff"]},
        {"id": "archive", "folder": "archive", "role": "closed",
         "entryGate": ["Outcome"], "warnWhenEmpty": []},
    ],
    "promote": {
        "sequence": ["backlog", "ready", "archive"],
        "explicitNone": "- none — <reason>",
        "filledRule": "An explicit none counts as FILLED. A heading present with an empty body "
                      "is malformed and refuses. An absent heading before its own gate is legal.",
        "openTasks": {"done": "refuse", "abandoned": "allow", "forceFlag": "--force"},
    },
    "stages": {
        "resolution": "last-match-wins",
        "derived": [
            {"id": "captured", "phase": "backlog", "when": {"filled": ["Problem"]}},
            {"id": "proposed", "phase": "backlog", "when": {"filled": ["Proposal"]}},
            {"id": "designed", "phase": "backlog", "when": {"filled": ["Design"]}},
            {"id": "refined", "phase": "backlog", "when": {"frontmatter": "refined"}},
            {"id": "executing", "phase": "ready",
             "when": {"anyOf": [{"taskState": ["x", "!"]}, {"filled": ["Handoff"]}]}},
        ],
    },
}

TEMPLATE_SPEC = """---
slug: <SLUG>
title: <TITLE>
verification: <VERIFICATION>
---

# <TITLE>

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading is created on first
     write by `specs.py section <slug> "<Heading>" --write`, which inserts it in canonical
     position.

     THE PHASE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN phase gate is reached:

       new (capture)        `## Problem`
       promote -> ready/    the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready/  (warn only)  `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written. Body prose
     follows the repo's language. A heading outside this set is a stray. -->

## Problem

<!-- AUDIENCE: human. Gate: new (capture).

     The problem or opportunity this spec answers, and why now. This is the only section a
     freshly captured spec carries — write it even if it is two sentences. -->
"""


# --------------------------------------------------------------------------- #
# minimal frontmatter parser (deliberately duplicated from okf-validate.py so
# each script stays self-contained — ~40 lines, no shared module)
# --------------------------------------------------------------------------- #
def parse_frontmatter(text: str) -> dict:
    """Top-level `key: value` pairs of a leading `---` block. List values are
    returned as Python lists for inline `[a, b]` and block `- item` forms; scalars
    as strings with surrounding quotes stripped. Empty dict when there is no block."""
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return {}
    close = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close = i
            break
    if close is None:
        return {}
    body = lines[1:close]
    fm: dict = {}
    j = 0
    while j < len(body):
        raw = body[j]
        if not raw.strip() or raw.lstrip().startswith("#") or raw[:1] in (" ", "\t"):
            j += 1
            continue
        if ":" not in raw:
            j += 1
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = val.split("#", 1)[0].strip() if "#" in val else val.strip()
        if val == "":
            items = []
            k = j + 1
            while k < len(body) and body[k][:1] in (" ", "\t") and body[k].lstrip().startswith("- "):
                items.append(body[k].lstrip()[2:].strip().strip("'\""))
                k += 1
            if items:
                fm[key] = items
                j = k
                continue
            fm[key] = ""
            j += 1
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key] = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()] if inner else []
        elif val.startswith("{") and val.endswith("}"):
            inner = val[1:-1].strip()
            rec: dict = {}
            for part in inner.split(","):
                if ":" in part:
                    k2, _, v2 = part.partition(":")
                    rec[k2.strip()] = v2.strip().strip("'\"")
            fm[key] = rec
        else:
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
                val = val[1:-1]
            fm[key] = val
        j += 1
    return fm


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


def titleize(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.replace("_", "-").split("-") if w)


def today() -> str:
    return datetime.date.today().isoformat()


def read_text(path: str) -> str | None:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def write_text(path: str, text: str) -> None:
    pathlib.Path(path).write_text(text, encoding="utf-8")


def load_schema() -> dict:
    p = os.path.join(ASSET_DIR, "schema.json")
    txt = read_text(p)
    if txt:
        try:
            obj = json.loads(txt)
            if isinstance(obj, dict) and obj.get("sections"):
                return obj
        except json.JSONDecodeError:
            pass
    return DEFAULT_SCHEMA


def load_template() -> str:
    """The FULL thirteen-section authoring reference — frontmatter, the contract preamble,
    and every heading with its guidance comment.

    Two consumers read it and they need different slices: `new` stamps only the capture
    form (below), while `section --write` pulls one heading's guidance when creating it.
    Keeping one source for both is what stops the guidance drifting from the contract."""
    txt = read_text(os.path.join(ASSET_DIR, "templates", "spec.md"))
    return txt if txt is not None else TEMPLATE_SPEC


def capture_form(template_text: str | None = None) -> str:
    """What `new` stamps: everything up to (not including) the SECOND `## ` heading — so
    frontmatter, the contract preamble, and `## Problem` with its guidance, and nothing else.

    A captured spec is four lines of body, not a thirteen-heading skeleton. That is not
    cosmetic: the explicit-none rule makes `- none — <reason>` count as filled, so a spec
    born with thirteen headings would derive as `designed` and pass every promote gate
    without anyone having thought anything."""
    text = template_text if template_text is not None else load_template()
    seen = 0
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) == 2:
            seen += 1
            if seen == 2:
                return "".join(lines[:i]).rstrip() + "\n"
    return text


def section_guidance(heading: str, template_text: str | None = None) -> str:
    """One heading's block from the template — the heading line plus its guidance comment,
    used by `section --write` when it creates a heading that does not exist yet."""
    text = template_text if template_text is not None else load_template()
    lines = text.splitlines()
    want = heading.strip().lower()
    start = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) == 2:
            if start is not None:
                return "\n".join(lines[start:i]).rstrip() + "\n"
            if m.group(2).strip().lower() == want:
                start = i
    if start is not None:
        return "\n".join(lines[start:]).rstrip() + "\n"
    return f"## {heading}\n"


def canonical_headings(schema: dict | None = None) -> list[str]:
    s = schema or load_schema()
    return [x["heading"] for x in sorted(s["sections"], key=lambda d: d.get("order", 0))]


def phase_spec(phase: str, schema: dict | None = None) -> dict:
    s = schema or load_schema()
    for p in s.get("phases", []):
        if p.get("id") == phase:
            return p
    return {"id": phase, "folder": phase, "entryGate": [], "warnWhenEmpty": []}


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def mask_comments(text: str) -> str:
    """Blank out HTML-comment spans, preserving every newline and column so line numbers
    and offsets still line up with the original.

    The template documents the task format with example checkboxes inside its comment
    guidance. Without this, those examples parse as real tasks and a freshly captured spec
    reports phantom progress — and `task --check` needs the surviving `lineno` to point at
    the true line, which stripping (rather than masking) would break."""
    return re.sub(r"<!--.*?-->",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                  text, flags=re.DOTALL)


def body_after_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def has_real_content(text: str) -> bool:
    """True when a block carries authored prose beyond the shipped template (headings,
    HTML comments, and `<placeholder>` lines don't count).

    `- none — <reason>` DOES count: an explicit null is an answer, and the whole
    explicit-none rule depends on this returning True for it."""
    body = strip_comments(text)
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        residue = PLACEHOLDER_RE.sub("", s)
        residue = re.sub(r"^[-*+]\s*(\[.?\])?\s*", "", residue)  # drop list/checkbox markers
        residue = re.sub(r"^\d+(?:\.\d+)*\s*", "", residue)      # drop a leading task id
        if re.search(r"[A-Za-z0-9]", residue):
            return True
    return False


# --------------------------------------------------------------------------- #
# workspace resolution and spec discovery
# --------------------------------------------------------------------------- #
def find_specs_root(root_arg: str | None) -> str:
    if root_arg:
        return os.path.abspath(root_arg)
    env = os.environ.get("SPECS_ROOT")
    if env:
        return os.path.abspath(env)
    cur = os.path.abspath(os.getcwd())
    if os.path.basename(cur) == "specs":
        return cur
    d = cur
    while True:
        cand = os.path.join(d, "specs")
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.join(cur, "specs")   # default (created by `new`)


def spec_files(root: str, phase: str | None = None) -> list[dict]:
    """Every conformant spec file across the phase folders, oldest first within each.

    A file whose name does not match `YYYY-MM-DD-<slug>.md` is NOT returned — it is a
    finding for `validate`/`doctor` to report, not something to silently half-support."""
    out: list[dict] = []
    for ph in ([phase] if phase else PHASES):
        d = os.path.join(root, ph)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            m = SPEC_FILE_RE.match(name)
            if not m:
                continue
            out.append({
                "phase": ph,
                "file": name,
                "path": os.path.join(d, name),
                "date": m.group(1),
                "slug": m.group(2),
            })
    return out


def resolve_slug(root: str, slug: str) -> tuple[dict | None, list[dict]]:
    """The one spec file whose basename ends in `-<slug>.md`, wherever it sits.

    Returns (spec, matches). TWO MATCHES IS A REFUSAL, never a guess: the caller exits 2
    and names both paths. This is what makes N folder moves survivable — every
    cross-reference names the bare slug and never a path."""
    matches = [s for s in spec_files(root) if s["slug"] == slug]
    return (matches[0] if len(matches) == 1 else None), matches


# --------------------------------------------------------------------------- #
# the single-file parser
# --------------------------------------------------------------------------- #
def parse_sections(text: str) -> dict[str, dict]:
    """Every level-2 section of a spec file, keyed by its heading text.

    Sub-headings (`###`+) belong to their parent section — `## Impact` carries its parsed
    `### Standards …` sub-heading, and splitting on them would orphan it.

    Each entry carries `lines` (the body), `lineno` (0-based, of the heading itself), and
    `filled` — the three-state distinction the whole contract rests on: a heading that is
    present but empty is MALFORMED, which is neither an answer nor a not-yet."""
    out: dict[str, dict] = {}
    current: str | None = None
    buf: list[str] = []
    start = 0
    lines = text.splitlines()

    def flush() -> None:
        if current is not None and current not in out:
            body = "\n".join(buf)
            out[current] = {"lines": list(buf), "lineno": start,
                            "filled": has_real_content(body), "body": body}

    for lineno, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) == 2:
            flush()
            current = m.group(2).strip()
            buf = []
            start = lineno
            continue
        if current is not None:
            buf.append(line)
    flush()
    return out


def section_state(sections: dict, heading: str) -> str:
    """`absent` · `empty` (present but malformed) · `filled`."""
    if heading not in sections:
        return "absent"
    return "filled" if sections[heading]["filled"] else "empty"


def stray_headings(sections: dict, schema: dict | None = None) -> list[str]:
    canon = set(canonical_headings(schema))
    return [h for h in sections if h not in canon]


def derive_stage(spec: dict, sections: dict, fm: dict, tasks: list[dict],
                 schema: dict | None = None) -> str:
    """The sub-stage, COMPUTED from section completeness and frontmatter — never declared.

    Declared state is forgotten on edit and goes stale; derived state regresses on its own
    when a section empties. Rules are evaluated in schema order and the LAST match wins."""
    s = schema or load_schema()
    stage = spec["phase"]
    for rule in s.get("stages", {}).get("derived", []):
        if rule.get("phase") != spec["phase"]:
            continue
        if _stage_match(rule.get("when", {}), sections, fm, tasks):
            stage = rule["id"]
    return stage


def _stage_match(when: dict, sections: dict, fm: dict, tasks: list[dict]) -> bool:
    if "anyOf" in when:
        return any(_stage_match(w, sections, fm, tasks) for w in when["anyOf"])
    if "filled" in when:
        return all(section_state(sections, h) == "filled" for h in when["filled"])
    if "frontmatter" in when:
        return bool(fm.get(when["frontmatter"]))
    if "taskState" in when:
        want = set(when["taskState"])
        return any(t["state"] in want for t in tasks)
    return False


def parse_tasks(text: str) -> list[dict]:
    """Every checkbox under `## Tasks`, in order: index, explicit id, state, text, line
    number, the `[P]` marker, the optional indented metadata (`files`/`pattern`/`verify`),
    and — for a blocked task — the reason written right in the line.

    `state` is `" "` (open), `"x"` (done) or `"!"` (blocked). The blocked marker is
    deliberately IN THE FILE rather than in sidecar state: it is what a human reads when
    they come to unblock it, and v1's hidden attempt counter was read by nobody."""
    sections = parse_sections(mask_comments(text))
    if "Tasks" not in sections:
        return []
    base = sections["Tasks"]["lineno"] + 1
    lines = sections["Tasks"]["lines"]
    out = []
    idx = 0
    section = 0
    for i, line in enumerate(lines):
        hm = HEADING_RE.match(line)
        if hm and len(hm.group(1)) == 3:
            section += 1          # a `### N.` heading starts a new task section
            continue
        m = CHECKBOX_RE.match(line)
        if not m:
            continue
        idx += 1
        state = m.group(2).lower()
        body = m.group(3).strip()
        idm = TASK_ID_RE.match(body)
        rest = body[idm.end():].lstrip() if idm else body
        parallel = bool(PARALLEL_RE.match(rest))
        blocked = BLOCKED_REASON_RE.search(body)
        files: list[str] = []
        pattern = verify = None
        for cont in lines[i + 1:]:
            # the task's block ends at a blank line, a non-indented line, or another
            # checkbox; anything else indented is scanned, so a wrapped prose line between
            # the checkbox and its `verify:` does not hide it.
            if not cont.strip() or cont[:1] not in (" ", "\t") or CHECKBOX_RE.match(cont):
                break
            mm = TASK_META_RE.match(cont)
            if not mm:
                continue
            key, val = mm.group(1).lower(), mm.group(2).strip()
            if key == "files":
                files = [p.strip() for p in val.split(",") if p.strip()]
            elif key == "pattern":
                pattern = val
            else:
                verify = val
        out.append({
            "index": idx,
            "id": idm.group(1) if idm else None,
            "state": state,
            "checked": state == "x",
            "blocked": state == "!",
            "reason": blocked.group(1) if blocked else None,
            "text": body,
            "lineno": base + i,
            "section": section,
            "parallel": parallel,
            "files": files,
            "pattern": pattern,
            "verify": verify,
        })
    return out


def task_progress(tasks: list[dict]) -> tuple[int, int, int]:
    """(checked, blocked, total)."""
    return (sum(1 for t in tasks if t["checked"]),
            sum(1 for t in tasks if t["blocked"]),
            len(tasks))


def parse_impact_standards(text: str, schema: dict | None = None) -> list[str]:
    """The `docs/standards/**.md` paths a spec DECLARES it will write, read from the one
    fixed sub-heading of `## Impact`.

    Only that sub-heading is parsed, and deliberately so. Its siblings name paths the spec
    does NOT promise to write — a background standard it *may* resolve, the product code it
    touches — and parsing those would flag a spec for not writing a doc it never claimed. A
    spec with no such sub-heading declares nothing and is never flagged: the check is
    opt-in by writing the heading."""
    s = schema or load_schema()
    imp = s.get("impact", {})
    anchors = [imp.get("parsedSubheading", "")] + list(imp.get("acceptedAliases", []))
    anchor_re = re.compile(
        r"^\s*(?:#{3,6}\s+|\*\*)\s*(?:" +
        "|".join(re.escape(a.rstrip("/ ")) for a in anchors if a) + r")",
        re.IGNORECASE)
    sections = parse_sections(strip_comments(text))
    if "Impact" not in sections:
        return []
    out: list[str] = []
    seen: set[str] = set()
    collecting = False
    for line in sections["Impact"]["lines"]:
        if anchor_re.match(line):
            collecting = True
            continue
        if SUBHEADING_RE.match(line):     # any other sub-heading closes the parsed zone
            collecting = False
            continue
        if not collecting or not BULLET_RE.match(line):
            continue
        # An unfilled `<placeholder>` declares nothing — the same rule has_real_content
        # uses. Without it the shipped template's own example bullet would make every
        # freshly captured spec report sp-impact-uncovered against a path nobody wrote.
        for m in STANDARD_PATH_RE.finditer(PLACEHOLDER_RE.sub("", line)):
            if m.group(0) not in seen:
                seen.add(m.group(0))
                out.append(m.group(0))
    return out


def load_spec(root: str, slug: str) -> tuple[dict | None, dict]:
    """Resolve a slug and read everything derivable from its file in one pass.

    Returns (info, err). `err` carries a ready-to-emit refusal when the slug is unknown or
    ambiguous, so every command handles both the same way."""
    spec, matches = resolve_slug(root, slug)
    if len(matches) > 1:
        return None, {
            "code": "sp-ambiguous-slug", "exit": 2, "slug": slug,
            "matches": [f"{m['phase']}/{m['file']}" for m in matches],
            "message": f"slug '{slug}' matches {len(matches)} files — "
                       f"{', '.join(m['phase'] + '/' + m['file'] for m in matches)}",
        }
    if not spec:
        return None, {"code": "sp-unknown-slug", "exit": 1, "slug": slug,
                      "message": f"no spec with slug '{slug}'"}
    text = read_text(spec["path"]) or ""
    fm = parse_frontmatter(text)
    sections = parse_sections(body_after_frontmatter(text))
    tasks = parse_tasks(text)
    info = dict(spec)
    info.update({
        "text": text,
        "frontmatter": fm,
        "sections": sections,
        "tasks": tasks,
        "stage": derive_stage(spec, sections, fm, tasks),
        "verification": _policy(fm),
    })
    return info, {}


def _policy(fm: dict) -> str:
    v = str(fm.get("verification", "")).strip().lower()
    return v if v in VERIFICATION_POLICIES else DEFAULT_VERIFICATION


def gate_report(info: dict, phase: str, schema: dict | None = None) -> dict:
    """What stands between this spec and `phase`: every gate section that is absent or
    present-but-empty. `- none — <reason>` counts as filled and never appears here."""
    ph = phase_spec(phase, schema)
    missing, malformed = [], []
    for h in ph.get("entryGate", []):
        st = section_state(info["sections"], h)
        if st == "absent":
            missing.append(h)
        elif st == "empty":
            malformed.append(h)
    warn = [h for h in ph.get("warnWhenEmpty", [])
            if section_state(info["sections"], h) != "filled"]
    return {"phase": phase, "missing": missing, "malformed": malformed,
            "warn": warn, "ok": not missing and not malformed}


# --------------------------------------------------------------------------- #
# output
# --------------------------------------------------------------------------- #
def emit(as_json: bool, obj: dict, human: str) -> None:
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        print(human)


def emit_err(as_json: bool, err: dict) -> int:
    emit(as_json, {"ok": False, **{k: v for k, v in err.items() if k != "exit"}},
         f"error: {err['message']}")
    return err.get("exit", 1)


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_new(args, root: str) -> int:
    """Scaffold `backlog/YYYY-MM-DD-<slug>.md` carrying `## Problem` and nothing else.

    THE DATE IS STAMPED HERE AND NEVER AGAIN — `promote` moves the file without renaming
    it, so this basename is the spec's identity for its whole lifecycle."""
    slug = slugify(args.name)
    if not SLUG_RE.match(slug):
        emit(args.json, {"ok": False, "code": "sp-bad-slug", "slug": args.name,
                         "message": f"'{args.name}' does not reduce to a kebab-case slug"},
             f"error: '{args.name}' does not reduce to a kebab-case slug")
        return 2
    _, matches = resolve_slug(root, slug)
    if matches:
        m = matches[0]
        emit(args.json, {"ok": False, "code": "sp-slug-exists", "slug": slug,
                         "existing": f"{m['phase']}/{m['file']}",
                         "message": f"slug '{slug}' already exists at {m['phase']}/{m['file']}"},
             f"refused: slug '{slug}' already exists at {m['phase']}/{m['file']}")
        return 2
    policy = args.verification or DEFAULT_VERIFICATION
    title = args.title or titleize(slug)
    name = f"{today()}-{slug}.md"
    dest_dir = os.path.join(root, "backlog")
    os.makedirs(dest_dir, exist_ok=True)
    body = (capture_form()
            .replace("<SLUG>", slug)
            .replace("<TITLE>", title)
            .replace("<VERIFICATION>", policy))
    path = os.path.join(dest_dir, name)
    write_text(path, body)
    emit(args.json,
         {"ok": True, "slug": slug, "title": title, "verification": policy,
          "phase": "backlog", "file": name, "stage": "backlog",
          "path": os.path.relpath(path, os.path.dirname(root)).replace(os.sep, "/")},
         f"created backlog/{name}  (slug: {slug} · verification: {policy})\n"
         f"next: write ## Problem, then `specs.py section {slug} Proposal --write`")
    return 0


def cmd_list(args, root: str) -> int:
    specs = spec_files(root)
    rows = []
    for s in specs:
        text = read_text(s["path"]) or ""
        fm = parse_frontmatter(text)
        sections = parse_sections(body_after_frontmatter(text))
        tasks = parse_tasks(text)
        checked, blocked, total = task_progress(tasks)
        rows.append({
            "slug": s["slug"], "phase": s["phase"], "file": s["file"], "date": s["date"],
            "title": fm.get("title", titleize(s["slug"])),
            "stage": derive_stage(s, sections, fm, tasks),
            "outcome": fm.get("outcome") or None,
            "tasks": {"checked": checked, "blocked": blocked, "total": total},
        })
    if args.json:
        print(json.dumps({"ok": True, "root": root, "count": len(rows), "specs": rows},
                         indent=2, ensure_ascii=False))
        return 0
    if not rows:
        print(f"no specs under {root}")
        return 0
    print(f"specs — {root} ({len(rows)})")
    for ph in PHASES:
        group = [r for r in rows if r["phase"] == ph]
        if not group:
            continue
        print(f"\n  {ph}/")
        for r in group:
            prog = (f"  {r['tasks']['checked']}/{r['tasks']['total']}"
                    if r["tasks"]["total"] else "")
            blk = f" · {r['tasks']['blocked']} blocked" if r["tasks"]["blocked"] else ""
            oc = f" · {r['outcome']}" if r["outcome"] else ""
            print(f"    {r['date']}  {r['slug']:<28} [{r['stage']}]{prog}{blk}{oc}")
    return 0


def _next_phase(phase: str, schema: dict | None = None) -> str | None:
    seq = (schema or load_schema()).get("promote", {}).get("sequence", list(PHASES))
    return seq[seq.index(phase) + 1] if phase in seq and seq.index(phase) + 1 < len(seq) else None


def cmd_status(args, root: str) -> int:
    info, err = load_spec(root, args.spec)
    if err:
        return emit_err(args.json, err)
    checked, blocked, total = task_progress(info["tasks"])
    dest = _next_phase(info["phase"])
    gates = gate_report(info, dest) if dest else None
    sections = [{"heading": h, "state": section_state(info["sections"], h)}
                for h in canonical_headings()]
    obj = {
        "ok": True, "slug": info["slug"], "title": info["frontmatter"].get("title", ""),
        "phase": info["phase"], "stage": info["stage"], "file": info["file"],
        "date": info["date"], "verification": info["verification"],
        "refined": info["frontmatter"].get("refined") or None,
        "outcome": info["frontmatter"].get("outcome") or None,
        "sections": sections,
        "strays": stray_headings(info["sections"]),
        "tasks": {"checked": checked, "blocked": blocked, "total": total,
                  "blockedTasks": [{"id": t["id"], "text": t["text"], "reason": t["reason"]}
                                   for t in info["tasks"] if t["blocked"]]},
        "promote": gates,
    }
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0
    print(f"{info['slug']} — {obj['title']}")
    print(f"  {info['phase']}/{info['file']}  [{info['stage']}]  "
          f"verification: {info['verification']}")
    if total:
        print(f"  tasks: {checked}/{total} complete" +
              (f" · {blocked} blocked" if blocked else ""))
    for s in sections:
        mark = {"filled": "✓", "empty": "!", "absent": "·"}[s["state"]]
        print(f"    {mark} ## {s['heading']}")
    if obj["strays"]:
        print(f"  strays: {', '.join(obj['strays'])}")
    if gates:
        if gates["ok"]:
            print(f"  promote → {dest}/: ready")
        else:
            if gates["missing"]:
                print(f"  promote → {dest}/: missing {', '.join(gates['missing'])}")
            if gates["malformed"]:
                print(f"  promote → {dest}/: empty (malformed) {', '.join(gates['malformed'])}")
    return 0


def _canonical_index(heading: str, schema: dict | None = None) -> int:
    canon = canonical_headings(schema)
    return canon.index(heading) if heading in canon else len(canon)


def _match_heading(heading: str) -> str | None:
    """Case-insensitive lookup onto the canonical spelling. Headings are a parsed contract,
    so the FILE always carries canonical English — but a human typing `specs.py section x
    validation` should not get a stray section for their trouble."""
    want = heading.strip().lower()
    for h in canonical_headings():
        if h.lower() == want:
            return h
    return None


def upsert_section(info: dict, heading: str, block: str) -> tuple[str, str]:
    """Replace a section's block, or create it in CANONICAL POSITION when absent.

    Position is derived from the schema's declared order, not from where the writer
    happened to be: a spec whose `## Tasks` was written before its `## Proposal` still
    reads in contract order, so a human and the parser see the same document."""
    text = info["text"]
    lines = text.splitlines(keepends=True)
    # sections were parsed from the body, so their line numbers need the frontmatter back
    fm_offset = len(lines) - len(body_after_frontmatter(text).splitlines(keepends=True))
    if heading in info["sections"]:
        sec = info["sections"][heading]
        start = sec["lineno"] + fm_offset
        end = start + 1 + len(sec["lines"])
        return "".join(lines[:start]) + block + "".join(lines[end:]), "replaced"
    idx = _canonical_index(heading)
    following = [sec["lineno"] + fm_offset for h, sec in info["sections"].items()
                 if _canonical_index(h) > idx]
    if following:
        at = min(following)
        return "".join(lines[:at]) + block + "\n" + "".join(lines[at:]), "created"
    return text.rstrip() + "\n\n" + block, "created"


def cmd_section(args, root: str) -> int:
    """Deterministic partial read/write of ONE section — what makes lean agent context real.

    An executor is handed a task line and `## Handoff`, never the whole spec; this is the
    command that slices it without an LLM re-reading and rewriting the file."""
    info, err = load_spec(root, args.spec)
    if err:
        return emit_err(args.json, err)
    heading = _match_heading(args.heading)
    if not heading:
        emit(args.json,
             {"ok": False, "code": "sp-stray-heading", "heading": args.heading,
              "canonical": canonical_headings(),
              "message": f"'{args.heading}' is not one of the thirteen canonical headings"},
             f"error: '{args.heading}' is not a canonical heading")
        return 2
    if not args.write:
        st = section_state(info["sections"], heading)
        body = info["sections"].get(heading, {}).get("body", "")
        if args.json:
            print(json.dumps({"ok": st != "absent", "slug": info["slug"],
                              "heading": heading, "state": st, "body": body},
                             indent=2, ensure_ascii=False))
        else:
            print(body.strip() if st != "absent" else f"(## {heading} is absent)")
        return 0 if st != "absent" else 1

    content = sys.stdin.read() if not sys.stdin.isatty() else ""
    block = (f"## {heading}\n\n{content.strip()}\n"
             if content.strip() else section_guidance(heading))
    new_text, action = upsert_section(info, heading, block)
    write_text(info["path"], new_text)
    emit(args.json,
         {"ok": True, "slug": info["slug"], "heading": heading, "action": action,
          "path": os.path.relpath(info["path"], os.path.dirname(root)).replace(os.sep, "/")},
         f"{action} ## {heading} in {info['phase']}/{info['file']}")
    return 0


def set_frontmatter_key(text: str, key: str, value: str) -> str:
    """Set one top-level frontmatter key, preserving every other line as authored.

    Rewriting the block wholesale would reformat a human's `refined: {mode, date}` and
    reorder their keys — a promote is a move, and the outcome stamp is the ONLY content it
    is allowed to write."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return f"---\n{key}: {value}\n---\n\n" + text
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return text
    for i in range(1, close):
        if lines[i].split(":", 1)[0].strip() == key:
            lines[i] = f"{key}: {value}\n"
            return "".join(lines)
    lines.insert(close, f"{key}: {value}\n")
    return "".join(lines)


def cmd_promote(args, root: str) -> int:
    """The gated transition — and the human OK made auditable.

    Promote to `ready/` IS the authorization to build: one plan, one OK becomes one file
    move in `git log`. It refuses (exit 2) with the missing list rather than warning,
    because a gate that warns is not a gate.

    The file is MOVED, never renamed: the date prefix was stamped at capture and the
    basename is the spec's identity for its whole lifecycle. Git detects the rename by
    content, so `git log --follow` reads as one history without this tool shelling out."""
    info, err = load_spec(root, args.spec)
    if err:
        return emit_err(args.json, err)
    dest = args.to or _next_phase(info["phase"])
    if not dest:
        emit(args.json,
             {"ok": False, "code": "sp-terminal-phase", "slug": info["slug"],
              "phase": info["phase"],
              "message": f"'{info['slug']}' is already in {info['phase']}/ — nowhere to promote"},
             f"refused: '{info['slug']}' is already in {info['phase']}/")
        return 2
    if dest not in PHASES:
        emit(args.json, {"ok": False, "code": "sp-unknown-phase", "phase": dest,
                         "message": f"'{dest}' is not a phase folder"},
             f"error: '{dest}' is not a phase folder")
        return 2

    gates = gate_report(info, dest)
    if not gates["ok"]:
        obj = {"ok": False, "code": "sp-gate-unmet", "slug": info["slug"],
               "from": info["phase"], "to": dest,
               "missing": gates["missing"], "malformed": gates["malformed"],
               "message": f"cannot promote '{info['slug']}' to {dest}/ — "
                          f"{len(gates['missing'])} missing, {len(gates['malformed'])} empty"}
        human = [f"refused: cannot promote '{info['slug']}' to {dest}/"]
        if gates["missing"]:
            human += [f"  missing:   ## {h}" for h in gates["missing"]]
        if gates["malformed"]:
            human += [f"  empty:     ## {h}  (write `- none — <reason>` or fill it)"
                      for h in gates["malformed"]]
        emit(args.json, obj, "\n".join(human))
        return 2

    outcome = None
    if dest == "archive":
        outcome = args.outcome or "done"
        if outcome not in OUTCOMES:
            emit(args.json, {"ok": False, "code": "sp-bad-outcome", "outcome": outcome,
                             "message": f"--outcome must be one of {', '.join(OUTCOMES)}"},
                 f"error: --outcome must be one of {', '.join(OUTCOMES)}")
            return 2
        # An abandoned spec is EXPECTED to have open tasks — refusing there would make
        # every abandonment a forced promote. Only `done` has to be true.
        open_tasks = [t for t in info["tasks"] if not t["checked"]]
        if outcome == "done" and open_tasks and not args.force:
            emit(args.json,
                 {"ok": False, "code": "sp-open-tasks", "slug": info["slug"],
                  "open": len(open_tasks), "total": len(info["tasks"]),
                  "openTasks": [{"id": t["id"], "text": t["text"], "state": t["state"]}
                                for t in open_tasks],
                  "message": f"{len(open_tasks)} of {len(info['tasks'])} tasks still open — "
                             f"pass --force, or --outcome abandoned"},
                 f"refused: {len(open_tasks)} of {len(info['tasks'])} tasks still open in "
                 f"'{info['slug']}'\n" +
                 "\n".join(f"  [{t['state']}] {t['text'][:70]}" for t in open_tasks[:8]) +
                 "\n  pass --force to archive anyway, or --outcome abandoned")
            return 2

    dest_dir = os.path.join(root, dest)
    dest_path = os.path.join(dest_dir, info["file"])
    rel = f"{dest}/{info['file']}"
    if args.dry_run:
        emit(args.json,
             {"ok": True, "dryRun": True, "slug": info["slug"], "from": info["phase"],
              "to": dest, "outcome": outcome, "dest": rel,
              "warn": gates["warn"]},
             f"dry-run: would move {info['phase']}/{info['file']} → {rel}" +
             (f"  (outcome: {outcome})" if outcome else ""))
        return 0
    if os.path.exists(dest_path):
        emit(args.json, {"ok": False, "code": "sp-dest-exists", "dest": rel,
                         "message": f"{rel} already exists"},
             f"error: {rel} already exists")
        return 1
    os.makedirs(dest_dir, exist_ok=True)
    if outcome:
        write_text(info["path"], set_frontmatter_key(info["text"], "outcome", outcome))
    os.rename(info["path"], dest_path)
    emit(args.json,
         {"ok": True, "slug": info["slug"], "from": info["phase"], "to": dest,
          "outcome": outcome, "dest": rel, "warn": gates["warn"]},
         f"promoted '{info['slug']}': {info['phase']}/ → {rel}" +
         (f"  (outcome: {outcome})" if outcome else "") +
         ("".join(f"\n  warning: ## {h} is empty" for h in gates["warn"])))
    return 0


def _find_task(tasks: list[dict], ident: str) -> dict | None:
    for t in tasks:
        if t["id"] == ident or str(t["index"]) == ident:
            return t
    return None


def cmd_task(args, root: str) -> int:
    """Flip a checkbox MECHANICALLY — never by string surgery on the caller's side.

    `--block` writes the reason into the line itself. That visibility is the whole point:
    v1 kept an attempt counter in `.specs.json` that nobody read, and a task went quiet
    after five failures with no trace of why."""
    info, err = load_spec(root, args.spec)
    if err:
        return emit_err(args.json, err)
    ident = args.check or args.uncheck or args.block
    if not ident:
        emit(args.json, {"ok": False, "code": "sp-no-action",
                         "message": "pass --check, --uncheck or --block"},
             "error: pass --check, --uncheck or --block")
        return 1
    if args.block and not args.reason:
        emit(args.json, {"ok": False, "code": "sp-no-reason",
                         "message": "--block requires --reason"},
             "error: --block requires --reason (a blocked task without a reason is the "
             "hidden state this replaced)")
        return 1
    t = _find_task(info["tasks"], ident)
    if not t:
        emit(args.json, {"ok": False, "code": "sp-unknown-task", "task": ident,
                         "message": f"no task '{ident}' in {info['slug']}"},
             f"error: no task '{ident}' in {info['slug']}")
        return 1

    lines = info["text"].splitlines(keepends=True)
    line = lines[t["lineno"]]
    m = CHECKBOX_RE.match(line.rstrip("\n"))
    if not m:
        emit(args.json, {"ok": False, "code": "sp-line-drift", "task": ident,
                         "lineno": t["lineno"],
                         "message": "the parsed line is not a checkbox — the file changed"},
             "error: the parsed line is not a checkbox — re-read the spec")
        return 1
    mark = {"check": "x", "uncheck": " ", "block": "!"}[
        "check" if args.check else "uncheck" if args.uncheck else "block"]
    body = m.group(3).rstrip()
    body = BLOCKED_REASON_RE.sub("", body).rstrip()      # drop any stale blocked suffix
    if args.block:
        body = f"{body} — blocked: {args.reason.strip()}"
    lines[t["lineno"]] = f"{m.group(1)}- [{mark}] {body}\n"
    write_text(info["path"], "".join(lines))

    verb = "checked" if args.check else "unchecked" if args.uncheck else "blocked"
    emit(args.json,
         {"ok": True, "slug": info["slug"], "task": ident, "action": verb,
          "state": mark, "text": body,
          "reason": args.reason if args.block else None},
         f"task {ident} {verb}: {body}")
    return 0


def cmd_next(args, root: str) -> int:
    """THE single next action, so a skill never infers state from prose.

    In `backlog/` that is the next unfilled promote gate; in `ready/` the next open task.
    A `[!]` task is SKIPPED — it already has an honest reason recorded and re-offering it
    forever is what the attempt budget was clumsily trying to prevent."""
    info, err = load_spec(root, args.spec)
    if err:
        return emit_err(args.json, err)
    dest = _next_phase(info["phase"])
    base = {"slug": info["slug"], "phase": info["phase"], "stage": info["stage"],
            "verification": info["verification"],
            "blocked": [{"id": t["id"], "text": t["text"], "reason": t["reason"]}
                        for t in info["tasks"] if t["blocked"]]}

    if info["phase"] == "backlog":
        gates = gate_report(info, "ready")
        if not gates["ok"]:
            want = (gates["missing"] + gates["malformed"])[0]
            obj = {"ok": True, "action": "write_section", "heading": want, **base,
                   "missing": gates["missing"], "malformed": gates["malformed"],
                   "message": f"write ## {want} (then {len(gates['missing']) + len(gates['malformed']) - 1} more) "
                              f"before promoting to ready/"}
            emit(args.json, obj, obj["message"])
            return 0
        obj = {"ok": True, "action": "promote", "to": "ready", **base,
               "message": f"all gates met — `specs.py promote {info['slug']}`"}
        emit(args.json, obj, obj["message"])
        return 0

    if info["phase"] == "ready":
        openable = [t for t in info["tasks"] if not t["checked"] and not t["blocked"]]
        if openable:
            t = openable[0]
            obj = {"ok": True, "action": "implement_task", "task": t["id"], "text": t["text"],
                   "verify": t["verify"], "files": t["files"], "pattern": t["pattern"],
                   "parallel": t["parallel"], **base,
                   "message": f"implement task {t['id']}: {t['text']}"}
            emit(args.json, obj, obj["message"])
            return 0
        if base["blocked"]:
            obj = {"ok": True, "action": "blocked", **base,
                   "message": f"every remaining task is blocked ({len(base['blocked'])})"}
            emit(args.json, obj, obj["message"] + "".join(
                f"\n  [!] {b['text']}" for b in base["blocked"]))
            return 0
        obj = {"ok": True, "action": "promote", "to": "archive", **base,
               "message": f"all tasks complete — write ## Outcome, then "
                          f"`specs.py promote {info['slug']} --to archive`"}
        emit(args.json, obj, obj["message"])
        return 0

    obj = {"ok": True, "action": "done", **base,
           "message": f"'{info['slug']}' is archived ("
                      f"{info['frontmatter'].get('outcome', 'done')})"}
    emit(args.json, obj, obj["message"])
    return 0


def _norm_file(p: str) -> str:
    p = p.strip().replace("\\", "/")
    p = re.sub(r"\s*\(new\)\s*$", "", p)      # `src/a.py (new)` is still src/a.py
    return p.strip("./")


def _overlaps(a: str, b: str) -> bool:
    a, b = _norm_file(a), _norm_file(b)
    return a == b or a.startswith(b.rstrip("/") + "/") or b.startswith(a.rstrip("/") + "/")


def parallel_groups(tasks: list[dict]) -> list[list[dict]]:
    """Consecutive `[P]` tasks within one `### N.` section form a group."""
    groups, cur, sec = [], [], None
    for t in tasks:
        if t["parallel"] and (sec is None or t["section"] == sec):
            cur.append(t)
            sec = t["section"]
            continue
        if len(cur) > 1:
            groups.append(cur)
        cur, sec = ([t], t["section"]) if t["parallel"] else ([], None)
    if len(cur) > 1:
        groups.append(cur)
    return groups


def cmd_parallel(args, root: str) -> int:
    """Prove a `[P]` group's `files:` sets are disjoint — MECHANICALLY, never judged in
    prose. A group with an undeclared `files:` is ineligible: nothing can be proven about
    a task that never said what it touches."""
    info, err = load_spec(root, args.spec)
    if err:
        return emit_err(args.json, err)
    findings = []
    for gi, group in enumerate(parallel_groups(info["tasks"]), 1):
        undeclared = [t["id"] for t in group if not t["files"]]
        clashes = []
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                for fa in a["files"]:
                    for fb in b["files"]:
                        if _overlaps(fa, fb):
                            clashes.append({"a": a["id"], "b": b["id"],
                                            "file": _norm_file(fa)})
        eligible = not undeclared and not clashes
        findings.append({"group": gi, "tasks": [t["id"] for t in group],
                         "eligible": eligible, "undeclared": undeclared,
                         "clashes": clashes})
    ok = all(f["eligible"] for f in findings)
    if args.json:
        print(json.dumps({"ok": ok, "slug": info["slug"], "groups": findings},
                         indent=2, ensure_ascii=False))
    else:
        if not findings:
            print(f"{info['slug']}: no [P] groups — serial execution")
        for f in findings:
            print(f"group {f['group']}: {', '.join(x or '?' for x in f['tasks'])} — "
                  f"{'eligible' if f['eligible'] else 'NOT eligible'}")
            for c in f["clashes"]:
                print(f"    {c['a']} and {c['b']} both touch {c['file']}")
            if f["undeclared"]:
                print(f"    no files: declared by {', '.join(f['undeclared'])}")
    return 0 if ok else 1


def cmd_discover(args, root: str) -> int:
    """Append one line to `## Discoveries`, creating the section when absent.

    Captured INDISCRIMINATELY during execution — whether a discovery is worth acting on is
    triage's judgment, not the executor's, and the cost of asking mid-build is a human
    interrupted for something that may not matter."""
    info, err = load_spec(root, args.spec)
    if err:
        return emit_err(args.json, err)
    entry = f"- {args.text.strip()}"
    sec = info["sections"].get("Discoveries")
    if sec and sec["filled"]:
        block = f"## Discoveries\n{sec['body'].rstrip()}\n{entry}\n"
    else:
        block = f"## Discoveries\n\n{entry}\n"
    new_text, _ = upsert_section(info, "Discoveries", block)
    write_text(info["path"], new_text)
    emit(args.json,
         {"ok": True, "slug": info["slug"], "entry": args.text.strip()},
         f"recorded in ## Discoveries: {args.text.strip()}")
    return 0


# --------------------------------------------------------------------------- #
# migrate (one-way, v1 -> v2)
# --------------------------------------------------------------------------- #
# Where each v1 artifact's sections land. `## Context` and `## Decisions` merge into the
# single `## Design`; everything else is a rename. The v1 heading is matched
# case-insensitively and its body is carried VERBATIM — a migration must not rewrite prose
# it does not understand.
V1_MAP = {
    "proposal.md": [("Why", "Problem"), ("What Changes", "Proposal"),
                    ("Out of Scope", "Out of Scope"), ("Validation", "Validation"),
                    ("Impact", "Impact")],
    "design.md": [("Context", "Design"), ("Decisions", "Design"),
                  ("Alternatives Considered", "Alternatives Considered"),
                  ("Open Decisions", "Open Decisions"), ("Risks", "Risks")],
}
MIGRATE_NONE = "- none — not recorded in the v1 plan"


def _git_first_commit_date(path: str) -> str | None:
    """The path's first commit date — used only when `.specs.json` has no `created`.

    A birth date is never INVENTED: this walks git history for the real one, and the caller
    falls back to the file's mtime rather than to today."""
    import subprocess
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%ad",
             "--date=short", "--", path],
            capture_output=True, text=True, timeout=10,
            cwd=os.path.dirname(os.path.abspath(path)) or ".")
        lines = [l.strip() for l in out.stdout.splitlines() if l.strip()]
        return lines[-1] if lines else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _birth_date(meta: dict, path: str) -> str:
    created = str(meta.get("created", "") or "")
    if re.match(r"^\d{4}-\d{2}-\d{2}", created):
        return created[:10]
    git = _git_first_commit_date(path)
    if git:
        return git
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()
    except OSError:
        return today()


def _v1_sections(plan_dir: str) -> dict[str, list[str]]:
    """Collect v1 bodies keyed by their V2 heading, in canonical order."""
    collected: dict[str, list[str]] = {}
    for fname, pairs in V1_MAP.items():
        text = read_text(os.path.join(plan_dir, fname))
        if text is None:
            continue
        secs = parse_sections(body_after_frontmatter(text))
        lower = {k.lower(): v for k, v in secs.items()}
        for v1h, v2h in pairs:
            sec = lower.get(v1h.lower())
            if sec and sec["filled"]:
                body = sec["body"].strip()
                # `## Context` and `## Decisions` both land in `## Design`
                collected.setdefault(v2h, []).append(
                    f"### {v1h}\n\n{body}" if v2h == "Design" else body)
    tasks_text = read_text(os.path.join(plan_dir, "tasks.md"))
    if tasks_text is not None:
        body = body_after_frontmatter(tasks_text)
        body = re.sub(r"(?m)^#\s+.*$", "", body, count=1)     # drop the `# Tasks — X` title
        # v1 grouped tasks under `## N.`; v2 nests them under the `## Tasks` section
        body = re.sub(r"(?m)^## ", "### ", body)
        if has_real_content(body):
            collected["Tasks"] = [body.strip()]
    return collected


def _migrate_plan(root: str, name: str, dry: bool) -> dict:
    plan_dir = os.path.join(root, name)
    meta_txt = read_text(os.path.join(plan_dir, ".specs.json")) or "{}"
    try:
        meta = json.loads(meta_txt)
    except json.JSONDecodeError:
        meta = {}
    slug = slugify(name)
    date = _birth_date(meta, os.path.join(plan_dir, ".specs.json"))
    collected = _v1_sections(plan_dir)
    dest_phase = "ready" if collected.get("Tasks") else "backlog"
    gate = phase_spec(dest_phase).get("entryGate", [])

    fm = [f"slug: {slug}", f"title: {meta.get('title') or titleize(slug)}",
          f"verification: {_policy(meta)}"]
    if isinstance(meta.get("refined"), dict) and meta["refined"].get("mode"):
        r = meta["refined"]
        fm.append(f"refined: {{mode: {r.get('mode')}, date: {r.get('date', date)}}}")

    parts = ["---", *fm, "---", "", f"# {meta.get('title') or titleize(slug)}", ""]
    for h in canonical_headings():
        if h in collected:
            parts += [f"## {h}", "", "\n\n".join(collected[h]), ""]
        elif h in gate:
            # the destination's gate must be satisfiable, and an explicit none that SAYS
            # the v1 plan never recorded it is a fact — not an invented answer
            parts += [f"## {h}", "", MIGRATE_NONE, ""]
    body = "\n".join(parts).rstrip() + "\n"

    strays = sorted(f for f in os.listdir(plan_dir)
                    if f not in (".specs.json", "proposal.md", "design.md", "tasks.md")
                    and os.path.isfile(os.path.join(plan_dir, f)))
    dest = os.path.join(root, dest_phase, f"{date}-{slug}.md")
    rec = {"from": f"{name}/", "slug": slug, "to": f"{dest_phase}/{date}-{slug}.md",
           "date": date, "dateSource": "created" if meta.get("created") else "git/mtime",
           "sections": sorted(collected), "strays": strays}
    if dry:
        return rec
    os.makedirs(os.path.join(root, dest_phase), exist_ok=True)
    write_text(dest, body)
    for f in (".specs.json", "proposal.md", "design.md", "tasks.md"):
        p = os.path.join(plan_dir, f)
        if os.path.isfile(p):
            os.remove(p)
    if not strays:
        try:
            os.rmdir(plan_dir)
        except OSError:
            rec["kept"] = True
    else:
        rec["kept"] = True          # never delete a folder still holding a human's file
    return rec


def _migrate_task(root: str, path: str, dry: bool) -> dict:
    text = read_text(path) or ""
    fm = parse_frontmatter(text)
    slug = slugify(os.path.splitext(os.path.basename(path))[0])
    stamp = str(fm.get("timestamp", ""))
    date = stamp[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", stamp) else _birth_date({}, path)
    body = strip_comments(body_after_frontmatter(text)).strip()
    body = re.sub(r"(?m)^#\s+.*$", "", body, count=1).strip()
    problem = fm.get("description") or body or titleize(slug)
    extra = [f"{k}: {fm[k]}" for k in ("priority", "tags", "complexity") if fm.get(k)]
    if extra:
        problem += f"\n\n_(v1 backlog task — {' · '.join(extra)})_"
    if body and fm.get("description") and body not in problem:
        problem += f"\n\n{body}"
    out = ["---", f"slug: {slug}", f"title: {fm.get('title') or titleize(slug)}",
           f"verification: {DEFAULT_VERIFICATION}", "---", "",
           f"# {fm.get('title') or titleize(slug)}", "", "## Problem", "", problem, ""]
    dest = os.path.join(root, "backlog", f"{date}-{slug}.md")
    rec = {"from": f"backlog/{os.path.basename(path)}", "slug": slug,
           "to": f"backlog/{date}-{slug}.md", "date": date, "kind": "task"}
    if dry:
        return rec
    write_text(dest, "\n".join(out).rstrip() + "\n")
    os.remove(path)
    return rec


def cmd_migrate(args, root: str) -> int:
    """One-way v1 -> v2. `specs/archive/**` is NEVER touched — it is historical and
    read-only, and churning it would break every link into it for no gain.

    Refuses (exit 2) when there is nothing v1 left, so a second run cannot quietly
    re-migrate an already-converted workspace."""
    plans = _v1_leftovers(root)
    tasks = []
    bdir = os.path.join(root, "backlog")
    if os.path.isdir(bdir):
        for name in sorted(os.listdir(bdir)):
            p = os.path.join(bdir, name)
            if name == "index.md" or not os.path.isfile(p) or SPEC_FILE_RE.match(name):
                continue
            if str(parse_frontmatter(read_text(p) or "").get("type", "")) == "task":
                tasks.append(p)
    if not plans and not tasks:
        emit(args.json, {"ok": False, "code": "sp-nothing-to-migrate", "root": root,
                         "message": "no v1 plan folders and no v1 backlog tasks — "
                                    "this workspace is already v2"},
             "refused: nothing to migrate — this workspace is already v2")
        return 2

    migrated = [_migrate_plan(root, n, args.dry_run) for n in plans]
    migrated += [_migrate_task(root, p, args.dry_run) for p in tasks]
    obj = {"ok": True, "dryRun": bool(args.dry_run), "root": root,
           "migrated": migrated,
           "archiveUntouched": True,
           "kept": [m["from"] for m in migrated if m.get("kept")]}
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        verb = "would migrate" if args.dry_run else "migrated"
        print(f"{verb} {len(migrated)} item(s) — specs/archive/** untouched")
        for m in migrated:
            print(f"  {m['from']:<40} → {m['to']}   (date from {m.get('dateSource', 'timestamp')})")
            if m.get("strays"):
                print(f"      kept, still holds: {', '.join(m['strays'])}")
    return 0


# --------------------------------------------------------------------------- #
# validate / doctor / backlog reindex
# --------------------------------------------------------------------------- #
def _finding(code: str, severity: str, message: str, **extra) -> dict:
    return {"code": code, "severity": severity, "message": message, **extra}


def validate_spec(root: str, s: dict) -> list[dict]:
    """Every finding for ONE spec file, in the v2 `sp-*` vocabulary.

    The phase-scoped rule is asserted against the schema's per-phase sets — the SAME sets
    `promote` gates on, so the two can never drift into disagreeing about what a phase
    requires."""
    where = f"{s['phase']}/{s['file']}"
    text = read_text(s["path"]) or ""
    fm = parse_frontmatter(text)
    sections = parse_sections(body_after_frontmatter(text))
    tasks = parse_tasks(text)
    out: list[dict] = []

    schema = load_schema()
    for key in schema.get("frontmatter", {}).get("required", []):
        if not str(fm.get(key, "")).strip():
            out.append(_finding("sp-missing-frontmatter", "error",
                                f"{where}: frontmatter has no `{key}`", spec=s["slug"],
                                path=where, remedy=f"add `{key}:` to the frontmatter"))
    if fm.get("slug") and fm["slug"] != s["slug"]:
        out.append(_finding("sp-slug-mismatch", "error",
                            f"{where}: frontmatter slug `{fm['slug']}` disagrees with the "
                            f"filename suffix `{s['slug']}`", spec=s["slug"], path=where,
                            remedy="make the frontmatter slug match the filename"))
    pol = str(fm.get("verification", "")).strip().lower()
    if pol and pol not in VERIFICATION_POLICIES:
        out.append(_finding("sp-bad-verification", "error",
                            f"{where}: verification `{pol}` is not one of "
                            f"{', '.join(VERIFICATION_POLICIES)}", spec=s["slug"], path=where,
                            remedy=f"set verification to one of {', '.join(VERIFICATION_POLICIES)}"))

    for h in stray_headings(sections, schema):
        out.append(_finding("sp-stray-heading", "warn",
                            f"{where}: `## {h}` is not one of the thirteen canonical headings",
                            spec=s["slug"], path=where, heading=h,
                            remedy="rename it to a canonical heading or fold it into one"))

    # The phase-scoped rule governs whether a heading must be PRESENT — so `missing` is
    # checked only against the gate of the phase this spec is IN.
    gates = gate_report({"sections": sections}, s["phase"], schema)
    for h in gates["missing"]:
        out.append(_finding("sp-gate-unmet", "warn",
                            f"{where}: `## {h}` is required in {s['phase']}/ and is absent",
                            spec=s["slug"], path=where, heading=h,
                            remedy=f"specs.py section {s['slug']} \"{h}\" --write"))
    # Malformed is NOT phase-scoped. Once a heading exists it must say something, in any
    # phase: it is neither an answer nor a not-yet, and leaving it for the promote to catch
    # means a spec looks fine right up until the gate refuses it.
    for h in canonical_headings(schema):
        if section_state(sections, h) == "empty":
            out.append(_finding("sp-empty-section", "error",
                                f"{where}: `## {h}` is present but empty — neither an answer "
                                f"nor a not-yet", spec=s["slug"], path=where, heading=h,
                                remedy="fill it, or write `- none — <reason>`"))
    for h in gates["warn"]:
        out.append(_finding("sp-handoff-empty", "warn",
                            f"{where}: `## {h}` is empty in {s['phase']}/ — an executor "
                            f"gets no context", spec=s["slug"], path=where, heading=h,
                            remedy="rewrite it after each committed task and at every promote"))

    declared = parse_impact_standards(text, schema)
    if declared:
        named = "\n".join(t["text"] for t in tasks)
        for p in declared:
            if p not in named:
                out.append(_finding("sp-impact-uncovered", "warn",
                                    f"{where}: `{p}` is declared under ## Impact but no task "
                                    f"names it", spec=s["slug"], path=where, standard=p,
                                    remedy="add a task that writes it, or drop the declaration"))

    # Judged against the READY gate, not backlog's: a spec is "unrefined" once it could be
    # promoted, not the moment it is captured. Warning on every fresh capture would train
    # the reader to ignore the code.
    if s["phase"] == "backlog" and not fm.get("refined") \
            and gate_report({"sections": sections}, "ready", schema)["ok"]:
        out.append(_finding("sp-unrefined", "warn",
                            f"{where}: ready to promote, but nobody has interrogated it",
                            spec=s["slug"], path=where,
                            remedy="run a refinement pass, or promote as-is (never gated)"))
    if s["phase"] == "archive" and not fm.get("outcome"):
        out.append(_finding("sp-no-outcome", "warn",
                            f"{where}: archived with no `outcome:` — done and abandoned "
                            f"read alike", spec=s["slug"], path=where,
                            remedy="stamp `outcome: done` or `outcome: abandoned`"))
    return out


def cmd_validate(args, root: str) -> int:
    specs = spec_files(root)
    findings: list[dict] = []

    seen: dict[str, list[str]] = {}
    for s in specs:
        seen.setdefault(s["slug"], []).append(f"{s['phase']}/{s['file']}")
    for slug, paths in seen.items():
        if len(paths) > 1:
            findings.append(_finding("sp-duplicate-slug", "error",
                                     f"slug `{slug}` resolves to {len(paths)} files: "
                                     f"{', '.join(paths)}", spec=slug,
                                     remedy="rename one — a slug is an identity, and two "
                                            "matches makes every command refuse"))

    for ph in PHASES:
        d = os.path.join(root, ph)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name == "index.md" or name.startswith("."):
                continue
            if os.path.isdir(os.path.join(d, name)):
                # archive/ is DELIBERATELY not migrated — it is historical and read-only, so
                # its v1 `YYYY-MM-DD-<name>/` plan folders are expected, not strays. Flagging
                # them would push a reader to migrate the one tree the design protects.
                if ph == "archive":
                    continue
                findings.append(_finding("sp-stray-dir", "warn",
                                         f"{ph}/{name}/ is a directory — v2 specs are files",
                                         path=f"{ph}/{name}",
                                         remedy="a v1 plan folder? run `specs.py migrate`"))
            elif not SPEC_FILE_RE.match(name):
                findings.append(_finding("sp-bad-filename", "error",
                                         f"{ph}/{name} is not `YYYY-MM-DD-<slug>.md`",
                                         path=f"{ph}/{name}",
                                         remedy="rename it to the one filename pattern all "
                                                "three folders share"))

    target = [s for s in specs if s["slug"] == args.spec] if args.spec else specs
    if args.spec and not target:
        emit(args.json, {"ok": False, "code": "sp-unknown-slug", "slug": args.spec,
                         "message": f"no spec with slug '{args.spec}'"},
             f"error: no spec with slug '{args.spec}'")
        return 1
    for s in target:
        findings.extend(validate_spec(root, s))

    errors = [f for f in findings if f["severity"] == "error"]
    if args.json:
        print(json.dumps({"ok": not errors, "root": root, "specs": len(specs),
                          "findings": findings}, indent=2, ensure_ascii=False))
    else:
        print(f"specs validate — {root} ({len(errors)} error(s), "
              f"{len(findings) - len(errors)} warning(s))")
        for f in findings:
            print(f"  [{f['severity']:<5}] {f['message']}  ({f['code']})")
            if f.get("remedy"):
                print(f"          remedy: {f['remedy']}")
        if not findings:
            print("  OK — every spec conforms.")
    return 1 if findings else 0


def _v1_leftovers(root: str) -> list[str]:
    """A v1 plan folder is a directory at the specs root holding proposal/tasks/.specs.json.

    Detecting it matters more than it looks: v2 `list` globs the three phase folders, so an
    unmigrated v1 workspace reads as EMPTY rather than as wrong-format, and a skill would
    conclude there is no work when there is."""
    out = []
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isdir(d) or name in PHASES or name.startswith("."):
            continue
        if any(os.path.isfile(os.path.join(d, f))
               for f in (".specs.json", "proposal.md", "tasks.md")):
            out.append(name)
    return out


def cmd_doctor(args, root: str) -> int:
    findings: list[dict] = []
    if not os.path.isdir(root):
        findings.append(_finding("sp-no-workspace", "error", f"no specs/ workspace at {root}",
                                 remedy="scaffold specs/ (copy the plugin's assets/specs skeleton)"))
        return _emit_doctor(args, root, findings)

    for ph in PHASES:
        if not os.path.isdir(os.path.join(root, ph)):
            findings.append(_finding("sp-missing-phase", "warn", f"no {ph}/ folder",
                                     path=ph, remedy=f"mkdir {ph}/ (the folder IS the phase)"))
    if not os.path.isfile(os.path.join(root, "backlog", "index.md")):
        findings.append(_finding("sp-no-backlog-index", "warn", "no backlog/index.md",
                                 remedy="install assets/specs/backlog/index.md"))

    leftovers = _v1_leftovers(root)
    for name in leftovers:
        findings.append(_finding("sp-v1-leftover", "error",
                                 f"`{name}/` is a v1 three-file plan folder",
                                 path=name,
                                 remedy=f"specs.py migrate  (folds {name}/ into one v2 file; "
                                        f"specs/archive/** is never touched)"))
    for entry in sorted(os.listdir(root)):
        full = os.path.join(root, entry)
        if os.path.isfile(full) and entry not in ("QUENCHING.md", "schema.json") \
                and not entry.startswith("."):
            findings.append(_finding("sp-stray-file", "warn",
                                     f"stray file at the specs root: {entry}", path=entry,
                                     remedy="move it into a phase folder or remove it"))
    return _emit_doctor(args, root, findings)


def _emit_doctor(args, root: str, findings: list[dict]) -> int:
    errors = [f for f in findings if f["severity"] == "error"]
    if args.json:
        print(json.dumps({"ok": not errors, "root": root, "findings": findings},
                         indent=2, ensure_ascii=False))
    else:
        print(f"specs doctor — {root} ({len(errors)} error(s), "
              f"{len(findings) - len(errors)} warning(s))")
        for f in findings:
            print(f"  [{f['severity']:<5}] {f['message']}  ({f['code']})")
            print(f"          remedy: {f['remedy']}")
        if not findings:
            print("  OK — workspace conforms.")
    return 1 if errors else 0


STAGE_ORDER = ("refined", "designed", "proposed", "captured", "backlog")


def render_backlog_zone(rows: list[dict]) -> str:
    """The GENERATED zone of `backlog/index.md`, grouped by DERIVED stage.

    This tool owns the format — the zone is rebuilt from disk, never hand-edited, so a
    listing can never drift from what the folder actually holds."""
    if not rows:
        return BACKLOG_EMPTY
    counts = {st: sum(1 for r in rows if r["stage"] == st) for st in STAGE_ORDER}
    head = f"**{len(rows)} spec{'s' if len(rows) != 1 else ''}**"
    parts = [f"{counts[st]} {st}" for st in STAGE_ORDER if counts[st]]
    lines = [head + (" · " + " · ".join(parts) if parts else ""), ""]
    for st in STAGE_ORDER:
        group = sorted((r for r in rows if r["stage"] == st), key=lambda r: r["file"])
        if not group:
            continue
        lines += [f"### {st.capitalize()}", "",
                  "| Spec | Title | Since |", "| --- | --- | --- |"]
        for r in group:
            lines.append(f"| [{r['slug']}]({r['file']}) | {r['title']} | {r['date']} |")
        lines.append("")
    return "\n".join(lines).rstrip()


def cmd_backlog(args, root: str) -> int:
    index = os.path.join(root, "backlog", "index.md")
    text = read_text(index)
    if text is None:
        emit(args.json, {"ok": False, "code": "sp-no-backlog-index",
                         "message": "no backlog/index.md to reindex"},
             "error: no backlog/index.md to reindex")
        return 1
    rows = []
    for s in spec_files(root, "backlog"):
        raw = read_text(s["path"]) or ""
        fm = parse_frontmatter(raw)
        rows.append({
            "slug": s["slug"], "file": s["file"], "date": s["date"],
            "title": fm.get("title", titleize(s["slug"])),
            "stage": derive_stage(s, parse_sections(body_after_frontmatter(raw)), fm,
                                  parse_tasks(raw)),
        })
    begin = text.find(GEN_BEGIN)
    end = text.find(GEN_END)
    if begin < 0 or end < 0 or end < begin:
        emit(args.json, {"ok": False, "code": "sp-no-generated-zone",
                         "message": "backlog/index.md has no BEGIN/END GENERATED zone"},
             "error: backlog/index.md has no BEGIN/END GENERATED zone")
        return 1
    head_end = text.find("-->", begin)
    if head_end < 0:
        emit(args.json, {"ok": False, "code": "sp-no-generated-zone",
                         "message": "the BEGIN GENERATED comment is unterminated"},
             "error: the BEGIN GENERATED comment is unterminated")
        return 1
    new_text = (text[:head_end + 3] + "\n" + render_backlog_zone(rows) + "\n" + text[end:])
    write_text(index, new_text)
    emit(args.json, {"ok": True, "specs": len(rows),
                     "stages": {st: sum(1 for r in rows if r["stage"] == st)
                                for st in STAGE_ORDER
                                if any(r["stage"] == st for r in rows)}},
         f"reindexed backlog/index.md — {len(rows)} spec(s)")
    return 0


# --------------------------------------------------------------------------- #
# dispatch
# --------------------------------------------------------------------------- #
def build_parser() -> tuple[argparse.ArgumentParser, argparse._SubParsersAction]:
    p = argparse.ArgumentParser(prog="specs.py",
                                description="deterministic trail for the specs/ front")
    p.add_argument("--root", help="the specs/ workspace directory (default: nearest specs/ upward)")
    p.add_argument("--version", action="store_true", help="print the version and exit")
    sub = p.add_subparsers(dest="cmd")

    def add_json(sp):
        sp.add_argument("--json", action="store_true", help="machine-readable output")
        return sp

    sp = add_json(sub.add_parser("new", help="capture a spec into backlog/"))
    sp.add_argument("name")
    sp.add_argument("--title")
    sp.add_argument("--verification", choices=list(VERIFICATION_POLICIES),
                    help=f"when the suite runs (default: {DEFAULT_VERIFICATION})")

    add_json(sub.add_parser("list", help="every spec, by folder and derived stage"))

    sp = add_json(sub.add_parser("status", help="one spec's sections, stage, tasks, gates"))
    sp.add_argument("--spec", required=True)

    sp = add_json(sub.add_parser("section", help="read or write ONE section"))
    sp.add_argument("spec")
    sp.add_argument("heading")
    sp.add_argument("--write", action="store_true",
                    help="replace the section from stdin, creating it in canonical position")

    sp = add_json(sub.add_parser("promote", help="the gated phase transition"))
    sp.add_argument("spec")
    sp.add_argument("--to", choices=list(PHASES), help="force the destination phase")
    sp.add_argument("--outcome", choices=list(OUTCOMES),
                    help="archive hop only (default: done)")
    sp.add_argument("--force", action="store_true",
                    help="archive as done despite open tasks")
    sp.add_argument("--dry-run", action="store_true", dest="dry_run")

    sp = add_json(sub.add_parser("task", help="flip or block a checkbox"))
    sp.add_argument("--spec", required=True)
    sp.add_argument("--check")
    sp.add_argument("--uncheck")
    sp.add_argument("--block", help="mark TASK blocked (requires --reason)")
    sp.add_argument("--reason", help="why the task is blocked — written into the line")

    sp = add_json(sub.add_parser("next", help="THE single next action"))
    sp.add_argument("--spec", required=True)

    sp = add_json(sub.add_parser("parallel", help="prove a [P] group's files: are disjoint"))
    sp.add_argument("--spec", required=True)

    sp = add_json(sub.add_parser("discover", help="append a line to ## Discoveries"))
    sp.add_argument("spec")
    sp.add_argument("text")

    sp = add_json(sub.add_parser("validate", help="the canonical set, the gates, the sp-* codes"))
    sp.add_argument("--spec", help="one slug (default: every spec)")

    add_json(sub.add_parser("doctor", help="workspace shape; remedies declared"))

    sp = add_json(sub.add_parser("backlog", help="backlog/index.md maintenance"))
    sp.add_argument("backlog_cmd", choices=["reindex"])

    sp = add_json(sub.add_parser("migrate", help="one-way v1 → v2 fold"))
    sp.add_argument("--dry-run", action="store_true", dest="dry_run")

    return p, sub


DISPATCH: dict = {
    "new": cmd_new,
    "list": cmd_list,
    "status": cmd_status,
    "section": cmd_section,
    "promote": cmd_promote,
    "task": cmd_task,
    "next": cmd_next,
    "parallel": cmd_parallel,
    "discover": cmd_discover,
    "validate": cmd_validate,
    "doctor": cmd_doctor,
    "backlog": cmd_backlog,
    "migrate": cmd_migrate,
}


def _force_utf8_output() -> None:
    """Spec files are prose — em-dashes, arrows, accented words — and a Windows console
    defaults to cp1252, where printing one raises UnicodeEncodeError AFTER the write
    already landed. That turns a successful `task --check` into a traceback and a nonzero
    exit, which the exit-code contract (0 ok / 1 findings / 2 refusal) reads as a finding.
    Encode output as UTF-8 and never let a glyph decide the exit code."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main(argv: list[str]) -> int:
    _force_utf8_output()
    if "--version" in argv:
        print(f"specs {VERSION}")
        return 0
    parser, _ = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 1
    if not hasattr(args, "json"):
        args.json = False
    root = find_specs_root(args.root)
    return DISPATCH[args.cmd](args, root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
