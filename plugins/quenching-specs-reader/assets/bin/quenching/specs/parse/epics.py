"""Epics — a spec whose `## Tasks` items reference member specs, derived and never ticked.

Pure derivation, no backend and no I/O: the caller hands over the epic's `info` and the members'
`info` rows it read, and gets the state back. That is what keeps one answer across the memory
fake, the git store and the tracker backends.

An epic item reads `- [ ] S2 Title — spec: #1202 — after: S1,S3`. The `### N.` headings above
the items are its groups (waves). The item's state is DERIVED from the member document: done when
the member is archived with `outcome: done`, blocked when one of its tasks is `[!]`. The box
written in the epic is never read as state, which is why `task` refuses epic items."""
from __future__ import annotations

import re

from quenching.specs.parse.sections import ready_report
from quenching.specs.parse.tasks import task_progress
from quenching.specs.parse.text import HEADING_RE

EPIC_TYPE = "epic"
# The 100-sub-issue ceiling a GitHub parent card carries (to be confirmed); `validate` warns.
MAX_ITEMS = 100

_SPEC_RE = re.compile(r"(?:^|\s)—\s*spec\s*:\s*#?([^\s—]+)", re.IGNORECASE)
_AFTER_RE = re.compile(r"(?:^|\s)—\s*after\s*:\s*([^—]*?)\s*(?=—|$)", re.IGNORECASE)
_TAIL_RE = re.compile(r"\s—\s*(?:spec|after|blocked|descoped)\s*:.*$", re.IGNORECASE)
_LABEL_NUM_RE = re.compile(r"(\d+)$")


def is_epic(fm: dict) -> bool:
    return str(fm.get("workItemType", "")).strip().lower() == EPIC_TYPE


def epic_ref(fm: dict) -> str | None:
    """The `epic:` key a member carries, as a bare id string."""
    v = str(fm.get("epic") or "").strip().lstrip("#").strip()
    return v or None


def group_titles(info: dict) -> list[str]:
    """The `### ` headings under `## Tasks`, in order; the first one is group 1."""
    sec = info["sections"].get("Tasks")
    heads = [HEADING_RE.match(line) for line in (sec["lines"] if sec else [])]
    return [m.group(2).strip() for m in heads if m and len(m.group(1)) == 3]


def parse_items(info: dict) -> list[dict]:
    """Every `## Tasks` line of an epic as an item: label, title, member id, `after` labels, group."""
    titles = group_titles(info)
    items = []
    for t in info["tasks"]:
        body = t["text"]
        head = _TAIL_RE.sub("", body).strip()
        label, _, title = head.partition(" ")
        sm, am = _SPEC_RE.search(body), _AFTER_RE.search(body)
        group = t["section"]
        items.append({
            "label": label, "title": title.strip(), "spec": sm.group(1) if sm else None,
            "after": [a.strip() for a in am.group(1).split(",") if a.strip()] if am else [],
            "group": group, "groupTitle": titles[group - 1] if 0 < group <= len(titles) else None,
            "writtenState": t["state"], "lineno": t["lineno"],
            "blockEndLineno": t["blockEndLineno"],
        })
    return items


def member_state(member: dict | None) -> str:
    """`missing`, `done`, `dropped` (archived without `done`), `blocked` or `open`."""
    if member is None:
        return "missing"
    if member["phase"] == "archive":
        return "done" if str(member["frontmatter"].get("outcome", "")).strip() == "done" \
            else "dropped"
    return "blocked" if task_progress(member["tasks"])[1] else "open"


def find_cycle(items: list[dict]) -> list[str] | None:
    """One dependency cycle as a label path (`A, B, A`), or `None`. Unknown labels are ignored."""
    graph = {i["label"]: list(i["after"]) for i in items}
    color: dict[str, int] = {}
    stack: list[str] = []

    def visit(n: str) -> list[str] | None:
        color[n] = 1
        stack.append(n)
        for d in graph.get(n, []):
            if d not in graph:
                continue
            if color.get(d, 0) == 1:
                return stack[stack.index(d):] + [d]
            if color.get(d, 0) == 0:
                found = visit(d)
                if found:
                    return found
        stack.pop()
        color[n] = 2
        return None

    for n in graph:
        if color.get(n, 0) == 0:
            found = visit(n)
            if found:
                return found
    return None


def derive_epic(info: dict, members: dict[str, dict | None]) -> dict:
    """The epic's whole derived state. `members` maps a member id string to its `info`, or `None`."""
    items = parse_items(info)
    by_label = {i["label"]: i for i in items}
    for i in items:
        m = members.get(str(i["spec"])) if i["spec"] else None
        i["member"] = m
        i["memberState"] = member_state(m) if i["spec"] else "missing"
    for i in items:
        m, st = i["member"], i["memberState"]
        waiting = [d for d in i["after"]
                   if d not in by_label or by_label[d]["memberState"] != "done"]
        i["waitingOn"] = waiting
        if st != "open":
            i["status"] = st
        elif waiting:
            i["status"] = "waiting"
        elif m["frontmatter"].get("approved") or ready_report(m)["ok"]:
            i["status"] = "in-progress" if m["stage"] == "executing" else "ready"
        else:
            i["status"] = "not-ready"
        i["checked"] = st == "done"
    cycle = find_cycle(items)
    return {"items": items, "groups": _groups(info, items), "cycle": cycle,
            "criticalPath": [] if cycle else _critical_path(items, by_label),
            "ready": [i for i in items if i["status"] in ("ready", "in-progress")]}


