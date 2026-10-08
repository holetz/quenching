"""`cq git audit` — the facts the `verifier` agent checks inside a spec's worktree, read with a
fixed argv so the agent needs no `Bash(git …)` grant at all.

A wildcard grant such as `Bash(git -C * status:*)` admits any git command that merely ends in
`status` — `branch -D`, `clean -fdx`, `-c core.fsmonitor=<cmd>` — and `git log:*` admits
`--output=<file>`. Here the agent names a worktree and refs; every git invocation is built in this
module, refs are resolved to commits before use, and the repository's own config cannot run a
command during the read. A REPORT only, exit 0 on any facts; judging them is the verifier's.

`--gate` is the one execution: the worktree's own `scripts/verify_repo.sh`, argv fixed."""
from __future__ import annotations

import os
import subprocess

from quenching.common.git import _git_run
from quenching.common.output import emit, refuse

GATE_SCRIPT = os.path.join("scripts", "verify_repo.sh")
GATE_TIMEOUT_S = 1800
SAFE = ("--no-optional-locks", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null")


def _run(cwd: str, *argv: str) -> tuple[int, str]:
    code, out, _err = _git_run(cwd, *SAFE, *argv)
    return code, out


def _lines(cwd: str, *argv: str) -> list[str]:
    code, out = _run(cwd, *argv)
    return [line for line in out.splitlines() if line] if code == 0 else []


def _registered(cwd: str, path: str) -> bool:
    code, out = _run(cwd, "worktree", "list", "--porcelain")
    if code != 0:
        return False
    want = os.path.realpath(path)
    return any(os.path.realpath(line[len("worktree "):]) == want
               for line in out.splitlines() if line.startswith("worktree "))


def _commit(cwd: str, ref: str) -> str | None:
    if not ref or ref.startswith("-"):
        return None
    code, out = _run(cwd, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{ref}^{{commit}}")
    return out.strip() if code == 0 and out.strip() else None


def _branch_ok(cwd: str, branch: str) -> bool:
    if branch.startswith("-"):
        return False
    return _run(cwd, "check-ref-format", "--branch", branch)[0] == 0


def _gate(worktree: str) -> dict:
    if not os.path.isfile(os.path.join(worktree, GATE_SCRIPT)):
        return {"exit": None, "reason": "absent"}
    try:
        done = subprocess.run(["bash", GATE_SCRIPT], cwd=worktree, capture_output=True,
                              text=True, timeout=GATE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"exit": None, "reason": "timeout"}
    tail = (done.stdout + done.stderr).splitlines()[-20:]
    return {"exit": done.returncode, "tail": tail}


def cmd_audit(args) -> int:
    cwd = os.getcwd()
    worktree = os.path.realpath(args.worktree)
    if not _registered(cwd, worktree):
        return refuse({"code": "audit-worktree-unregistered",
                       "message": f"not a worktree this repository registers: {args.worktree}"},
                      args.json)
    if not _branch_ok(worktree, args.branch):
        return refuse({"code": "audit-ref-invalid", "message": f"not a branch name: {args.branch}"},
                      args.json)
    resolved = {}
    for label, ref in [("base", args.base), ("branch", f"refs/heads/{args.branch}"),
                       *(("sha", s) for s in args.sha)]:
        sha = _commit(worktree, ref)
        if sha is None:
            return refuse({"code": "audit-ref-invalid",
                           "message": f"{label} does not resolve to a commit: {ref}"}, args.json)
        resolved[ref] = sha
    base, tip = resolved[args.base], resolved[f"refs/heads/{args.branch}"]

    payload = {
        "ok": True,
        "worktree": worktree,
        "base": {"ref": args.base, "sha": base},
        "branch": {"ref": args.branch, "sha": tip},
        "status": _lines(worktree, "status", "--porcelain"),
        "stash": _lines(worktree, "stash", "list"),
        "commits": _lines(worktree, "log", "--oneline", f"{base}..{tip}"),
        "changed": _lines(worktree, "diff", "--name-only", f"{base}...{tip}"),
        "ancestry": {s: _run(worktree, "merge-base", "--is-ancestor", resolved[s], tip)[0] == 0
                     for s in args.sha},
        "reflog": {"branch": _lines(worktree, "reflog", "show", "--format=%gs",
                                    f"refs/heads/{args.branch}"),
                   "head": _lines(worktree, "reflog", "show", "--format=%gs", "HEAD")},
    }
    if args.gate:
        payload["gate"] = _gate(worktree)

    lines = [f"worktree: {worktree}", f"branch: {args.branch} ({tip[:12]}) over {args.base}",
             f"commits: {len(payload['commits'])}", f"changed: {len(payload['changed'])} path(s)",
             f"status: {len(payload['status'])} entries", f"stash: {len(payload['stash'])} entries"]
    lines += [f"ancestor {s}: {'yes' if ok else 'NO'}" for s, ok in payload["ancestry"].items()]
    if args.gate:
        lines.append(f"gate exit: {payload['gate']['exit']}")
    emit(args.json, payload, "\n".join(lines))
    return 0
