"""`digest` reads an OpenCode session from its SQLite database through the parser it already has:
the session by id, the one running, or the newest in the directory — in flight or finished, with
the same attribution, and refusing with a reason where there is nothing honest to read."""
import contextlib
import io
import itertools
import json
import os
import pathlib
import sqlite3
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.session.commands.cli import build_parser
from quenching.session.transcript import encode_cwd

START = 1_790_000_000_000
CWD = str(pathlib.Path.cwd().resolve())
SECRET = "RESULT-BODY-THAT-MUST-NEVER-REACH-THE-DIGEST"


CALLS = itertools.count(1)


def tool(name, **inp):
    return {"type": "tool", "id": f"toolu_{next(CALLS)}", "name": name,
            "state": {"status": "completed", "input": inp, "content": [{"type": "text", "text": SECRET}]}}


def run(*argv):
    args = build_parser().parse_args(["digest", *argv, "--json"])
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = args.func(args)
    return code, out.getvalue(), err.getvalue()


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.db = self.root / "opencode.db"
        self.projects = self.root / "projects"
        self.projects.mkdir()
        env = {"QUENCHING_TRANSCRIPTS_ROOT": str(self.projects), "QUENCHING_OPENCODE_DB": str(self.db)}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("OPENCODE_SESSION_ID", None)
        self.build()

    def build(self):
        db = sqlite3.connect(self.db)
        db.executescript("""
            CREATE TABLE session_v2 (id TEXT, parent_id TEXT, agent TEXT, directory TEXT, time_updated INT);
            CREATE TABLE session_message (id TEXT, session_id TEXT, type TEXT, seq INT, data TEXT);
            CREATE TABLE session_part (message_id TEXT, session_id TEXT, ordinal INT, type TEXT, data TEXT);""")
        db.execute("INSERT INTO session_v2 VALUES ('ses_old', NULL, 'build', ?, 1)", (CWD,))
        db.execute("INSERT INTO session_v2 VALUES ('ses_root', NULL, 'build', ?, 2)", (CWD,))
        db.execute("INSERT INTO session_v2 VALUES ('ses_child', 'ses_root', 'explore', ?, 3)", (CWD,))
        db.execute("INSERT INTO session_v2 VALUES ('ses_elsewhere', NULL, 'build', ?, 9)",
                   (str(self.root / "elsewhere"),))

        def message(mid, sid, kind, seq, data):
            db.execute("INSERT INTO session_message VALUES (?, ?, ?, ?, ?)", (mid, sid, kind, seq, json.dumps(data)))

        message("m1", "ses_root", "user", 1, {"time": {"created": START}, "text": "build it"})
        # A finished message keeps its blocks inline; the skill call is the caller's own record.
        message("m2", "ses_root", "assistant", 2, {"time": {"created": START + 1}, "content": [
            {"type": "text", "text": "loading"}, tool("skill", id="demo-flow")]})
        message("m3", "ses_root", "user", 3, {"time": {"created": START + 2}, "text": "no, use the other file"})
        # The message still running has no inline blocks yet: its parts are the only record.
        message("m4", "ses_root", "assistant", 4, {"time": {"created": START + 3}, "content": []})
        for ordinal, block in enumerate([
                tool("read", path="/a.py"), tool("read", path="/a.py"),
                tool("read", path="/b.py", offset=1, limit=50), tool("edit", path="/a.py", oldString="x", newString="y"),
                tool("shell", command="echo hi"), tool("shell", command="echo hi")]):
            db.execute("INSERT INTO session_part VALUES ('m4', 'ses_root', ?, 'tool', ?)", (ordinal, json.dumps(block)))
        message("c1", "ses_child", "assistant", 1, {"time": {"created": START}, "content": [
            tool("read", path="/child-only.py")]})
        message("o1", "ses_old", "assistant", 1, {"time": {"created": START}, "content": [
            tool("skill", id="demo-old")]})
        db.commit()
        db.close()

    def commands(self, *argv):
        code, out, err = run(*argv)
        self.assertEqual(err, "")
        self.assertNotIn(SECRET, out)
        payload = json.loads(out)
        return code, payload, {c["command"]: c for c in payload["commands"]}


