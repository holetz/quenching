"""Dependency commands use the backend, refuse atomically, and derive without writing."""
import contextlib
import copy
import io
import json
import unittest
from unittest.mock import patch

import _paths  # noqa: F401
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import deps, validate
from quenching.specs.commands.cli import main


class DependencyCommands(unittest.TestCase):
    def setUp(self):
        self.backend = MemoryBackend()
        for title in ("First", "Second", "Third", "Isolated"):
            self.backend.create_spec("plans", f"---\ntitle: {title}\ndate: 2026-10-24\n"
                                     "---\n\n## Problem\nKeep this body.\n")
        self.writer = self.enterContext(patch.object(self.backend, "write_spec",
                                                    wraps=self.backend.write_spec))
        self.enterContext(patch.object(deps, "open_backend", return_value=(self.backend, {})))
        self.enterContext(patch.object(validate, "open_backend", return_value=(self.backend, {})))
        self.enterContext(patch.object(validate, "origin_url", return_value=None))

    def call(self, *argv, as_json=True):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = main([*argv, *(["--json"] if as_json else [])])
        return code, json.loads(stream.getvalue()) if as_json else stream.getvalue()

    def text(self, spec=1):
        return self.backend.read_spec(spec)[0]["text"]

    def test_add_remove_and_read_flow_list_preserves_other_content(self):
        before = self.text()
        code, payload = self.call("depends", "1", "--add", "2,3")
        self.assertEqual((0, ["2", "3"]), (code, payload["dependsOn"]))
        self.assertIn("dependsOn: [2, 3]\n", self.text())
        self.assertEqual(before, self.text().replace("dependsOn: [2, 3]\n", ""))
        code, payload = self.call("depends", "--spec", "1", "--remove", "2")
        self.assertEqual((0, ["3"]), (code, payload["dependsOn"]))
        self.assertIn("dependsOn: [3]\n", self.text())
        self.writer.reset_mock()
        self.assertEqual(["3"], self.call("depends", "1")[1]["dependsOn"])
        self.assertIn("dependsOn: [3]", self.call("depends", "1", as_json=False)[1])
        self.writer.assert_not_called()
        self.assertEqual([], self.call("depends", "1", "--remove", "3")[1]["dependsOn"])
        self.assertIn("dependsOn: []\n", self.text())

    def test_idempotence_deduplicates_and_does_not_write_again(self):
        self.call("depends", "1", "--add", " #2, 2,3, #3")
        before = copy.deepcopy(self.backend.docs)
        self.writer.reset_mock()
        for flags in (("--add", "3,2"), ("--remove", "4"),
                      ("--add", "4", "--remove", "4")):
            self.assertEqual(0, self.call("depends", "1", *flags)[0])
        self.assertEqual(before, self.backend.docs)
        self.writer.assert_not_called()

    def test_unknown_and_self_references_refuse_without_writes(self):
        for flag, value, expected in (("--add", "2,99", "sp-dep-missing"),
                                      ("--remove", "99", "sp-dep-missing"),
                                      ("--add", "2,1", "sp-dep-self"),
                                      ("--remove", "1", "sp-dep-self")):
            with self.subTest(flag=flag, value=value):
                before = copy.deepcopy(self.backend.docs)
                code, payload = self.call("depends", "1", flag, value)
                self.assertEqual((2, False, expected), (code, payload["ok"], payload["code"]))
                self.assertEqual(before, self.backend.docs)
                self.writer.assert_not_called()
        code, payload = self.call("depends", "99", "--add", "2")
        self.assertNotEqual(0, code)
        self.assertEqual("sp-unknown-id", payload["code"])
        self.writer.assert_not_called()

    def test_transitive_cycle_refuses_entire_edit(self):
        self.call("depends", "1", "--add", "2")
        self.call("depends", "2", "--add", "3")
        before = copy.deepcopy(self.backend.docs)
        self.writer.reset_mock()
        code, payload = self.call("depends", "3", "--add", "4,1")
        self.assertEqual((2, "sp-dep-cycle", ["1", "2", "3", "1"]),
                         (code, payload["code"], payload["cycle"]))
        self.assertEqual(before, self.backend.docs)
        self.writer.assert_not_called()

    def seed_schedule(self, cycle=False):
        for spec, fm in ((1, "start: 2026-01-01\ntarget: 2026-01-10\n"),
                         (2, "start: 2026-01-05\ntarget: 2026-01-08\ndependsOn: [1]\n"),
                         (3, "start: 2026-01-12\ntarget: 2026-01-15\ndependsOn: [2]\n")):
            phase, text = self.backend.docs[spec]
            if cycle and spec == 1:
                fm += "dependsOn: [3]\n"
            self.backend.docs[spec] = (phase, text.replace("date: 2026-10-24\n",
                                                         "date: 2026-10-24\n" + fm))

    def seed_dependency(self, spec, dependencies, phase="plans", outcome=None):
        text = self.text(spec)
        fm = f"dependsOn: [{', '.join(map(str, dependencies))}]\n"
        if outcome is not None:
            fm += f"outcome: {outcome}\n"
        self.backend.docs[spec] = (phase, text.replace("date: 2026-10-24\n",
                                                     "date: 2026-10-24\n" + fm))

    def dependency_findings(self, *flags):
        _, payload = self.call("validate", *flags)
        self.writer.assert_not_called()
        return [f for f in payload["findings"] if f["code"].startswith("sp-dep-")]

    def test_validate_missing_and_self_dependencies_have_remedies(self):
        self.seed_dependency(1, [99, 1])
        findings = self.dependency_findings()
        self.assertEqual([("sp-dep-missing", "error", "1"),
                          ("sp-dep-self", "error", "1")],
                         [(f["code"], f["severity"], f["spec"]) for f in findings])
        self.assertIn("99", findings[0]["message"])
        self.assertTrue(all(f["remedy"] for f in findings))

    def test_validate_cycle_names_full_path(self):
        self.seed_dependency(1, [2])
        self.seed_dependency(2, [3])
        self.seed_dependency(3, [1])
        for flags in ((), ("--spec", "1")):
            with self.subTest(flags=flags):
                findings = self.dependency_findings(*flags)
                self.assertEqual(1, len(findings))
                finding = findings[0]
                self.assertEqual(("sp-dep-cycle", "error", ["1", "2", "3", "1"]),
                                 (finding["code"], finding["severity"], finding["cycle"]))
                self.assertIn("1 -> 2 -> 3 -> 1", finding["message"])
                self.assertTrue(finding["remedy"])

    def test_validate_warns_for_archived_dependencies_unless_done(self):
        self.seed_dependency(1, [2])
        for outcome in ("abandoned", "superseded", "", "done"):
            with self.subTest(outcome=outcome):
                # Replace the target body so each outcome is an independent fixture.
                self.backend.docs[2] = ("archive", "---\ntitle: Second\n"
                                       f"outcome: {outcome}\n---\n")
                findings = self.dependency_findings("--spec", "1")
                if outcome == "done":
                    self.assertEqual([], findings)
                else:
                    self.assertEqual(1, len(findings))
                    self.assertEqual(("sp-dep-dropped", "warn", "1", outcome),
                                     tuple(findings[0][k] for k in
                                           ("code", "severity", "spec", "outcome")))
                    self.assertTrue(findings[0]["remedy"])

    def test_validate_clean_graph_reuses_sweep_and_bulk_reads_extra_ids_once(self):
        self.seed_dependency(1, [2, 3])
        self.seed_dependency(2, [3])
        self.seed_dependency(3, [], phase="archive", outcome="done")
        before = copy.deepcopy(self.backend.docs)
        with patch.object(self.backend, "read_specs", wraps=self.backend.read_specs) as reader:
            self.assertEqual([], self.dependency_findings())
            reader.assert_not_called()
            self.assertEqual([], self.dependency_findings("--spec", "1"))
            reader.assert_called_once_with(["2", "3"])
            reader.reset_mock()
            self.assertEqual([], self.dependency_findings("--phase", "plans"))
            reader.assert_called_once_with(["3"])
        self.assertEqual(before, self.backend.docs)

    def test_validate_narrowed_scope_reads_transitive_ids_and_missing_ids_once(self):
        self.seed_dependency(1, [2, 99])
        self.seed_dependency(2, [3, 99])
        self.seed_dependency(3, [99])
        with patch.object(self.backend, "read_specs", wraps=self.backend.read_specs) as reader:
            findings = self.dependency_findings("--spec", "1")
        self.assertEqual([["2", "99"], ["3"]],
                         [call.args[0] for call in reader.call_args_list])
        self.assertEqual([("sp-dep-missing", "1")],
                         [(f["code"], f["spec"]) for f in findings])

    def test_schedule_payload_bulk_reads_and_never_writes(self):
        self.seed_schedule()
        before = copy.deepcopy(self.backend.docs)
        events = []
        original_list = self.backend.list_specs
        original_read = self.backend.read_specs

        def listing(*args, **kwargs):
            events.append("list")
            return original_list(*args, **kwargs)

        def reading(ids):
            events.append(("read", ids))
            return original_read(ids)

        with patch.object(self.backend, "list_specs", side_effect=listing), \
                patch.object(self.backend, "read_specs", side_effect=reading):
            code, payload = self.call("schedule")
        self.assertEqual(["list", ("read", [1, 2, 3, 4])], events[:2])
        self.assertEqual((0, True, None, ["1", "2", "3"]),
                         (code, payload["ok"], payload["cycle"], payload["criticalPath"]))
        node = payload["nodes"][1]
        self.assertEqual(("2", "2026-01-05", "2026-01-08", "2026-01-10", "2026-01-13", 5, True),
                         tuple(node[key] for key in ("id", "start", "target", "earliestStart",
                                                    "earliestFinish", "slipDays", "critical")))
        self.assertEqual(["1", "2"], [node["id"] for node in
                         self.call("schedule", "--spec", "2")[1]["nodes"]])
        self.assertEqual(["4"], [node["id"] for node in
                         self.call("schedule", "4")[1]["nodes"]])
        self.assertIn("criticalPath: 1 -> 2 -> 3", self.call("schedule", as_json=False)[1])
        self.assertEqual(before, self.backend.docs)
        self.writer.assert_not_called()

    def test_schedule_cycle_exit_one_and_empty_schedule(self):
        self.assertEqual([], self.call("schedule")[1]["nodes"])
        self.seed_schedule(cycle=True)
        before = copy.deepcopy(self.backend.docs)
        code, payload = self.call("schedule")
        self.assertEqual((1, False, ["1", "3", "2", "1"], [], []),
                         (code, payload["ok"], payload["cycle"], payload["nodes"],
                          payload["criticalPath"]))
        self.assertIn("dependency cycle:", self.call("schedule", as_json=False)[1])
        self.assertEqual(before, self.backend.docs)
        self.writer.assert_not_called()

    def test_backend_refusal_and_unknown_schedule_selection(self):
        with patch.object(deps, "open_backend", return_value=(None, {
                "code": "sp-config", "message": "missing config", "exit": 2})):
            for argv in (("depends", "1"), ("schedule",)):
                code, payload = self.call(*argv)
                self.assertEqual((2, "sp-config"), (code, payload["code"]))
        self.assertEqual("sp-unknown-id", self.call("schedule", "--spec", "99")[1]["code"])
        self.writer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
