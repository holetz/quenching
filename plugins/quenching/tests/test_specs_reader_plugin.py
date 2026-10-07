"""`plugins/quenching-specs-reader` — the read-only sibling a target enables alone.

Three claims are load-bearing and each goes silently false without a test:

- the reader registers ONE command, or enabling it alone buys the target nothing;
- `cq-specs-read` never writes: the allowlist refuses write verbs and write flags before any
  provider call, and the runtime block refuses every backend write path even if a read verb
  grew a side effect;
- the generated payload is byte-identical to `plugins/quenching`, or the reader runs a package
  nobody edits.

The write block runs in a subprocess: it patches backend classes, and the discovery run shares
one interpreter with every other suite that writes through `MemoryBackend`.
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
READER = REPO_ROOT / "plugins" / "quenching-specs-reader"
SHIM = READER / "bin" / "cq-specs-read"
SYNC = REPO_ROOT / "scripts" / "sync_specs_reader_plugin.py"


def run_shim(*argv, env=None):
    return subprocess.run([sys.executable, str(SHIM), *argv], capture_output=True, text=True,
                          env={**os.environ, **(env or {})})


class TheReaderSurface(unittest.TestCase):
    def test_it_registers_exactly_one_command(self):
        commands = sorted(p.relative_to(READER / "commands").as_posix()
                          for p in (READER / "commands").rglob("*.md"))
        self.assertEqual(["read.md"], commands)

    def test_its_entry_point_is_executable_and_not_named_cq(self):
        self.assertTrue(os.access(SHIM, os.X_OK), SHIM)
        self.assertEqual(["cq-specs-read"], sorted(p.name for p in (READER / "bin").iterdir()
                                                  if p.name != "__pycache__"))

    def test_the_marketplace_pins_its_version_to_the_source(self):
        marketplace = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json")
                                 .read_text(encoding="utf-8"))
        entry = next(p for p in marketplace["plugins"] if p["name"] == "quenching-specs-reader")
        self.assertEqual("./plugins/quenching-specs-reader", entry["source"])
        version = (REPO_ROOT / "plugins" / "quenching" / "VERSION").read_text().strip()
        self.assertEqual(version, entry["version"])

    def test_its_payload_is_in_lockstep_with_the_source(self):
        run = subprocess.run([sys.executable, str(SYNC), "--check"], capture_output=True,
                             text=True)
        self.assertEqual(0, run.returncode, run.stderr)
        version = (REPO_ROOT / "plugins" / "quenching" / "VERSION").read_text().strip()
        manifest = json.loads((READER / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(version, manifest["version"])

    def test_it_carries_only_the_slice_specs_imports(self):
        package = READER / "assets" / "bin" / "quenching"
        self.assertEqual(["common", "specs"], sorted(p.name for p in package.iterdir()))
        import re
        for path in package.rglob("*.py"):
            for pillar in re.findall(r"^\s*(?:from|import) quenching\.(\w+)", path.read_text(),
                                    re.M):
                self.assertIn(pillar, ("common", "specs"), path)


class TheAllowlist(unittest.TestCase):
    def test_help_answers(self):
        run = run_shim("--help")
        self.assertEqual(0, run.returncode, run.stderr)
        self.assertIn("cq-specs-read", run.stdout)

    def test_every_write_verb_is_refused_before_any_provider_call(self):
        # A root that does not exist proves the refusal happens before root resolution.
        for verb in ("new", "task", "record", "promote", "discover", "verification", "tags",
                     "assignee", "start", "target", "migrate", "release", "parallel",
                     "validate", "doctor", "find", "export"):
            with self.subTest(verb=verb):
                run = run_shim("--root", "/nonexistent", verb, "1", "--json")
                self.assertEqual(2, run.returncode, run.stdout)
                self.assertEqual("sp-read-only", json.loads(run.stdout)["code"])

    def test_section_write_and_fold_are_refused_in_every_spelling(self):
        for flag in ("--write", "--wri", "--w", "--fold", "--fo", "--fold=Stray"):
            with self.subTest(flag=flag):
                run = run_shim("--root", "/nonexistent", "section", "1", "Problem", flag,
                               "--json")
                self.assertEqual(2, run.returncode, run.stdout)
                self.assertEqual("sp-read-only", json.loads(run.stdout)["code"])

    def test_a_missing_checkout_is_a_refusal(self):
        run = run_shim("list", "--json", env={"QUENCHING_SPECS_ROOT": "/nonexistent/checkout"})
        self.assertEqual(2, run.returncode, run.stdout)
        self.assertEqual("sp-read-root", json.loads(run.stdout)["code"])

    def test_a_read_verb_reaches_the_specs_pillar(self):
        # A git checkout with no provider remote: the specs pillar itself refuses, with no
        # network call, which proves the verb was dispatched and the root was honoured.
        with tempfile.TemporaryDirectory() as root:
            subprocess.run(["git", "init", "-q", root], check=True)
            run = run_shim("--root", root, "list", "--json")
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertEqual("sp-provider-unknown", json.loads(run.stdout)["code"])


class TheRuntimeWriteBlock(unittest.TestCase):
    PROBE = """
import importlib.machinery, importlib.util, json, sys
sys.dont_write_bytecode = True
loader = importlib.machinery.SourceFileLoader("cq_specs_read", sys.argv[1])
spec = importlib.util.spec_from_loader("cq_specs_read", loader)
shim = importlib.util.module_from_spec(spec)
loader.exec_module(shim)
sys.path.insert(0, shim.PACKAGE_ROOT)
shim.block_writes()
from quenching.specs.backends.base import BackendRefusal, SpecBackend
from quenching.specs.backends.github import GitHubBackend
from quenching.specs.backends.azure import AzureBoardsBackend
from quenching.specs.backends.memory import MemoryBackend
refused = {}
for cls in (GitHubBackend, AzureBoardsBackend, MemoryBackend):
    for name in ("write_spec", "create_spec", "move_spec"):
        try:
            getattr(cls, name)(object.__new__(cls), {}, "")
            refused[f"{cls.__name__}.{name}"] = None
        except BackendRefusal as exc:
            refused[f"{cls.__name__}.{name}"] = exc.err["code"]
try:
    GitHubBackend._write_api(object.__new__(GitHubBackend), "x", "PATCH", "p", {})
    refused["GitHubBackend._write_api"] = None
except BackendRefusal as exc:
    refused["GitHubBackend._write_api"] = exc.err["code"]
print(json.dumps(refused))
"""

    def test_every_backend_write_path_refuses(self):
        run = subprocess.run([sys.executable, "-c", self.PROBE, str(SHIM)], capture_output=True,
                             text=True)
        self.assertEqual(0, run.returncode, run.stderr)
        refused = json.loads(run.stdout)
        self.assertEqual(10, len(refused))
        self.assertEqual({"sp-read-only"}, set(refused.values()), refused)


if __name__ == "__main__":
    unittest.main()
