"""`cmd_doctor`'s `github` block — the diagnostic half of "an empty listing is two states".

THE ONE THING THIS FILE EXISTS TO PROVE is that `doctor` keeps completing. Its whole contract
is to reach the end and report; a listing that refuses at the read choke point must arrive
here as a finding, and the suspicion that cannot be proved must arrive as `warn` and never as
an error. Both ways of getting that wrong are invisible in ordinary use — the first turns
`doctor` itself into an exit-2 exactly when a human is asking what is wrong, and the second
fails conformant repositories over a state that is legitimate.

Self-contained: `open_github_backend` is patched to a stub, so no network, no `gh`, no
repository. The config is a real file in a temp directory, because the block is gated on the
declared backend and a stubbed `load_config` would stop proving that gate.
"""
import argparse
import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.commands import doctor as doctor_mod
from quenching.specs.commands.doctor import cmd_doctor
from quenching.specs.commands.output import Emitter


class _StubBackend:
    """What `cmd_doctor` asks of the github backend, and nothing else: the specs it lists, the
    open-issue count that corroborates a zero, and the repository it names in the message."""

    repo = "owner/repo"

    def __init__(self, rows: list | None = None, raises: dict | None = None,
                 open_issues: int | None = None) -> None:
        self._rows = rows or []
        self._raises = raises
        self.open_issues = open_issues

    def list_specs(self, phase: str | None = None) -> list:
        if self._raises:
            raise BackendRefusal(self._raises)
        return self._rows


class GithubDoctorFindings(unittest.TestCase):

    def _findings(self, backend: _StubBackend) -> tuple[list[dict], int]:
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, ".claude"))
            with open(os.path.join(tmp, ".claude", "quenching.json"), "w") as fh:
                json.dump({"backend": "github"}, fh)
            # The SPECS root, which under an external backend is a path that does not exist —
            # `find_repo_root` then resolves `.claude/` from its parent, exactly as it does
            # in a real repository on this backend.
            root = os.path.join(tmp, ".specs")
            buf = io.StringIO()
            with mock.patch.object(doctor_mod, "open_github_backend",
                                   lambda _root: (backend, {})), \
                    contextlib.redirect_stdout(buf):
                code = cmd_doctor(argparse.Namespace(json=True), root, Emitter())
        return json.loads(buf.getvalue())["findings"], code

    def test_zero_specs_with_open_issues_is_a_warn_and_names_the_number(self):
        findings, code = self._findings(_StubBackend(rows=[], open_issues=38))
        suspect = [f for f in findings if f["code"] == "sp-gh-listing-suspect"]
        self.assertEqual(len(suspect), 1)
        self.assertEqual(suspect[0]["severity"], "warn")
        self.assertIn("38 open issue(s)", suspect[0]["message"])
        self.assertTrue(suspect[0]["remedy"])
        self.assertEqual(code, 0, "a suspicion that cannot be proved must not fail the "
                                  "diagnostic — warn is the whole severity decision")

    def test_zero_specs_with_no_open_issues_is_not_a_finding(self):
        # Nothing corroborates the zero, so there is nothing to say. A finding here would
        # fire on every repository that has not adopted the front yet.
        findings, _ = self._findings(_StubBackend(rows=[], open_issues=0))
        self.assertEqual([f["code"] for f in findings], [])

    def test_a_front_that_read_specs_is_never_reported_suspect(self):
        findings, _ = self._findings(_StubBackend(rows=[{"slug": "alpha"}], open_issues=38))
        self.assertEqual([f["code"] for f in findings], [])

    def test_a_refusing_listing_becomes_a_finding_and_the_diagnostic_still_completes(self):
        # The exact evidence that is an exit-2 at the read choke point. Here it is a `warn`
        # and `cmd_doctor` returns, which is the difference between a diagnostic and a read.
        refusal = {"code": "sp-gh-empty-listing", "exit": 2,
                   "message": "the listing came back with zero pages",
                   "remedy": "re-run the command"}
        findings, code = self._findings(_StubBackend(raises=refusal))
        self.assertEqual([f["code"] for f in findings], ["sp-gh-empty-listing"])
        self.assertEqual(findings[0]["severity"], "warn")
        self.assertEqual(code, 0)

    def test_a_refusal_with_no_remedy_of_its_own_still_gets_one(self):
        # `gh_refusal`'s three classifications carry no `remedy` key, and they reach this
        # block too — a KeyError here would crash the command it is meant to keep alive.
        findings, code = self._findings(_StubBackend(
            raises={"code": "sp-gh-api-error", "exit": 2, "message": "gh said: HTTP 503"}))
        self.assertTrue(findings[0]["remedy"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
