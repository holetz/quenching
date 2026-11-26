"""The named mounts (`MOUNTS`) and `cq mcp --only`: what the server publishes, per pillar, and the
refusal. Spec 625 grouped the published tools by pillar and class: `all` publishes one tool per
(pillar, class) pair, `core` at most eight, and the specs adapter rides inside the `specs` pillar."""

import collections
import pathlib
import sys
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.mcp import catalog, cli as mcp_cli  # noqa: E402


def published(only=None) -> tuple[int, collections.Counter]:
    tools = mcp_cli.surface(only=only).list_tools()
    return len(tools), collections.Counter(catalog.pillar_of(tool["name"]) for tool in tools)


class TheNamedMounts(unittest.TestCase):
    def test_no_only_publishes_every_catalogued_tool(self):
        total, counts = published()
        self.assertEqual(len(catalog.tool_names()), total)
        self.assertEqual({row.pillar for row in catalog.CATALOG.values()}, set(counts))

    def test_core_publishes_the_three_pillars_a_spec_cycle_reaches(self):
        total, counts = published(catalog.MOUNTS["core"])
        self.assertEqual({"specs", "git", "components"}, set(counts))
        self.assertEqual(sum(len(catalog.tool_names((pillar,))) for pillar in catalog.MOUNTS["core"]),
                         total)

    def test_the_specs_mount_publishes_the_adapter_too(self):
        total, counts = published(("specs",))
        self.assertEqual({"specs"}, set(counts))
        names = {tool["name"] for tool in mcp_cli.surface(only=("specs",)).list_tools()}
        self.assertEqual({"specs_read", "specs_write", "specs_external"}, names)
        self.assertEqual(len(catalog.tool_names(("specs",))), total)

    def test_a_pillar_outside_the_mount_publishes_nothing(self):
        total, counts = published(("knowledge",))
        self.assertEqual({"knowledge"}, set(counts))
        self.assertNotIn("specs_read",
                         {tool["name"] for tool in mcp_cli.surface(only=("knowledge",)).list_tools()})

    def test_every_published_tool_belongs_to_a_pillar_of_the_mount(self):
        for pillar in catalog.MOUNTS["core"]:
            total, counts = published((pillar,))
            self.assertEqual({pillar}, set(counts), pillar)
            self.assertGreater(total, 0, pillar)

    def test_the_mount_names_expand_to_the_pillar_list(self):
        self.assertEqual(("specs", "git", "components"), catalog.mount_pillars("core"))
        self.assertEqual(("specs", "git"), catalog.mount_pillars("specs,git"))
        self.assertEqual([], catalog.mount_refusal("core"))
        self.assertEqual([], catalog.mount_refusal("all"))
        self.assertEqual(["nope"], catalog.mount_refusal("nope"))


class TheOnlyFlag(unittest.TestCase):
    def test_a_routed_list_is_accepted(self):
        only, refusal = mcp_cli.only_pillars("specs,git")
        self.assertIsNone(refusal)
        self.assertEqual(("specs", "git"), only)

    def test_no_flag_publishes_everything(self):
        self.assertEqual((None, None), mcp_cli.only_pillars(None))

    def test_a_name_the_router_does_not_have_is_refused(self):
        only, refusal = mcp_cli.only_pillars("nope")
        self.assertIsNone(only)
        self.assertEqual("ct-mcp-only", refusal["code"])
        self.assertIn("specs", refusal["pillars"])


if __name__ == "__main__":
    unittest.main()
