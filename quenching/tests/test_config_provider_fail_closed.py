"""An unknown configuration provider refuses (exit 2) instead of failing open."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
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
from quenching.specs import backends

CQ = pathlib.Path(__file__).resolve().parents[1] / "assets" / "bin" / "cq"


class UnknownProviderFailsClosed(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name) / "repo"
        (self.repo / ".claude").mkdir(parents=True)
        (self.repo / ".claude" / "quenching.json").write_text(json.dumps({"backend": "git"}))
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.user = str(pathlib.Path(tmp.name) / "user.json")

    def _cq(self, provider, *argv):
        env = {k: v for k, v in os.environ.items() if k != cfg.PROVIDER_ENV}
        env[cfg.USER_CONFIG_ENV] = self.user
        if provider is not None:
            env[cfg.PROVIDER_ENV] = provider
        return subprocess.run([sys.executable, str(CQ), "--root", str(self.repo), *argv],
                              capture_output=True, text=True, env=env, cwd=str(self.repo))

    def test_config_show_refuses(self):
        done = self._cq("nope", "config", "show", "--effective")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("cq-config-provider-unknown", done.stderr)
        self.assertEqual(done.stdout, "")

    def test_specs_status_refuses(self):
        done = self._cq("nope", "specs", "config", "--json")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("cq-config-provider-unknown", done.stderr)

    def test_registered_or_unset_provider_still_reads(self):
        for provider in (None, "file"):
            done = self._cq(provider, "config", "show", "--effective")
            self.assertEqual(done.returncode, 0, done.stderr)

    def test_open_backend_returns_the_refusal(self):
        backends._BACKEND_CACHE.pop(str(self.repo), None)
        with mock.patch.dict(os.environ, {cfg.PROVIDER_ENV: "nope", cfg.USER_CONFIG_ENV: self.user}):
            backend, err = backends.open_backend(str(self.repo))
        self.assertIsNone(backend)
        self.assertEqual((err["code"], err["exit"]), ("cq-config-provider-unknown", 2))


if __name__ == "__main__":
    unittest.main()
