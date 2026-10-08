"""The epic verbs — `epic add`, `status --epic` and `next --epic`.

An epic is a spec whose `## Tasks` items reference member specs (`parse/epics.py` owns the
grammar and the derivation, which is pure). This module is only the backend plumbing: read the
epic and its members in ONE `read_specs` call, hand them to the derivation, print the answer.
Nothing here is written back on a read, so a member's state is never stored twice."""
from __future__ import annotations

import json
import re
import subprocess

from quenching.specs.backends import open_backend
from quenching.specs.commands.output import Emitter, front_fields
from quenching.specs.parse.edit import upsert_section
from quenching.specs.parse.epics import (derive_epic, epic_ref, group_titles, is_epic,
                                         next_label, parse_items, pr_number, render_item)
from quenching.specs.parse.fields import scalar_break, set_frontmatter_key
from quenching.specs.parse.sections import parse_sections
from quenching.specs.parse.text import HEADING_RE, mask_comments

LABEL_RE = re.compile(r"^[A-Za-z0-9][\w.-]*$")
GROUP_NUMBER_RE = re.compile(r"^\d+\.\s*")


def _refuse(out: Emitter, args, code: str, message: str, **extra) -> int:
    return out.emit_err(args.json, {"code": code, "exit": 2, "message": message, **extra})


def _pr_target(member: dict) -> str:
    """What `gh pr view` is given: the recorded `pr.url` when it is a URL (it names the repository
    itself), else the bare number, which `gh` resolves against the working directory."""
    rec = member["frontmatter"].get("pr")
    url = str(rec.get("url", "")).strip() if isinstance(rec, dict) else ""
    return url if url.startswith(("http://", "https://")) else pr_number(member)


def pr_states(members: dict, root: str | None = None, timeout: int = 15) -> dict[str, str]:
    """`member id -> PR state` for every archived member carrying a `pr:` record, read with
    `gh pr view` from `root` (the repository `--root` names, not the process cwd). A lookup that
    fails is left out, and the derivation then marks it `unverified`."""
    out: dict[str, str] = {}
    for sid, m in members.items():
        if not m or m["phase"] != "archive" or not pr_number(m):
            continue
        try:
            r = subprocess.run(["gh", "pr", "view", _pr_target(m), "--json", "state", "-q", ".state"],
                               capture_output=True, text=True, timeout=timeout, cwd=root)
        except (OSError, subprocess.SubprocessError):
            continue
        if r.returncode == 0 and r.stdout.strip():
            out[str(sid)] = r.stdout.strip()
    return out


def load_epic(backend, epic_id, args, out: Emitter, root: str | None = None):
    """`(info, derived, None)` for a readable epic, or `(None, None, exit_code)` after a refusal."""
    got = backend.read_specs([epic_id])
    info = got.get(str(epic_id))
    if info is None:
        return None, None, _refuse(out, args, "sp-unknown-id", f"no spec with id '{epic_id}'",
                                   id=epic_id)
    if not is_epic(info["frontmatter"]):
        return None, None, _refuse(out, args, "sp-epic-not-an-epic",
                                   f"spec {epic_id} is not a `workItemType: epic` spec",
                                   id=epic_id)
    ids = [i["spec"] for i in parse_items(info) if i["spec"]]
    members = backend.read_specs(ids)
    return info, derive_epic(info, members, pr_states(members, root)), None


def _find_group(titles: list[str], wanted: str) -> int | None:
    want = wanted.strip().casefold()
    for n, title in enumerate(titles, 1):
        bare = GROUP_NUMBER_RE.sub("", title).casefold()
        if want in (title.casefold(), bare) or bare.startswith(want + " —"):
            return n
    return None


def _group_heading(group: str, number: int) -> str:
    """A group label that already opens with "N." is used as is; any other gets `number`."""
    return group if GROUP_NUMBER_RE.match(group) else f"{number}. {group}"


