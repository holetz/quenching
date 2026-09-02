"""`cq git worktree link` — materialise the target's declared shared paths.

The store is derived from git's common directory rather than from the checkout path.  Asking
for an absolute common directory is essential: a primary checkout otherwise answers with a
relative ``.git`` and would create a different sibling store depending on the caller's cwd.
"""
from __future__ import annotations

import os

from quenching.common.git import _git, _git_run
from quenching.common.config import load_config, namespace
from quenching.common.output import emit, refuse

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


def cmd_worktree(args) -> int:
    repo = _repo_root(os.getcwd())
    if not repo:
        return refuse({"code": "git-worktree-not-repository",
                        "message": "the current directory is not inside a git repository"},
                       args.json)

    config = load_config(repo)
    if config.get("migrationRefusal"):
        return refuse(config["migrationRefusal"], args.json)

    results = []
    for relative in _declared_paths(config):
        store = _store_for(repo, relative)
        if store is None:
            return refuse({"code": "git-worktree-no-common-dir",
                           "path": relative,
                           "message": "git could not resolve the repository's common directory"},
                          args.json)
        try:
            item = _materialise(repo, relative, store)
        except FileExistsError:
            return refuse({"code": "git-worktree-path-not-empty", "path": relative,
                           "message": f"'{relative}' is a real path with content; merge it into "
                                      "the shared store by hand before linking it"}, args.json)
        warning = _ignore_warning(repo, relative)
        if warning:
            item["warning"] = warning
        results.append(item)

    human = []
    for item in results:
        line = f"{item['path']}: {item['state']} -> {item['store']}"
        if item.get("warning"):
            line += f" [warning: {item['warning']}]"
        human.append(line)
    emit(args.json, {"ok": True, "paths": results}, "\n".join(human) or "shared paths: none")
    return 0