def _groups(info: dict, items: list[dict]) -> list[dict]:
    titles = group_titles(info)
    out = []
    for n in sorted({i["group"] for i in items}):
        its = [i for i in items if i["group"] == n]
        out.append({"group": n, "title": titles[n - 1] if 0 < n <= len(titles) else None,
                    "done": sum(1 for i in its if i["status"] == "done"),
                    "blocked": sum(1 for i in its if i["status"] == "blocked"),
                    "total": len(its)})
    return out


def _critical_path(items: list[dict], by_label: dict[str, dict]) -> list[str]:
    """The longest dependency chain of items not yet done, in execution order."""
    memo: dict[str, list[str]] = {}

    def chain(label: str) -> list[str]:
        if label in memo:
            return memo[label]
        best: list[str] = []
        for d in by_label[label]["after"]:
            if d in by_label and by_label[d]["status"] != "done":
                c = chain(d)
                if len(c) > len(best):
                    best = c
        memo[label] = best + [label]
        return memo[label]

    longest: list[str] = []
    for i in items:
        if i["status"] != "done":
            c = chain(i["label"])
            if len(c) > len(longest):
                longest = c
    return longest


def next_label(items: list[dict]) -> str:
    nums = [int(m.group(1)) for i in items if (m := _LABEL_NUM_RE.search(i["label"]))]
    return f"S{max(nums, default=0) + 1}"


def render_item(label: str, title: str, spec_id: str, after: list[str]) -> str:
    line = f"- [ ] {label} {title} — spec: #{spec_id}"
    return line + (f" — after: {','.join(after)}" if after else "")


def open_items(info: dict, members: dict[str, dict | None]) -> list[dict]:
    """Items that keep an epic from being archived as `done`."""
    return [i for i in derive_epic(info, members)["items"] if i["status"] != "done"]


def epic_findings(info: dict, members: dict[str, dict | None]) -> list[dict]:
    """Finding rows for ONE epic: missing members, divergence, unknown dependencies, cycles."""
    eid = str(info["id"])
    items = parse_items(info)
    rows: list[dict] = []

    def add(code, severity, message, **extra):
        rows.append({"code": code, "severity": severity, "message": message, "spec": eid,
                     **extra})

    if not items:
        add("sp-epic-empty", "warn", f"epic {eid} lists no member specs under ## Tasks")
    if len(items) > MAX_ITEMS:
        add("sp-epic-too-large", "warn",
            f"epic {eid} has {len(items)} items; a GitHub parent card carries at most "
            f"{MAX_ITEMS} sub-issues — split the epic")
    labels: set[str] = set()
    for i in items:
        if i["label"] in labels:
            add("sp-epic-duplicate-label", "error",
                f"epic {eid}: label `{i['label']}` is used twice", label=i["label"])
        labels.add(i["label"])
        if i["writtenState"] != " ":
            add("sp-epic-manual-tick", "warn",
                f"epic {eid}: item {i['label']} is written `[{i['writtenState']}]` — epic item "
                f"state is derived from the member; leave the box open", label=i["label"])
    seen: dict[str, str] = {}
    for i in items:
        if not i["spec"]:
            add("sp-epic-item-unlinked", "error",
                f"epic {eid}: item {i['label']} has no `— spec: #<id>`", label=i["label"])
            continue
        if i["spec"] in seen:
            add("sp-epic-duplicate-member", "error",
                f"epic {eid}: spec {i['spec']} is listed by {seen[i['spec']]} and "
                f"{i['label']}", member=i["spec"])
        seen[i["spec"]] = i["label"]
        for d in i["after"]:
            if d not in labels:
                add("sp-epic-unknown-dependency", "error",
                    f"epic {eid}: item {i['label']} comes after `{d}`, which is not an item",
                    label=i["label"], dependency=d)
        m = members.get(i["spec"])
        if m is None:
            add("sp-epic-missing-member", "error",
                f"epic {eid}: item {i['label']} references spec {i['spec']}, which does not "
                f"exist", label=i["label"], member=i["spec"])
            continue
        if is_epic(m["frontmatter"]):
            add("sp-epic-nested", "error",
                f"epic {eid}: member {i['spec']} is itself an epic — one level only",
                member=i["spec"])
        back = epic_ref(m["frontmatter"])
        if back != eid:
            add("sp-epic-divergent", "error",
                f"epic {eid} lists spec {i['spec']}, but that spec's `epic:` is "
                f"{back or 'unset'}", member=i["spec"],
                remedy=f"cq specs epic add {eid} {i['spec']}")
    cycle = find_cycle(items)
    if cycle:
        add("sp-epic-cycle", "error",
            f"epic {eid}: dependency cycle {' -> '.join(cycle)}", cycle=cycle)
    return rows


def claim_findings(info: dict, epics: dict[str, dict | None]) -> list[dict]:
    """The member's side: its `epic:` names an epic that is absent, not an epic, or omits it."""
    ref = epic_ref(info["frontmatter"])
    if not ref:
        return []
    sid, parent = str(info["id"]), epics.get(ref)
    if parent is None:
        code, msg = "sp-epic-orphan", f"spec {sid} declares `epic: {ref}`, which does not exist"
    elif not is_epic(parent["frontmatter"]):
        code, msg = ("sp-epic-not-an-epic", f"spec {sid} declares `epic: {ref}`, which is not a "
                                             f"`workItemType: epic` spec")
    elif sid not in {str(i["spec"]) for i in parse_items(parent)}:
        code, msg = "sp-epic-divergent", (f"spec {sid} declares `epic: {ref}`, but that epic "
                                          f"does not list it")
    else:
        return []
    return [{"code": code, "severity": "error", "message": msg, "spec": sid,
             "remedy": f"cq specs epic add {ref} {sid}"}]
