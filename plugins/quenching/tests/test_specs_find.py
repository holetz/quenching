"""`find_match` — the reverse lookup `cq specs find` runs: a branch, a commit's subject, or a
PR number resolved back to the spec that recorded it. Self-contained — `MemoryBackend`, no git,
no `open_backend` config resolution; `_pr_number` and the sha-to-subject step are exercised in
`cmd_find` itself, which this file does not call.
"""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands.find import _pr_number, find_match


def _doc(slug: str, *, branch=None, pr=None, merge=None, task_subject=None) -> str:
    lines = ["---", f"slug: {slug}", f"title: {slug.title()}", "date: 2026-08-01"]
    if branch:
        lines.append(f"branch: {{base: {branch['base']}, work: {branch['work']}}}")
    if pr:
        lines.append(f"pr: {{number: {pr['number']}, url: {pr['url']}, date: 2026-08-10}}")
    if merge:
        lines.append(f"merge: {{strategy: squash, subject: none, pr: {merge['pr']}}}")
    lines += ["---", "", "## Problem", "", "x", ""]
    if task_subject:
        lines += ["## Tasks", "", "### 1. Work", "",
                  f"- [x] 1.1 Do it\n      subject: {task_subject}", ""]
    return "\n".join(lines)


class FindMatch(unittest.TestCase):
    def setUp(self):
        self.backend = MemoryBackend()
        self.backend.create_spec("plans", "alpha.md",
                                 _doc("alpha", branch={"base": "develop", "work": "plan/alpha"}))
        self.backend.create_spec(
            "plans", "beta.md",
            _doc("beta", pr={"number": "42", "url": "https://github.com/o/r/pull/42"}))
        self.backend.create_spec(
            "plans", "gamma.md",
            _doc("gamma", task_subject="plan/gamma: 2.1 Add the thing"))
        self.backend.create_spec(
            "plans", "delta.md",
            _doc("delta", merge={"pr": "https://github.com/o/r/pull/99"}))
        self.backend.create_spec(
            "plans", "epsilon.md",
            _doc("epsilon", branch={"base": "develop", "work": "develop"}))

    def test_branch_resolves_the_owning_slug(self):
        hit = find_match(self.backend, branch="plan/alpha")
        self.assertEqual(hit["info"]["slug"], "alpha")
        self.assertEqual(hit["matchedBy"], "branch")

    def test_pr_number_resolves_against_the_pr_record(self):
        hit = find_match(self.backend, pr="42")
        self.assertEqual(hit["info"]["slug"], "beta")

    def test_pr_number_resolves_against_merge_pr_too(self):
        hit = find_match(self.backend, pr="99")
        self.assertEqual(hit["info"]["slug"], "delta")

    def test_commit_subject_resolves_against_a_tasks_recorded_subject(self):
        hit = find_match(self.backend, commit_subject="plan/gamma: 2.1 Add the thing")
        self.assertEqual(hit["info"]["slug"], "gamma")

    def test_an_in_place_record_never_answers_for_its_base(self):
        # `epsilon` records `work == base == develop` — a spec built in place, not the owner
        # of `develop`. Every such spec records the same name, so a match here would hand
        # back an arbitrary one of them as if it owned the ref (`git.md` §Where a branch
        # comes from). The sibling guard in `cq specs next` lives in `test_specs_next.py`.
        self.assertIsNone(find_match(self.backend, branch="develop"))

    def test_no_criterion_matches_returns_none(self):
        self.assertIsNone(find_match(self.backend, branch="plan/nonesuch"))
        self.assertIsNone(find_match(self.backend, pr="1"))
        self.assertIsNone(find_match(self.backend, commit_subject="nothing recorded this"))


class PrNumber(unittest.TestCase):
    """Both forms `--pr` and a recorded `pr`/`merge.pr` field may carry — a bare number and a
    full URL — normalise to the same trailing digits so either side of the comparison agrees."""

    CASES = (
        ("42", "42"),
        ("https://github.com/o/r/pull/42", "42"),
        ("https://github.com/o/r/pull/42/", None),
        ("", None),
        (None, None),
    )

    def test_every_case_normalises_as_documented(self):
        for value, want in self.CASES:
            with self.subTest(value=value):
                self.assertEqual(_pr_number(value), want)


if __name__ == "__main__":
    unittest.main()
