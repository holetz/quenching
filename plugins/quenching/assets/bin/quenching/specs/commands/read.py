"""The report verbs — `list`, `status`, and the write-only `export` dump.

Three readers over the same derivation: the whole front by folder and derived stage, ONE spec's
sections/records/gates, and the canonical markdown written to disk for the day an external
backend is lost."""
from __future__ import annotations

import json
import os

from quenching.specs.backends import open_backend
from quenching.specs.commands.output import (announced, display_locator, emit, emit_err,
                                             read_one, receipt_line)
from quenching.specs.parse import PHASES, derive_info, titleize
from quenching.specs.parse.records import spec_records
from quenching.specs.parse.sections import (gate_report, ready_report, section_state,
                                            stray_headings)
from quenching.specs.parse.spec import LEGACY_PHASES, PHASE_DIRS
from quenching.specs.parse.tasks import task_progress
from quenching.specs.schema import canonical_headings, load_schema


def cmd_list(args, root: str) -> int:
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    specs = backend.list_specs()
    rows = []
    for s in specs:
        # ASKED OF THE BACKEND, never of the path. This was the last command reading
        # `read_text(s["path"])` directly, which worked only because the files backend's
        # locator happens to be a filesystem path — against GitHub it is an issue URL, and
        # `list` would have reported every spec as empty rather than failing.
        info, rerr = backend.read_spec(s["slug"])
        if rerr or info is None:
            # The only refusal reachable here is an ambiguous slug — the slug came from the
            # listing, so it cannot be unknown — and `list` is exactly the command a human
            # runs to SEE that duplicate. The row survives, derived from an empty document
            # so every field still comes from the one shared derivation, and `unreadable`
            # says so rather than letting the spec look empty. `validate` names it
            # sp-duplicate-slug.
            info, unreadable = derive_info(s, ""), (rerr or {}).get("code")
        else:
            unreadable = None
        checked, blocked, total = task_progress(info["tasks"])
        rows.append({
            "slug": s["slug"], "phase": s["phase"], "folder": s["folder"],
            "legacy": s["legacy"], "file": s["file"], "date": info["date"],
            "title": info["frontmatter"].get("title", titleize(s["slug"])),
            "stage": info["stage"],
            "outcome": info["frontmatter"].get("outcome") or None,
            # The seven records, on every row. Without them a caller that wants the front's
            # rankings — `triage` reading `priority`, `status` narrating a spec's history —
            # has to open each file itself, which is a path read and so only works while the
            # backend happens to be `files`.
            "records": spec_records(info["frontmatter"]),
            "unreadable": unreadable,
            "tasks": {"checked": checked, "blocked": blocked, "total": total},
            "path": display_locator(s["path"], root),
        })
    if args.json:
        print(json.dumps({"ok": True, "root": root, "count": len(rows), "specs": rows},
                         indent=2, ensure_ascii=False))
        return 0
    if not rows:
        print(f"no specs on the {backend.name} front")
        return 0
    print(f"specs — {backend.name} front ({len(rows)})")
    for folder in PHASE_DIRS:
        group = [r for r in rows if r["folder"] == folder]
        if not group:
            continue
        legacy = " (v2 — `specs.py migrate` folds it into plans/)" \
            if folder in LEGACY_PHASES else ""
        print(f"\n  {folder}/{legacy}")
        for r in group:
            prog = (f"  {r['tasks']['checked']}/{r['tasks']['total']}"
                    if r["tasks"]["total"] else "")
            blk = f" · {r['tasks']['blocked']} blocked" if r["tasks"]["blocked"] else ""
            oc = f" · {r['outcome']}" if r["outcome"] else ""
            un = f" · {r['unreadable']} (nothing derived)" if r["unreadable"] else ""
            print(f"    {r['date']}  {r['slug']:<28} [{r['stage']}]{prog}{blk}{oc}{un}")
    return 0


def _next_phase(phase: str, schema: dict | None = None) -> str | None:
    seq = (schema or load_schema()).get("promote", {}).get("sequence", list(PHASES))
    return seq[seq.index(phase) + 1] if phase in seq and seq.index(phase) + 1 < len(seq) else None


