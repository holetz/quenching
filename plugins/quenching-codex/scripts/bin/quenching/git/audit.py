"""`cq git audit` — the facts the `verifier` agent checks inside a spec's worktree, read with a
fixed argv so the agent needs no `Bash(git …)` grant at all.

A wildcard grant such as `Bash(git -C * status:*)` admits any git command that merely ends in
`status` — `branch -D`, `clean -fdx`, `-c core.fsmonitor=<cmd>` — and `git log:*` admits
`--output=<file>`. Here the agent names a worktree and refs; every git invocation is built in this
module, refs are resolved to commits before use, and the repository's own config cannot run a
command during the read: the `filter.<x>` drivers it declares are blanked before `status`, which
does not descend into submodules (their own config is not ours to blank), and `log.showSignature`
is forced off so `gpg.program` never runs. A
REPORT only, exit 0 on any facts; judging them is the verifier's. Nothing here executes the
audited branch's code: the gate is certified by CI before the merge, never by this verb."""
from __future__ import annotations

import os
import re
from quenching.common.git import _git_run
from quenching.common.output import emit, refuse

FILTER_KEY = re.compile(r"^filter\.(.+)\.(clean|smudge|process)$")
SAFE = ("--no-optional-locks", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
        "-c", "log.showSignature=false")


def _run(cwd: str, *argv: str) -> tuple[int, str]:
    code, out, _err = _git_run(cwd, *SAFE, *argv)
    return code, out


def _lines(cwd: str, *argv: str) -> list[str]:
    code, out = _run(cwd, *argv)
    return [line for line in out.splitlines() if line] if code == 0 else []


def _reflog(cwd: str, ref: str) -> list[str]:
    """The reflog subjects of `ref`, newest first, minus the `reset` entries that moved nothing:
    a reset whose sha equals the next older entry's rewrote no history (`git merge --abort` logs
    `reset: moving to HEAD`). A reset that moved the ref stays, so the verifier still sees it."""
    entries = [line.split(" ", 1) + [""] for line in _lines(cwd, "reflog", "show", "--format=%H %gs", ref)]
    return [e[1] for i, e in enumerate(entries)
            if e[1] and not (e[1].startswith("reset:") and i + 1 < len(entries)
                             and entries[i + 1][0] == e[0])]


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


def _filter_overrides(cwd: str) -> list[str]:
    """`-c` pairs that blank every `filter.<x>` driver the repository config declares, so the
    status cannot run one against the branch's `.gitattributes`. `required` is cleared too: a
    required filter with no command would die instead of being skipped."""
    code, out = _run(cwd, "config", "--name-only", "--get-regexp", r"^filter\..*\.(clean|smudge|process)$")
    argv: list[str] = []
    if code != 0:
        return argv
    for key in out.splitlines():
        m = FILTER_KEY.match(key.strip())
        if m:
            argv += ["-c", f"filter.{m.group(1)}.{m.group(2)}=",
                     "-c", f"filter.{m.group(1)}.required=false"]
    return argv


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
        "status": _lines(worktree, *_filter_overrides(worktree), "status", "--porcelain", "--ignore-submodules=all"),
        "stash": _lines(worktree, "stash", "list"),
        "commits": _lines(worktree, "log", "--oneline", f"{base}..{tip}"),
        "changed": _lines(worktree, "diff", "--name-only", f"{base}...{tip}"),
        "ancestry": {s: _run(worktree, "merge-base", "--is-ancestor", resolved[s], tip)[0] == 0
                     for s in args.sha},
        "reflog": {"branch": _reflog(worktree, f"refs/heads/{args.branch}"),
                   "head": _reflog(worktree, "HEAD")},
    }

    lines = [f"worktree: {worktree}", f"branch: {args.branch} ({tip[:12]}) over {args.base}",
             f"commits: {len(payload['commits'])}", f"changed: {len(payload['changed'])} path(s)",
             f"status: {len(payload['status'])} entries", f"stash: {len(payload['stash'])} entries"]
    lines += [f"ancestor {s}: {'yes' if ok else 'NO'}" for s, ok in payload["ancestry"].items()]
    emit(args.json, payload, "\n".join(lines))
    return 0
