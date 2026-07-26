#!/usr/bin/env python3
"""specs.py — self-contained deterministic trail for the `specs/` front.

Payload of the `claude-quenching` plugin, sibling of `assets/hooks/okf-validate.py`
and built in the same mold: stdlib-only, ZERO dependencies (its own minimal
frontmatter parser — no PyYAML), one script installed alone into a target repo.

It replaces the external `@fission-ai/openspec` CLI the `specs/` skills used to
depend on. Where the OpenSpec CLI needed a Node runtime, a `config.yaml`, a main
spec store, and a delta format, this front is entirely native: a **plan** writes
straight into the OKF `docs/` bundle, isolated on a branch, and this tool gives the
LLM deterministic rails so it branches on DATA (an exit code, a `--json` field),
never on prose it has to infer.

THE WORKSPACE
-------------
The front lives under `specs/` at the target repo root (never inside `docs/`):

    specs/
      <plan-name>/          # an active plan, one folder per plan
        .specs.json         # metadata: name, created, seed task, verification policy,
                            #   refinement record, per-task attempt state
        proposal.md         # what & why (+ Out of Scope, Validation, the parsed Impact)
        design.md           # how — ALWAYS present; empty sections read `- none — <reason>`
        tasks.md            # implementation checklist (- [ ] / - [x], + files:/verify:)
      archive/              # completed/abandoned plans, YYYY-MM-DD-<name>/
      backlog/              # the task inbox (type: task), one file per task
        index.md            # a listing with a GENERATED zone (see `backlog reindex`)
        <task-slug>.md

The artifact graph is THREE artifacts, not four — the OpenSpec `specs` (delta) node
is gone: `proposal` -> `design` -> `tasks`, with `applyRequires: [tasks]`.

`design` is required as a SECTION SET but deliberately NOT as a dependency: the file
always exists, yet `applyRequires` stays `[tasks]`, so a bare scaffold is reported
(`sp-design-scaffold`, warn) and never blocks. Adding it to `applyRequires` would move
every plan authored before that rule from apply-ready to blocked on upgrade.

OUTPUT CONTRACT (uniform across every subcommand)
-------------------------------------------------
`--json` on every subcommand, and STRICT exit codes so the skill ramifies on data:
  0  ok
  1  findings (validate/doctor found something; a plan/task was not found)
  2  refusal  (archive with open tasks and no --force)

SUBCOMMANDS
  new <name> [--title T] [--backlog-task SLUG] [--verification P]
                                                  scaffold a plan folder + filled templates + .specs.json
  list                                            active plans, task progress, lastModified
  status --plan N                                 the artifact graph (done/ready/blocked) + policy, refinement, blocked tasks
  next --plan N                                   THE single next action (write X / implement task Y / blocked / archive)
  task --plan N --check ID | --uncheck ID         flip a checkbox in tasks.md mechanically
  task --plan N --attempt ID [--error MSG]        record a failed attempt against the budget
  task --plan N --reset-attempts ID               clear a task's attempt state
  parallel --plan N                               verify each [P] group's files: sets are disjoint
  backlog reindex                                 regenerate the GENERATED zone of backlog/index.md from frontmatter
  validate [--plan N]                             structure (artifacts, checkboxes, kebab names) + the
                                                  non-gating warnings sp-unrefined / sp-design-scaffold /
                                                  sp-impact-uncovered
  archive N [--dry-run] [--force]                 move to specs/archive/YYYY-MM-DD-N/ (exit 2 on open tasks)
  doctor                                          workspace shape; remedies DECLARED for the skill to apply

There is no `init` (scaffold is an asset copy — the skill's job), no `store`, no
`profiles`, no telemetry, and no delta parser.

WORKSPACE RESOLUTION
  --root PATH, else $SPECS_ROOT, else the nearest `specs/` directory walking up from
  cwd (or cwd itself if it is named `specs`). `new` creates `./specs` when none exists.

ASSETS
  Schema and templates load from `<script>/../specs/` when present (so editing the
  shipped `assets/specs/schema.json` / `assets/specs/templates/*.md` changes behavior
  in the plugin), and fall back to the constants embedded below — so an installed copy
  under `.claude/hooks/` with no adjacent assets still works.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import sys

VERSION = "1.2.0"  # kept in lockstep with the plugin VERSION file, plugin.json, and okf-validate.py

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.normpath(os.path.join(HERE, "..", "specs"))
RESERVED_DIRS = ("archive", "backlog")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CHECKBOX_RE = re.compile(r"^(\s*)-\s\[( |x|X)\]\s+(.*)$")
CHECKBOX_LOOSE_RE = re.compile(r"^\s*-\s*\[.*?\]")   # looks like a checkbox (for malformed detection)
TASK_ID_RE = re.compile(r"^(\d+(?:\.\d+)*)\b")
TASK_META_RE = re.compile(r"^\s+(files|pattern|verify)\s*:\s*(.+?)\s*$", re.IGNORECASE)
PARALLEL_RE = re.compile(r"^\[P\](?:\s|$)")
VERIFICATION_POLICIES = ("per-task", "per-section", "end-of-plan")
DEFAULT_VERIFICATION = "per-section"
ATTEMPT_BUDGET = 5   # attempts before a task is reported blocked rather than re-offered
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET_RE = re.compile(r"^\s*[-*+]\s")
SUBHEADING_RE = re.compile(r"^\s*(?:#{1,6}\s+|\*\*\S)")
# the ONE parsed anchor inside `## Impact` — as a sub-heading or a bold line
IMPACT_WRITES_RE = re.compile(r"^\s*(?:#{3,6}\s+|\*\*)\s*Standards this plan will write into\b",
                              re.IGNORECASE)
STANDARD_PATH_RE = re.compile(r"docs/standards/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*\.md")
PRIORITIES = ("critical", "high", "medium", "low")
GEN_BEGIN = "<!-- BEGIN GENERATED"
GEN_END = "<!-- END GENERATED -->"
BACKLOG_EMPTY = ("_(no tasks parked — this listing is regenerated deterministically "
                 "from `backlog/*.md` frontmatter)_")

# --------------------------------------------------------------------------- #
# embedded assets (fallbacks when the sibling asset files are absent)
# --------------------------------------------------------------------------- #
# `design` stays `required: false` and stays OUT of `applyRequires`, and the two facts are
# not in tension: design.md is required as a SECTION SET (the file exists, and an empty
# section is answered `- none — <reason>`), never as a DEPENDENCY of apply. Promoting it to
# a dependency would strand every plan authored before that rule — each would go from
# apply-ready to blocked on upgrade. `sp-design-scaffold` (warn) is how the section-set rule
# is enforced; `applyReady` is untouched by it. Keep this in lockstep with assets/specs/schema.json.
DEFAULT_SCHEMA: dict = {
    "schema": "spec-driven",
    "version": VERSION,
    "artifacts": [
        {"id": "proposal", "file": "proposal.md", "required": True, "dependsOn": []},
        {"id": "design", "file": "design.md", "required": False, "dependsOn": ["proposal"]},
        {"id": "tasks", "file": "tasks.md", "required": True, "dependsOn": ["proposal"]},
    ],
    "applyRequires": ["tasks"],
}

TEMPLATE_PROPOSAL = """# <TITLE>