class ById(Fixture):
    def test_a_session_id_names_the_session_to_read(self):
        _, payload, commands = self.commands("ses_root")
        self.assertEqual(payload["resolvedBy"], "OpenCode session id")
        self.assertTrue(payload["transcript"].endswith("#ses_root"))
        self.assertEqual(payload["session"]["sessionId"], "ses_root")
        self.assertEqual(set(commands), {"demo-flow"})

    def test_the_stage_work_is_attributed_to_the_skill_entered_before_it(self):
        _, _, commands = self.commands("ses_root")
        counts = commands["demo-flow"]["counts"]
        self.assertEqual(counts["distinctFilesRead"], 2)
        self.assertEqual(counts["repeatedReadTargets"], 1)    # /a.py twice, the same window
        self.assertEqual(counts["distinctFilesWritten"], 1)   # an edit is a write, not a read
        self.assertEqual(counts["repeatedShellCommands"], 1)
        self.assertEqual(commands["demo-flow"]["entryForms"], ["skill"])

    def test_the_skill_call_itself_belongs_to_nobody_and_the_command_exists_by_its_entry(self):
        _, _, commands = self.commands("ses_root")
        self.assertEqual(commands["demo-flow"]["tools"].get("Skill"), None)

    def test_a_human_turn_after_the_entry_is_a_correction_of_the_command(self):
        _, _, commands = self.commands("ses_root")
        kinds = [c["kind"] for c in commands["demo-flow"]["corrections"]]
        self.assertEqual(kinds, ["interjection"])

    def test_a_session_of_another_id_is_not_mixed_in(self):
        _, _, commands = self.commands("ses_old")
        self.assertEqual(set(commands), {"demo-old"})

    def test_only_the_asked_session_is_read_not_its_children(self):
        _, payload, _ = self.commands("ses_root")
        self.assertNotIn("/child-only.py", json.dumps(payload))


class Selection(Fixture):
    def test_the_running_session_is_the_one_in_the_environment(self):
        with mock.patch.dict(os.environ, {"OPENCODE_SESSION_ID": "ses_old"}):
            _, payload, commands = self.commands()
        self.assertEqual(payload["resolvedBy"], "OPENCODE_SESSION_ID")
        self.assertEqual(set(commands), {"demo-old"})

    def test_without_an_id_the_newest_root_session_in_the_directory_is_read(self):
        _, payload, commands = self.commands()
        self.assertEqual(payload["resolvedBy"], "most recent OpenCode session in this directory")
        self.assertEqual(set(commands), {"demo-flow"})   # not ses_elsewhere, not the child

    def test_a_claude_transcript_for_the_directory_wins_when_nothing_names_opencode(self):
        project = self.projects / encode_cwd(CWD)
        project.mkdir()
        (project / "s1.jsonl").write_text(json.dumps(
            {"type": "assistant", "uuid": "u1", "attributionSkill": "claude:cmd",
             "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "x"}}]}}) + "\n")
        _, payload, commands = self.commands()
        self.assertEqual(set(commands), {"claude:cmd"})
        self.assertTrue(payload["transcript"].endswith("s1.jsonl"))


class Refusals(Fixture):
    def refusal(self, *argv):
        code, out, _ = run(*argv)
        self.assertEqual(code, 2)
        return json.loads(out)

    def test_an_unknown_session_refuses_with_its_id(self):
        refusal = self.refusal("ses_missing")
        self.assertEqual(refusal["code"], "se-no-transcript")
        self.assertIn("ses_missing", refusal["message"])

    def test_no_database_refuses_by_naming_where_it_looked(self):
        self.db.unlink()
        refusal = self.refusal("ses_root")
        self.assertEqual(refusal["code"], "se-no-transcript")
        self.assertIn(str(self.db), refusal["message"])

    def test_a_database_of_the_other_generation_says_so_instead_of_reading_nothing(self):
        self.db.unlink()
        db = sqlite3.connect(self.db)
        db.executescript("CREATE TABLE session (id TEXT, parent_id TEXT, agent TEXT, directory TEXT);"
                         "CREATE TABLE message (id TEXT, session_id TEXT, data TEXT);")
        db.commit()
        db.close()
        refusal = self.refusal("ses_root")
        self.assertEqual(refusal["code"], "se-no-transcript")
        self.assertIn("OpenCode 2", refusal["message"])

    def test_a_session_that_ran_no_command_refuses_rather_than_reporting_nothing(self):
        db = sqlite3.connect(self.db)
        db.execute("INSERT INTO session_v2 VALUES ('ses_quiet', NULL, 'build', ?, 5)", (CWD,))
        db.execute("INSERT INTO session_message VALUES ('q1', 'ses_quiet', 'user', 1, ?)",
                   (json.dumps({"time": {"created": START}, "text": "hello"}),))
        db.commit()
        db.close()
        self.assertEqual(self.refusal("ses_quiet")["code"], "se-no-command-parsed")

    def test_with_nothing_anywhere_the_claude_reason_is_the_one_reported(self):
        self.db.unlink()
        refusal = self.refusal()
        self.assertEqual(refusal["code"], "se-no-transcript")
        self.assertIn("no transcript directory", refusal["message"])


if __name__ == "__main__":
    unittest.main()
