"""The leak gate's excerpt names where and what, never the matched text itself.

Samples are assembled at run time so this file does not trip the gate it tests."""
from __future__ import annotations

import pathlib
import re
import sys
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common import leak

CPF = "123.456" + ".789-09"
PAT = "dapi" + "0123456789abcdef" * 2


class ExcerptMasked(unittest.TestCase):
    def test_matched_text_is_masked_and_context_kept(self) -> None:
        text = f"first\nowner cpf {CPF} registered\n"
        found = leak.scan_text("a.md", text, dict(leak.GENERIC_PATTERNS))
        self.assertEqual(1, len(found))
        finding = found[0]
        self.assertNotIn(CPF, finding.excerpt)
        self.assertEqual("brazilian-cpf", finding.label)
        self.assertEqual(2, finding.line)
        self.assertIn("owner cpf", finding.excerpt)
        self.assertIn("registered", finding.excerpt)
        self.assertNotIn(CPF, finding.render())

    def test_second_secret_on_the_line_is_masked_too(self) -> None:
        text = f"cpf {CPF} token {PAT} end"
        found = leak.scan_text("a.md", text, dict(leak.GENERIC_PATTERNS))
        self.assertEqual({"brazilian-cpf", "databricks-pat"}, {f.label for f in found})
        for finding in found:
            self.assertNotIn(CPF, finding.excerpt)
            self.assertNotIn(PAT, finding.excerpt)
            self.assertIn("end", finding.excerpt)

    def test_zero_width_match_does_not_break_the_excerpt(self) -> None:
        text = "plain text 7"
        found = leak.scan_text("a.md", text, {"empty": re.compile(r"(?=7)"), "digit": re.compile("7")})
        self.assertEqual(2, len(found))
        self.assertTrue(all("plain text" in f.excerpt for f in found))


if __name__ == "__main__":
    unittest.main()
