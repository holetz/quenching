#!/usr/bin/env python3
"""Small dependency-free CI gate for the generated Codex plugin."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


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
    print(f"validated {root} ({len(skills)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "plugins/quenching-codex"))
