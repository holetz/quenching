"""Every text-mode subprocess call in the cq sources declares its encoding.

Without ``encoding=``, Python decodes the child's output with the locale
encoding, which on Windows is cp1252 and corrupts or kills the reader thread.
"""
import ast
import pathlib
import subprocess
import sys
import unittest

BIN = pathlib.Path(__file__).resolve().parents[1] / "assets" / "bin"
CALLS = {"run", "Popen", "check_output", "check_call", "call"}
TEXT_FLAGS = {"text", "universal_newlines"}


def violations(source: str, name: str = "<src>") -> list[str]:
    found = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        callee = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if callee not in CALLS:
            continue
        keywords = {k.arg: k.value for k in node.keywords if k.arg}
        text = any(isinstance(keywords.get(f), ast.Constant) and keywords[f].value is True
                   for f in TEXT_FLAGS)
        if text and "encoding" not in keywords:
            found.append(f"{name}:{node.lineno}")
    return found


class SubprocessTextEncoding(unittest.TestCase):
    def test_lint_flags_a_call_without_encoding(self):
        self.assertEqual(len(violations("subprocess.run(['x'], text=True)")), 1)
        self.assertEqual(violations("subprocess.run(['x'], text=True, encoding='utf-8')"), [])

    def test_no_text_call_in_bin_lacks_encoding(self):
        found = []
        for path in sorted(BIN.rglob("*.py")):
            found += violations(path.read_text(encoding="utf-8"), str(path.relative_to(BIN)))
        self.assertEqual(found, [], "text=True without encoding=")

    def test_utf8_child_output_is_read_intact(self):
        code = "import sys; sys.stdout.buffer.write('ÁREA ação'.encode('utf-8'))"
        done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        self.assertEqual(done.stdout, "ÁREA ação")


if __name__ == "__main__":
    unittest.main()
