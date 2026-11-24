"""`_work_ref` — which ref `cq specs next` treats as a spec's work branch, and the one shape
that is NOT one: the in-place record `execute` stamps with `work` equal to `base`.

That pair is the whole reason this suite exists. The base branch is always alive, so a
consumer reading it as a live work ref ranks every spec built in place as permanently in
flight — `live` and `current` both true forever, on a ref it never took. `git.md` §Where a
branch comes from owns the rule; `test_specs_find.py` asserts the sibling guard in
`find_match`.
"""
import pathlib
import argparse
import contextlib
import datetime
import importlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.commands.next import (TABLE_COLUMNS, _cell, _order_key,
                                           _resolve_columns, _state, _table_row, _work_ref)
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands.output import Emitter
from test_specs_promote_gate import _document

next_module = importlib.import_module("quenching.specs.commands.next")


def _snapshot(leases=None, available=True):
    return {"available": available, "scope": "remote", "me": "mine", "leases": leases or {},
            "at": datetime.datetime(2026, 11, 24, 12, 0, tzinfo=datetime.timezone.utc)}


def _lease(holder, minutes=30):
    expires = datetime.datetime(2026, 11, 24, 12, 0) + datetime.timedelta(minutes=minutes)
    return {"holder": f"{holder}:s", "label": "box", "expires": expires.strftime("%Y-%m-%dT%H:%M:%SZ")}


class ClaimedFront(unittest.TestCase):
    """`next --front` leaves out what another machine is building, and says so."""

    def setUp(self):
        self.backend = MemoryBackend()
        for _ in range(2):
            self.backend.create_spec("plans", _document("- [ ] 1.1 Open\n"))
        p = patch.object(next_module, "open_backend", return_value=(self.backend, {}))
        p.start()
        self.addCleanup(p.stop)
        for name, value in (("_git_refs", (set(), None)), ("front_fields", {})):
            q = patch.object(next_module, name, return_value=value)
            q.start()
            self.addCleanup(q.stop)

    def front(self, snap, **flags):
        with patch.object(next_module.claims, "snapshot", return_value=snap):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = next_module._next_front(
                    argparse.Namespace(json=True, **flags), ".", Emitter())
        self.assertEqual(0, code)
        return json.loads(buf.getvalue())

    def ids(self, payload):
        return [c["id"] for c in payload["candidates"]]

    def test_a_live_lease_of_another_machine_is_left_out_and_named(self):
        got = self.front(_snapshot({"1": _lease("other")}))
        self.assertEqual([2], self.ids(got))
        self.assertEqual(([1], 2, True), (got["claimedExcluded"], got["top"], got["claimsAvailable"]))

    def test_include_claimed_lists_it_with_the_claim(self):
        got = self.front(_snapshot({"1": _lease("other")}), include_claimed=True)
        self.assertEqual([1, 2], sorted(self.ids(got)))
        claim = next(c for c in got["candidates"] if c["id"] == 1)["claim"]
        self.assertEqual((True, False, "box"), (claim["live"], claim["mine"], claim["label"]))
        self.assertEqual([], got["claimedExcluded"])

    def test_my_own_an_expired_and_an_unreadable_lease_do_not_exclude(self):
        for snap in (_snapshot({"1": _lease("mine")}), _snapshot({"1": _lease("other", -30)}),
                     _snapshot(available=False)):
            self.assertEqual([1, 2], sorted(self.ids(self.front(snap))))
        self.assertTrue(next(c for c in self.front(_snapshot({"1": _lease("mine")}))["candidates"]
                             if c["id"] == 1)["claim"]["mine"])

    def test_the_flag_is_on_the_cli(self):
        from quenching.specs.commands.cli import build_parser
        parser, _ = build_parser()
        self.assertTrue(parser.parse_args(["next", "--front", "--include-claimed"]).include_claimed)
        self.assertFalse(parser.parse_args(["next", "--front"]).include_claimed)


