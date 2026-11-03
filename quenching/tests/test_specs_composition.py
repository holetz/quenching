"""The composition model, offline: one `## Tasks` grammar, the derived levels and the
composite's progress. Pure derivation wherever possible, the memory fake where a document
has to be written."""
import argparse
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import epic as epic_cmd
from quenching.specs.commands import next as next_cmd
from quenching.specs.commands import read as read_cmd
from quenching.specs.commands import task as task_cmd
from quenching.specs.commands import validate as validate_cmd
from quenching.specs.commands.output import Emitter
from quenching.specs.parse import derive_info
from quenching.specs.parse.derive import board_state_of
from quenching.specs.parse.epics import (composition_cycle, derive_composition,
                                         parse_items, presentation_level)
from quenching.specs.parse.records import derive_labels
from quenching.specs.parse.tasks import task_progress

TASKS = """## Tasks

### 1. Foundations

- [ ] 1.1 Build the schema
- [ ] S1 Foundation — spec: #2

### 2. Delivery

- [ ] S2 Migration — spec: #3 — after: S1
- [ ] 2.1 Wire the job — after: S2
"""

READY = """## Problem

Why it exists.

## Proposal

What it does.

## Out of Scope

- none — the rest.

## Impact

- the surface.

## Validation

- `true`.

## Design

- the shape.

## Alternatives Considered

- none — no other.

## Open Decisions

- none — settled.

## Risks

- none — contained.

## Handoff

Start here.

## Outcome

Delivered.

"""


def doc(title="Spec", fm="", tasks=TASKS):
    return (f"---\ntitle: {title}\ndate: 2026-01-01\n{fm}---\n\n" + READY + tasks)


def run(fn, backend, **kw):
    args = argparse.Namespace(json=True, **kw)
    buf = io.StringIO()
    with contextlib.ExitStack() as stack:
        for mod in (epic_cmd, next_cmd, read_cmd, task_cmd, validate_cmd):
            stack.enter_context(mock.patch.object(mod, "open_backend",
                                                  return_value=(backend, {})))
        stack.enter_context(contextlib.redirect_stdout(buf))
        code = fn(args, tempfile.gettempdir(), Emitter())
    text = buf.getvalue().strip()
    return code, (json.loads(text) if text else {})


class TheOneGrammar(unittest.TestCase):
    def test_a_task_and_a_spec_item_are_one_checkbox_with_two_readings(self):
        info = derive_info({"id": 1, "phase": "plans"}, doc())
        self.assertEqual(["1.1", "2.1"], [t["id"] for t in info["tasks"]])
        self.assertEqual(["S1", "S2"], [t["label"] for t in info["links"]])
        self.assertEqual([None, None], [t["id"] for t in info["links"]])
        self.assertEqual(["#2", "#3"], [f"#{t['spec']}" for t in info["links"]])
        self.assertEqual(["S1"], info["links"][1]["after"])
        self.assertEqual(["S2"], info["tasks"][1]["after"])
        self.assertEqual("Migration", info["links"][1]["title"])
        self.assertEqual((0, 0, 2), task_progress(info["tasks"]))

    def test_parse_items_reads_a_hand_built_info_without_the_split(self):
        info = derive_info({"id": 1, "phase": "plans"}, doc())
        bare = {"tasks": info["tasks"] + info["links"], "sections": info["sections"]}
        self.assertEqual(["S1", "S2"], [i["label"] for i in parse_items(bare)])


class PresentationLevel(unittest.TestCase):
    def _level(self, tasks, fm=""):
        return presentation_level(derive_info({"id": 1, "phase": "plans"},
                                              doc(fm=fm, tasks=tasks)))

    def test_no_member_is_a_story_even_when_the_type_says_epic(self):
        self.assertEqual("story", self._level("## Tasks\n\n- [ ] 1.1 one\n"))
        self.assertEqual("story", self._level("## Tasks\n\n- [ ] 1.1 one\n",
                                              "workItemType: epic\n"))

    def test_one_wave_of_members_is_a_feature(self):
        self.assertEqual("feature", self._level(TASKS.replace("### 2. Delivery", "")))
        self.assertEqual("feature", self._level("## Tasks\n\n- [ ] S1 One — spec: #2\n"))

    def test_two_waves_of_members_are_an_epic(self):
        self.assertEqual("epic", self._level(TASKS))

    def test_a_task_only_wave_does_not_make_an_epic(self):
        self.assertEqual("feature", self._level(
            "## Tasks\n\n### 1. One\n- [ ] S1 A — spec: #2\n"
            "### 2. Two\n- [ ] 2.1 work\n"))

    def test_the_label_and_the_card_state_carry_the_level(self):
        from quenching.specs import cards
        info = derive_info({"id": 1, "phase": "plans"}, doc())
        self.assertIn("spec:epic", derive_labels(info))
        state = cards.card_state(info, [{"id": 2, "label": "S1", "title": "Foundation",
                                         "status": "in-progress"}])
        self.assertEqual("epic", state["level"])
        self.assertEqual("executing", state["board"])
        body = cards.render_card_body(state, None, "branch quenching, specs/1.md")
        self.assertIn("Level: Epic", body)
        self.assertIn("Specs 0/1", body)
        self.assertIn("S1 spec 2 — in-progress: Foundation", body)

    def test_the_board_follows_a_ready_or_unmerged_member(self):
        info = derive_info({"id": 1, "phase": "plans"}, doc())
        for status in ("ready", "unmerged", "in-progress"):
            rows = [{"id": 2, "label": "S1", "title": "x", "status": status}]
            self.assertEqual("executing", board_state_of(info, rows))
        rows = [{"id": 2, "label": "S1", "title": "x", "status": "done"}]
        self.assertNotEqual("executing", board_state_of(info, rows))


