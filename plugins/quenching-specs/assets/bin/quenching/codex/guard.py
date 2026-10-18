"""The git guard: what a Codex run must leave as it found it, read without writing anything.

Codex runs with `--dangerously-bypass-approvals-and-sandbox`, so its bounds are proved by code
here, before and after the run. `refs` are the worktree's `HEAD`, branch, reflog length, stash ref
and every worktree's `HEAD`. `tree` maps every path `git status` reports to its status code and
the hash of its bytes, so the review can prove it changed nothing at all. The review's snapshot
also holds every ref, the hash of the index and the ignored files that carry local configuration
(`.claude/**` and `*.local.json`), and a git command that fails is `GuardError`: the guard fails
closed, never as an empty tree.
"""
from __future__ import annotations

import hashlib
import os
import subprocess

BYPASS = "--dangerously-bypass-approvals-and-sandbox"
SECRET_NAMES = ("GH_TOKEN", "GITHUB_TOKEN")
SECRET_PREFIXES = ("AWS_", "AZURE_", "GOOGLE_")


def clean_env(env: dict) -> dict:
    """The environment a bypassed Codex gets: no forge token and no cloud credential."""
    return {k: v for k, v in env.items()
            if k not in SECRET_NAMES and not k.startswith(SECRET_PREFIXES)}


def git(worktree: str, *args: str) -> str:
    result = subprocess.run(["git", "-C", worktree, *args], capture_output=True, text=True,
                            errors="replace")
    return result.stdout if result.returncode == 0 else ""


class GuardError(Exception):
    """A git command the guard depends on failed, so nothing can be proved."""


def git_strict(worktree: str, *args: str) -> str:
    result = subprocess.run(["git", "-C", worktree, *args], capture_output=True, text=True,
                            errors="replace")
    if result.returncode != 0:
        raise GuardError(f"git {' '.join(args)} failed ({result.returncode}): "
                         f"{result.stderr.strip()}")
    return result.stdout


def status(worktree: str, strict: bool = False) -> list[tuple[str, str]]:
    """Every `(XY, path)` `git status` reports, rename sources included."""
    run = git_strict if strict else git
    entries = run(worktree, "status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0")
    out: list[tuple[str, str]] = []
    source = None
    for entry in entries:
        if source is not None:
            out.append((source, entry))
            source = None
            continue
        if len(entry) > 3:
            out.append((entry[:2], entry[3:]))
            source = entry[:2] if "R" in entry[:2] or "C" in entry[:2] else None
    return out


def touched(worktree: str) -> set[str]:
    return {path for _, path in status(worktree)}


def refs(worktree: str) -> dict:
    """The refs Codex must not move."""
    others = {}
    for block in git(worktree, "worktree", "list", "--porcelain").split("\n\n"):
        fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
        if "worktree" in fields:
            others[fields["worktree"]] = fields.get("HEAD")
    return {"head": git(worktree, "rev-parse", "HEAD").strip(),
            "branch": git(worktree, "symbolic-ref", "-q", "HEAD").strip(),
            "reflogLength": len(git(worktree, "reflog", "--format=%H").splitlines()),
            "stash": git(worktree, "rev-parse", "-q", "--verify", "refs/stash").strip(),
            "worktrees": others}


def _digest(full: str) -> str:
    if os.path.isfile(full):
        with open(full, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    return "-"


def _skipped(path: str, skip: str | None) -> bool:
    return bool(skip) and (path == skip or path.startswith(skip.rstrip("/") + "/"))


def _local_config(path: str) -> bool:
    return path.startswith(".claude/") or path.endswith(".local.json")


def strict_refs(worktree: str) -> dict:
    """Every ref (`for-each-ref`) and the hash of the index (`ls-files -s`); fails closed."""
    return {"allRefs": git_strict(worktree, "for-each-ref", "--format=%(refname) %(objectname)"),
            "index": hashlib.sha256(
                git_strict(worktree, "ls-files", "-s", "-z").encode("utf-8", "replace")
            ).hexdigest()}


def tree(worktree: str, skip: str | None = None) -> dict[str, str]:
    """`path -> "XY sha256"` for every path `git status` reports, except those under `skip`, plus
    the ignored files that hold local configuration. Raises `GuardError` if git fails."""
    out: dict[str, str] = {}
    for code, path in status(worktree, strict=True):
        if _skipped(path, skip):
            continue
        out[path] = f"{code} {_digest(os.path.join(worktree, path))}"
    ignored = git_strict(worktree, "ls-files", "--others", "--ignored", "--exclude-standard",
                         "-z").split("\0")
    for path in ignored:
        if path and _local_config(path) and not _skipped(path, skip):
            out[path] = f"!! {_digest(os.path.join(worktree, path))}"
    return out
