"""Export replayable classroom demo snapshots from the real rule and review engine."""
from pathlib import Path
import json
import sys

DEMO = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO.parent))

from engine import resolve_review, run_offline
from fixtures import AS_OF, CASES, DEMO_CASES, DEMO_PROFILE, TOOL_LABELS


def snapshot(case_id, result):
    return {
        "id": case_id,
        "title": CASES[case_id]["role_title"],
        "employer": CASES[case_id]["employer"],
        "outcome": result["outcome"],
        "summary": result["summary"],
        "deadline": result["deadline"],
        "nextAction": result["next_action"],
        "review": result["review"],
        "citations": result["citations"],
        "trace": [
            dict(event, label=TOOL_LABELS.get(event["action"], event["action"]))
            for event in result["trace"]
        ],
    }


def main():
    results = {case_id: run_offline(case_id) for case_id in DEMO_CASES}
    review_case = "PC-103"
    notes = {
        "equivalent": "Reviewed the signed academic record and confirmed that Applied AI Lab is equivalent to AI Strategy Practicum for this role.",
        "not_equivalent": "The supplied course record does not establish equivalence to AI Strategy Practicum for this role.",
        "request_evidence": "Please attach the signed capstone record and approved mapping for this role.",
    }
    after = {
        decision: snapshot(review_case, resolve_review(review_case, results[review_case], decision, note))
        for decision, note in notes.items()
    }
    snapshots = [snapshot(key, result) for key, result in results.items()]
    assert [row["outcome"] for row in snapshots] == ["ready", "not_ready", "needs_review"]
    assert after["equivalent"]["outcome"] == "ready"
    assert after["not_equivalent"]["outcome"] == "not_ready"
    assert after["request_evidence"]["outcome"] == "missing_evidence"
    payload = json.dumps({
        "profile": DEMO_PROFILE,
        "asOf": AS_OF,
        "cases": snapshots,
        "reviewCase": review_case,
        "reviewResults": after,
    }, ensure_ascii=False)
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = (DEMO / "offline_template.html").read_text(encoding="utf-8")
    marker = "__DEMO_SNAPSHOTS__"
    if template.count(marker) != 1:
        raise ValueError("The offline template requires exactly one snapshot marker.")
    path = DEMO / "Placement_Copilot_Offline_Demo.html"
    path.write_text(template.replace(marker, payload), encoding="utf-8")
    print(f"Built {path.name} from {len(snapshots)} cases and {len(after)} review outcomes.")


if __name__ == "__main__":
    main()