## Why

<!-- The problem or opportunity this plan answers. Why now? -->

## What Changes

<!-- The change at a high level, in bullet points. -->

## Out of Scope

<!-- What this plan deliberately does NOT do, and why it was ruled out.

     An empty section is written as an explicit `- none` — NEVER omitted. "We drew the
     boundary and nothing fell outside it" and "nobody ever drew the boundary" are
     different answers, and an absent section cannot tell them apart. -->

## Validation

<!-- How anyone confirms this plan actually worked: the commands to run and the output
     they must produce, the fixtures to check, the invariants that must still hold
     afterwards. Same rule — an empty section is written as `- none`, which is a claim
     that the plan is unverifiable by construction. Make it on purpose or fill it in. -->

## Impact

<!-- Declared scope for human review.

     The `### Standards this plan will write into docs/standards/` sub-heading below is
     PARSED by `specs.py validate`: every `docs/standards/**.md` path bulleted under it
     must be named by a `tasks.md` item, or validate emits `sp-impact-uncovered` (warn).
     Keep that heading text verbatim — it is the anchor. A `**Standards this plan will
     write into ...**` bold line is accepted too, for plans written before this format.

     Example of a parsed bullet:
       - `docs/standards/naming/command-surface.md` — the bijection rule for wrappers

     The other sub-headings are prose for the reader and are deliberately NOT parsed:
     they name paths the plan does not promise to write. -->

### Standards this plan will write into docs/standards/

- `<docs/standards/subject/concept.md>` — <the rule it states>

### Standards at `authority: background` this plan may resolve

- <path, or `none`>

### Product code this plan expects to touch

- `<path>` — <why>
"""

TEMPLATE_DESIGN = """# Design — <TITLE>

<!-- design.md is REQUIRED-WITH-EXPLICIT-FALLBACK: the file always exists, and a section
     with nothing in it is answered `- none — <reason>`, never deleted and never padded.

     Do NOT delete this file to signal "no design was needed". An absent design.md cannot
     distinguish "we weighed the alternatives and there were none" from "nobody ever
     thought about it", and those are opposite facts. An explicit null is strictly more
     information than a missing file.

     A file left as this bare scaffold is reported by `specs.py validate` as
     `sp-design-scaffold` (warn), and `specs.py next` names it as the next artifact to
     write while tasks.md is still unwritten. Neither one blocks apply. -->

## Context

<!-- Background, the binding contracts this design must not contradict, and the forces
     at play. -->

## Decisions

<!-- The choices made and their rationale. For each: what was chosen, why, and what was
     weighed against it. -->

## Alternatives Considered

<!-- Whole-shape alternatives rejected at the plan level, each with the reason it lost.
     Per-decision alternatives can stay inside `## Decisions`; this section is for the
     ones that would have changed the plan's shape.

     Empty is written `- none — <reason>` (e.g. "only one viable approach"). -->

## Open Decisions

<!-- What is deliberately still undecided, and how each will be decided — the evidence
     or the moment that settles it, not "TBD".

     Empty is written `- none — <reason>`. -->

## Risks

<!-- What could go wrong, and the mitigation for each.

     Empty is written `- none — <reason>`. -->
"""

TEMPLATE_TASKS = """# Tasks — <TITLE>

<!-- Checkboxes are `- [ ] <id> <text>`, grouped under `## N. <Section>` headings.
     `specs.py task --plan <n> --check <id>` flips one mechanically — never hand-edit the
     `[ ]` / `[x]` character.

     A checkbox MAY carry indented metadata lines directly beneath it. They are parsed by
     `specs.py` and are purely additive: a task without them behaves exactly as it always
     did, and every tasks.md written before this format parses unchanged.

       - [ ] 3.2 Add rate limiting to the auth middleware
             files: src/middleware/auth.ts, src/config/limits.ts (new)
             pattern: src/middleware/cors.ts
             verify: pnpm test middleware/

     files:    the paths this task may touch. Declaring them is what PERMITS the task to be
               handed to an executor sub-agent, and what makes a `[P]` marker checkable.
     pattern:  an existing file to imitate — the cheapest context an executor can be given.
     verify:   the command that proves the task done. When it runs is the plan's
               `verification` policy in `.specs.json`, not this file's business.

     `[P]` right after the id marks a task parallel-eligible:

       - [ ] 3.3 [P] Add the rate-limit config loader

     It is set HERE, at propose time, and NEVER inferred while applying. It is honoured only
     when the marked tasks' `files:` sets are provably disjoint and none of them writes into
     `docs/` — `specs.py` checks the disjunction mechanically rather than judging it in prose.
     Serial execution is the default and needs no marker. -->

## 1. <Section>

