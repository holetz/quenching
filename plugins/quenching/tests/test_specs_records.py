"""The specs pillar's frontmatter STATE fields and RECORDS: carry-forward on an ordinary
write, calendar-real date parsing, and a record's round trip through `set_frontmatter_record`.

Migrated from the pre-refactor specs script's `_failures()` suites — `carry_forward_failures`,
`field_date_failures`, `record_round_trip_failures`, `record_field_failures`. Parsing,
handoff and slug resolution live in `test_specs_parse.py`.
"""
import unittest
import argparse
import contextlib
import io
import json

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import task as task_module
from quenching.specs.commands.output import Emitter
from quenching.specs.commands.fields import parse_field_date, record_field_value_error
from quenching.specs.commands.validate import validate_spec
from quenching.specs.parse.fields import FIELD_KEYS, carry_forward_fields, set_frontmatter_record
from quenching.specs.schema import capture_form


class CarryForwardFields(unittest.TestCase):
    """THE BUG THIS FIXES: a key `strip_frontmatter_keys` removes is gone from the document
    once stored, so an ORDINARY write — editing a section, ticking a task — hands
    `write_spec` text that never mentions `tags` at all. Reading that absence as "clear the
    tags" would wipe every stored field on the next unrelated write. An ordinary write keeps
    every old value; an explicit write, even to an empty list, overrides just the key it
    named."""

    OLD = {"tags": ["a"], "assignee": "someone", "start": "2026-01-01", "target": None}

    CASES = (
        ({}, OLD, "an ordinary write (no keys in the new text) keeps everything"),
        ({"tags": []}, {**OLD, "tags": []}, "an explicit empty list overrides just `tags`"),
        ({"assignee": "other"}, {**OLD, "assignee": "other"},
         "an explicit new value overrides just `assignee`, `tags` untouched"),
    )

    def test_every_case_carries_forward_as_documented(self):
        for new, want, label in self.CASES:
            with self.subTest(label=label):
                self.assertEqual(carry_forward_fields(self.OLD, new, FIELD_KEYS), want, label)


class ParseFieldDate(unittest.TestCase):
    """REAL calendar validation, not a digit-shaped regex: `^\\d{4}-\\d{2}-\\d{2}$` accepts
    `2026-13-99`, which `date.fromisoformat` refuses."""

    CASES = (
        ("2026-08-05", "2026-08-05"),
        ("2026-13-99", None),
        ("not-a-date", None),
        ("2026-02-30", None),
    )

    def test_every_case_parses_or_refuses_as_documented(self):
        for value, want in self.CASES:
            with self.subTest(value=value):
                self.assertEqual(parse_field_date(value), want)


class SetFrontmatterRecordRoundTrip(unittest.TestCase):
    """Every record this tool writes must read back as what was written. A serialisation
    that round-trips for short values and silently truncates a long or comma-carrying one
    fails months later, on the spec that finally had a subject with a comma in it — and it
    fails as a record that reads *plausibly*, missing only its tail."""

    BASE = "---\nslug: alpha\ntitle: Alpha\nverification: per-task\n---\n\n## Problem\n\nx\n"
    CASES = {
        "short": {"level": "1", "criticality": "high"},
        "comma": {"strategy": "merge-commit", "subject": "plan/a: merge, then tidy"},
        "long": {"strategy": "merge-commit",
                 "subject": "plan/a-rather-long-slug-name-here: merge (merge-commit) "
                            "carrying every task"},
        "pr-open": {"number": "42", "url": "https://github.com/o/r/pull/42",
                    "date": "2026-08-12"},
    }

    def test_every_record_shape_round_trips_verbatim(self):
        for label, rec in self.CASES.items():
            with self.subTest(label=label):
                text = set_frontmatter_record(self.BASE, "priority", rec)
                self.assertEqual(parse_frontmatter(text).get("priority"), rec)
                for k, v in (("slug", "alpha"), ("title", "Alpha"),
                            ("verification", "per-task")):
                    self.assertEqual(parse_frontmatter(text).get(k), v,
                                     f"writing a record must not lose `{k}: {v}`")

    def test_reflowing_a_block_record_to_flow_drops_its_old_fields(self):
        # Block -> flow is the shape that orphans lines: the block form's fields sit on
        # their own lines, and replacing only the `key:` line would leave them below the
        # new value, where they parse as fields of whatever record comes next.
        blocked = set_frontmatter_record(self.BASE, "merge", self.CASES["comma"])
        reflowed = set_frontmatter_record(blocked, "merge", {"strategy": "rebase"})
        self.assertEqual(parse_frontmatter(reflowed).get("merge"), {"strategy": "rebase"})


class RecordFieldValueError(unittest.TestCase):
    """A field declaring `levels:` admits exactly those — and a field that declares none
    stays unrestricted. The refusal half is the point of the complexity scale: an hour
    count that sailed through the old record would silently break every gear derivation
    downstream, which is why the rule is proved here rather than eyeballed."""

    RSPEC = {"fields": ["level", "criticality", "complexity", "date"],
             "complexity": {"levels": ["low", "medium", "high", "xhigh"],
                            "writtenBy": ["triage", "create", "develop"]}}

    def test_every_declared_level_is_admitted(self):
        for good in ("low", "medium", "high", "xhigh"):
            with self.subTest(value=good):
                self.assertIsNone(record_field_value_error(self.RSPEC, "complexity", good))

    def test_an_undeclared_value_is_refused_because_the_scale_is_closed(self):
        for bad in ("8", "simple", ""):
            with self.subTest(value=bad):
                self.assertIsNotNone(record_field_value_error(self.RSPEC, "complexity", bad))

    def test_a_field_without_a_levels_block_stays_unrestricted(self):
        self.assertIsNone(record_field_value_error(self.RSPEC, "level", "1"))


