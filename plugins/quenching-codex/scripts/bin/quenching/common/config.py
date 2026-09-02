"""Read the repository-wide configuration envelope.

The file is shared by every front, while each namespace remains owned by its adapter. This
module only discovers the configuration home, parses the envelope and derives the provider; it
does not interpret a front's values.
"""
from __future__ import annotations

import json
import os

from quenching.common.git import _git
from quenching.common.io import read_text, write_text


CONFIG_FILE = os.path.join(".agents", "quenching.json")
LEGACY_CONFIG_FILE = "config.json"
NAMESPACES = ("shared", "specs", "ops", "proof", "delivery")

# Root-level keys accepted by the pre-envelope format. They are diagnostic-only now: a front
# adapter must refuse to interpret them because doing so makes a half-migrated repository look
# healthy while one namespace silently wins over another.
LEGACY_KEYS = frozenset({
    "worktreeSetup", "sharedPaths", "specsBranch", "azureStates", "hooks", "profiles",
    "azurePlacement", "azureColumns", "subjects", "tagCatalog", "workItemTypes",
    "fanoutMinComplexity", "opsRoot", "router", "registry", "proofRoot", "layers",
    "measuredRoots", "proofExclusions", "ratchetPath", "gitConventions",
})

LEGACY_DESTINATIONS = {
    "worktreeSetup": "shared",
    "sharedPaths": "shared",
    "hooks": "shared",
    "profiles": "shared",
    "gitConventions": "shared",
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
        "delivery": {},
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


def namespace(config: dict, name: str) -> dict:
    """Return one parsed namespace without letting a caller fall back to another one.

    The envelope is the shared loader's boundary; this small accessor keeps adapters from
    reaching through it with a flat-key fallback.  A malformed or absent namespace is an empty
    declaration and remains the owning adapter's decision to accept or refuse.
    """
    namespaces = config.get("namespaces")
    if not isinstance(namespaces, dict):
        return {}
    value = namespaces.get(name)
    return value if isinstance(value, dict) else {}


def detect_profile(root: str, backend: str | None = None) -> list[str]:
    """Detect the fronts with a local signal for a first-use profile.

    This is deliberately a conservative signal inventory, not an align implementation. It
    only names a front when the same inexpensive filesystem evidence that `/align` documents is
    present. The provider-owned `specs` axis is included when a backend is known, because its
    external document store has no local directory to probe.
    """
    repo = os.path.abspath(root)

    def has_executable(directory: str) -> bool:
        path = os.path.join(repo, directory)
        if not os.path.isdir(path):
            return False
        try:
            with os.scandir(path) as entries:
                return any(entry.is_file() and os.access(entry.path, os.X_OK)
                           for entry in entries)
        except OSError:
            return False

    def has_file(directory: str) -> bool:
        path = os.path.join(repo, directory)
        if not os.path.isdir(path):
            return False
        try:
            with os.scandir(path) as entries:
                return any(entry.is_file() for entry in entries)
        except OSError:
            return False

    detected: list[str] = []
    if os.path.isdir(os.path.join(repo, "docs")):
        detected.append("knowledge")
    if any(os.path.exists(os.path.join(repo, name))
           for name in (".design", "PRODUCT.md", "DESIGN.md")):
        detected.append("design")
    if any(has_file(name) for name in (os.path.join(".claude", "commands"),
                                       os.path.join(".agents", "skills"), "commands")):
        detected.append("components")
    if any(has_executable(name) for name in ("scripts", "tools", "bin", "script")):
        detected.append("ops")
    if any(has_file(name) for name in ("tests", "test")):
        detected.append("proof")
    if any(os.path.isfile(os.path.join(repo, name)) for name in (
            "pyproject.toml", "setup.cfg", "package.json", "Cargo.toml", "uv.lock",
            "poetry.lock", "package-lock.json", "Cargo.lock", ".python-version", ".nvmrc")):
        detected.append("toolchain")
    if any(has_file(name) for name in (os.path.join(".github", "workflows"),
                                       ".azure-pipelines", ".gitlab")):
        detected.append("delivery")
    if backend:
        # `specs` is not part of LOCAL_FRONT_ORDER because it has no local align row. Keeping it
        # beside knowledge still makes the generated profile stable and human-readable.
        detected.insert(1 if detected and detected[0] == "knowledge" else 0, "specs")
    return detected


def prepare_minimal_config(root: str) -> tuple[dict | None, dict]:
    """Prepare the first-use envelope without writing it or clobbering an existing one."""
    repo = os.path.abspath(find_repo_root(root))
    path = os.path.join(repo, CONFIG_FILE)
    if os.path.isfile(path):
        return None, {
            "code": "cq-config-present",
            "exit": 2,
            "config": path,
            "message": f"{CONFIG_FILE} already exists; setup will not overwrite it",
            "remedy": f"use the existing {CONFIG_FILE}, or edit it explicitly before rerunning doctor",
        }
    backend, host = detect_provider(repo)
    if not backend:
        return None, {
            "code": "cq-setup-provider-missing",
            "exit": 2,
            "config": path,
            "provider": host,
            "message": "first-use setup could not detect a GitHub or Azure DevOps provider",
            "remedy": "configure an origin remote for GitHub or Azure DevOps, then rerun `cq doctor --setup`",
        }
    profile = detect_profile(repo, backend)
    document = {
        "backend": backend,
        "shared": {"profiles": {"installed": profile}},
    }
    return {"path": path, "backend": backend, "profile": profile, "document": document}, {}


def write_minimal_config(root: str) -> tuple[dict | None, dict]:
    """Write the prepared first-use envelope after the caller's explicit confirmation."""
    plan, error = prepare_minimal_config(root)
    if error:
        return None, error
    assert plan is not None
    os.makedirs(os.path.dirname(plan["path"]), exist_ok=True)
    write_text(plan["path"], json.dumps(plan["document"], indent=2, ensure_ascii=False) + "\n")
    return {**plan, "written": True}, {}
