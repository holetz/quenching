"""`cq git state` — the checkout facts the git commands read before they act: the current branch,
the porcelain status, the staged paths, the stash entries and the remotes. One fixed argv, run with `audit.SAFE` under
`audit._inert_env` — the repository's `filter.<x>` drivers blanked and the lazy fetch off — so a caller needs no `Bash(git …)` grant to read
them. A REPORT only, exit 0 on any facts."""
from __future__ import annotations

import os

from quenching.common.output import emit, refuse
from quenching.git.audit import _inert_env, _lines, _run


def cmd_state(args) -> int:
    cwd = os.getcwd()
    env = _inert_env(cwd)
    code, top = _run(cwd, "rev-parse", "--show-toplevel", env=env)
    if code != 0:
        return refuse({"code": "git-state-not-repository",
                       "message": "the current directory is not inside a git repository"},
                      args.json)
    remotes = {}
    for name in _lines(cwd, "remote", env=env):
        code, url = _run(cwd, "remote", "get-url", "--", name, env=env)
        remotes[name] = url.strip() if code == 0 else None
    payload = {
        "ok": True,
        "root": top.strip(),
        "branch": "".join(_lines(cwd, "branch", "--show-current", env=env)) or None,
        "status": _lines(cwd, "status", "--porcelain", "--ignore-submodules=all", env=env),
        "staged": _lines(cwd, "diff", "--cached", "--name-only", env=env),
        "stash": _lines(cwd, "stash", "list", env=env),
        "remotes": remotes,
    }
    human = [f"branch: {payload['branch'] or '(detached)'}",
             f"status: {len(payload['status'])} entries", f"staged: {len(payload['staged'])} path(s)",
             f"stash: {len(payload['stash'])} entries",
             *(f"remote {n}: {u}" for n, u in remotes.items())]
    emit(args.json, payload, "\n".join(human))
    return 0
