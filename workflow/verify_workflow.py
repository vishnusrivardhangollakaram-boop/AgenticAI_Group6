"""Exercise exported code nodes, routing, and the Dify API adapter offline."""

import json
from functools import cache
from io import BytesIO
from pathlib import Path
import sys
from time import perf_counter
import unittest
from unittest.mock import patch

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dify_client import RESULT_OUTPUT_NAMES, _read_workflow_stream, run_dify
from engine import MAX_ROUNDS, choose_adaptive, verify_remote
from fixtures import CASES


@cache
def nodes_and_edges():
    graph = yaml.safe_load((ROOT / "workflow/Placement_Application_Copilot.yml").read_text())["workflow"]["graph"]
    nodes = {node["id"]: node["data"] for node in graph["nodes"]}
    edges = {}
    for edge in graph["edges"]:
        assert edge["source"] in nodes and edge["target"] in nodes
        assert (edge["source"], edge["sourceHandle"]) not in edges
        edges[edge["source"], edge["sourceHandle"]] = edge["target"]
    return nodes, edges


def offline_workflow(case_id, planner):
    """Walk the exported graph with a substituted planner, preserving the real code nodes."""
    nodes, edges = nodes_and_edges()
    values = {"start": {"case_id": case_id}}
    executions = 0
    node_id = edges["start", "source"]
    visited = set()

    def value(reference):
        return values[reference[0]][reference[1]]

    while node_id:
        assert node_id not in visited
        visited.add(node_id)
        spec = nodes[node_id]
        kind = spec["type"]
        handle = "source"
        if kind == "code":
            namespace = {}
            exec(compile(spec["code"], node_id, "exec"), namespace)
            inputs = {entry["variable"]: value(entry["value_selector"]) for entry in spec["variables"]}
            values[node_id] = namespace["main"](**inputs)
            assert set(values[node_id]) == set(spec["outputs"])
        elif kind == "llm":
            var = spec["prompt_template"][1]["text"].split("{{#", 1)[1].split("#}}", 1)[0]
            context = json.loads(value(var.split(".")))
            executions += 1
            values[node_id] = {"text": planner(context)}
        elif kind == "if-else":
            condition = spec["cases"][0]["conditions"][0]
            assert condition["comparison_operator"] == "is"
            handle = "true" if value(condition["variable_selector"]) == condition["value"] else "false"
        elif kind == "end":
            output = spec["outputs"][0]
            assert output["variable"] == RESULT_OUTPUT_NAMES[executions - 1]
            return json.loads(value(output["value_selector"])), executions
        else:
            raise AssertionError(f"Unhandled exported node type: {kind}")
        node_id = edges[node_id, handle]
    raise AssertionError("The exported graph did not reach an output.")


def adaptive_stub(case_id):
    return lambda view: json.dumps({"action": choose_adaptive({
        "case_id": case_id,
        "ticket": view["ticket"],
        "observed": view["evidence"],
        "finished": view["finished"],
        "trace": view["trace"],
    })})


