"""The upgrade check's disposable marketplace source keeps its loose objects while Codex clones it."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import _paths  # noqa: F401

REPO = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("check_codex_upgrade", REPO / "scripts/check_codex_upgrade.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

# Synchronous auto-gc on every commit: the legacy trigger at its lowest threshold, plus the
# geometric strategy Git 2.54+ uses by default, so the race becomes a deterministic deletion.
FORCED_GC = {"gc.auto": "1", "gc.autoDetach": "false", "maintenance.autoDetach": "false",
             "maintenance.strategy": "geometric"}


def git(repo: Path, *args: str, env: dict | None = None) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], env=env, check=True,
                          capture_output=True, text=True).stdout


class DisposableSourceRepository(unittest.TestCase):
    def commit_many(self, config: tuple) -> dict:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name)
        git(repo, "init", "-q", "-b", "main")
        for key, value in config:
            git(repo, "config", key, value)
        for n in range(2000):
            (repo / f"f{n}.txt").write_text(f"object {n}\n")
        env = {**os.environ, "GIT_CONFIG_COUNT": str(len(FORCED_GC))}
        for i, (key, value) in enumerate(FORCED_GC.items()):
            env.update({f"GIT_CONFIG_KEY_{i}": key, f"GIT_CONFIG_VALUE_{i}": value})
        git(repo, "add", "-A", env=env)
        git(repo, "commit", "-qm", "Previously published Codex package", env=env)
        return dict(line.split(": ") for line in git(repo, "count-objects", "-v").splitlines())

    def test_forced_auto_gc_packs_loose_objects_without_the_source_config(self):
        identity = tuple(item for item in check.SOURCE_GIT_CONFIG
                         if item[0] in ("user.name", "user.email", "commit.gpgsign"))
        objects = self.commit_many(identity)
        self.assertEqual(objects["count"], "0", "the forced environment must delete loose objects")

    def test_source_config_keeps_every_loose_object_under_forced_auto_gc(self):
        objects = self.commit_many(check.SOURCE_GIT_CONFIG)
        self.assertEqual(objects["in-pack"], "0")
        self.assertEqual(objects["count"], "2002")  # 2000 blobs, one tree, one commit


if __name__ == "__main__":
    unittest.main()
