"""The authoring doctrine the four documents owe the builder: the tests a task declares, the
`(operational)` marker, the gate exit in the fixed report, and the resume of a paused subagent.

Each rule lives in the document that owns it and is cited by the body that follows it, never
restated there — so this suite asserts the rule where a human writing or reading that document
will meet it."""

import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "quenching/references/specs-develop/artifacts.md"
DEVELOP = ROOT / "quenching/skills/quenching-specs/references/develop.md"
AGENTS = ROOT / "docs/standards/automation/agents.md"
CONTEXT_DISCIPLINE = ROOT / "docs/standards/automation/context-discipline.md"


def text(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


class FilesDeclaresItsTests(unittest.TestCase):
    def test_artifacts_names_the_tests_the_task_produces(self):
        body = text(ARTIFACTS)
        self.assertIn("Every test whose diff the task produces belongs in its `files:`", body)
        self.assertIn("which tests does this touch?", body)
        self.assertIn("The verifier compares the branch's changed paths with the union", body)

    def test_artifacts_documents_the_operational_marker(self):
        body = text(ARTIFACTS)
        self.assertIn("A task that writes no repository file declares `files: (operational)`",
                      body)
        self.assertIn("`sp-files-operational`", body)
        self.assertIn("`sp-operational-no-verify`", body)
        self.assertIn("without a commit sha because it has no path to hang one on", body)
        self.assertIn("that flag — never the empty list — is what excuses the sha", body)


class ComposeAsksForTheTests(unittest.TestCase):
    def test_develop_asks_the_question_beside_the_three_execution_decisions(self):
        body = text(DEVELOP)
        self.assertIn("The fourth execution question is asked here", body)
        self.assertIn("which tests does this task touch?", body)
        self.assertIn("beside them, per task", body)
        self.assertIn("the out-of-scope diff the verifier charges at the door", body)


class TheReportAndTheOperationalTask(unittest.TestCase):
    def test_agents_names_the_gate_exit_field(self):
        body = text(AGENTS)
        self.assertIn("The fixed report carries the gate's exit in a field of its own", body)
        self.assertIn("`GATE_EXIT: <code | not-run>`", body)
        self.assertIn("an omitted line is read as inconclusive, never as a pass", body)

    def test_agents_accepts_the_operational_task_without_a_commit(self):
        body = text(AGENTS)
        self.assertIn("A task that writes no repository file is accepted without a commit", body)
        self.assertIn("the verifier requires a sha only from the tasks that declared paths", body)
        self.assertIn("so the marker can never hide a change", body)


class AResumedSubagent(unittest.TestCase):
    def test_context_discipline_resumes_inside_the_measured_boundary(self):
        body = text(CONTEXT_DISCIPLINE)
        self.assertIn("A paused subagent is resumed inside the measured boundary, never "
                      "relaunched by habit", body)
        self.assertIn("A resume is not a launch", body)
        self.assertIn("Past the measured `boundaries`", body)
        self.assertIn("after a `budget:` stop, the cold relaunch is the honest option", body)


if __name__ == "__main__":
    unittest.main()
