"""`quenching://references/` — the plugin's references as MCP resources, by outline and by section."""
import json
import os
import pathlib
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401  — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.mcp import catalog, resources, server

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets" / "references"


def rpc(request_id, method, params=None):
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}


def read(uri):
    return resources.read_resource(uri, "/x")


class Listing(unittest.TestCase):
    def test_every_reference_is_listed_once_beside_the_index(self):
        listed = [r["uri"] for r in resources.list_resources("/x")]
        on_disk = sorted(p.relative_to(ASSETS).as_posix() for p in ASSETS.rglob("*.md"))
        self.assertEqual(listed[0], "quenching://references")
        self.assertEqual(sorted(listed[1:]), [f"quenching://references/{p}" for p in on_disk])

    def test_the_index_carries_each_reference_with_its_size(self):
        (content,) = read("quenching://references")
        payload = json.loads(content["text"])
        self.assertEqual(payload["count"], len(resources.files()))
        self.assertTrue(all(row["chars"] > 0 for row in payload["references"]))


class Reading(unittest.TestCase):
    def small_and_large(self):
        sizes = {rel: len(resources._read(rel)) for rel in resources.files()}
        small = min((r for r, n in sizes.items() if n <= resources.DOC_WHOLE), key=sizes.get)
        large = max(sizes, key=sizes.get)
        return small, large, sizes[large]

    def test_a_small_reference_comes_whole_with_its_outline(self):
        small, _, _ = self.small_and_large()
        text, outline = read(f"quenching://references/{small}")
        self.assertEqual(text["mimeType"], "text/markdown")
        self.assertEqual(text["text"], resources._read(small))
        self.assertIn("outline", json.loads(outline["text"]))

    def test_a_large_reference_answers_its_outline_and_then_one_section(self):
        _, large, size = self.small_and_large()
        if size <= resources.DOC_WHOLE:
            self.skipTest("no reference above the document ceiling")
        (note,) = read(f"quenching://references/{large}")
        outline = json.loads(note["text"])
        self.assertTrue(outline["truncated"])
        heading = next(h["heading"] for h in outline["outline"] if h["level"] == 2)
        (section,) = read(f"quenching://references/{large}?section={heading}")
        self.assertTrue(section["text"].startswith(f"## {heading}"))
        self.assertLess(len(section["text"]), size)

    def test_an_absent_section_is_a_refusal_naming_it(self):
        small, _, _ = self.small_and_large()
        with self.assertRaises(server.ResourceError) as caught:
            read(f"quenching://references/{small}?section=No%20such%20heading")
        self.assertEqual(caught.exception.code, server.BAD_PARAMS)
        self.assertIn("No such heading", caught.exception.message)


class Containment(unittest.TestCase):
    def test_a_uri_resolves_only_inside_the_references_tree(self):
        for uri in ("quenching://references/../modules.json", "quenching://references/../README.md",
                    "quenching://references//etc/passwd.md", "quenching://references/x/../../a.md",
                    "quenching://references/align/tool-resolution.txt"):
            with self.subTest(uri), self.assertRaises(server.ResourceError) as caught:
                read(uri)
            self.assertIn(caught.exception.code, (server.BAD_PARAMS, server.NOT_FOUND))

    def test_a_symlink_out_of_the_tree_is_not_a_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree, outside = pathlib.Path(tmp, "references"), pathlib.Path(tmp, "secret.md")
            tree.mkdir()
            pathlib.Path(tree, "real.md").write_text("# real\n", encoding="utf-8")
            outside.write_text("# secret\n", encoding="utf-8")
            os.symlink(outside, tree / "link.md")
            held, resources.REFERENCES = resources.REFERENCES, str(tree)
            try:
                self.assertEqual(resources.files(), ["real.md"])
                with self.assertRaises(server.ResourceError) as caught:
                    read("quenching://references/link.md")
                self.assertEqual(caught.exception.code, server.NOT_FOUND)
            finally:
                resources.REFERENCES = held

    def test_another_resource_is_not_found_so_a_composite_passes_it_on(self):
        with self.assertRaises(server.ResourceError) as caught:
            read("quenching://config")
        self.assertEqual(caught.exception.code, server.NOT_FOUND)


class Served(unittest.TestCase):
    def test_the_whole_server_reads_references_and_still_the_specs_resources(self):
        surface = server.Composite("quenching", [resources.ReferencesSurface(),
                                                 catalog.surface()])
        listed = server.handle(rpc(1, "resources/list"), "/x", None, surface)
        uris = {r["uri"] for r in listed["result"]["resources"]}
        self.assertIn("quenching://references", uris)
        self.assertIn("quenching://config", uris)
        reply = server.handle(rpc(2, "resources/read", {"uri": "quenching://references"}),
                              "/x", None, surface)
        self.assertIn("contents", reply["result"])
        templates = server.handle(rpc(3, "resources/templates/list"), "/x", None, surface)
        self.assertIn("quenching://references/{path}{?section}",
                      {t["uriTemplate"] for t in templates["result"]["resourceTemplates"]})
        missing = server.handle(rpc(4, "resources/read", {"uri": "quenching://nope"}),
                                "/x", None, surface)
        self.assertEqual(missing["error"]["code"], server.NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
