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


# --------------------------------------------------------------------------- #
# `okf-legacy-*` — pre-rename layout debt (renomear-docs-para-knowledge, task 2.2)
#
# Each detector checks exactly one site; a fixture proves it fires on the old name and
# stays silent once that one site is renamed, without the other three sites in play.
# --------------------------------------------------------------------------- #
class LegacyRootDetector(unittest.TestCase):
    def test_fires_when_new_root_absent_and_old_root_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, ".docs"))
            findings = validate_tree(os.path.join(tmp, ".knowledge"))
        codes = {code for sev, rel, code, msg in findings}
        self.assertEqual(codes, {"okf-legacy-root"})

    def test_no_bundle_survives_when_neither_root_exists(self):
        # Regression guard on the branch this task edited: a target with no bundle at
        # all — migrated or not — must still get the original finding, not a silent drop.
        with tempfile.TemporaryDirectory() as tmp:
            findings = validate_tree(os.path.join(tmp, ".knowledge"))
        codes = {code for sev, rel, code, msg in findings}
        self.assertEqual(codes, {"no-bundle"})


class LegacyHomeDetector(unittest.TestCase):
    def test_fires_on_both_pre_rename_homes(self):
        fixture = {
            "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n',
            "knowledge/index.md": "# Knowledge\n",
            "reference/index.md": "# Reference\n",
        }
        findings = _validated(fixture)
        legacy = {(rel, code) for sev, rel, code, msg in findings if code == "okf-legacy-home"}
        self.assertEqual(legacy, {("knowledge/", "okf-legacy-home"), ("reference/", "okf-legacy-home")})

    def test_silent_once_renamed(self):
        fixture = {
            "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n',
            "concepts/index.md": "# Concepts\n",
            "external/index.md": "# External\n",
        }
        findings = _validated(fixture)
        codes = {code for sev, rel, code, msg in findings}
        self.assertNotIn("okf-legacy-home", codes)


class LegacyDocQuadrantDetector(unittest.TestCase):
    def test_fires_on_both_pre_rename_quadrants(self):
        fixture = {
            "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n',
            "documentation/getting-started/index.md": "# Getting started\n",
            "documentation/concepts/index.md": "# Concepts\n",
        }
        findings = _validated(fixture)
        legacy = {rel for sev, rel, code, msg in findings if code == "okf-legacy-doc-quadrant"}
        self.assertEqual(legacy, {"documentation/getting-started/", "documentation/concepts/"})

    def test_silent_once_renamed(self):
        fixture = {
            "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n',
            "documentation/tutorials/index.md": "# Tutorials\n",
            "documentation/explanation/index.md": "# Explanation\n",
        }
        findings = _validated(fixture)
        codes = {code for sev, rel, code, msg in findings}
        self.assertNotIn("okf-legacy-doc-quadrant", codes)


class LegacyGlossaryDetector(unittest.TestCase):
    def test_fires_only_on_the_nested_copy(self):
        fixture = {
            "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n',
            "glossary.md": "# Glossary\n\n- [Term](standards/term.md)\n",
            "concepts/glossary.md": "# Glossary\n",
        }
        findings = _validated(fixture)
        legacy = {rel for sev, rel, code, msg in findings if code == "okf-legacy-glossary"}
        self.assertEqual(legacy, {"concepts/glossary.md"})

    def test_silent_when_only_the_root_copy_exists(self):
        fixture = {
            "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n',
            "glossary.md": "# Glossary\n",
        }
        findings = _validated(fixture)
        codes = {code for sev, rel, code, msg in findings}
        self.assertNotIn("okf-legacy-glossary", codes)


# --------------------------------------------------------------------------- #
# `generated-listing-missing` / `generated-listing-drift` — the GENERATED zone of
# `standards/index.md` against the docs on disk (validar-a-zona-generated-contra-o-disco)
#
# Both directions are proved, because a check with only the positive arm cannot be told apart
# from one that fires on everything. The two arms are the SAME bundle — identical file set,
# identical prose — differing only inside the zone, so the control below can assert that every
# OTHER finding is identical between them: a fixture that drifted into firing for an unrelated
# reason fails that assertion even while the positive arm still passes.
# --------------------------------------------------------------------------- #
_ZONE_MOLD = ("<!-- BEGIN GENERATED: rebuilt from disk — DO NOT edit by hand.\n"
              "     Row model per subfolder:\n"
              "       | [imports.md](code/imports.md) | <the doc's description:> |\n"
              "-->\n")