- [ ] 1.1 <first task>
- [ ] 1.2 <next task>
"""

TEMPLATES = {"proposal": TEMPLATE_PROPOSAL, "design": TEMPLATE_DESIGN, "tasks": TEMPLATE_TASKS}


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


def now_iso() -> str:
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def today() -> str:
    return datetime.date.today().isoformat()


def read_text(path: str) -> str | None:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def load_schema() -> dict:
    p = os.path.join(ASSET_DIR, "schema.json")
    txt = read_text(p)
    if txt:
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            pass
    return DEFAULT_SCHEMA


def template(name: str) -> str:
    p = os.path.join(ASSET_DIR, "templates", f"{name}.md")
    txt = read_text(p)
    return txt if txt is not None else TEMPLATES[name]


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


def plan_dirs(root: str) -> list[str]:
    if not os.path.isdir(root):
        return []
    out = []
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if os.path.isdir(full) and name not in RESERVED_DIRS and not name.startswith("."):
            out.append(name)
    return out


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def mask_comments(text: str) -> str:
    """Blank out HTML-comment spans, preserving every newline and column so line numbers
    and offsets still line up with the original.

    `tasks.md`'s own template documents the format with example checkboxes inside its
    comment guidance. Without this, those examples parse as real tasks and a freshly
    scaffolded plan reports phantom progress — and `task --check` needs the surviving
    `lineno` to point at the true line, which stripping (rather than masking) would break."""
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
    """True when a file carries authored prose beyond the shipped template
    (headings, HTML comments, and `<placeholder>` lines don't count)."""
    body = strip_comments(body_after_frontmatter(text))
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


def section_lines(text: str, heading: str) -> list[str]:
    """The body lines of one `## <heading>` section — everything up to the next heading
    at the same or a higher level. Sub-headings (`###`+) stay in. Empty list when the
    section is absent."""
    want = heading.strip().lower()
    out: list[str] = []
    inside = False
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            if inside and level <= 2:
                break
            if not inside:
                inside = level == 2 and m.group(2).strip().lower() == want
                continue
        if inside:
            out.append(line)
    return out


def parse_impact_standards(text: str) -> list[str]:
    """The `docs/standards/**.md` paths a proposal DECLARES it will write, read from the
    one fixed sub-heading of `## Impact` (`### Standards this plan will write into ...`,
    or the same text as a `**bold**` line).

    Only that sub-heading is parsed, and deliberately so. Its siblings name paths the
    plan does NOT promise to write — a background standard it *may* resolve, the product
    code it touches — and parsing those would flag a plan for not writing a doc it never
    claimed. A proposal with no such sub-heading (every plan authored before this format)
    declares nothing and is therefore never flagged: the check is opt-in by writing the
    heading."""
    out: list[str] = []
    seen: set[str] = set()
    collecting = False
    for line in section_lines(strip_comments(text), "Impact"):
        if IMPACT_WRITES_RE.match(line):
            collecting = True
            continue
        if SUBHEADING_RE.match(line):     # any other sub-heading closes the parsed zone
            collecting = False
            continue
        if not collecting or not BULLET_RE.match(line):
            continue
        # An unfilled `<placeholder>` declares nothing — same rule has_real_content uses.
        # Without this the shipped template's own example bullet would make every freshly
        # scaffolded plan report sp-impact-uncovered against a path nobody ever wrote.
        for m in STANDARD_PATH_RE.finditer(PLACEHOLDER_RE.sub("", line)):
            if m.group(0) not in seen:
                seen.add(m.group(0))
                out.append(m.group(0))
    return out


def parse_tasks(text: str) -> list[dict]:
    """Every checkbox in tasks.md, in order: index (1-based), explicit id (leading dotted
    number, or None), checked bool, text, 0-based line number, the `[P]` parallel-eligible
    marker, and the optional indented execution metadata beneath it (`files`, `pattern`,
    `verify`).

    CHECKBOX_RE is deliberately UNTOUCHED. The metadata lives on lines that never matched
    it, so every tasks.md authored before this format parses identically and simply reports
    empty metadata — the extension is additive, never a migration."""
    out = []
    idx = 0
    section = 0
    lines = mask_comments(text).splitlines()
    for lineno, line in enumerate(lines):
        hm = HEADING_RE.match(line)
        if hm and len(hm.group(1)) == 2:
            section += 1          # a `## N.` heading starts a new section
            continue
        m = CHECKBOX_RE.match(line)
        if not m:
            continue
        idx += 1
        checked = m.group(2).lower() == "x"
        body = m.group(3).strip()
        idm = TASK_ID_RE.match(body)
        rest = body[idm.end():].lstrip() if idm else body
        parallel = bool(PARALLEL_RE.match(rest))
        files: list[str] = []
        pattern = verify = None
        for cont in lines[lineno + 1:]:
            # the task's block ends at a blank line, a non-indented line (a heading or the
            # next section), or another checkbox; anything else indented is scanned, so a
            # wrapped prose line between the checkbox and its `verify:` does not hide it.
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
            "checked": checked,
            "text": body,
            "lineno": lineno,
            "section": section,
            "parallel": parallel,
            "files": files,
            "pattern": pattern,
            "verify": verify,
        })
    return out


def meta_path(root: str, name: str) -> str:
    return os.path.join(root, name, ".specs.json")


def read_meta(root: str, name: str) -> dict:
    txt = read_text(meta_path(root, name))
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
    except json.JSONDecodeError:
        return {}
    return obj if isinstance(obj, dict) else {}


def write_meta(root: str, name: str, meta: dict) -> None:
    """MERGE semantics are the caller's: read_meta, mutate, write_meta. Never build a
    fresh dict here — `name`, `title`, `created`, `backlogTask`, `refined`, and
    `verification` all have to survive an attempt being recorded."""
    pathlib.Path(meta_path(root, name)).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def verification_policy(root: str, name: str) -> str:
    """The plan's declared verification policy. Declared once at propose time so `apply`
    never has to guess when to run the suite, and never has to ask mid-implementation."""
    v = str(read_meta(root, name).get("verification", "")).strip().lower()
    return v if v in VERIFICATION_POLICIES else DEFAULT_VERIFICATION


def task_attempts(root: str, name: str) -> dict:
    a = read_meta(root, name).get("attempts")
    return a if isinstance(a, dict) else {}


def attempt_count(attempts: dict, label: str) -> int:
    rec = attempts.get(label)
    if not isinstance(rec, dict):
        return 0
    try:
        return int(rec.get("count", 0))
    except (TypeError, ValueError):
        return 0


def task_progress(text: str) -> tuple[int, int]:
    tasks = parse_tasks(text)
    return sum(1 for t in tasks if t["checked"]), len(tasks)


