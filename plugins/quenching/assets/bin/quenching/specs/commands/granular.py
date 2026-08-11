"""Granular reading — `section` and `show`.

The two verbs that exist so an executor is handed a task line and `## Handoff` rather than the
whole document. `section` slices N sections deterministically (and writes ONE); `show` answers
what `section` cannot — which headings and task ids exist, one task's line and metadata, and the
whole document only under a name nobody types by accident."""
from __future__ import annotations

import json
import sys

from quenching.specs.backends import open_backend
from quenching.specs.commands.output import Emitter, display_locator, read_one
from quenching.specs.commands.task import _find_task
from quenching.specs.parse.edit import _match_heading, upsert_section, write_handoff_block
from quenching.specs.parse.sections import section_state, stray_headings
from quenching.specs.schema import canonical_headings, headings_for_moment, section_guidance


def cmd_section(args, root: str, out: Emitter) -> int:
    """Deterministic partial read/write of N sections — what makes lean agent context real.

    An executor is handed a task line and `## Handoff`, never the whole spec; this is the
    command that slices it without an LLM re-reading and rewriting the file.

    **The read form is plural, and that is half the saving, not a convenience.** Every turn
    re-sends the whole conversation, so a cost has two factors — tokens AND the turns that
    follow it. Six headings fetched over six turns can lose to the one `Read` this command
    replaced. Comma-separated, one call, back in the order asked.

    `--write` stays singular: it takes stdin, and there is no unambiguous way to split one
    stream across several sections.

    The document comes from the BACKEND, never from a path: this is the reader every other
    front calls, so a backend that could not serve it would leave the whole surface tied to
    `files`."""
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    info, err = read_one(backend, args.spec, out)
    if err:
        return out.emit_err(args.json, err)
    if args.moment:
        wanted = headings_for_moment(args.moment)
        if not wanted:
            out.emit(args.json,
                     {"ok": False, "code": "sp-unknown-moment", "moment": args.moment,
                      "message": f"no canonical section declares moment '{args.moment}'"},
                     f"error: no canonical section declares moment '{args.moment}'")
            return 2
    else:
        wanted = [h for h in (p.strip() for p in (args.heading or "").split(",")) if h]
        if not wanted:
            out.emit(args.json,
                     {"ok": False, "code": "sp-no-heading",
                      "message": "give a heading, or --moment, to read"},
                     "error: give a heading, or --moment, to read")
            return 2
    headings, stray = [], []
    for name in wanted:
        h = _match_heading(name)
        (headings.append(h) if h else stray.append(name))
    if stray:
        out.emit(args.json,
                 {"ok": False, "code": "sp-stray-heading", "heading": stray[0],
                  "stray": stray, "canonical": canonical_headings(),
                  "message": f"not one of the fourteen canonical headings: {', '.join(stray)}"},
                 f"error: not a canonical heading: {', '.join(stray)}")
        return 2
    if args.write and len(headings) != 1:
        out.emit(args.json,
                 {"ok": False, "code": "sp-write-plural", "stray": headings,
                  "message": "--write takes exactly one heading — stdin is one stream"},
                 "error: --write takes exactly one heading")
        return 2
    if not args.write:
        rows = [{"heading": h, "state": section_state(info["sections"], h),
                 "body": info["sections"].get(h, {}).get("body", "")} for h in headings]
        absent = [r["heading"] for r in rows if r["state"] == "absent"]
        if args.json:
            one = rows[0] if len(rows) == 1 else {}
            print(json.dumps({"ok": not absent, "slug": info["slug"],
                              **one, "sections": rows, "absent": absent},
                             indent=2, ensure_ascii=False))
        else:
            for r in rows:
                if r["state"] == "absent":
                    print(f"(## {r['heading']} is absent)")
                elif len(rows) == 1:
                    print(r["body"].strip())
                else:
                    print(f"## {r['heading']}\n\n{r['body'].strip()}\n")
        return 0 if not absent else 1
    heading = headings[0]
    scope = getattr(args, "scope", None)
    if scope and heading != "Handoff":
        out.emit(args.json,
                 {"ok": False, "code": "sp-scope-not-handoff", "heading": heading,
                  "message": "--scope only applies to ## Handoff — every other section is "
                             "written whole"},
                 "error: --scope only applies to ## Handoff")
        return 2

    content = sys.stdin.read() if not sys.stdin.isatty() else ""
    if scope:
        new_text, action = write_handoff_block(info, scope, content)
    else:
        block = (f"## {heading}\n\n{content.strip()}\n"
                 if content.strip() else section_guidance(heading))
        new_text, action = upsert_section(info, heading, block)
    backend.write_spec(info, new_text)
    out.emit(args.json,
             {"ok": True, "slug": info["slug"], "heading": heading, "action": action,
              "scope": scope, "path": display_locator(info["path"], root)},
             f"{action} ## {heading}{f' ({scope})' if scope else ''} in "
             f"{info['phase']}/{info['file']}")
    return 0


# The reader's view of a task. `metaInsertAt`, `metaIndent`, `subjectLineno` and
# `commitLineno` are deliberately NOT here: they are the offsets `task` upserts by, and
# handing them to a reader is an invitation to do the string surgery `task` exists to
# prevent. `lineno` stays, because locating a task in the file is reading, not writing.
SHOWN_TASK_KEYS = ("index", "id", "state", "checked", "blocked", "reason", "text",
                   "section", "parallel", "files", "pattern", "verify", "subject",
                   "commit", "lineno")


