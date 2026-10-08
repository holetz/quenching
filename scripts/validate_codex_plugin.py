#!/usr/bin/env python3
"""Small dependency-free CI gate for the generated Codex plugin."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CQ_INVOCATION = re.compile(r"(?<![A-Za-z0-9_./-])cq\s+(?:specs|knowledge|components|git)\b")
CQ_COMMAND = re.compile(r'python3\s+"\$\(find .*quenching-codex.*/scripts/cq"')


class ValidationError(Exception):
    """A failed check; explicit, so `python -O` cannot strip it the way it strips `assert`."""


def check(condition: bool, detail: object) -> None:
    if not condition:
        raise ValidationError(str(detail))


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
        for block in bash_blocks(text):
            # Scoped to the executable blocks: prose legitimately names the relative path
            # when explaining how resolution works, and the file-wide form banned that too.
            check("../../scripts/cq" not in block, path)
            if CQ_COMMAND.search(block):
                check("quenching-codex" in block and "scripts/cq" in block, path)
            elif CQ_INVOCATION.search(block):
                check("cq() {" in block and "scripts/cq" in block, path)


AGENT_PATH = re.compile(r"(?:plugins/quenching(?:-codex)?/|\.\./\.\./)agents/([a-z][a-z0-9-]*)\.md")
AGENT_NAME = re.compile(r"(?<![A-Za-z0-9_/.-])quenching:([a-z][a-z0-9-]*)(?![A-Za-z0-9:-])")


def validate_agent_citations(root: Path) -> None:
    """A skill may not cite an agent the Codex tree does not carry.

    `translate --check` compares bytes against the source, so a faithful translation of a
    dangling citation is in sync by construction; only the generated tree can say it dangles.
    """
    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        for name in sorted(set(AGENT_PATH.findall(text)) | set(AGENT_NAME.findall(text))):
            check((root / "agents" / f"{name}.md").is_file(),
                  f"{skill}: cites agent `{name}` but {root / 'agents' / (name + '.md')} does not exist")


def main(path: str = "plugins/quenching-codex") -> int:
    root = Path(path)
    manifest = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    check(manifest["name"] == "quenching-codex", "manifest name is not quenching-codex")
    check(manifest["version"] == (root / "VERSION").read_text(encoding="utf-8").strip(),
          "manifest version differs from VERSION")
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    # Derived from what the translator recorded, never a literal: a frozen count goes
    # stale the next time a command is minted, and nobody notices until this script dies.
    expected = json.loads((root / ".generated-from.json").read_text(encoding="utf-8"))["command_count"]
    check(len(skills) == expected, (len(skills), expected))
    for skill in skills:
        text = skill.read_text(encoding="utf-8")
        check(text.startswith("---\n") and "\n---\n" in text, skill)
        front = text[4:text.index("\n---\n", 4)]
        check(re.search(r"^name: [a-z0-9-]+$", front, re.MULTILINE), skill)
        check(re.search(r"^description: .+", front, re.MULTILINE), skill)
        check("[TODO:" not in text, skill)
    validate_cq_resolution(root)
    validate_agent_citations(root)
    print(f"validated {root} ({len(skills)} skills)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "plugins/quenching-codex"))
    except ValidationError as err:
        print(f"validate_codex_plugin: FAILED: {err}", file=sys.stderr)
        raise SystemExit(1)
