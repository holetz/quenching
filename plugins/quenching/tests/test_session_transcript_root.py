"""`quenching.session.transcript.projects_root` — which transcript root each host gets."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.session.transcript import projects_root


class ProjectsRootTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        env = {k: v for k, v in os.environ.items() if k != "QUENCHING_TRANSCRIPTS_ROOT"}
        patches = [mock.patch.dict(os.environ, env, clear=True),
                   mock.patch.object(Path, "home", return_value=self.home)]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_env_override_wins(self):
        with mock.patch.dict(os.environ, {"QUENCHING_TRANSCRIPTS_ROOT": str(self.home / "x")}):
            self.assertEqual(projects_root(), self.home / "x")

    def test_claude_root_when_present(self):
        (self.home / ".claude" / "projects").mkdir(parents=True)
        (self.home / ".codex" / "sessions").mkdir(parents=True)
        self.assertEqual(projects_root(), self.home / ".claude" / "projects")

    def test_codex_host_reads_sessions_not_projects(self):
        (self.home / ".codex" / "sessions" / "2026" / "10" / "16").mkdir(parents=True)
        self.assertEqual(projects_root(), self.home / ".codex" / "sessions")

    def test_nothing_present_falls_back_to_claude_root(self):
        self.assertEqual(projects_root(), self.home / ".claude" / "projects")


if __name__ == "__main__":
    unittest.main()
