"""Run the labelled synthetic evaluation. Live Dify is opt-in."""
import argparse
import csv
import os
from pathlib import Path

from engine import available, evaluate_evidence, finalize, resolve_review, run_offline, start, step
from fixtures import CASES

# A separate, manually specified evidence oracle. The controllers never read it.
# Every citation has an explicit version/status, even when no single notice governs.
PRODUCT = ("PL-PA-01", 1, "governing")
BUSINESS = ("PL-BA-01", 1, "governing")
BUSINESS_SUPERSEDED = ("PL-BA-01", 1, "superseded")
BUSINESS_CURRENT = ("PL-BA-02", 2, "governing")
AI = ("PL-AI-01", 1, "governing")
NOTICE_STATUSES = {"governing", "superseded", "conflicting", "unchecked"}
NOTICE_ORACLE = {
    "EV-01": ((PRODUCT,), 26),
    "EV-02": ((BUSINESS_SUPERSEDED, BUSINESS_CURRENT), 27),
    "EV-03": ((AI,), 28),
    "EV-04": ((AI,), 28),
    "EV-05": ((AI,), 28),
    "EV-06": ((AI,), 28),
    "EV-07": ((PRODUCT,), 18),
    "EV-08": ((PRODUCT,), 26),
    "EV-09": ((PRODUCT,), 26),
    "EV-10": ((BUSINESS_SUPERSEDED, ("PL-BA-02", 2, "conflicting"),
               ("PL-BA-02B", 2, "conflicting")), None),
    "EV-11": ((BUSINESS,), 27),
    "EV-12": ((PRODUCT,), 26),
    "EV-13": ((AI,), 28),
    "EV-14": ((BUSINESS_SUPERSEDED, BUSINESS_CURRENT), 27),
}


def run_optimized_rules(case_id):
    """Policy-first fixed order with deterministic early exits for sufficient evidence."""
    state = start(case_id)
    observed = state["observed"]
    as_of = CASES[case_id]["as_of"]
    for action in ("read_notice", "find_amendments", "read_profile", "verify_equivalence"):
        if evaluate_evidence(observed, as_of):
            break
        if action in available(observed):
            step(state, action)
    return finalize(state)


def notice_signature(result):
    return tuple(sorted(
        (record["id"], record["revision"], record["status"])
        for record in result["citations"]
        if record["status"] in NOTICE_STATUSES or record["title"].endswith(" notice")
    ))


def render_sources(citations):
    return " | ".join(f"{identifier} rev {revision} ({status})" for identifier, revision, status in citations)


def score(case_id, item, mode, result=None, error=""):
    expected = item["expected"]
    expected_notices, expected_day = NOTICE_ORACLE[case_id]
    expected_deadline = f"{expected_day} Nov 2026, 18:00 IST" if expected_day else None
    expected_escalation = expected == "needs_review"
    observed_review = None if result is None else result.get("review_required")
    observed_notices = () if result is None else notice_signature(result)
    observed_deadline = None if result is None else result["deadline"]
    observed = "error" if result is None else result["outcome"]
    return {
        "case": case_id, "scenario": item["title"], "mode": mode,
        "expected": expected, "observed": observed, "correct": expected == observed,
        "expected_notices": render_sources(expected_notices),
        "observed_notices": render_sources(observed_notices),
        "notices_correct": result is not None and tuple(sorted(expected_notices)) == observed_notices,
        "expected_deadline": expected_deadline, "observed_deadline": observed_deadline,
        "deadline_correct": result is not None and expected_deadline == observed_deadline,
        "expected_escalation": expected_escalation, "observed_escalation": observed_review,
        "escalation_correct": observed_review is expected_escalation,
        "missed_escalation": expected_escalation and observed_review is not True,
        "unexpected_escalation": not expected_escalation and observed_review is True,
        "lookups": None if result is None else sum(entry["accepted"] for entry in result["trace"]),
        "unsupported_ready": observed == "ready" and expected != "ready",
        "live_latency_ms": result.get("elapsed_ms") if result and mode == "Dify model" else None,
        "live_tokens": result.get("tokens") if result and mode == "Dify model" else None,
        "error": error,
    }


def batch(live=None):
    """Evaluate every synthetic scoring scenario; optionally include a real Dify callback."""
    modes = {
        "Fixed checklist": lambda key: run_offline(key, baseline=True),
        "Optimized rules": run_optimized_rules,
        "Adaptive simulation": run_offline,
    }
    if live:
        modes["Dify model"] = live
    rows = []
    for key, item in CASES.items():
        if item["demo"]:
            continue
        for mode, runner in modes.items():
            try:
                rows.append(score(key, item, mode, runner(key)))
            except (RuntimeError, ValueError) as error:
                rows.append(score(key, item, mode, error=str(error)))
    return rows


def summarize(rows):
    result = {}
    for mode in dict.fromkeys(row["mode"] for row in rows):
        group = [row for row in rows if row["mode"] == mode]
        result[mode] = {
            "correct": sum(row["correct"] for row in group),
            "cases": len(group),
            "notices_correct": sum(row["notices_correct"] for row in group),
            "deadline_correct": sum(row["deadline_correct"] for row in group),
            "escalation_correct": sum(row["escalation_correct"] for row in group),
            "missed_escalations": sum(row["missed_escalation"] for row in group),
            "unexpected_escalations": sum(row["unexpected_escalation"] for row in group),
            "lookups": sum(row["lookups"] or 0 for row in group),
            "unsupported_ready": sum(row["unsupported_ready"] for row in group),
            "errors": sum(row["observed"] == "error" for row in group),
        }
    return result


def review_batch():
    """Score officer decisions separately from the autonomous-only cases."""
    rows = []
    case_id = "PC-103"
    pending = run_offline(case_id)
    for decision, expected, reason in (
        ("equivalent", "ready", "equivalence_verified"),
        ("not_equivalent", "not_ready", "equivalence_rejected"),
        ("request_evidence", "missing_evidence", "review_evidence"),
    ):
        note = "Synthetic office review confirms the supporting record for this exercise."
        result = resolve_review(case_id, pending, decision, note)
        review_source = any(
            source["id"] == "PLACEMENT-REVIEW" and source["status"] == decision and source["text"] == note
            for source in result["citations"]
        )
        trace_preserved = result["trace"] == pending["trace"]
        original_notice = notice_signature(result) == (AI,)
        rows.append({
            "case": case_id, "decision": decision, "expected": expected, "observed": result["outcome"],
            "verified_review_citation": review_source, "trace_preserved": trace_preserved,
            "governing_notice_preserved": original_notice,
            "passed": result["outcome"] == expected and result["reason_code"] == reason
            and review_source and trace_preserved and original_notice,
        })
    return rows


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Run the configured Dify model on the full suite.")
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--review-csv", type=Path)
    args = parser.parse_args()
    live = None
    if args.live:
        from dify_client import run_dify
        if not os.getenv("DIFY_API_KEY"):
            parser.error("DIFY_API_KEY is required for a live run")
        base = os.getenv("DIFY_API_BASE_URL", "https://api.dify.ai/v1")
        token = os.environ["DIFY_API_KEY"]
        live = lambda key: run_dify(key, base, token, "placement-evaluation")
    rows = batch(live)
    for mode, summary in summarize(rows).items():
        print(f"{mode}: {summary}")
    reviews = review_batch()
    print(f"Officer decisions: {sum(row['passed'] for row in reviews)}/{len(reviews)} passed")
    if args.csv:
        write_csv(args.csv, rows)
    if args.review_csv:
        write_csv(args.review_csv, reviews)


if __name__ == "__main__":
    main()
