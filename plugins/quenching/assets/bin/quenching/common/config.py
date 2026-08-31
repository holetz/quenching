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

# Root-level keys accepted by the pre-envelope format. They remain visible to the front
# adapters while the extraction is completed; the migration refusal is their concern.
LEGACY_KEYS = frozenset({
    "worktreeSetup", "sharedPaths", "specsBranch", "azureStates", "hooks", "profiles",
    "azurePlacement", "azureColumns", "subjects", "tagCatalog", "workItemTypes",
    "fanoutMinComplexity", "opsRoot", "router", "registry", "proofRoot", "layers",
    "measuredRoots", "proofExclusions", "ratchetPath",
})


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
    top = _git(specs_root, "rev-parse", "--show-toplevel").strip()
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
        "unknownKeys": [],
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
    return out
