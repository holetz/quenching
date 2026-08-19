#!/usr/bin/env python3
"""Small dependency-free CI gate for the generated Codex plugin."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CQ_INVOCATION = re.compile(r"(?<![A-Za-z0-9_./-])cq\s+(?:specs|knowledge|components|git)\b")
CQ_COMMAND = re.compile(r'python3\s+"\$\(find .*quenching-codex.*/scripts/cq"')


def bash_blocks(text: str):
    lines = text.splitlines()
    in_bash = False
    block = []
    for line in lines:
        opening = re.match(r"^\s*```bash\s*$", line)
        if opening:
            in_bash = True
            block = []
        elif in_bash and re.match(r"^\s*```\s*$", line):
            yield "\n".join(block)
            in_bash = False
        elif in_bash:
            block.append(line)


def validate_cq_resolution(root: Path) -> None:
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert "../../scripts/cq" not in text, path
        for block in bash_blocks(text):
            if CQ_COMMAND.search(block):
                assert "quenching-codex" in block and "scripts/cq" in block, path
            elif CQ_INVOCATION.search(block):
                assert "cq() {" in block and "scripts/cq" in block, path


def main(path: str) -> int:
    root = Path(path)
    manifest = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "quenching-codex"
    assert manifest["version"] == (root / "VERSION").read_text(encoding="utf-8").strip()
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    assert len(skills) == 34, len(skills)
    for skill in skills:
        text = skill.read_text(encoding="utf-8")
        assert text.startswith("---\n") and "\n---\n" in text, skill
        front = text[4:text.index("\n---\n", 4)]
        assert re.search(r"^name: [a-z0-9-]+$", front, re.MULTILINE), skill
        assert re.search(r"^description: .+", front, re.MULTILINE), skill
        assert "[TODO:" not in text, skill
    validate_cq_resolution(root)
    print(f"validated {root} ({len(skills)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "plugins/quenching-codex"))
