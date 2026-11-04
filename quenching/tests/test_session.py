"""The transcript reader's own fixture: one JSONL file exercising every rule
`read_session`/`close_attribution`/`silence_refusal` hold, migrated from the pre-refactor
session script's `selftest_failures`.

Each fixture below stayed exactly what it was in the script — a case earns its place because
some prior, real reading of a transcript got it wrong, and the comment on each record says
which mistake.
"""
import argparse
import json
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.session.commands.cli import build_parser
from quenching.session.parse import read_session, silence_refusal

# A typed `/` invocation, a conducted stage, redundant vs. paged reads, a write miscounted
# as a read, an unclosed stage, an interjection/interrupt/compaction turn, an unparsable
# line, and a replayed uuid — one transcript proving all of it at once.
FIXTURE = [
    # A typed `/` invocation: a user turn whose content is a STRING.
    {"type": "user", "uuid": "u1", "timestamp": "2026-07-28T10:00:00Z",
     "message": {"content": "<command-message>demo:conduct</command-message>\n"
                            "<command-name>/demo:conduct</command-name>\n"
                            "<command-args>alpha beta</command-args>"}},
    # The harness-injected command body. Reads exactly like a long human message; isMeta
    # is the only thing separating them, and without it every command scores a correction
    # against itself at its own first turn.
    {"type": "user", "uuid": "u2", "isMeta": True, "timestamp": "2026-07-28T10:00:01Z",
     "message": {"content": [{"type": "text", "text": "# /demo:conduct — the expanded body"}]}},
    # Two Reads of the SAME window: redundant.
    {"type": "assistant", "uuid": "u3", "attributionSkill": "demo:conduct",
     "attributionPlugin": "demo", "timestamp": "2026-07-28T10:00:02Z",
     "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/a.py"}}]}},
    {"type": "assistant", "uuid": "u4", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/a.py"}}]}},
    # Two Reads of DIFFERENT windows: paging, not redundancy.
    {"type": "assistant", "uuid": "u5", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Read",
                              "input": {"file_path": "/b.py", "offset": 1, "limit": 50}}]}},
    {"type": "assistant", "uuid": "u6", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Read",
                              "input": {"file_path": "/b.py", "offset": 60, "limit": 50}}]}},
    # An Edit is a WRITE. Counting it as a read once reported 51 edits as "redundant x72".
    {"type": "assistant", "uuid": "u7", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Edit",
                              "input": {"file_path": "/a.py", "old_string": "x", "new_string": "y"}}]}},
    # A conductor's stage. The Skill call itself is attributed to the CALLER.
    {"type": "assistant", "uuid": "u8", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Skill",
                              "input": {"skill": "demo:stage", "args": "gamma"}}]}},
    {"type": "assistant", "uuid": "u9", "attributionSkill": "demo:stage",
     "message": {"content": [{"type": "tool_use", "name": "Bash",
                              "input": {"command": "echo hi"}}]}},
    {"type": "assistant", "uuid": "u10", "attributionSkill": "demo:stage",
     "message": {"content": [{"type": "tool_use", "name": "Bash",
                              "input": {"command": "echo hi"}}]}},
    # A human turn as a text BLOCK in a list. Reading only the string form found ZERO
    # interjections on a real session that visibly had several.
    {"type": "user", "uuid": "u11", "timestamp": "2026-07-28T10:00:11Z",
     "message": {"content": [{"type": "text", "text": "no, use the other file"}]}},
    {"type": "user", "uuid": "u12", "timestamp": "2026-07-28T10:00:12Z",
     "message": {"content": [{"type": "text", "text": "[Request interrupted by user]"}]}},
    "{ this line is not JSON",          # must be COUNTED and REPORTED, never silently dropped
    # A replayed uuid: a compact summary re-embeds earlier turns, which would double the run.
    {"type": "user", "uuid": "u12",
     "message": {"content": [{"type": "text", "text": "[Request interrupted by user]"}]}},
    # The harness talking, not the human. Counting it blames the command for running long.
    {"type": "user", "uuid": "u15",
     "message": {"content": "This session is being continued from a previous conversation "
                            "that ran out of context."}},
]

