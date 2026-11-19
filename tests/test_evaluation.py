"""Regression checks for the actual disposition, provenance and officer routes."""
import copy
import unittest

from engine import run_offline
from evaluate import batch, review_batch, score, summarize
from fixtures import CASES


class EvaluationTests(unittest.TestCase):
    def test_stronger_rules_comparator_ties_offline_simulation(self):
        totals = summarize(batch())
        for name, lookups in (("Fixed checklist", 46), ("Optimized rules", 43),
                              ("Adaptive simulation", 43)):
            with self.subTest(mode=name):
                result = totals[name]
                self.assertEqual(result["cases"], 14)
                for measure in ("correct", "notices_correct", "deadline_correct", "escalation_correct"):
                    self.assertEqual(result[measure], 14, measure)
                for measure in ("missed_escalations", "unexpected_escalations", "unsupported_ready", "errors"):
                    self.assertEqual(result[measure], 0, measure)
                self.assertEqual(result["lookups"], lookups)

    def test_scorer_catches_wrong_governing_source_and_unsafe_status(self):
        result = copy.deepcopy(run_offline("EV-02"))
        result["citations"][0]["status"] = "governing"
        result["citations"][1]["status"] = "superseded"
        result["outcome"] = "ready"
        scored = score("EV-02", CASES["EV-02"], "Dify model", result)
        self.assertFalse(scored["notices_correct"])
        self.assertFalse(scored["correct"])
        self.assertTrue(scored["unsupported_ready"])

    def test_scorer_counts_workflow_failure_as_missing_required_review(self):
        row = score("EV-03", CASES["EV-03"], "Dify model", error="Synthetic workflow failure")
        self.assertFalse(row["correct"])
        self.assertFalse(row["notices_correct"])
        self.assertTrue(row["missed_escalation"])

    def test_all_officer_decisions_keep_original_notice_and_add_review_record(self):
        rows = review_batch()
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row["passed"] for row in rows))
