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
from quenching.git.push import remote_probe

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
    has_remote = remote_probe(cwd, args.remote)
    if has_remote is None:
        return refuse({"code": "git-worktree-remote-unreadable",
                       "message": f"git could not read the remote: {args.remote}"}, args.json)
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


def _registered_worktrees(cwd: str) -> list[tuple[str, str | None]]:
    """(path, branch) of every worktree git registers, the primary checkout first."""
    code, out, _err = _git_run(cwd, *SAFE, "worktree", "list", "--porcelain")
    found: list[tuple[str, str | None]] = []
    path = branch = None
    for line in (out.splitlines() if code == 0 else []) + [""]:
        if line.startswith("worktree "):
            path = line[len("worktree "):]
        elif line.startswith("branch "):
            branch = line[len("branch "):].removeprefix("refs/heads/")
        elif not line and path is not None:
            found.append((path, branch))
            path = branch = None
    return found


def _ignored_files(path: str) -> list[str] | None:
    """Ignored entries the worktree holds that are not symlinks: the shared paths `worktree link`
    materialises are symlinks into a store and survive the removal, anything else is deleted.
    None when `git status` fails: the caller refuses, an unread worktree is not an empty one."""
    code, out, _err = _git_run(path, *SAFE, "status", "--porcelain", "--untracked-files=normal",
                               "--ignored=matching")
    if code != 0:
        return None
    entries = [line[3:] for line in out.splitlines() if line.startswith("!! ")]
    return [e for e in entries if not os.path.islink(os.path.join(path, e.rstrip("/")))]


def _regenerable_paths(config: dict) -> list[str]:
    values = namespace(config, "shared").get("regenerablePaths")
    if not isinstance(values, list):
        return []
    return [os.path.normpath(v.strip()) + ("/" if v.strip().endswith("/") else "")
            for v in values if isinstance(v, str) and v.strip()
            and not os.path.isabs(v.strip()) and ".." not in v.strip().split("/")]


def _is_regenerable(entry: str, declared: list[str]) -> bool:
    """A declared entry without a slash names a component at any depth; one with a slash, inner
    or trailing, names a path from the repo root, itself or anything under it."""
    parts = os.path.normpath(entry.rstrip("/")).split(os.sep)
    for rule in declared:
        if os.sep in rule:
            anchored = rule.rstrip(os.sep)
            width = len(anchored.split(os.sep))
            if os.sep.join(parts[:width]) == anchored:
                return True
        elif rule in parts:
            return True
    return False


def _undeclared(path: str, entries: list[str], declared: list[str]) -> list[str]:
    """The ignored entries no declaration covers; git reports a wholly ignored directory as one
    entry, so a directory that merely contains a declared path is opened to its files."""
    left = []
    for entry in entries:
        if _is_regenerable(entry, declared):
            continue
        if entry.endswith("/"):
            files = [os.path.relpath(os.path.join(root, name), path)
                     for root, _dirs, names in os.walk(os.path.join(path, entry))
                     for name in names]
            left += [f for f in files if not _is_regenerable(f, declared)]
            if not files:
                left.append(entry)
        else:
            left.append(entry)
    return left


