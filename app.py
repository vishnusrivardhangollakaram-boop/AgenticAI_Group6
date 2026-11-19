"""Student and placement office workspaces over the same synthetic placement case."""
from base64 import b64encode
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
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
MODE_DESCRIPTIONS = {
    LIVE: "The published workflow chooses which evidence to check.",
    OFFLINE: "Walk through the same fictional cases locally.",
    BASELINE: "Run a fixed sequence of evidence checks.",
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


@lru_cache(maxsize=2)
def hero_photo(workspace):
    photo = ROOT / "assets" / f"{workspace}-hero.webp"
    return "data:image/webp;base64," + b64encode(photo.read_bytes()).decode("ascii")


def render_hero(workspace, label, title, lead, *, compact=False):
    photo = (
        f'<div class="hero-image"><img src="{hero_photo(workspace)}" alt=""></div>'
        if workspace in {"student", "office"}
        else ""
    )
    st.html(f"""
      <section class="workspace-hero {workspace}-hero{' hero-compact' if compact else ''}">
        <div class="hero-copy">
          <span class="hero-kicker">{safe(label)}</span>
          <h1>{safe(title)}</h1>
          <p class="hero-lead">{safe(lead)}</p>
        </div>
        {photo}
      </section>
    """)


def section_title(title):
    st.html(f'<div class="flow-heading"><h2>{safe(title)}</h2></div>')


def render_stats(items):
    blocks = []
    for label, value, detail in items:
        subtitle = f"<small>{safe(detail)}</small>" if detail else ""
        blocks.append(f'<div class="stat-block"><span>{safe(label)}</span><strong>{safe(value)}</strong>{subtitle}</div>')
    st.html('<div class="stats-grid">' + "".join(blocks) + "</div>")


def outcome_badge(outcome):
    title, tone = OUTCOMES.get(outcome, ("Awaiting check", "neutral"))
    return (f'<span class="status-tag status-{tone}"><span aria-hidden="true">'
            f'●</span> {title}</span>')


def role_tile(case_id, result=None):
    role = CASES[case_id]
    deadline = result.get("deadline") if result else None
    deadline_copy = f'<small>Due {safe(deadline.partition(",")[0])}</small>' if deadline else ""
    outcome = result["outcome"] if result else None
    _, tone = OUTCOMES.get(outcome, ("Awaiting check", "neutral"))
    return f"""
      <article class="role-tile role-{tone}">
        <span class="role-code">{safe(role["employer"])}</span>
        <strong>{safe(role["role_title"])}</strong>
        {outcome_badge(outcome)}
        {deadline_copy}
      </article>
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
        metadata = f'{source.get("id", "Placement record")} · Revision {revision}' if revision else source.get("id", "")
        superseded = " reference-archived" if status in {"superseded", "archived"} else ""
        status_label = f"<span>{safe(status.replace('_', ' ').title())}</span>" if status else ""
        st.html(f"""
          <div class="reference{superseded}">
            <div class="source-meta"><small>{safe(metadata)}</small>{status_label}</div>
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

st.html(f"""
  <header class="brandbar">
    <span class="brandmark" aria-hidden="true">P</span>
    <div class="brand-wordmark"><strong>Placement Copilot</strong><small>Campus Careers</small></div>
    <span class="brand-status">
      <span class="connection-dot{' is-connected' if api_key else ''}" aria-hidden="true"></span>
      {'Dify available' if api_key else 'Simulation available'}
    </span>
    <span class="demo-label">Classroom demo</span>
  </header>
""")

tabs = st.tabs(["Student workspace", "Placement office", "Evaluation"])

with tabs[0]:
    hero = st.empty()

    def show_student_hero():
        with hero.container():
            render_hero(
                "student", "Student workspace", "Placement Application Copilot",
                "Check which campus roles you can apply for and see the rule behind each decision.",
                compact=bool(state.reports),
            )

    show_student_hero()
    rail, workspace = st.columns([1, 2.4], gap="large")
    student = DEMO_PROFILE["student_name"]
    initials = "".join(part[0] for part in student.split()[:2])
    with rail:
        with st.container(border=True, key="run_form"):
            section_title("Check eligibility")
            scope = st.selectbox(
                "Roles to check",
                ["all", *DEMO_CASES],
                format_func=lambda key: "All campus roles" if key == "all" else CASES[key]["role_title"],
            )
            modes = [OFFLINE, BASELINE] + ([LIVE] if api_key else [])
            with st.expander("Run settings"):
                mode = st.radio("Run mode", modes, index=2 if api_key else 0, key="selected_run_mode")
                st.caption(MODE_DESCRIPTIONS[mode])
            if st.button("Check my shortlist", type="primary", width="stretch"):
                latest = {}
                failures = []
                case_ids = DEMO_CASES if scope == "all" else (scope,)
                progress = st.empty()
                for index, case_id in enumerate(case_ids, start=1):
                    progress.progress(
                        (index - 1) / len(case_ids),
                        text=f"Checking {CASES[case_id]['role_title']} · {index} of {len(case_ids)}",
                    )
                    try:
                        checked = (
                            run_dify(case_id, base_url, api_key, state.visitor)
                            if mode == LIVE
                            else run_offline(case_id, baseline=mode == BASELINE)
                        )
                        latest[case_id] = apply_review(checked, state.office_reviews.get(case_id))
                    except ValueError as error:
                        failures.append(f"{CASES[case_id]['role_title']}: {error}")
                progress.empty()
                resize_hero = bool(latest) != bool(state.reports)
                state.reports = latest
                state.pop("office_message", None)
                state.run_mode = mode
                state.generation += 1
                state.run_errors = failures
                if resize_hero:
                    show_student_hero()
        with st.expander("Sample student profile", expanded=not bool(state.reports)):
            st.html(f"""
              <section class="profile">
                <div class="profile-person"><span class="avatar" aria-hidden="true">{safe(initials)}</span>
                <div><strong>{safe(student)}</strong><span>Sample MBA candidate</span></div></div>
                <dl>
                  <div><dt>CGPA</dt><dd>{safe(DEMO_PROFILE["cgpa"])} / {safe(DEMO_PROFILE["cgpa_scale"])}</dd></div>
                  <div><dt>Experience</dt><dd>{safe(DEMO_PROFILE["experience_months"])} months</dd></div>
                  <div><dt>Coursework</dt><dd>{safe(DEMO_PROFILE["capstone"])} · {safe(DEMO_PROFILE["capstone_credits"])} credits</dd></div>
                </dl>
              </section>
            """)

    with workspace:
        section_title("Your application shortlist")
        reports = state.reports
        if state.get("run_errors"):
            for error in state.run_errors:
                st.error(error)
        if reports:
            counts = Counter(r["outcome"] for r in reports.values())
            st.caption(f"Latest run · {state.run_mode}")
            render_stats((
                ("Roles checked", len(reports), None),
                ("Ready to apply", counts["ready"], None),
                ("Awaiting office review", sum(r["review_required"] for r in reports.values()), None),
            ))
            st.html(
                '<div class="role-grid">' + "".join(role_tile(c, reports[c]) for c in DEMO_CASES if c in reports) + '</div>'
            )
            visited = [case for case in DEMO_CASES if case in reports]
            case_id = st.selectbox(
                "Inspect an application", visited, format_func=lambda key: CASES[key]["role_title"]
            )
            result = reports[case_id]
            with st.container(border=True, key="role_assessment"):
                st.html(f"""
                  <div class="assessment-heading">
                    <small class="sub-label">{safe(CASES[case_id]["employer"])} · {safe(case_id)}</small>
                    <h3>{safe(CASES[case_id]["role_title"])}</h3>
                    {outcome_badge(result["outcome"])}
                    <p>{safe(result["summary"])}</p>
                  </div>
                """)
                st.html(f'<div class="next-action"><strong>Next step</strong><p>{safe(result["next_action"])}</p></div>')
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
                '<div class="role-grid">' + "".join(role_tile(key) for key in DEMO_CASES) + '</div>'
            )
            st.html('<div class="empty-note"><strong>Start with a shortlist check</strong>'
                    '<p>See the current notice, any revisions, and what the placement office needs to verify.</p></div>')

