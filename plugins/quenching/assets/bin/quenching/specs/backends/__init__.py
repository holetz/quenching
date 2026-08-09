"""The spec backends, and the one factory that opens the declared one.

`open_backend` and its cache live in the package `__init__` because they are the package's
whole public surface: every caller wants `from quenching.specs.backends import open_backend`,
and this is the ONLY place that may know all four implementations at once. Keeping the fan-out
here is what lets `files`, `memory`, `github` and `azure` stay unaware of each other.

This is therefore the one directory under `quenching/` that is a regular package rather than a
PEP 420 namespace one — an `__init__.py` that carries the factory, never an empty file added
for its own sake."""
from __future__ import annotations

from quenching.specs.backends.azure import open_azure_backend
from quenching.specs.backends.base import SpecBackend
from quenching.specs.backends.files import FilesBackend
from quenching.specs.backends.github import open_github_backend
from quenching.specs.config import CONFIG_FILE, load_config
from quenching.specs.worktree import resolve_files_root


_BACKEND_CACHE: dict[str, SpecBackend] = {}


def open_backend(root: str) -> tuple[SpecBackend | None, dict]:
    """The backend this workspace declares, or a ready-to-emit refusal.

    Memoised per root because resolving it reads the config from disk, and a single command
    asks for it more than once. The cache holds no mutable state — a backend is its root and
    nothing else — so this is a lookup table, not a session.

    THIS IS WHERE "ON DEMAND" IS MADE TRUE for the `files` backend's specs worktree, and the
    reason it is here rather than in `FilesBackend.__init__`. Every command that reads or
    writes a spec passes through here and nothing else does — `doctor`, `config` and `selftest`
    never open a backend — so the worktree is created by the first command that actually needs
    the specs and never as a side effect of a diagnostic. A constructor could not make that
    distinction: `FilesBackend(root)` is also how the equivalence cases instantiate it over a
    bare temp directory with no repository, which must keep costing nothing and touching
    nothing.

    A backend named in the config but not yet implemented refuses with exit 2 rather than
    falling back to `files`. Silently writing specs to the local filesystem for a repo that
    asked for GitHub is the one failure that loses work instead of reporting it."""
    if root in _BACKEND_CACHE:
        return _BACKEND_CACHE[root], {}
    cfg = load_config(root)
    name = cfg["backend"]
    if name == "files":
        target, err = resolve_files_root(root, cfg)
        if err:
            # A worktree that could not be created — unignored, occupied, or refused by git.
            # Nothing falls back to the declared root: the specs are on the specs branch, and
            # writing them beside the code is the state this backend exists to end.
            return None, err
        backend: SpecBackend = FilesBackend(target)
    elif name == "github":
        gh, err = open_github_backend(root)
        if err:
            # `gh` missing, nobody logged in, or no repository to point at. Each is an
            # exit-2 refusal for the same reason the worktree failures above are: nothing
            # falls back to `files` when the repo asked for GitHub.
            return None, err
        backend = gh                                        # type: ignore[assignment]
    elif name == "azure-boards":
        az, err = open_azure_backend(root)
        if err:
            # No `az`, no extension, nobody logged in, no configured project, or no declared
            # phase-to-state mapping. Each is an exit-2 refusal, and nothing falls back to
            # `files` when the repo asked for Azure Boards.
            return None, err
        backend = az                                        # type: ignore[assignment]
    else:
        return None, {
            "code": "sp-backend-unavailable", "exit": 2, "backend": name,
            "message": f"backend '{name}' is declared in {CONFIG_FILE} but this copy of "
                       f"specs.py does not implement it yet — no spec was read or written",
        }
    _BACKEND_CACHE[root] = backend
    return backend, {}
