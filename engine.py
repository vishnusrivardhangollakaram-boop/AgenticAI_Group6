"""Read-only evidence tools, placement rules and local prototype controllers."""
from datetime import datetime
import json
import time

from fixtures import CASES, REVIEW_DECISIONS, TOOL_LABELS

MAX_ROUNDS = 7
TOOLS = tuple(TOOL_LABELS)
OUTCOMES = {
    "ready": "Ready to apply",
    "not_ready": "Published criteria not met",
    "needs_review": "Placement Office review",
    "missing_evidence": "Evidence needed",
    "closed": "Application window closed",
    "incomplete": "Investigation incomplete",
}
ACTIONS = {
    "ready": "Review the notice and apply through the official placement portal before the stated deadline.",
    "not_ready": "Check the cited criterion before using an application slot.",
    "needs_review": "Send the cited discrepancy to the placement office.",
    "missing_evidence": "Supply or verify the missing record through the placement office.",
    "closed": "Watch for a revised deadline in the official notices.",
    "incomplete": "Review the case manually or retry the investigation.",
}


def start(case_id):
    item = CASES[case_id]
    return {"case_id": case_id, "ticket": item["ticket"], "observed": {}, "trace": [], "finished": False}


def format_deadline(raw):
    deadline = datetime.fromisoformat(raw)
    return f"{deadline.day} {deadline.strftime('%b %Y, %H:%M')} IST"


def get_notice(observed):
    updates = observed.get("find_amendments", {})
    records = updates.get("current", [])
    return records[0] if len(records) == 1 else None


def evaluate_evidence(observed, as_of, review=None):
    """Return (outcome, explanation, reason_code), or None if more tools are needed."""
    amendments = observed.get("find_amendments")
    if not amendments:
        return None
    if amendments["status"] == "conflict":
        return "needs_review", "Official notices with the same revision disagree. An officer must establish which notice governs.", "notice_conflict"
    current = get_notice(observed)
    if not current:
        return None
    if datetime.fromisoformat(current["deadline"]) <= datetime.fromisoformat(as_of):
        return "closed", "The deadline in the governing notice has already passed.", "deadline"
    profile = observed.get("read_profile")
    if not profile:
        return None
    if profile["status"] == "unavailable":
        return "missing_evidence", "A profile within this case’s authorized scope is required.", "profile"
    required = (("cgpa", "min_cgpa", "CGPA"), ("experience_months", "min_experience_months", "Experience"))
    for field, rule, label in required:
        if profile.get(field) is None:
            return "missing_evidence", f"The candidate record has no verified {label.lower()} value.", field
        actual, target = profile[field], current[rule]
        if actual < target:
            if field == "experience_months":
                return "not_ready", f"The governing notice requires {target} months of experience. The profile records {actual} months.", field
            return "not_ready", f"The governing notice requires a CGPA of {target:g}/10. The verified profile shows {actual:g}/10.", field
    goal = current.get("capstone_required")
    if not goal or profile.get("capstone") == goal:
        return "ready", "The verified profile meets the applicable requirements in the governing notice.", "matched"
    if not profile.get("capstone"):
        return "missing_evidence", "An academic record for the required capstone is missing.", "capstone"
    equivalence = observed.get("verify_equivalence")
    if not equivalence:
        return None
    status = equivalence["status"]
    if status == "accepted" or (review and review["decision"] == "equivalent"):
        return "ready", "The other requirements are met and the capstone equivalence is verified.", "equivalence_verified"
    if status == "rejected" or (review and review["decision"] == "not_equivalent"):
        return "not_ready", "The recorded capstone does not meet the role’s verified equivalence requirement.", "equivalence_rejected"
    if review and review["decision"] == "request_evidence":
        return "missing_evidence", "The officer requested additional evidence before deciding equivalence.", "review_evidence"
    return "needs_review", f"The register does not map {profile['capstone']} to {goal}. An officer must verify equivalence.", "equivalence_unlisted"


