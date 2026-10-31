"""OKF v0.2 — the optional families the validator reads, and the v0.1 fallbacks it keeps.

The spec moved provenance, trust and lifecycle into frontmatter (§5), superseded `timestamp`
with `generated.at`, and added the `Attested Computation` type (§10). None of that is required
for conformance, so the cases below are about two things only:

1. **A present family is shaped right** — a malformed `generated`, `verified`, `status`,
   `stale_after` or `sources` is reported, and a well-formed one is silent.
2. **A v0.1 bundle stays consumable** — a legacy `timestamp` still satisfies the recency
   recommendation, and `generated: true` (this plugin's projection marker) is not read as the
   v0.2 family.
"""

import pathlib
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.knowledge.cli import _density
from quenching.knowledge.schema import recency
from quenching.knowledge.validate import validate_tree


def _bundle(files: dict, version: str = "0.2") -> list[tuple[str, str, str, str]]:
    with tempfile.TemporaryDirectory() as tmp:
        pathlib.Path(tmp, "index.md").write_text(
            f'---\nokf_version: "{version}"\n---\n\n# Bundle\n\n- [a](a.md)\n',
            encoding="utf-8",
        )
        for name, text in files.items():
            pathlib.Path(tmp, name).write_text(text, encoding="utf-8")
        return validate_tree(tmp)


def _codes(findings) -> set[str]:
    return {code for _sev, _rel, code, _msg in findings}


def _doc(frontmatter: str) -> str:
    return (
        "---\n"
        "type: Metric\n"
        "title: Revenue\n"
        "description: Recognized revenue.\n"
        "resource: x\n"
        f"{frontmatter}\n"
        "---\n\n# Definition\n\nBody.\n"
    )


class RootVersion(unittest.TestCase):
    VERSION_CODES = {"root-no-okf-version", "root-okf-version-mismatch", "root-extra-keys"}

    def test_a_v02_root_is_read_without_a_version_finding(self):
        self.assertEqual(_codes(_bundle({}, version="0.2")) & self.VERSION_CODES, set())

    def test_a_v01_root_stays_readable(self):
        self.assertEqual(_codes(_bundle({}, version="0.1")) & self.VERSION_CODES, set())

    def test_an_unknown_version_is_a_mismatch(self):
        codes = _codes(_bundle({}, version="0.3"))
        self.assertIn("root-okf-version-mismatch", codes)


class Recency(unittest.TestCase):
    def test_generated_satisfies_the_recommendation(self):
        codes = _codes(_bundle({"a.md": _doc(
            "generated: { by: human:analyst, at: 2026-06-20T22:53:05Z }")}))
        self.assertNotIn("missing-generated", codes)

    def test_a_legacy_timestamp_is_accepted_silently(self):
        codes = _codes(_bundle({"a.md": _doc("timestamp: 2026-06-20")}))
        self.assertNotIn("missing-generated", codes)
        self.assertNotIn("missing-timestamp", codes)

    def test_neither_field_warns(self):
        self.assertIn("missing-generated", _codes(_bundle({"a.md": _doc("")})))

    def test_recency_prefers_generated_at_and_falls_back_to_timestamp(self):
        self.assertEqual(
            recency({"generated": {"by": "human:a", "at": "2026-06-20T22:53:05Z"},
                     "timestamp": "2020-01-01"}),
            "2026-06-20T22:53:05Z",
        )
        self.assertEqual(recency({"timestamp": "2020-01-01"}), "2020-01-01")
        self.assertIsNone(recency({"generated": "true"}))

    def test_status_figures_read_generated_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            pathlib.Path(tmp, "docs").mkdir()
            pathlib.Path(tmp, "docs", "index.md").write_text(
                '---\nokf_version: "0.2"\n---\n', encoding="utf-8")
            pathlib.Path(tmp, "docs", "a.md").write_text(_doc(
                "generated: { by: human:a, at: 2026-06-20T22:53:05Z }"), encoding="utf-8")
            self.assertEqual(_density(str(pathlib.Path(tmp, "docs")))["lastActivity"],
                             "2026-06-20T22:53:05Z")


class GeneratedFamily(unittest.TestCase):
    def test_a_well_formed_generated_family_is_silent(self):
        codes = _codes(_bundle({"a.md": _doc(
            "generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }")}))
        self.assertEqual(codes, set())

    def test_generated_needs_an_actor_and_an_offset(self):
        codes = _codes(_bundle({"a.md": _doc("generated: { by: nobody, at: 2026-06-20 }")}))
        self.assertIn("generated-by-invalid", codes)
        self.assertIn("generated-at-invalid", codes)

    def test_generated_without_by_warns(self):
        self.assertIn("generated-malformed",
                      _codes(_bundle({"a.md": _doc("generated: { at: 2026-06-20T22:53:05Z }")})))

    def test_a_boolean_marker_is_not_the_v02_family(self):
        # `generated: true` is the plugin's own projection marker; the v0.2 family is a mapping.
        self.assertNotIn("generated-malformed", _codes(_bundle({"a.md": _doc("generated: true")})))