def _task_view(t: dict) -> dict:
    return {k: t[k] for k in SHOWN_TASK_KEYS}


def _show_index(info: dict) -> dict:
    """The MAP of one spec — which sections exist, how big each is, which task ids there are.

    Bounded by the fourteen headings and the task count no matter how long the document is,
    which is what makes it affordable as the default. It also makes the NEXT call exact: a
    caller that knows the heading spellings and the task ids never has to read the document
    to find out what it may ask for."""
    return {
        "sections": [{"heading": h,
                      "state": section_state(info["sections"], h),
                      "lines": len(info["sections"].get(h, {}).get("lines", []))}
                     for h in canonical_headings()],
        "strays": stray_headings(info["sections"]),
        "tasks": [{"id": t["id"], "index": t["index"], "state": t["state"], "text": t["text"]}
                  for t in info["tasks"]],
    }


def _show_human(obj: dict, info: dict) -> str:
    head = (f"{obj['slug']} — {obj['title']}\n"
            f"  {info['folder']}/{info['file']}  [{obj['stage']}]")
    if obj["view"] == "full":
        return info["text"].rstrip("\n")
    marks = {"filled": "✓", "empty": "!", "absent": "·"}
    out = [head]
    if obj["view"] == "index":
        out.append(f"  sections ({sum(1 for s in obj['sections'] if s['state'] != 'absent')}"
                   f"/{len(obj['sections'])} present)")
        for s in obj["sections"]:
            size = f"  {s['lines']} line(s)" if s["state"] != "absent" else ""
            out.append(f"    {marks[s['state']]} ## {s['heading']}{size}")
        if obj["strays"]:
            out.append(f"  strays: {', '.join(obj['strays'])}")
        if obj["tasks"]:
            out.append(f"  tasks ({len(obj['tasks'])})")
            for t in obj["tasks"]:
                out.append(f"    [{t['state']}] {t['text']}")
        out.append(f"  read sections: cq specs section {obj['slug']} \"<Heading>,<Heading>\"\n"
                   f"  read one task: cq specs show --spec {obj['slug']} --task <id>"
                   f"   (--full for the whole document)")
        return "\n".join(out)
    for t in obj["tasks"]:
        out.append(f"\n- [{t['state']}] {t['text']}")
        for key in ("files", "pattern", "verify", "subject", "commit"):
            val = t[key]
            if val:
                val = ", ".join(val) if isinstance(val, list) else val
                out.append(f"      {key}: {val}")
    return "\n".join(out)


def cmd_show(args, root: str, out: Emitter) -> int:
    """Read ONE task, or the map of what is there — the whole document only when it is asked
    for by name.

    THE COST THIS ADDRESSES IS THE AGENT'S CONTEXT, NOT I/O. A backend may well have fetched
    the entire document to answer `--task 3.1`, and that is fine — reading a file twice is
    free. What is not free is an executor handed fourteen sections in order to edit one: it
    carries the other thirteen through every remaining turn of its conversation and pays for
    them again on each. So the DEFAULT IS THE INDEX AND NEVER THE DOCUMENT, and `--full`
    exists precisely so that the whole document has to be typed on purpose.

    **Section bodies are `section`'s, not this command's.** That reader is already plural and
    already resolves a `--moment` to its section set, so a second way to ask for a heading
    would be a second spelling of a measured answer — and the two would drift. What is left
    here is what `section` cannot say: WHICH headings and task ids exist (the index), one
    task's line and metadata, and the whole document under a name nobody types by accident.

    An unknown task id is a finding (exit 1), the same as an unknown slug."""
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    info, err = read_one(backend, args.spec, out)
    if err:
        return out.emit_err(args.json, err)

    wanted_tasks = list(args.task or [])
    if args.full and wanted_tasks:
        # Two different cost profiles in one request. Silently letting one win would hand
        # back the whole document to a caller that asked for a slice, which is the exact
        # failure this command exists to make impossible.
        out.emit(args.json,
                 {"ok": False, "code": "sp-conflicting-selection",
                  "message": "--full asks for the whole document and --task for a slice of it "
                             "— pass one or the other"},
                 "error: --full does not combine with --task")
        return 2

    tasks: list[dict] = []
    for ident in wanted_tasks:
        t = _find_task(info["tasks"], ident)
        if not t:
            out.emit(args.json, {"ok": False, "code": "sp-unknown-task", "task": ident,
                                 "message": f"no task '{ident}' in {info['slug']}"},
                     f"error: no task '{ident}' in {info['slug']}")
            return 1
        tasks.append(_task_view(t))

    view = "full" if args.full else ("slice" if tasks else "index")
    obj = {"ok": True, "slug": info["slug"],
           "title": info["frontmatter"].get("title", ""),
           "stage": info["stage"], "phase": info["phase"], "folder": info["folder"],
           "file": info["file"], "view": view}
    if view == "full":
        obj["document"] = info["text"]
        obj["lines"] = len(info["text"].splitlines())
    elif view == "slice":
        obj["tasks"] = tasks
    else:
        obj.update(_show_index(info))
    out.emit(args.json, obj, _show_human(obj, info))
    return 0
