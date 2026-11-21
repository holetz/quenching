"""`cq specs parallel` compares `files:` as repository paths: two spellings of one path clash,
two distinct paths never do, and a path it cannot place in the repository fails closed."""
from __future__ import annotations

import pathlib
import sys
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.specs.commands.parallel import _overlaps
from test_specs_operational import Workspace


def group(a: str, b: str) -> str:
    return ("### 1. One\n\n"
            f"- [ ] 1.1 [P] Alpha\n      files: {a}\n"
            f"- [ ] 1.2 [P] Beta\n      files: {b}\n")


class Overlaps(unittest.TestCase):
    def test_a_dot_directory_is_not_its_dotless_twin(self):
        self.assertFalse(_overlaps(".github/x", "github/x"))

    def test_spellings_of_one_path_overlap(self):
        self.assertTrue(_overlaps("a.py", "src/../a.py"))
        self.assertTrue(_overlaps("./a.py (new)", "a.py"))

    def test_a_directory_covers_its_children_by_segment(self):
        self.assertTrue(_overlaps("src/", "src/a.py"))
        self.assertFalse(_overlaps("src/a", "src/ab.py"))

    def test_the_root_and_the_outside_fail_closed(self):
        self.assertTrue(_overlaps(".", "src/a.py"))
        self.assertTrue(_overlaps("./", "b.py"))
        self.assertTrue(_overlaps("../x", "src/a.py"))
        self.assertTrue(_overlaps("src/a.py", "a/../../x"))


class Parallel(Workspace):
    def test_a_relative_climb_to_the_same_file_is_a_clash(self):
        code, payload = self.parallel(self.write(group("a.py", "src/../a.py")))
        self.assertEqual(code, 1)
        self.assertFalse(payload["groups"][0]["eligible"])
        self.assertEqual(payload["groups"][0]["clashes"],
                         [{"a": "1.1", "b": "1.2", "file": "a.py"}])

    def test_dot_github_and_github_stay_disjoint(self):
        code, payload = self.parallel(self.write(group(".github/x.yml", "github/x.yml")))
        self.assertEqual(code, 0)
        self.assertTrue(payload["groups"][0]["eligible"])

    def test_the_reported_file_keeps_its_leading_dot(self):
        code, payload = self.parallel(self.write(group(".github/x.yml", "./.github/x.yml")))
        self.assertEqual(code, 1)
        self.assertEqual(payload["groups"][0]["clashes"][0]["file"], ".github/x.yml")

    def test_a_path_outside_the_repository_is_never_eligible(self):
        code, payload = self.parallel(self.write(group("../x.py", "src/a.py")))
        self.assertEqual(code, 1)
        self.assertEqual(payload["groups"][0]["clashes"][0]["file"], "../x.py")


if __name__ == "__main__":
    unittest.main()
