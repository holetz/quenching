"""Locks the corpus sweep on a rename, the doc vocabulary rule and the flow sweep (text contract)."""
from __future__ import annotations

import pathlib
import unittest

CONCLUDE = (pathlib.Path(__file__).resolve().parent.parent / "skills" / "quenching-specs" / "references" / "conclude.md").read_text()


def step(number: int) -> str:
    """The flow's step `number`, on one line, so assertions never depend on the wrap."""
    start = CONCLUDE.index(f"### {number}. ")
    try:
        end = CONCLUDE.index(f"### {number + 1}. ", start)
    except ValueError:
        end = len(CONCLUDE)
    return " ".join(CONCLUDE[start:end].split())


class ConcludeRenameSweepsTheCorpus(unittest.TestCase):
    def test_step_two_widens_the_read_from_the_diff_to_the_corpus(self):
        text = step(2)
        self.assertIn("A rename widens the read from the diff to the corpus", text)
        self.assertIn("`/docs/` included", text)
        self.assertIn("A grep scoped to the folders the diff touched is not proof", text)

    def test_step_three_takes_the_names_from_the_branch_not_the_spec(self):
        text = step(3)
        self.assertIn("The names it writes are the branch's, not the spec's", text)
        self.assertIn("never copied from the spec's own prose", text)


class ConcludeFlowSweep(unittest.TestCase):
    def test_the_sweep_is_its_own_step_before_the_gate(self):
        self.assertIn("### 6. Sweep the flow itself", CONCLUDE)
        self.assertIn("### 7. Prove the gate green", CONCLUDE)
        self.assertIn("step 6\nwrites only the spec store", CONCLUDE)

    def test_the_candidate_needs_evidence_and_never_judges_the_change(self):
        text = step(6)
        self.assertIn("how the work was carried", text)
        self.assertIn("Zero is the normal result", text)
        self.assertIn("**Insumos**", text)
        self.assertIn("Never develop the captured spec", text)
        self.assertIn("quenching checkout", text)
        self.assertIn("cq deploy", text)

    def test_the_sweep_reports_through_the_report_block(self):
        self.assertIn("what the sweep captured in step 6", step(8))

    def test_the_invariants_keep_the_sweep_out_of_the_delivered_change(self):
        invariants = CONCLUDE[CONCLUDE.index("## Invariants to never violate"):]
        self.assertIn("Never develop a swept candidate in the run that found it", invariants)
        self.assertIn("Never let the sweep judge the delivered change", invariants)


if __name__ == "__main__":
    unittest.main()
