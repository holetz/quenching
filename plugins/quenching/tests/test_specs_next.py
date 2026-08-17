"""`_work_ref` — which ref `cq specs next` treats as a spec's work branch, and the one shape
that is NOT one: the in-place record `execute` stamps with `work` equal to `base`.

That pair is the whole reason this suite exists. The base branch is always alive, so a
consumer reading it as a live work ref ranks every spec built in place as permanently in
flight — `live` and `current` both true forever, on a ref it never took. `git.md` §Where a
branch comes from owns the rule; `test_specs_find.py` asserts the sibling guard in
`find_match`.
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.commands.next import (TABLE_COLUMNS, _cell, _order_key,
                                           _resolve_columns, _state, _table_row, _work_ref)


class WorkRef(unittest.TestCase):
    def test_a_stamped_work_ref_is_the_answer(self):
        fm = {"branch": {"base": "develop", "work": "plan/alpha"}}
        self.assertEqual(_work_ref(fm, "alpha"), "plan/alpha")

    def test_no_record_falls_back_to_the_default_name(self):
        # A human may have cut `plan/<slug>` by hand, with no record at all — the ref being
        # alive is what counts, so the default name stays the thing to look for.
        self.assertEqual(_work_ref({}, "alpha"), "plan/alpha")

    def test_a_malformed_record_falls_back_the_same_way(self):
        self.assertEqual(_work_ref({"branch": "develop"}, "alpha"), "plan/alpha")
        self.assertEqual(_work_ref({"branch": {}}, "alpha"), "plan/alpha")

    def test_work_equal_to_base_is_no_work_ref_at_all(self):
        fm = {"branch": {"base": "develop", "work": "develop"}}
        self.assertIsNone(_work_ref(fm, "alpha"),
                          "a spec built in place must not rank as in flight on its base")

    def test_the_in_place_answer_does_not_depend_on_the_base_being_named_main(self):
        for base in ("main", "develop", "trunk", "release/7.x"):
            with self.subTest(base=base):
                self.assertIsNone(_work_ref({"branch": {"base": base, "work": base}}, "alpha"))


def _candidate(**over):
    """A `_candidate` payload with only the keys the table renderer reads."""
    c = {"slug": "alpha", "title": "Alpha the titled", "summary": None, "stage": "ready",
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
    def test_summary_falls_back_to_the_title_and_says_so(self):
        cells, fellback = _table_row(_candidate(), False)
        self.assertEqual(cells["summary"], "Alpha the titled")
        self.assertTrue(fellback, "an unwritten summary must be reported, never silent")

    def test_a_written_summary_wins_and_is_not_reported_as_a_fallback(self):
        cells, fellback = _table_row(_candidate(summary="One line about alpha"), False)
        self.assertEqual(cells["summary"], "One line about alpha")
        self.assertFalse(fellback)

    def test_a_long_summary_is_elided_not_truncated_silently(self):
        cells, _ = _table_row(_candidate(summary="x" * 400), False)
        self.assertTrue(cells["summary"].endswith("…"))
        self.assertLessEqual(len(cells["summary"]), 120)

    def test_the_recommended_row_carries_the_mold_glyph(self):
        cells, _ = _table_row(_candidate(), True)
        self.assertTrue(cells["spec"].startswith("→ "))
        self.assertFalse(_table_row(_candidate(), False)[0]["spec"].startswith("→"))

    def test_every_declared_column_is_produced(self):
        cells, _ = _table_row(_candidate(), False)
        self.assertEqual(set(cells), set(TABLE_COLUMNS),
                         "a column in the ordered set with no cell would print blank")

    def test_tasks_and_priority_render_the_mold_separator(self):
        cells, _ = _table_row(_candidate(
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
    RANKED = [{"_key": (1, 1, 0.0, 3.0, "2026-01-01", "gamma"), "date": "2026-01-01",
               "slug": "gamma", "priority": {"level": "3"}},
              {"_key": (0, 0, -0.5, 9.0, "2026-01-02", "alpha"), "date": "2026-01-02",
               "slug": "alpha", "priority": {"level": "9"}},
              {"_key": (1, 1, 0.0, 1.0, "2026-01-03", "beta"), "date": "2026-01-03",
               "slug": "beta", "priority": {"level": "1"}}]

    def test_rank_is_the_four_factor_ordering_this_module_owns(self):
        got = [c["slug"] for c in sorted(self.RANKED, key=_order_key("rank"))]
        self.assertEqual(got, ["alpha", "beta", "gamma"],
                         "the live branch / executing spec leads under `rank`")

    def test_priority_is_the_human_ranking_alone(self):
        got = [c["slug"] for c in sorted(self.RANKED, key=_order_key("priority"))]
        self.assertEqual(got, ["beta", "gamma", "alpha"])

    def test_an_unranked_spec_sorts_last_under_priority_never_first(self):
        rows = self.RANKED + [{"_key": (1, 1, 0.0, float("inf"), "2026-01-04", "delta"),
                               "date": "2026-01-04", "slug": "delta", "priority": None}]
        got = [c["slug"] for c in sorted(rows, key=_order_key("priority"))]
        self.assertEqual(got[-1], "delta")


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
