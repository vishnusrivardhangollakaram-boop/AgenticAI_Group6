"""Student and placement office workspaces over the same synthetic placement case."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from uuid import uuid4

import streamlit as st

from dify_client import run_dify, settings
from engine import resolve_review, run_offline
from evaluate import batch, summarize
from fixtures import AS_OF, CASES, DEMO_CASES, DEMO_PROFILE, TOOL_LABELS

ROOT = Path(__file__).resolve().parent
OFFLINE = "Case simulation"
BASELINE = "Fixed checklist"
LIVE = "Dify agent"
OUTCOMES = {
    "ready": ("Ready to apply", "teal"),
    "not_ready": ("Does not meet notice", "rust"),
    "needs_review": ("Office review needed", "gold"),
    "missing_evidence": ("Evidence needed", "gold"),
    "closed": ("Application closed", "rust"),
    "incomplete": ("Check incomplete", "gold"),
}
DECISIONS = {
    "Verify as equivalent": "equivalent",
    "Confirm not equivalent": "not_equivalent",
    "Request additional evidence": "request_evidence",
}

st.set_page_config(
    page_title="Placement Application Copilot",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.html(ROOT / "ui.css")


def get_secret(key):
    try:
        return st.secrets.get(key)
    except (FileNotFoundError, KeyError):
        return None


def safe(value):
    return escape(str(value))


def outcome_badge(outcome):
    title, tone = OUTCOMES.get(outcome, ("Awaiting check", "neutral"))
    return (f'<span class="status-tag status-{tone}"><span aria-hidden="true">'
            f'●</span> {title}</span>')


def stage_summary(result):
    """Format one assessment without relying on arbitrary LLM HTML."""
    deadline = result.get("deadline")
    deadline_copy = f'<small>Due {safe(deadline)}</small>' if deadline else ""
    return f"""
      <div class="role-tile">
        <strong>{safe(CASES[result["case_id"]]["role_title"])}</strong>
        <p>{safe(CASES[result["case_id"]]["employer"])}</p>
        {outcome_badge(result["outcome"])}
        {deadline_copy}
      </div>
    """


def render_trace(result):
    events = []
    for index, event in enumerate(result.get("trace", ()), 1):
        action_id = str(event.get("action", ""))
        action = TOOL_LABELS.get(action_id, action_id.replace("_", " ").capitalize())
        status = str(event.get("status", "")).replace("_", " ")
        detail = event.get("detail")
        events.append(f"""
          <li class="tool-event">
            <span class="tool-index">{index:02}</span>
            <div><strong>{safe(action)}</strong><small>{safe(detail) if detail else ''}</small></div>
            <span class="tool-status">{safe(status)}</span>
          </li>
        """)
    if result.get("review"):
        events.append(f"""
          <li class="tool-event tool-reviewed">
            <span class="tool-index">{len(events) + 1:02}</span>
            <div><strong>Placement office decision</strong><small>The rules rechecked the case against the reviewed evidence.</small></div>
            <span class="tool-status">review recorded</span>
          </li>
        """)
    if events:
        st.html('<ol class="tool-trace" aria-label="Investigation timeline">' + "".join(events) + "</ol>")


def render_notice_comparison(result):
    """Compare observed figures without reading unseen evidence from fixture records."""
    evidence = result["observed"]
    original = evidence.get("read_notice", {}).get("notice")
    amendments = evidence.get("find_amendments", {})
    records = amendments.get("current", ())
    if amendments.get("status") != "amended" or not original or len(records) != 1:
        return
    current = records[0]
    profile = evidence.get("read_profile", {})
    rows = [("Original notice", original["id"], original["min_experience_months"]),
            ("Governing notice", current["id"], current["min_experience_months"])]
    if profile.get("experience_months") is not None:
        rows.append(("Verified student profile", profile["student_id"], profile["experience_months"]))
    parts = [f'<tr><th scope="row">{safe(label)}<small>{safe(reference)}</small></th>'
             f'<td>{safe(months)} months</td></tr>' for label, reference, months in rows]
    st.html('<table class="notice-comparison"><caption>Experience check</caption><tbody>'
            + "".join(parts) + "</tbody></table>")


def render_sources(result):
    sources = result.get("citations", ())
    if not sources:
        st.caption("The check did not return a policy citation.")
    for source in sources:
        status = str(source.get("status", "")).lower()
        revision = source.get("revision")
        metadata = " / ".join(str(part) for part in [source.get("id"), revision, status.title()] if part)
        superseded = " reference-archived" if status in {"superseded", "archived"} else ""
        st.html(f"""
          <div class="reference{superseded}">
            <small>{safe(metadata)}</small>
            <strong>{safe(source.get("title", "Placement record"))}</strong>
            <p>{safe(source.get("text", ""))}</p>
          </div>
        """)



def render_review_note(result):
    review = result.get("review")
    if isinstance(review, dict):
        decision = review.get("label") or str(review.get("decision", "")).replace("_", " ").title()
        st.html(f"""
          <div class="review-note">
            <strong>Placement office response · {safe(decision)}</strong>
            <p>{safe(review.get("note", ""))}</p>
            {('<small>Recorded ' + safe(result['review_recorded_at']) + '</small>') if result.get('review_recorded_at') else ''}
          </div>
        """)


def evidence_fingerprint(result):
    """Bind a decision to the exact evidence shown to the room, independent of lookup order."""
    material = {key: result[key] for key in ("case_id", "as_of", "observed")}
    return sha256(json.dumps(material, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def apply_review(result, recorded):
    if not recorded or not result["review_required"] or recorded["fingerprint"] != evidence_fingerprint(result):
        return result
    return result | resolve_review(result["case_id"], result, recorded["decision"], recorded["note"]) | {
        "review_recorded_at": recorded["recorded_at"],
    }


@st.cache_data(show_spinner=False)
def evaluate_offline():
    rows = batch()
    return rows, summarize(rows)


base_url, api_key = settings(get_secret)
state = st.session_state
if "visitor" not in state:
    state.visitor = uuid4().hex
if "reports" not in state:
    state.reports = {}
if "generation" not in state:
    state.generation = 0
if "run_mode" not in state:
    state.run_mode = None
if "office_reviews" not in state:
    state.office_reviews = {}

st.html("""
  <header class="mast">
    <div class="mast-top"><span class="mast-icon" aria-hidden="true">▥</span>
      <div><div class="mast-brand">Campus Careers</div><div class="mast-brand-note">PLACEMENT DESK</div></div>
      <div class="demo-mark"><span aria-hidden="true">●</span> CLASSROOM DEMO</div>
    </div>
    <div class="mast-inner">
      <div><p class="mast-kicker">YOUR NEXT APPLICATION</p>
      <h1>Placement Application Copilot</h1>
      <p class="mast-lead">See which roles you can apply for, which notice governs each decision, and what the placement office needs to verify.</p></div>
      <div class="mast-side"><span>ONE SHORTLIST, THREE OUTCOMES</span>
       <strong>Apply, check the rule, or ask the office.</strong>
       <small>The current notice appears with each assessment.</small>
      </div>
    </div>
  </header>