def _retire(args) -> int:
    """Remove a merged spec's worktree and delete its branch with `branch -d`, never `-D`.

    Merged means the branch tip is an ancestor of `<remote>/<base>` (fetched here; the local base
    when the remote does not exist), because a PR merged through `gh` moves the remote base. Every
    refusal (exit 2) happens before a write. The worktree goes first, since git will not delete a
    branch checked out in one; `worktree remove` runs without `--force`, so a dirty worktree
    stands. A worktree holding ignored files that are not symlinks stands too (exit 1, `ignored`
    lists them) unless `shared.regenerablePaths` declares them regenerable or `--discard-ignored` is passed. `branch -d` compares the branch with its upstream when one is configured, so a published branch is
    deleted even while the local base is behind; with no upstream it compares with the checked-out
    HEAD and refuses when the local base is behind: the branch stands, exit 1."""
    cwd = os.getcwd()
    missing = [f"--{k}" for k in ("path", "branch", "base") if not getattr(args, k)]
    if missing:
        return refuse({"code": "git-worktree-retire-args",
                       "message": f"`worktree retire` needs {', '.join(missing)}"}, args.json)
    for label, value in (("branch", args.branch), ("base", args.base), ("remote", args.remote)):
        if not value or value.startswith("-") or not _branch_ok(cwd, value):
            return refuse({"code": "git-worktree-ref-invalid",
                           "message": f"{label} is not a usable name: {value}"}, args.json)
    if args.branch == args.base:
        return refuse({"code": "git-worktree-retire-base",
                       "message": f"the branch is the base: {args.branch}"}, args.json)
    registered = _registered_worktrees(cwd)
    want = os.path.realpath(args.path)
    match = [(p, b) for p, b in registered if os.path.realpath(p) == want]
    if not match:
        return refuse({"code": "git-worktree-retire-unregistered",
                       "message": f"not a worktree this repository registers: {args.path}"},
                      args.json)
    path, registered_branch = match[0]
    if want in (os.path.realpath(registered[0][0]), os.path.realpath(_repo_root(cwd))):
        return refuse({"code": "git-worktree-retire-primary",
                       "message": "the primary checkout, or the one this runs in, is never retired"},
                      args.json)
    if registered_branch != args.branch:
        return refuse({"code": "git-worktree-retire-mismatch",
                       "message": f"{args.path} holds {registered_branch or 'a detached HEAD'}, "
                                  f"not {args.branch}"}, args.json)
    has_remote = remote_probe(cwd, args.remote)
    if has_remote is None:
        return refuse({"code": "git-worktree-remote-unreadable",
                       "message": f"git could not read the remote: {args.remote}"}, args.json)
    if has_remote:
        code, _out, err = _git_run(cwd, *SAFE, "fetch", "--no-recurse-submodules", "--",
                                   args.remote, f"refs/heads/{args.base}")
        if code != 0:
            return refuse({"code": "git-worktree-fetch-failed",
                           "message": f"git fetch {args.remote} {args.base} failed: {err.strip()}"},
                          args.json)
        target, base_sha = f"{args.remote}/{args.base}", _commit(cwd, "FETCH_HEAD")
    else:
        target, base_sha = args.base, _commit(cwd, f"refs/heads/{args.base}")
    tip = _commit(cwd, f"refs/heads/{args.branch}")
    if base_sha is None or tip is None:
        return refuse({"code": "git-worktree-ref-invalid",
                       "message": "the base or the branch does not resolve to a commit"}, args.json)
    if _run(cwd, "merge-base", "--is-ancestor", tip, base_sha)[0] != 0:
        return refuse({"code": "git-worktree-retire-not-merged",
                       "message": f"{args.branch} is not merged into {target}; nothing was removed"},
                      args.json)
    payload = {"ok": False, "path": path, "branch": args.branch, "base": target,
               "worktreeRemoved": False, "branchDeleted": False}
    ignored = [] if args.discard_ignored else _ignored_files(path)
    if ignored:
        declared = _regenerable_paths(load_config(_repo_root(cwd)))
        ignored = _undeclared(path, ignored, declared)
    if ignored is None:
        return refuse({"code": "git-worktree-retire-status-failed",
                       "message": f"git status failed in {path}; nothing was removed"}, args.json)
    if ignored:
        payload.update(ignored=ignored, message=f"the worktree holds ignored files that removal "
                       f"would delete: {', '.join(ignored)}; pass --discard-ignored to remove anyway")
        emit(args.json, payload, f"worktree {path} kept: {payload['message']}")
        return FINDINGS
    code, _out, err = _git_run(cwd, *SAFE, "worktree", "remove", "--", path)
    if code != 0:
        payload["message"] = err.strip()
        emit(args.json, payload, f"worktree {path} refused: {err.strip()}")
        return FINDINGS
    payload["worktreeRemoved"] = True
    code, _out, err = _git_run(cwd, *SAFE, "branch", "-d", "--", args.branch)
    if code != 0:
        payload["message"] = err.strip()
        emit(args.json, payload, f"worktree removed; branch {args.branch} stands: {err.strip()}")
        return FINDINGS
    payload.update(ok=True, branchDeleted=True)
    emit(args.json, payload, f"retired {path} and branch {args.branch}")
    return 0


def cmd_worktree(args) -> int:
    if args.action == "add":
        return _add(args)
    if args.action == "retire":
        return _retire(args)
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