def available(observed):
    current = get_notice(observed)
    profile = observed.get("read_profile", {})
    actions = []
    if "read_profile" not in observed:
        actions.append("read_profile")
    if "read_notice" not in observed:
        actions.append("read_notice")
    if "read_notice" in observed and "find_amendments" not in observed:
        actions.append("find_amendments")
    if (current and current["capstone_required"] and profile.get("capstone")
            and profile["capstone"] != current["capstone_required"]
            and "verify_equivalence" not in observed):
        actions.append("verify_equivalence")
    return actions


def read_tool(item, action):
    if action == "read_profile":
        profile = item["profile"]
        if profile["identity_scope"] != "verified":
            return {"status": "unavailable"}
        return {"status": "verified", **{key: profile[key] for key in (
            "student_id", "student_name", "cgpa", "cgpa_scale", "experience_months", "capstone", "capstone_credits"
        )}}
    if action == "read_notice":
        return {"status": "base_notice", "notice": item["notice"]}
    if action == "find_amendments":
        current_date = datetime.fromisoformat(item["as_of"]).date().isoformat()
        records = [item["notice"]] + [a for a in item["amendments"] if a["published"] <= current_date]
        revision = max(record["revision"] for record in records)
        current = [record for record in records if record["revision"] == revision]
        status = "conflict" if len(current) > 1 else "amended" if revision > item["notice"]["revision"] else "current"
        return {"status": status, "current": current,
                "superseded": [record["id"] for record in records if record["revision"] < revision]}
    if action == "verify_equivalence":
        return item["equivalence"] or {"id": "PL-EQ-00", "title": "Academic equivalence register",
                                       "revision": 1, "status": "unlisted", "text": "No matching entry is on file."}
    raise ValueError("Unsupported tool")


def tool_detail(action, result):
    if action == "read_profile":
        if result["status"] == "unavailable":
            return "No candidate record was available in the authorized case scope."
        return f"Verified {result['student_id']}: {result['cgpa']} CGPA, {result['experience_months']} months of experience."
    if action == "read_notice":
        source = result["notice"]
        return f"{source['id']} states a {source['min_experience_months']}-month experience minimum."
    if action == "find_amendments":
        if result["status"] == "conflict":
            return "Two records share the current revision. The case must be reviewed."
        current = result["current"][0]
        return f"{current['id']} governs. Minimum experience: {current['min_experience_months']} months."
    return result["text"]


def step(state, action):
    if state["finished"]:
        return state
    observed = state["observed"]
    item = CASES[state["case_id"]]
    if action == "finish" and evaluate_evidence(observed, item["as_of"]):
        state["finished"] = True
    elif action in available(observed):
        result = read_tool(item, action)
        observed[action] = result
        state["trace"].append({"action": action, "status": result["status"], "accepted": True,
                               "detail": tool_detail(action, result)})
    else:
        state["trace"].append({"action": "rejected_action", "status": "blocked", "accepted": False,
                               "detail": "The action was unavailable or lacked required evidence."})
    return state


def model_view(state):
    observed = state["observed"]
    return {"ticket": state["ticket"], "evidence": observed, "available_tools": available(observed),
            "ready_to_finish": bool(evaluate_evidence(observed, CASES[state["case_id"]]["as_of"])),
            "finished": state["finished"], "trace": state["trace"]}


def citation(record, status):
    capstone = f" A {record['capstone_required']} capstone or verified equivalent is required." if record.get("capstone_required") else ""
    return {"id": record["id"], "title": record["role_title"] + " notice", "revision": record["revision"],
            "status": status, "text": f"CGPA ≥ {record['min_cgpa']:g}/10. Experience ≥ {record['min_experience_months']} months. Deadline {format_deadline(record['deadline'])}.{capstone}"}


