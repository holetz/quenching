"""`cq git stale` — branches already merged into the base or whose upstream is gone, and
worktrees git still registers whose directory no longer exists. A REPORT only: nothing here
deletes a branch or removes a worktree — task 4.6's `cleanup` command acts on this list, on
the human's own confirmation, the same split every other destructive step in this plugin
keeps between "what is true" and "what to do about it"."""
from __future__ import annotations

import json
import os
import subprocess

from quenching.common.config import detect_provider
from quenching.common.git import _git
from quenching.common.output import emit
from quenching.git.base import resolve_base
from quenching.session.worktrees import worktree_branch as _worktree_branch
from quenching.session.worktrees import worktree_gitdir as _worktree_gitdir

UNREGISTERED_WORKTREES_KEY = "unregisteredWorktrees"


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


def _unregistered_worktrees(cwd: str) -> list[dict]:
    common = _git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    if not common:
        return []
    common = os.path.realpath(common)
    registered = set()
    for line in _git(cwd, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            registered.add(os.path.realpath(line[len("worktree "):]))

    siblings = os.path.dirname(os.path.dirname(common))
    found = []
    try:
        entries = sorted(os.scandir(siblings), key=lambda entry: entry.name)
    except OSError:
        return []
    for entry in entries:
        if not entry.is_dir(follow_symlinks=False):
            continue
        path = os.path.realpath(entry.path)
        if path in registered:
            continue
        git_file = os.path.join(entry.path, ".git")
        if not os.path.isfile(git_file):
            continue
        gitdir = _worktree_gitdir(git_file)
        if not gitdir:
            continue
        try:
            belongs = os.path.commonpath((gitdir, common)) == common and gitdir != common
        except ValueError:
            belongs = False
        if belongs:
            found.append({"path": path, "branch": _worktree_branch(gitdir),
                          "size": _directory_size(path)})
    return found


def _directory_size(path: str) -> int | None:
    size = 0
    try:
        for root, directories, files in os.walk(path, followlinks=False):
            for name in [*directories, *files]:
                try:
                    entry = os.lstat(os.path.join(root, name))
                    size += (getattr(entry, "st_blocks", 0) * 512
                             or entry.st_size)
                except OSError:
                    continue
    except OSError:
        return None
    return size


def _checked_out_branches(cwd: str) -> set[str]:
    out = _git(cwd, "worktree", "list", "--porcelain")
    return {line[len("branch "):].removeprefix("refs/heads/")
            for line in out.splitlines() if line.startswith("branch ")}


def _open_pr_heads(cwd: str) -> set[str] | None:
    """Head branches of open PRs, or None when the lookup is unavailable (no `gh`/`az`, no
    host). An Azure DevOps origin is read with `az repos pr list`, any other with `gh`."""
    try:
        provider = detect_provider(cwd)[0]
    except Exception:  # an unreadable origin keeps the GitHub route
        provider = None
    if provider == "azure-boards":
        argv = ["az", "repos", "pr", "list", "--status=active", "--top=500", "--detect=true",
                "--output=json"]
        key = "sourceRefName"
    else:
        argv = ["gh", "pr", "list", "--state", "open", "--limit", "500", "--json", "headRefName"]
        key = "headRefName"
    try:
        done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=20)
        if done.returncode != 0:
            return None
        return {row[key].removeprefix("refs/heads/") for row in json.loads(done.stdout)}
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError,
            AttributeError):
        return None


def _local_branches(cwd: str) -> set[str]:
    out = _git(cwd, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    return {b for b in out.splitlines() if b}


def stale_report(cwd: str, remote: str = "origin") -> dict:
    """The report `cq git stale` prints, and the one `cq git prune` re-reads before it acts."""
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
    # Guidance first: a branch that must stay is listed with the reason, never offered for
    # deletion. `open-pr` needs the host (`gh` or `az`); when it is unreachable the report says so.
    open_prs = _open_pr_heads(cwd)
    checked_out = _checked_out_branches(cwd)
    kept: dict[str, set[str]] = {}
    for b in _local_branches(cwd) - protected:
        why = set()
        if open_prs and b in open_prs:
            why.add("open-pr")
        if b in checked_out:
            why.add("worktree")
        if b not in reasons:
            why.add("unmerged-commits")
        if why:
            kept[b] = why
            reasons.pop(b, None)
    branches = [{"branch": b, "reasons": sorted(r)} for b, r in sorted(reasons.items())]
    kept_branches = [{"branch": b, "reasons": sorted(r)} for b, r in sorted(kept.items())]
    remote_branches = _merged_remote_branches(cwd, base, protected, remote)
    return {"ok": True, "base": base, "remote": remote, "staleBranches": branches,
            "keptBranches": kept_branches,
            "prLookup": "ok" if open_prs is not None else "unavailable",
            "remoteBranches": remote_branches, "orphanWorktrees": _orphan_worktrees(cwd),
            UNREGISTERED_WORKTREES_KEY: _unregistered_worktrees(cwd)}


def cmd_stale(args) -> int:
    report = stale_report(os.getcwd(), getattr(args, "remote", None) or "origin")
    base, branches = report["base"], report["staleBranches"]
    remote_branches, worktrees = report["remoteBranches"], report["orphanWorktrees"]
    unregistered_worktrees = report[UNREGISTERED_WORKTREES_KEY]

    lines = [f"base: {base}"]
    lines.append("stale branches:" if branches else "stale branches: none")
    for b in branches:
        lines.append(f"  {b['branch']} ({', '.join(b['reasons'])})")
    kept_rows = report["keptBranches"]
    lines.append("kept branches (not removable):" if kept_rows else "kept branches: none")
    for b in kept_rows:
        lines.append(f"  {b['branch']} ({', '.join(b['reasons'])})")
    lines.append("stale remote branches:" if remote_branches else "stale remote branches: none")
    for b in remote_branches:
        lines.append(f"  {b['remote']}/{b['branch']} ({', '.join(b['reasons'])})")
    lines.append("orphan worktrees:" if worktrees else "orphan worktrees: none")
    for w in worktrees:
        lines.append(f"  {w['path']} ({w['branch'] or 'detached'})")
    lines.append("unregistered worktrees (repository siblings):"
                 if unregistered_worktrees
                 else "unregistered worktrees (repository siblings): none")
    for w in unregistered_worktrees:
        branch = w["branch"] or "detached"
        size = f"{w['size']} bytes" if w["size"] is not None else "size unavailable"
        lines.append(f"  {w['path']} ({branch}, {size})")

    emit(args.json, report, "\n".join(lines))
    return 0
