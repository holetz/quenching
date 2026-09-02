"""Structural proof for the shared local-front mold."""
from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
DOC = ROOT / "docs" / "standards" / "architecture" / "front-mold.md"
COMMANDS = ROOT / "plugins" / "quenching" / "commands"
SOURCE_REFS = ROOT / "plugins" / "quenching" / "assets" / "references"
CODEX = ROOT / "plugins" / "quenching-codex"
TESTS = ROOT / "plugins" / "quenching" / "tests"


def front_footprint(front: str) -> list[pathlib.Path]:
    """Return the measured mold footprint, excluding front-specific creation commands."""
    paths = [
        ROOT / "docs" / "standards" / "architecture" / f"{front}-front.md",
        COMMANDS / front / "align.md",
        COMMANDS / front / "status.md",
        *sorted((SOURCE_REFS / f"{front}-align").glob("*.md")),
        CODEX / "skills" / f"quenching-{front}-align" / "SKILL.md",
        CODEX / "skills" / f"quenching-{front}-status" / "SKILL.md",
        *sorted((CODEX / "references" / f"{front}-align").glob("*.md")),
        TESTS / f"test_{front}.py",
        *sorted((TESTS / "fixtures" / "golden").glob(f"{front}-*.json")),
    ]
    return [path for path in paths if path.is_file()]


class FrontMoldContract(unittest.TestCase):
    def setUp(self):
        self.document = DOC.read_text(encoding="utf-8")

    def test_common_minimum_has_one_binding_host_and_the_route_floor(self):
        required_sections = (
            "## One binding host",
            "## The common minimum",
            "## Route floor",
            "## Applicability and ownership",
            "## Disposition bands",
            "## Measured baseline and footprint",
            "## Explicit front deltas",
        )
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, self.document)

        minimum = self.document.split("## The common minimum", 1)[1].split(
            "## Route floor", 1
        )[0]
        for term in (
            "owned tree",
            "boundary",
            "configuration home",
            "applicability",
            "read model",
            "verifier",
            "align",
            "status",
            "finding ownership",
        ):
            with self.subTest(term=term):
                self.assertIn(term, minimum)

        route = self.document.split("## Route floor", 1)[1].split(
            "## Applicability and ownership", 1
        )[0]
        for term in (
            "--help",
            "--json",
            "doctor",
            "status",
            "exit `0`",
            "`1` for findings",
            "`2` for misuse or refusal",
        ):
            with self.subTest(route_term=term):
                self.assertIn(term, route)

        self.assertIn("This file is the canonical host", self.document)
        self.assertIn("must not introduce a competing binding rule", self.document)
        self.assertIn("plugins/quenching/assets/references/front-align/mold.md", self.document)

    def test_front_specific_deltas_and_bands_are_explicit(self):
        deltas = self.document.split("## Explicit front deltas", 1)[1]
        for front, terms in {
            "design": ("DTCG", "Impeccable", "genres"),
            "ops": ("opsRoot", "router", "registry", "op-*"),
            "proof": ("proofRoot", "layers", "fixtures", "pf-*"),
        }.items():
            with self.subTest(front=front):
                row = deltas.split(f"| {front} |", 1)[1].split("\n", 1)[0]
                for term in terms:
                    self.assertIn(term, row)

        bands = self.document.split("## Disposition bands", 1)[1].split(
            "## Measured baseline and footprint", 1
        )[0]
        for band in ("Mechanical", "Structural", "Judgement"):
            self.assertIn(band, bands)
        self.assertIn("maps every finding exactly once", bands)

    def test_measured_baseline_and_final_footprint_are_distinct(self):
        baseline = {
            "design": (6, 55_860),
            "ops": (18, 96_529),
            "proof": (18, 101_461),
        }
        final = {
            "design": (8, 66_148),
            "ops": (18, 99_493),
            "proof": (18, 104_069),
        }
        baseline_section = self.document.split(
            "### Pre-adoption baseline (task 1.1)", 1
        )[1].split("### Post-adoption final footprint (task 4.3)", 1)[0]
        final_section = self.document.split(
            "### Post-adoption final footprint (task 4.3)", 1
        )[1].split("## Explicit front deltas", 1)[0]

        for front, (expected_files, expected_bytes) in baseline.items():
            with self.subTest(snapshot="baseline", front=front):
                self.assertRegex(
                    baseline_section,
                    rf"{front} \| .*\*\*{expected_files} files / {expected_bytes:,} bytes\*\*",
                )

        total_files = total_bytes = 0
        for front, (expected_files, expected_bytes) in final.items():
            paths = front_footprint(front)
            measured = (len(paths), sum(path.stat().st_size for path in paths))
            with self.subTest(snapshot="final", front=front):
                self.assertEqual(measured, (expected_files, expected_bytes))
                self.assertRegex(
                    final_section,
                    rf"{front} \| .*\*\*{expected_files} files / {expected_bytes:,} bytes\*\*",
                )
            total_files += measured[0]
            total_bytes += measured[1]

        self.assertIn("42 files / 253,850 bytes", baseline_section)
        self.assertEqual((total_files, total_bytes), (44, 269_710))
        self.assertIn("44 files / 269,710 bytes", final_section)
        conductor = (
            ROOT / "plugins" / "quenching" / "commands" / "align.md",
            ROOT / "plugins" / "quenching" / "tests" / "test_align_contract.py",
        )
        self.assertEqual(sum(path.stat().st_size for path in conductor), 14_472)
        self.assertIn("2 files / 17,813 bytes", baseline_section)
        self.assertIn("46 files / 284,182 bytes", final_section)


if __name__ == "__main__":
    unittest.main()
