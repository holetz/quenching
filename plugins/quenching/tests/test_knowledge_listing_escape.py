import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "assets" / "bin"))

from quenching.knowledge.structure import (  # noqa: E402
    _escape_cell, _unescape_cell, regenerate_listing)

MOLD = ("<!-- BEGIN GENERATED: rebuilt from disk — DO NOT edit by hand.\n"
        "     Row model per subfolder:\n"
        "       | [imports.md](code/imports.md) | <the doc's description:> |\n-->\n")


def _std(title, desc):
    return f"---\ntype: standard\ntitle: {title}\ndescription: {desc}\n---\n\n# {title}\n"


class ListingEscapeRoundTrip(unittest.TestCase):
    def test_escape_is_inverted_by_unescape(self):
        for text in ["plain", "a | b", r"Read \| write", "ends with \\", r"a\\|b", "|\\|"]:
            self.assertEqual(_unescape_cell(_escape_cell(text)), text)

    def test_write_converges_with_backslash_pipe_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp) / "docs"
            files = {
                "index.md": '---\nokf_version: "0.1"\n---\n\n# Bundle\n\n- [Standards](standards/index.md)\n',
                "standards/index.md": "# Standards\n\n## Current docs\n\n" + MOLD
                + "\n### code/\n\n| Doc | Covers |\n| --- | --- |\n"
                + "| [exports.md](code/exports.md) | How we export |\n\n<!-- END GENERATED -->\n",
                "standards/code/index.md": "# code/\n\n- [imports.md](imports.md)\n- [exports.md](exports.md)\n",
                "standards/code/imports.md": _std("Imports", r"Read \| write"),
                "standards/code/exports.md": _std("Exports", "How we export"),
            }
            for rel, text in files.items():
                p = base / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text, encoding="utf-8")
            regenerate_listing(str(base), write=True)
            second = regenerate_listing(str(base), write=True)
            self.assertFalse(second["changed"])
            zone = (base / "standards/index.md").read_text(encoding="utf-8")
            self.assertEqual(zone.count("[imports.md](code/imports.md)"), 2)  # mold + one row


if __name__ == "__main__":
    unittest.main()
