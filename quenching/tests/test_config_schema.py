"""`quenching.config.schema` — one registry of every configuration key, held equal to the code that
reads the keys and to `plugin-configuration.md`'s table."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import re
import subprocess
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.config import main as config_main
from quenching.config.effective import DEFAULT_BLOCKS
from quenching.config.schema import CATEGORIES, REGISTRY, SCOPES, TYPES, validate
from quenching.config.seed import flatten, seed_document
from quenching.git.conventions import GIT_CONVENTION_KEYS
from quenching.ops.config import OPS_CONFIG_KEYS
from quenching.specs.config import BRANCH_CONFIG_KEYS, CONFIG_KEYS

TABLE = (pathlib.Path(__file__).resolve().parent.parent / "references" / "specs-align"
         / "plugin-configuration.md").read_text()


def covered(key: str) -> bool:
    """`key` is a registry entry, or a leaf inside a read-only catalog the registry holds."""
    parts = key.split(".")
    return any(".".join(parts[:n]) in REGISTRY for n in range(1, len(parts) + 1))


def table_keys() -> list[str]:
    section = TABLE[TABLE.index("| Key |"):]
    rows = [line for line in section.splitlines()[2:] if line.startswith("| ")]
    keys = []
    for row in rows:
        first = row.split(" | ")[0]
        keys += re.findall(r"`([A-Za-z.]+)`", first)
    return keys


class EveryEntryIsComplete(unittest.TestCase):
    def test_each_entry_has_copy_in_both_languages_a_category_and_a_scope(self):
        categories = {cid for cid, _en, _pt in CATEGORIES}
        for key, entry in REGISTRY.items():
            with self.subTest(key=key):
                self.assertIn(entry["scope"], SCOPES)
                self.assertIn(entry["category"], categories)
                self.assertIn(entry["type"], TYPES)
                for lang in ("en", "pt-BR"):
                    self.assertTrue(entry["copy"][lang]["title"].strip())
                    self.assertTrue(entry["copy"][lang]["summary"].strip())
                if entry["type"] == "enum" and entry["default"] is not None:
                    self.assertIn(entry["default"], entry["choices"])

    def test_every_category_holds_a_key(self):
        used = {e["category"] for e in REGISTRY.values()}
        self.assertEqual(used, {cid for cid, _en, _pt in CATEGORIES})


class TheRegistryCoversTheReaders(unittest.TestCase):
    def test_the_seed_and_the_default_blocks(self):
        for leaf in flatten(seed_document(".")):
            self.assertTrue(covered(leaf), leaf)
        for (ns, key), defaults in DEFAULT_BLOCKS.items():
            for leaf in flatten(defaults, f"{ns}.{key}"):
                self.assertTrue(covered(leaf), leaf)

    def test_the_namespace_adapters(self):
        specs = {k for k in CONFIG_KEYS if k != "backend"} | set(BRANCH_CONFIG_KEYS)
        shared = {"worktreeSetup", "sharedPaths", "hooks", "profiles"}
        for key in specs - shared:
            self.assertTrue(covered(f"specs.{key}"), key)
        for key in shared | {"regenerablePaths", "contextBudgets", "okfValidate", "workHost",
                             "worktreeSlots", "autonomy", "codex", "gitConventions"}:
            self.assertTrue(any(k.startswith(f"shared.{key}") for k in REGISTRY), key)
        for key in GIT_CONVENTION_KEYS:
            self.assertIn(f"shared.gitConventions.{key}", REGISTRY)
        for key in OPS_CONFIG_KEYS:
            self.assertIn(f"ops.{key}", REGISTRY)
        self.assertIn("backend", REGISTRY)


class TheTableMatches(unittest.TestCase):
    def test_table_rows_and_registry_name_the_same_keys(self):
        rows = table_keys()
        for key in rows:
            self.assertTrue(key in REGISTRY or any(k.startswith(key + ".") for k in REGISTRY),
                            f"table row {key} has no registry entry")
        for key in REGISTRY:
            self.assertTrue(any(key == row or key.startswith(row + ".") for row in rows),
                            f"registry key {key} has no table row")


class Validation(unittest.TestCase):
    def test_types_ranges_and_catalogs(self):
        self.assertEqual(validate("shared.worktreeSlots.max", 6), (6, None))
        self.assertIsNotNone(validate("shared.worktreeSlots.max", 0)[1])
        self.assertIsNotNone(validate("shared.worktreeSlots.max", True)[1])
        self.assertIsNotNone(validate("shared.autonomy.merge", "sometimes")[1])
        self.assertIsNotNone(validate("specs.subjects", {})[1])
        self.assertIsNotNone(validate("nope.key", 1)[1])
        self.assertEqual(validate("shared.sharedPaths", ["a"]), (["a"], None))


class SchemaVerb(unittest.TestCase):
    def test_schema_json_lists_categories_and_keys(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(config_main(["schema", "--json"]), 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(len(payload["categories"]), len(CATEGORIES))
        self.assertEqual({k["key"] for k in payload["keys"]}, set(REGISTRY))



class SetAndUnset(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = os.path.realpath(tmp.name)
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        os.makedirs(os.path.join(self.repo, ".agents"))
        self.project = os.path.join(self.repo, ".agents", "quenching.json")
        self.local = os.path.join(self.repo, ".agents", "quenching.local.json")
        with open(self.project, "w") as fh:
            json.dump({"backend": "git", "shared": {"zeta": 1, "autonomy": {"merge": "never"},
                                                    "alpha": 2}}, fh)
        patch = mock.patch.dict(os.environ, {"QUENCHING_USER_CONFIG":
                                             os.path.join(self.repo, "no-user.json")})
        patch.start()
        self.addCleanup(patch.stop)

    def cq(self, *argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            code = config_main(["--root", self.repo, *argv, "--json"])
        return code, json.loads(buf.getvalue())

    def test_set_validates_the_type_and_keeps_every_other_key_in_order(self):
        code, out = self.cq("set", "shared.autonomy.maxWorkers", "5", "--layer", "project")
        self.assertEqual(code, 0, out)
        with open(self.project) as fh:
            doc = json.load(fh)
        self.assertEqual(list(doc["shared"]), ["zeta", "autonomy", "alpha"])
        self.assertEqual(doc["shared"]["autonomy"], {"merge": "never", "maxWorkers": 5})
        code, out = self.cq("set", "shared.autonomy.maxWorkers", "nine", "--layer", "project")
        self.assertEqual(code, 2)
        self.assertEqual(out["code"], "cq-config-value-invalid")

    def test_set_refuses_unknown_keys_and_project_keys_in_the_local_layer(self):
        self.assertEqual(self.cq("set", "shared.nope", "1", "--layer", "local")[1]["code"],
                         "cq-config-key-unknown")
        self.assertEqual(self.cq("set", "shared.worktreeSetup", "make",
                                 "--layer", "local")[1]["code"], "cq-config-scope-project")
        self.assertFalse(os.path.exists(self.local))

    def test_the_first_local_write_excludes_the_file_from_git_once(self):
        code, out = self.cq("set", "shared.worktreeSlots.max", "6", "--layer", "local")
        self.assertEqual(code, 0, out)
        self.assertTrue(out["excluded"])
        self.cq("set", "shared.worktreeSlots.min", "2", "--layer", "local")
        with open(os.path.join(self.repo, ".git", "info", "exclude")) as fh:
            self.assertEqual(fh.read().count("/.agents/quenching.local.json"), 1)
        status = subprocess.run(["git", "-C", self.repo, "status", "--porcelain",
                                 "--untracked-files=all"], capture_output=True, text=True).stdout
        self.assertNotIn("quenching.local.json", status)
        with open(self.local) as fh:
            self.assertEqual(json.load(fh), {"shared": {"worktreeSlots": {"max": 6, "min": 2}}})

    def test_unset_removes_the_key_and_the_blocks_it_empties(self):
        self.cq("set", "shared.worktreeSlots.max", "6", "--layer", "local")
        code, out = self.cq("unset", "shared.worktreeSlots.max", "--layer", "local")
        self.assertEqual((code, out["changed"], out["previous"]), (0, True, 6))
        with open(self.local) as fh:
            self.assertEqual(json.load(fh), {})

    def test_schema_values_show_the_layer(self):
        self.cq("set", "shared.worktreeSlots.max", "6", "--layer", "local")
        _code, out = self.cq("schema", "--values")
        self.assertEqual(out["values"]["shared.worktreeSlots.max"], {"value": 6,
                                                                     "source": "local"})
        self.assertEqual(out["values"]["shared.autonomy.merge"]["source"], "repository")


if __name__ == "__main__":
    unittest.main()
