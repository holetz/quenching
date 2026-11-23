"""cq reads stdin and writes stdout as UTF-8 whatever the locale says."""
import os
import pathlib
import subprocess
import sys
import unittest

CQ = pathlib.Path(__file__).resolve().parents[1] / "assets" / "bin" / "cq"

SCRIPT = (
    "import sys, importlib.machinery as m, importlib.util as u\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "spec = u.spec_from_loader('cqmod', m.SourceFileLoader('cqmod', sys.argv[2]))\n"
    "mod = u.module_from_spec(spec); spec.loader.exec_module(mod)\n"
    "mod.force_utf8_streams()\n"
    "data = sys.stdin.read()\n"
    "sys.stdout.write(ascii(data) + '\\n\\u2014 \\u00e3\\n')\n"
)


class CqStdioUtf8(unittest.TestCase):
    def run_cq(self, payload: bytes) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING")}
        env["PYTHONIOENCODING"] = "cp1252"
        return subprocess.run([sys.executable, "-c", SCRIPT, str(CQ.parent), str(CQ)],
                              input=payload, capture_output=True, env=env, timeout=60)

    def test_utf8_input_is_decoded_not_mojibake(self):
        result = self.run_cq("ã—".encode("utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.decode("utf-8").splitlines()[0], "'\\xe3\\u2014'")

    def test_powershell_bom_is_stripped(self):
        result = self.run_cq(b"\xef\xbb\xbf" + "ã".encode("utf-8"))
        self.assertEqual(result.stdout.decode("utf-8").splitlines()[0], "'\\xe3'")

    def test_output_is_valid_utf8(self):
        result = self.run_cq(b"x")
        self.assertIn("— ã", result.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
