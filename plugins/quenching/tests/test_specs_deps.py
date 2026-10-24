"""Spec dependencies, offline: pure findings and date scheduling over info maps."""
import copy
import pathlib
import sys
import unittest

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.specs.parse.deps import dep_findings, deps_of, find_cycle, schedule


def info(phase="plans", **fm):
    return {"phase": phase, "frontmatter": fm}


def by_id(result):
    return {node["id"]: node for node in result["nodes"]}


class DependencyParsing(unittest.TestCase):
    def test_forms_normalization_and_order(self):
        for raw, expected in (
            (None, []), ("", []), ([], []), ("2036", ["2036"]),
            (" #2036, 2037, , #2036, # ", ["2036", "2037"]),
            ([" 2037 ", "#2036", "", " # 2037 "], ["2037", "2036"]),
            ([2036, 2037], ["2036", "2037"]),
        ):
            with self.subTest(raw=raw):
                self.assertEqual(expected, deps_of({"dependsOn": raw}))
        self.assertEqual([], deps_of({}))

    def test_cycle_search_is_sorted_and_ignores_unknown_nodes(self):
        self.assertEqual(["A", "B", "A"], find_cycle({
            "Z": ["Z"], "B": ["A"], "A": ["missing", "B"],
        }))
        self.assertIsNone(find_cycle({"B": ["A", "missing"], "A": []}))
        self.assertIsNone(find_cycle({}))


class DependencyFindings(unittest.TestCase):
    def test_missing_and_self_are_errors_in_sorted_spec_order(self):
        infos = {"12": info(dependsOn="12, 99"), "10": info(dependsOn="98")}
        got = dep_findings(infos)
        self.assertEqual(["10", "12", "12"], [row["spec"] for row in got])
        self.assertEqual(["sp-dep-missing", "sp-dep-self", "sp-dep-missing"],
                         [row["code"] for row in got])
        self.assertTrue(all(row["severity"] == "error" for row in got))
        self.assertEqual("spec 12 depends on 99, which is not in the store", got[-1]["message"])
        self.assertIsNone(schedule(infos)["cycle"])

    def test_archive_outcomes_are_trimmed_and_only_done_is_done(self):
        for outcome, expected in ((" done ", []), (None, [""]), ("", [""]),
                                  (" dropped ", ["dropped"]), ("DONE", ["DONE"])):
            with self.subTest(outcome=outcome):
                rows = dep_findings({"A": info("archive", outcome=outcome),
                                     "B": info(dependsOn="A")})
                self.assertEqual(expected, [row["outcome"] for row in rows])
                if rows:
                    self.assertEqual(("sp-dep-dropped", "warn", "B"),
                                     (rows[0]["code"], rows[0]["severity"], rows[0]["spec"]))

    def test_cycle_is_reported_once_and_schedule_derives_nothing(self):
        infos = {"C": info(dependsOn="A"), "B": info(dependsOn="C"),
                 "A": info(dependsOn="A, B")}
        rows = dep_findings(infos)
        self.assertEqual(["sp-dep-self", "sp-dep-cycle"], [row["code"] for row in rows])
        cycle = ["A", "B", "C", "A"]
        self.assertEqual(cycle, rows[-1]["cycle"])
        self.assertEqual(("A", "error"), (rows[-1]["spec"], rows[-1]["severity"]))
        self.assertIn("A -> B -> C -> A", rows[-1]["message"])
        self.assertEqual({"cycle": cycle, "nodes": [], "criticalPath": []}, schedule(infos))


