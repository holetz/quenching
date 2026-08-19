#!/usr/bin/env python3
"""Measure and guard the repository's always-loaded Claude harness.

The Claude system prompt and its runtime registry are deliberately reported as
unavailable. Source descriptions are an inventory signal, not a measurement
of the runtime prompt.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_MD = ROOT / "CLAUDE.md"
COMMANDS_DIR = ROOT / "plugins" / "quenching" / "commands"
BASELINE_BYTES = 8_548
MAX_BYTES = BASELINE_BYTES // 2


def _utf8_bytes(value: str) -> int:
    return len(value.encode("utf-8"))


def _description(text: str) -> str:
    """Return the frontmatter description without parsing the whole schema."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    lines = parts[1].splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^description:\s*(.*)$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if value in {">", ">-", "|", "|-"}:
            continuation: list[str] = []
            for next_line in lines[index + 1 :]:
                if next_line and not next_line[0].isspace():
                    break
                continuation.append(next_line.strip())
            value = " ".join(item for item in continuation if item)
        return value
    return ""


def _source_descriptions() -> dict[str, int]:
    count = 0
    bytes_total = 0
    if COMMANDS_DIR.is_dir():
        for path in sorted(COMMANDS_DIR.rglob("*.md")):
            value = _description(path.read_text(encoding="utf-8"))
            if value:
                count += 1
                bytes_total += _utf8_bytes(value)
    return {"count": count, "source_bytes": bytes_total}


def _section_inventory(text: str) -> list[dict[str, int | str]]:
    headings = list(re.finditer(r"(?m)^#{1,3} .+$", text))
    result: list[dict[str, int | str]] = []
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[match.start() : end]
        result.append(
            {
                "heading": match.group(0).strip(),
                "bytes": _utf8_bytes(section),
                "lines": section.count("\n"),
            }
        )
    return result


def report() -> dict[str, object]:
    text = CLAUDE_MD.read_text(encoding="utf-8")
    descriptions = _source_descriptions()
    return {
        "baseline": {"bytes": BASELINE_BYTES, "max_bytes": MAX_BYTES},
        "claude_md": {
            "path": "CLAUDE.md",
            "bytes": CLAUDE_MD.stat().st_size,
            "lines": len(text.splitlines()),
            "sections": _section_inventory(text),
        },
        "command_descriptions_source": descriptions,
        "external": {
            "system_prompt": {
                "status": "unavailable",
                "bytes": None,
                "reason": "provided by the Claude runtime, not this checkout",
            },
            "registered_descriptions": {
                "status": "unavailable",
                "bytes": None,
                "reason": "runtime registry size is not derivable from source files",
                "source_inventory": descriptions,
            },
            "active_command_body": {
                "status": "unavailable",
                "bytes": None,
                "reason": "no active command is selected by this static check",
            },
        },
    }


def check(data: dict[str, object]) -> list[str]:
    text = CLAUDE_MD.read_text(encoding="utf-8")
    claude = data["claude_md"]
    assert isinstance(claude, dict)
    errors: list[str] = []
    if claude["bytes"] > MAX_BYTES:
        errors.append(f"CLAUDE.md is {claude['bytes']} bytes; limit is {MAX_BYTES}")
    for marker in (
        "Language: pt-BR — the contract is /.knowledge/standards/agents/communication.md.",
        "plugins/quenching/README.md",
        ".knowledge/index.md",
        "plugins/quenching/assets/bin/cq",
        "context: fork",
        "Never downgrade classification",
    ):
        if marker not in text:
            errors.append(f"missing required harness marker: {marker}")
    for path in (
        ROOT / ".knowledge" / "index.md",
        ROOT / ".knowledge" / "standards" / "agents" / "communication.md",
        ROOT / "plugins" / "quenching" / "README.md",
        ROOT / "plugins" / "quenching" / "assets" / "bin" / "cq",
    ):
        if not path.exists():
            errors.append(f"missing local target: {path.relative_to(ROOT)}")
    for heading in (
        "## Where knowledge lives",
        "## The plugin itself",
        "### Two rules that must survive any refactor",
    ):
        if heading in text:
            errors.append(f"duplicated operational block remains: {heading}")
    for component in ("system_prompt", "registered_descriptions", "active_command_body"):
        external = data["external"]
        assert isinstance(external, dict)
        value = external[component]
        assert isinstance(value, dict)
        if value["status"] != "unavailable" or value["bytes"] is not None:
            errors.append(f"external component {component} was presented as measured")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = report()
    errors = check(data) if args.check else []
    payload = {"ok": not errors, "errors": errors, **data}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
