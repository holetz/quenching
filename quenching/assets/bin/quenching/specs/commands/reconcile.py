"""The spec store is the quenching ref, so the archive waits for the merge. This verb
is the one post-merge close every caller runs: conclude resumed after the merge,
/quenching-git merge, the orchestrator after `cq git pr merge`, and reconciliation
at the open of execute, orchestrate and conclude.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess

from quenching.specs.backends import open_backend
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.commands import promote
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.sections import section_state


def cmd_reconcile(args, root: str, out: Emitter) -> int:
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    candidates = backend.list_specs("plans")
    # Descriptors do not carry branch records; use the backend's batched snapshot.
    infos = backend.read_specs([s["id"] for s in candidates])
    isolated = [info for info in infos.values() if info and promote.isolated(info)]
    remote = args.remote
    try:
        subprocess.run(["git", "fetch", "--quiet", remote], cwd=root,
                       capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        pass
    rows = []
    for info in isolated:
        merged, reason = promote.merge_evidence(info, root, remote, fetch=False)
        if not merged:
            continue
        fm = info["frontmatter"]
        row = {"id": info["id"], "title": fm.get("title") or "",
               "work": fm["branch"]["work"], "reason": reason,
               "action": "would-archive", "why": ""}
        if section_state(info["sections"], "Outcome") != "filled":
            row.update(action="needs-human", why="merged but ## Outcome is not written")
        elif args.write:
            close_args = argparse.Namespace(json=True, spec=info["id"], to="archive",
                                            outcome="done", force=False, dry_run=False)
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    code = promote.cmd_promote(close_args, root, Emitter())
                result = json.loads(buf.getvalue())
            except BackendRefusal as refusal:
                code, result = 2, refusal.err
            if code == 0:
                row["action"] = "archived"
            else:
                row.update(action="needs-human", why=result["message"])
        rows.append(row)
    payload = {"ok": True, "remote": remote, "write": bool(args.write),
               "count": len(rows), "specs": rows}
    human = (f"reconcile — {len(rows)} merged spec(s) not archived" if rows else
             "reconcile — nothing merged is left unarchived")
    for row in rows:
        human += (f"\n  {row['action']:<13} {row['id']}  {row['title']}  "
                  f"({row['why'] or row['reason']})")
    out.emit(args.json, payload, human)
    return 0