def cmd_status(args, root: str) -> int:
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = read_one(backend, args.spec)
    if err:
        return emit_err(args.json, err)
    checked, blocked, total = task_progress(info["tasks"])
    dest = _next_phase(info["phase"])
    gates = gate_report(info, dest) if dest else None
    ready = ready_report(info) if info["phase"] == "plans" else None
    sections = [{"heading": h, "state": section_state(info["sections"], h)}
                for h in canonical_headings()]
    records = spec_records(info["frontmatter"])
    obj = {
        "ok": True, "slug": info["slug"], "title": info["frontmatter"].get("title", ""),
        "phase": info["phase"], "folder": info["folder"], "legacy": info["legacy"],
        "stage": info["stage"], "file": info["file"],
        "date": info["date"], "verification": info["verification"],
        # every human-judgment record in one place and in schema order, so `conclude` and
        # `continue` read state instead of re-parsing the file
        "records": records,
        "ready": ready,
        "sections": sections,
        "strays": stray_headings(info["sections"]),
        "tasks": {"checked": checked, "blocked": blocked, "total": total,
                  "blockedTasks": [{"id": t["id"], "text": t["text"], "reason": t["reason"]}
                                   for t in info["tasks"] if t["blocked"]],
                  "subjects": [{"id": t["id"], "subject": t["subject"]}
                               for t in info["tasks"] if t["subject"]],
                  "commits": [{"id": t["id"], "commit": t["commit"]}
                              for t in info["tasks"] if t["commit"]]},
        "promote": gates,
        "path": display_locator(info["path"], root),
    }
    if args.json:
        print(json.dumps(announced(obj), indent=2, ensure_ascii=False))
        return 0
    print(receipt_line(), end="")
    print(f"{info['slug']} — {obj['title']}")
    print(f"  {info['folder']}/{info['file']}  [{info['stage']}]  "
          f"verification: {info['verification']}")
    if total:
        print(f"  tasks: {checked}/{total} complete" +
              (f" · {blocked} blocked" if blocked else ""))
    for s in sections:
        mark = {"filled": "✓", "empty": "!", "absent": "·"}[s["state"]]
        print(f"    {mark} ## {s['heading']}")
    if obj["strays"]:
        print(f"  strays: {', '.join(obj['strays'])}")
    if ready:
        if not ready["ok"]:
            print(f"  ready gate: missing {', '.join(ready['missing'] + ready['malformed'])}")
        elif not records.get("approved"):
            print("  ready gate: met — not approved (execute stamps `approved:` inline)")
        else:
            print(f"  ready gate: met · approved {records['approved']}")
    held = [(k, v) for k, v in records.items() if v]
    if held:
        print("  records:")
        for k, v in held:
            if isinstance(v, dict):
                v = ", ".join(f"{kk}: {vv}" for kk, vv in v.items())
            print(f"    {k + ':':<10} {v}")
    if obj["tasks"]["subjects"]:
        print(f"  subjects: {len(obj['tasks']['subjects'])} task(s) carry one")
    if obj["tasks"]["commits"]:
        print(f"  commits: {len(obj['tasks']['commits'])} task(s) carry an older sha")
    if gates:
        if gates["ok"]:
            print(f"  promote → {dest}/: ready")
        else:
            if gates["missing"]:
                print(f"  promote → {dest}/: missing {', '.join(gates['missing'])}")
            if gates["malformed"]:
                print(f"  promote → {dest}/: empty (malformed) {', '.join(gates['malformed'])}")
    return 0


def cmd_export(args, root: str) -> int:
    """Dump the canonical markdown of one spec, or every spec, to disk — write-only.

    THE MITIGATION `## Risks` NAMES FOR LOSING AN EXTERNAL BACKEND, AND NOTHING MORE. Nothing
    in this tool reads the dump back and nothing keeps it in sync with the backend, so it is
    never a second store — a stale copy on disk cannot silently outrank the backend the way a
    cache could. `info["text"]` is the same canonical document every other command derives
    from and shows under `show --full`; this command only adds the write to disk."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    slugs = [s["slug"] for s in backend.list_specs()] if args.all else [args.spec]
    written = []
    for slug in slugs:
        info, rerr = backend.read_spec(slug)
        if rerr:
            return emit_err(args.json, rerr)
        dest = os.path.join(args.out, info["folder"], info["file"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(info["text"])
        written.append(dest)
    obj = {"ok": True, "out": args.out, "count": len(written), "files": written}
    human = f"exported {len(written)} spec(s) to {args.out}/\n" + \
            "\n".join(f"  {w}" for w in written)
    emit(args.json, obj, human)
    return 0
