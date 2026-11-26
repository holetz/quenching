"""`GET /api/modules` and `GET /api/deploy-plan` — the Módulos tab's read-only payloads.

The tab shows which modules the source offers and the target installs, the installed version
against the source's, and what `cq deploy` would change. The plan is `deploy.cli.deploy_plan`, the
SAME carrier `cq deploy --json` prints. Nothing here writes, and the portal has no route that
runs a deploy: the tab names the command and the human runs it.
"""
from __future__ import annotations

import shlex


def _command(root: str, modules: list[str]) -> str:
    """The `cq deploy` a human runs to apply the plan; displayed, never executed here."""
    return " ".join(["cq", "deploy", "--target", shlex.quote(root),
                     "--modules", shlex.quote(",".join(modules) or "core"), "--write"])


def modules_payload(root: str) -> tuple[int, dict]:
    """`(status, body)` for `GET /api/modules`."""
    from quenching.common.deploy import read_manifest
    from quenching.common.version import VERSION
    from quenching.deploy import tree

    try:
        source = tree.source_root()
        registry = tree.load_modules(source)
    except (OSError, ValueError) as exc:
        return 503, {"ok": False, "code": "sp-modules-source", "message": str(exc)}
    manifest = read_manifest(root) or {}
    recorded = manifest.get("modules")
    installed = [name for name in recorded if isinstance(name, str)] if isinstance(recorded, list) else []
    rows = []
    for module in registry["modules"]:
        owned = module.get("owned")
        if owned is None:
            continue
        name = module["name"]
        rows.append({"name": name, "short": tree.MODULE_SHORT.get(name, name),
                     "installed": name in installed, "core": tree.MODULE_SHORT.get(name) in tree.CORE.split(","),
                     "packages": list(owned.get("packages", [])),
                     "skills": list(owned.get("skills", []))})
    installedVersion = manifest.get("version")
    return 200, {"ok": True, "target": root, "source": str(source), "version": VERSION,
                 "installedVersion": installedVersion if isinstance(installedVersion, str) else None,
                 "deployed": bool(manifest), "modules": rows, "installed": installed,
                 "command": _command(root, installed)}


def plan_payload(root: str) -> tuple[int, dict]:
    """`(status, body)` for `GET /api/deploy-plan`: `cq deploy --json`, minus any write."""
    from pathlib import Path

    from quenching.deploy.cli import deploy_plan

    refusal, plan = deploy_plan(Path(root))
    if refusal:
        return 409, {"ok": False, **refusal}
    return 200, plan
