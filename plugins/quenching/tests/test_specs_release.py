"""The version lockstep — `bump_release_artifacts` proved against a disposable tree standing
in for the real artifacts (`RELEASE_ARTIFACTS`) and its changelog gate, never the plugin's own, so this runs
safely on every test run without ever bumping a real version.

Migrated from the pre-refactor specs script's `release_lockstep_failures`. Both directions
matter: agreeing values all move together, and one already-drifted value refuses before
any artifact is touched — kept as two separate cases below rather than folded into one, so
a failure names which direction broke.
"""
import argparse
import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common.io import read_text, write_text
from quenching.common.modules import MANIFEST, load_manifest
from quenching.specs.release import (
    RELEASE_ARTIFACTS,
    _RELEASE_JSON_VERSION_RE,
    _RELEASE_PY_VERSION_RE,
    bump_release_artifacts,
)

# One value per artifact `kind`, each pre-set to the old version the bump must move away from.
PUBLISHED = [m["name"] for m in load_manifest(Path(__file__).resolve().parents[3])["modules"]
             if m["published"]]
KINDS = {
    "plain": "9.9.9\n",
    "json": '{\n  "name": "x",\n  "version": "9.9.9"\n}\n',
    "jsonall": json.dumps({"plugins": [
        {"name": name, "version": "9.9.9"}
        for name in PUBLISHED]}),
    "py": 'VERSION = "9.9.9"  # a comment that must survive the bump\n',
}