class ReadVerbs(unittest.TestCase):
    """`list --lean` and `status --json` carry `claim` from the snapshot."""

    def setUp(self):
        self.backend = MemoryBackend()
        self.backend.create_spec("plans", _document("- [ ] 1.1 Open\n"))
        read = importlib.import_module("quenching.specs.commands.read")
        self.read = read
        p = patch.object(read, "open_backend", return_value=(self.backend, {}))
        p.start()
        self.addCleanup(p.stop)
        snap = _snapshot({"1": _lease("other")})
        q = patch.object(next_module.claims, "snapshot", return_value=snap)
        q.start()
        self.addCleanup(q.stop)

    def run_verb(self, fn, **flags):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = fn(argparse.Namespace(json=True, **flags), ".", Emitter())
        self.assertEqual(0, code)
        return json.loads(buf.getvalue())

    def test_list_lean_rows_carry_the_claim(self):
        got = self.run_verb(self.read.cmd_list, lean=True, phase=None)
        claim = got["specs"][0]["claim"]
        self.assertEqual((True, False, "box"), (claim["live"], claim["mine"], claim["label"]))

    def test_status_carries_the_claim_and_no_fetch_carries_none(self):
        got = self.run_verb(self.read.cmd_status, spec=1, epic=None, no_fetch=False)
        self.assertTrue(got["claim"]["live"])
        with patch.object(self.backend, "has_local_ref", return_value=True, create=True):
            got = self.run_verb(self.read.cmd_status, spec=1, epic=None, no_fetch=True)
        self.assertIsNone(got["claim"])


class PostMergeNext(unittest.TestCase):
    def setUp(self):
        self.backend = MemoryBackend()
        text = _document("- [x] 1.1 Done\n").replace(
            "date: 2026-08-11\n",
            "date: 2026-08-11\nbranch:\n  base: main\n  work: plan/1-x\n", 1)
        self.backend.create_spec("plans", text)
        p = patch.object(next_module, "open_backend", return_value=(self.backend, {}))
        p.start()
        self.addCleanup(p.stop)
        q = patch.object(next_module.claims, "snapshot", return_value=_snapshot())
        q.start()
        self.addCleanup(q.stop)

    def test_front_reports_merged_specs_offline_without_reading_them_twice(self):
        with patch.object(next_module, "_git_refs", return_value=(set(), None)), \
                patch.object(next_module, "front_fields", return_value={}), \
                patch.object(next_module.promote, "merge_evidence",
                             return_value=(True, "merge record")) as evidence, \
                patch.object(self.backend, "read_spec", wraps=self.backend.read_spec) as read:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = next_module._next_front(argparse.Namespace(json=True), ".", Emitter())
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["mergedNotArchived"], [
            {"id": 1, "title": "Gate fixture", "reason": "merge record"}])
        evidence.assert_called_once()
        self.assertEqual(evidence.call_args.kwargs, {"fetch": False, "ask_pr": False})
        read.assert_called_once_with(1)
        self.assertNotIn("_info", payload["candidates"][0])

    def test_complete_spec_points_to_reconcile_after_merge(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = next_module.cmd_next(
                argparse.Namespace(json=True, front=False, spec=1), ".", Emitter())
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["action"], "promote")
        self.assertEqual(payload["to"], "archive")
        self.assertEqual(payload["message"], "all tasks complete — write ## Outcome and open "
                         "the PR; after the merge, `cq specs reconcile --write` archives it")


class WorkRef(unittest.TestCase):
    TITLE = "Alpha the titled"

    def test_a_stamped_work_ref_is_the_answer(self):
        fm = {"branch": {"base": "develop", "work": "plan/974-alpha"}}
        self.assertEqual(_work_ref(fm, 974, self.TITLE), "plan/974-alpha")

    def test_no_record_falls_back_to_the_default_name(self):
        # A human may have cut `plan/<id>-<handle>` by hand, with no record at all — the ref
        # being alive is what counts, so the default name stays the thing to look for.
        self.assertEqual(_work_ref({}, 974, self.TITLE), "plan/974-alpha-the-titled")

    def test_the_default_name_leads_on_the_id_and_the_handle_is_cosmetic(self):
        # `plan/974-<anything>` is resolved by `974`; the handle is there so `git branch`
        # reads as titles. A spec with no title still gets a nameable branch.
        self.assertEqual(_work_ref({}, 974, ""), "plan/974-spec")

    def test_a_malformed_record_falls_back_the_same_way(self):
        self.assertEqual(_work_ref({"branch": "develop"}, 974, self.TITLE),
                         "plan/974-alpha-the-titled")
        self.assertEqual(_work_ref({"branch": {}}, 974, self.TITLE),
                         "plan/974-alpha-the-titled")

    def test_work_equal_to_base_is_no_work_ref_at_all(self):
        fm = {"branch": {"base": "develop", "work": "develop"}}
        self.assertIsNone(_work_ref(fm, 974, self.TITLE),
                          "a spec built in place must not rank as in flight on its base")

    def test_the_in_place_answer_does_not_depend_on_the_base_being_named_main(self):
        for base in ("main", "develop", "trunk", "release/7.x"):
            with self.subTest(base=base):
                self.assertIsNone(
                    _work_ref({"branch": {"base": base, "work": base}}, 974, self.TITLE))


