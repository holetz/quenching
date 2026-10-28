"""Executable proofs for the configuration provider seam: the file stays the default read."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common import config as cfg


class Double:
    """A provider that holds the envelope in memory, with no file on disk."""

    name = "double"

    def __init__(self, document):
        self.document = document

    def read(self, repo_root):
        return self.document, {"name": self.name, "path": "double://envelope",
                               "present": True, "unparseable": None}


class ConfigProviderSeam(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name) / "repo"
        (self.repo / ".claude").mkdir(parents=True)
        user = pathlib.Path(tmp.name) / "user.json"
        env = mock.patch.dict(os.environ, {cfg.USER_CONFIG_ENV: str(user)})
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop(cfg.PROVIDER_ENV, None)
        self.addCleanup(cfg.unregister_provider, "double")

    def _file(self, text):
        (self.repo / ".claude" / "quenching.json").write_text(text)

    def _load(self):
        return cfg.load_config(str(self.repo), detect_provider_info=False)

    def test_home_is_read_before_the_legacy_file_and_shadows_it(self):
        self._file(json.dumps({"backend": "github"}))
        home = self.repo / ".agents" / "quenching.json"
        home.parent.mkdir()
        home.write_text(json.dumps({"backend": "git"}))
        out = self._load()
        self.assertEqual(out["path"], str(home))
        self.assertEqual(out["data"]["backend"], "git")
        self.assertEqual(out["shadowedPath"], str(self.repo / ".claude" / "quenching.json"))

    def test_legacy_file_is_read_when_the_home_is_absent(self):
        self._file(json.dumps({"backend": "git"}))
        out = self._load()
        self.assertEqual(out["path"], str(self.repo / ".claude" / "quenching.json"))
        self.assertIsNone(out["shadowedPath"])

    def test_file_present(self):
        self._file(json.dumps({"backend": "git", "shared": {"worktreeSetup": "make"}}))
        out = self._load()
        self.assertEqual((out["source"], out["present"], out["unparseable"]), ("file", True, None))
        self.assertEqual(cfg.namespace(out, "shared"), {"worktreeSetup": "make"})
        self.assertEqual(out["data"]["backend"], "git")

    def test_file_absent(self):
        out = self._load()
        self.assertEqual((out["source"], out["present"], out["data"]), ("file", False, {}))
        self.assertIsNone(out["providerRefusal"])

    def test_file_unparseable(self):
        self._file("{nope")
        out = self._load()
        self.assertTrue(out["present"])
        self.assertTrue(out["unparseable"])
        self.assertEqual(out["data"], {})

    def test_file_not_an_object(self):
        self._file("[1]")
        self.assertIn("not an object", self._load()["unparseable"])

    def test_flat_legacy_still_refused(self):
        self._file(json.dumps({"worktreeSetup": "make"}))
        out = self._load()
        self.assertEqual(out["legacyKeys"], ["worktreeSetup"])
        self.assertEqual(out["migrationRefusal"]["code"], "sp-config-unscoped")

    def test_double_with_no_file_on_disk(self):
        cfg.register_provider(Double({"backend": "git", "specs": {"subjects": {"a": 1}}}))
        with mock.patch.dict(os.environ, {cfg.PROVIDER_ENV: "double"}):
            out = self._load()
        self.assertFalse((self.repo / ".claude" / "quenching.json").exists())
        self.assertEqual((out["source"], out["present"], out["path"]),
                         ("double", True, "double://envelope"))
        self.assertEqual(cfg.namespace(out, "specs"), {"subjects": {"a": 1}})

    def test_unknown_provider_refuses_and_names_the_registered(self):
        self._file(json.dumps({"shared": {"worktreeSetup": "make"}}))
        with mock.patch.dict(os.environ, {cfg.PROVIDER_ENV: "service"}):
            out = self._load()
        refusal = out["providerRefusal"]
        self.assertEqual((refusal["code"], refusal["exit"]), ("cq-config-provider-unknown", 2))
        self.assertEqual(refusal["registered"], ["file"])
        self.assertFalse(out["present"])
        self.assertEqual(cfg.namespace(out, "shared"), {})

    def test_file_cannot_be_unregistered(self):
        cfg.unregister_provider("file")
        provider, refusal = cfg.active_provider()
        self.assertEqual(provider.name, "file")
        self.assertIsNone(refusal)


class ConfigVerbs(ConfigProviderSeam):
    def _run(self, *argv):
        from quenching.config import main
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--root", str(self.repo), *argv])
        return code, out.getvalue(), err.getvalue()

    def test_export_file(self):
        self._file(json.dumps({"backend": "git", "shared": {"worktreeSetup": "make"}}))
        code, out, _ = self._run("export", "--json")
        payload = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual((payload["provider"], payload["document"]["shared"]),
                         ("file", {"worktreeSetup": "make"}))

    def test_export_double_with_no_file(self):
        cfg.register_provider(Double({"backend": "git"}))
        with mock.patch.dict(os.environ, {cfg.PROVIDER_ENV: "double"}):
            code, out, _ = self._run("export", "--json")
        self.assertEqual((code, json.loads(out)["document"]), (0, {"backend": "git"}))

    def test_export_absent_refuses(self):
        code, out, _ = self._run("export", "--json")
        self.assertEqual((code, json.loads(out)["code"]), (2, "cq-config-absent"))

    def test_export_unknown_provider_refuses(self):
        with mock.patch.dict(os.environ, {cfg.PROVIDER_ENV: "service"}):
            code, out, _ = self._run("export", "--json")
        self.assertEqual((code, json.loads(out)["code"]), (2, "cq-config-provider-unknown"))

    def test_init_and_check_refuse_under_a_non_file_provider(self):
        cfg.register_provider(Double({"backend": "git"}))
        with mock.patch.dict(os.environ, {cfg.PROVIDER_ENV: "double"}):
            for verb in ("init", "check"):
                code, out, _ = self._run(verb, "--json")
                self.assertEqual((code, json.loads(out)["code"]), (2, "cq-config-provider-not-file"))
        self.assertFalse((self.repo / ".claude" / "quenching.json").exists())


if __name__ == "__main__":
    unittest.main()
