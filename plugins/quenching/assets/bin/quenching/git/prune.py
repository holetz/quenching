"""`cq git prune` — delete ONE item `cq git stale` reports, and nothing it does not.

The report is re-read here, at delete time, so a name the caller passes is acted on only when
the fresh report still lists it under the matching class. The deletes are the safe forms only —
`branch -d`, `worktree remove`, `push --delete` of a reported remote branch leased on the sha
the report read (a tip that moved since is refused; a branch already gone from the remote only loses its
tracking ref) — never `-D`, a plain `--force` or a
refspec the caller wrote. Runs with `audit.SAFE`.

Exit 0 deleted · 1 git refused (not fully merged, dirty worktree) and the item stands ·
2 refusal: not in the report."""
from __future__ import annotations

import os

from quenching.common.git import _git, _git_run
from quenching.common.output import FINDINGS, OK, emit, refuse
from quenching.git.audit import SAFE
from quenching.git.push import remote_ok
from quenching.git.stale import stale_report


def _same_path(a: str | None, b: str) -> bool:
    return bool(a) and (a == b or os.path.realpath(a) == os.path.realpath(b))


def cmd_prune(args) -> int:
    cwd = os.getcwd()
    if args.remote_branch is not None and not remote_ok(cwd, args.remote):
        return refuse({"code": "git-prune-remote-unknown",
                       "message": f"not a configured remote: {args.remote}"}, args.json)
    report = stale_report(cwd, args.remote)
    if args.branch is not None:
        kind, target = "branch", args.branch
        listed = any(b["branch"] == target for b in report["staleBranches"])
        argv = ("branch", "-d", "--", target)
    elif args.worktree is not None:
        kind, target = "worktree", args.worktree
        listed = any(_same_path(w["path"], target) for w in report["orphanWorktrees"])
        argv = ("worktree", "remove", "--", target)
    else:
        kind, target = "remote-branch", args.remote_branch
        listed = any(b["branch"] == target and b["remote"] == args.remote
                     for b in report["remoteBranches"])
        seen = _git(cwd, "rev-parse", "--verify", "--quiet",
                    f"refs/remotes/{args.remote}/{target}").strip()
        argv = ("push", "--delete", "--porcelain",
                f"--force-with-lease=refs/heads/{target}:{seen}",
                "--", args.remote, f"refs/heads/{target}")
    if not listed:
        return refuse({"code": "git-prune-not-reported",
                       "message": f"`cq git stale` does not report the {kind} {target}"},
                      args.json)
    if kind == "remote-branch" and not seen:
        return refuse({"code": "git-prune-no-lease",
                       "message": f"no tracking ref to lease for {args.remote}/{target}"},
                      args.json)
    code, out, err = _git_run(cwd, *SAFE, *argv)
    payload = {"ok": code == 0, "kind": kind, "target": target, "remote": args.remote}
    if code != 0 and kind == "remote-branch":
        gone, _o, _e = _git_run(cwd, *SAFE, "ls-remote", "--exit-code", "--heads",
                                args.remote, f"refs/heads/{target}")
        if gone == 2:
            code, _o, err = _git_run(cwd, *SAFE, "branch", "-dr", f"{args.remote}/{target}")
            if code == 0:
                payload.update(ok=True, message="already gone on the remote; tracking ref removed")
                emit(args.json, payload, f"pruned {kind} {target} (already gone on the remote)")
                return OK
    if code != 0:
        reason = "\n".join(x for x in (out.strip(), err.strip()) if x)
        payload["message"] = reason
        emit(args.json, payload, f"{kind} {target} refused: {reason}")
        return FINDINGS
    emit(args.json, payload, f"pruned {kind} {target}")
    return OK