# --------------------------------------------------------------------------- #
# artifact graph / status
# --------------------------------------------------------------------------- #
def artifact_state(root: str, name: str) -> dict:
    """Resolve the graph for one plan: per-artifact done/ready/blocked, task
    progress, apply-readiness, and the concrete file paths."""
    schema = load_schema()
    pdir = os.path.join(root, name)
    arts = []
    done_ids: set[str] = set()
    for spec in schema["artifacts"]:
        fpath = os.path.join(pdir, spec["file"])
        txt = read_text(fpath)
        present = os.path.isfile(fpath)
        if spec["id"] == "tasks":
            done = present and txt is not None and bool(parse_tasks(txt)) and has_real_content(txt)
        else:
            done = present and txt is not None and has_real_content(txt)
        arts.append({"spec": spec, "present": present, "done": done, "path": fpath})
        if done:
            done_ids.add(spec["id"])
    result = []
    for a in arts:
        spec = a["spec"]
        deps_done = all(d in done_ids for d in spec["dependsOn"])
        if a["done"]:
            state = "done"
        elif deps_done:
            state = "ready"
        else:
            state = "blocked"
        result.append({
            "id": spec["id"],
            "file": spec["file"],
            "required": spec["required"],
            "state": state,
            "path": os.path.relpath(a["path"], os.path.dirname(root)).replace(os.sep, "/"),
        })
    tasks_txt = read_text(os.path.join(pdir, "tasks.md")) or ""
    done_ct, total_ct = task_progress(tasks_txt)
    apply_ready = all(i in done_ids for i in schema["applyRequires"])
    attempts = task_attempts(root, name)
    blocked = []
    for t in parse_tasks(tasks_txt):
        if t["checked"]:
            continue
        label = t["id"] or str(t["index"])
        tried = attempt_count(attempts, label)
        if tried >= ATTEMPT_BUDGET:
            rec = attempts.get(label) or {}
            blocked.append({"task": label, "attempts": tried,
                            "lastError": rec.get("lastError")})
    meta = read_meta(root, name)
    return {
        "plan": name,
        "artifacts": result,
        "tasks": {"checked": done_ct, "total": total_ct, "blocked": blocked},
        "applyReady": apply_ready,
        "verification": verification_policy(root, name),
        "refined": meta.get("refined") if isinstance(meta.get("refined"), dict) else None,
    }


def compute_next(root: str, name: str) -> dict:
    st = artifact_state(root, name)
    by_id = {a["id"]: a for a in st["artifacts"]}
    if by_id["proposal"]["state"] != "done":
        return {"plan": name, "action": "write_artifact", "artifact": "proposal",
                "file": "proposal.md",
                "message": "write proposal.md — the plan's why and declared impact"}
    design = by_id.get("design")
    if (design is not None and design["state"] != "done"
            and by_id["tasks"]["state"] != "done"
            and os.path.isfile(os.path.join(root, name, "design.md"))):
        # design.md exists but is a bare scaffold: it is required-with-explicit-fallback,
        # so an empty section is answered with `- none — <reason>`, never left unfilled.
        # An ABSENT design.md is a legacy plan and is left alone (backward compatible),
        # and once tasks.md is authored the plan has moved past the design phase — the
        # scaffold is then a `sp-design-scaffold` warning from `validate`, not a next action.
        return {"plan": name, "action": "write_artifact", "artifact": "design",
                "file": "design.md",
                "message": "fill design.md — context, decisions, alternatives considered, open "
                           "decisions, risks (write `- none — <reason>` where a section is empty)"}
    if by_id["tasks"]["state"] != "done":
        return {"plan": name, "action": "write_artifact", "artifact": "tasks",
                "file": "tasks.md",
                "message": "write tasks.md — the implementation checklist"}
    tasks_txt = read_text(os.path.join(root, name, "tasks.md")) or ""
    attempts = task_attempts(root, name)
    blocked: list[dict] = []
    for t in parse_tasks(tasks_txt):
        if t["checked"]:
            continue
        label = t["id"] or str(t["index"])
        tried = attempt_count(attempts, label)
        if tried >= ATTEMPT_BUDGET:
            # A failed task is not an untried one. Re-offering a task that already burned
            # its budget is how an apply loop spins forever on the same error.
            rec = attempts.get(label) or {}
            blocked.append({"task": label, "attempts": tried,
                            "lastError": rec.get("lastError")})
            continue
        return {"plan": name, "action": "implement_task", "task": label,
                "text": t["text"], "attempts": tried,
                "verify": t["verify"], "files": t["files"], "pattern": t["pattern"],
                "parallel": t["parallel"],
                "verification": verification_policy(root, name),
                "blocked": blocked,
                "message": f"implement task {label}: {t['text']}"}
    if blocked:
        names = ", ".join(b["task"] for b in blocked)
        return {"plan": name, "action": "blocked", "blocked": blocked,
                "message": f"every remaining task is blocked after {ATTEMPT_BUDGET} attempts "
                           f"({names}) — a human decides: revise the plan "
                           f"(`/specs:plan:update`) or reset the attempts"}
    return {"plan": name, "action": "archive_ready",
            "message": "all tasks checked — ready to archive (`specs.py archive %s`)" % name}


# --------------------------------------------------------------------------- #
# backlog reindex — this tool OWNS the GENERATED zone format
# --------------------------------------------------------------------------- #
def _as_list(v) -> list[str]:
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def backlog_tasks(backlog_dir: str) -> list[dict]:
    out = []
    for name in sorted(os.listdir(backlog_dir)):
        if not name.endswith(".md") or name == "index.md":
            continue
        txt = read_text(os.path.join(backlog_dir, name))
        if txt is None:
            continue
        fm = parse_frontmatter(txt)
        prio = str(fm.get("priority", "")).strip().lower()
        out.append({
            "slug": name[:-3],
            "title": str(fm.get("title", "")).strip() or name[:-3],
            "description": str(fm.get("description", "")).strip(),
            "tags": _as_list(fm.get("tags")),
            "priority": prio if prio in PRIORITIES else "",
            "complexity": str(fm.get("complexity", "")).strip(),
            "timestamp": str(fm.get("timestamp", "")).strip(),
        })
    return out


def render_backlog_zone(tasks: list[dict]) -> str:
    if not tasks:
        return BACKLOG_EMPTY
    groups: dict[str, list[dict]] = {p: [] for p in PRIORITIES}
    untriaged: list[dict] = []
    for t in tasks:
        (groups[t["priority"]] if t["priority"] else untriaged).append(t)
    counts = {p: len(groups[p]) for p in PRIORITIES}
    summary = (f"**{len(tasks)} task{'s' if len(tasks) != 1 else ''}** · "
               f"{counts['critical']} critical · {counts['high']} high · "
               f"{counts['medium']} medium · {counts['low']} low · "
               f"{len(untriaged)} untriaged")
    lines = [summary, ""]
    ordered = [(p.capitalize(), groups[p]) for p in PRIORITIES] + [("Untriaged", untriaged)]
    for label, rows in ordered:
        if not rows:
            continue
        rows = sorted(rows, key=lambda r: (r["timestamp"] or "~", r["slug"]))  # oldest-first
        lines.append(f"#### {label}")
        lines.append("")
        lines.append("| Task | Description | Tags | Complexity | Since |")
        lines.append("| --- | --- | --- | --- | --- |")
        for r in rows:
            tags = ", ".join(r["tags"]) if r["tags"] else "—"
            cx = f"{r['complexity']}h" if r["complexity"] else "—"
            since = r["timestamp"] or "—"
            desc = r["description"] or "—"
            lines.append(f"| [{r['title']}]({r['slug']}.md) | {desc} | {tags} | {cx} | {since} |")
        lines.append("")
    theme: dict[str, list[dict]] = {}
    for t in tasks:
        for tag in t["tags"]:
            theme.setdefault(tag, []).append(t)
    if theme:
        lines.append("#### By theme")
        lines.append("")
        for tag in sorted(theme):
            members = sorted(theme[tag], key=lambda r: r["slug"])
            links = ", ".join(f"[{m['slug']}]({m['slug']}.md)" for m in members)
            lines.append(f"- **{tag}** ({len(members)}): {links}")
    return "\n".join(lines).rstrip()