class WorkflowExportTest(unittest.TestCase):
    def test_export_has_unique_end_output_names_for_publish(self):
        nodes, _ = nodes_and_edges()
        ends = [node for node in nodes.values() if node["type"] == "end"]
        names = [node["outputs"][0]["variable"] for node in ends]
        self.assertEqual(len(ends), MAX_ROUNDS)
        self.assertEqual(names, list(RESULT_OUTPUT_NAMES))
        self.assertEqual(len(set(names)), MAX_ROUNDS)

    def test_all_synthetic_cases_reach_verified_output(self):
        for case_id, case in CASES.items():
            with self.subTest(case=case_id):
                result, calls = offline_workflow(case_id, adaptive_stub(case_id))
                self.assertEqual(result["outcome"], case["expected"])
                self.assertEqual(verify_remote(case_id, result), result)
                self.assertLessEqual(calls, 4)

    def test_invalid_model_output_never_causes_a_lookup(self):
        result, calls = offline_workflow("PC-101", lambda _: '}')
        self.assertEqual(result["outcome"], "incomplete")
        self.assertEqual(result["observed"], {})
        self.assertEqual(calls, 7)

    def test_planner_may_pick_a_different_lookup_order(self):
        fallback = adaptive_stub("PC-101")

        def read_profile_first(view):
            if not view["evidence"]:
                return '{"action":"read_profile"}'
            return fallback(view)

        result, calls = offline_workflow("PC-101", read_profile_first)
        self.assertEqual(result["trace"][0]["action"], "read_profile")
        self.assertEqual(result["outcome"], "ready")
        self.assertEqual(calls, 3)

    def test_api_adapter_uses_workflow_contract_and_verifies_output(self):
        result, _ = offline_workflow("PC-102", adaptive_stub("PC-102"))
        reply = {"workflow_run_id": "offline-test", "data": {"status": "succeeded", "total_tokens": 100,
                  "outputs": {"result_json": json.dumps(result)}}}
        with patch("dify_client._call_workflow", return_value=reply) as mocked:
            checked = run_dify("PC-102", "https://api.dify.ai/v1", "test", "fixture-user")
            self.assertEqual(checked["outcome"], "not_ready")
            self.assertEqual(checked["tokens"], 100)
            mocked.assert_called_once_with(
                "https://api.dify.ai/v1/workflows/run", "test",
                {"inputs": {"case_id": "PC-102"}, "response_mode": "streaming", "user": "fixture-user"},
            )
        result["outcome"] = "ready"
        reply["data"]["outputs"]["result_json"] = json.dumps(result)
        with patch("dify_client._call_workflow", return_value=reply):
            with self.assertRaisesRegex(ValueError, "trusted case evidence"):
                run_dify("PC-102", "https://api.dify.ai/v1", "test", "fixture-user")

    def test_api_adapter_accepts_numbered_ends_and_rejects_ambiguous_outputs(self):
        case_id = "PC-103"
        result, calls = offline_workflow(case_id, adaptive_stub(case_id))
        encoded = json.dumps(result)
        key = RESULT_OUTPUT_NAMES[calls - 1]
        self.assertNotEqual(key, "result_json")
        outputs = dict.fromkeys(RESULT_OUTPUT_NAMES)
        outputs["result_json"] = " "
        outputs[key] = encoded
        reply = {"data": {"status": "succeeded", "outputs": outputs}}
        with patch("dify_client._call_workflow", return_value=reply):
            checked = run_dify(case_id, "https://api.dify.ai/v1", "test", "fixture-user")
            self.assertEqual(checked["outcome"], "needs_review")
            outputs["result_json"] = encoded
            with self.assertRaisesRegex(ValueError, "exactly one populated"):
                run_dify(case_id, "https://api.dify.ai/v1", "test", "fixture-user")
            outputs["result_json"] = None
            outputs[key] = ""
            with self.assertRaisesRegex(ValueError, "exactly one populated"):
                run_dify(case_id, "https://api.dify.ai/v1", "test", "fixture-user")
            outputs[key] = {"unexpected": "object"}
            with self.assertRaisesRegex(ValueError, "JSON string"):
                run_dify(case_id, "https://api.dify.ai/v1", "test", "fixture-user")

    def test_stream_uses_only_terminal_output(self):
        result, _ = offline_workflow("PC-103", adaptive_stub("PC-103"))
        start = {"event": "workflow_started", "workflow_run_id": "fixture-run"}
        intermediate = {"event": "node_finished", "workflow_run_id": "fixture-run", "data": {"status": "succeeded"}}
        payload = {"status": "succeeded", "total_tokens": 314, "outputs": {"result_json": json.dumps(result)}}
        finished = {"event": "workflow_finished", "data": payload}
        lines = ["event: ping\n\n", *(f"data: {json.dumps(x)}\r\n\r\n" for x in (start, intermediate, finished))]
        response = BytesIO("".join(lines).encode())
        self.assertEqual(_read_workflow_stream(response, perf_counter() + 1),
                         {"workflow_run_id": "fixture-run", "data": payload})

    def test_stream_reports_truncation_or_error(self):
        with self.assertRaisesRegex(ValueError, "before the workflow finished"):
            _read_workflow_stream(BytesIO(b"event: ping\n\n"), perf_counter() + 1)
        with self.assertRaisesRegex(ValueError, "stopped the workflow"):
            _read_workflow_stream(BytesIO(b'data: {"event":"error"}\n\n'), perf_counter() + 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
