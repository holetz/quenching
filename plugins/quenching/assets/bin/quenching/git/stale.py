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
from quenching.specs.config import load_config


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
    release = load_config(cwd)["releaseBranch"]
    # `base` and the release branch are permanent by convention, not "safe to delete just
    # because their tip is an ancestor of base" — the ordinary state for a release branch is
    # to sit merged into `base` between releases. `current` is excluded because you cannot
    # delete the branch you are standing on; cleanup (task 4.6) re-checks that at delete time
    # regardless, this list is a report, not a promise nothing else changed since.
    protected = {base, current} | ({release} if release else set())

    reasons: dict[str, set[str]] = {}
    for b in _merged_branches(cwd, base, protected):
        reasons.setdefault(b, set()).add("merged")
    for b in _gone_branches(cwd, protected):
        reasons.setdefault(b, set()).add("gone")
    branches = [{"branch": b, "reasons": sorted(r)} for b, r in sorted(reasons.items())]
    worktrees = _orphan_worktrees(cwd)

    lines = [f"base: {base}"]
    lines.append("stale branches:" if branches else "stale branches: none")
    for b in branches:
        lines.append(f"  {b['branch']} ({', '.join(b['reasons'])})")
    lines.append("orphan worktrees:" if worktrees else "orphan worktrees: none")
    for w in worktrees:
        lines.append(f"  {w['path']} ({w['branch'] or 'detached'})")

    emit(args.json, {"ok": True, "base": base, "staleBranches": branches,
                     "orphanWorktrees": worktrees}, "\n".join(lines))
    return 0