class VerifiedFamily(unittest.TestCase):
    def test_a_bare_mapping_is_one_event(self):
        codes = _codes(_bundle({"a.md": _doc(
            "generated: { by: human:a, at: 2026-06-20T22:53:05Z }\n"
            "verified: { by: human:reviewer, at: 2026-06-25T09:00:00Z }")}))
        self.assertEqual(codes, set())

    def test_a_block_list_of_events_is_read(self):
        codes = _codes(_bundle({"a.md": _doc(
            "generated: { by: human:a, at: 2026-06-20T22:53:05Z }\n"
            "verified:\n"
            "  - { by: human:reviewer, at: 2026-06-25T09:00:00Z }\n"
            "  - { by: process:nightly, at: 2026-06-26T02:00:00Z }")}))
        self.assertEqual(codes, set())

    def test_an_event_without_a_human_or_process_actor_warns(self):
        codes = _codes(_bundle({"a.md": _doc(
            "generated: { by: human:a, at: 2026-06-20T22:53:05Z }\n"
            "verified: { by: reviewer, at: 2026-06-25T09:00:00Z }")}))
        self.assertIn("verified-by-invalid", codes)


class LifecycleFamily(unittest.TestCase):
    def test_a_known_status_and_a_datetime_are_silent(self):
        codes = _codes(_bundle({"a.md": _doc(
            "generated: { by: human:a, at: 2026-06-20T22:53:05Z }\n"
            "status: deprecated\nstale_after: 2026-09-23T00:00:00Z")}))
        self.assertEqual(codes, set())

    def test_an_unknown_status_and_a_loose_date_warn(self):
        codes = _codes(_bundle({"a.md": _doc(
            "generated: { by: human:a, at: 2026-06-20T22:53:05Z }\n"
            "status: live\nstale_after: 2026-09-23")}))
        self.assertIn("status-invalid", codes)
        self.assertIn("stale-after-invalid", codes)


class SourcesFamily(unittest.TestCase):
    def test_a_block_sequence_of_sources_is_read(self):
        codes = _codes(_bundle({"a.md": _doc(
            "generated: { by: human:a, at: 2026-06-20T22:53:05Z }\n"
            "sources:\n"
            "  - id: rev-policy\n"
            "    resource: https://wiki.acme/finance/revenue-recognition\n"
            "    title: Revenue recognition policy\n"
            "    last_modified: 2026-04-02T00:00:00Z\n"
            "  - id: exec-dash\n"
            "    resource: dashboards/exec-revenue\n"
            "usage_window: { from: 2026-06-01T00:00:00Z, to: 2026-06-30T00:00:00Z }")}))
        self.assertEqual(codes, set())

    def test_a_source_without_a_resource_and_a_repeated_id_warn(self):
        codes = _codes(_bundle({"a.md": _doc(
            "generated: { by: human:a, at: 2026-06-20T22:53:05Z }\n"
            "sources:\n"
            "  - id: same\n"
            "  - id: same\n"
            "    resource: x")}))
        self.assertIn("source-missing-resource", codes)
        self.assertIn("source-id-duplicate", codes)

    def test_a_usage_window_needs_both_ends(self):
        self.assertIn("usage-window-invalid", _codes(_bundle({"a.md": _doc(
            "generated: { by: human:a, at: 2026-06-20T22:53:05Z }\n"
            "usage_window: { from: 2026-06-01T00:00:00Z }")})))


class AttestedComputation(unittest.TestCase):
    def _doc(self, body: str) -> str:
        return ("---\n"
                "type: Attested Computation\n"
                "title: Revenue\n"
                "description: Recognized revenue.\n"
                f"{body}\n"
                "---\n\n# Computation\n\n    SELECT 1\n")

    def test_runtime_is_required_for_the_type(self):
        self.assertIn("attested-computation-no-runtime",
                      _codes(_bundle({"a.md": self._doc(
                          "generated: { by: human:a, at: 2026-06-20T22:53:05Z }")})))

    def test_a_complete_contract_is_silent(self):
        codes = _codes(_bundle({"a.md": self._doc(
            "runtime: bigquery\n"
            "parameters:\n"
            "  - { name: year, type: integer, required: true }\n"
            "executor:\n"
            "  resource: references/skills/run-on-bq.md\n"
            "  receipt: [job_id, executed_sql, result]\n"
            "attester:\n"
            "  resource: references/attesters/revenue.py\n"
            "generated: { by: human:a, at: 2026-06-20T22:53:05Z }")}))
        self.assertEqual(codes, set())


if __name__ == "__main__":
    unittest.main()
