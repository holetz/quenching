"""Contract: a spawn that dies without a report is resumed from `specs_status`, never parked as `blocked`."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "quenching"
ORCHESTRATOR = PLUGIN / "agents/spec-orchestrator.md"
RUNNER = PLUGIN / "agents/spec-runner.md"
ORCHESTRATE = PLUGIN / "skills/quenching-specs/references/orchestrate.md"
SCHEMA = PLUGIN / "assets/specs/schema.json"


def flat(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


class SchemaTests(unittest.TestCase):
    def test_schema_run_state_admits_interrupted(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        levels = schema["frontmatter"]["records"]["run"]["state"]["levels"]
        self.assertIn("interrupted", levels)


class FlowTextTests(unittest.TestCase):
    def test_orchestrator_resumes_a_dead_spawn(self):
        body = flat(ORCHESTRATOR)
        self.assertIn("died without a report", body)
        self.assertIn("`resume`", body)
        self.assertIn('"state": "interrupted"', body)
        self.assertIn("one resume per crash", body)

    def test_runner_knows_resume(self):
        body = flat(RUNNER)
        self.assertIn("Given `resume`", body)
        self.assertIn("never discard", body)

    def test_orchestrate_relay_separates_dead_spawn_from_blocked(self):
        body = flat(ORCHESTRATE)
        self.assertIn("resume", body)
        self.assertIn("without a report", body)


if __name__ == "__main__":
    unittest.main()