def insert_item(info: dict, line: str, group: str | None) -> str:
    """The epic's document with `line` added under `## Tasks` — after the last item of `group`
    (a new `### N.` heading when the group is new), else after the last item overall."""
    text = info["text"]
    sec = parse_sections(mask_comments(text)).get("Tasks")
    if sec is None:
        body = "## Tasks\n\n" + (f"### {_group_heading(group, 1)}\n" if group else "") + line + "\n"
        return upsert_section(info, "Tasks", body)[0]
    lines = text.splitlines(keepends=True)
    base = sec["lineno"] + 1
    end = base + len(sec["lines"])
    while end > base and not lines[end - 1].strip():
        end -= 1
    items, titles = parse_items(info), group_titles(info)
    add = [line + "\n"]
    pos = end
    if group is None:
        pos = items[-1]["blockEndLineno"] if items else end
    else:
        n = _find_group(titles, group)
        if n is None:
            heading = _group_heading(group, len(titles) + 1)
            add = [] if not lines[end - 1].strip() else ["\n"]
            add += [f"### {heading}\n", line + "\n"]
        else:
            mine = [i for i in items if i["group"] == n]
            if mine:
                pos = mine[-1]["blockEndLineno"]
            else:
                heads = [i for i in range(base, end)
                         if (m := HEADING_RE.match(lines[i])) and len(m.group(1)) == 3]
                pos = heads[n - 1] + 1
    if pos > 0 and not lines[pos - 1].endswith("\n"):
        lines[pos - 1] += "\n"
    lines[pos:pos] = add
    return "".join(lines)


def cmd_epic(args, root: str, out: Emitter) -> int:
    """`epic add <epic> <spec>` — list a spec as an epic item AND stamp `epic:` on the spec.

    Both documents change in one `write_specs` batch where the backend has one (a single commit
    on the git store); elsewhere the epic is written first, so a half-failed add leaves the
    `epic:` divergence `validate` names, with `epic add` itself as the remedy."""
    if getattr(args, "epic_cmd", None) != "add":
        return _refuse(out, args, "sp-no-command", "choose an epic command: add")
    # The group becomes a `### N.` heading line: a break would forge the lines after it.
    bad = scalar_break(args.group or "")
    if bad:
        return _refuse(out, args, "sp-bad-scalar",
                       f"--group is one line with no control character — got {bad}",
                       field="group", char=bad)
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    epic_id, spec_id = str(args.epic), str(args.spec)
    if epic_id == spec_id:
        return _refuse(out, args, "sp-epic-self", "an epic cannot be its own member")
    epic, _, code = load_epic(backend, epic_id, args, out, root)
    if code is not None:
        return code
    member = backend.read_specs([spec_id]).get(spec_id)
    if member is None:
        return _refuse(out, args, "sp-unknown-id", f"no spec with id '{spec_id}'", id=spec_id)
    if is_epic(member["frontmatter"]):
        return _refuse(out, args, "sp-epic-nested",
                       f"spec {spec_id} is itself an epic — an epic has one level only")
    current = epic_ref(member["frontmatter"])
    if current and current != epic_id:
        return _refuse(out, args, "sp-epic-member-taken",
                       f"spec {spec_id} already belongs to epic {current}", epic=current)
    items = parse_items(epic)
    existing = next((i for i in items if i["spec"] == spec_id), None)
    new_epic, label = None, None
    if existing:
        label = existing["label"]
    else:
        after = [a.strip() for a in (args.after or "").split(",") if a.strip()]
        known = {i["label"] for i in items}
        label = args.label or next_label(items)
        if not LABEL_RE.match(label) or label in known:
            return _refuse(out, args, "sp-epic-bad-label",
                           f"label '{label}' is used or not a plain token")
        unknown = [a for a in after if a not in known]
        if unknown:
            return _refuse(out, args, "sp-epic-unknown-dependency",
                           f"--after names no item of epic {epic_id}: {', '.join(unknown)}",
                           unknown=unknown)
        title = str(member["frontmatter"].get("title") or "").strip() or f"Spec {spec_id}"
        new_epic = insert_item(epic, render_item(label, title, spec_id, after), args.group)
    batch = []
    if new_epic is not None:
        batch.append((epic, new_epic))
    if current != epic_id:
        batch.append((member, set_frontmatter_key(member["text"], "epic", epic_id,
                                                  after="workItemType")))
    if len(batch) > 1 and hasattr(backend, "write_specs"):
        backend.write_specs(batch)
    else:
        for info, text in batch:
            backend.write_spec(info, text)
    out.emit(args.json, {"ok": True, "epic": epic_id, "spec": spec_id, "label": label,
                         "changed": bool(batch)},
             f"epic {epic_id}: {label} -> spec {spec_id}" + ("" if batch else " (already linked)"))
    return 0


