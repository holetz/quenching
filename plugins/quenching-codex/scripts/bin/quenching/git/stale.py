"""`cq git stale` — branches already merged into the base or whose upstream is gone, and
worktrees git still registers whose directory no longer exists. A REPORT only: nothing here
deletes a branch or removes a worktree — task 4.6's `cleanup` command acts on this list, on
the human's own confirmation, the same split every other destructive step in this plugin
keeps between "what is true" and "what to do about it"."""
from __future__ import annotations

import os

from quenching.common.git import _git
from quenching.common.output import emit
from quenching.git.base import resolve_base


def _merged_branches(cwd: str, base: str, protected: set[str]) -> set[str]:
    out = _git(cwd, "for-each-ref", "--format=%(refname:short)", "refs/heads", "--merged", base)
    return {b for b in out.splitlines() if b and b not in protected}


def _gone_branches(cwd: str, protected: set[str]) -> set[str]:
    out = _git(cwd, "for-each-ref", "--format=%(refname:short)|%(upstream:track)", "refs/heads")
    gone = set()
    for line in out.splitlines():
        name, _, track = line.partition("|")
        if "[gone]" in track and name not in protected:
            gone.add(name)
    return gone


def _merged_remote_branches(cwd: str, base: str, protected: set[str],
                            remote: str = "origin") -> list[dict]:
    """Report fetched remote branches already reachable from ``base``.

    This is deliberately a read of remote-tracking refs. It does not fetch, prune local refs, or
    claim that the server has not changed since the last fetch; cleanup owns the later, confirmed
    delete of a selected server branch.
    """
    prefix = f"{remote}/"
    out = _git(cwd, "for-each-ref", "--format=%(refname:short)",
               f"refs/remotes/{remote}", "--merged", base)
    branches = []
    for ref in out.splitlines():
        if not ref.startswith(prefix):
            continue
        branch = ref[len(prefix):]
        if not branch or branch == "HEAD" or branch in protected:
            continue
        branches.append({"remote": remote, "branch": branch, "reasons": ["merged"]})
    return branches


def _orphan_worktrees(cwd: str) -> list[dict]:
    out = _git(cwd, "worktree", "list", "--porcelain")
    orphans = []
    path = branch = None
    for line in out.splitlines() + [""]:
        if line.startswith("worktree "):
            path = line[len("worktree "):]
        elif line.startswith("branch "):
            branch = line[len("branch "):].removeprefix("refs/heads/")
        elif not line and path is not None:
            if not os.path.isdir(path):
                orphans.append({"path": path, "branch": branch})
            path = branch = None
    return orphans


def cmd_stale(args) -> int:
    cwd = os.getcwd()
    base, _is_default = resolve_base(cwd)
    current = _git(cwd, "branch", "--show-current").strip()
    # `base` is permanent by convention, not "safe to delete just because its tip is an
    # ancestor of base". `current` is excluded because you cannot delete the branch you are
    # standing on; cleanup (task 4.6) re-checks that at delete time regardless, this list is
    # a report, not a promise nothing else changed since.
    protected = {base, current}

    reasons: dict[str, set[str]] = {}
    for b in _merged_branches(cwd, base, protected):
        reasons.setdefault(b, set()).add("merged")
    for b in _gone_branches(cwd, protected):
        reasons.setdefault(b, set()).add("gone")
    branches = [{"branch": b, "reasons": sorted(r)} for b, r in sorted(reasons.items())]
    remote_branches = _merged_remote_branches(cwd, base, protected)
    worktrees = _orphan_worktrees(cwd)

    lines = [f"base: {base}"]
    lines.append("stale branches:" if branches else "stale branches: none")
    for b in branches:
        lines.append(f"  {b['branch']} ({', '.join(b['reasons'])})")
    lines.append("stale remote branches:" if remote_branches else "stale remote branches: none")
    for b in remote_branches:
        lines.append(f"  {b['remote']}/{b['branch']} ({', '.join(b['reasons'])})")
    lines.append("orphan worktrees:" if worktrees else "orphan worktrees: none")
    for w in worktrees:
        lines.append(f"  {w['path']} ({w['branch'] or 'detached'})")

    emit(args.json, {"ok": True, "base": base, "staleBranches": branches,
                     "remoteBranches": remote_branches, "orphanWorktrees": worktrees},
         "\n".join(lines))
    return 0