class Lockstep(unittest.TestCase):
    def setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.tmp = tmpdir.name
        for rel, kind in RELEASE_ARTIFACTS:
            path = os.path.join(self.tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            write_text(path, KINDS[kind])
        manifest = load_manifest(Path(__file__).resolve().parents[3])
        manifest["modules"] = [m for m in manifest["modules"]
                               if m["published"] or m["path"] == manifest["source"]]
        source = Path(self.tmp) / manifest["source"] / "assets"
        for module in manifest["modules"]:
            plugin = Path(self.tmp) / module["path"] / ".claude-plugin/plugin.json"
            plugin.write_text(json.dumps({"name": module["name"], "version": "9.9.9"}))
            module.pop("generated", None)
            # Principal records name source closures load_manifest checks exist; stand them up empty.
            if "owned" in module:
                support = module["generatedSupport"]
                for package in [*module["owned"]["packages"], *support["packages"]]:
                    (source / "bin/quenching" / package).mkdir(parents=True, exist_ok=True)
                for reference in support["references"]:
                    (source / "references" / reference).mkdir(parents=True, exist_ok=True)
        market = Path(self.tmp) / manifest["marketplace"]
        market.write_text(json.dumps({"plugins": [
            {"name": m["name"], "source": "./" + m["path"], "version": "9.9.9"}
            for m in manifest["modules"] if m["published"]]}))
        for distribution in manifest.get("distributions", []):
            plugin = Path(self.tmp) / distribution["path"] / distribution["pluginManifest"]
            plugin.write_text(json.dumps({"name": distribution["name"], "version": "9.9.9"}))
            catalog = Path(self.tmp) / distribution["marketplace"]
            catalog.parent.mkdir(parents=True, exist_ok=True)
            catalog.write_text(json.dumps({"plugins": [{
                "name": distribution["name"], "source": "./" + distribution["path"],
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools"}]}))
        self.manifest_path = Path(self.tmp) / MANIFEST
        self.manifest_path.write_text(json.dumps(manifest))
        write_text(os.path.join(self.tmp, "CHANGELOG.md"), "# Changelog\n\n## 9.10.0\n")
        self.initial = {rel: read_text(os.path.join(self.tmp, rel)) for rel, _ in RELEASE_ARTIFACTS}

    def test_four_agreeing_artifacts_are_reported_moved(self):
        result = bump_release_artifacts(self.tmp, "9.10.0")
        self.assertTrue(result["ok"], result.get("error"))
        self.assertEqual((result["oldVersion"], result["newVersion"]), ("9.9.9", "9.10.0"))

    def test_the_hud_manifest_moves_with_the_lockstep(self):
        bump_release_artifacts(self.tmp, "9.10.0")
        text = read_text(os.path.join(
            self.tmp, "plugins/quenching-hud/.claude-plugin/plugin.json"))
        self.assertEqual(json.loads(text)["version"], "9.10.0")

    def test_every_artifact_reads_back_the_new_version(self):
        bump_release_artifacts(self.tmp, "9.10.0")
        pattern = {"plain": None, "json": _RELEASE_JSON_VERSION_RE,
                   "jsonall": _RELEASE_JSON_VERSION_RE, "py": _RELEASE_PY_VERSION_RE}
        for rel, kind in RELEASE_ARTIFACTS:
            with self.subTest(artifact=rel):
                text = read_text(os.path.join(self.tmp, rel))
                pat = pattern[kind]
                got = ({text.strip()} if pat is None
                       else {m.group(2) for m in pat.finditer(text)})
                self.assertEqual(got, {"9.10.0"})

    def test_bumping_a_py_artifact_touches_only_the_quoted_value(self):
        # The substitution is a regex on the VERSION line, not a line replacement — a comment
        # riding the same line must survive it.
        bump_release_artifacts(self.tmp, "9.10.0")
        text = read_text(os.path.join(
            self.tmp, "plugins/quenching/assets/bin/quenching/common/version.py"))
        self.assertIn("# a comment that must survive the bump", text)

    def test_a_release_without_a_matching_changelog_entry_is_refused_before_writes(self):
        write_text(os.path.join(self.tmp, "CHANGELOG.md"), "# Changelog\n\n## 9.9.9\n")

        result = bump_release_artifacts(self.tmp, "9.10.0")

        self.assertFalse(result["ok"])
        self.assertIn("CHANGELOG.md", result["error"])
        self.assertIn("9.10.0", result["error"])
        for rel, kind in RELEASE_ARTIFACTS:
            with self.subTest(artifact=rel):
                self.assertEqual(read_text(os.path.join(self.tmp, rel)), self.initial[rel])

    def test_a_lockstep_already_drifted_is_refused_rather_than_compounded(self):
        # Precondition: one artifact disagreeing with the rest BEFORE the bump is a refusal,
        # not a fifth value folded into the compare.
        write_text(os.path.join(self.tmp, "plugins/quenching/VERSION"), "9.9.8\n")
        result = bump_release_artifacts(self.tmp, "9.10.0")
        self.assertFalse(result["ok"])

    def test_a_drifted_lockstep_is_refused_before_any_artifact_is_written(self):
        write_text(os.path.join(self.tmp, "plugins/quenching/VERSION"), "9.9.8\n")
        bump_release_artifacts(self.tmp, "9.10.0")
        for rel, kind in RELEASE_ARTIFACTS:
            if rel == "plugins/quenching/VERSION":
                continue
            with self.subTest(artifact=rel):
                self.assertEqual(read_text(os.path.join(self.tmp, rel)), self.initial[rel])

    def test_a_marketplace_entry_without_a_version_is_refused(self):
        path = os.path.join(self.tmp, ".claude-plugin/marketplace.json")
        write_text(path, '{"plugins": [{"name": "a", "version": "9.9.9"}, {"name": "b"}]}')
        self.assertFalse(bump_release_artifacts(self.tmp, "9.10.0")["ok"])

    def add_published_consumer(self):
        manifest = json.loads(self.manifest_path.read_text())
        manifest["modules"].append({"name": "quenching-extra", "path": "plugins/quenching-extra",
                                    "published": True, "versionFile": True, "cqPathOwner": False})
        self.manifest_path.write_text(json.dumps(manifest))
        folder = Path(self.tmp) / "plugins/quenching-extra"
        (folder / ".claude-plugin").mkdir(parents=True)
        (folder / "VERSION").write_text(KINDS["plain"])
        (folder / ".claude-plugin/plugin.json").write_text(json.dumps({
            "name": "quenching-extra", "version": "9.9.9"}))
        market_path = Path(self.tmp) / ".claude-plugin/marketplace.json"
        market = json.loads(market_path.read_text())
        market["plugins"].append({"name": "quenching-extra", "source": "./plugins/quenching-extra",
                                 "version": "9.9.9"})
        market_path.write_text(json.dumps(market))
        return folder

    def test_target_manifest_adds_release_surfaces_without_changing_bundled_export(self):
        folder = self.add_published_consumer()
        result = bump_release_artifacts(self.tmp, "9.10.0")
        self.assertTrue(result["ok"], result.get("error"))
        self.assertEqual("9.10.0", (folder / "VERSION").read_text().strip())
        self.assertEqual("9.10.0", json.loads((folder / ".claude-plugin/plugin.json").read_text())["version"])
        self.assertIn("plugins/quenching-extra/VERSION", {a["path"] for a in result["artifacts"]})
        self.assertNotIn(("plugins/quenching-extra/VERSION", "plain"), RELEASE_ARTIFACTS)

    def test_new_target_consumer_drift_refuses_before_any_existing_surface_changes(self):
        folder = self.add_published_consumer()
        (folder / "VERSION").write_text("9.9.8\n")
        before = {p: p.read_bytes() for p in Path(self.tmp).rglob("*") if p.is_file()}
        result = bump_release_artifacts(self.tmp, "9.10.0")
        self.assertFalse(result["ok"])
        self.assertIn("lockstep already disagrees", result["error"])
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_missing_manifest_refuses_without_version_writes(self):
        self.manifest_path.unlink()
        before = {p: p.read_bytes() for p in Path(self.tmp).rglob("*") if p.is_file()}
        result = bump_release_artifacts(self.tmp, "9.10.0")
        self.assertFalse(result["ok"])
        self.assertIn("module manifest refused", result["error"])
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_extra_marketplace_entry_refuses_before_any_writes(self):
        path = Path(self.tmp) / ".claude-plugin/marketplace.json"
        market = json.loads(path.read_text())
        market["plugins"].append({"name": "undeclared", "version": "9.9.9"})
        path.write_text(json.dumps(market))
        before = {p: p.read_bytes() for p in Path(self.tmp).rglob("*") if p.is_file()}
        result = bump_release_artifacts(self.tmp, "9.10.0")
        self.assertFalse(result["ok"])
        self.assertIn("published modules", result["error"])
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_codex_distribution_failure_refuses_before_any_version_moves(self):
        manifest = json.loads(self.manifest_path.read_text())
        catalog = Path(self.tmp) / manifest["distributions"][0]["marketplace"]
        original = catalog.read_text()
        for failure in ("missing", "unlisted", "wrong path", "malformed"):
            with self.subTest(failure=failure):
                catalog.write_text(original)
                document = json.loads(original)
                if failure == "missing":
                    catalog.unlink()
                else:
                    if failure == "unlisted":
                        document["plugins"] = []
                    elif failure == "wrong path":
                        document["plugins"][0]["source"] = "./plugins/absent"
                    else:
                        document["plugins"] = None
                    catalog.write_text(json.dumps(document))
                before = {p: p.read_bytes() for p in Path(self.tmp).rglob("*") if p.is_file()}
                result = bump_release_artifacts(self.tmp, "9.10.0")
                self.assertFalse(result["ok"], result)
                self.assertIn(str(catalog.relative_to(self.tmp)), result["error"])
                self.assertEqual(before, {p: p.read_bytes() for p in before})
        catalog.write_text(original)


GENERATOR = (
    "import pathlib, sys\n"
    "v = pathlib.Path('plugins/quenching/VERSION').read_text().strip()\n"
    "pathlib.Path('copy.txt').write_text('copy ' + v + '\\n')\n"
)


class CmdReleaseCommit(Lockstep):
    """`cmd_release` in a disposable git repository: the commit is self-contained."""

    def setUp(self):
        super().setUp()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")
        os.makedirs(os.path.join(self.tmp, "scripts"))
        write_text(os.path.join(self.tmp, "scripts/generate_plugin_modules.py"), GENERATOR)
        write_text(os.path.join(self.tmp, "copy.txt"), "copy\n")
        write_text(os.path.join(self.tmp, "CHANGELOG.md"), "# Changelog\n\n## 9.9.9\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        write_text(os.path.join(self.tmp, "CHANGELOG.md"), "# Changelog\n\n## 9.10.0\n\n## 9.9.9\n")

    def git(self, *argv):
        return subprocess.run(["git", *argv], cwd=self.tmp, capture_output=True, text=True,
                              check=True).stdout

    def release(self):
        from quenching.specs.commands.output import Emitter
        from quenching.specs.commands.release import cmd_release
        cwd = os.getcwd()
        os.chdir(self.tmp)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                return cmd_release(argparse.Namespace(new_version="9.10.0", json=True),
                                   self.tmp, Emitter())
        finally:
            os.chdir(cwd)

    def test_the_commit_carries_changelog_bump_and_regenerated_copy(self):
        self.assertEqual(self.release(), 0)
        files = set(self.git("show", "--name-only", "--format=", "HEAD").split())
        self.assertIn("CHANGELOG.md", files)
        self.assertIn("copy.txt", files)
        self.assertIn("plugins/quenching/VERSION", files)
        self.assertEqual(read_text(os.path.join(self.tmp, "copy.txt")), "copy 9.10.0\n")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.git("rev-list", "-n1", "9.10.0"), self.git("rev-parse", "HEAD"))

    def test_a_tree_dirty_beyond_the_changelog_is_refused_and_nothing_is_written(self):
        write_text(os.path.join(self.tmp, "stray.txt"), "x")
        head = self.git("rev-parse", "HEAD")
        self.assertEqual(self.release(), 2)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(read_text(os.path.join(self.tmp, "plugins/quenching/VERSION")).strip(), "9.9.9")

    def test_a_failing_generator_leaves_the_bump_uncommitted_and_untagged(self):
        write_text(os.path.join(self.tmp, "scripts/generate_plugin_modules.py"),
                   "raise SystemExit(3)\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "break generator")
        head = self.git("rev-parse", "HEAD")
        self.assertEqual(self.release(), 2)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.git("tag"), "")

    def test_a_generator_that_drops_the_codex_catalog_cannot_commit_or_tag(self):
        manifest = json.loads(self.manifest_path.read_text())
        catalog = manifest["distributions"][0]["marketplace"]
        write_text(os.path.join(self.tmp, "scripts/generate_plugin_modules.py"),
                   f"from pathlib import Path\nPath({catalog!r}).unlink()\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "generator drops publication")
        head = self.git("rev-parse", "HEAD")
        self.assertEqual(self.release(), 2)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.git("tag"), "")


REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class RealRepoLockstep(unittest.TestCase):
    def test_every_published_version_is_equal(self):
        found = {}
        for rel, kind in RELEASE_ARTIFACTS:
            text = read_text(os.path.join(REPO, rel))
            self.assertIsNotNone(text, rel)
            if kind == "plain":
                found[rel] = text.strip()
            elif kind == "py":
                found[rel] = _RELEASE_PY_VERSION_RE.search(text).group(2)
            elif kind == "json":
                found[rel] = json.loads(text)["version"]
        market = json.loads(read_text(os.path.join(REPO, ".claude-plugin/marketplace.json")))
        for entry in market["plugins"]:
            self.assertIn("version", entry, entry["name"])
            found["marketplace:" + entry["name"]] = entry["version"]
        self.assertEqual(len(set(found.values())), 1, found)

    def test_manifests_carry_no_hard_coded_command_count(self):
        for rel in (".claude-plugin/marketplace.json",
                    "plugins/quenching/.claude-plugin/plugin.json"):
            self.assertNotRegex(read_text(os.path.join(REPO, rel)), r"\d+ commands", rel)


if __name__ == "__main__":
    unittest.main()
