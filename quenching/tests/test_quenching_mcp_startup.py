"""The whole `quenching` server answers `initialize` and `tools/list` within one second.

A harness gives an MCP server a bounded time to come up (30 s in the session that timed out), and
every catalogued tool is described on `tools/list`; this measures the real server over stdio, the
way a harness starts it.
"""
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time
import unittest

CQ = Path(__file__).resolve().parents[1] / "assets" / "bin" / "cq"
LIMIT = 1.0
RUNS = 3


def measure(root):
    """Start the server, run initialize + tools/list, and return (elapsed seconds, replies by id)."""
    started = time.perf_counter()
    server = subprocess.Popen([sys.executable, str(CQ), "mcp"], cwd=root,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
    try:
        for message in (
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}):
            server.stdin.write(json.dumps(message) + "\n")
        server.stdin.flush()
        replies = {}
        while 2 not in replies:
            line = server.stdout.readline()
            if not line:
                raise AssertionError("the server closed stdout before answering tools/list")
            reply = json.loads(line)
            replies[reply.get("id")] = reply
        elapsed = time.perf_counter() - started
    finally:
        server.stdin.close()
        server.wait(timeout=30)
    return elapsed, replies


class Startup(unittest.TestCase):
    def test_initialize_and_tools_list_answer_within_one_second(self):
        # The median of RUNS starts: one slow start under a sibling gate's load is the host, not
        # the server; a tree that really got slower is slow in every run.
        with tempfile.TemporaryDirectory() as root:
            runs = [measure(root) for _ in range(RUNS)]
        times = [elapsed for elapsed, _ in runs]
        replies = runs[-1][1]
        self.assertEqual("quenching", replies[1]["result"]["serverInfo"]["name"])
        tools = replies[2]["result"]["tools"]
        self.assertGreaterEqual(len(tools), 20)  # one tool per pillar and class (spec 625)
        median = statistics.median(times)
        self.assertLess(median, LIMIT, f"initialize + tools/list median {median:.2f} s over "
                                       f"{RUNS} runs ({', '.join(f'{t:.2f}' for t in times)})")


if __name__ == "__main__":
    unittest.main()
