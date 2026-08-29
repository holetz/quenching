"""Small deterministic Markdown/YAML helpers for generated design artifacts."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def split_h2(markdown: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in markdown.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1)
            sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def read_sections(paths: list[Path]) -> dict[str, list[str]]:
    collected: dict[str, list[str]] = {}
    for path in paths:
        try:
            sections = split_h2(path.read_text(encoding="utf-8"))
        except OSError:
            continue
        for heading, body in sections.items():
            if body:
                collected.setdefault(heading, []).append(body)
    return collected


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def yaml_map(value: dict[str, Any], indent: int = 0) -> list[str]:
    lines: list[str] = []
    pad = " " * indent
    for key, item in value.items():
        safe_key = key if re.fullmatch(r"[A-Za-z0-9_-]+", str(key)) else yaml_scalar(key)
        if isinstance(item, dict):
            lines.append(f"{pad}{safe_key}:")
            lines.extend(yaml_map(item, indent + 2))
        else:
            lines.append(f"{pad}{safe_key}: {yaml_scalar(item)}")
    return lines


def parse_yaml_subset(text: str) -> dict[str, Any]:
    """Parse the map-only YAML subset Impeccable 4.1.2 itself accepts."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or re.match(r"^\s*#", raw):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        content = raw[indent:]
        colon = _top_level_colon(content)
        if colon < 0:
            continue
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()
        key = _parse_scalar(content[:colon].strip())
        rest = _strip_comment(content[colon + 1:].strip())
        parent = stack[-1][1]
        if not isinstance(key, str):
            key = str(key)
        if not rest:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(rest)
    return root


def parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("DESIGN.md must start with YAML frontmatter")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("DESIGN.md frontmatter is not closed") from exc
    return parse_yaml_subset("\n".join(lines[1:end])), "\n".join(lines[end + 1:]).lstrip("\n")


def parse_document_frontmatter(markdown: str) -> tuple[dict[str, str], str]:
    """Parse the flat frontmatter used by genre documents."""
    front, body = parse_frontmatter(markdown)
    return {str(key): str(value) for key, value in front.items()}, body


def _top_level_colon(value: str) -> int:
    quote: str | None = None
    for index, char in enumerate(value):
        if quote:
            if char == quote and (index == 0 or value[index - 1] != "\\"):
                quote = None
        elif char in {'"', "'"}:
            quote = char
        elif char == ":":
            return index
    return -1


def _strip_comment(value: str) -> str:
    quote: str | None = None
    for index, char in enumerate(value):
        if quote:
            if char == quote and value[index - 1] != "\\":
                quote = None
        elif char in {'"', "'"}:
            quote = char
        elif char == "#" and index > 0 and value[index - 1].isspace():
            return value[:index].rstrip()
    return value

def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if value == "true":
        return True
    if value == "false":
        return False
    if value in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?(?:\d+\.\d*|\.\d+)", value):
        return float(value)
    return value
