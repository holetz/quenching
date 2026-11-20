"""2158 — the `end` date a spec declares, beside `start`/`target`, through `cmd_field`."""
import unittest
from types import SimpleNamespace

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from test_specs_duplicate_heading import _Base
from quenching.specs.commands.fields import cmd_field
from quenching.specs.schema import load_schema


class TheEndField(_Base):
    def _end(self, value):
        return self.call(cmd_field, SimpleNamespace(json=True, spec=1, field="end", value=value))

    def test_sets_and_reads_a_real_date(self):
        code, obj = self._end("2026-12-01")
        self.assertEqual((code, obj["end"]), (0, "2026-12-01"))
        self.assertIn("end: 2026-12-01", self.text())
        code, obj = self._end(None)
        self.assertEqual((code, obj["end"]), (0, "2026-12-01"))

    def test_refuses_an_impossible_date_and_writes_nothing(self):
        before = self.text()
        code, obj = self._end("2026-02-30")
        self.assertEqual((code, obj["code"]), (2, "sp-bad-end"))
        self.assertEqual(self.text(), before)

    def test_end_is_a_declared_optional_key(self):
        self.assertIn("end", load_schema()["frontmatter"]["optional"])


if __name__ == "__main__":
    unittest.main()