def reindex_backlog(root: str) -> tuple[int, dict]:
    backlog_dir = os.path.join(root, "backlog")
    index_path = os.path.join(backlog_dir, "index.md")
    if not os.path.isdir(backlog_dir):
        return 1, {"ok": False, "findings": [{"code": "sp-no-backlog",
                   "message": "no backlog/ directory under the specs root"}]}
    txt = read_text(index_path)
    if txt is None:
        return 1, {"ok": False, "findings": [{"code": "sp-no-backlog-index",
                   "message": "backlog/index.md is missing or unreadable"}]}
    zone = render_backlog_zone(backlog_tasks(backlog_dir))
    begin = txt.find(GEN_BEGIN)
    end = txt.find(GEN_END)
    if begin != -1 and end != -1 and end > begin:
        comment_close = txt.find("-->", begin)
        head = txt[:comment_close + 3]
        tail = txt[end:]
        new = f"{head}\n{zone}\n{tail}"
    else:
        anchor = txt.find("## Current tasks")
        if anchor == -1:
            return 1, {"ok": False, "findings": [{"code": "sp-no-zone",
                       "message": "backlog/index.md has neither GENERATED markers nor a "
                                  "`## Current tasks` heading to anchor the zone"}]}
        nl = txt.find("\n", anchor)
        marker = (f"{GEN_BEGIN}: rebuilt from the tasks' frontmatter by `specs.py backlog reindex` "
                  f"— DO NOT edit by hand. -->\n{zone}\n{GEN_END}")
        new = f"{txt[:nl+1]}\n{marker}\n{txt[nl+1:]}"
    if new != txt:
        pathlib.Path(index_path).write_text(new, encoding="utf-8")
    return 0, {"ok": True, "changed": new != txt,
               "path": os.path.relpath(index_path, os.path.dirname(root)).replace(os.sep, "/"),
               "taskCount": len(backlog_tasks(backlog_dir))}


# --------------------------------------------------------------------------- #
# subcommands
# --------------------------------------------------------------------------- #
def emit(as_json: bool, obj: dict, human: str) -> None:
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        print(human)


def cmd_new(args, root: str) -> int:
    slug = slugify(args.name)
    if not slug:
        emit(args.json, {"ok": False, "error": "empty name"}, "error: empty plan name")
        return 1
    pdir = os.path.join(root, slug)
    if os.path.exists(pdir):
        emit(args.json, {"ok": False, "error": "exists", "plan": slug},
             f"error: plan '{slug}' already exists")
        return 1
    os.makedirs(pdir, exist_ok=True)
    title = args.title or titleize(slug)
    for key, fname in (("proposal", "proposal.md"), ("design", "design.md"), ("tasks", "tasks.md")):
        content = template(key).replace("<TITLE>", title)
        pathlib.Path(os.path.join(pdir, fname)).write_text(content, encoding="utf-8")
    # `refined` is seeded null so the field is discoverable in every plan rather than
    # appearing out of nowhere: quenching-specs-plan-refine replaces it with
    # {"mode": ..., "date": ...}, and anything that is not an object reads as unrefined.
    verification = (args.verification or DEFAULT_VERIFICATION).strip().lower()
    if verification not in VERIFICATION_POLICIES:
        emit(args.json, {"ok": False, "error": "bad-verification", "value": verification,
                         "allowed": list(VERIFICATION_POLICIES)},
             f"error: --verification must be one of {', '.join(VERIFICATION_POLICIES)}")
        return 1
    meta = {"schema": load_schema().get("schema", "spec-driven"), "name": slug,
            "title": title, "created": now_iso(),
            "backlogTask": args.backlog_task or None,
            # declared at propose time so apply never guesses when to run the suite, and
            # never has to ask mid-implementation; `refined` seeded null so the field is
            # discoverable rather than appearing out of nowhere after a refine pass.
            "verification": verification,
            "refined": None}
    pathlib.Path(os.path.join(pdir, ".specs.json")).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rel = os.path.relpath(pdir, os.path.dirname(root)).replace(os.sep, "/")
    emit(args.json, {"ok": True, "plan": slug, "title": title, "path": rel,
                     "files": ["proposal.md", "design.md", "tasks.md", ".specs.json"]},
         f"created plan '{slug}' at {rel}/ (proposal.md, design.md, tasks.md, .specs.json)")
    return 0


def cmd_list(args, root: str) -> int:
    plans = []
    for name in plan_dirs(root):
        pdir = os.path.join(root, name)
        tasks_txt = read_text(os.path.join(pdir, "tasks.md")) or ""
        checked, total = task_progress(tasks_txt)
        mtime = 0.0
        for f in os.listdir(pdir):
            try:
                mtime = max(mtime, os.path.getmtime(os.path.join(pdir, f)))
            except OSError:
                pass
        plans.append({"plan": name, "tasks": {"checked": checked, "total": total},
                      "lastModified": datetime.datetime.fromtimestamp(mtime).replace(
                          microsecond=0).isoformat() if mtime else None})
    if args.json:
        print(json.dumps({"plans": plans}, indent=2, ensure_ascii=False))
    else:
        if not plans:
            print("no active plans")
        for p in plans:
            print(f"  {p['plan']}  [{p['tasks']['checked']}/{p['tasks']['total']} tasks]"
                  f"  {p['lastModified'] or ''}")
    return 0


def _require_plan(args, root: str) -> str | None:
    if not os.path.isdir(os.path.join(root, args.plan)):
        emit(args.json, {"ok": False, "error": "no-plan", "plan": args.plan},
             f"error: no plan '{args.plan}' under {root}")
        return None
    return args.plan


def cmd_status(args, root: str) -> int:
    if _require_plan(args, root) is None:
        return 1
    st = artifact_state(root, args.plan)
    if args.json:
        print(json.dumps(st, indent=2, ensure_ascii=False))
    else:
        print(f"plan: {st['plan']}  (tasks {st['tasks']['checked']}/{st['tasks']['total']}, "
              f"applyReady={st['applyReady']})")
        for a in st["artifacts"]:
            opt = "" if a["required"] else " (optional)"
            print(f"  {a['id']:<9} {a['state']:<8}{opt}  {a['file']}")
    return 0


