"""Structural proof for the shared local-front mold."""
from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
DOC = ROOT / "docs" / "standards" / "architecture" / "front-mold.md"
COMMANDS = ROOT / "plugins" / "quenching" / "commands"
SOURCE_REFS = ROOT / "plugins" / "quenching" / "assets" / "references"
CONDUCTOR = COMMANDS / "align.md"


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
            "toolchain": ("toolchain", "manifests", "locks", "tc-*"),
            "delivery": ("workflow", "provider", "publication", "delivery-*"),
            "security": ("read-only", "permissions", "advisory", "owner"),
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

    def test_the_conductor_declares_all_seven_aligned_fronts(self):
        order = CONDUCTOR.read_text(encoding="utf-8")
        execution = order.split("## Execution order", 1)[1].split("## Workflow", 1)[0]
        expected = {
            "knowledge": "/quenching:knowledge:align",
            "design": "/quenching:design:align",
            "components": "/quenching:components:align",
            "ops": "/quenching:ops:align",
            "proof": "/quenching:proof:align",
            "toolchain": "/quenching:toolchain:align",
            "delivery": "/quenching:delivery:align",
        }
        for front, route in expected.items():
            with self.subTest(front=front):
                self.assertIn(f"| `{front}`", execution)
                self.assertIn(route, execution)

    def test_the_mold_resource_and_projection_cover_the_domain_surfaces(self):
        resource = self.document.split("resource:", 1)[1].split("\n", 1)[0]
        for path in (
            "design-front.md", "ops-front.md", "proof-front.md", "toolchain-front.md",
            "delivery-front.md", "security-pillar.md",
        ):
            with self.subTest(resource=path):
                self.assertIn(path, resource)

        projection = (SOURCE_REFS / "front-align" / "mold.md").read_text(encoding="utf-8")
        deltas = projection.split("## Domain deltas", 1)[1]
        for front in ("design", "ops", "proof", "toolchain", "delivery", "security"):
            with self.subTest(projection=front):
                self.assertRegex(deltas, rf"(?m)^- {front} ")


if __name__ == "__main__":
    unittest.main()
