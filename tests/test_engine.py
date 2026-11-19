"""Regression checks for governing notices, human decisions and the read-only tool boundary."""
import copy
import unittest

from engine import finalize, model_view, resolve_review, run_offline, start, step, verify_remote
from evaluate import batch, summarize


class PlacementEngineTests(unittest.TestCase):
    def test_never_advises_from_an_unchecked_notice(self):
        state = start("PC-102")
        for action in ("read_profile", "read_notice", "finish"):
            step(state, action)
        self.assertFalse(state["finished"])
        self.assertEqual(finalize(state)["outcome"], "incomplete")
        self.assertEqual(finalize(state)["citations"][0]["status"], "unchecked")

    def test_official_amendment_changes_result_with_sources(self):
        result = run_offline("PC-102")
        self.assertEqual(result["outcome"], "not_ready")
        self.assertIn("24 months", result["summary"])
        self.assertEqual([(item["id"], item["status"]) for item in result["citations"]],
                         [("PL-BA-01", "superseded"), ("PL-BA-02", "governing")])
        self.assertEqual(run_offline("EV-11")["outcome"], "ready")
        self.assertEqual(run_offline("EV-14")["outcome"], "ready")

    def test_conflicting_sources_require_review(self):
        result = run_offline("EV-10")
        self.assertEqual(result["reason_code"], "notice_conflict")
        self.assertEqual(sum(c["status"] == "conflicting" for c in result["citations"]), 2)
        with self.assertRaises(ValueError):
            resolve_review("EV-10", result, "equivalent", "Outside review scope")

    def test_officer_can_resume_only_a_pending_case(self):
        case = run_offline("PC-103")
        self.assertTrue(case["review_required"])
        updated = resolve_review("PC-103", case, "equivalent", "Academic office verified the equivalency record.")
        self.assertEqual(updated["outcome"], "ready")
        self.assertEqual(updated["citations"][-1]["id"], "PLACEMENT-REVIEW")
        self.assertEqual(updated["trace"], case["trace"])
        with self.assertRaises(ValueError):
            resolve_review("PC-103", updated, "equivalent", "Cannot apply twice")
        with self.assertRaises(ValueError):
            resolve_review("PC-101", run_offline("PC-101"), "equivalent", "No review required")
        self.assertEqual(resolve_review("PC-103", case, "request_evidence", "Please attach the capstone transcript.")["outcome"],
                         "missing_evidence")
        self.assertEqual(resolve_review("PC-103", case, "not_equivalent", "Academic office found no match.")["outcome"],
                         "not_ready")

    def test_unknown_tool_and_out_of_scope_profile(self):
        state = start("EV-12")
        self.assertNotIn("profile", model_view(state))
        step(state, "submit_application")
        step(state, "read_profile")
        self.assertEqual(state["observed"]["read_profile"], {"status": "unavailable"})
        self.assertEqual(state["trace"][0]["action"], "rejected_action")
        self.assertEqual(run_offline("EV-12")["outcome"], "missing_evidence")

    def test_dify_result_cannot_change_canonical_evidence(self):
        remote = run_offline("PC-102")
        self.assertEqual(verify_remote("PC-102", remote)["outcome"], "not_ready")
        forged = copy.deepcopy(remote)
        forged["outcome"] = "ready"
        with self.assertRaises(ValueError):
            verify_remote("PC-102", forged)
        forged = copy.deepcopy(remote)
        forged["trace"][0]["detail"] = "Forged case trace"
        with self.assertRaises(ValueError):
            verify_remote("PC-102", forged)

    def test_benchmark_labels_accuracy_and_comparator(self):
        metrics = summarize(batch())
        for mode in ("Fixed checklist", "Adaptive simulation"):
            self.assertEqual(metrics[mode]["correct"], 14)
            self.assertEqual(metrics[mode]["unsupported_ready"], 0)
        self.assertLess(metrics["Adaptive simulation"]["lookups"], metrics["Fixed checklist"]["lookups"])


if __name__ == "__main__":
    unittest.main()
