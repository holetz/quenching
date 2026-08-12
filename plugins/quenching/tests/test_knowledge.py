"""Two retirement fixtures from the pre-refactor OKF validator script's `run_selftest`: proof
that a checker DROPPED cleanly, not partially.

Both prove a NEGATIVE — "this used to fire, and must not anymore" — which a plain absence-of-
error test cannot distinguish from "the fixture stopped exercising the code path at all". Each
fixture is therefore run against a bundle the retired behaviour used to judge, with a second
assertion that the rest of that same bundle stays clean — a fixture that drifted quiet for the
wrong reason must not pass either.

The canonical frontmatter cases (`CANONICAL_CASES`/`canonical_case_failures`) are NOT here —
they moved to `test_frontmatter.py` with the parser they prove, per that module's docstring.
"""
import os
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.knowledge.hook import hard_block_exempt
from quenching.knowledge.schema import RESERVED
from quenching.knowledge.validate import validate_tree


def _validated(fixture: dict) -> list[tuple[str, str, str, str]]:
    with tempfile.TemporaryDirectory() as tmp:
        for relpath, text in fixture.items():
            path = os.path.join(tmp, *relpath.split("/"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pathlib.Path(path).write_text(text, encoding="utf-8")
        return validate_tree(tmp)


# --------------------------------------------------------------------------- #
# the retired `log.md` checker — `log.md` lost its checker, never its reservation
#
# With `check_log` gone, nothing else in the pillar would notice if `log.md` also fell out of
# `RESERVED` or out of the hard gate's skip list, and the damage would not announce itself:
# every log surviving in an already-aligned bundle would quietly start reporting `missing-type`
# at ERROR and, under `hardBlock`, become unwritable. So the fixture validates a real bundle
# holding the worst log this tool ever accepted — a `type` in its frontmatter, date headings in
# ascending order, the three things the retired codes used to fire on — and demands silence
# about it.
# --------------------------------------------------------------------------- #
RETIRED_LOG_FIXTURE = {
    # Both shapes a surviving log actually takes, because they fail differently: the typed one
    # is what `log-has-type` used to catch, and the bare one falls to `missing-type` at ERROR —
    # the failure the retiring spec named — if the dispatch branch is ever brought back.
    "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n\n- [Log](log.md)\n'
                "- [Standards](standards/index.md)\n",
    "log.md": ("---\ntype: standard\n---\n\n"
               "## 2026-01-01\n\n- typed, and oldest first\n\n"
               "## 2026-07-28\n\n- newest last\n"),
    "standards/index.md": "# Standards\n\n- [Log](log.md)\n",
    "standards/log.md": "# Log\n\n- an entry under no date heading at all\n",
}


class RetiredLogChecker(unittest.TestCase):
    """Prove the retirement in all three places it has to hold at once."""

    @classmethod
    def setUpClass(cls):
        cls.findings = _validated(RETIRED_LOG_FIXTURE)

    def test_a_populated_log_md_is_judged_by_nothing(self):
        judged = sorted(f"{rel}:{sev}/{code}" for sev, rel, code, msg in self.findings
                        if os.path.basename(rel) == "log.md")
        self.assertEqual(judged, [])

    def test_the_rest_of_the_fixture_is_otherwise_clean(self):
        # A drifted fixture could go silent on `log.md` for the wrong reason (e.g. the whole
        # bundle failing to parse) and still pass the assertion above — this is the control.
        rest = sorted(f"{rel}:{code}" for sev, rel, code, msg in self.findings
                      if os.path.basename(rel) != "log.md")
        self.assertEqual(rest, [])

    def test_log_md_stays_reserved_so_a_surviving_log_is_never_read_as_a_concept_doc(self):
        self.assertIn("log.md", RESERVED)

    def test_log_md_stays_exempt_from_the_pretooluse_hard_gate(self):
        self.assertTrue(hard_block_exempt("log.md"))


# --------------------------------------------------------------------------- #
# the retired `--listing-root` mode
#
# `plans/index.md` was retired whole, and with it the only caller of the mode that scanned a
# non-bundle tree. The mode's failure is the mirror of the log's: re-adding it is a one-line
# change nothing else complains about, and the tree it used to skip would go silently
# unjudged again. So the fixture is a tree the OLD mode validated CLEAN — a spec beside a
# plain listing — and demands the checker judge it now, because a bundle is the only thing
# this pillar validates.
# --------------------------------------------------------------------------- #
RETIRED_LISTING_ROOT_FIXTURE = {
    "index.md": "# Plans\n\n- [a spec](2026-07-28-a-spec.md)\n",
    "2026-07-28-a-spec.md": ("---\nslug: a-spec\ntitle: A spec\n"
                             "verification: per-section\n---\n\n# A spec\n"),
}


class RetiredListingRootMode(unittest.TestCase):
    """Prove the mode is gone, and that retiring it did not touch the reservation."""

    def test_a_spec_shaped_file_outside_the_bundle_is_judged_not_skipped(self):
        findings = _validated(RETIRED_LISTING_ROOT_FIXTURE)
        codes = {code for sev, rel, code, msg in findings if rel == "2026-07-28-a-spec.md"}
        self.assertIn("missing-type", codes)

    def test_validate_tree_takes_no_listing_root_parameter(self):
        # The parameter is the mode; a caller cannot reach a mode the signature cannot express.
        params = validate_tree.__code__.co_varnames[:validate_tree.__code__.co_argcount]
        self.assertNotIn("listing_root", params)

    def test_index_md_stays_reserved_retiring_a_mode_is_never_unreserving_a_name(self):
        self.assertIn("index.md", RESERVED)

    def test_index_md_does_not_enter_the_pretooluse_hard_gate_exemption(self):
        # `log.md` is exempt because a retired artifact is judged by nothing; `index.md` is
        # still PRODUCED by the bundle, and denying a typed one is the hard gate's whole job.
        # Exempting it here is the mutation this asserts against.
        self.assertFalse(hard_block_exempt("index.md"))


if __name__ == "__main__":
    unittest.main()
