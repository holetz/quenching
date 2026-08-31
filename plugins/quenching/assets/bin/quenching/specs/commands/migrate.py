"""Retirement boundary for the removed local specs backend.

External providers own the canonical spec documents, so filesystem layout migrations are no
longer meaningful. The command remains as an explicit refusal for installed callers that still
invoke it, rather than silently pretending to migrate a local workspace.
"""
from __future__ import annotations

from quenching.common.config import load_config
from quenching.specs.commands.output import Emitter


def cmd_migrate(args, root: str, out: Emitter) -> int:
    cfg = load_config(root)
    return out.emit_err(args.json, {
        "code": "sp-local-backend-removed",
        "exit": 2,
        "backend": cfg.get("provider") or cfg.get("backend"),
        "message": "`cq specs migrate` only migrated the removed local files backend; "
                   "specs now live in the repository provider and need no local migration",
    })
