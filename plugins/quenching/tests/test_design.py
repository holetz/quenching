"""The design front's source/projection/import/render contract."""
from __future__ import annotations

import json
import pathlib
import shutil
import stat
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401 — installs assets/bin exactly as the cq entry point does

from quenching.design.align import align_plan, align_write
from quenching.design.build import build_drift, compute_build, write_build
from quenching.design.doctor import inspect_design
from quenching.design.genre import new_genre, render_genre
from quenching.design.importer import import_design
from quenching.design.model import (
    DTCG_SCHEMA,
    DesignError,
    font_asset_paths,
    read_json,
    validate_source,
)


PRODUCT = {
    "Platform": "web",
    "Stack": "Python",
    "Users": "Analysts who need a durable report of the decision and its evidence.",
    "Product Purpose": "Turn reviewed findings into consistent artifacts across media.",
    "Positioning": "One design source feeds portable design context and editorial rendering.",
    "Operating Context": "Repositories with an installed OKF bundle.",
    "Capabilities and Constraints": "Generated projections are deterministic and intentionally lossy.",
    "Brand Commitments": "A quiet evidence-led hierarchy with one accent thread.",
    "Product Principles": "One source; explicit arbitration; inspect the rendered destination.",
    "Accessibility & Inclusion": "WCAG AA is the minimum for foreground/background pairs.",
}


