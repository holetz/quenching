"""Regression checks for the opt-in Azure payload and controlled preview contract."""
import json
import pathlib
import unittest

import _paths  # noqa: F401

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "zensical"


class AzureDocumentationPayload(unittest.TestCase):
    def test_pipeline_builds_strict_site_artifact(self):
        text = (ASSETS / "azure-pipelines-docs.yml").read_text(encoding="utf-8")
        self.assertIn("zensical build --clean --strict", text)
        self.assertIn("targetPath: site", text)
        self.assertIn("artifact: documentation-site", text)

    def test_remote_fixture_distinguishes_hosts(self):
        fixture = json.loads((ASSETS / "fixtures" / "azure-remotes.json").read_text(encoding="utf-8"))
        self.assertTrue(all("dev.azure.com" in url or "visualstudio.com" in url
                            for url in fixture["azure_devops"]))
        self.assertTrue(all("azure" not in url and "visualstudio" not in url
                            for url in fixture["non_azure"]))

    def test_offer_is_conditional_and_preview_is_loopback(self):
        build = (ROOT / "commands" / "knowledge" / "documentation" / "build.md").read_text(encoding="utf-8")
        align = (ROOT / "commands" / "knowledge" / "align.md").read_text(encoding="utf-8")
        self.assertIn("separate confirmation", build)
        self.assertIn("127.0.0.1", build)
        self.assertIn("only when the target remote is Azure DevOps", align)


if __name__ == "__main__":
    unittest.main()