def cmd_next(args, root: str) -> int:
    if _require_plan(args, root) is None:
        return 1
    nxt = compute_next(root, args.plan)
    emit(args.json, nxt, f"next: {nxt['message']}")
    return 0


def cmd_task(args, root: str) -> int:
    if _require_plan(args, root) is None:
        return 1
    modes = [bool(args.check), bool(args.uncheck), bool(args.attempt),
             bool(args.reset_attempts)]
    if sum(modes) != 1:
        emit(args.json, {"ok": False,
                         "error": "need exactly one of --check / --uncheck / --attempt / "
                                  "--reset-attempts"},
             "error: pass exactly one of --check ID, --uncheck ID, --attempt ID, "
             "--reset-attempts ID")
        return 1
    if args.attempt or args.reset_attempts:
        return _cmd_task_attempt(args, root)
    target = args.check or args.uncheck
    to_checked = bool(args.check)
    tpath = os.path.join(root, args.plan, "tasks.md")
    txt = read_text(tpath)
    if txt is None:
        emit(args.json, {"ok": False, "error": "no-tasks"}, "error: tasks.md missing")
        return 1
    tasks = parse_tasks(txt)
    match = None
    for t in tasks:
        if t["id"] == target or str(t["index"]) == target:
            match = t
            break
    if match is None:
        emit(args.json, {"ok": False, "error": "no-such-task", "task": target},
             f"error: no task '{target}' in {args.plan}/tasks.md")
        return 1
    lines = txt.splitlines(keepends=True)
    ln = match["lineno"]
    old = lines[ln]
    mark = "x" if to_checked else " "
    new_line = re.sub(r"\[( |x|X)\]", f"[{mark}]", old, count=1)
    lines[ln] = new_line
    pathlib.Path(tpath).write_text("".join(lines), encoding="utf-8")
    label = match["id"] or str(match["index"])
    emit(args.json, {"ok": True, "task": label, "checked": to_checked,
                     "text": match["text"], "changed": old != new_line},
         f"task {label} {'checked' if to_checked else 'unchecked'}: {match['text']}")
    return 0


def _cmd_task_attempt(args, root: str) -> int:
    """Record (or clear) a task's attempt state. Kept mechanical for the same reason the
    checkbox is: an apply loop hand-editing JSON between retries is exactly the string
    surgery this tool exists to remove."""
    target = args.attempt or args.reset_attempts
    tasks_txt = read_text(os.path.join(root, args.plan, "tasks.md"))
    if tasks_txt is None:
        emit(args.json, {"ok": False, "error": "no-tasks"}, "error: tasks.md missing")
        return 1
    labels = {(t["id"] or str(t["index"])) for t in parse_tasks(tasks_txt)}
    if target not in labels:
        emit(args.json, {"ok": False, "error": "no-such-task", "task": target},
             f"error: no task '{target}' in {args.plan}/tasks.md")
        return 1
    meta = read_meta(root, args.plan)
    attempts = meta.get("attempts")
    if not isinstance(attempts, dict):
        attempts = {}
    if args.reset_attempts:
        attempts.pop(target, None)
        meta["attempts"] = attempts
        write_meta(root, args.plan, meta)
        emit(args.json, {"ok": True, "task": target, "attempts": 0, "reset": True},
             f"task {target}: attempts reset")
        return 0
    count = attempt_count(attempts, target) + 1
    attempts[target] = {"count": count, "lastError": args.error or None,
                        "lastAttempt": now_iso()}
    meta["attempts"] = attempts
    write_meta(root, args.plan, meta)
    exhausted = count >= ATTEMPT_BUDGET
    emit(args.json,
         {"ok": True, "task": target, "attempts": count, "budget": ATTEMPT_BUDGET,
          "exhausted": exhausted, "lastError": args.error or None},
         f"task {target}: attempt {count}/{ATTEMPT_BUDGET}"
         + (" — budget exhausted, reported blocked" if exhausted else ""))
    return 0


def cmd_backlog(args, root: str) -> int:
    if args.backlog_cmd != "reindex":
        emit(args.json, {"ok": False, "error": "unknown backlog subcommand"},
             "error: only `backlog reindex` is supported")
        return 1
    code, obj = reindex_backlog(root)
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    elif obj.get("ok"):
        print(f"backlog reindexed: {obj['path']} ({obj['taskCount']} task(s), "
              f"{'changed' if obj['changed'] else 'already current'})")
    else:
        for f in obj.get("findings", []):
            print(f"  [{f['code']}] {f['message']}")
    return code


def _norm_file(p: str) -> str:
    p = re.sub(r"\s*\([^)]*\)\s*$", "", p.strip())   # drop a trailing "(new)" annotation
    p = p.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    return p.rstrip("/")


def _overlaps(a: str, b: str) -> bool:
    """Two declared paths conflict when they are the same file, or when one is a
    directory containing the other — `src/` and `src/a.ts` are not disjoint."""
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def parallel_groups(tasks: list[dict]) -> list[list[dict]]:
    """Maximal runs of consecutive still-open `[P]` tasks within ONE `## N.` section. An
    already-checked task does not split a run (it is done, so it cannot conflict); a
    non-parallel open task does, and so does a section boundary — a section is the smallest
    independently shippable unit, so a group must not straddle two. A lone `[P]` task is not
    a group; there is nothing to run it alongside."""
    groups: list[list[dict]] = []
    cur: list[dict] = []
    for t in tasks:
        if t["checked"]:
            continue
        if t["parallel"] and (not cur or t["section"] == cur[-1]["section"]):
            cur.append(t)
            continue
        if len(cur) >= 2:
            groups.append(cur)
        cur = [t] if t["parallel"] else []
    if len(cur) >= 2:
        groups.append(cur)
    return groups


def check_parallel(tasks: list[dict]) -> list[dict]:
    """Verify each `[P]` group MECHANICALLY. The marker is a proposal-time claim; this is
    what makes it a fact, so apply branches on data instead of judging disjunction in prose."""
    out = []
    for g in parallel_groups(tasks):
        labels = [t["id"] or str(t["index"]) for t in g]
        files = {lbl: [_norm_file(f) for f in t["files"]] for lbl, t in zip(labels, g)}
        reasons: list[str] = []
        for lbl in labels:
            if not files[lbl]:
                reasons.append(f"task {lbl} declares no `files:` — disjunction cannot be proved")
            for f in files[lbl]:
                if f == "docs" or f.startswith("docs/"):
                    reasons.append(f"task {lbl} writes into docs/ ({f}) — never parallelized")
        for i, a in enumerate(labels):
            for b in labels[i + 1:]:
                for fa in files[a]:
                    for fb in files[b]:
                        if _overlaps(fa, fb):
                            both = fa if fa == fb else f"{fa} / {fb}"
                            reasons.append(f"tasks {a} and {b} are not disjoint ({both})")
        out.append({"tasks": labels, "files": files, "eligible": not reasons,
                    "reasons": sorted(set(reasons))})
    return out