def _candidate(**over):
    """A `_candidate` payload with only the keys the table renderer reads."""
    c = {"id": 974, "title": "Alpha the titled", "stage": "ready",
         "tasks": {"checked": 0, "blocked": 0, "total": 0}, "priority": None,
         "records": {"priority": None, "refined": None}, "ageDays": 3, "state": None}
    c.update(over)
    return c


class State(unittest.TestCase):
    """`_state` — the one thing worth saying beyond the stage, in the sweep's vocabulary."""

    BRANCH = {"work": "plan/alpha", "live": False, "current": False}

    def test_a_blocked_task_outranks_everything_else(self):
        # Blocked outranks complete deliberately: a spec can be both (every box ticked or
        # blocked), and the blocked one is what a human has to act on.
        got = _state({"checked": 4, "blocked": 1, "total": 5}, True,
                     {"work": "plan/alpha", "live": True, "current": True}, 500)
        self.assertEqual(got, "sp-spec-blocked")

    def test_every_box_ticked_is_complete(self):
        self.assertEqual(_state({"checked": 5, "blocked": 0, "total": 5}, True,
                                self.BRANCH, 3), "sp-spec-complete")

    def test_no_tasks_at_all_is_not_complete(self):
        # 0/0 is a spec nobody has written tasks for, not a finished one.
        self.assertIsNone(_state({"checked": 0, "blocked": 0, "total": 0}, False,
                                 self.BRANCH, 3))

    def test_the_branch_fact_when_no_code_applies(self):
        tasks = {"checked": 1, "blocked": 0, "total": 5}
        self.assertEqual(_state(tasks, True, {"work": "plan/alpha", "live": True,
                                              "current": True}, 3), "on this branch")
        self.assertEqual(_state(tasks, True, {"work": "plan/alpha", "live": True,
                                              "current": False}, 3), "in flight on plan/alpha")

    def test_staleness_needs_open_work_to_mean_anything(self):
        idle = {"checked": 0, "blocked": 0, "total": 0}
        # 90 days is `sp-spec-stale`'s own threshold, per specs-align/conformance.md.
        self.assertIsNone(_state(idle, False, self.BRANCH, 200),
                          "a spec nobody started is waiting, not rotting")
        self.assertEqual(_state(idle, True, self.BRANCH, 200), "sp-spec-stale (200d)")
        self.assertIsNone(_state(idle, True, self.BRANCH, 89))


class TableRow(unittest.TestCase):
    def test_the_summary_column_is_sourced_from_the_native_title(self):
        # `summary:` is retired — `optional-payload-fields.md` §Retired fields stay retired.
        # The column keeps its name and reads the title, so there is no fallback to report
        # and no second value that could disagree with it.
        cells = _table_row(_candidate(), False)
        self.assertEqual(cells["summary"], "Alpha the titled")

    def test_a_retired_summary_key_on_the_candidate_is_never_read(self):
        cells = _table_row(_candidate(summary="One line about alpha"), False)
        self.assertEqual(cells["summary"], "Alpha the titled",
                         "a stray `summary` must not outrank the title the column now reads")

    def test_a_long_title_is_elided_not_truncated_silently(self):
        cells = _table_row(_candidate(title="x" * 400), False)
        self.assertTrue(cells["summary"].endswith("…"))
        self.assertLessEqual(len(cells["summary"]), 120)

    def test_the_spec_cell_is_the_native_id(self):
        self.assertEqual(_table_row(_candidate(), False)["spec"], "974")

    def test_the_recommended_row_carries_the_mold_glyph(self):
        cells = _table_row(_candidate(), True)
        self.assertTrue(cells["spec"].startswith("→ "))
        self.assertFalse(_table_row(_candidate(), False)["spec"].startswith("→"))

    def test_every_declared_column_is_produced(self):
        cells = _table_row(_candidate(), False)
        self.assertEqual(set(cells), set(TABLE_COLUMNS),
                         "a column in the ordered set with no cell would print blank")

    def test_tasks_and_priority_render_the_mold_separator(self):
        cells = _table_row(_candidate(
            tasks={"checked": 2, "blocked": 1, "total": 5},
            priority={"level": "3", "criticality": "high", "complexity": "low"}), False)
        self.assertEqual(cells["tasks"], "2/5 · 1 blocked")
        self.assertEqual(cells["priority"], "3 · high")
        self.assertEqual(cells["complexity"], "low")