def _row(i: dict) -> dict:
    m = i["member"]
    return {"label": i["label"], "title": i["title"], "spec": i["spec"], "group": i["group"],
            "status": i["status"], "after": i["after"], "waitingOn": i["waitingOn"],
            "stage": m["stage"] if m else None}


def cmd_epic_status(args, root: str, out: Emitter) -> int:
    """`status --epic <id>` — progress per group, what is blocked, and the critical path."""
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    info, d, code = load_epic(backend, args.epic, args, out, root)
    if code is not None:
        return code
    items = d["items"]
    done = sum(1 for i in items if i["status"] == "done")
    blocked = [{**_row(i), "reasons": [t["reason"] or t["text"] for t in i["member"]["tasks"]
                                       if t["blocked"]] if i["member"] else []}
               for i in items if i["status"] in ("blocked", "dropped", "missing", "unmerged", "unverified")]
    for b, i in zip(blocked, [i for i in items if i["status"] in
                              ("blocked", "dropped", "missing", "unmerged", "unverified")]):
        if i["status"] == "unmerged":
            b["reasons"] = [f"PR #{pr_number(i['member'])} is {i['prState']}"]
        elif i["status"] == "unverified":
            b["reasons"] = [f"PR #{pr_number(i['member'])} state could not be read"]
    obj = {"ok": True, **front_fields(root), "id": info["id"],
           "title": info["frontmatter"].get("title", ""), "phase": info["phase"],
           "progress": {"done": done, "total": len(items), "blocked": len(blocked),
                        "ready": len(d["ready"])},
           "groups": d["groups"], "items": [_row(i) for i in items], "blocked": blocked,
           "criticalPath": d["criticalPath"], "cycle": d["cycle"]}
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0
    p = obj["progress"]
    print(f"epic {info['id']} — {obj['title']}: {p['done']}/{p['total']} done, "
          f"{p['blocked']} blocked, {p['ready']} ready")
    for g in d["groups"]:
        name = g["title"] or "(no group)"
        print(f"  {name}: {g['done']}/{g['total']} done"
              + (f", {g['blocked']} blocked" if g["blocked"] else ""))
    for b in blocked:
        print(f"  [{b['status']}] {b['label']} spec {b['spec']}: {'; '.join(b['reasons'])}")
    if d["cycle"]:
        print(f"  cycle: {' -> '.join(d['cycle'])}")
    elif d["criticalPath"]:
        print(f"  critical path: {' -> '.join(d['criticalPath'])}")
    return 0


def cmd_next_epic(args, root: str, out: Emitter) -> int:
    """`next --epic <id> [--limit N]` — the ready set: dependencies done, member approved or
    ready, not blocked. In-flight members first, then the human's priority, then wave order."""
    from quenching.specs.commands.next import _priority_rank   # next imports this module
    limit = getattr(args, "limit", None)
    if limit is not None and limit < 1:
        return _refuse(out, args, "sp-bad-limit", "--limit takes a positive number")
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    info, d, code = load_epic(backend, args.epic, args, out, root)
    if code is not None:
        return code
    order = {i["label"]: n for n, i in enumerate(d["items"])}
    ready = sorted(d["ready"], key=lambda i: (
        i["status"] != "in-progress", _priority_rank(i["member"]["frontmatter"].get("priority"))[0],
        i["group"], order[i["label"]]))
    shown = ready[:limit] if limit else ready
    rows = [{**_row(i), "executing": i["status"] == "in-progress",
             "priority": i["member"]["frontmatter"].get("priority") or None} for i in shown]
    left = [i for i in d["items"] if i["status"] != "done"]
    obj = {"ok": True, "epic": info["id"], "count": len(rows), "readyTotal": len(ready),
           "remaining": len(left), "finished": not left and bool(d["items"]),
           "cycle": d["cycle"], "ready": rows}
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0
    if not rows:
        print(f"epic {info['id']}: nothing ready — {len(left)} item(s) remaining"
              if left else f"epic {info['id']}: every item is done")
        return 0
    print(f"epic {info['id']}: {len(rows)} of {len(ready)} ready to run")
    for r in rows:
        print(f"  {r['label']:<5} spec {r['spec']:<8} {r['title']}"
              + ("  (in progress)" if r["executing"] else ""))
    return 0
