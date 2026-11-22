"""A task `after:` naming no label, or closing a cycle, is named instead of waiting forever.

`next` opens a task only when every `after:` label is done, so a typo or a loop between tasks
left the spec `blocked` with nothing pointing at the bad line, and `validate` never read the
field."""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import next as next_cmd
from quenching.specs.commands.validate import validate_spec
from quenching.specs.parse.epics import task_after_problems
from quenching.specs.schema import capture_form
from test_specs_composition import doc, run


def _doc(tasks_body: str) -> str:
    doc = (capture_form().replace("<SLUG>", "alpha").replace("<TITLE>", "Alpha")
           .replace("<DATE>", "2026-01-01").replace("<VERIFICATION>", "per-task"))
    return doc + "\n## Tasks\n\n### 1. Build\n\n" + tasks_body + "\n"


def _problems(tasks_body: str) -> dict:
    b = MemoryBackend()
    b.create_spec("plans", _doc(tasks_body))
    info, _ = b.read_spec(b.list_specs()[0]["id"])
    return task_after_problems(info)


class TaskAfterProblems(unittest.TestCase):
    def test_an_unknown_label_is_named_with_its_task(self):
        got = _problems("- [ ] 1.1 Alpha — after: 9.9\n")
        self.assertEqual([("1.1", "9.9")], [(u["task"], u["label"]) for u in got["unknown"]])
        self.assertIsNone(got["cycle"])

    def test_two_tasks_waiting_on_each_other_are_a_cycle(self):
        got = _problems("- [ ] 1.1 Alpha — after: 1.2\n- [ ] 1.2 Beta — after: 1.1\n")
        self.assertEqual(["1.1", "1.2", "1.1"], got["cycle"])
        self.assertEqual([], got["unknown"])

    def test_a_task_waiting_on_itself_is_a_cycle(self):
        self.assertEqual(["1.1", "1.1"], _problems("- [ ] 1.1 Alpha — after: 1.1\n")["cycle"])

    def test_a_task_waiting_on_a_spec_item_of_the_document_is_fine(self):
        got = _problems("- [ ] S2 Migration — spec: #3\n- [ ] 2.1 Wire — after: S2\n")
        self.assertEqual({"unknown": [], "cycle": None}, got)

    def test_a_valid_chain_raises_nothing(self):
        got = _problems("- [ ] 1.1 Alpha\n- [ ] 1.2 Beta — after: 1.1\n")
        self.assertEqual({"unknown": [], "cycle": None}, got)


def _findings(tasks_body: str) -> list[dict]:
    b = MemoryBackend()
    b.create_spec("plans", _doc(tasks_body))
    return [f for f in validate_spec(b, b.list_specs()[0])
            if f["code"] in ("sp-after-unknown", "sp-after-cycle")]


class ValidateNamesTheBadAfter(unittest.TestCase):
    def test_an_unknown_label_is_an_error_naming_task_label_and_line(self):
        (f,) = _findings("- [ ] 1.1 Alpha — after: 9.9\n")
        self.assertEqual(("sp-after-unknown", "error", "1.1", "9.9"),
                         (f["code"], f["severity"], f["task"], f["dependency"]))
        self.assertIsInstance(f["line"], int)

    def test_a_cycle_is_one_error_carrying_the_path(self):
        (f,) = _findings("- [ ] 1.1 Alpha — after: 1.2\n- [ ] 1.2 Beta — after: 1.1\n")
        self.assertEqual(("sp-after-cycle", "error", ["1.1", "1.2", "1.1"]),
                         (f["code"], f["severity"], f["cycle"]))

    def test_a_spec_item_label_and_a_valid_chain_raise_nothing(self):
        self.assertEqual([], _findings("- [ ] S2 Migration — spec: #3\n"
                                       "- [ ] 2.1 Wire — after: S2\n- [ ] 2.2 Ship — after: 2.1\n"))


class NextPointsAtTheBadAfter(unittest.TestCase):
    def _next(self, tasks_body: str) -> tuple[int, dict]:
        b = MemoryBackend()
        b.create_spec("plans", doc("Alpha", tasks="## Tasks\n\n" + tasks_body))
        return run(next_cmd.cmd_next, b, spec=1, epic=None, front=False, limit=None)

    def test_an_unknown_label_marks_the_waiting_row_and_names_validate(self):
        code, got = self._next("- [ ] 1.1 Alpha — after: 9.9\n")
        self.assertEqual((0, "blocked"), (code, got["action"]))
        self.assertEqual((["9.9"], False), (got["waiting"][0]["unknown"],
                                            got["waiting"][0]["cycle"]))
        self.assertIn("cq specs validate", got["message"])

    def test_a_cycle_marks_both_rows(self):
        code, got = self._next("- [ ] 1.1 Alpha — after: 1.2\n- [ ] 1.2 Beta — after: 1.1\n")
        self.assertEqual("blocked", got["action"])
        self.assertEqual([True, True], [r["cycle"] for r in got["waiting"]])

    def test_a_plain_block_carries_no_hint(self):
        b = MemoryBackend()
        b.create_spec("plans", doc("Alpha", tasks="## Tasks\n\n- [!] 1.1 Alpha — blocked: x\n"
                                                  "- [ ] 1.2 Beta — after: 1.1\n"))
        code, got = run(next_cmd.cmd_next, b, spec=1, epic=None, front=False, limit=None)
        self.assertEqual("blocked", got["action"])
        self.assertEqual(([], False), (got["waiting"][0]["unknown"], got["waiting"][0]["cycle"]))
        self.assertNotIn("cq specs validate", got["message"])


if __name__ == "__main__":
    unittest.main()