_ROWS = {
    "imports.md": "| [imports.md](code/imports.md) | {} |",
    # Written WITHOUT the closing pipe, which GFM makes optional and this bundle's own zone
    # already does. A parser that requires it drops the row and reports the doc it lists as
    # unlisted — the one false positive a membership check cannot afford.
    "exports.md": "| [exports.md](code/exports.md) | How we export",
}


def _standard(title: str, description: str) -> str:
    return f"---\ntype: standard\ntitle: {title}\ndescription: {description}\n---\n\n# {title}\n"


def _generated_fixture(listed: tuple[str, ...], imports_row: str) -> dict:
    """The same four-doc bundle every time; only the zone's rows move.

    `exports.md` is linked from `standards/code/index.md` in BOTH arms, so dropping its row
    from the zone never makes it an `index-orphan` — that is the measured case this check
    exists for (`architecture/bundle-root.md`, cited by four siblings and absent from the
    listing, with the validator green throughout).
    """
    table = "\n".join(_ROWS[name].format(imports_row) for name in listed)
    return {
        "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n\n- [Standards](standards/index.md)\n',
        "standards/index.md": ("# Standards\n\n## Current docs\n\n" + _ZONE_MOLD +
                               "\n### code/\n\n| Doc | Covers |\n| --- | --- |\n" + table +
                               "\n\n<!-- END GENERATED -->\n"),
        "standards/code/index.md": "# code/\n\n- [imports.md](imports.md)\n- [exports.md](exports.md)\n",
        "standards/code/imports.md": _standard("Imports", "How we import"),
        "standards/code/exports.md": _standard("Exports", "How we export"),
    }


CONFORMANT_ZONE = _generated_fixture(("imports.md", "exports.md"), "How we import")
STALE_ZONE = _generated_fixture(("imports.md",), "How we imported, once")


class GeneratedListingChecker(unittest.TestCase):
    """The zone against disk — fires on a stale copy, silent on a conformant one."""

    @classmethod
    def setUpClass(cls):
        cls.stale = _validated(STALE_ZONE)
        cls.clean = _validated(CONFORMANT_ZONE)

    @staticmethod
    def _new_codes(findings):
        return {(rel, code, msg) for sev, rel, code, msg in findings
                if code.startswith("generated-listing")}

    def test_a_doc_the_zone_does_not_link_is_reported_against_the_listing(self):
        missing = [(rel, msg) for rel, code, msg in self._new_codes(self.stale)
                   if code == "generated-listing-missing"]
        self.assertEqual(len(missing), 1, missing)
        rel, msg = missing[0]
        self.assertEqual(rel, "standards/index.md")   # the file the fix is made in
        self.assertIn("standards/code/exports.md", msg)

    def test_that_doc_is_not_an_orphan_which_is_why_index_orphan_never_saw_it(self):
        orphans = {rel for sev, rel, code, msg in self.stale if code == "index-orphan"}
        self.assertEqual(orphans, set())

    def test_a_row_whose_description_no_longer_matches_the_doc_is_reported(self):
        drift = [(rel, msg) for rel, code, msg in self._new_codes(self.stale)
                 if code == "generated-listing-drift"]
        self.assertEqual(len(drift), 1, drift)
        rel, msg = drift[0]
        self.assertEqual(rel, "standards/index.md")
        self.assertIn("standards/code/imports.md", msg)

    def test_a_conformant_zone_says_nothing(self):
        self.assertEqual(self._new_codes(self.clean), set())

    def test_the_two_arms_differ_by_the_new_codes_and_by_nothing_else(self):
        # The control. Without it the positive arm cannot distinguish "the check fired" from
        # "the stale fixture broke in some unrelated way and the check fired on the wreckage".
        def rest(findings):
            return sorted(f for f in findings if not f[2].startswith("generated-listing"))
        self.assertEqual(rest(self.stale), rest(self.clean))

    def test_the_row_mold_inside_the_opening_comment_is_never_read_as_a_row(self):
        # The mold links `code/imports.md` for real. Counted as a row, it would vouch for a doc
        # the zone does not actually list — and the drift check would compare against the mold's
        # `<the doc's description:>` slot.
        findings = _validated(_generated_fixture((), ""))
        missing = {msg for sev, rel, code, msg in findings
                   if code == "generated-listing-missing"}
        self.assertEqual(len(missing), 2, missing)
        self.assertTrue(any("standards/code/imports.md" in m for m in missing), missing)

    def test_whitespace_around_a_cell_is_not_drift(self):
        fixture = _generated_fixture(("imports.md",), "How we import   ")
        drift = {code for sev, rel, code, msg in _validated(fixture)
                 if code == "generated-listing-drift"}
        self.assertEqual(drift, set())


if __name__ == "__main__":
    unittest.main()