""")

with st.expander("90-second demo guide"):
    st.markdown(
        "1. Run **Check my shortlist**. Compare the three outcomes.\n"
        "2. Open **Business Analyst** and inspect the 12 → 24 month amendment.\n"
        "3. In **Placement office**, resolve the capstone question for **AI Strategy Associate**. "
        "Return to the shortlist to see the new result."
    )
    if st.button("Reset classroom demo"):
        state.reports = {}
        state.office_reviews = {}
        state.run_mode = None
        state.generation += 1
        state.pop("office_message", None)
        state.pop("run_errors", None)
        st.rerun()

tabs = st.tabs(["Student workspace", "Placement office", "Evaluation"])


with tabs[0]:
    rail, workspace = st.columns([1, 2.4], gap="large")
    student = DEMO_PROFILE["student_name"]
    initials = "".join(part[0] for part in student.split()[:2])
    with rail:
        st.html(f"""
          <section class="profile">
            <small class="sub-label">STUDENT PROFILE</small>
            <div class="profile-person"><span class="avatar">{safe(initials)}</span>
            <div><strong>{safe(student)}</strong><span>Sample MBA candidate</span></div></div>
            <dl>
              <div><dt>CGPA</dt><dd>{safe(DEMO_PROFILE["cgpa"])} / {safe(DEMO_PROFILE["cgpa_scale"])}</dd></div>
              <div><dt>Experience</dt><dd>{safe(DEMO_PROFILE["experience_months"])} months</dd></div>
              <div><dt>Coursework</dt><dd>{safe(DEMO_PROFILE["capstone"])} · {safe(DEMO_PROFILE["capstone_credits"])} credits</dd></div>
            </dl>
          </section>
        """)
        scope = st.selectbox(
            "What would you like to check?",
            ["all", *DEMO_CASES],
            format_func=lambda key: "Which open campus roles can I apply for?"
            if key == "all" else f"Can I apply for {CASES[key]['role_title']}?",
        )
        modes = [OFFLINE, BASELINE] + ([LIVE] if api_key else [])
        mode = st.radio("Run mode", modes, index=2 if api_key else 0, key="selected_run_mode")
        st.caption({
            OFFLINE: "Offline simulation with synthetic records.",
            BASELINE: "Offline comparison with fixed checks.",
            LIVE: "The published Dify workflow chooses its evidence lookups.",
        }[mode])
        if st.button("Check my shortlist", type="primary", width="stretch"):
            latest = {}
            failures = []
            with st.spinner("Checking role notices and profile evidence…"):
                for case_id in (DEMO_CASES if scope == "all" else [scope]):
                    try:
                        checked = (
                            run_dify(case_id, base_url, api_key, state.visitor)
                            if mode == LIVE
                            else run_offline(case_id, baseline=mode == BASELINE)
                        )
                        latest[case_id] = apply_review(checked, state.office_reviews.get(case_id))
                    except ValueError as error:
                        failures.append(f"{CASES[case_id]['role_title']}: {error}")
            state.reports = latest
            state.pop("office_message", None)
            state.run_mode = mode
            state.generation += 1
            state.run_errors = failures
        st.caption("Sample profile and notices only. Students submit applications through their campus process.")
        st.caption(f"Case snapshot · {datetime.fromisoformat(AS_OF).strftime('%d %b %Y, %H:%M')} IST")

    with workspace:
        st.subheader("Your application shortlist")
        reports = state.reports
        if state.get("run_errors"):
            for error in state.run_errors:
                st.error(error)
        if reports:
            counts = Counter(r["outcome"] for r in reports.values())
            st.caption(f"{state.run_mode} · {len(reports)} role checks · {counts['ready']} ready · "
                       f"{counts['needs_review']} awaiting office review")
            st.html(
                '<div class="role-grid">' + "".join(stage_summary(reports[c]) for c in DEMO_CASES if c in reports) + '</div>'
            )
            visited = [case for case in DEMO_CASES if case in reports]
            case_id = st.selectbox(
                "Inspect an application", visited, format_func=lambda key: CASES[key]["role_title"]
            )
            result = reports[case_id]
            with st.container(border=True):
                st.html(f"""
                  <div class="assessment-heading">
                    <small class="sub-label">{safe(case_id)} / ROLE ASSESSMENT</small>
                    <h3>{safe(CASES[case_id]["role_title"])}</h3>
                    {outcome_badge(result["outcome"])}
                    <p>{safe(result["summary"])}</p>
                  </div>
                """)
                st.markdown("**Next step**")
                st.write(result["next_action"])
                if result.get("deadline"):
                    st.caption(f"Application deadline · {result['deadline']}")
                render_notice_comparison(result)
                render_review_note(result)
                with st.expander("Notice citations and revisions", expanded=True):
                    render_sources(result)
                with st.expander("Investigation trace"):
                    render_trace(result)
                    if state.run_mode == LIVE:
                        if result.get("workflow_run_id"):
                            st.caption(f"Dify run {result['workflow_run_id']}")
                        measurements = []
                        if result.get("elapsed_ms") is not None:
                            measurements.append(f"{result['elapsed_ms'] / 1000:.2f} seconds")
                        if result.get("tokens") is not None:
                            measurements.append(f"{result['tokens']} tokens")
                        if measurements:
                            st.caption(" · ".join(measurements))
            st.download_button(
                "Download shortlist evidence",
                data=json.dumps({"mode": state.run_mode, "assessments": reports}, ensure_ascii=False, indent=2),
                file_name="placement-shortlist-evidence.json",
                mime="application/json",
            )
        else:
            st.html(
                '<p class="workspace-hint">Run a check to compare one student profile against three role notices.</p>'
                '<div class="role-grid">' + "".join(
                    f'<div class="role-tile role-queued"><strong>{safe(CASES[key]["role_title"])}</strong>'
                    '<p>Awaiting a profile and notice check</p></div>' for key in DEMO_CASES
                ) + '</div>'
                '<div class="empty-note"><strong>See the rule behind each outcome</strong>'
                '<p>The shortlist shows current notices, earlier revisions, and any question the office needs to resolve.</p></div>'
            )

with tabs[1]:
    st.html("""
      <div class="office-heading">
        <small class="sub-label">STAFF WORKSPACE</small>
        <h2>Placement office review</h2>
        <p>Resolve evidence that a role notice and student profile cannot settle by themselves.</p>
      </div>
    """)
    pending = [key for key, result in state.reports.items() if result["review_required"]]
    completed = [key for key, result in state.reports.items() if result.get("review")]
    queue, body = st.columns([1, 2.4], gap="large")
    with queue:
        st.metric("Pending review", len(pending))
        st.metric("Recorded responses", len(completed))
        st.caption("Reviews persist across checks in this browser session. Reset the demo to clear them.")
    with body:
        if not pending:
            st.info("No cases await an office decision. Check the shortlist in the student workspace to populate the inbox.")
        else:
            case_id = st.selectbox("Select an open review", pending, format_func=lambda case: CASES[case]["role_title"])
            result = state.reports[case_id]
            st.markdown(f"### {safe(CASES[case_id]['role_title'])}")
            st.write(result["summary"])
            with st.expander("Evidence sent with the review", expanded=True):
                render_sources(result)
                with st.expander("Investigation timeline"):
                    render_trace(result)
            with st.form(f"review-{case_id}-{state.generation}", clear_on_submit=True):
                selected = st.selectbox("Office decision", tuple(DECISIONS), index=None)
                note = st.text_area(
                    "Verification note", placeholder="Record the evidence the office verified.", max_chars=500
                )
                if st.form_submit_button("Record decision and resume", type="primary"):
                    if not selected:
                        st.error("Select the decision you can verify.")
                    elif not note.strip():
                        st.error("Add a verification note.")
                    else:
                        try:
                            decision = {"decision": DECISIONS[selected], "note": note.strip(),
                                        "fingerprint": evidence_fingerprint(result),
                                        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
                            state.reports[case_id] = apply_review(result, decision)
                            state.office_reviews[case_id] = decision
                        except ValueError as error:
                            st.error(str(error))
                        else:
                            state.office_message = (
                                f"Recorded for {CASES[case_id]['role_title']}. "
                                "The student shortlist now reflects this decision."
                            )
                            st.rerun()
        if state.get("office_message"):
            st.success(state.office_message)
        for case_id in completed:
            st.markdown(f"**{CASES[case_id]['role_title']}**")
            render_review_note(state.reports[case_id])

with tabs[2]:
    st.subheader("Evaluation")
    st.caption(
        "These results compare offline controllers on an identical synthetic case set. "
        "Published Dify runs require a separate live evaluation."
    )
    rows, scores = evaluate_offline()
    columns = st.columns(len(scores))
    for column, (label, result) in zip(columns, scores.items()):
        column.metric(str(label), f"{result['correct']} / {result['cases']}", f"{result['lookups']} tool lookups",
                      delta_color="off")
        column.caption(f"{result['unsupported_ready']} unsupported ready verdicts")
        if "notices_correct" in result:
            column.caption(f"{result['notices_correct']} correct notice selections · "
                           f"{result['missed_escalations']} missed escalations")
    st.dataframe(
        rows,
        hide_index=True,
        width="stretch",
        column_order=["case", "scenario", "mode", "expected", "observed", "correct", "lookups"],
    )
    st.download_button(
        "Download evaluation results",
        data=json.dumps(rows, indent=2),
        file_name="placement-evaluation-offline.json",
        mime="application/json",
    )
