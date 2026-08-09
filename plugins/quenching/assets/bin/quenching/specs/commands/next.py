"""`next` — THE single next action, and the ranking behind `--front`.

The ranking lives here and nowhere else: four lexicographic factors, plus a live `plan/<slug>`
ref that outranks all four in both directions."""
from __future__ import annotations

import datetime
import json

from quenching.common.dates import today
from quenching.common.git import _git
from quenching.specs.backends import open_backend
from quenching.specs.backends.base import SpecBackend
from quenching.specs.commands.output import display_locator, emit, emit_err, read_one
from quenching.specs.parse import derive_info, titleize
from quenching.specs.parse.derive import derive_stage
from quenching.specs.parse.sections import ready_report
from quenching.specs.parse.tasks import _files_bad_annotation, task_progress
from quenching.specs.schema import load_schema


CRITICALITY_RANK = {"critical": 0, "high": 1, "medium": 2, "normal": 2, "low": 3}


def _priority_rank(rec) -> tuple[float, str]:
    """A spec's human-assigned urgency as one comparable number, plus how it was read.

    `level` is the field triage writes and the one that ranks; `criticality` is a coarse
    fallback so a partially-filled record still ranks instead of silently sorting last.
    No record at all sorts after every record — never before."""
    if not isinstance(rec, dict):
        return (float("inf"), "")
    lvl = str(rec.get("level", "")).strip()
    if lvl:
        try:
            return (float(lvl), f"priority level {lvl}")
        except ValueError:
            pass
    crit = str(rec.get("criticality", "")).strip().lower()
    if crit in CRITICALITY_RANK:
        return (float(CRITICALITY_RANK[crit]), f"criticality {crit}")
    return (float("inf"), "")


def _days_since(date: str) -> int:
    try:
        d = datetime.date.fromisoformat(date)
    except ValueError:
        return 0
    return max(0, (datetime.date.fromisoformat(today()) - d).days)


def _git_refs(root: str) -> tuple[set[str], str | None]:
    """Every local branch, and the one checked out. Two calls for the WHOLE front, never
    one per spec — ranking twenty specs must not cost forty subprocesses.

    No git, or no repo → an empty set and no current branch, which ranks exactly as today."""
    heads = {l.strip() for l in
             _git(root, "for-each-ref", "--format=%(refname:short)",
                  "refs/heads").splitlines() if l.strip()}
    current = _git(root, "rev-parse", "--abbrev-ref", "HEAD").strip() or None
    return heads, (current if current and current != "HEAD" else None)


def _work_ref(fm: dict, slug: str) -> str:
    """The branch this spec's work would live on.

    The `branch:` record when one was stamped, else the default `plan/<slug>` — because a
    human may have cut the branch by hand, with no record at all. The record alone is NEVER
    the signal: what counts is whether the ref is alive."""
    rec = fm.get("branch")
    work = str(rec.get("work", "")).strip() if isinstance(rec, dict) else ""
    return work or f"plan/{slug}"


def _candidate(backend: SpecBackend, s: dict, schema: dict, heads: set[str],
               current: str | None, root: str) -> dict:
    # ASKED OF THE BACKEND, never of the path. Against GitHub the locator is an issue URL, so
    # every candidate derived from an EMPTY document — the whole front ranked as `captured`
    # with no title, no tasks and nothing executing, and `/specs:continue` handed out its
    # single next action from exactly that.
    info, rerr = backend.read_spec(s["slug"])
    unreadable = (rerr or {}).get("code")
    if info is None:
        # Ambiguous slug — the slug came from the listing, so it cannot be unknown, and
        # `validate` names it `sp-duplicate-slug`. The candidate SURVIVES, derived from an
        # empty document exactly as `list` keeps its row: dropping it would hide a spec from
        # the ranking, and `unreadable` says why it ranks as an empty one.
        info = derive_info(s, "")
    fm, sections, tasks = info["frontmatter"], info["sections"], info["tasks"]
    checked, blocked, total = task_progress(tasks)
    stage = derive_stage(s, sections, fm, tasks, schema)
    ready = ready_report({"sections": sections}, schema)
    prank, pwhy = _priority_rank(fm.get("priority"))
    progress = (checked / total) if total else 0.0
    executing = stage == "executing"
    work = _work_ref(fm, s["slug"])
    live = work in heads
    # A record whose ref is gone stops counting: the branch was merged or deleted, so the
    # spec is no more "in flight" than one that never had a branch at all.
    on_it = live and work == current
    branch_rank = 0 if on_it else (2 if live else 1)
    return {
        "slug": s["slug"], "folder": s["folder"], "file": s["file"], "date": info["date"],
        "title": fm.get("title", titleize(s["slug"])), "stage": stage,
        "tasks": {"checked": checked, "blocked": blocked, "total": total},
        "progress": round(progress, 3),
        "readyGateMet": ready["ok"],
        "approved": fm.get("approved") or None,
        "priority": fm.get("priority") or None,
        "ageDays": _days_since(info["date"]),
        "unreadable": unreadable,
        "branch": {"work": work, "live": live, "current": on_it},
        "path": display_locator(s["path"], root),
        "_key": (branch_rank, 0 if executing else 1, -progress, prank,
                 info["date"], s["slug"]),
        "_why": pwhy,
        "_executing": executing,
    }


def _rank_reason(c: dict) -> str:
    """Why this candidate sits where it does — the ONE dominant factor, not a formula."""
    t = c["tasks"]
    if c["branch"]["current"]:
        return f"you are on this branch ({c['branch']['work']})"
    if c["branch"]["live"]:
        return f"in flight on `{c['branch']['work']}` — check it out to continue"
    if c["_executing"]:
        r = f"executing — {t['checked']}/{t['total']} tasks done"
        if t["blocked"]:
            r += f", {t['blocked']} blocked"
        return r
    if c["_why"]:
        return f"{c['_why']} — {c['stage']}"
    if c["readyGateMet"]:
        return f"ready to build, untouched for {c['ageDays']}d"
    return f"{c['stage']}, {c['ageDays']}d old"


