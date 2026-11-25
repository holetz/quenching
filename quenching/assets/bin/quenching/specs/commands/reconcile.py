"""The spec store is the quenching ref, so the archive waits for the merge. This verb
is the one post-merge close every caller runs: conclude resumed after the merge,
/quenching-git merge, the orchestrator after `cq git pr merge`, and reconciliation
at the open of execute, orchestrate and conclude.

It also deletes the build reservation (`refs/quenching/claims/<id>`) of every terminal spec —
archived, or carrying an `outcome` or `merge` record — by compare-and-swap with the sha it read, so
a lease re-acquired in between is never deleted. Reading the leases never fails the reconcile.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess

from quenching.specs import claims
from quenching.specs.backends import open_backend
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.commands import promote
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.sections import section_state


def _release_slot(root: str, branch: dict, remote: str) -> dict | None:
    """Give back the slot holding the archived spec's work branch, through `release` itself, so
    a dirty slot stays held and is reported. None when no slot holds it (a legacy worktree is
    conclude's `retire`)."""
    from quenching.git import slots

    held = [s for s in slots.survey(root)["slots"] if s["branch"] == branch.get("work")]
    if not held:
        return None
    ns = argparse.Namespace(json=True, path=held[0]["path"], branch=None,
                            base=branch.get("base"), remote=remote)
    buf, cwd = io.StringIO(), os.getcwd()
    try:
        os.chdir(root)
        with contextlib.redirect_stdout(buf):
            slots.release(ns)
    finally:
        os.chdir(cwd)
    try:
        got = json.loads(buf.getvalue())
    except ValueError:
        got = {"released": False, "message": buf.getvalue().strip()}
    return {"path": held[0]["path"], "released": bool(got.get("released")),
            "message": got.get("message", "")}


def _terminal(info: dict | None) -> bool:
    front = (info or {}).get("frontmatter") or {}
    return (info or {}).get("phase") == "archive" or bool(front.get("outcome")) \
        or bool(front.get("merge"))


def _release_terminal_claims(backend, root: str, remote: str, write: bool) -> dict:
    """`{available, released}`: one row per lease of a terminal spec — `would-release` without
    `--write`, `released`, or `kept` with the reason. Git that cannot answer is `available: False`."""
    try:
        store = claims.Store(root, remote)
        heads = store.heads()
    except (claims.ClaimError, OSError, subprocess.SubprocessError):
        return {"available": False, "released": []}
    infos = backend.read_specs(sorted(heads)) if heads else {}
    rows = []
    for spec_id, sha in sorted(heads.items()):
        if not _terminal(infos.get(spec_id)):
            continue
        row = {"spec": spec_id, "action": "would-release", "why": ""}
        if write:
            try:
                moved = store.swap(spec_id, None, sha)
            except (claims.ClaimError, OSError, subprocess.SubprocessError) as e:
                row.update(action="kept", why=str(e))
            else:
                row["action"] = "released" if moved else "kept"
                row["why"] = "" if moved else "the lease moved since it was read"
        rows.append(row)
    return {"available": True, "scope": store.scope, "released": rows}


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
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
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
                row["slot"] = _release_slot(root, fm["branch"], remote)
            else:
                row.update(action="needs-human", why=result["message"])
        rows.append(row)
    leases = _release_terminal_claims(backend, root, remote, bool(args.write))
    payload = {"ok": True, "remote": remote, "write": bool(args.write),
               "count": len(rows), "specs": rows, "claims": leases}
    human = (f"reconcile — {len(rows)} merged spec(s) not archived" if rows else
             "reconcile — nothing merged is left unarchived")
    for row in rows:
        human += (f"\n  {row['action']:<13} {row['id']}  {row['title']}  "
                  f"({row['why'] or row['reason']})")
    for lease in leases["released"]:
        human += f"\n  {lease['action']:<13} claim {lease['spec']}" + \
            (f"  ({lease['why']})" if lease["why"] else "")
    out.emit(args.json, payload, human)
    return 0
