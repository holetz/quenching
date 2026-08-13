"""`_work_ref` — which ref `cq specs next` treats as a spec's work branch, and the one shape
that is NOT one: the in-place record `execute` stamps with `work` equal to `base`.

That pair is the whole reason this suite exists. The base branch is always alive, so a
consumer reading it as a live work ref ranks every spec built in place as permanently in
flight — `live` and `current` both true forever, on a ref it never took. `git.md` §Where a
branch comes from owns the rule; `test_specs_find.py` asserts the sibling guard in
`find_match`.
"""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.commands.next import _work_ref


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


if __name__ == "__main__":
    unittest.main()
