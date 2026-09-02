"""The exit-code ladder and the four doors a run leaves by.

Before the module these tests cover, the contract was declared in three docstrings and implemented
in none — the three scripts answered 1, 2 and 0 to the same trivial case. Every assertion here is
therefore about a number a conductor branches on, not about wording.
"""

import contextlib
import io
import json
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common.output import (
    CQArgumentParser,
    FINDINGS,
    OK,
    REFUSAL,
    USAGE,
    emit,
    emit_err,
    exit_for,
    finding,
    refuse,
    report_findings,
)


@contextlib.contextmanager
def captured():
    """Yield (stdout, stderr) buffers — separate, because which stream a door writes to is part
    of the contract."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        yield out, err


class Ladder(unittest.TestCase):
    def test_the_verdict_steps_are_zero_one_two_in_that_order(self):
        self.assertEqual((OK, FINDINGS, REFUSAL), (0, 1, 2))

    def test_usage_is_the_first_code_after_the_refusal_ladder(self):
        self.assertEqual(USAGE, 3)


class Parser(unittest.TestCase):
    def test_argparse_syntax_uses_the_distinct_usage_exit(self):
        parser = CQArgumentParser(prog="cq test")
        parser.add_argument("command", choices=("run",))
        with captured() as (out, err):
            with self.assertRaises(SystemExit) as raised:
                parser.parse_args(["unknown"])
        self.assertEqual(raised.exception.code, USAGE)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("usage: cq test", err.getvalue())


class Emit(unittest.TestCase):
    PAYLOAD = {"ok": True, "count": 2}

    def test_json_rendering_is_the_payload_and_nothing_else(self):
        with captured() as (out, err):
            emit(True, self.PAYLOAD, "two things")
        self.assertEqual(json.loads(out.getvalue()), self.PAYLOAD)
        self.assertEqual(err.getvalue(), "")

    def test_human_rendering_is_the_human_string(self):
        with captured() as (out, _):
            emit(False, self.PAYLOAD, "two things")
        self.assertEqual(out.getvalue(), "two things\n")

    def test_prefix_leads_the_human_rendering(self):
        with captured() as (out, _):
            emit(False, self.PAYLOAD, "two things", prefix="resolved x\n")
        self.assertEqual(out.getvalue(), "resolved x\ntwo things\n")

    def test_prefix_never_reaches_the_json_rendering(self):
        with captured() as (out, _):
            emit(True, self.PAYLOAD, "two things", prefix="resolved x\n")
        self.assertEqual(json.loads(out.getvalue()), self.PAYLOAD)


class EmitErr(unittest.TestCase):
    def test_an_error_without_a_declared_step_exits_by_findings(self):
        with captured():
            self.assertEqual(emit_err(True, {"code": "sp-missing", "message": "no such spec"}),
                             FINDINGS)

    def test_an_error_carrying_a_step_exits_by_the_step_it_declares(self):
        with captured():
            self.assertEqual(
                emit_err(True, {"code": "sp-no-backend", "message": "no backend", "exit": REFUSAL}),
                REFUSAL)

    def test_the_exit_key_is_stripped_from_the_json_payload(self):
        with captured() as (out, _):
            emit_err(True, {"code": "sp-no-backend", "message": "no backend", "exit": REFUSAL})
        payload = json.loads(out.getvalue())
        self.assertEqual(payload, {"ok": False, "code": "sp-no-backend", "message": "no backend"})

    def test_human_rendering_prefixes_the_message_with_error(self):
        with captured() as (out, _):
            emit_err(False, {"code": "sp-missing", "message": "no such spec"})
        self.assertEqual(out.getvalue(), "error: no such spec\n")

    def test_a_refusal_uses_the_refusal_door(self):
        with captured() as (out, err):
            self.assertEqual(emit_err(False, {"code": "sp-no-backend", "message": "no backend",
                                               "exit": REFUSAL}), REFUSAL)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "refused: no backend\n")


class Refuse(unittest.TestCase):
    PAYLOAD = {"code": "sp-dirty-tree", "message": "the tree is dirty"}

    def test_a_refusal_exits_by_the_third_step(self):
        with captured():
            self.assertEqual(refuse(self.PAYLOAD, True), REFUSAL)
            self.assertEqual(refuse(self.PAYLOAD, False), REFUSAL)

    def test_the_human_refusal_goes_to_stderr_and_leaves_stdout_empty(self):
        # A refusal is not an answer, and a caller piping stdout is collecting answers.
        with captured() as (out, err):
            refuse(self.PAYLOAD, False)
        self.assertEqual(err.getvalue(), "refused: the tree is dirty\n")
        self.assertEqual(out.getvalue(), "")

    def test_the_json_refusal_goes_to_stdout_and_says_it_is_not_ok(self):
        with captured() as (out, err):
            refuse(self.PAYLOAD, True)
        self.assertEqual(json.loads(out.getvalue()), {"ok": False, **self.PAYLOAD})
        self.assertEqual(err.getvalue(), "")


class ExitFor(unittest.TestCase):
    def test_a_warning_does_not_fail_the_run(self):
        # `stale-doc` is a warning by construction, so this is what keeps it from turning a sweep red.
        self.assertEqual(exit_for([finding("stale-doc", "warning", "aged")]), OK)

    def test_an_error_fails_the_run(self):
        self.assertEqual(exit_for([finding("okf-bad-type", "error", "unknown type")]), FINDINGS)

    def test_an_error_alongside_warnings_still_fails_the_run(self):
        self.assertEqual(exit_for([finding("stale-doc", "warning", "aged"),
                                   finding("okf-bad-type", "error", "unknown type")]), FINDINGS)

    def test_no_findings_at_all_is_ok(self):
        self.assertEqual(exit_for([]), OK)


class ReportFindings(unittest.TestCase):
    ERROR = finding("okf-bad-type", "error", "unknown type", subject="a.md")
    WARNING = finding("stale-doc", "warning", "aged", subject="b.md")

    def test_json_says_not_ok_when_an_error_is_present(self):
        with captured() as (out, _):
            self.assertEqual(report_findings(True, "bundle", {"scanned": 2},
                                             [self.ERROR, self.WARNING]), FINDINGS)
        payload = json.loads(out.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["scanned"], 2)
        self.assertEqual(payload["findings"], [self.ERROR, self.WARNING])

    def test_json_says_ok_when_only_warnings_are_present(self):
        with captured() as (out, _):
            self.assertEqual(report_findings(True, "bundle", {}, [self.WARNING]), OK)
        self.assertTrue(json.loads(out.getvalue())["ok"])

    def test_the_human_header_counts_errors_and_warnings_apart(self):
        with captured() as (out, _):
            report_findings(False, "bundle", {}, [self.ERROR, self.WARNING])
        self.assertEqual(out.getvalue().splitlines()[0], "bundle (1 error(s), 1 warning(s))")

    def test_each_human_line_carries_the_severity_the_subject_and_the_code(self):
        with captured() as (out, _):
            report_findings(False, "bundle", {}, [self.ERROR])
        self.assertEqual(out.getvalue().splitlines()[1],
                         "  [error] a.md: unknown type  (okf-bad-type)")

    def test_a_clean_run_says_so_in_words_rather_than_printing_an_empty_list(self):
        with captured() as (out, _):
            self.assertEqual(report_findings(False, "bundle", {}, []), OK)
        self.assertEqual(out.getvalue().splitlines(),
                         ["bundle (0 error(s), 0 warning(s))", "  OK — no findings."])


if __name__ == "__main__":
    unittest.main()
