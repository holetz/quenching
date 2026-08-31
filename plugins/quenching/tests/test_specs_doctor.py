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
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.base import BackendRefusal
from quenching.common.config import load_config as load_envelope
from quenching.specs.commands import doctor as doctor_mod
from quenching.specs.commands.doctor import cmd_doctor
from quenching.specs.commands.output import Emitter
from quenching.specs.config import load_config as load_specs_config
from quenching.ops import config as ops_config_module
from quenching.ops.config import load_ops_config
from quenching.proof import config as proof_config_module
from quenching.proof.config import load_proof_config
from quenching.git import base as git_config_module


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
            cfg = {"backend": "github", "unknownBackend": None, "unknownKeys": [],
                   "unknownFanoutMinComplexity": None, "legacyPath": None,
                   "unparseable": None}
            with mock.patch.object(doctor_mod, "open_github_backend",
                                   lambda _root: (backend, {})), \
                    mock.patch.object(doctor_mod, "load_config", return_value=cfg), \
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


class ConfigMigrationMatrix(unittest.TestCase):
    """Every pre-envelope shape refuses before a front can interpret a flat declaration."""

    def _write(self, document: dict) -> str:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = directory.name
        os.makedirs(os.path.join(root, ".claude"))
        with open(os.path.join(root, ".claude", "quenching.json"), "w") as handle:
            json.dump(document, handle)
        return root

    def test_pure_flat_configuration_names_every_key_and_destination(self):
        root = self._write({"opsRoot": "scripts", "proofRoot": "tests"})
        envelope = load_envelope(root, detect_provider_info=False)

        refusal = envelope["migrationRefusal"]
        self.assertEqual(refusal["code"], "sp-config-unscoped")
        self.assertEqual(refusal["exit"], 2)
        self.assertEqual(refusal["shape"], "flat")
        self.assertEqual(refusal["keys"], ["opsRoot", "proofRoot"])
        self.assertEqual(refusal["destinations"], [
            {"key": "opsRoot", "namespace": "ops"},
            {"key": "proofRoot", "namespace": "proof"},
        ])
        self.assertIn("`opsRoot` → `ops`", refusal["message"])
        self.assertIn("`proofRoot` → `proof`", refusal["message"])
        self.assertIn("move every listed key", refusal["remedy"])

    def test_mixed_configuration_refuses_and_does_not_merge_the_two_shapes(self):
        root = self._write({
            "ops": {"opsRoot": "scripts", "router": "pyproject.toml"},
            "opsRoot": "old-scripts",
        })
        envelope = load_envelope(root, detect_provider_info=False)
        self.assertEqual(envelope["migrationRefusal"]["shape"], "mixed")
        self.assertEqual(envelope["migrationRefusal"]["keys"], ["opsRoot"])
        self.assertEqual(envelope["ops"]["opsRoot"], "scripts")

        config, error = load_ops_config(root)
        self.assertIsNone(config)
        self.assertEqual(error["code"], "sp-config-unscoped")
        self.assertEqual(error["exit"], 2)

    def test_namespaced_configuration_resolves_each_front_without_cross_front_leakage(self):
        root = self._write({
            "backend": "github",
            "shared": {"worktreeSetup": "make setup"},
            "specs": {"fanoutMinComplexity": "low"},
            "ops": {"opsRoot": "scripts", "router": "pyproject.toml"},
            "proof": {"proofRoot": "tests", "measuredRoots": ["src"]},
        })
        envelope = load_envelope(root, detect_provider_info=False)
        self.assertIsNone(envelope["migrationRefusal"])
        self.assertEqual(envelope["unknownNamespaces"], [])

        specs = load_specs_config(root, detect_provider_info=False)
        self.assertEqual(specs["fanoutMinComplexity"], "low")
        self.assertEqual(specs["worktreeSetup"], "make setup")
        self.assertNotIn("opsRoot", specs)

        ops, ops_error = load_ops_config(root)
        self.assertEqual(ops_error, {})
        self.assertEqual(ops["declaredOpsRoot"], "scripts")

        proof, proof_error = load_proof_config(root)
        self.assertEqual(proof_error, {})
        self.assertEqual(proof["declaredProofRoot"], "tests")

    def test_specs_adapter_carries_flat_migration_refusal_without_using_the_legacy_value(self):
        root = self._write({"specsBranch": "legacy"})
        specs = load_specs_config(root, detect_provider_info=False)
        self.assertEqual(specs["specsBranch"], "specs")
        self.assertEqual(specs["migrationRefusal"]["code"], "sp-config-unscoped")
        self.assertEqual(specs["migrationRefusal"]["exit"], 2)

    def test_ops_proof_and_git_import_common_configuration_not_specs_configuration(self):
        for module in (ops_config_module, proof_config_module, git_config_module):
            with self.subTest(module=module.__name__):
                source = Path(module.__file__).read_text(encoding="utf-8")
                self.assertIn("quenching.common.config", source)
                self.assertNotIn("quenching.specs.config", source)

    def test_unknown_namespace_is_reported_without_being_treated_as_a_front_declaration(self):
        root = self._write({"experimental": {"opsRoot": "scripts"}})
        envelope = load_envelope(root, detect_provider_info=False)
        self.assertEqual(envelope["unknownNamespaces"], ["experimental"])
        self.assertEqual(envelope["migrationRefusal"], None)
        config, error = load_ops_config(root)
        self.assertIsNone(config)
        self.assertEqual(error["code"], "op-config-missing")

    def test_invalid_namespace_shape_is_not_a_flat_fallback(self):
        root = self._write({"ops": ["scripts", "pyproject.toml"]})
        envelope = load_envelope(root, detect_provider_info=False)
        self.assertEqual(envelope["invalidNamespaces"], ["ops"])
        self.assertEqual(envelope["migrationRefusal"], None)
        config, error = load_ops_config(root)
        self.assertIsNone(config)
        self.assertEqual(error["code"], "op-config-missing")

    def test_proof_adapter_returns_the_same_exit_two_migration_refusal(self):
        root = self._write({"proofRoot": "tests"})
        config, error = load_proof_config(root)
        self.assertIsNone(config)
        self.assertEqual(error["code"], "sp-config-unscoped")
        self.assertEqual(error["exit"], 2)


if __name__ == "__main__":
    unittest.main()