with tabs[1]:
    render_hero(
        "office", "Staff workspace", "Placement office review",
        "Review referred cases and record the evidence that resolves them.",
        compact=bool(state.reports),
    )
    pending = [key for key, result in state.reports.items() if result["review_required"]]
    completed = [key for key, result in state.reports.items() if result.get("review")]
    queue, body = st.columns([1, 2.4], gap="large")
    with queue:
        section_title("Review inbox")
        render_stats((("Pending review", len(pending), None), ("Recorded responses", len(completed), None)))
        st.html('<div class="office-context">Demo decisions apply to this browser session.</div>')
    with body:
        section_title("Case review")
        if state.get("office_message"):
            st.success(state.office_message)
        if not pending and not completed:
            st.html('<div class="empty-note"><strong>No cases await an office decision</strong>'
                    '<p>Run the shortlist in the Student workspace to see whether a case needs review.</p></div>')
        elif not pending:
            st.caption("No further cases await a decision.")
        else:
            case_id = st.selectbox("Select an open review", pending, format_func=lambda case: CASES[case]["role_title"])
            result = state.reports[case_id]
            st.html(f"""
              <div class="assessment-heading">
                <small class="sub-label">{safe(CASES[case_id]["employer"])} · {safe(case_id)}</small>
                <h3>{safe(CASES[case_id]["role_title"])}</h3>
                {outcome_badge(result["outcome"])}
                <p>{safe(result["summary"])}</p>
              </div>
            """)
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
        if completed:
            st.subheader("Recorded decisions")
        for case_id in completed:
            st.markdown(f"**{CASES[case_id]['role_title']}**")
            render_review_note(state.reports[case_id])

with tabs[2]:
    render_hero(
        "evaluation", "Synthetic benchmark", "Evaluation",
        "Compare the offline controllers on the same 14 synthetic cases. Live Dify performance is measured separately.",
        compact=True,
    )
    section_title("Controller comparison")
    rows, scores = evaluate_offline()
    render_stats([
        (label, f"{result['correct']} / {result['cases']} correct",
         f"{result['lookups']} tool lookups · {result['unsupported_ready']} unsupported ready decisions. "
         f"{result['notices_correct']} correct notice selections · {result['missed_escalations']} missed escalations.")
        for label, result in scores.items()
    ])
    section_title("Case-by-case results")
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

with st.expander("90-second demo guide"):
    st.markdown(
        "1. Run **Check my shortlist** and compare the three outcomes.\n"
        "2. Inspect **Business Analyst** for the 12 → 24 month amendment.\n"
        "3. In **Placement office**, resolve the capstone question for **AI Strategy Associate**. "
        "Return to the shortlist to see the updated result."
    )
    if st.button("Reset classroom demo"):
        state.reports = {}
        state.office_reviews = {}
        state.run_mode = None
        state.generation += 1
        state.pop("office_message", None)
        state.pop("run_errors", None)
        st.rerun()

snapshot_date = datetime.fromisoformat(AS_OF).strftime("%d %b %Y, %H:%M IST")
st.html(f"""
  <footer class="support-footer">
    <span>Fictional profiles and role notices</span>
    <span>Case snapshot · {safe(snapshot_date)}</span>
  </footer>
""")
