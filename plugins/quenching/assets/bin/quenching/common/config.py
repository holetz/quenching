"""Read the repository-wide configuration envelope.

The file is shared by every front, while each namespace remains owned by its adapter. This
module only discovers the configuration home, parses the envelope and derives the provider; it
does not interpret a front's values.
"""
from __future__ import annotations

import json
import os

from quenching.common.git import _git
from quenching.common.io import read_text


CONFIG_FILE = os.path.join(".claude", "quenching.json")
LEGACY_CONFIG_FILE = "config.json"
NAMESPACES = ("shared", "specs", "ops", "proof")

# Root-level keys accepted by the pre-envelope format. They are diagnostic-only now: a front
# adapter must refuse to interpret them because doing so makes a half-migrated repository look
# healthy while one namespace silently wins over another.
LEGACY_KEYS = frozenset({
    "worktreeSetup", "sharedPaths", "specsBranch", "azureStates", "hooks", "profiles",
    "azurePlacement", "azureColumns", "subjects", "tagCatalog", "workItemTypes",
    "fanoutMinComplexity", "opsRoot", "router", "registry", "proofRoot", "layers",
    "measuredRoots", "proofExclusions", "ratchetPath",
})

LEGACY_DESTINATIONS = {
    "worktreeSetup": "shared",
    "sharedPaths": "shared",
    "hooks": "shared",
    "profiles": "shared",
    "specsBranch": "specs",
    "azureStates": "specs",
    "azurePlacement": "specs",
    "azureColumns": "specs",
    "subjects": "specs",
    "tagCatalog": "specs",
    "workItemTypes": "specs",
    "fanoutMinComplexity": "specs",
    "opsRoot": "ops",
    "router": "ops",
    "registry": "ops",
    "proofRoot": "proof",
    "layers": "proof",
    "measuredRoots": "proof",
    "proofExclusions": "proof",
    "ratchetPath": "proof",
}


def find_repo_root(specs_root: str) -> str:
    """Find the repository containing the shared configuration home."""
    current = os.path.abspath(specs_root)
    while True:
        if os.path.isfile(os.path.join(current, CONFIG_FILE)):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    top = (_git(specs_root, "rev-parse", "--show-toplevel").strip()
           if os.path.isdir(specs_root) else "")
    if top:
        return top
    return os.path.dirname(os.path.abspath(specs_root))


def _remote_host(remote: str) -> str:
    host = remote.strip().split("#", 1)[0]
    if "://" in host:
        host = host.split("://", 1)[1]
    host = host.rsplit("@", 1)[-1]
    return host.split("/", 1)[0].split(":", 1)[0].lower()


def detect_provider(root: str) -> tuple[str | None, str | None]:
    """Derive the provider from the repository's origin URL."""
    repo = find_repo_root(root)
    remote = _git(repo, "remote", "get-url", "origin").strip()
    if not remote:
        return None, None
    host = _remote_host(remote)
    if host == "github.com" or host.endswith(".github.com"):
        return "github", host
    if (host == "dev.azure.com" or host.endswith(".dev.azure.com")
            or host == "visualstudio.com" or host.endswith(".visualstudio.com")):
        return "azure-boards", host
    return None, host


def infer_base_branch(cfg: dict, origin_head: str | None, init_default: str | None) -> str:
    """Resolve the unstamped base branch from already-collected git facts.

    The branch chain is shared by the git and specs fronts. Keeping it here lets git consume
    the common envelope without importing the specs adapter just for this pure decision.
    ``cfg`` remains in the signature for callers that pass the full configuration envelope;
    no configuration key participates in the fallback chain.
    """
    if origin_head:
        return origin_head
    if init_default:
        return init_default
    return "main"


def _migration_refusal(path: str, obj: dict, legacy_keys: list[str]) -> dict | None:
    """Describe the exit-2 refusal for a flat or mixed pre-envelope document."""
    if not legacy_keys:
        return None
    destinations = [
        {"key": key, "namespace": LEGACY_DESTINATIONS[key]}
        for key in legacy_keys
    ]
    shape = "mixed" if any(name in obj for name in NAMESPACES) else "flat"
    moved = ", ".join(f"`{row['key']}` → `{row['namespace']}`" for row in destinations)
    return {
        "code": "sp-config-unscoped",
        "exit": 2,
        "config": path,
        "shape": shape,
        "keys": legacy_keys,
        "destinations": destinations,
        "message": f"{CONFIG_FILE} uses {shape} legacy configuration: {moved}; "
                   "the front refuses to read unscoped declarations",
        "remedy": f"move every listed key into its destination namespace in {CONFIG_FILE}; "
                  "do not mix flat and namespaced declarations",
    }


def load_config(root: str, *, detect_provider_info: bool = True) -> dict:
    """Return the parsed envelope and metadata without interpreting any namespace."""
    repo = find_repo_root(root)
    path = os.path.join(repo, CONFIG_FILE)
    provider, provider_host = (detect_provider(root) if detect_provider_info
                               else (None, None))
    out = {
        "path": path,
        "present": os.path.isfile(path),
        "unparseable": None,
        "provider": provider,
        "providerHost": provider_host,
        "unknownProvider": provider_host if provider is None else None,
        "data": {},
        "namespaces": {name: {} for name in NAMESPACES},
        "shared": {},
        "specs": {},
        "ops": {},
        "proof": {},
        "legacyKeys": [],
        "migrationRefusal": None,
        "unknownKeys": [],
        "unknownNamespaces": [],
        "invalidNamespaces": [],
        "legacyPath": os.path.join(root, LEGACY_CONFIG_FILE)
        if os.path.isfile(os.path.join(root, LEGACY_CONFIG_FILE)) else None,
    }
    if not out["present"]:
        return out
    try:
        obj = json.loads(read_text(path) or "")
    except json.JSONDecodeError as exc:
        out["unparseable"] = str(exc)
        return out
    if not isinstance(obj, dict):
        out["unparseable"] = f"top level is {type(obj).__name__}, not an object"
        return out

    out["data"] = obj
    for name in NAMESPACES:
        value = obj.get(name)
        if isinstance(value, dict):
            out[name] = value
            out["namespaces"][name] = value
        elif name in obj:
            out["invalidNamespaces"].append(name)
    out["legacyKeys"] = sorted(key for key in obj if key in LEGACY_KEYS)
    envelope_keys = {"backend", *NAMESPACES}
    out["unknownKeys"] = sorted(
        key for key in obj if key not in envelope_keys and key not in LEGACY_KEYS
    )
    out["unknownNamespaces"] = sorted(
        key for key, value in obj.items()
        if isinstance(value, dict) and key not in envelope_keys and key not in LEGACY_KEYS
    )
    out["migrationRefusal"] = _migration_refusal(path, obj, out["legacyKeys"])
    return out
