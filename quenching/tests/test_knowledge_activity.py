"""Resource activity is a figure, and `stale-doc` stays retired.

The check compared a doc's `timestamp` against the last commit touching its `resource:` and called
the difference staleness. The comparison is honest; the verdict built on it was not. A `resource:`
glob is deliberately wide, so what it detects is activity in the radius of the glob — a doc correct
about a stable rule gets reported as possibly wrong whenever anything near it moves. Measured on
this repo the day it was retired: **50 of 95 docs**, which is a signal nobody reads.

Three rules, and each has a case here that fails without it:

1. **Nothing emits `stale-doc`.** Retirement is a property of the output, not of a deleted
   function — the measurement stayed and only the finding went.
2. **The measurement is per `resource:` entry.** It used to collapse into one `git log` over the
   union of every pathspec, so the widest glob always won and no reader could tell which entry
   moved.
3. **An unmeasurable scope is reported as unmeasurable.** Every entry a `uri`, an `unknown` or a
   bundle aggregate leaves nothing to ask git about, and returning empty made that doc
   indistinguishable from one measured and found quiet.

MUTATION PASS (2026-08-27, three mutations, each applied, run, observed, reverted), per
`docs/standards/quality/selftest-mutation.md`, in both modes — this suite, and the human
`cq knowledge validate docs` / `--activity` arms over the real bundle:

| Mutation | Rule | This suite | Human arm |
| --- | --- | --- | --- |
| re-emit the WARN from `_validate_text` | 1 | 1 failure | 50 `stale-doc` warnings return |
| measure every entry in one `git log` | 2 | 1 failure | unchanged — the collapse is invisible in the count |
| return `None` instead of `scopeMeasured: False` | 3 | 2 failures | 3 rows vanish from the figure |

**Rule 2's human column is the one worth reading.** Collapsing the measurement changes no count
anywhere: the figure prints the same number of lines, with the same docs, and every entry of a doc
simply answers with the widest glob's date. Nothing in the human arm can see it, which is why this
fixture is its only witness.

The fixture is a real git checkout built in a tmpdir, not a mock: the measurement's whole content
is what `git log` answers, and a fake would be asserting on the stub.
"""

import os
import pathlib
import subprocess
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.knowledge.render import _render_activity
from quenching.knowledge.stale import resource_activity
from quenching.knowledge.validate import validate_tree

DOC = """\
---
type: standard
title: Governed
description: A doc whose resource names one file and one glob
resource: {resource}
tags: [test]
timestamp: {timestamp}
audience: both
authority: current
source: fixture
maintainer: quenching
---

# Governed

Body.
"""


def git(cwd, *args, when=None):
    """`when` sets the COMMITTER date, which is what the measurement reads.

    `git commit --date` sets the AUTHOR date alone, and `_git_last_commit_date` asks for `%cI`.
    A fixture that only passed `--date` produced two commits stamped today, both entries
    answering with the same value — the exact collapse rule 2 exists to catch, hidden by the
    fixture rather than by the code."""
    env = dict(os.environ)
    if when:
        env["GIT_COMMITTER_DATE"] = when
        env["GIT_AUTHOR_DATE"] = when
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env)


