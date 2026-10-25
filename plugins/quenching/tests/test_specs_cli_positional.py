"""`show`, `status` and `parallel` take the spec id positionally as well as through `--spec`.

`section` and `promote` already took it positionally; callers mixed the two forms and bounced off
`required: --spec`. Both forms must mean the same, a conflict must refuse, and `status` keeps
working with `--epic` and no id.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.commands.cli import SPEC_POSITIONAL, build_parser


def parse(*argv):
    parser, _ = build_parser()
    return parser.parse_args(list(argv))


class PositionalSpecId(unittest.TestCase):
    def test_the_three_verbs_accept_the_id_positionally(self):
        for verb in SPEC_POSITIONAL:
            self.assertEqual(parse(verb, "1192").spec_id, "1192")

    def test_the_spec_flag_still_parses(self):
        for verb in SPEC_POSITIONAL:
            args = parse(verb, "--spec", "1192")
            self.assertEqual(args.spec, "1192")
            self.assertIsNone(args.spec_id)

    def test_status_keeps_its_epic_alternative(self):
        args = parse("status", "--epic", "1197")
        self.assertIsNone(args.spec_id)
        self.assertEqual(args.epic, "1197")

    def test_show_options_follow_the_positional(self):
        self.assertEqual(parse("show", "1192", "--task", "1.1").task, ["1.1"])


class Folding(unittest.TestCase):
    """`main` folds the positional into `args.spec`; exercised through the entry point."""

    def run_main(self, *argv):
        import contextlib
        import io
        from quenching.specs.commands.cli import main
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            try:
                code = main(["--root", "/nonexistent-root", *argv])
            except SystemExit as e:
                code = e.code
        return code, err.getvalue()

    def test_a_missing_id_refuses_naming_both_forms(self):
        code, err = self.run_main("show")
        self.assertNotEqual(code, 0)
        self.assertIn("--spec", err)

    def test_two_different_ids_refuse(self):
        code, err = self.run_main("parallel", "1", "--spec", "2")
        self.assertNotEqual(code, 0)
        self.assertIn("differs", err)


if __name__ == "__main__":
    unittest.main()


class RootOption(unittest.TestCase):
    """`--root` after the verb: `status`, `show` and `section` read that repository from any cwd."""

    def test_the_three_read_verbs_parse_a_verb_level_root(self):
        for verb in ("status", "show", "section"):
            self.assertEqual(parse(verb, "1192", "--root", "/r").root, "/r")

    def test_a_verb_level_root_wins_over_the_global_one(self):
        self.assertEqual(parse("--root", "/a", "status", "1", "--root", "/b").root, "/b")

    def test_the_global_root_survives_when_the_verb_has_none(self):
        self.assertEqual(parse("--root", "/a", "status", "1").root, "/a")

    def test_no_root_at_all_leaves_the_cwd_to_decide(self):
        self.assertIsNone(parse("status", "1").root)

    def test_status_reads_the_named_repository_from_another_cwd(self):
        import _paths
        cq = os.path.join(os.path.dirname(os.path.abspath(_paths.__file__)),
                          "..", "assets", "bin", "cq")
        repo = os.path.abspath(os.path.join(os.path.dirname(cq), "..", "..", "..", ".."))

        def code(*extra, cwd):
            proc = subprocess.run([sys.executable, cq, "specs", "status", "--spec", "1", *extra,
                                   "--json"], cwd=cwd, capture_output=True, text=True)
            self.assertNotIn("unrecognized arguments", proc.stderr)
            return json.loads(proc.stdout).get("code")

        with tempfile.TemporaryDirectory() as other:
            subprocess.run(["git", "init", "-q", other], check=True)
            self.assertEqual(code(cwd=other), "sp-provider-unknown")
            self.assertNotEqual(code("--root", repo, cwd=other), "sp-provider-unknown")