def cmd_parallel(args, root: str) -> int:
    if _require_plan(args, root) is None:
        return 1
    tasks_txt = read_text(os.path.join(root, args.plan, "tasks.md"))
    if tasks_txt is None:
        emit(args.json, {"ok": False, "error": "no-tasks"}, "error: tasks.md missing")
        return 1
    groups = check_parallel(parse_tasks(tasks_txt))
    ok = all(g["eligible"] for g in groups)
    if args.json:
        print(json.dumps({"ok": ok, "plan": args.plan, "groups": groups},
                         indent=2, ensure_ascii=False))
    elif not groups:
        print(f"no [P] groups in {args.plan} — every task runs serially")
    else:
        for g in groups:
            state = "eligible" if g["eligible"] else "NOT eligible — run serially"
            print(f"  [{', '.join(g['tasks'])}] {state}")
            for r in g["reasons"]:
                print(f"      {r}")
    return 0 if ok else 1


def _validate_plan(root: str, name: str) -> list[dict]:
    findings = []
    pdir = os.path.join(root, name)
    if not KEBAB_RE.match(name):
        findings.append({"severity": "error", "plan": name, "code": "sp-bad-name",
                         "message": f"plan folder '{name}' is not kebab-case"})
    if not os.path.isfile(os.path.join(pdir, ".specs.json")):
        findings.append({"severity": "warn", "plan": name, "code": "sp-no-meta",
                         "message": "plan has no .specs.json metadata"})
    prop = read_text(os.path.join(pdir, "proposal.md"))
    if prop is None:
        findings.append({"severity": "error", "plan": name, "code": "sp-missing-proposal",
                         "message": "proposal.md is missing"})
    elif not has_real_content(prop):
        findings.append({"severity": "warn", "plan": name, "code": "sp-empty-proposal",
                         "message": "proposal.md is still the unfilled template"})
    design = read_text(os.path.join(pdir, "design.md"))
    if design is not None and not has_real_content(design):
        # An ABSENT design.md is a legacy plan and never flagged; a PRESENT but unfilled
        # one is the case the old contract could not tell from "we weighed alternatives
        # and there were none" — an explicit `- none — <reason>` is the answer.
        findings.append({"severity": "warn", "plan": name, "code": "sp-design-scaffold",
                         "message": "design.md exists but is still the unfilled scaffold — fill "
                                    "it, or answer each empty section with `- none — <reason>`"})
    tasks_txt = read_text(os.path.join(pdir, "tasks.md"))
    if tasks_txt is None:
        findings.append({"severity": "error", "plan": name, "code": "sp-missing-tasks",
                         "message": "tasks.md is missing"})
    else:
        strict = 0
        for line in mask_comments(tasks_txt).splitlines():
            if CHECKBOX_LOOSE_RE.match(line):
                if CHECKBOX_RE.match(line):
                    strict += 1
                else:
                    findings.append({"severity": "error", "plan": name, "code": "sp-bad-checkbox",
                                     "message": f"malformed checkbox: {line.strip()!r} "
                                                "(expected `- [ ] ` or `- [x] `)"})
        if strict == 0:
            findings.append({"severity": "warn", "plan": name, "code": "sp-no-tasks",
                             "message": "tasks.md has no parseable checkbox"})
    # Refinement: visible, never gating. A plan with a checklist has reached the point where
    # somebody should have disagreed with it, and `applyReady` cannot tell whether anyone did.
    # WARN only — gating apply on this would break every plan in every installed repo on
    # upgrade, and the front never blocks on a judgment call.
    if tasks_txt is not None:
        meta = {}
        meta_txt = read_text(os.path.join(pdir, ".specs.json"))
        if meta_txt:
            try:
                meta = json.loads(meta_txt)
            except json.JSONDecodeError:
                meta = {}
        if not isinstance(meta.get("refined"), dict):
            findings.append({"severity": "warn", "plan": name, "code": "sp-unrefined",
                             "message": "no refinement recorded in .specs.json — the plan reached "
                                        "a checklist without anyone interrogating it "
                                        "(`/specs:plan:refine`)"})
    # Impact coverage: a standard the proposal PROMISES to write must be somebody's job.
    # Matched against the whole of tasks.md rather than a single parsed checkbox, because
    # a task item routinely wraps across lines and the path can land on a continuation.
    if prop is not None and tasks_txt is not None:
        for path in parse_impact_standards(prop):
            if path not in tasks_txt:
                findings.append({"severity": "warn", "plan": name, "code": "sp-impact-uncovered",
                                 "message": f"proposal.md `## Impact` declares `{path}` but no "
                                            "tasks.md item names it — add the task, or drop the "
                                            "path from the declared scope"})
    return findings


def cmd_validate(args, root: str) -> int:
    names = [args.plan] if args.plan else plan_dirs(root)
    if args.plan and not os.path.isdir(os.path.join(root, args.plan)):
        emit(args.json, {"ok": False, "error": "no-plan", "plan": args.plan},
             f"error: no plan '{args.plan}'")
        return 1
    findings = []
    for name in names:
        findings.extend(_validate_plan(root, name))
    errors = [f for f in findings if f["severity"] == "error"]
    if args.json:
        print(json.dumps({"ok": not errors, "findings": findings}, indent=2, ensure_ascii=False))
    else:
        print(f"specs validate — {len(errors)} error(s), "
              f"{len(findings) - len(errors)} warning(s)")
        for f in findings:
            print(f"  [{f['severity']:<5}] {f['plan']}: {f['message']}  ({f['code']})")
        if not findings:
            print("  OK — plans conform.")
    return 1 if errors else 0