class DependencySchedule(unittest.TestCase):
    def test_chain_shifts_dates_and_marks_the_critical_path(self):
        infos = {
            "C": info(title="Third", dependsOn="B", start="2026-01-12", target="2026-01-15"),
            "B": info(dependsOn="A", start="2026-01-05", target="2026-01-08"),
            "A": info(start="2026-01-01", target="2026-01-10"),
        }
        before = copy.deepcopy(infos)
        got = schedule(infos)
        nodes = by_id(got)
        self.assertIsNone(got["cycle"])
        self.assertEqual(["A", "B", "C"], got["criticalPath"])
        self.assertEqual(["A", "B", "C"], [node["id"] for node in got["nodes"]])
        for spec, start, finish, slip, driver in (
            ("A", "2026-01-01", "2026-01-10", 0, None),
            ("B", "2026-01-10", "2026-01-13", 5, "A"),
            ("C", "2026-01-13", "2026-01-16", 1, "B"),
        ):
            node = nodes[spec]
            self.assertEqual((start, finish, slip, driver, True),
                             (node["earliestStart"], node["earliestFinish"], node["slipDays"],
                              node["drivenBy"], node["critical"]))
        self.assertEqual(("Third", "plans", "2026-01-12", "2026-01-15", ["B"]),
                         tuple(nodes["C"][key] for key in ("title", "phase", "start", "target", "dependsOn")))
        self.assertEqual(before, infos)

    def test_later_dependency_drives_a_fork(self):
        got = schedule({
            "A": info(target="2026-01-05"), "B": info(target="2026-01-10"),
            "C": info(dependsOn=["A", "B"], start="2026-01-01", target="2026-01-03"),
        })
        nodes = by_id(got)
        self.assertEqual(("2026-01-10", "2026-01-12", "B", 9),
                         tuple(nodes["C"][key] for key in
                               ("earliestStart", "earliestFinish", "drivenBy", "slipDays")))
        self.assertEqual(["B", "C"], got["criticalPath"])
        self.assertFalse(nodes["A"]["critical"])

    def test_undated_and_invalid_dates_stay_unknown(self):
        for fm in ({}, {"start": "invalid", "target": "2026-02-30"}):
            with self.subTest(fm=fm):
                got = schedule({"A": info(**fm)}, ["A"])
                node = got["nodes"][0]
                self.assertEqual([None] * 4, [node[key] for key in
                                             ("start", "target", "earliestStart", "earliestFinish")])
                self.assertEqual((0, None, False), (node["slipDays"], node["drivenBy"], node["critical"]))
                self.assertEqual([], got["criticalPath"])

    def test_archived_done_uses_its_own_target_to_constrain_successor(self):
        got = schedule({
            "X": info(target="2026-02-01"),
            "A": info("archive", dependsOn="X", outcome=" done ",
                      start="2026-01-01", target="2026-01-10"),
            "B": info(dependsOn="A", start="2026-01-05", target="2026-01-07"),
        })
        node = by_id(got)["B"]
        self.assertEqual(("2026-01-10", "2026-01-12", "A"),
                         (node["earliestStart"], node["earliestFinish"], node["drivenBy"]))

    def test_dropped_or_undated_done_dependency_adds_no_constraint(self):
        for fm in ({"outcome": "dropped", "target": "2026-02-01"}, {"outcome": "done"}):
            with self.subTest(fm=fm):
                got = schedule({"A": info("archive", **fm),
                                "B": info(dependsOn="A", start="2026-01-05", target="2026-01-07")})
                node = by_id(got)["B"]
                self.assertEqual(("2026-01-05", "2026-01-07", 0, None),
                                 tuple(node[key] for key in
                                       ("earliestStart", "earliestFinish", "slipDays", "drivenBy")))

    def test_unknown_open_dependency_finish_propagates_as_unknown(self):
        got = schedule({"A": info(),
                        "B": info(dependsOn="A", start="2026-01-05", target="2026-01-07")}, ["B"])
        node = by_id(got)["B"]
        self.assertEqual((None, None, 0), (node["earliestStart"], node["earliestFinish"], node["slipDays"]))

    def test_archived_done_node_reports_its_own_target_as_finish(self):
        got = schedule({
            "X": info(start="2026-01-01", target="2026-01-08"),
            "A": info("archive", dependsOn="X", outcome="done",
                      start="2026-01-01", target="2026-01-10"),
            "B": info(dependsOn="A", start="2026-01-01", target="2026-01-03"),
        }, ["B"])
        nodes = by_id(got)
        self.assertEqual("2026-01-10", nodes["A"]["earliestFinish"])
        self.assertEqual("2026-01-10", nodes["B"]["earliestStart"])

    def test_selection_closes_dependencies_and_skips_missing_specs(self):
        infos = {"A": info(), "B": info(dependsOn="A, ghost"),
                 "C": info(dependsOn="B"), "isolated": info(),
                 "old": info("archive", dependsOn="isolated")}
        self.assertEqual({"A", "B", "C"}, set(by_id(schedule(infos))))
        self.assertEqual({"A", "B"}, set(by_id(schedule(infos, ["B", "ghost"]))))
        self.assertEqual(["A", "ghost"], by_id(schedule(infos))["B"]["dependsOn"])
        self.assertEqual({"cycle": None, "nodes": [], "criticalPath": []}, schedule(infos, []))
        self.assertEqual([], schedule({})["nodes"])

    def test_own_start_wins_ties_and_dependency_ties_keep_declaration_order(self):
        infos = {"A": info(target="2026-01-10"), "B": info(target="2026-01-10"),
                 "C": info(dependsOn="B, A", start="2026-01-10", target="2026-01-11")}
        self.assertIsNone(by_id(schedule(infos))["C"]["drivenBy"])
        infos["C"]["frontmatter"]["start"] = "2026-01-09"
        self.assertEqual("B", by_id(schedule(infos))["C"]["drivenBy"])
        self.assertEqual(["A"], schedule(infos, ["A", "B"])["criticalPath"])

    def test_target_fallback_and_reversed_dates_do_not_invent_duration(self):
        got = schedule({"A": info(start="2026-01-10", target="2026-01-05"),
                        "B": info(dependsOn="A"), "C": info(target="2026-01-03")},
                       ["B", "C"])
        nodes = by_id(got)
        self.assertEqual("2026-01-05", nodes["A"]["earliestFinish"])
        self.assertEqual(("2026-01-05", None, 0),
                         (nodes["B"]["earliestStart"], nodes["B"]["earliestFinish"], nodes["B"]["slipDays"]))
        self.assertEqual("C", got["nodes"][-1]["id"])


if __name__ == "__main__":
    unittest.main()