def _next_front(args, root: str) -> int:
    """The ranked candidate list — THE only place ranking logic lives.

    Four factors, lexicographic and in this order:
      1. executing first     finish what is already started before opening something new
      2. closest to done     among those, the one nearest the end
      3. priority            the human's ranking, when triage has written one
      4. age                 oldest first, so nothing rots quietly

    Factor 2 is harmless for everything else: a spec with no ticked task scores 0, so the
    whole non-executing set ties there and falls through to priority — which is exactly the
    intent, without a special case.

    A LIVE `plan/<slug>` ref outranks all four, in both directions: the branch you are
    standing on goes to the top, and one alive but not checked out is demoted below the
    untouched specs — offering it would send a second run at work already under way
    somewhere else. The signal is the ref, never the `branch:` record: a human may cut a
    branch with no record, and a record outlives the branch it names."""
    schema = load_schema()
    heads, current = _git_refs(root)
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    cands = [_candidate(backend, s, schema, heads, current, root)
             for s in backend.list_specs("plans")]
    cands.sort(key=lambda c: c["_key"])
    ranked = []
    for c in cands:
        c = dict(c)
        c["reason"] = _rank_reason(c)
        for k in ("_key", "_why", "_executing"):
            c.pop(k)
        ranked.append(c)

    # When nothing carries a priority record and nothing is in flight, the order is age
    # alone — which is an ordering, not a judgment. Say so rather than implying a ranking
    # that was never made.
    prioritized = [c for c in ranked if c["priority"]]
    # A live branch IS in flight, whether or not any task has been ticked yet — and it has
    # already reordered the list, so claiming the order is age alone would be false.
    in_flight = [c for c in ranked if c["stage"] == "executing" or c["branch"]["live"]]
    needs_triage = bool(ranked) and not prioritized and not in_flight and len(ranked) > 1

    obj = {"ok": True, "root": root, "count": len(ranked),
           "top": ranked[0]["slug"] if ranked else None,
           "needsTriage": needs_triage,
           "candidates": ranked}
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0
    if not ranked:
        print(f"no active specs under {root} — nothing to continue")
        return 0
    print(f"specs front — {len(ranked)} active, ranked")
    for i, c in enumerate(ranked, 1):
        print(f"  {i}. {c['slug']:<32} {c['reason']}")
    if needs_triage:
        print("\n  nothing is in flight and nothing carries a priority record — this order "
              "is age alone.\n  `specs.py`-driven triage would give it something to stand on.")
    return 0


def cmd_next(args, root: str) -> int:
    """THE single next action, so a skill never infers state from prose.

    In `plans/` the ladder is one chain, because the folder no longer splits it: fill the
    ready gate, then work the tasks, then close out. A `[!]` task is SKIPPED — it already
    has an honest reason recorded and re-offering it forever is what the attempt budget
    was clumsily trying to prevent.

    Reaching the ready gate does NOT stop the ladder to demand approval. Refusing here
    would rebuild the `promote` this fold removed; `execute` asks for the stamp inline,
    and `approved` rides along in the payload so it can.

    With `--front` the question is the other one — WHICH spec — and that is answered by
    `_next_front`."""
    if args.front:
        return _next_front(args, root)
    if not args.spec:
        emit(args.json, {"ok": False, "code": "sp-no-target",
                         "message": "pass --spec <slug> for one spec's next action, "
                                    "or --front for the ranked candidate list"},
             "error: pass --spec <slug>, or --front")
        return 1
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = read_one(backend, args.spec)
    if err:
        return emit_err(args.json, err)
    base = {"slug": info["slug"], "phase": info["phase"], "folder": info["folder"],
            "stage": info["stage"], "verification": info["verification"],
            "approved": info["frontmatter"].get("approved") or None,
            "blocked": [{"id": t["id"], "text": t["text"], "reason": t["reason"]}
                        for t in info["tasks"] if t["blocked"]]}

    if info["phase"] == "plans":
        ready = ready_report(info)
        if not ready["ok"]:
            want = (ready["missing"] + ready["malformed"])[0]
            remaining = len(ready["missing"]) + len(ready["malformed"]) - 1
            obj = {"ok": True, "action": "write_section", "heading": want, **base,
                   "missing": ready["missing"], "malformed": ready["malformed"],
                   "message": f"write ## {want}"
                              + (f" (then {remaining} more)" if remaining else "")
                              + " to reach the ready gate"}
            emit(args.json, obj, obj["message"])
            return 0
        openable = [t for t in info["tasks"] if not t["checked"] and not t["blocked"]]
        if openable:
            t = openable[0]
            bad = [e for e in t["files"] if _files_bad_annotation(e)]
            if bad:
                # The consumer of `files:` is an executor who cannot tell an invented
                # piece from a path the task will create — refuse HERE, at the door,
                # never hand the list over.
                return emit_err(args.json, {
                    "code": "sp-files-annotation",
                    "message": f"task {t['id']} declares files entries that are not "
                               f"paths: {', '.join(repr(b) for b in bad)} — remove the "
                               f"comment; `(new)` is the only reserved `files:` annotation"})
            obj = {"ok": True, "action": "implement_task", "task": t["id"], "text": t["text"],
                   "verify": t["verify"], "files": t["files"], "pattern": t["pattern"],
                   "cwd": t["cwd"],
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
