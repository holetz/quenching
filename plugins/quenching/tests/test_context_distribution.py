"""Hand-computed fixtures guard the spike's accounting and evidence boundaries."""
import importlib.util
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "context_distribution", Path(__file__).resolve().parents[3] / "scripts/measure_context_distribution.py")
instrument = importlib.util.module_from_spec(spec)
spec.loader.exec_module(instrument)


def request(key, window, output=1, command=None, model="model-a"):
    result = {"type": "assistant", "message": {"id": key, "model": model,
              "usage": {"input_tokens": window, "output_tokens": output}, "content": []}}
    if command:
        result["attributionSkill"] = command
    return result


def transcript(tmp_path, records, subagent=False, metadata=None):
    path = tmp_path / ("session/subagents/agent-one.jsonl" if subagent else "session.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) if not isinstance(r, str) else r for r in records))
    if metadata is not None:
        path.with_name(path.stem + ".meta.json").write_text(json.dumps(metadata))
    return instrument.measure(path, tmp_path)


class TestContextDistribution(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.tmp_path = Path(scratch.name)

    def test_historical_command_identifier_survives_as_namespace_tokens(self):
        label = ":".join(["quenching", "specs", "isolate"])
        row = transcript(self.tmp_path, [request("one", 123, command=label)])
        group = next(g for g in instrument.aggregate([row])["groups"] if g["dimension"] == "commandByModel")
        assert ":".join(group["nameParts"]) == label
        assert "name" not in group
        assert group["tokenExposure"] == 123

    def test_final_split_usage_is_one_request_and_all_input_fields_count(self):
        first = request("same", 10, 1)
        final = request("same", 10, 9)
        final["message"]["usage"].update(cache_read_input_tokens=20, cache_creation_input_tokens=30)
        row = transcript(self.tmp_path, [first, final, request("next", 70)])
        totals = instrument.summary([row])
        assert totals["requests"] == 2
        assert totals["tokenExposure"] == 130
        assert totals["peak"]["max"] == 70
        assert totals["firstObservedWindow"]["median"] == 60
        assert totals["firstObservedFreshInput"]["median"] == 40


    def test_malformed_missing_and_invalid_usage_are_visible(self):
        no_id = request("", 100)
        invalid = request("bad", -5)
        missing = request("missing", 8)
        del missing["message"]["usage"]
        row = transcript(self.tmp_path, ["{broken", [], no_id, invalid, missing, request("ok", 12)])
        assert len(row["requests"]) == 1
        assert row["anomalies"] == {"unparsed-record": 1, "non-object-record": 1,
                                    "assistant-without-message-id": 1, "invalid-token-usage": 1,
                                    "assistant-without-usage": 1}


    def test_unclosed_skill_is_upper_bound_and_unknown_pointer_stays_unknown(self):
        caller = request("a", 10, command="quenching:specs:orchestrate")
        caller["message"]["content"] = [{"type": "tool_use", "name": "Skill",
                                            "input": {"skill": "quenching:specs:execute"}}]
        row = transcript(self.tmp_path, [caller, request("b", 100, command="quenching:specs:execute"),
                                    request("c", 20)])
        assert [r["attribution"] for r in row["requests"]] == [
            "pointer-closed", "pointer-upper-bound", "unknown"]
        assert row["anomalies"]["se-attribution-unclosed"] == 1
        assert row["requests"][-1]["command"] == "unknown"


    def test_role_comes_from_metadata_and_models_do_not_merge(self):
        row = transcript(self.tmp_path, [request("a", 10), request("b", 40, model="model-b")],
                         subagent=True, metadata={"agentType": "quenching:orchestrator"})
        assert row["role"] == "conductor"
        groups = instrument.aggregate([row])["groups"]
        assert [(g["model"], g["tokenExposure"]) for g in groups if g["dimension"] == "roleByModel"] == [
            ("model-a", 10), ("model-b", 40)]


    def test_missing_metadata_and_zero_request_files_are_not_silently_measured(self):
        row = transcript(self.tmp_path, [], subagent=True)
        assert row["role"] == "unknown-subagent"
        report = instrument.aggregate([row])
        assert report["filesWithoutRequests"] == 1
        assert report["groups"] == []
        assert report["anomalies"] == {"unreadable-agent-metadata": 1}


    def test_quantiles_and_above_threshold_share_are_hand_computed(self):
        row = transcript(self.tmp_path, [request("one", 200000), request("two", 50000)])
        result = instrument.summary([row])
        assert result["thresholdComparisons"][2]["samplesAbove"] == 0
        assert result["thresholdComparisons"][1]["exposureShareAbove"] == 1
        assert instrument.distribution([5, 1, 8, 3])["median"] == 4
        assert instrument.distribution([5, 1, 8, 3])["p90"] == 8


    def test_entry_proxy_cannot_pass_restart_gate(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            assert instrument.check_restart({"firstObservedWindow": 40000}) == 2
        assert "needs-human" in stderr.getvalue()


    def test_compaction_summary_copies_do_not_count(self):
        rec = request("summary", 900000)
        rec["isCompactSummary"] = True
        row = transcript(self.tmp_path, [rec, request("live", 10)])
        assert len(row["requests"]) == 1
        assert row["compactSummariesSkipped"] == 1


    def test_aggregate_request_input_is_not_one_context_window(self):
        rec = request("multi", 900)
        rec["message"]["usage"]["iterations"] = [
            {"type": "message", "input_tokens": 400},
            {"type": "advisor_message", "input_tokens": 10000, "model": "advisor-model"},
            {"type": "message", "input_tokens": 500}]
        row = transcript(self.tmp_path, [rec])
        result = instrument.summary([row])
        assert result["peak"]["max"] == 900
        assert result["observedExecutorIterationPeak"]["max"] == 500
        assert result["requestsWithMultipleExecutorIterations"] == 1
        assert result["tokenExposure"] == 900


    def test_identified_resume_preparation_ends_at_task_selection(self):
        earlier = transcript(self.tmp_path, [request("one", 10)], subagent=True,
                             metadata={"agentType": "quenching:spec-runner"})
        earlier.update(assignmentSpec="1234", startedAt="2026-01-01T00:00:00Z",
                       taskChecks=[{"task": "1.1", "line": 4}])
        later = transcript(self.tmp_path, [request("new", 20), request("work", 80)], subagent=True,
                           metadata={"agentType": "quenching:spec-runner"})
        later.update(assignmentSpec="1234", startedAt="2026-01-01T01:00:00Z", explicitResume=True,
                     firstNextQueryLine=1)
        cost = instrument.resumptions([earlier, later])
        assert cost["status"] == "measured"
        assert cost["pairs"][0]["startupTokenExposure"] == 20
        assert cost["pairs"][0]["startupPeak"] == 20
        assert "not-measured" in cost["causalSavings"]


    def test_resume_without_identified_spec_cannot_form_a_pair(self):
        earlier = transcript(self.tmp_path, [request("one", 10)], subagent=True,
                             metadata={"agentType": "quenching:spec-runner"})
        earlier.update(startedAt="2026-01-01T00:00:00Z",
                       taskChecks=[{"task": "1.1", "line": 4}])
        later = transcript(self.tmp_path, [request("new", 20)], subagent=True,
                           metadata={"agentType": "quenching:spec-runner"})
        later.update(startedAt="2026-01-01T01:00:00Z", explicitResume=True,
                     firstNextQueryLine=1)
        cost = instrument.resumptions([earlier, later])
        assert cost["status"] == "not-measured"
        assert cost["pairs"] == []
