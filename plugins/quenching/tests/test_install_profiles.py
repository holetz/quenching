"""The profile contract is conduction scope, not a host-residency promise."""
from __future__ import annotations

import pathlib
import unittest

import _paths  # noqa: F401

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
STANDARD = REPO_ROOT / "docs" / "standards" / "architecture" / "install-profiles.md"
ALIGN = REPO_ROOT / "plugins" / "quenching" / "commands" / "align.md"
CONFIG_REFERENCE = (REPO_ROOT / "plugins" / "quenching" / "assets" / "references" /
                    "specs-align" / "plugin-configuration.md")


class InstallProfileContract(unittest.TestCase):
    def test_standard_does_not_claim_host_residency_or_context_control(self):
        standard = STANDARD.read_text(encoding="utf-8").lower()
        self.assertIn("conduction scope", standard)
        self.assertIn("does not remove, shorten, hide or rewrite", standard)
        for forbidden in ("disable-model-invocation", "always-on context",
                          "stop being carried in every session"):
            self.assertNotIn(forbidden, standard)

    def test_root_align_consumes_profile_as_conductor_scope(self):
        align = ALIGN.read_text(encoding="utf-8").lower()
        for phrase in ("cq specs config --json", "shared.profiles.installed", "skipped by profile",
                       "does not remove commands"):
            self.assertIn(phrase, align)

    def test_config_reference_uses_the_same_scope_and_default(self):
        reference = CONFIG_REFERENCE.read_text(encoding="utf-8").lower()
        self.assertIn("shared.profiles", reference)
        self.assertIn("all seven local fronts eligible", reference)
        self.assertIn("conduction scope", reference)


if __name__ == "__main__":
    unittest.main()
