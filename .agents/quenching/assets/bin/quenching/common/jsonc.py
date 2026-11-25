"""JSON with comments and trailing commas, as VS Code and OpenCode read their settings files.

The reader is shared by the deploy (`opencode.json`, and the `.vscode/settings.json` report) and by
the workspace report, so it lives in `common` rather than in either caller.
"""
from __future__ import annotations

import json
import re


def jsonc_loads(text: str):
    """JSON with `//` and `/* */` comments and trailing commas, as both clients write it."""
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
