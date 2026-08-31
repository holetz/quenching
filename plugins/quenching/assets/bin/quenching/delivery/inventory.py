"""Build the delivery front's static workflow inventory."""
from __future__ import annotations

import os
import re
from pathlib import Path

from quenching.delivery.model import DeliveryInventory, Job, Workflow
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


def _job_blocks(lines: list[str]) -> list[tuple[str, list[str]]]:
    block = _block(lines, "jobs")
    starts = [(index, match.group(1)) for index, line in enumerate(block[1:], 1)
              if (match := _CHILD.match(line))]
    result: list[tuple[str, list[str]]] = []
    for position, (start, name) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(block)
        result.append((name, block[start:end]))
    return result


def _key_value(line: str, key: str) -> tuple[int, str] | None:
    match = re.match(rf"^(\s*){re.escape(key)}:\s*(.*?)\s*$", line)
    return (len(match.group(1)), _strip_comment(match.group(2))) if match else None


def _inline_values(value: str) -> tuple[str, ...]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return tuple(item.strip(" '\"") for item in value[1:-1].split(",") if item.strip())
    return (value.strip(" '\""),) if value else ()


def _values_after(lines: list[str], key: str) -> tuple[str, ...]:
    for index, line in enumerate(lines):
        found = _key_value(line, key)
        if found is None:
            continue
        indent, inline = found
        values = list(_inline_values(inline))
        for child in lines[index + 1:]:
            child_indent = len(child) - len(child.lstrip())
            if child.strip() and child_indent <= indent:
                break
            if (match := _LIST.match(child)):
                values.append(_strip_comment(match.group(1)))
        return tuple(sorted(set(values)))
    return ()


def _job(lines: list[str], name: str) -> Job:
    actions = tuple(sorted(set(match.group(1) for line in lines
                                if (match := re.search(r"\buses:\s*([^\s#]+)", line)))))
    commands = tuple(_strip_comment(found.group(1)) for line in lines
                     if (found := re.match(r"^\s*run:\s*(.*?)\s*$", line)) and found.group(1))
    runtimes: list[str] = []
    for line in lines:
        match = re.search(r"\b(python|node|ruby|java|go|rust)[-_]version:\s*([^\s#]+)",
                          line, re.IGNORECASE)
        if match:
            runtimes.append(match.group(1).lower() + ":" + match.group(2).strip(" '\""))
    environment = next((found.group(1).strip(" '\"") for line in lines
                        if (found := re.match(r"^\s*environment:\s*(.+?)\s*$", line))), None)
    stage = next((found.group(1).strip(" '\"") for line in lines
                  if (found := re.match(r"^\s*stage:\s*(.+?)\s*$", line))), None)
    permissions = _values_after(lines, "permissions")
    release = bool(re.search(r"(?i)(release|publish|deploy)", name)
                   or any(re.search(r"(?i)(gh\s+release|npm\s+publish|twine\s+upload|docker\s+push|publish)", value)
                          for value in commands)
                   or any(re.search(r"(?i)(release|publish|deploy)", action) for action in actions))
    active = not any(re.search(r"^\s*if:\s*(?:\$\{\{\s*)?(?:false|never)(?:\s*\}\})?\s*$", line, re.IGNORECASE)
                     for line in lines)
    return Job(
        name=name,
        needs=_values_after(lines, "needs"),
        commands=commands,
        actions=actions,
        checkout=any(action.startswith("actions/checkout@") for action in actions),
        setup=any(action.startswith("actions/setup-") for action in actions),
        runtimes=tuple(sorted(set(runtimes))),
        stage=stage,
        release=release,
        environment=environment,
        permissions=permissions,
        active=active,
    )


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
    jobs = _mapping_names(lines, "jobs")
    return Workflow(
        relative,
        provider,
        kind,
        "ok",
        triggers=_triggers(lines),
        jobs=jobs,
        stages=_list_values(lines, "stages"),
        job_details=tuple(_job(block, name) for name, block in _job_blocks(lines)),
        permissions=_values_after(lines, "permissions"),
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
