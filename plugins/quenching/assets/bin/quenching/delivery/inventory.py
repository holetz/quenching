"""Build the delivery front's static workflow inventory."""
from __future__ import annotations

import os
import re
from pathlib import Path

from quenching.delivery.model import DeliveryInventory, Workflow
from quenching.delivery.probe import probe_delivery, workflow_artifacts


_TOP_LEVEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):(?:\s*(.*?))?\s*$")
_CHILD = re.compile(r"^  ([A-Za-z_][A-Za-z0-9_.-]*):(?:\s*(.*?))?\s*$")
_LIST = re.compile(r"^\s*-\s*([^\s#]+)")


def _read(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except FileNotFoundError:
        return None, "missing"
    except (OSError, UnicodeDecodeError):
        return None, "unreadable"


def _strip_comment(value: str) -> str:
    return value.split(" #", 1)[0].strip()


def _block(lines: list[str], heading: str) -> list[str]:
    start = next((index for index, line in enumerate(lines)
                  if _TOP_LEVEL.match(line) and _TOP_LEVEL.match(line).group(1) == heading), None)
    if start is None:
        return []
    end = next((index for index in range(start + 1, len(lines))
                if _TOP_LEVEL.match(lines[index])), len(lines))
    return lines[start:end]


def _mapping_names(lines: list[str], heading: str) -> tuple[str, ...]:
    block = _block(lines, heading)
    return tuple(sorted(match.group(1) for line in block[1:]
                         if (match := _CHILD.match(line))))


def _list_values(lines: list[str], heading: str) -> tuple[str, ...]:
    block = _block(lines, heading)
    return tuple(sorted({_strip_comment(match.group(1)) for line in block[1:]
                         if (match := _LIST.match(line))}))


def _triggers(lines: list[str]) -> tuple[str, ...]:
    block = _block(lines, "on") or _block(lines, "trigger")
    if not block:
        return ()
    first = _TOP_LEVEL.match(block[0])
    inline = _strip_comment(first.group(2) or "") if first else ""
    if inline and inline not in {"{}", "null"}:
        if inline.startswith("[") and inline.endswith("]"):
            return tuple(sorted(item.strip(" '\"") for item in inline[1:-1].split(",")
                                if item.strip()))
        return (inline.strip(" '\""),)
    return tuple(sorted(match.group(1) for line in block[1:]
                         if (match := _CHILD.match(line))))


def _workflow(root: Path, relative: str, provider: str, kind: str) -> Workflow:
    text, error = _read(root / relative)
    if error:
        return Workflow(relative, provider, kind, error)
    assert text is not None
    lines = text.splitlines()
    return Workflow(
        relative,
        provider,
        kind,
        "ok",
        triggers=_triggers(lines),
        jobs=_mapping_names(lines, "jobs"),
        stages=_list_values(lines, "stages"),
    )


def build_inventory(root: str) -> tuple[DeliveryInventory | None, dict]:
    """Return one inventory for an applicable target, or its refusal payload."""
    repo_root = Path(os.path.abspath(root))
    applicability = probe_delivery(str(repo_root))
    if applicability.state == "refused":
        return None, applicability.config_error
    if applicability.state != "applicable":
        return None, {}
    workflows = tuple(_workflow(repo_root, relative, provider, kind)
                      for relative, provider, kind in workflow_artifacts(repo_root))
    unreadable = next((workflow for workflow in workflows if workflow.parse != "ok"), None)
    if unreadable:
        return None, {
            "code": "delivery-workflow-unreadable",
            "exit": 2,
            "path": unreadable.path,
            "message": f"workflow `{unreadable.path}` could not be read",
        }
    return DeliveryInventory(str(repo_root), applicability, workflows), {}