class DesignFront(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temporary.name)
        bundle = self.root / "docs"
        bundle.mkdir()
        (bundle / "index.md").write_text('---\nokf_version: "0.1"\n---\n\n# Knowledge\n',
                                           encoding="utf-8")
        self.aligned = align_write(self.root, PRODUCT)

    def tearDown(self):
        self.temporary.cleanup()

    def test_align_installs_one_valid_source_and_all_portable_projections(self):
        source = read_json(self.root / ".design" / "tokens.json")
        self.assertEqual(source["$schema"], DTCG_SCHEMA)
        self.assertEqual([], validate_source(source))
        self.assertEqual([], build_drift(compute_build(self.root)))

        product = (self.root / "PRODUCT.md").read_text(encoding="utf-8")
        design = (self.root / "DESIGN.md").read_text(encoding="utf-8")
        medium = (self.root / "MEDIUM.md").read_text(encoding="utf-8")
        sidecar = json.loads((self.root / ".impeccable" / "design.json").read_text(encoding="utf-8"))
        self.assertIn("<!-- impeccable:product-schema 1 -->", product)
        self.assertRegex(product, r"## Platform\n\nweb")
        self.assertRegex(product, r"## Stack\n\nPython")
        self.assertRegex(product, r"## Capabilities and Constraints\n\nGenerated projections")
        self.assertRegex(product, r"## Accessibility & Inclusion\n\nWCAG AA")
        self.assertTrue(design.startswith("---\n# GENERATED"))
        self.assertIn("# Design System: Project Design System", design)
        self.assertIn("## Do's and Don'ts", design)
        self.assertEqual(sidecar["schemaVersion"], 2)
        self.assertEqual(
            {"primary", "on-primary", "secondary", "on-secondary", "surface", "on-surface"},
            set(sidecar["extensions"]["colorMeta"]),
        )
        self.assertEqual(8, len(sidecar["extensions"]["colorMeta"]["surface"]["tonalRamp"]))
        self.assertEqual({"display", "body", "label"}, set(sidecar["extensions"]["typographyMeta"]))
        self.assertEqual(
            {component["refersTo"] for component in sidecar["components"]},
            {"button-primary", "input", "navigation", "chip", "card", "eyebrow", "rule", "frame"},
        )
        self.assertTrue((self.root / ".design" / "assets" / "lockup.svg").is_file())
        self.assertNotIn("var(--design-", " ".join(component["css"] for component in sidecar["components"]))
        button_css = next(component["css"] for component in sidecar["components"] if component["refersTo"] == "button-primary")
        self.assertIn(":hover", button_css)
        self.assertIn(":focus-visible", button_css)
        self.assertIn("| Report | read | html, typst, pdf |", medium)
        compile((self.root / ".design" / "build" / "tokens.py").read_text(encoding="utf-8"),
                "tokens.py", "exec")

    def test_align_copies_binary_brand_assets_without_decoding(self):
        pack = self.root / "brand-pack-fixture"
        shutil.copytree(pathlib.Path(__file__).parents[1] / "assets" / "design" / "brand-pack", pack)
        font = pack / ".design" / "assets" / "starter.woff2"
        expected = b"\x00\x01\x02font-bytes\xff"
        font.write_bytes(expected)
        with mock.patch("quenching.design.align.payload_root", return_value=pack):
            align_write(self.root, PRODUCT)
        self.assertEqual(expected, (self.root / ".design" / "assets" / "starter.woff2").read_bytes())

    def test_doctor_proves_byte_identity_and_names_drift(self):
        payload, findings = inspect_design(self.root)
        self.assertTrue(payload["installed"])
        self.assertEqual([], findings)
        self.assertEqual(25, payload["tokenCount"])
        self.assertEqual("alpha", payload["designMdVersion"])
        self.assertEqual(1, payload["productSchema"])
        self.assertEqual(2, payload["sidecarSchemaVersion"])
        self.assertEqual(8, payload["sidecarComponentCount"])
        self.assertEqual("skipped", payload["webDetector"]["state"])
        self.assertEqual(3, len(payload["contrastPairs"]))
        self.assertTrue(all(item["status"] == "measured" for item in payload["contrastPairs"]))
        design = self.root / "DESIGN.md"
        design.write_text(design.read_text(encoding="utf-8") + "\nmanual drift\n", encoding="utf-8")
        _, findings = inspect_design(self.root)
        self.assertIn(("design-generated-drift", "DESIGN.md"),
                      {(finding["code"], finding["path"]) for finding in findings})

    def test_import_folds_portable_changes_back_then_build_restores_identity(self):
        design = self.root / "DESIGN.md"
        text = design.read_text(encoding="utf-8")
        self.assertIn('primary: "#0F766E"', text)
        design.write_text(text.replace('primary: "#0F766E"', 'primary: "#B8422E"'),
                          encoding="utf-8")
        checked = import_design(self.root, write=False)
        self.assertIn("colors.primary", checked["changed"])
        written = import_design(self.root, write=True)
        self.assertTrue(written["lossy"])
        source = read_json(self.root / ".design" / "tokens.json")
        self.assertEqual(source["colors"]["primary"]["$value"]["hex"], "#B8422E")
        write_build(compute_build(self.root))
        _, findings = inspect_design(self.root)
        self.assertEqual([], findings)

    def test_external_design_requires_an_explicit_human_winner(self):
        design = self.root / "DESIGN.md"
        design.write_text('---\nname: Incoming\ncolors:\n  primary: "#B8422E"\n---\n', encoding="utf-8")
        plan = align_plan(self.root, PRODUCT)
        self.assertTrue(any("source winner" in blocker for blocker in plan["blockers"]))
        with self.assertRaises(DesignError):
            align_write(self.root, PRODUCT)
        align_write(self.root, PRODUCT, design_winner="import")
        self.assertEqual(read_json(self.root / ".design" / "tokens.json")["colors"]["primary"]["$value"]["hex"], "#B8422E")

    def test_generated_notice_does_not_hide_manual_projection_drift(self):
        design = self.root / "DESIGN.md"
        text = design.read_text(encoding="utf-8")
        design.write_text(text.replace("one accent on the decision", "two accents on the decision"), encoding="utf-8")
        plan = align_plan(self.root, PRODUCT)
        self.assertTrue(any("source winner" in blocker for blocker in plan["blockers"]))

    def test_import_retains_valid_dtcg_and_reports_richer_impeccable_values(self):
        (self.root / "DESIGN.md").write_text(
            """---
name: Incoming
colors:
  primary: \"oklch(49% 0.09 185)\"
typography:
  scale:
    \"16\": \"1rem\"
  display:
    fontFamily: \"Montserrat\"
    fontSize: \"clamp(3rem, 6vw, 5rem)\"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: \"0\"
rounded:
  none: \"0\"
components:
  button-primary:
    textColor: \"{colors.on-primary}\"
    borderColor: \"{colors.primary}\"
---
""", encoding="utf-8")
        imported = import_design(self.root, write=False)
        self.assertIn("colors.primary", imported["changed"])
        self.assertIn("typography.scale", imported["skipped"])
        self.assertIn("typography.display", imported["skipped"])
        self.assertIn("components.button-primary.borderColor", imported["skipped"])

    def test_dtcg_json_pointer_alias_resolves_in_adapters(self):
        path = self.root / ".design" / "tokens.json"
        source = read_json(path)
        source["spacing"]["xl"]["$value"] = {"$ref": "#/spacing/lg"}
        source["colors"]["$root"] = {"$ref": "#/colors/primary"}
        path.write_text(json.dumps(source), encoding="utf-8")
        self.assertEqual([], validate_source(source))
        write_build(compute_build(self.root))
        css = (self.root / ".design" / "build" / "tokens.css").read_text(encoding="utf-8")
        self.assertIn("--design-spacing-xl: var(--design-spacing-lg);", css)
        self.assertIn("--design-colors: var(--design-colors-primary);", css)
        sidecar = json.loads((self.root / ".impeccable" / "design.json").read_text(encoding="utf-8"))
        self.assertIn("colors", sidecar["extensions"]["colorMeta"])
        source["$extensions"]["org.quenching"]["designMd"]["components"]["button-primary"]["height"] = "{spacing.missing}"
        self.assertIn("design-component-reference", {item["code"] for item in validate_source(source)})

    def test_font_family_tokens_support_metadata_and_nested_typography_references(self):
        path = self.root / ".design" / "tokens.json"
        source = read_json(path)
        source["fonts"] = {
            "body": {
                "$type": "fontFamily",
                "$value": ["Brand Sans", "sans-serif"],
                "$extensions": {"org.quenching": {"font": {
                    "source": "licensed",
                    "license": "OFL-1.1",
                    "files": ["fonts/brand-sans.woff2"],
                }}},
            }
        }
        source["typography"]["body"]["$value"]["fontFamily"] = "{fonts.body}"
        self.assertEqual([], validate_source(source))
        paths = font_asset_paths(source, self.root / ".design" / "assets")
        self.assertEqual([self.root / ".design" / "assets" / "fonts" / "brand-sans.woff2"], paths["fonts.body"])
        path.write_text(json.dumps(source), encoding="utf-8")
        write_build(compute_build(self.root))
        css = (self.root / ".design" / "build" / "tokens.css").read_text(encoding="utf-8")
        self.assertIn("--design-typography-body-font-family: Brand Sans, sans-serif;", css)

    def test_genre_renders_html_from_fields_and_generated_tokens(self):
        created = new_genre(
            self.root, "bulletin", "Bulletin", "read", ["html", "typst"],
            ["title:required:Document title", "body:required:Reviewed body"],
        )
        self.assertIn(".design/genres/bulletin.md", created["files"])
        data = self.root / "bulletin.json"
        data.write_text(json.dumps({"title": "Risk review", "body": "Evidence first."}),
                        encoding="utf-8")
        rendered = render_genre(self.root, "bulletin", "html", data)
        output = self.root / rendered["output"]
        html = output.read_text(encoding="utf-8")
        self.assertIn("Risk review", html)
        self.assertIn("--design-colors-primary", html)
        self.assertNotIn("{{", html)

    def test_read_genre_renders_markdown_semantically_in_html_and_typst(self):
        new_genre(
            self.root, "markdown-note", "Markdown note", "read", ["html", "typst"],
            ["title:required:Title", "body:required:Reviewed body"],
        )
        data = self.root / "markdown-note.json"
        data.write_text(json.dumps({
            "title": "A note",
            "body": "# Findings\n\n**Strong** and *emphasis* with [evidence](https://example.test).\n\n- one\n- two\n\n| Key | Value |\n| --- | --- |\n| A | B |",
        }), encoding="utf-8")
        html_output = render_genre(self.root, "markdown-note", "html", data)
        html = (self.root / html_output["output"]).read_text(encoding="utf-8")
        self.assertIn("<h1>Findings</h1>", html)
        self.assertIn("<strong>Strong</strong>", html)
        self.assertIn("<ul><li>one</li><li>two</li></ul>", html)
        self.assertIn("<table>", html)
        self.assertNotIn("**Strong**", html)
        typst_output = render_genre(self.root, "markdown-note", "typst", data)
        typst = (self.root / typst_output["output"]).read_text(encoding="utf-8")
        self.assertIn("= Findings", typst)
        self.assertIn("#strong[Strong]", typst)
        self.assertIn("- one", typst)
        self.assertIn("#table(columns: 2", typst)

    def test_non_read_genre_keeps_body_as_escaped_scalar_text(self):
        new_genre(
            self.root, "data-note", "Data note", "write", ["html"],
            ["title:required:Title", "body:required:Body"],
        )
        data = self.root / "data-note.json"
        data.write_text(json.dumps({"title": "A note", "body": "**literal** <tag>"}), encoding="utf-8")
        rendered = render_genre(self.root, "data-note", "html", data)
        html = (self.root / rendered["output"]).read_text(encoding="utf-8")
        self.assertIn("**literal** &lt;tag&gt;", html)
        self.assertNotIn("<strong>literal</strong>", html)

    def test_genre_template_matches_non_report_field_contract(self):
        new_genre(
            self.root, "brief", "Brief", "read", ["html"],
            ["headline:required:Headline", "summary:required:Executive summary"],
        )
        data = self.root / "brief.json"
        data.write_text(json.dumps({"headline": "Decision", "summary": "Evidence first."}), encoding="utf-8")
        rendered = render_genre(self.root, "brief", "html", data)
        html = (self.root / rendered["output"]).read_text(encoding="utf-8")
        self.assertIn("Decision", html)
        self.assertIn("Evidence first.", html)
        self.assertNotIn("field.title", html)

    def test_pdf_render_uses_typst_when_available(self):
        new_genre(
            self.root, "pdf-note", "PDF note", "read", ["pdf"],
            ["title:required:Title", "body:required:Body"],
        )
        data = self.root / "pdf-note.json"
        data.write_text(json.dumps({"title": "A note", "body": "Text."}), encoding="utf-8")
        compiler = self.root / "fake-typst"
        compiler.write_text("#!/bin/sh\nprintf '%%PDF-1.4\\n' > \"$3\"\n", encoding="utf-8")
        compiler.chmod(compiler.stat().st_mode | stat.S_IXUSR)
        with mock.patch("quenching.design.genre.shutil.which", return_value=str(compiler)):
            rendered = render_genre(self.root, "pdf-note", "pdf", data)
        self.assertTrue((self.root / rendered["output"]).is_file())

    def test_pdf_render_passes_declared_font_directories_to_typst(self):
        path = self.root / ".design" / "tokens.json"
        source = read_json(path)
        font = self.root / ".design" / "assets" / "fonts" / "brand.woff2"
        font.parent.mkdir(parents=True)
        font.write_bytes(b"font")
        source["fonts"] = {"brand": {
            "$type": "fontFamily", "$value": "Brand Sans",
            "$extensions": {"org.quenching": {"font": {
                "source": "licensed", "license": "OFL-1.1", "files": ["fonts/brand.woff2"]
            }}}
        }}
        source["typography"]["display"]["$value"]["fontFamily"] = "{fonts.brand}"
        path.write_text(json.dumps(source), encoding="utf-8")
        new_genre(self.root, "pdf-font", "PDF font", "read", ["pdf"],
                  ["title:required:Title", "body:required:Body"])
        data = self.root / "pdf-font.json"
        data.write_text(json.dumps({"title": "A note", "body": "Text."}), encoding="utf-8")
        compiler = self.root / "fake-typst"
        compiler.write_text("#!/bin/sh\nprintf '%%PDF-1.4\\n' > \"$3\"\n", encoding="utf-8")
        compiler.chmod(compiler.stat().st_mode | stat.S_IXUSR)
        with mock.patch("quenching.design.genre.shutil.which", return_value=str(compiler)):
            render_genre(self.root, "pdf-font", "pdf", data)
        # The fake compiler keeps the target at argv[3]; successful output proves
        # the additional font flags did not change the required Typst invocation.
        self.assertTrue((self.root / ".design" / "build" / "pdf-font.pdf").is_file())

    def test_doctor_reports_missing_declared_font_assets(self):
        path = self.root / ".design" / "tokens.json"
        source = read_json(path)
        source["fonts"] = {"brand": {
            "$type": "fontFamily", "$value": "Brand Sans",
            "$extensions": {"org.quenching": {"font": {
                "source": "licensed", "license": "OFL-1.1", "files": ["fonts/missing.woff2"]
            }}}
        }}
        source["typography"]["display"]["$value"]["fontFamily"] = "{fonts.brand}"
        path.write_text(json.dumps(source), encoding="utf-8")
        write_build(compute_build(self.root))
        _, findings = inspect_design(self.root)
        missing = [item for item in findings if item["code"] == "design-font-unresolved"]
        self.assertEqual(1, len(missing))
        self.assertIn("Brand Sans", missing[0]["message"])

    def test_doctor_measures_color_pairs_with_declared_wcag_policy(self):
        path = self.root / ".design" / "tokens.json"
        source = read_json(path)
        source["colors"]["primary"]["$value"] = {
            "colorSpace": "srgb", "components": [0.5, 0.5, 0.5], "hex": "#808080"
        }
        path.write_text(json.dumps(source), encoding="utf-8")
        write_build(compute_build(self.root))
        payload, findings = inspect_design(self.root)
        failures = [item for item in findings if item["code"] == "design-contrast-failure"]
        self.assertEqual(1, len(failures))
        self.assertEqual("3.98", failures[0]["ratio"])
        self.assertEqual("4.50", failures[0]["threshold"])
        self.assertEqual("normal", payload["contrastPolicy"]["textSize"])
        source["$extensions"]["org.quenching"]["accessibility"] = {
            "contrast": {"level": "AA", "textSize": "large"}
        }
        path.write_text(json.dumps(source), encoding="utf-8")
        write_build(compute_build(self.root))
        payload, findings = inspect_design(self.root)
        self.assertNotIn("design-contrast-failure", {item["code"] for item in findings})
        self.assertEqual(3.0, payload["contrastPolicy"]["threshold"])

    def test_doctor_reports_orphan_assets_and_non_web_literal_drift(self):
        asset = self.root / ".design" / "assets" / "unused.svg"
        asset.write_text("<svg/>", encoding="utf-8")
        manual = self.root / ".design" / "media" / "typst" / "manual.typ"
        manual.write_text('#let forbidden = "#0F766E"\n', encoding="utf-8")
        _, findings = inspect_design(self.root)
        codes = {finding["code"] for finding in findings}
        self.assertIn("design-asset-orphan", codes)
        self.assertIn("design-nonweb-literal", codes)


if __name__ == "__main__":
    unittest.main()
