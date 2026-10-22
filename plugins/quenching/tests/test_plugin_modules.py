"""Manifest generation: ownership, bounded repair and published lockstep in disposable trees."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import _paths  # noqa: F401
from quenching.common.modules import (
    MANIFEST, distribution_findings, load_manifest, namespace_map, published_id, release_artifacts,
)

REPO = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("generate_plugin_modules", REPO / "scripts/generate_plugin_modules.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class GeneratedDistribution(unittest.TestCase):
    def setUp(self):
        (REPO / ".quenching").mkdir(exist_ok=True)
        tmp = tempfile.TemporaryDirectory(dir=REPO / ".quenching")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.manifest = copy.deepcopy(load_manifest(REPO))
        # The generated-consumer contract is exercised in the pre-activation shape (the source
        # published and owning cq); principal modules have source dependencies, and a separate
        # fixture exercises their real partition.
        self.manifest["modules"] = [m for m in self.manifest["modules"] if "owned" not in m]
        source_record = next(m for m in self.manifest["modules"] if m["path"] == self.manifest["source"])
        source_record.update(published=True, cqPathOwner=True)
        self.source = self.root / self.manifest["source"]
        self.target = self.root / "plugins/quenching-specs-reader"
        for module in self.manifest["modules"]:
            folder = self.root / module["path"]
            (folder / ".claude-plugin").mkdir(parents=True)
            (folder / ".claude-plugin/plugin.json").write_text(json.dumps({
                "name": module["name"], "version": "1.2.3", "author": {"name": "test"}, "license": "MIT"}))
            if module["versionFile"]:
                (folder / "VERSION").write_text("1.2.3\n")
        (self.source / "bin").mkdir()
        (self.source / "bin/cq").write_text("#!/bin/sh\n")
        (self.source / "bin/cq").chmod(0o755)
        reader = self.manifest["modules"][1]
        for tree in reader["generated"]["trees"]:
            directory = self.source / tree
            directory.mkdir(parents=True)
            (directory / "sample.txt").write_text(tree + "\n")
        (self.source / "assets/bin/quenching/common/version.py").write_text('VERSION = "1.2.3"\n')
        for distribution in self.manifest.get("distributions", []):
            plugin = self.root / distribution["path"] / distribution["pluginManifest"]
            plugin.parent.mkdir(parents=True, exist_ok=True)
            plugin.write_text(json.dumps({"name": distribution["name"], "version": "1.2.3"}))
            (self.root / distribution["path"] / "VERSION").write_text("1.2.3\n")
            catalog = self.root / distribution["marketplace"]
            catalog.parent.mkdir(parents=True, exist_ok=True)
            catalog.write_text(json.dumps({"plugins": [{
                "name": distribution["name"], "source": "./" + distribution["path"],
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools"}]}))
        self.market = self.root / self.manifest["marketplace"]
        self.market.parent.mkdir(parents=True)
        self.market.write_text(json.dumps({"plugins": [
            {"name": m["name"], "source": "./" + m["path"], "version": "1.2.3"}
            for m in self.manifest["modules"]]}))
        for rel in reader["authored"]:
            path = self.target / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("authored " + rel)
        self.save_manifest()

    def save_manifest(self):
        (self.root / MANIFEST).write_text(json.dumps(self.manifest))

    def run_generator(self, mode):
        with patch.object(generator, "ROOT", self.root):
            return generator.main([mode])

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mode & 0o777)
                for p in self.root.rglob("*") if p.is_file()}

    def test_write_preserves_authored_files_and_is_idempotent(self):
        authored = {rel: (self.target / rel).read_bytes() for rel in self.manifest["modules"][1]["authored"]}
        self.assertEqual(0, self.run_generator("--write"))
        first = self.snapshot()
        self.assertEqual(0, self.run_generator("--write"))
        self.assertEqual(first, self.snapshot())
        for rel, data in authored.items():
            self.assertEqual(data, (self.target / rel).read_bytes())
        self.assertEqual(0, self.run_generator("--check"))

    def test_check_detects_each_drift_without_writes_and_write_repairs_bounded_files(self):
        self.assertEqual(0, self.run_generator("--write"))
        tree = self.target / "assets/specs"
        (tree / "sample.txt").unlink()
        (self.target / "assets/portal/sample.txt").write_text("changed")
        (self.target / "assets/bin/quenching/specs/sample.txt").chmod(0o755)
        (tree / "stale.txt").write_text("obsolete")
        unrelated = self.target / "notes.txt"
        unrelated.write_text("not generated")
        before = self.snapshot()
        self.assertEqual(1, self.run_generator("--check"))
        self.assertEqual(before, self.snapshot())
        self.assertEqual(0, self.run_generator("--write"))
        self.assertFalse((tree / "stale.txt").exists())
        self.assertEqual("not generated", unrelated.read_text())
        self.assertEqual(0, self.run_generator("--check"))

    def test_executable_bits_and_bytes_are_copied_but_python_cache_is_not(self):
        path = self.source / "assets/portal/sample.txt"
        path.write_bytes(b"\x00\xff\n")
        path.chmod(0o755)
        cache = path.parent / "__pycache__"
        cache.mkdir()
        (cache / "x.pyc").write_bytes(b"cache")
        self.assertEqual(0, self.run_generator("--write"))
        target = self.target / "assets/portal/sample.txt"
        self.assertEqual(path.read_bytes(), target.read_bytes())
        self.assertTrue(target.stat().st_mode & 0o111)
        self.assertFalse((target.parent / "__pycache__").exists())

    def test_invalid_paths_and_overlaps_refuse_before_any_writes(self):
        for unsafe in ("../escape", "/escape", "assets/../../escape", "README.md"):
            with self.subTest(path=unsafe):
                original = copy.deepcopy(self.manifest)
                self.manifest["modules"][1]["generated"]["trees"].append(unsafe)
                self.save_manifest()
                before = self.snapshot()
                self.assertEqual(2, self.run_generator("--write"))
                self.assertEqual(before, self.snapshot())
                self.manifest = original

    def test_source_missing_symlink_and_target_collision_refuse_before_any_writes(self):
        directory = self.source / "assets/portal"
        shutil.rmtree(directory)
        before = self.snapshot()
        self.assertEqual(2, self.run_generator("--write"))
        self.assertEqual(before, self.snapshot())
        directory.mkdir()
        (directory / "link").symlink_to(self.source / "VERSION")
        self.assertEqual(2, self.run_generator("--write"))
        (directory / "link").unlink()
        (self.target / "assets").write_text("collision")
        before = self.snapshot()
        self.assertEqual(2, self.run_generator("--write"))
        self.assertEqual(before, self.snapshot())

    def test_version_marketplace_and_path_owner_drift_are_findings(self):
        self.assertEqual(0, self.run_generator("--write"))
        hud = self.root / "plugins/quenching-hud/.claude-plugin/plugin.json"
        metadata = json.loads(hud.read_text())
        metadata["version"] = "1.2.2"
        hud.write_text(json.dumps(metadata))
        extra = self.target / "bin/cq"
        extra.write_text("duplicate")
        self.market.write_text(json.dumps({"plugins": []}))
        before = self.snapshot()
        self.assertEqual(1, self.run_generator("--check"))
        self.assertEqual(before, self.snapshot())
        findings = generator.published_findings(self.root, load_manifest(self.root))
        self.assertTrue(any("version drift" in f for f in findings))
        self.assertTrue(any("PATH cq ownership" in f for f in findings))
        self.assertIn("marketplace membership disagrees with published modules", findings)

    def test_platform_distribution_version_drift_is_a_finding(self):
        self.assertEqual(0, self.run_generator("--write"))
        distribution = self.manifest["distributions"][0]
        rel = distribution["path"] + "/" + distribution["pluginManifest"]
        (self.root / rel).write_text(json.dumps({"name": distribution["name"], "version": "1.2.2"}))
        self.assertEqual(1, self.run_generator("--check"))
        findings = generator.published_findings(self.root, load_manifest(self.root))
        self.assertTrue(any(f.startswith("version drift " + rel) for f in findings))

    def test_codex_publication_failures_are_named_without_writes(self):
        self.assertEqual(0, self.run_generator("--write"))
        distribution = self.manifest["distributions"][0]
        catalog = self.root / distribution["marketplace"]
        plugin = self.root / distribution["path"] / distribution["pluginManifest"]
        original, original_plugin = catalog.read_bytes(), plugin.read_bytes()
        for failure in ("missing catalog", "missing entry", "wrong source", "missing plugin",
                        "wrong identity", "unavailable", "malformed catalog"):
            with self.subTest(failure=failure):
                catalog.write_bytes(original)
                plugin.write_bytes(original_plugin)
                document = json.loads(original)
                if failure == "missing catalog":
                    catalog.unlink()
                elif failure == "missing entry":
                    document["plugins"] = []
                elif failure == "wrong source":
                    document["plugins"][0]["source"] = "./plugins/nonexistent"
                elif failure == "missing plugin":
                    plugin.unlink()
                elif failure == "wrong identity":
                    plugin.write_text(json.dumps({"name": "wrong", "version": "1.2.3"}))
                elif failure == "unavailable":
                    document["plugins"][0]["policy"]["installation"] = "NOT_AVAILABLE"
                elif failure == "malformed catalog":
                    document["plugins"] = "invalid"
                if failure != "missing catalog":
                    catalog.write_text(json.dumps(document))
                before = self.snapshot()
                findings = generator.published_findings(self.root, load_manifest(self.root))
                identity_path = distribution["path"] + "/" + distribution["pluginManifest"]
                self.assertTrue(any(distribution["marketplace"] in f or identity_path in f
                                    for f in findings), findings)
                self.assertEqual(1, self.run_generator("--check"))
                self.assertEqual(before, self.snapshot())

    def test_multiple_declared_path_owners_are_refused(self):
        self.manifest["modules"][1]["cqPathOwner"] = True
        self.save_manifest()
        self.assertEqual(2, self.run_generator("--write"))

    def test_unsafe_or_ambiguous_platform_distribution_refuses_before_writes(self):
        original = copy.deepcopy(self.manifest)
        variants = [("path", "../outside"), ("marketplace", "/outside.json"),
                    ("pluginManifest", "../plugin.json"), ("versionFile", "yes"),
                    ("platform", "unknown"), ("path", self.manifest["source"]),
                    ("marketplace", self.manifest["marketplace"])]
        for key, value in variants:
            with self.subTest(key=key, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest["distributions"][0][key] = value
                self.save_manifest()
                before = self.snapshot()
                self.assertEqual(2, self.run_generator("--write"))
                self.assertEqual(before, self.snapshot())


ROOT_TOKEN = "${CLAUDE_" + "PLUGIN_ROOT}"  # split so the repository citation check reads no claim
OLD = "quenching" + ":"  # the pre-module prefix, split for the same reason


class PrincipalGeneration(unittest.TestCase):
    """Activated principal modules materialize from the source with a closed citation set."""

    def setUp(self):
        (REPO / ".quenching").mkdir(exist_ok=True)
        tmp = tempfile.TemporaryDirectory(dir=REPO / ".quenching")
        self.addCleanup(tmp.cleanup)
        self.root = root = Path(tmp.name)
        src = root / "plugins/quenching"
        files = {
            "commands/specs/develop.md": f"Read {ROOT_TOKEN}/assets/references/specs-develop/a.md; "
                                         "then /quenching-design:design:status.\n",
            "commands/design/status.md": f"Run cq design; see {ROOT_TOKEN}/assets/references/design-align/.\n",
            "agents/scout.md": "agent\n",
            "assets/references/specs-develop/a.md": "shared\n",
            "assets/references/design-align/b.md": "design\n",
            "assets/bin/quenching/common/version.py": 'VERSION = "1.2.3"\n',
            "assets/bin/quenching/specs/core.py": "from quenching.common import version\n",
            "assets/bin/quenching/design/core.py": "from quenching.common import version\n",
            "assets/specs/schema.json": "{}\n",
            "assets/bin/cq": "#!/usr/bin/env python3\n",
            "bin/cq": "#!/usr/bin/env python3\n",
            "README.md": "manual\n",
            "VERSION": "1.2.3\n",
            ".claude-plugin/plugin.json": json.dumps({"name": "quenching", "version": "1.2.3",
                                                     "author": {"name": "t"}, "license": "MIT",
                                                     "keywords": ["k"]}),
        }
        for rel, text in files.items():
            path = src / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        (src / "bin/cq").chmod(0o755)
        (src / "assets/bin/cq").chmod(0o755)
        refs = ["specs-develop"]
        self.manifest = {
            "schemaVersion": 1, "source": "plugins/quenching", "marketplace": ".claude-plugin/marketplace.json",
            "versionConstant": "plugins/quenching/assets/bin/quenching/common/version.py",
            "modules": [
                {"name": "quenching", "path": "plugins/quenching", "published": False,
                 "versionFile": True, "cqPathOwner": False},
                {"name": "quenching-specs", "path": "plugins/quenching-specs", "published": True,
                 "versionFile": True, "cqPathOwner": True,
                 "owned": {"commands": ["specs"], "packages": ["specs"], "agents": True},
                 "generatedSupport": {"packages": ["common"], "references": refs, "router": True}},
                {"name": "quenching-design", "path": "plugins/quenching-design", "published": True,
                 "versionFile": True, "cqPathOwner": False,
                 "owned": {"commands": ["design"], "packages": ["design"], "agents": False},
                 "generatedSupport": {"packages": ["common"], "references": [*refs, "design-align"],
                                      "router": True}},
            ]}
        (root / MANIFEST).write_text(json.dumps(self.manifest))
        market = root / self.manifest["marketplace"]
        market.parent.mkdir(parents=True)
        market.write_text(json.dumps({"plugins": [
            {"name": m["name"], "source": "./" + m["path"], "version": "1.2.3"}
            for m in self.manifest["modules"] if m["published"]]}))

    def run_generator(self, mode):
        with patch.object(generator, "ROOT", self.root):
            return generator.main([mode])

    def test_write_materializes_owned_surface_support_closure_and_one_cq(self):
        self.assertEqual(0, self.run_generator("--write"))
        specs, design = self.root / "plugins/quenching-specs", self.root / "plugins/quenching-design"
        self.assertTrue((specs / "commands/specs/develop.md").is_file())
        self.assertTrue((specs / "agents/scout.md").is_file())
        self.assertFalse((specs / "commands/design").exists())
        self.assertFalse((specs / "assets/references/design-align").exists())
        self.assertTrue((design / "assets/references/design-align/b.md").is_file())
        self.assertFalse((design / "agents").exists())
        self.assertTrue((specs / "bin/cq").stat().st_mode & 0o111)
        self.assertFalse((design / "bin/cq").exists())
        self.assertTrue((design / "assets/bin/cq").is_file())
        self.assertTrue((design / "assets/specs/schema.json").is_file())
        self.assertEqual("quenching-design",
                         json.loads((design / ".claude-plugin/plugin.json").read_text())["name"])
        self.assertEqual(0, self.run_generator("--check"))
        (design / "stale.txt").write_text("x")
        self.assertEqual(1, self.run_generator("--check"))
        self.assertEqual(0, self.run_generator("--write"))
        self.assertFalse((design / "stale.txt").exists())

    def test_check_names_dangling_citations_unpublished_ids_and_unshipped_imports(self):
        src = self.root / "plugins/quenching"
        (src / "commands/specs/develop.md").write_text(
            f"{ROOT_TOKEN}/assets/references/design-align/b.md /{OLD}specs:x "
            "quenching-design:nowhere\n")
        (src / "assets/bin/quenching/specs/core.py").write_text("from quenching.design import core\n")
        with patch.object(generator, "ROOT", self.root), \
                patch("sys.stderr", new_callable=__import__("io").StringIO) as err:
            self.assertEqual(1, generator.main(["--check"]))
        for needle in ("dangling citation assets/references/design-align/b.md",
                       "unpublished /quenching: id", "quenching-design:nowhere has no owner",
                       "imports unshipped quenching.design"):
            self.assertIn(needle, err.getvalue())


    def test_check_names_an_unpublished_id_in_an_authored_consumer_file(self):
        self.manifest["modules"][2]["authored"] = ["commands/notes.md"]
        (self.root / MANIFEST).write_text(json.dumps(self.manifest))
        notes = self.root / "plugins/quenching-design/commands/notes.md"
        notes.parent.mkdir(parents=True)
        notes.write_text(f"see /{OLD}specs:x\n")
        with patch.object(generator, "ROOT", self.root), \
                patch("sys.stderr", new_callable=__import__("io").StringIO) as err:
            self.assertEqual(1, generator.main(["--check"]))
        self.assertIn("unpublished /quenching: id in commands/notes.md", err.getvalue())


class PrincipalPartition(unittest.TestCase):
    def test_codex_is_declared_published_and_in_the_release_lockstep(self):
        manifest = load_manifest(REPO)
        distributions = manifest["distributions"]
        self.assertEqual([("codex", "quenching-codex")],
                         [(d["platform"], d["name"]) for d in distributions])
        self.assertEqual([], distribution_findings(REPO, manifest))
        package = distributions[0]
        self.assertIn((package["path"] + "/VERSION", "plain"), release_artifacts(manifest))
        self.assertIn((package["path"] + "/" + package["pluginManifest"], "json"),
                      release_artifacts(manifest))

    def test_single_repository_gate_checks_the_general_distribution(self):
        gate = (REPO / "scripts/verify_repo.sh").read_text()
        self.assertIn("python3 scripts/generate_plugin_modules.py --check", gate)
        self.assertNotIn("python3 scripts/sync_specs_reader_plugin.py --check", gate)

    def test_nine_principal_modules_are_published_and_the_source_is_not(self):
        manifest = load_manifest(REPO)
        principal = [m for m in manifest["modules"] if "owned" in m]
        self.assertEqual({"specs", "align", "design", "ops", "proof", "toolchain", "delivery", "security",
                          "opensource"},
                         {m["name"].removeprefix("quenching-") for m in principal})
        self.assertTrue(all(m["published"] for m in principal))
        published = [m for m in manifest["modules"] if m["published"]]
        self.assertEqual(["quenching-specs"], [m["name"] for m in published if m["cqPathOwner"]])
        source = next(m for m in manifest["modules"] if m["path"] == manifest["source"])
        self.assertFalse(source["published"])
        self.assertFalse(source["cqPathOwner"])
        market = json.loads((REPO / manifest["marketplace"]).read_text())
        self.assertEqual({m["name"] for m in published}, {e["name"] for e in market["plugins"]})
        for module in principal:
            self.assertTrue((REPO / module["path"] / ".claude-plugin/plugin.json").is_file(), module["name"])
            self.assertIn((module["path"] + "/VERSION", "plain"), release_artifacts(manifest))
        # The source still carries the version the generated modules copy.
        self.assertIn((manifest["source"] + "/VERSION", "plain"), release_artifacts(manifest))

    def test_namespace_map_assigns_every_command_head_and_agent_one_module(self):
        manifest = load_manifest(REPO)
        mapping = namespace_map(REPO, manifest)
        source = REPO / manifest["source"]
        heads = {p.name.removesuffix(".md") for p in (source / "commands").iterdir()}
        heads |= {p.stem for p in (source / "agents").glob("*.md")}
        self.assertEqual(heads, set(mapping))
        self.assertEqual("quenching-specs:specs:develop", published_id(OLD + "specs:develop", mapping))
        self.assertEqual("quenching-specs:handoff", published_id(OLD + "handoff", mapping))
        self.assertEqual("quenching-align:align", published_id(OLD + "align", mapping))
        self.assertEqual("quenching-align:knowledge:add", published_id(OLD + "knowledge:add", mapping))
        self.assertEqual("quenching-specs:orchestrator", published_id(OLD + "orchestrator", mapping))
        self.assertEqual("quenching-design:design:status", published_id(OLD + "design:status", mapping))
        with self.assertRaises(ValueError):
            published_id(OLD + "nowhere:x", mapping)

    def test_every_package_pillar_and_reference_has_an_owner_module(self):
        manifest = load_manifest(REPO)
        self.assertEqual([], generator.ownership_findings(REPO, manifest))
        specs = next(m for m in manifest["modules"] if m["name"] == "quenching-specs")
        for package in ("codex", "portal"):
            broken = copy.deepcopy(manifest)
            owner = next(m for m in broken["modules"] if m["name"] == "quenching-specs")
            owner["owned"]["packages"].remove(package)
            lines = generator.ownership_findings(REPO, broken)
            self.assertTrue(any(f"package {package} has no owner" in x for x in lines), lines)
            self.assertTrue(any(f"pillar package {package} has no owner" in x for x in lines), lines)
        broken = copy.deepcopy(manifest)
        for module in broken["modules"]:
            if "owned" in module:
                support = module["generatedSupport"]["references"]
                if "opensource-controls" in support:
                    support.remove("opensource-controls")
        lines = generator.ownership_findings(REPO, broken)
        self.assertEqual(["reference opensource-controls is shipped by no module"], lines)
        self.assertIn("codex", specs["owned"]["packages"])

    def test_principal_modules_activate_together_and_unpublish_the_source(self):
        manifest = load_manifest(REPO)
        with tempfile.TemporaryDirectory(dir=REPO / ".quenching") as tmp:
            root = Path(tmp)
            shutil.copytree(REPO / manifest["source"], root / manifest["source"],
                            ignore=shutil.ignore_patterns("__pycache__", "tests"))
            reader = REPO / "plugins/quenching-specs-reader"
            shutil.copytree(reader, root / "plugins/quenching-specs-reader",
                            ignore=shutil.ignore_patterns("__pycache__"))

            def refused(data):
                (root / MANIFEST).write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    load_manifest(root)

            # One principal module published beside the still-published source: refused.
            partial = copy.deepcopy(manifest)
            for module in partial["modules"]:
                if "owned" in module:
                    module["published"] = module["name"] == "quenching-design"
                    module["cqPathOwner"] = module["name"] == "quenching-specs"
                if module["name"] == "quenching":
                    module.update(published=True, cqPathOwner=True)
            refused(partial)
            both = copy.deepcopy(manifest)
            for module in both["modules"]:
                if "owned" in module:
                    module["published"] = True
                if module["name"] == "quenching":
                    module.update(published=True, cqPathOwner=False)
            refused(both)
            active = copy.deepcopy(both)
            next(m for m in active["modules"] if m["name"] == "quenching")["published"] = False
            (root / MANIFEST).write_text(json.dumps(active))
            self.assertEqual(9, sum(m["published"] for m in load_manifest(root)["modules"] if "owned" in m))

    def test_manifest_drives_release_surface_expansion(self):
        manifest = load_manifest(REPO)
        design = next(m for m in manifest["modules"] if m["name"] == "quenching-design")
        design["published"] = False
        self.assertNotIn(("plugins/quenching-design/VERSION", "plain"), release_artifacts(manifest))
        design["published"] = True
        self.assertIn(("plugins/quenching-design/VERSION", "plain"), release_artifacts(manifest))
        self.assertIn(("plugins/quenching-design/.claude-plugin/plugin.json", "json"),
                      release_artifacts(manifest))


if __name__ == "__main__":
    unittest.main()
