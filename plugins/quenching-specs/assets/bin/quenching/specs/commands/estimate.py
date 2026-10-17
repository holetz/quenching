"""Declared build reading by task section, explicitly a heuristic rather than telemetry."""
from __future__ import annotations

import re
from pathlib import Path

from quenching.specs.backends import open_backend
from quenching.specs.commands.output import Emitter, read_one
from quenching.specs.parse.tasks import _files_bad_annotation
from quenching.specs.parse.text import STANDARD_PATH_RE, strip_comments
from quenching.specs.schema import headings_for_moment


WORKER_BUDGET_TOKENS = 100000
BYTES_PER_TOKEN = 4
EXCLUDED = [
    "host/system/harness overhead", "conditional execute references", "tool/test output",
    "iteration count", "growing conversation history", "generated code",
]
EXECUTE_BODY = Path(__file__).resolve().parents[5] / "commands/specs/execute.md"


def _file_size(root: Path, entry: str, standard: bool = False) -> dict:
    annotation = _files_bad_annotation(entry)
    raw = re.sub(r"\s*\(new\)\s*$", "", entry).strip()
    # Standards use the bundle's canonical /docs/ spelling, not an OS absolute path.
    if standard:
        raw = raw.lstrip("/")
    path = Path(raw)
    if annotation or path.is_absolute() or not raw:
        return {"path": entry, "bytes": None, "reason": "not a repository-relative file"}
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        return {"path": entry, "bytes": None, "reason": "path escapes repository"}
    label = resolved.relative_to(root).as_posix()
    try:
        size = resolved.stat().st_size if resolved.is_file() else None
    except OSError:
        size = None
    return {"path": label, "bytes": size,
            **({"reason": "missing, new or unreadable file"} if size is None else {})}


def estimate_build(info: dict, root: str | Path, budget: int = WORKER_BUDGET_TOKENS,
                   preamble: Path = EXECUTE_BODY) -> dict:
    """Load no task file contents: sizes and the backend's parsed document are enough."""
    root = Path(root).resolve()
    impact = strip_comments(info["sections"].get("Impact", {}).get("body", ""))
    standards = sorted(set(STANDARD_PATH_RE.findall(impact)))
    build_bytes = sum(len(info["sections"].get(h, {}).get("body", "").encode("utf-8"))
                      for h in headings_for_moment("build"))
    try:
        preamble_bytes = preamble.stat().st_size
        preamble_missing = False
    except OSError:
        preamble_bytes, preamble_missing = 0, True
    common_bytes = preamble_bytes + build_bytes
    groups: dict[int, list] = {}
    for task in info["tasks"]:
        groups.setdefault(task["section"], []).append(task)
    rows = []
    for section, tasks in groups.items():
        files: dict[str, dict] = {}
        for entry in standards:
            row = _file_size(root, entry, standard=True)
            files[row["path"]] = row
        for task in tasks:
            for entry in task["files"]:
                row = _file_size(root, entry)
                files[row["path"]] = row
        unresolved = [{"path": row["path"], "reason": row["reason"]}
                      for row in files.values() if row["bytes"] is None]
        unresolved.extend({"task": task["id"], "reason": "no files declared"}
                          for task in tasks if not task["files"])
        if preamble_missing:
            unresolved.append({"path": str(preamble), "reason": "execute preamble unavailable"})
        byte_count = common_bytes + sum(row["bytes"] or 0 for row in files.values())
        tokens = (byte_count + BYTES_PER_TOKEN - 1) // BYTES_PER_TOKEN
        rows.append({"section": section, "tasks": [task["id"] for task in tasks],
                     "taskCount": len(tasks), "files": sorted(files.values(), key=lambda r: r["path"]),
                     "bytes": byte_count, "estimatedTokens": tokens, "unresolved": unresolved,
                     "complete": not unresolved, "overBudget": tokens > budget})
    peak = max((row["estimatedTokens"] for row in rows), default=0)
    return {"kind": "estimated-declared-reading", "method": "ceil(UTF-8 bytes / 4)",
            "workerBudgetTokens": budget, "budgetSource": "S2 worker policy (spec 1629)",
            "preamble": {"source": str(preamble), "bytes": preamble_bytes,
                         "available": not preamble_missing}, "specBuildBytes": build_bytes,
            "standards": standards, "sections": rows, "maxSectionTokens": peak,
            "totalReadTokens": sum(row["estimatedTokens"] for row in rows),
            "complete": bool(rows) and all(row["complete"] for row in rows),
            "overBudget": peak > budget, "excluded": EXCLUDED,
            "uncertainty": "Incomplete build forecast: below budget never proves the build fits; "
                           "unknown files and excluded overhead can dominate. "
                           "totalReadTokens is reading volume, not a context peak."}


def cmd_estimate(args, root: str, out: Emitter) -> int:
    if args.worker_budget is None:
        from quenching.common.config import setting
        args.worker_budget, warning = setting(
            root, "shared", "contextBudgets.worker", WORKER_BUDGET_TOKENS,
            lambda v: isinstance(v, int) and not isinstance(v, bool) and v > 0)
        if warning:
            print(f"warning: {warning}", file=sys.stderr)
    if args.worker_budget <= 0:
        return out.emit_err(args.json, {"code": "sp-bad-worker-budget", "exit": 2,
                                       "message": "worker budget must be a positive token count"})
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    info, err = read_one(backend, args.spec, out)
    if err:
        return out.emit_err(args.json, err)
    payload = {"ok": True, "id": info["id"], **estimate_build(info, root, args.worker_budget)}
    human = (f"{info['id']} — estimated declared reading (UTF-8 bytes / 4)\n"
             f"  max section: {payload['maxSectionTokens']} estimated tokens / "
             f"worker budget: {args.worker_budget}\n")
    for row in payload["sections"]:
        human += (f"  section {row['section']}: {row['estimatedTokens']} estimated tokens; "
                  f"{row['taskCount']} tasks; {len(row['unresolved'])} unresolved inputs\n")
    human += ("  Known reading exceeds budget: propose epic decomposition before approval.\n"
              if payload["overBudget"] else "  No known-reading excess; this is NOT a build-fit verdict.\n")
    if not payload["complete"]:
        human += "  Declared input coverage is incomplete.\n"
    human += "  Excluded: " + "; ".join(payload["excluded"]) + "\n" + payload["uncertainty"]
    out.emit(args.json, payload, human)
    return 0
