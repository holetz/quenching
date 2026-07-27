#!/usr/bin/env python3
"""specs.py — self-contained deterministic trail for the `specs/` front.

Payload of the `quenching` plugin, sibling of `assets/hooks/okf-validate.py`
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
        .specs.json         # plan metadata (schema, name, created, seed task)
        proposal.md         # what & why
        design.md           # how (OPTIONAL)
        tasks.md            # implementation checklist (- [ ] / - [x])
      archive/              # completed/abandoned plans, YYYY-MM-DD-<name>/
      backlog/              # the task inbox (type: task), one file per task
        index.md            # a listing with a GENERATED zone (see `backlog reindex`)
        <task-slug>.md

The artifact graph is THREE artifacts, not four — the OpenSpec `specs` (delta) node
is gone: `proposal` -> `design` (optional) -> `tasks`, with `applyRequires: [tasks]`.

OUTPUT CONTRACT (uniform across every subcommand)
-------------------------------------------------
`--json` on every subcommand, and STRICT exit codes so the skill ramifies on data:
  0  ok
  1  findings (validate/doctor found something; a plan/task was not found)
  2  refusal  (archive with open tasks and no --force)

SUBCOMMANDS
  new <name> [--title T] [--backlog-task SLUG]   scaffold a plan folder + filled templates + .specs.json
  list                                            active plans, task progress, lastModified
  status --plan N                                 the artifact graph over the schema (done/ready/blocked)
  next --plan N                                   THE single next action (write X / implement task Y / archive)
  task --plan N --check ID | --uncheck ID         flip a checkbox in tasks.md mechanically
  backlog reindex                                 regenerate the GENERATED zone of backlog/index.md from frontmatter
  validate [--plan N]                             required artifacts present, tasks parseable, canonical names
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

VERSION = "1.0.0"  # kept in lockstep with the plugin VERSION file, plugin.json, and okf-validate.py

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.normpath(os.path.join(HERE, "..", "specs"))
RESERVED_DIRS = ("archive", "backlog")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CHECKBOX_RE = re.compile(r"^(\s*)-\s\[( |x|X)\]\s+(.*)$")
CHECKBOX_LOOSE_RE = re.compile(r"^\s*-\s*\[.*?\]")   # looks like a checkbox (for malformed detection)
TASK_ID_RE = re.compile(r"^(\d+(?:\.\d+)*)\b")
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
PRIORITIES = ("critical", "high", "medium", "low")
GEN_BEGIN = "<!-- BEGIN GENERATED"
GEN_END = "<!-- END GENERATED -->"
BACKLOG_EMPTY = ("_(no tasks parked — this listing is regenerated deterministically "
                 "from `backlog/*.md` frontmatter)_")

# --------------------------------------------------------------------------- #
# embedded assets (fallbacks when the sibling asset files are absent)
# --------------------------------------------------------------------------- #
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

## Impact

<!-- Declared scope for human review: the `docs/` paths this plan intends to create
     or change, and any product code it touches. Prose, not a machine contract. -->
"""

TEMPLATE_DESIGN = """# Design — <TITLE>

## Context

<!-- Background, constraints, and the forces at play. Delete this file if the plan
     needs no design note — `design.md` is optional. -->

## Decisions

<!-- The choices made, their rationale, and the alternatives considered. -->

## Risks

<!-- What could go wrong, and the mitigation. -->
"""

TEMPLATE_TASKS = """# Tasks — <TITLE>

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


def parse_tasks(text: str) -> list[dict]:
    """Every checkbox in tasks.md, in order: index (1-based), explicit id (leading
    dotted number, or None), checked bool, text, and 0-based line number."""
    out = []
    idx = 0
    for lineno, line in enumerate(text.splitlines()):
        m = CHECKBOX_RE.match(line)
        if not m:
            continue
        idx += 1
        checked = m.group(2).lower() == "x"
        body = m.group(3).strip()
        idm = TASK_ID_RE.match(body)
        out.append({
            "index": idx,
            "id": idm.group(1) if idm else None,
            "checked": checked,
            "text": body,
            "lineno": lineno,
        })
    return out


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
    return {
        "plan": name,
        "artifacts": result,
        "tasks": {"checked": done_ct, "total": total_ct},
        "applyReady": apply_ready,
    }


def compute_next(root: str, name: str) -> dict:
    st = artifact_state(root, name)
    by_id = {a["id"]: a for a in st["artifacts"]}
    if by_id["proposal"]["state"] != "done":
        return {"plan": name, "action": "write_artifact", "artifact": "proposal",
                "file": "proposal.md",
                "message": "write proposal.md — the plan's why and declared impact"}
    if by_id["tasks"]["state"] != "done":
        return {"plan": name, "action": "write_artifact", "artifact": "tasks",
                "file": "tasks.md",
                "message": "write tasks.md — the implementation checklist (design.md is optional)"}
    tasks_txt = read_text(os.path.join(root, name, "tasks.md")) or ""
    for t in parse_tasks(tasks_txt):
        if not t["checked"]:
            label = t["id"] or str(t["index"])
            return {"plan": name, "action": "implement_task", "task": label,
                    "text": t["text"],
                    "message": f"implement task {label}: {t['text']}"}
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
    meta = {"schema": load_schema().get("schema", "spec-driven"), "name": slug,
            "title": title, "created": now_iso(),
            "backlogTask": args.backlog_task or None}
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
    if bool(args.check) == bool(args.uncheck):
        emit(args.json, {"ok": False, "error": "need exactly one of --check / --uncheck"},
             "error: pass exactly one of --check ID or --uncheck ID")
        return 1
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
    tasks_txt = read_text(os.path.join(pdir, "tasks.md"))
    if tasks_txt is None:
        findings.append({"severity": "error", "plan": name, "code": "sp-missing-tasks",
                         "message": "tasks.md is missing"})
    else:
        strict = 0
        for line in tasks_txt.splitlines():
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
    sp.add_argument("--backlog-task", dest="backlog_task"); add_json(sp)
    add_json(sub.add_parser("list"))
    sp = sub.add_parser("status"); sp.add_argument("--plan", required=True); add_json(sp)
    sp = sub.add_parser("next"); sp.add_argument("--plan", required=True); add_json(sp)
    sp = sub.add_parser("task"); sp.add_argument("--plan", required=True)
    sp.add_argument("--check"); sp.add_argument("--uncheck"); add_json(sp)
    sp = sub.add_parser("backlog"); sp.add_argument("backlog_cmd", choices=["reindex"]); add_json(sp)
    sp = sub.add_parser("validate"); sp.add_argument("--plan"); add_json(sp)
    sp = sub.add_parser("archive"); sp.add_argument("name")
    sp.add_argument("--dry-run", action="store_true"); sp.add_argument("--force", action="store_true")
    add_json(sp)
    add_json(sub.add_parser("doctor"))
    return p


DISPATCH = {
    "new": cmd_new, "list": cmd_list, "status": cmd_status, "next": cmd_next,
    "task": cmd_task, "backlog": cmd_backlog, "validate": cmd_validate,
    "archive": cmd_archive, "doctor": cmd_doctor,
}


def main(argv: list[str]) -> int:
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