# The rare good case: the conductor DOES take attribution back, so the stage's run genuinely
# ends and its counts are exact. Measured at 1 of 43 stages, which is exactly why the other
# 42 must not be reported as though they looked like this.
CLOSED_FIXTURE = [
    {"type": "user", "uuid": "c1",
     "message": {"content": "<command-name>/demo:conduct</command-name>"}},
    {"type": "assistant", "uuid": "c2", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Skill",
                              "input": {"skill": "demo:stage"}}]}},
    {"type": "assistant", "uuid": "c3", "attributionSkill": "demo:stage",
     "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "a"}}]}},
    {"type": "assistant", "uuid": "c4", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "b"}}]}},
]

# A transcript that plainly HELD something and yielded no command. The point of the case
# is that this must never come back as a clean, empty report.
SILENT_FIXTURE = [
    {"type": "user", "uuid": "s1", "message": {"content": "just a conversation"}},
    {"type": "assistant", "uuid": "s2",
     "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}},
]


def _read(records: list) -> dict:
    """Write `records` to a throwaway `.jsonl` — dicts as JSON lines, any other item verbatim,
    so a fixture can plant a line that is deliberately not JSON — and read it back."""
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "fixture.jsonl"
        path.write_text("\n".join(json.dumps(r) if isinstance(r, dict) else r for r in records)
                        + "\n", encoding="utf-8")
        return read_session(path)


class MainFixture(unittest.TestCase):
    """Every assertion `FIXTURE` was built to drive, against `demo:conduct`/`demo:stage`."""

    @classmethod
    def setUpClass(cls):
        cls.model = _read(FIXTURE)
        cls.by_name = {c.name: c for c in cls.model["_commands"]}

    def test_both_commands_are_found(self):
        self.assertEqual(sorted(self.by_name), ["demo:conduct", "demo:stage"])

    def test_typed_entry_carries_its_form_and_args(self):
        conduct = self.by_name["demo:conduct"]
        self.assertEqual(conduct.entry_forms, ["typed"])
        self.assertEqual([i["args"] for i in conduct.invocations], ["alpha beta"])
        self.assertEqual(conduct.plugin, "demo")

    def test_skill_entry_records_who_invoked_it_and_with_what(self):
        stage = self.by_name["demo:stage"]
        self.assertEqual(stage.entry_forms, ["skill"])
        self.assertEqual([i["invokedBy"] for i in stage.invocations], ["demo:conduct"])
        self.assertEqual([i["args"] for i in stage.invocations], ["gamma"])

    def test_the_skill_call_is_attributed_to_the_caller_the_stage_work_to_the_callee(self):
        conduct, stage = self.by_name["demo:conduct"], self.by_name["demo:stage"]
        self.assertEqual(conduct.tools, {"Read": 4, "Edit": 1, "Skill": 1})
        self.assertEqual(stage.tools, {"Bash": 2})

    def test_two_reads_of_the_same_window_are_redundant_not_two_different_files(self):
        conduct = self.by_name["demo:conduct"]
        self.assertEqual(sorted(conduct.reads), ["/a.py", "/b.py"])
        self.assertEqual(conduct.reads["/a.py"], ["full", "full"])

    def test_two_reads_of_different_windows_are_paging_not_redundant(self):
        self.assertEqual(self.by_name["demo:conduct"].reads["/b.py"], ["1+50", "60+50"])

    def test_an_edit_is_a_write_counted_apart_from_reads(self):
        self.assertEqual(self.by_name["demo:conduct"].touches, {"/a.py": 1})

    def test_a_repeated_shell_command_is_counted_not_deduped_away(self):
        self.assertEqual(self.by_name["demo:stage"].shell, {"echo hi": 2})

    def test_corrections_are_collected_by_line_and_kind(self):
        # Where a correction gets ATTACHED is a separate, harder question this fixture does
        # not settle — only that the three kinds are found and counted right.
        kinds = [(c["line"], c["kind"]) for c in self.model["corrections"]]
        self.assertEqual(kinds, [(11, "interjection"), (12, "interrupt"), (15, "compaction")])

    def test_a_conductors_own_run_is_closed(self):
        self.assertTrue(self.by_name["demo:conduct"].closed)

    def test_an_unresumed_stage_is_marked_unclosed_and_names_who_may_own_its_turns(self):
        stage = self.by_name["demo:stage"]
        self.assertFalse(stage.closed)
        self.assertEqual(stage.may_include, "demo:conduct")

    def test_the_unclosed_misread_is_reported_as_an_anomaly_not_just_flagged_on_the_command(self):
        codes = [a["code"] for a in self.model["anomalies"] if a["code"] == "se-attribution-unclosed"]
        self.assertEqual(codes, ["se-attribution-unclosed"])

    def test_an_unparsable_line_is_counted_and_reported_at_its_own_line_number(self):
        unparsed_anomalies = [a for a in self.model["anomalies"] if a["code"] == "se-unparsed-line"]
        self.assertEqual(self.model["unparsed"], 1)
        self.assertEqual([a["line"] for a in unparsed_anomalies], [13])

    def test_a_parsed_run_with_commands_does_not_refuse(self):
        self.assertIsNone(silence_refusal(self.model))


class ClosedFixture(unittest.TestCase):
    """The rare good case, proved apart from the misread it is the mirror of: a real
    `closed: True` and a `last` line that stops before the conductor resumes must both hold,
    or the signal in `MainFixture` means nothing."""

    @classmethod
    def setUpClass(cls):
        model = _read(CLOSED_FIXTURE)
        cls.by_name = {c.name: c for c in model["_commands"]}
        cls.anomalies = model["anomalies"]

    def test_a_resumed_stage_is_closed(self):
        self.assertTrue(self.by_name["demo:stage"].closed)

    def test_a_closed_stages_run_ends_before_the_conductor_resumes(self):
        self.assertEqual(self.by_name["demo:stage"].last, 3)

    def test_no_anomaly_is_raised_on_the_clean_case(self):
        self.assertEqual(self.anomalies, [])


class SilenceRefusal(unittest.TestCase):
    """`silence_refusal` — "no commands found" and "could not read this file" must never
    collapse into the same, silent, empty report."""

    def test_a_transcript_that_held_something_and_yielded_no_command_refuses(self):
        model = _read(SILENT_FIXTURE)
        refusal = silence_refusal(model)
        self.assertIsNotNone(refusal)
        self.assertEqual(refusal["code"], "se-no-command-parsed")

    def test_the_refusal_states_how_much_it_actually_read(self):
        refusal = silence_refusal(_read(SILENT_FIXTURE))
        self.assertIn("2 record(s)", refusal["message"])

    def test_an_empty_transcript_refuses_with_its_own_code(self):
        refusal = silence_refusal(_read([]))
        self.assertEqual(refusal["code"], "se-empty-transcript")


class ParserContract(unittest.TestCase):
    """The uniform contract, proved against the parser rather than against the docstring: a
    subcommand added without `--json` is the whole failure mode this catches."""

    def test_the_parser_declares_at_least_one_subcommand(self):
        subparsers = [a for a in build_parser()._actions
                     if isinstance(a, argparse._SubParsersAction)]
        self.assertTrue(subparsers)

    def test_every_subcommand_accepts_json(self):
        subparsers = [a for a in build_parser()._actions
                     if isinstance(a, argparse._SubParsersAction)]
        choices = subparsers[0].choices
        self.assertTrue(choices, "no subcommands registered — the loop below would pass vacuously")
        for name, sub in choices.items():
            with self.subTest(subcommand=name):
                opts = {o for action in sub._actions for o in action.option_strings}
                self.assertIn("--json", opts)


if __name__ == "__main__":
    unittest.main()
