"""Contract for the autopilot's default of one round, its resumable record and launch ceiling."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
AUTOPILOT = ROOT / "plugins/quenching/commands/specs/autopilot.md"


def text():
    return re.sub(r"\s+", " ", AUTOPILOT.read_text(encoding="utf-8"))


class AutopilotRoundsTests(unittest.TestCase):
    def test_no_flag_runs_one_round(self):
        body = text()
        self.assertIn("no flag runs **ONE round**", body)
        self.assertIn("`--until-dry` repeats rounds until the queue runs dry", body)
        self.assertIn("`--until <date-time with offset>`", body)
        self.assertIn("one round is the default", body)

    def test_round_record_is_resumable(self):
        body = text()
        self.assertIn("autopilot/<date>/rounds.md", body)
        self.assertIn("`open|closed`", body)
        self.assertIn("resumes at its recorded next step", body)

    def test_next_round_opens_in_fresh_context_with_fallback(self):
        body = text()
        self.assertIn("**fresh context**", body)
        self.assertIn("If a sub-agent cannot launch sub-agents, stop instead", body)

    def test_launch_ceiling_is_provisional_forty(self):
        body = text()
        self.assertIn("`--max-launches <n>`", body)
        self.assertIn("default **40**, provisional", body)
        self.assertIn("The launch ceiling binds the whole tree", body)

    def test_grants_are_unchanged(self):
        head = AUTOPILOT.read_text(encoding="utf-8").split("---")[1]
        self.assertIn("allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(git:*), Bash, Read, Grep, Glob, Agent, Task, TaskStop", head)


if __name__ == "__main__":
    unittest.main()
