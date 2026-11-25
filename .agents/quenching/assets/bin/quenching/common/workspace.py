"""The VS Code workspace settings that keep generated trees out of search and long flows running.

One source for the block, the snippet and the per-key report: `cq deploy` seeds
`.vscode/settings.json` from it and `cq doctor` reports it. `files.exclude` is the setting that
excludes a path from the Explorer, from text search and from the semantic index; `search.exclude`
would keep the files visible and only narrow text search and grep, so it is not part of the block.

The seeds are opted in by the repository's own `shared.workspace.vscode`, read from the repository
document and never from the merged envelope: a client projection written here must not vary by
machine.
"""
from __future__ import annotations

import json
import os

from quenching.common.config import repository_document
from quenching.common.io import read_text
from quenching.common.jsonc import jsonc_loads

PATH = ".vscode/settings.json"
# Root-relative on purpose: a settings glob without `**/` matches at the workspace root only, so a
# nested `site` fixture the `.gitignore` reopens is not hidden.
EXCLUDED = (".agents/quenching", ".claude/skills", "site", "site-source")
# The client's default is 25 (VS Code reference, consulted 2026-11-25); long flows need more room.
MAX_REQUESTS = 100
KEYS = ("files.exclude", "chat.agent.maxRequests")
_HEADER = (
    "// The quenching workspace settings: keep the generated copies out of the Explorer, the\n"
    "// text search and the semantic index, and give a long agent run room before it asks to\n"
    "// continue. `cq doctor --workspace` checks this file.\n"
)


def recommended() -> dict:
    """The block's values, as the report and the snippet both read them."""
    return {"files.exclude": {path: True for path in EXCLUDED},
            "chat.agent.maxRequests": MAX_REQUESTS}


def snippet() -> str:
    """The JSONC block the doctor prints and the deploy seeds, comments included."""
    return _HEADER + json.dumps(recommended(), indent=2, ensure_ascii=False) + "\n"


def declared(root: str) -> tuple[bool, str | None]:
    """`shared.workspace.vscode` from the repository document only, as `(value, error)`.

    `error` names a malformed block and is never a value: the deploy refuses rather than guess.
    An unknown configuration provider is not this key's finding, so it reads as absent.
    """
    document, _info, refusal = repository_document(str(root))
    if refusal:
        return False, None
    shared = (document or {}).get("shared")
    workspace = shared.get("workspace") if isinstance(shared, dict) else None
    if workspace is None:
        return False, None
    if not isinstance(workspace, dict):
        return False, "`shared.workspace` must be an object with the `vscode` key"
    unknown = sorted(set(workspace) - {"vscode"})
    if unknown:
        return False, f"`shared.workspace` has unknown key(s): {', '.join(unknown)}"
    value = workspace.get("vscode", False)
    if not isinstance(value, bool):
        return False, "`shared.workspace.vscode` must be true or false"
    return value, None


def report(root: str, declared_value: bool | None = None) -> dict:
    """What `.vscode/settings.json` carries: its state, the recommended keys and the gaps.

    Read-only, and tolerant by design: an absent file, an unreadable one and a partial block are
    all facts the doctor reports, never errors that stop a deploy.
    """
    value = declared(root)[0] if declared_value is None else declared_value
    path = os.path.join(str(root), PATH)
    out = {"path": PATH, "declared": value, "state": "absent",
           "keys": {key: False for key in KEYS}, "missing": list(KEYS),
           "excluded": [], "missingExclusions": list(EXCLUDED),
           "maxRequests": None, "complete": False}
    if not os.path.isfile(path):
        return out
    text = read_text(path)
    if text is None:
        return {**out, "state": "unreadable", "reason": "the file is not readable UTF-8 text"}
    try:
        document = jsonc_loads(text)
    except ValueError as error:
        return {**out, "state": "unreadable", "reason": str(error)}
    if not isinstance(document, dict):
        return {**out, "state": "unreadable", "reason": "the root must be an object"}
    excluded = document.get("files.exclude")
    excluded = excluded if isinstance(excluded, dict) else {}
    present = [pattern for pattern in EXCLUDED if excluded.get(pattern) is True]
    ceiling = document.get("chat.agent.maxRequests")
    ceiling = ceiling if isinstance(ceiling, int) and not isinstance(ceiling, bool) else None
    missing = [key for key in KEYS if key not in document]
    return {"path": PATH, "declared": value, "state": "present",
            "keys": {key: key in document for key in KEYS},
            "missing": missing, "excluded": present,
            "missingExclusions": [path for path in EXCLUDED if path not in present],
            "maxRequests": ceiling,
            "complete": (not missing and len(present) == len(EXCLUDED)
                         and ceiling is not None and ceiling >= MAX_REQUESTS)}
