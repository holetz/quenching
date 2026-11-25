"""`cq specs record <id> approved` never writes an `approved` without `date`, whatever the route.

The MCP tool always injects the date; the CLI fallback must reach the same record."""
import datetime
import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring

from test_specs_create_collapse import _Workspace
from quenching.specs.commands import fields as fields_module
from quenching.specs.commands.fields import cmd_record
from quenching.specs.commands.output import Emitter


class TheApprovedRecordDate(_Workspace):
    def setUp(self):
        super().setUp()
        patch = mock.patch.object(fields_module, "open_backend",
                                  lambda _root: (self.backend, {}))
        patch.start()
        self.addCleanup(patch.stop)
        code, obj = self.run_new(title="plain", stdin="## Problem\n\nP.\n")
        self.assertEqual(code, 0, obj)
        self.spec = max(self.backend.docs)

    def stamp(self, *pairs):
        buf = io.StringIO()
        args = SimpleNamespace(json=True, spec=str(self.spec), name="approved", set=list(pairs))
        with redirect_stdout(buf):
            code = cmd_record(args, self.root, Emitter())
        self.assertEqual(code, 0, buf.getvalue())
        return self.read_back(self.spec)["frontmatter"]["approved"]

    def test_without_a_date_it_stamps_today(self):
        record = self.stamp("by=orchestrator-forced")
        self.assertEqual(record, {"date": datetime.date.today().isoformat(),
                                  "by": "orchestrator-forced"})

    def test_a_given_date_is_kept(self):
        record = self.stamp("by=human", "date=2026-01-02")
        self.assertEqual(record, {"date": "2026-01-02", "by": "human"})


if __name__ == "__main__":
    unittest.main()