class NestingAndCycles(unittest.TestCase):
    def test_a_composite_may_be_a_member_and_finishes_only_when_archived(self):
        child = derive_info({"id": 3, "phase": "plans"}, doc("Child"))
        parent = derive_info({"id": 1, "phase": "plans"},
                             doc("Parent", tasks="## Tasks\n\n- [ ] S1 Child — spec: #3\n"))
        got = derive_composition(parent, {"3": child})
        self.assertEqual("ready", got["items"][0]["status"])
        archived = derive_info({"id": 3, "phase": "archive"},
                               doc("Child", "outcome: done\n", "## Tasks\n\n"))
        got = derive_composition(parent, {"3": archived})
        self.assertEqual("done", got["items"][0]["status"])

    def test_a_member_cycle_is_found_across_documents(self):
        a = derive_info({"id": 1, "phase": "plans"},
                        doc("A", tasks="## Tasks\n\n- [ ] S1 B — spec: #2\n"))
        b = derive_info({"id": 2, "phase": "plans"},
                        doc("B", tasks="## Tasks\n\n- [ ] S1 A — spec: #1\n"))
        self.assertEqual(["1", "2", "1"], composition_cycle({"1": a, "2": b}))

    def test_a_missing_member_is_reported_and_never_satisfies_a_dependency(self):
        parent = derive_info({"id": 1, "phase": "plans"},
                             doc("Parent", tasks="## Tasks\n\n- [ ] S1 Ghost — spec: #9\n"))
        got = derive_composition(parent, {"9": None})
        self.assertEqual("missing", got["items"][0]["status"])


class CommandSurface(unittest.TestCase):
    def setUp(self):
        self.b = MemoryBackend()
        self.b.create_spec("plans", doc("Program"))
        self.b.create_spec("plans", doc("Foundation", "approved: yes\n",
                                        "## Tasks\n\n- [ ] 1.1 build\n"))
        self.b.create_spec("plans", doc("Migration", "approved: yes\n",
                                        "## Tasks\n\n- [ ] 1.1 build\n"))

    def _link(self, member, **kw):
        kw.setdefault("after", None)
        kw.setdefault("group", None)
        kw.setdefault("label", None)
        return run(epic_cmd.cmd_epic, self.b, link_cmd="add", epic=1, spec=member, **kw)

    def test_status_spec_auto_detects_the_composition(self):
        self._link(2, group="1. Foundations")
        code, got = run(read_cmd.cmd_status, self.b, spec=1, epic=None, no_fetch=False)
        self.assertEqual(0, code, got)
        # The task/records half survives: a composite is also developed and executed.
        self.assertEqual(1, got["id"])
        self.assertIn("records", got)
        self.assertEqual("epic", got["level"])
        self.assertEqual(2, got["composition"]["progress"]["total"])
        self.assertEqual("S1", got["composition"]["items"][0]["label"])

    def test_next_runs_the_tasks_first_then_hands_the_members_over(self):
        self._link(2, group="1. Foundations")
        code, got = run(next_cmd.cmd_next, self.b, spec=1, epic=None, front=False,
                        limit=None)
        self.assertEqual((0, "implement_task", "1.1"), (code, got["action"], got["task"]))
        run(task_cmd.cmd_task, self.b, spec=1, check="1.1", uncheck=None, block=None,
            descope=None, reason=None, subject=None, commit=None)
        code, got = run(next_cmd.cmd_next, self.b, spec=1, epic=None, front=False,
                        limit=None)
        self.assertEqual((0, "orchestrate"), (code, got["action"]))
        self.assertEqual(["S1"], [r["label"] for r in got["ready"]])

    def test_task_tick_toggles_an_ordinary_task_and_refuses_a_spec_item(self):
        self._link(2)
        code, got = run(task_cmd.cmd_task, self.b, spec=1, check="S1", uncheck=None,
                        block=None, descope=None, reason=None, subject=None, commit=None)
        self.assertEqual((2, "sp-link-derived-task"), (code, got["code"]))
        code, got = run(task_cmd.cmd_task, self.b, spec=1, check="1.1", uncheck=None,
                        block=None, descope=None, reason=None, subject=None, commit=None)
        self.assertEqual(0, code, got)

    def test_the_archive_gate_counts_tasks_and_members(self):
        self._link(2)
        code, got = run(epic_cmd.cmd_epic, self.b, epic_cmd="add", epic=1, spec=3,
                        after=None, group=None, label=None)
        self.assertEqual(0, code, got)
        from quenching.specs.commands import promote as promote_cmd
        with mock.patch.object(promote_cmd, "open_backend", return_value=(self.b, {})):
            args = argparse.Namespace(json=True, spec=1, to=None, outcome="done",
                                      force=False, dry_run=True)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = promote_cmd.cmd_promote(args, tempfile.gettempdir(), Emitter())
        payload = json.loads(buf.getvalue())
        self.assertEqual((2, "sp-open-tasks"), (code, payload["code"]))
        self.assertEqual((4, 4), (payload["open"], payload["total"]))

    def test_validate_reports_a_cross_document_cycle_once(self):
        self._link(2)
        other, _ = self.b.read_spec(2)
        self.b.write_spec(other, other["text"].replace("## Tasks\n\n",
                                                       "## Tasks\n\n- [ ] S1 Back — spec: #1\n"))
        code, got = run(validate_cmd.cmd_validate, self.b, spec=None, phase=None,
                        by_code=False)
        cycles = [f for f in got["findings"] if f["code"] == "sp-link-member-cycle"]
        self.assertEqual(1, len(cycles))
        self.assertEqual(["1", "2", "1"], cycles[0]["cycle"])
        self.assertFalse(got["ok"])


if __name__ == "__main__":
    unittest.main()
