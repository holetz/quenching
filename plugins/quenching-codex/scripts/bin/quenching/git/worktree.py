"""`cq git worktree link` — materialise the target's declared shared paths; `cq git worktree add`
— cut a branch from the fetched remote base into a new worktree, then link it.

The store is derived from git's common directory rather than from the checkout path.  Asking
for an absolute common directory is essential: a primary checkout otherwise answers with a
relative ``.git`` and would create a different sibling store depending on the caller's cwd.
"""
from __future__ import annotations

import os

from quenching.common.git import _git, _git_run
from quenching.common.config import load_config, namespace
from quenching.common.output import FINDINGS, emit, refuse
from quenching.git.audit import SAFE, _branch_ok, _commit, _run

def _repo_root(cwd: str) -> str:
    return _git(cwd, "rev-parse", "--show-toplevel").strip()


def _declared_paths(config: dict) -> list[str]:
    values = namespace(config, "shared").get("sharedPaths")
    if not isinstance(values, list):
        return []

    paths = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            continue
        relative = os.path.normpath(value.strip())
        if os.path.isabs(relative) or relative == "." or relative == "..":
            continue
        if relative.startswith(f"..{os.sep}"):
            continue
        paths.append(relative)
    return paths


def _store_for(repo: str, relative: str) -> str | None:
    common = _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    if not common:
        return None
    name = relative.replace(os.sep, ".")
    return f"{os.path.dirname(common)}.{name}"


def _link_path(repo: str, relative: str) -> str:
    return os.path.join(repo, relative)


def _materialise(repo: str, relative: str, store: str) -> dict:
    link = _link_path(repo, relative)
    if os.path.islink(link):
        if os.path.realpath(link) == os.path.realpath(store):
            return {"path": relative, "store": store, "state": "unchanged"}
        os.unlink(link)
        os.symlink(store, link)
        return {"path": relative, "store": store, "state": "repointed"}

    empty_directory = False
    if os.path.lexists(link):
        if os.path.isdir(link) and not os.listdir(link):
            empty_directory = True
        else:
            raise FileExistsError(link)

    os.makedirs(store, exist_ok=True)
    os.makedirs(os.path.dirname(link), exist_ok=True)
    if empty_directory:
        os.rmdir(link)
    os.symlink(store, link)
    return {"path": relative, "store": store, "state": "created"}


def _ignore_warning(repo: str, relative: str) -> str | None:
    code, _stdout, _stderr = _git_run(repo, "check-ignore", "--quiet", "--", relative)
    if code == 0:
        return None
    return f"'{relative}' is not covered by git check-ignore"


def _link(repo: str) -> tuple[list[dict] | None, dict | None]:
    """The declared shared paths of `repo` materialised, or the refusal that stopped it."""
    config = load_config(repo)
    if config.get("migrationRefusal"):
        return None, config["migrationRefusal"]
    results = []
    for relative in _declared_paths(config):
        store = _store_for(repo, relative)
        if store is None:
            return None, {"code": "git-worktree-no-common-dir", "path": relative,
                          "message": "git could not resolve the repository's common directory"}
        try:
            item = _materialise(repo, relative, store)
        except FileExistsError:
            return None, {"code": "git-worktree-path-not-empty", "path": relative,
                          "message": f"'{relative}' is a real path with content; merge it into "
                                     "the shared store by hand before linking it"}
        warning = _ignore_warning(repo, relative)
        if warning:
            item["warning"] = warning
        results.append(item)
    return results, None


def _link_lines(results: list[dict]) -> list[str]:
    human = []
    for item in results:
        line = f"{item['path']}: {item['state']} -> {item['store']}"
        if item.get("warning"):
            line += f" [warning: {item['warning']}]"
        human.append(line)
    return human


def _add(args) -> int:
    """Cut `--branch` from `<remote>/<base>` into a new worktree at `--path`, then link it.

    Every git call is built here with `audit.SAFE`; the start point is resolved to a commit
    before `worktree add`, so the new branch has no upstream and a push without a destination
    never targets the base. Only a remote that does not exist falls back to the local base."""
    cwd = os.getcwd()
    missing = [f"--{k}" for k in ("path", "branch", "base") if not getattr(args, k)]
    if missing:
        return refuse({"code": "git-worktree-add-args",
                       "message": f"`worktree add` needs {', '.join(missing)}"}, args.json)
    path = os.path.abspath(args.path)
    if os.path.lexists(path):
        return refuse({"code": "git-worktree-path-exists", "path": path,
                       "message": f"the worktree path already exists: {path}"}, args.json)
    for label, value in (("branch", args.branch), ("base", args.base), ("remote", args.remote)):
        if not value or value.startswith("-") or not _branch_ok(cwd, value):
            return refuse({"code": "git-worktree-ref-invalid",
                           "message": f"{label} is not a usable name: {value}"}, args.json)
    if _commit(cwd, f"refs/heads/{args.branch}") is not None:
        return refuse({"code": "git-worktree-branch-exists",
                       "message": f"the branch already exists: {args.branch}"}, args.json)
    has_remote = _run(cwd, "remote", "get-url", "--", args.remote)[0] == 0
    if has_remote:
        code, _out, err = _git_run(cwd, *SAFE, "fetch", "--no-recurse-submodules", "--",
                                   args.remote, f"refs/heads/{args.base}")
        if code != 0:
            return refuse({"code": "git-worktree-fetch-failed",
                           "message": f"git fetch {args.remote} {args.base} failed: {err.strip()}"},
                          args.json)
        start_ref = f"refs/remotes/{args.remote}/{args.base}"
        sha = _commit(cwd, "FETCH_HEAD")
    else:
        start_ref = f"refs/heads/{args.base}"
        sha = _commit(cwd, start_ref)
    if sha is None:
        return refuse({"code": "git-worktree-ref-invalid",
                       "message": f"the base does not resolve to a commit: {start_ref}"}, args.json)
    code, _out, err = _git_run(cwd, *SAFE, "worktree", "add", "--no-track", "-b", args.branch,
                               "--", path, sha)
    if code != 0:
        return refuse({"code": "git-worktree-add-failed",
                       "message": f"git worktree add failed: {err.strip()}"}, args.json)
    results, refusal = _link(path)
    payload = {"ok": refusal is None, "path": path, "branch": args.branch, "base": args.base,
               "start": f"{args.remote}/{args.base}" if has_remote else args.base,
               "fromRemote": has_remote, "startSha": sha, "paths": results or [],
               "linkRefusal": refusal}
    human = [f"worktree: {path}", f"branch: {args.branch} from {payload['start']} ({sha[:12]})"]
    if not has_remote:
        human.append(f"NO-REMOTE: {args.remote} is not configured; cut from the local {args.base}")
    human += _link_lines(results or [])
    if refusal:
        human.append(f"link refused: {refusal.get('message')}")
    emit(args.json, payload, "\n".join(human))
    return 0 if refusal is None else FINDINGS


def cmd_worktree(args) -> int:
    if args.action == "add":
        return _add(args)
    repo = _repo_root(os.getcwd())
    if not repo:
        return refuse({"code": "git-worktree-not-repository",
                        "message": "the current directory is not inside a git repository"},
                       args.json)
    results, refusal = _link(repo)
    if refusal:
        return refuse(refusal, args.json)
    emit(args.json, {"ok": True, "paths": results}, "\n".join(_link_lines(results)) or "shared paths: none")
    return 0
