"""Every vitrine `cq specs list` call names the shape it reads: `--lean` or `--full` (#614).

`specs list --json` is lean by default (#605); a caller that reads `stage`, `date`, `tasks` or
`records.branch` must ask for `--full`, or every spec shows as `captured` with 0/0 tasks.
"""
from pathlib import Path
import re
import unittest

import _paths  # noqa: F401
from quenching.specs.commands.cli import build_parser

REPO = Path(__file__).resolve().parents[2]
SOURCES = {
    "claude-vitrine": REPO / "integrations/claude-vitrine/hooks/specs.ts",
    "opencode-vitrine": REPO / "integrations/opencode-vitrine/src/specs.ts",
}

LIST_CALL = re.compile(r"""\[\s*['"]specs['"]\s*,\s*['"]list['"]([^\]]*)\]""")
ARG = re.compile(r"""['"]([^'"]+)['"]""")


def list_calls(source: Path) -> list[list[str]]:
    text = source.read_text(encoding="utf-8")
    return [ARG.findall(match.group(1)) for match in LIST_CALL.finditer(text)]


class VitrineSpecsList(unittest.TestCase):
    def test_every_list_call_declares_its_shape(self):
        for name, path in SOURCES.items():
            calls = list_calls(path)
            with self.subTest(vitrine=name):
                self.assertTrue(calls, f"{path}: no `['specs', 'list', ...]` literal found")
                for argv in calls:
                    self.assertTrue({"--lean", "--full"} & set(argv), f"{name}: specs list {argv} names no shape")

    def test_the_plans_list_asks_for_the_full_shape(self):
        for name, path in SOURCES.items():
            plans = [argv for argv in list_calls(path) if argv[:2] == ["--phase", "plans"]]
            with self.subTest(vitrine=name):
                self.assertEqual(1, len(plans), f"{name}: expected one `specs list --phase plans` call")
                self.assertIn("--full", plans[0])

    def test_the_cli_accepts_list_full_json(self):
        parser, _ = build_parser()
        args = parser.parse_args(["list", "--phase", "plans", "--full", "--json"])
        self.assertTrue(args.full)
        self.assertTrue(args.json)


if __name__ == "__main__":
    unittest.main()
