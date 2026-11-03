"""1343 — a canonical heading written twice, and every write vector that could write one.

The 1315 reached `archive/` with `## Handoff` twice. `parse_sections` keeps the FIRST copy, so the
empty first one read as the section, while the real text sat under the second. Two halves here:
what is ALREADY on disk (`validate`, `promote`, and the rewrite that repairs it) and, one test per
vector, that no write path can put it there."""
import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from test_specs_create_collapse import _Workspace as CreateWorkspace
from test_specs_section_write import HANDOFF_SPEC, _Workspace
from quenching.specs.commands import fields as fields_module
from quenching.specs.commands import promote as promote_module
from quenching.specs.commands import task as task_module
from quenching.specs.commands.fields import cmd_field, cmd_record, cmd_title
from quenching.specs.commands.output import Emitter
from quenching.specs.commands.task import cmd_discover, cmd_task
from quenching.specs.commands.validate import cmd_validate
from quenching.specs.parse.sections import duplicate_headings

# The 1315 shape: an empty first `## Handoff`, the text under a second one.
DOUBLED = HANDOFF_SPEC.replace(
    "## Handoff\n\nO bloco evergreen.\n",
    "## Handoff\n\n## Handoff\n\nO bloco evergreen.\n", 1)


def _count(text, heading="Handoff"):
    return text.count(f"\n## {heading}\n")


class _Base(_Workspace):
    spec_text = HANDOFF_SPEC

    def setUp(self):
        super().setUp()
        for module in (task_module, promote_module, fields_module):
            p = mock.patch.object(module, "open_backend", lambda _r: (self.backend, {}))
            p.start()
            self.addCleanup(p.stop)

    def text(self):
        return self.backend.read_spec(1)[0]["text"]

    def call(self, fn, args, stdin=None):
        buf, stream = io.StringIO(), io.StringIO(stdin or "")
        stream.isatty = lambda: stdin is None
        with mock.patch("sys.stdin", stream), redirect_stdout(buf):
            code = fn(args, self.root, Emitter())
        out = buf.getvalue()
        return code, (json.loads(out) if out.strip().startswith("{") else {})


