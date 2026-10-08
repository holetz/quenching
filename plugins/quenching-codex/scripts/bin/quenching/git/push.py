"""`cq git push` — publish one local branch to one remote under its own name, with upstream.

The argv is fixed here: the branch must be a local ref and the remote a configured one, both
checked before git sees them, and the refspec is spelled out (`refs/heads/<b>:refs/heads/<b>`)
so neither can be read as an option or a force. Runs with `audit.SAFE`. Never `--force`, never
`--delete`, never a refspec the caller wrote.

Exit 0 pushed · 1 git refused the push (non-fast-forward, auth) · 2 refusal."""
from __future__ import annotations

import os

from quenching.common.git import _git_run
from quenching.common.output import FINDINGS, OK, emit, refuse
from quenching.git.audit import SAFE, _branch_ok, _commit, _run


def remote_probe(cwd: str, remote: str) -> bool | None:
    """Whether `remote` is configured: True (exit 0), False (exit 2, git's "no such remote" — a
    fact) or None (any other exit: git could not answer, which is neither yes nor no)."""
    if not remote or remote.startswith("-"):
        return False
    code = _run(cwd, "remote", "get-url", "--", remote)[0]
    return True if code == 0 else False if code == 2 else None


def remote_ok(cwd: str, remote: str) -> bool:
    return remote_probe(cwd, remote) is True


def cmd_push(args) -> int:
    cwd = os.getcwd()
    if args.branch.startswith("-") or not _branch_ok(cwd, args.branch):
        return refuse({"code": "git-push-ref-invalid",
                       "message": f"not a branch name: {args.branch}"}, args.json)
    sha = _commit(cwd, f"refs/heads/{args.branch}")
    if sha is None:
        return refuse({"code": "git-push-ref-invalid",
                       "message": f"no local branch named {args.branch}"}, args.json)
    if remote_probe(cwd, args.remote) is None:
        return refuse({"code": "git-push-remote-unreadable",
                       "message": f"git could not read the remote: {args.remote}"}, args.json)
    if not remote_ok(cwd, args.remote):
        return refuse({"code": "git-push-remote-unknown",
                       "message": f"not a configured remote: {args.remote}"}, args.json)
    ref = f"refs/heads/{args.branch}"
    code, _out, err = _git_run(cwd, *SAFE, "push", "--set-upstream", "--porcelain", "--",
                               args.remote, f"{ref}:{ref}")
    if code != 0:
        emit(args.json, {"ok": False, "remote": args.remote, "branch": args.branch,
                         "message": err.strip()}, f"push refused: {err.strip()}")
        return FINDINGS
    emit(args.json, {"ok": True, "remote": args.remote, "branch": args.branch, "sha": sha},
         f"pushed {args.branch} ({sha[:12]}) to {args.remote}")
    return OK
