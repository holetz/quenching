#!/usr/bin/env python3
"""Validate the repository harness: AGENTS.md is the source, CLAUDE.md imports it.

Checks meaning, not size: the import exists, the `Language:` and `Ephemeral writes:` lines exist,
the single gate and both safety rules are stated, the scoped rules exist with `paths:`, and every
repository path the harness cites resolves.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_MD = ROOT / "AGENTS.md"
CLAUDE_MD = ROOT / "CLAUDE.md"
RULES_DIR = ROOT / ".claude" / "rules"

REQUIRED_AGENTS = {
    "Language line": r"(?m)^Language: [A-Za-z]{2,3}(-[A-Za-z0-9]+)* — the contract is /docs/standards/agents/communication\.md\.?$",
    "Ephemeral writes line": r"(?m)^Ephemeral writes: \.quenching/ — the contract is /docs/standards/agents/ephemeral-writes\.md$",
    "single gate": r"bash scripts/verify_repo\.sh",
    "context: fork safety rule": r"Do not add `context: fork`",
    "haiku safety rule": r"Never downgrade classification or executor sub-agents to `haiku`",
}
STALE = ("stale-doc` is advisory", "This size check measures CLAUDE.md only")
SCOPED_RULES = {
    "command-fork.md": ("plugins/quenching/commands/**", "context: fork"),
    "import-memory-models.md": (
        "plugins/quenching/commands/knowledge/import-memory.md",
        "haiku",
    ),
}
CITED = re.compile(
    r"\]\((?!https?:|#)([^)#\s]+)|`((?:plugins|docs|scripts)/[^`\s*]+)`|`(/docs/[^`\s*]+)`"
)


def check() -> list[str]:
    errors: list[str] = []
    if not AGENTS_MD.is_file():
        return ["AGENTS.md is missing"]
    agents = AGENTS_MD.read_text(encoding="utf-8")
    if not CLAUDE_MD.is_file():
        errors.append("CLAUDE.md is missing")
    elif not re.search(r"(?m)^@AGENTS\.md\s*$", CLAUDE_MD.read_text(encoding="utf-8")):
        errors.append("CLAUDE.md does not import @AGENTS.md")
    for name, pattern in REQUIRED_AGENTS.items():
        if not re.search(pattern, agents):
            errors.append(f"AGENTS.md is missing: {name}")
    for text in STALE:
        if text in agents:
            errors.append(f"AGENTS.md carries a stale or proxy statement: {text}")
    for filename, (path_glob, needle) in SCOPED_RULES.items():
        rule = RULES_DIR / filename
        if not rule.is_file():
            errors.append(f"missing scoped rule: .claude/rules/{filename}")
            continue
        body = rule.read_text(encoding="utf-8")
        if not body.startswith("---\n") or "paths:" not in body.split("---", 2)[1]:
            errors.append(f".claude/rules/{filename} has no `paths:` frontmatter")
        if path_glob not in body or needle not in body:
            errors.append(f".claude/rules/{filename} does not scope `{needle}` to {path_glob}")
    for match in CITED.finditer(agents):
        cited = next(group for group in match.groups() if group)
        target = ROOT / cited.lstrip("/")
        if not target.exists():
            errors.append(f"AGENTS.md cites a path that does not exist: {cited}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="accepted for compatibility")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors = check()
    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    else:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        if not errors:
            print("harness ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
