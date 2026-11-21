"""`validate_spec` names a stored spec whose text ends inside an open fence (`sp-unclosed-fence`).

`section --write` refuses such a body since 2244, but a spec written before it, or by another
path, still parses every `## ` after the opener as code: the later sections vanish from every
read and the next write of the holding section deletes them. The finding names the opener's
line, the section that holds it, and a remedy the write path accepts."""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands.validate import validate_spec
from quenching.specs.parse.edit import unclosed_fence, unclosed_fence_at

CODE = "sp-unclosed-fence"

DOC = """---
title: Alpha
date: 2026-08-15
---

# Alpha

## Problem

O problema.

{fence}bash
echo hi
{close}
## Proposal

A proposta.
"""


def _spec(close: str, fence: str = "```") -> tuple[MemoryBackend, dict]:
    b = MemoryBackend()
    b.create_spec("plans", DOC.format(fence=fence, close=close))
    return b, b.list_specs()[0]


def _findings(b: MemoryBackend, s: dict) -> list[dict]:
    return [f for f in validate_spec(b, s) if f["code"] == CODE]


class UnclosedFenceAt(unittest.TestCase):
    def test_names_the_opener_line_and_text(self):
        self.assertEqual(unclosed_fence_at("a\n\n```bash\nx\n"), (3, "```bash"))

    def test_a_closed_fence_is_none(self):
        self.assertIsNone(unclosed_fence_at("```\nx\n```\n"))

    def test_a_shorter_mark_does_not_close_a_longer_fence(self):
        self.assertEqual(unclosed_fence_at("````md\n```\n"), (1, "````md"))

    def test_unclosed_fence_keeps_returning_the_opener(self):
        self.assertEqual(unclosed_fence("```bash\nx\n"), "```bash")


class ValidateNamesTheOpenFence(unittest.TestCase):
    def test_an_open_fence_is_an_error_naming_line_and_section(self):
        found = _findings(*_spec(close=""))
        self.assertEqual(len(found), 1)
        f = found[0]
        self.assertEqual(f["severity"], "error")
        self.assertEqual((f["line"], f["opener"], f["heading"]), (12, "```bash", "Problem"))
        self.assertIn("line 12", f["message"])
        self.assertIn('"Problem,<each swallowed heading>" --write', f["remedy"])

    def test_a_closed_fence_is_not_flagged(self):
        self.assertEqual(_findings(*_spec(close="```\n")), [])

    def test_a_tilde_fence_follows_the_same_rule(self):
        self.assertEqual(len(_findings(*_spec(close="", fence="~~~"))), 1)
        self.assertEqual(_findings(*_spec(close="~~~\n", fence="~~~")), [])


if __name__ == "__main__":
    unittest.main()
