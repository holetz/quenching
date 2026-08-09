"""`promote` — the one remaining transition, `plans/` -> `archive/`."""
from __future__ import annotations

import os

from quenching.specs.backends import open_backend
from quenching.specs.commands.output import emit, emit_err, read_one
from quenching.specs.commands.read import _next_phase
from quenching.specs.parse import PHASES
from quenching.specs.parse.fields import set_frontmatter_key
from quenching.specs.parse.sections import gate_report
from quenching.specs.schema import OUTCOMES


def cmd_promote(args, root: str) -> int:
    """The one remaining transition: `plans/` -> `archive/`, closing a spec out.

    v3 has a single hop. The `backlog/` -> `ready/` promote is gone with the folders — it
    recorded that a human said go, and that is now `approved:` in frontmatter, which no
    file move is needed to express. What is left refuses (exit 2) with the missing list
    rather than warning, because a gate that warns is not a gate.

    The file is MOVED, never renamed: the date prefix was stamped at capture and the
    basename is the spec's identity for its whole lifecycle. Git detects the rename by
    content, so `git log --follow` reads as one history without this tool shelling out."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = read_one(backend, args.spec)
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
    if dest == info["phase"]:
        emit(args.json,
             {"ok": False, "code": "sp-same-phase", "slug": info["slug"], "phase": dest,
              "message": f"'{info['slug']}' is already in phase {dest}"},
             f"refused: '{info['slug']}' is already in phase {dest}")
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

    dest_path = os.path.join(root, dest, info["file"])
    rel = f"{dest}/{info['file']}"
    if args.dry_run:
        emit(args.json,
             {"ok": True, "dryRun": True, "slug": info["slug"], "from": info["folder"],
              "to": dest, "outcome": outcome, "dest": rel,
              "warn": gates["warn"]},
             f"dry-run: would move {info['folder']}/{info['file']} → {rel}" +
             (f"  (outcome: {outcome})" if outcome else ""))
        return 0
    if os.path.exists(dest_path):
        emit(args.json, {"ok": False, "code": "sp-dest-exists", "dest": rel,
                         "message": f"{rel} already exists"},
             f"error: {rel} already exists")
        return 1
    # The outcome is stamped BEFORE the hop, so the document that moves already carries it —
    # a backend whose move is not atomic must never be able to land an archived spec with no
    # outcome on it.
    if outcome:
        backend.write_spec(info, set_frontmatter_key(info["text"], "outcome", outcome))
    backend.move_spec(info, dest)
    emit(args.json,
         {"ok": True, "slug": info["slug"], "from": info["folder"], "to": dest,
          "outcome": outcome, "dest": rel, "warn": gates["warn"]},
         f"promoted '{info['slug']}': {info['folder']}/ → {rel}" +
         (f"  (outcome: {outcome})" if outcome else "") +
         ("".join(f"\n  warning: ## {h} is empty" for h in gates["warn"])))
    return 0