def _spec_doc(complexity: str, slug: str = "alpha") -> str:
    """A minimal captured spec, its `priority.complexity` set directly in frontmatter — the
    write path `record_field_value_error` already guards, bypassed on purpose, the same way
    the invalid specs on disk today (`priority: {complexity: "4"}`) got there: written before
    the scale existed, never through `cq specs record`."""
    doc = (capture_form().replace("<SLUG>", slug).replace("<TITLE>", "Alpha")
           .replace("<DATE>", "2026-01-01").replace("<VERIFICATION>", "per-task"))
    return set_frontmatter_record(doc, "priority", {"complexity": complexity})


class SpBadComplexity(unittest.TestCase):
    """`validate_spec` flags a `priority.complexity` outside the four declared levels — the
    write-side guard above only ever sees a value passed through `cq specs record`, and the
    specs already on disk with a numeric complexity (written before the scale existed) predate
    it entirely. Warn, not error: the record is a hint for the orchestrator's gear derivation,
    and a bad one blocks nothing else."""

    def test_a_value_outside_the_four_levels_is_flagged(self):
        b = MemoryBackend()
        b.create_spec("plans", _spec_doc("3"))
        codes = [f["code"] for f in validate_spec(b, b.list_specs()[0])]
        self.assertIn("sp-bad-complexity", codes)

    def test_one_of_the_four_levels_is_not_flagged(self):
        b = MemoryBackend()
        b.create_spec("plans", _spec_doc("medium"))
        codes = [f["code"] for f in validate_spec(b, b.list_specs()[0])]
        self.assertNotIn("sp-bad-complexity", codes)


class DescopeTask(unittest.TestCase):
    """A descope closes the checkbox while carrying its reason into the close-out section.

    The state is intentionally represented by the existing checked marker: every downstream
    reader already knows that `[x]` is closed, while the explicit `descoped:` line and Outcome
    entry preserve why it is closed rather than pretending the work shipped."""

    DOC = ("---\ntitle: Descope fixture\nverification: per-task\n---\n\n"
           "## Tasks\n\n- [ ] 1.1 Remove the unused path\n")

    def test_descope_closes_the_task_and_appends_the_reason_to_outcome(self):
        backend = MemoryBackend()
        backend.create_spec("plans", self.DOC)
        spec_id = max(backend.docs)
        previous = task_module.open_backend
        self.addCleanup(setattr, task_module, "open_backend", previous)
        task_module.open_backend = lambda _root: (backend, {})

        args = argparse.Namespace(json=True, spec=spec_id, check=None, uncheck=None,
                                  block=None, descope="1.1", reason="não será construído",
                                  subject=None, commit=None)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = task_module.cmd_task(args, ".", Emitter())

        self.assertEqual(code, 0, buf.getvalue())
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["action"], "descoped")
        self.assertEqual(payload["text"], "1.1 Remove the unused path — descoped: não será construído")
        text = backend.docs[spec_id][1]
        self.assertIn("- [x] 1.1 Remove the unused path — descoped: não será construído", text)
        self.assertIn("## Outcome\n\n- task 1.1 descoped: não será construído", text)


class UncheckTask(unittest.TestCase):
    """Reopening a reverted task drops its stale implementation anchors and leaves a discovery.

    The single write matters for provider-backed specs: a revert must not leave `[x]` pointing at
    a commit that has just been compensated, and its reason must survive as durable spec text."""

    DOC = ("---\ntitle: Revert fixture\nverification: per-task\n---\n\n"
           "## Tasks\n\n- [x] 1.1 Remove the unused path\n"
           "      subject: plan/revert-fixture: remove the unused path\n"
           "      commit: 1234567\n\n"
           "## Discoveries\n\n- prior discovery\n")

    def test_uncheck_requires_reason_and_records_discovery(self):
        backend = MemoryBackend()
        backend.create_spec("plans", self.DOC)
        spec_id = max(backend.docs)
        previous = task_module.open_backend
        self.addCleanup(setattr, task_module, "open_backend", previous)
        task_module.open_backend = lambda _root: (backend, {})

        args = argparse.Namespace(json=True, spec=spec_id, check=None, uncheck="1.1",
                                  block=None, descope=None, reason="revert commit 7654321",
                                  subject=None, commit=None)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = task_module.cmd_task(args, ".", Emitter())

        self.assertEqual(code, 0, buf.getvalue())
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["action"], "unchecked")
        self.assertEqual(payload["reason"], "revert commit 7654321")
        text = backend.docs[spec_id][1]
        self.assertIn("- [ ] 1.1 Remove the unused path", text)
        self.assertNotIn("subject: plan/revert-fixture", text)
        self.assertNotIn("commit: 1234567", text)
        self.assertIn("- prior discovery", text)
        self.assertIn("- task 1.1 unchecked: revert commit 7654321", text)


if __name__ == "__main__":
    unittest.main()
