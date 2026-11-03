"""The gateway grader calls a local stub only: it fails closed and never touches a real endpoint."""
import http.server
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

import _paths  # noqa: F401

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts/eval_gateway_grader.py"


class Stub(http.server.BaseHTTPRequestHandler):
    reply = (200, {"choices": [{"message": {"content": "GRADES"}, "finish_reason": "stop"}]})
    seen: list = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        Stub.seen.append({"path": self.path, "auth": self.headers.get("Authorization"),
                          "body": json.loads(self.rfile.read(length))})
        status, payload = Stub.reply
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def log_message(self, *args):
        pass


class Gateway(unittest.TestCase):
    def setUp(self):
        self.server = http.server.HTTPServer(("127.0.0.1", 0), Stub)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        Stub.seen = []
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.prompt = Path(tmp.name) / "prompt.txt"
        self.prompt.write_text("grade this", encoding="utf-8")

    def call(self, *extra, env=None):
        base = {k: v for k, v in os.environ.items() if not k.startswith("EVAL_GATEWAY_")}
        base.update({"EVAL_GATEWAY_URL": f"http://127.0.0.1:{self.server.server_port}/v1",
                     "EVAL_GATEWAY_TOKEN": "stub-token"} if env is None else env)
        return subprocess.run([sys.executable, "-I", str(SCRIPT), "--model", "m",
                               "--prompt-file", str(self.prompt), *extra],
                              env=base, capture_output=True, text=True, timeout=60)

    def test_a_complete_answer_is_printed_and_the_request_is_well_formed(self):
        Stub.reply = (200, {"choices": [{"message": {"content": "GRADES"}, "finish_reason": "stop"}]})
        done = self.call()
        self.assertEqual((done.returncode, done.stdout.strip()), (0, "GRADES"))
        sent = Stub.seen[0]
        self.assertEqual((sent["path"], sent["auth"]), ("/v1/chat/completions", "Bearer stub-token"))
        self.assertEqual((sent["body"]["max_tokens"], sent["body"]["model"]), (16000, "m"))
        self.assertEqual(sent["body"]["messages"][0]["content"], "grade this")

    def test_finish_length_fails_closed(self):
        Stub.reply = (200, {"choices": [{"message": {"content": "[{"}, "finish_reason": "length"}]})
        done = self.call()
        self.assertEqual(done.returncode, 4)
        self.assertIn("finish: length", done.stderr)
        self.assertEqual(done.stdout, "")

    def test_a_ceiling_under_the_floor_is_refused_before_any_call(self):
        done = self.call("--max-tokens", "8000")
        self.assertEqual(done.returncode, 2)
        self.assertEqual(Stub.seen, [])

    def test_missing_environment_is_refused_without_leaking_values(self):
        done = self.call(env={})
        self.assertEqual(done.returncode, 2)
        self.assertIn("EVAL_GATEWAY_URL", done.stderr)
        self.assertEqual(Stub.seen, [])

    def test_an_http_error_and_a_malformed_answer_fail_closed(self):
        Stub.reply = (500, {"error": "boom"})
        self.assertEqual(self.call().returncode, 3)
        Stub.reply = (200, {"unexpected": True})
        self.assertEqual(self.call().returncode, 3)

    def test_the_token_never_reaches_the_output(self):
        Stub.reply = (500, {"error": "stub-token"})
        done = self.call()
        self.assertNotIn("stub-token", done.stdout + done.stderr)


class Profile(unittest.TestCase):
    def test_the_gateway_profile_declares_the_script_and_the_floor(self):
        profile = json.loads((REPO / "scripts/eval_harnesses.json").read_text())["profiles"]["gateway"]
        self.assertIn("{root}/scripts/eval_gateway_grader.py", profile["argv"])
        self.assertIn("16000", profile["argv"])
        self.assertIn("{prompt_file}", profile["argv"])
        self.assertEqual(profile["arms"], {})
        self.assertNotIn("http", json.dumps(profile))


if __name__ == "__main__":
    unittest.main()