def finalize(state, review=None):
    item = CASES[state["case_id"]]
    observed = state["observed"]
    outcome, summary, reason = evaluate_evidence(observed, item["as_of"], review) or (
        "incomplete", "There is not enough verified evidence to recommend a next step.", "incomplete")
    citations = []
    base = observed.get("read_notice", {}).get("notice")
    updates = observed.get("find_amendments", {})
    if base and base["id"] in updates.get("superseded", []):
        citations.append(citation(base, "superseded"))
    if base and not updates:
        citations.append(citation(base, "unchecked"))
    for current in updates.get("current", []):
        citations.append(citation(current, "conflicting" if updates["status"] == "conflict" else "governing"))
    if observed.get("verify_equivalence"):
        citations.append(observed["verify_equivalence"])
    if review:
        citations.append({"id": "PLACEMENT-REVIEW", "title": "Officer decision", "revision": 1,
                          "status": review["decision"], "text": review["note"]})
    selected = get_notice(observed)
    return {
        "case_id": state["case_id"], "outcome": outcome, "title": OUTCOMES[outcome],
        "summary": summary, "reason_code": reason, "observed": observed, "trace": state["trace"],
        "citations": citations, "deadline": format_deadline(selected["deadline"]) if selected else None,
        "review_required": outcome == "needs_review", "next_action": ACTIONS[outcome],
        "as_of": item["as_of"], "review": review,
    }


def choose_adaptive(state):
    """Deterministic controller for the labeled simulation. Runs without a model."""
    observed = state["observed"]
    guidance = model_view(state)
    if guidance["ready_to_finish"]:
        return "finish"
    for tool in ("read_notice", "find_amendments", "read_profile", "verify_equivalence"):
        if tool in guidance["available_tools"]:
            return tool
    return "finish"


def run_offline(case_id, *, baseline=False):
    """Shared tools and policy gates with either fixed or evidence-driven lookup order."""
    clock = time.perf_counter()
    state = start(case_id)
    if baseline:
        for action in TOOLS:
            if action in available(state["observed"]):
                step(state, action)
    else:
        for _ in range(MAX_ROUNDS):
            step(state, choose_adaptive(state))
            if state["finished"]:
                break
    result = finalize(state)
    result["elapsed_ms"] = round((time.perf_counter() - clock) * 1000, 3)
    return result


def decode_action(raw):
    try:
        message = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        action = json.loads(message)["action"]
        return action if isinstance(action, str) else ""
    except (AttributeError, KeyError, TypeError, ValueError):
        return ""


def replay(case_id, trace):
    if not isinstance(trace, list) or len(trace) > MAX_ROUNDS:
        raise ValueError("Invalid tool trace.")
    state = start(case_id)
    for entry in trace:
        if not isinstance(entry, dict) or not isinstance(entry.get("action"), str):
            raise ValueError("Invalid tool trace entry.")
        step(state, entry["action"])
    if state["trace"] != trace:
        raise ValueError("Tool trace differs from verified case evidence.")
    return state


def verify_remote(case_id, supplied):
    if not isinstance(supplied, dict) or supplied.get("case_id") != case_id:
        raise ValueError("Workflow returned a different case.")
    checked = finalize(replay(case_id, supplied.get("trace")))
    for key in ("outcome", "observed", "citations", "deadline", "reason_code"):
        if supplied.get(key) != checked[key]:
            raise ValueError("Workflow evidence differs from the verified case.")
    return checked


def resolve_review(case_id, result, decision, note):
    note = note.strip()
    if decision not in REVIEW_DECISIONS or not 1 <= len(note) <= 500:
        raise ValueError("Select a review decision and provide an evidence note up to 500 characters.")
    checked = verify_remote(case_id, result)
    if result.get("review") or checked["outcome"] != "needs_review":
        raise ValueError("This case has no pending review.")
    if checked["reason_code"] != "equivalence_unlisted":
        raise ValueError("This review only accepts capstone-equivalence decisions.")
    review = {"decision": decision, "label": REVIEW_DECISIONS[decision], "note": note}
    return finalize(replay(case_id, checked["trace"]), review=review)