class ActivityFixture(unittest.TestCase):
    """One tmpdir checkout: a bundle, a governed file, and two commits a day apart."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(cls._tmp.name)
        cls.bundle = root / "docs"
        (cls.bundle / "standards").mkdir(parents=True)
        (root / "src").mkdir()
        (root / "src" / "one.py").write_text("x = 1\n")
        (cls.bundle / "index.md").write_text('---\nokf_version: "0.1"\n---\n\n# Bundle\n')

        git(root, "init", "-q")
        git(root, "config", "user.email", "fixture@example.invalid")
        git(root, "config", "user.name", "Fixture")
        git(root, "add", "-A")
        git(root, "-c", "commit.gpgsign=false", "commit", "-qm", "seed",
            when="2026-01-01T00:00:00+00:00")

        # A second commit touching ONLY the glob's tree, so the two entries answer differently —
        # which is the whole point of measuring per entry.
        (root / "src" / "two.py").write_text("y = 2\n")
        git(root, "add", "-A")
        git(root, "-c", "commit.gpgsign=false", "commit", "-qm", "later",
            when="2026-06-01T00:00:00+00:00")
        cls.root = root

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def write(self, name, resource, timestamp="2026-01-01"):
        path = self.bundle / "standards" / name
        path.write_text(DOC.format(resource=resource, timestamp=timestamp))
        return path

    def test_nothing_emits_stale_doc(self):
        """Rule 1. Kills: re-emit the WARN from `_validate_text`."""
        self.write("governed.md", "src/one.py, src/**", timestamp="2026-01-01")
        findings = validate_tree(str(self.bundle))
        self.assertEqual([f for f in findings if f[2] == "stale-doc"], [],
                         "`stale-doc` is retired — the measurement stayed, the verdict did not")

    def test_each_resource_entry_is_measured_on_its_own(self):
        """Rule 2. Kills: measure every entry in one `git log`.

        `src/one.py` was last touched by the seed commit; `src/**` by the later one. Collapsed
        into a single pathspec both would answer with the newer date, and the reader could not
        tell which entry moved."""
        text = self.write("governed.md", "src/one.py, src/**").read_text()
        activity = resource_activity(text, str(self.bundle))
        self.assertTrue(activity["scopeMeasured"])
        by_entry = {e["entry"]: e for e in activity["entries"]}
        self.assertEqual(sorted(by_entry), ["src/**", "src/one.py"])
        self.assertNotEqual(by_entry["src/one.py"]["lastCommit"], by_entry["src/**"]["lastCommit"],
                            "the two entries collapsed into one answer")
        self.assertLess(by_entry["src/one.py"]["days"], by_entry["src/**"]["days"])

    def test_an_unmeasurable_scope_says_so(self):
        """Rule 3. Kills: return `{}` instead of `scopeMeasured: False`."""
        text = self.write("external.md", "https://example.invalid/spec").read_text()
        activity = resource_activity(text, str(self.bundle))
        self.assertIsNotNone(activity, "a doc with an unmeasurable scope is still a row")
        self.assertFalse(activity["scopeMeasured"])
        self.assertEqual(activity["entries"], [])

    def test_the_unmeasurable_doc_is_printed_rather_than_dropped(self):
        """Rule 3, in the arm a human reads: a silent omission looks like a quiet doc."""
        text = self.write("external.md", "https://example.invalid/spec").read_text()
        rendered = _render_activity([("standards/external.md", resource_activity(
            text, str(self.bundle)))], str(self.bundle))
        self.assertIn("scope not measured", rendered)

    def test_the_figure_carries_no_finding_code(self):
        """The contract of the whole change: the numbers are published, the verdict is not."""
        text = self.write("governed.md", "src/one.py, src/**").read_text()
        rendered = _render_activity([("standards/governed.md", resource_activity(
            text, str(self.bundle)))], str(self.bundle))
        self.assertNotIn("stale-doc", rendered)
        self.assertNotIn("WARN", rendered)
        self.assertIn("figure, not a verdict", rendered)


class NotAGitCheckout(unittest.TestCase):
    def test_a_tree_with_no_history_measures_nothing_and_says_nothing(self):
        """No git facts is not the same as a quiet scope, and it is not a finding either — the
        one case that returns None rather than a row."""
        with tempfile.TemporaryDirectory() as tmp:
            bundle = pathlib.Path(tmp) / "docs"
            bundle.mkdir(parents=True)
            text = DOC.format(resource="src/one.py", timestamp="2026-01-01")
            self.assertIsNone(resource_activity(text, str(bundle)))


if __name__ == "__main__":
    unittest.main()