class Cell(unittest.TestCase):
    def test_an_empty_value_is_the_not_yet_glyph(self):
        for empty in (None, "", 0):
            self.assertEqual(_cell(empty), "—")

    def test_a_pipe_in_a_value_cannot_break_the_table(self):
        self.assertEqual(_cell("a | b"), r"a \| b")

    def test_a_newline_never_reaches_a_row(self):
        self.assertEqual(_cell("two\nlines"), "two lines")


class ResolveColumns(unittest.TestCase):
    def test_nothing_asked_prints_the_whole_declared_set(self):
        self.assertEqual(_resolve_columns(None), (list(TABLE_COLUMNS), []))
        self.assertEqual(_resolve_columns(""), (list(TABLE_COLUMNS), []))

    def test_a_subset_is_omitted_from_the_declared_order_never_reordered(self):
        # §The spec table: a command OMITS a column, never reorders one. Asking in a
        # scrambled order must come back in the declared one, or the mold's ordering rule is
        # enforced only by whoever remembers to type it.
        got, unknown = _resolve_columns("state,spec,age")
        self.assertEqual(got, ["spec", "age", "state"])
        self.assertEqual(unknown, [])

    def test_whitespace_and_case_do_not_change_the_answer(self):
        self.assertEqual(_resolve_columns(" Spec , STAGE ")[0], ["spec", "stage"])

    def test_an_unknown_column_is_named_and_nothing_is_printed(self):
        got, unknown = _resolve_columns("spec,invented,stage")
        self.assertEqual(unknown, ["invented"])
        self.assertEqual(got, [], "a refusal must not fall through to a partial table")


class OrderKey(unittest.TestCase):
    # The final tiebreak is `str(c["id"])`, so these IDs are ordered by their STRING form —
    # which is what the sort actually compares, and the reason the key stringifies at all:
    # `github` hands back ints and `azure-boards` hands back ints of a different magnitude,
    # and a mixed front must not raise on `int > str`.
    RANKED = [{"_key": (1, 1, 0.0, 3.0, "2026-01-01", "31"), "date": "2026-01-01",
               "id": 31, "priority": {"level": "3"}},
              {"_key": (0, 0, -0.5, 9.0, "2026-01-02", "11"), "date": "2026-01-02",
               "id": 11, "priority": {"level": "9"}},
              {"_key": (1, 1, 0.0, 1.0, "2026-01-03", "21"), "date": "2026-01-03",
               "id": 21, "priority": {"level": "1"}}]

    def test_rank_is_the_four_factor_ordering_this_module_owns(self):
        got = [c["id"] for c in sorted(self.RANKED, key=_order_key("rank"))]
        self.assertEqual(got, [11, 21, 31],
                         "the live branch / executing spec leads under `rank`")

    def test_priority_is_the_human_ranking_alone(self):
        got = [c["id"] for c in sorted(self.RANKED, key=_order_key("priority"))]
        self.assertEqual(got, [21, 31, 11])

    def test_an_unranked_spec_sorts_last_under_priority_never_first(self):
        rows = self.RANKED + [{"_key": (1, 1, 0.0, float("inf"), "2026-01-04", "41"),
                               "date": "2026-01-04", "id": 41, "priority": None}]
        got = [c["id"] for c in sorted(rows, key=_order_key("priority"))]
        self.assertEqual(got[-1], 41)

    def test_a_string_id_and_an_int_id_sort_together_rather_than_raising(self):
        # A hybrid front is exactly where this bit: `sorted` compares the tiebreak directly,
        # and `int` against `str` is a TypeError, not a ranking.
        rows = [{"date": "2026-01-01", "id": 7, "priority": {"level": "1"}},
                {"date": "2026-01-01", "id": "961489", "priority": {"level": "1"}}]
        self.assertEqual([c["id"] for c in sorted(rows, key=_order_key("priority"))],
                         [7, "961489"], "\"7\" sorts before \"961489\" as strings")


class TableRefusesJson(unittest.TestCase):
    """`--table` IS the human rendering, so emitting a payload beside it would put one
    ranking on two surfaces that can drift. The guard runs before the backend opens, which
    is what lets this assert against a workspace holding nothing."""

    def test_table_with_json_exits_two(self):
        cq = pathlib.Path(__file__).resolve().parents[1] / "assets" / "bin" / "cq"
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / ".specs"
            (root / "plans").mkdir(parents=True)
            run = subprocess.run(
                [sys.executable, str(cq), "specs", "--root", str(root),
                 "next", "--front", "--table", "--json"],
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
            self.assertIn("sp-table-not-json", run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
