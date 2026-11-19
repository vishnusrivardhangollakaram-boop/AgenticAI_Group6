"""Check that a student outcome changes only after a recorded office decision."""
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parent.parent


class ShortlistWorkflowTest(unittest.TestCase):
    @patch("dify_client.settings", return_value=("https://api.dify.ai/v1", ""))
    def test_amendment_and_officer_round_trip(self, _settings):
        app = AppTest.from_file(ROOT / "app.py", default_timeout=15).run()
        self.assertFalse(app.exception)
        next(button for button in app.button if button.label == "Check my shortlist").click().run()

        reports = app.session_state.reports
        self.assertEqual(
            [reports[key]["outcome"] for key in ("PC-101", "PC-102", "PC-103")],
            ["ready", "not_ready", "needs_review"],
        )
        self.assertEqual(
            [(source["id"], source["status"]) for source in reports["PC-102"]["citations"]],
            [("PL-BA-01", "superseded"), ("PL-BA-02", "governing")],
        )
        next(button for button in app.button if button.label == "Record decision and resume").click().run()
        self.assertEqual(app.session_state.reports["PC-103"]["outcome"], "needs_review")

        next(select for select in app.selectbox if select.label == "Office decision").select("Verify as equivalent")
        next(field for field in app.text_area if field.label == "Verification note").input(
            "Verified against the synthetic programme record."
        )
        next(button for button in app.button if button.label == "Record decision and resume").click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state.reports["PC-103"]["outcome"], "ready")
        self.assertEqual(app.session_state.reports["PC-103"]["review"]["decision"], "equivalent")
        self.assertEqual(app.session_state.reports["PC-102"]["outcome"], "not_ready")
        self.assertTrue(any("shortlist now reflects this decision" in element.value for element in app.success))

        next(radio for radio in app.radio if radio.label == "Run mode").set_value("Fixed checklist")
        next(button for button in app.button if button.label == "Check my shortlist").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state.reports["PC-103"]["outcome"], "ready")
        self.assertIn("review_recorded_at", app.session_state.reports["PC-103"])

        next(button for button in app.button if button.label == "Reset classroom demo").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.session_state.office_reviews)
        next(button for button in app.button if button.label == "Check my shortlist").click().run()
        self.assertEqual(app.session_state.reports["PC-103"]["outcome"], "needs_review")


if __name__ == "__main__":
    unittest.main()