def cmd_archive(args, root: str) -> int:
    name = args.name
    pdir = os.path.join(root, name)
    if not os.path.isdir(pdir):
        emit(args.json, {"ok": False, "error": "no-plan", "plan": name},
             f"error: no plan '{name}'")
        return 1
    tasks_txt = read_text(os.path.join(pdir, "tasks.md")) or ""
    checked, total = task_progress(tasks_txt)
    open_tasks = total - checked
    dest_name = f"{today()}-{name}"
    dest = os.path.join(root, "archive", dest_name)
    if open_tasks > 0 and not args.force:
        emit(args.json,
             {"ok": False, "code": "sp-open-tasks", "plan": name,
              "openTasks": open_tasks, "total": total,
              "message": f"{open_tasks} of {total} tasks still open — pass --force to archive anyway"},
             f"refused: {open_tasks} of {total} tasks still open in '{name}' — "
             f"pass --force to archive anyway")
        return 2
    if args.dry_run:
        emit(args.json,
             {"ok": True, "dryRun": True, "plan": name, "openTasks": open_tasks,
              "dest": os.path.relpath(dest, os.path.dirname(root)).replace(os.sep, "/")},
             f"dry-run: would move '{name}' -> archive/{dest_name} "
             f"({open_tasks} open task(s))")
        return 0
    os.makedirs(os.path.join(root, "archive"), exist_ok=True)
    if os.path.exists(dest):
        emit(args.json, {"ok": False, "error": "dest-exists", "dest": dest_name},
             f"error: archive/{dest_name} already exists")
        return 1
    os.rename(pdir, dest)
    emit(args.json,
         {"ok": True, "plan": name,
          "dest": os.path.relpath(dest, os.path.dirname(root)).replace(os.sep, "/"),
          "openTasks": open_tasks},
         f"archived '{name}' -> archive/{dest_name}")
    return 0


def cmd_doctor(args, root: str) -> int:
    findings = []
    if not os.path.isdir(root):
        findings.append({"code": "sp-no-workspace", "severity": "error",
                         "message": f"no specs/ workspace at {root}",
                         "remedy": "scaffold specs/ (copy the plugin's assets/specs skeleton)"})
        _emit_doctor(args, root, findings)
        return 1
    backlog_index = os.path.join(root, "backlog", "index.md")
    if not os.path.isfile(backlog_index):
        findings.append({"code": "sp-no-backlog", "severity": "warn",
                         "message": "no backlog/index.md",
                         "remedy": "install assets/specs/backlog/index.md"})
    for name in plan_dirs(root):
        pdir = os.path.join(root, name)
        if not os.path.isfile(os.path.join(pdir, ".specs.json")):
            findings.append({"code": "sp-no-meta", "severity": "warn", "plan": name,
                             "message": f"plan '{name}' has no .specs.json",
                             "remedy": "run `specs.py new` semantics or add .specs.json"})
        if not KEBAB_RE.match(name):
            findings.append({"code": "sp-bad-name", "severity": "error", "plan": name,
                             "message": f"plan '{name}' is not kebab-case",
                             "remedy": "rename the plan folder to kebab-case (gate on code coupling)"})
    for entry in (os.listdir(root) if os.path.isdir(root) else []):
        full = os.path.join(root, entry)
        if os.path.isfile(full) and entry != ".specs.json":
            findings.append({"code": "sp-stray-file", "severity": "warn", "path": entry,
                             "message": f"stray file at the specs root: {entry}",
                             "remedy": "move it into a plan folder or remove it"})
    _emit_doctor(args, root, findings)
    return 1 if any(f["severity"] == "error" for f in findings) else 0


def _emit_doctor(args, root: str, findings: list[dict]) -> None:
    if args.json:
        print(json.dumps({"ok": not any(f["severity"] == "error" for f in findings),
                          "root": root, "findings": findings}, indent=2, ensure_ascii=False))
    else:
        errs = sum(1 for f in findings if f["severity"] == "error")
        print(f"specs doctor — {root} ({errs} error(s), {len(findings) - errs} warning(s))")
        for f in findings:
            print(f"  [{f['severity']:<5}] {f.get('plan', f.get('path', '-'))}: "
                  f"{f['message']}  ({f['code']})")
            print(f"          remedy: {f['remedy']}")
        if not findings:
            print("  OK — workspace conforms.")


# --------------------------------------------------------------------------- #
# dispatch
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="specs.py", description="deterministic trail for the specs/ front")
    p.add_argument("--root", help="the specs/ workspace directory (default: nearest specs/ upward)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_json(sp):
        sp.add_argument("--json", action="store_true", help="machine-readable output")

    sp = sub.add_parser("new"); sp.add_argument("name"); sp.add_argument("--title")
    sp.add_argument("--backlog-task", dest="backlog_task")
    sp.add_argument("--verification", choices=list(VERIFICATION_POLICIES),
                    help=f"when the suite runs (default: {DEFAULT_VERIFICATION})")
    add_json(sp)
    add_json(sub.add_parser("list"))
    sp = sub.add_parser("status"); sp.add_argument("--plan", required=True); add_json(sp)
    sp = sub.add_parser("next"); sp.add_argument("--plan", required=True); add_json(sp)
    sp = sub.add_parser("task"); sp.add_argument("--plan", required=True)
    sp.add_argument("--check"); sp.add_argument("--uncheck")
    sp.add_argument("--attempt", help="record a failed attempt at TASK (against the budget)")
    sp.add_argument("--reset-attempts", dest="reset_attempts",
                    help="clear TASK's attempt state so `next` offers it again")
    sp.add_argument("--error", help="the failure to record alongside --attempt")
    add_json(sp)
    sp = sub.add_parser("parallel"); sp.add_argument("--plan", required=True); add_json(sp)
    sp = sub.add_parser("backlog"); sp.add_argument("backlog_cmd", choices=["reindex"]); add_json(sp)
    sp = sub.add_parser("validate"); sp.add_argument("--plan"); add_json(sp)
    sp = sub.add_parser("archive"); sp.add_argument("name")
    sp.add_argument("--dry-run", action="store_true"); sp.add_argument("--force", action="store_true")
    add_json(sp)
    add_json(sub.add_parser("doctor"))
    return p


DISPATCH = {
    "new": cmd_new, "list": cmd_list, "status": cmd_status, "next": cmd_next,
    "task": cmd_task, "parallel": cmd_parallel, "backlog": cmd_backlog,
    "validate": cmd_validate, "archive": cmd_archive, "doctor": cmd_doctor,
}


def _force_utf8_output() -> None:
    """Plan artifacts are prose — em-dashes, arrows, accented words — and a Windows
    console defaults to cp1252, where printing one raises UnicodeEncodeError AFTER the
    write already landed. That turns a successful `task --check` into a traceback and a
    nonzero exit, which the exit-code contract (0 ok / 1 findings / 2 refusal) reads as a
    finding. Encode output as UTF-8 and never let a glyph decide the exit code."""
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
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "json"):
        args.json = False
    root = find_specs_root(args.root)
    return DISPATCH[args.cmd](args, root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
