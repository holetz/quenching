"""JSON with comments, as the clients that read a `.jsonc`/JSONC settings file do.

`.vscode/settings.json` and `opencode.jsonc` are JSONC in the world: the first one carries
comments and a trailing comma in most workspaces, so a `json.load` would refuse the very file the
deploy and the doctor must read. This reader keeps strings intact, drops `//` and `/* */`
comments and the trailing commas, and hands the result to `json.loads`.
"""
from __future__ import annotations

import json
import re


def jsonc_loads(text: str):
    """JSON with `//` and `/* */` comments and trailing commas, as the clients read it."""
    out, index, size = [], 0, len(text)
    while index < size:
        char = text[index]
        if char == '"':
            end = index + 1
            while end < size and text[end] != '"':
                end += 2 if text[end] == "\\" else 1
            out.append(text[index:end + 1])
            index = end + 1
        elif text.startswith("//", index):
            newline = text.find("\n", index)
            index = size if newline < 0 else newline
        elif text.startswith("/*", index):
            close = text.find("*/", index + 2)
            index = size if close < 0 else close + 2
        else:
            out.append(char)
            index += 1
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", "".join(out)))
