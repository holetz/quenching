"""`cost` counts requests (one per message.id), groups by agentType and model, and never
sums across models."""
import contextlib
import io
import json
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.session.commands.cli import build_parser


def rec(mid, model, out, inp=2, cr=0, cw=0):
    return {"type": "assistant", "uuid": f"{mid}-{out}",
            "message": {"id": mid, "model": model,
                        "usage": {"input_tokens": inp, "cache_read_input_tokens": cr,
                                  "cache_creation_input_tokens": cw, "output_tokens": out}}}


def write(path, records):
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


def run(*argv):
    args = build_parser().parse_args(["cost", *argv])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        code = args.func(args)
    return code, buf.getvalue()


class CostTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.sub = pathlib.Path(self.tmp.name) / "sess" / "subagents"
        self.sub.mkdir(parents=True)
        # Streamed twice: the same message.id repeats with a growing usage; one request.
        write(self.sub / "agent-a.jsonl", [
            rec("m1", "opus", 8, cw=100), rec("m1", "opus", 50, cw=100),
            rec("m2", "opus", 10, cr=100, cw=30),
            {"type": "user", "uuid": "x"}])
        (self.sub / "agent-a.meta.json").write_text('{"agentType":"Explore"}')
        write(self.sub / "agent-b.jsonl", [rec("m3", "sonnet", 5, cr=7)])
        (self.sub / "agent-b.meta.json").write_text('{"agentType":"Explore"}')
        write(self.sub / "agent-c.jsonl", [rec("m4", "opus", 1)])

    def tearDown(self):
        self.tmp.cleanup()

    def test_groups_dedupe_and_window(self):
        code, out = run("--json", str(self.sub))
        self.assertEqual(code, 0)
        data = json.loads(out)
        rows = {(g["agentType"], g["model"]): g for g in data["groups"]}
        ex = rows[("Explore", "opus")]
        self.assertEqual((ex["requests"], ex["output"], ex["cacheWrite"], ex["cacheRead"]),
                         (2, 60, 130, 100))
        self.assertEqual(ex["maxWindow"], 132)
        self.assertEqual(rows[("Explore", "sonnet")]["requests"], 1)
        self.assertEqual(rows[("unknown", "opus")]["requests"], 1)

    def test_never_one_total_across_models(self):
        data = json.loads(run("--json", str(self.sub))[1])
        self.assertEqual({m["model"] for m in data["byModel"]}, {"opus", "sonnet"})
        self.assertNotIn("total", data)

    def test_session_directory_resolves_subagents(self):
        code, _ = run("--json", str(self.sub.parent))
        self.assertEqual(code, 0)

    def test_refuses_without_requests(self):
        empty = pathlib.Path(self.tmp.name) / "none" / "subagents"
        empty.mkdir(parents=True)
        self.assertEqual(run("--json", str(empty))[0], 2)

    def test_unparsable_line_is_a_finding(self):
        with (self.sub / "agent-b.jsonl").open("a") as fh:
            fh.write("{not json\n")
        code, out = run("--json", str(self.sub))
        self.assertEqual(code, 1)
        self.assertEqual(len(json.loads(out)["anomalies"]), 1)


if __name__ == "__main__":
    unittest.main()
