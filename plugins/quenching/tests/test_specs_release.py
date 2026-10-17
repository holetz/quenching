"""The version lockstep — `bump_release_artifacts` proved against a disposable tree standing
in for the real artifacts (`RELEASE_ARTIFACTS`) and its changelog gate, never the plugin's own, so this runs
safely on every test run without ever bumping a real version.

Migrated from the pre-refactor specs script's `release_lockstep_failures`. Both directions
matter: agreeing values all move together, and one already-drifted value refuses before
any artifact is touched — kept as two separate cases below rather than folded into one, so
a failure names which direction broke.
"""
import json
import os
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
            module.pop("generated", None)
            # Principal records name source closures load_manifest checks exist; stand them up empty.
            if "owned" in module:
                support = module["generatedSupport"]
                for package in [*module["owned"]["packages"], *support["packages"]]:
                    (source / "bin/quenching" / package).mkdir(parents=True, exist_ok=True)
                for reference in support["references"]:
                    (source / "references" / reference).mkdir(parents=True, exist_ok=True)
        self.manifest_path = Path(self.tmp) / MANIFEST
        self.manifest_path.write_text(json.dumps(manifest))
        write_text(os.path.join(self.tmp, "CHANGELOG.md"), "# Changelog\n\n## 9.10.0\n")

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
                self.assertEqual(read_text(os.path.join(self.tmp, rel)), KINDS[kind])

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
                self.assertEqual(read_text(os.path.join(self.tmp, rel)), KINDS[kind])

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
        (folder / ".claude-plugin/plugin.json").write_text(KINDS["json"])
        market_path = Path(self.tmp) / ".claude-plugin/marketplace.json"
        market = json.loads(market_path.read_text())
        market["plugins"].append({"name": "quenching-extra", "version": "9.9.9"})
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
