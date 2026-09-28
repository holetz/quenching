"""Regression checks for the public workflow-study contract."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import _paths  # noqa: F401


ROOT = Path(__file__).resolve().parents[3]


class StudyMaterial(unittest.TestCase):
    def test_public_material_has_no_withdrawn_or_host_drift(self):
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        source_readme = (ROOT / "plugins/quenching/README.md").read_text(encoding="utf-8")
        codex_readme = (ROOT / "plugins/quenching-codex/README.md").read_text(encoding="utf-8")
        source_index = (ROOT / "plugins/quenching/assets/knowledge/index.md").read_text(encoding="utf-8")
        codex_index = (ROOT / "plugins/quenching-codex/knowledge/index.md").read_text(encoding="utf-8")
        getting_started = (ROOT / "docs/tutorials/getting-started.md").read_text(encoding="utf-8")
        vision = (ROOT / "docs/vision/index.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertNotIn("`cq knowledge hook`", root_readme)
        self.assertIn("`54` in this heading", source_readme)
        self.assertNotIn("claude --plugin-dir", codex_readme)
        self.assertIn(".agents/skills/", codex_readme)
        self.assertNotIn("specs/backlog", source_index)
        self.assertNotIn("specs/backlog", codex_index)
        self.assertNotIn("read-only by construction", getting_started)
        self.assertNotIn("cannot touch a file", getting_started)
        self.assertNotIn("/.specs/backlog/", vision)
        self.assertIn("docs/standards/ci-cd/versioning-release.md", changelog)

    def test_experiment_is_reachable_from_the_published_reader_route(self):
        tutorial = (ROOT / "docs/tutorials/first-workflow-study.md").read_text(encoding="utf-8")
        tutorials_index = (ROOT / "docs/tutorials/index.md").read_text(encoding="utf-8")
        nav = (ROOT / "zensical.toml").read_text(encoding="utf-8")

        self.assertIn("bash experiments/first-workflow/run.sh", tutorial)
        self.assertIn("first-workflow-study.md", tutorials_index)
        self.assertIn('"tutorials/first-workflow-study.md"', nav)

    def test_disposable_runner_completes_without_checkout_mutation(self):
        runner = ROOT / "experiments/first-workflow/run.sh"
        result = subprocess.run(
            ["bash", str(runner)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS — deterministic check/write/check flow completed", result.stdout)
        self.assertNotIn("retained failed target", result.stderr)
