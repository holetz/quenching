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
from quenching.specs.config import (CONFIG_FILE, ROOT_TOO_HIGH_REMEDY, is_root_too_high,
                                    load_config, root_too_high_message)
from quenching.specs.worktree import resolve_files_root


_BACKEND_CACHE: dict[str, SpecBackend] = {}


def backend_root(root: str, cfg: dict) -> str | None:
    """Where the declared backend keeps its documents — measured, and never created.

    THE ANSWER `open_backend` CANNOT BE ASKED FOR. Opening the backend is what makes the specs
    worktree exist, deliberately (see `open_backend` below), so a diagnostic that opened one to
    learn its root would create the very thing it was sent to report on. This resolves the same
    directory arithmetically instead: `doctor` and `migrate --dry-run` get the truth, and a
    read-only command stays read-only.

    `None` under an external backend, because there is no directory. GitHub and Azure Boards
    keep the documents outside the filesystem entirely, and the declared root there names a
    folder that does not exist — emitting it is the lie this replaces, and an empty string would
    only move the problem into every consumer's own vacuity test."""
    if cfg["backend"] != "files":
        return None
    # The non-creating mode has no failure path — see `resolve_files_root`'s own contract.
    target, _ = resolve_files_root(root, cfg, create=False)
    return target


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
        if is_root_too_high(root):
            # `--root`/`SPECS_ROOT` named the container that holds a phased `.specs/`, not the
            # workspace itself — reading it as empty (today's behaviour) would silently lose
            # every `list`/`validate`/`new` call this root reaches. Refuse instead of resolving.
            return None, {
                "code": "sp-root-too-high", "exit": 2, "root": root,
                "message": root_too_high_message(root), "remedy": ROOT_TOO_HIGH_REMEDY,
            }
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
                       f"cq specs does not implement it yet — no spec was read or written",
        }
    _BACKEND_CACHE[root] = backend
    return backend, {}
