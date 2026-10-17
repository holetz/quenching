"""Contract: the spec-runner never waits in a loop, and no agent or command body teaches `pgrep -f` in a wait loop."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
PLUGIN = ROOT / "plugins/quenching"
SPEC_RUNNER = PLUGIN / "agents/spec-runner.md"
LOOP_WITH_PGREP = re.compile(r"\b(until|while)\b[^;\n]*pgrep\s+-f")


class SpecRunnerWaitTests(unittest.TestCase):
    def test_rule_is_declared(self):
        body = re.sub(r"\s+", " ", SPEC_RUNNER.read_text(encoding="utf-8"))
        self.assertIn("Never wait in a loop", body)
        self.assertIn("foreground with an explicit `timeout`", body)
        self.assertIn("completion notification of a background task", body)
        self.assertIn("Never match a process with `pgrep -f`", body)

    def test_no_surface_body_waits_with_pgrep(self):
        offenders = [
            str(path.relative_to(ROOT))
            for folder in ("agents", "commands")
            for path in (PLUGIN / folder).rglob("*.md")
            if LOOP_WITH_PGREP.search(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(offenders, [])

    def test_detector_catches_the_incident_line(self):
        line = "until ! pgrep -f verify_repo.sh >/dev/null; do sleep 3; done"
        self.assertTrue(LOOP_WITH_PGREP.search(line))


if __name__ == "__main__":
    unittest.main()
