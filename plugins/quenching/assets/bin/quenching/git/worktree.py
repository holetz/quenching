"""`cq git worktree link` — materialise the target's declared shared paths.

The store is derived from git's common directory rather than from the checkout path.  Asking
for an absolute common directory is essential: a primary checkout otherwise answers with a
relative ``.git`` and would create a different sibling store depending on the caller's cwd.
"""
from __future__ import annotations

import json
import os

from quenching.common.git import _git
from quenching.common.output import emit, refuse

CONFIG_FILE = os.path.join(".claude", "quenching.json")


def _repo_root(cwd: str) -> str:
    return _git(cwd, "rev-parse", "--show-toplevel").strip()


def _declared_paths(repo: str) -> list[str]:
    path = os.path.join(repo, CONFIG_FILE)
    try:
        with open(path, encoding="utf-8") as stream:
            config = json.load(stream)
    except (OSError, ValueError):
        return []
    values = config.get("sharedPaths") if isinstance(config, dict) else None
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
    os.makedirs(store, exist_ok=True)
    os.makedirs(os.path.dirname(link), exist_ok=True)

    if os.path.islink(link):
        if os.path.realpath(link) == os.path.realpath(store):
            return {"path": relative, "store": store, "state": "unchanged"}
        os.unlink(link)
        os.symlink(store, link)
        return {"path": relative, "store": store, "state": "repointed"}

    if os.path.lexists(link):
        if os.path.isdir(link) and not os.listdir(link):
            os.rmdir(link)
        else:
            raise FileExistsError(link)

    os.symlink(store, link)
    return {"path": relative, "store": store, "state": "created"}


def cmd_worktree(args) -> int:
    repo = _repo_root(os.getcwd())
    if not repo:
        return refuse({"code": "git-worktree-not-repository",
                        "message": "the current directory is not inside a git repository"},
                       args.json)

    results = []
    for relative in _declared_paths(repo):
        store = _store_for(repo, relative)
        if store is None:
            return refuse({"code": "git-worktree-no-common-dir",
                           "path": relative,
                           "message": "git could not resolve the repository's common directory"},
                          args.json)
        try:
            results.append(_materialise(repo, relative, store))
        except FileExistsError:
            return refuse({"code": "git-worktree-path-not-empty", "path": relative,
                           "message": f"'{relative}' is a real path with content; merge it into "
                                      "the shared store by hand before linking it"}, args.json)

    emit(args.json, {"ok": True, "paths": results},
         "\n".join(f"{item['path']}: {item['state']} -> {item['store']}" for item in results)
         or "shared paths: none")
    return 0