class TheDuplicateOnDisk(_Base):
    spec_text = DOUBLED

    def test_the_parser_helper_names_it(self):
        self.assertEqual(duplicate_headings(DOUBLED), ["Handoff"])
        self.assertEqual(duplicate_headings(HANDOFF_SPEC), [])

    def test_validate_reports_it_as_an_error(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cmd_validate(SimpleNamespace(json=True, spec="1", phase=None, strict=False,
                                                fix=False), self.root, Emitter())
        found = json.loads(buf.getvalue())
        codes = [f["code"] for f in found.get("findings", [])]
        self.assertIn("sp-duplicate-heading", codes, found)
        self.assertNotEqual(code, 0)

    def test_promote_refuses_it_and_force_does_not_waive_it(self):
        for force in (False, True):
            with self.subTest(force=force):
                code, obj = self.call(promote_module.cmd_promote, SimpleNamespace(
                    json=True, spec=1, to="archive", outcome="abandoned", force=force,
                    dry_run=False, complexity=None))
                self.assertEqual((code, obj["code"]), (2, "sp-duplicate-heading"))
                self.assertEqual(_count(self.text()), 2)

    def test_promote_dry_run_refuses_it_too(self):
        code, obj = self.call(promote_module.cmd_promote, SimpleNamespace(
            json=True, spec=1, to="archive", outcome="abandoned", force=True,
            dry_run=True, complexity=None))
        self.assertEqual((code, obj["code"]), (2, "sp-duplicate-heading"))

    def test_rewriting_the_section_repairs_it(self):
        code, obj = self.run_section(heading="Handoff", write=True, scope="global",
                                     stdin="Texto refeito.\n")
        self.assertEqual(code, 0, obj)
        self.assertEqual(_count(self.text()), 1)
        self.assertEqual(duplicate_headings(self.text()), [])
        self.assertIn("Tasks", self.text())


class EveryWriteVectorRefusesAHeading(_Base):
    """One test per remaining writer that splices caller text into the body."""

    EVIL = "achado\n\n## Handoff\n\nfalso"

    def assert_untouched(self, code, obj, expected=("sp-write-nested-heading",)):
        self.assertIn(code, (1, 2), obj)
        self.assertIn(obj.get("code"), expected, obj)
        self.assertEqual(_count(self.text()), 1)

    def test_discover(self):
        code, obj = self.call(cmd_discover, SimpleNamespace(json=True, spec=1, text=self.EVIL))
        self.assert_untouched(code, obj)

    def _task(self, **kw):
        base = dict(json=True, spec="1", check=None, uncheck=None, block=None, descope=None,
                    reason=None, subject=None, commit=None)
        base.update(kw)
        return self.call(cmd_task, SimpleNamespace(**base))

    def test_task_descope_reason(self):
        code, obj = self._task(descope="2.1", reason=self.EVIL)
        self.assert_untouched(code, obj)

    def test_task_uncheck_reason(self):
        code, obj = self._task(uncheck="1.1", reason=self.EVIL)
        self.assert_untouched(code, obj)

    def test_task_block_reason(self):
        code, obj = self._task(block="2.1", reason=self.EVIL)
        self.assert_untouched(code, obj)

    def test_task_subject_and_commit(self):
        code, obj = self._task(check="2.1", subject="a\n## Handoff\nb")
        self.assert_untouched(code, obj, ("sp-bad-subject",))
        code, obj = self._task(check="2.1", commit="abc1234\n## Handoff")
        self.assert_untouched(code, obj, ("sp-bad-commit-sha",))

    def test_fields_title(self):
        code, obj = self.call(cmd_title, SimpleNamespace(json=True, spec=1,
                                                         title="x\n## Handoff\ny"))
        self.assert_untouched(code, obj, ("sp-bad-title",))

    def test_fields_scalars(self):
        for key in ("assignee", "tags", "start", "target"):
            with self.subTest(key=key):
                code, obj = self.call(cmd_field, SimpleNamespace(
                    json=True, spec=1, field=key, value="x\n## Handoff\ny"))
                self.assertEqual(code, 2, obj)
                self.assertEqual(_count(self.text()), 1)

    def test_fields_record(self):
        code, obj = self.call(cmd_record, SimpleNamespace(
            json=True, spec=1, name="merge", set=["subject=x\n## Handoff\ny"]))
        self.assertEqual(code, 2, obj)
        self.assertEqual(_count(self.text()), 1)

    def test_conclude_outcome_via_descope_and_promote(self):
        # `conclude` writes `## Outcome` only through `task --descope` and `section`; both refuse.
        code, obj = self.run_section(heading="Outcome", write=True,
                                     stdin="resumo\n\n## Handoff\n\nfalso\n")
        self.assertEqual((code, obj["code"]), (2, "sp-write-nested-heading"))
        self.assertEqual(_count(self.text()), 1)


class CreateVectors(CreateWorkspace):
    """`cq specs new`: the stream and the title are the two caller texts that reach the body."""

    def test_a_stream_naming_a_heading_twice_writes_nothing(self):
        code, obj = self.run_new(stdin="## Handoff\n\n## Handoff\n\ntexto\n")
        self.assertEqual((code, obj["code"]), (2, "sp-write-duplicate-heading"))
        self.assertEqual(self.list_ids(), [])

    def test_a_title_with_a_heading_line_writes_nothing_or_one_heading(self):
        code, obj = self.run_new(title="x\n## Handoff\n\nfalso",
                                    stdin="## Problem\n\nO problema.\n")
        ids = self.list_ids()
        if ids:
            self.assertEqual(code, 0, obj)
            self.assertEqual(duplicate_headings(self.read_back()["text"]), [])
            self.assertNotIn("\n## Handoff\n", self.read_back()["text"])
        else:
            self.assertEqual(code, 2, obj)


if __name__ == "__main__":
    unittest.main()
