"""The operations front's declared root and canonical router.

`opsRoot` and `router` live beside the specs settings in `.claude/quenching.json`, but their
meaning belongs to this front.  The shared loader reads them as data; this module is the one
boundary that turns the two declarations into repository-relative paths and refuses to guess
when either declaration is absent.
"""
from __future__ import annotations

import os

from quenching.specs.config import CONFIG_FILE, load_config


OPS_CONFIG_KEYS = ("opsRoot", "router")


def _repo_path(repo_root: str, declared: str) -> str:
    """Resolve one configured path without changing the declaration's spelling."""
    return os.path.abspath(os.path.join(repo_root, declared))


def _find_repo_root(root: str) -> str:
    """Find the config home by ancestry, without asking git to execute anything."""
    current = os.path.abspath(root)
    while True:
        if os.path.isfile(os.path.join(current, CONFIG_FILE)):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(root)
        current = parent


def _loader_root(repo_root: str) -> str:
    """Give the shared loader a non-directory root so its provider lookup stays dormant."""
    return os.path.join(repo_root, ".quenching-ops-loader-root")


def load_ops_config(root: str) -> tuple[dict | None, dict]:
    """Return the resolved operations configuration, or the one refusal it can carry.

    The ordinary `load_config` result remains available to every specs caller.  This wrapper
    deliberately does not add a default for `opsRoot` or `router`: an operations tree and a
    router are target-repository decisions, and selecting `scripts/` or a guessed build entry
    point would make the verifier inspect the wrong surface while appearing healthy.
    """
    repo_root = _find_repo_root(root)
    cfg = load_config(_loader_root(repo_root), detect_provider_info=False)
    missing = [key for key in OPS_CONFIG_KEYS if not cfg.get(key)]
    if missing:
        missing_text = ", ".join(f"`{key}`" for key in missing)
        return None, {
            "code": "op-config-missing",
            "exit": 2,
            "config": CONFIG_FILE,
            "missing": missing,
            "message": f"{CONFIG_FILE} must declare both `opsRoot` and `router`; "
                       f"missing {missing_text} — the ops front refuses to guess its "
                       "operations tree or canonical router",
        }

    ops_root = _repo_path(repo_root, cfg["opsRoot"])
    router = _repo_path(repo_root, cfg["router"])
    return {
        "config": cfg["path"],
        "repoRoot": repo_root,
        "opsRoot": ops_root,
        "router": router,
        "declaredOpsRoot": cfg["opsRoot"],
        "declaredRouter": cfg["router"],
    }, {}


def resolve_ops_config(root: str) -> tuple[dict | None, dict]:
    """Alias named for callers that need to make the resolution boundary explicit."""
    return load_ops_config(root)
