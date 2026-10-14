"""Recruiter mode (demo): a shortlist of fictional candidates, screened once on their blind CVs.
The recruiter reviews the evidence, records a decision with a reason, and only then sees the name.
Every decision goes into an audit log. No AI call happens on this screen."""
import csv
import io
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from blind import blind
from results_view import STATUS_ICON

CV_FOLDER = Path("test_data/recruiter")
RESULTS_FILE = CV_FOLDER / "screening_results.json"
REQUIRED_TYPES = ("required", "qualification")
GROUPS = [
    ("all", "None missing", "No required item missing."),
    ("few", "A few missing", "Up to a third of required items missing."),
    ("most", "Most missing", "More than a third of required items missing."),
]
DECISIONS = ["Shortlist", "Not now"]


@st.cache_data(show_spinner=False)
def load_results():
    """Screening results saved by screen_all.py: one fixed requirement list per job, every CV judged against it."""
    return json.loads(RESULTS_FILE.read_text())


@st.cache_data(show_spinner=False)
def blind_cv(text):
    """Blind a CV once and remember the answer."""
    return blind(text)


def evidence(result):
    """Counts for the required items only (required and qualification)."""
    items = [r for r in result["requirements"] if r["type"] in REQUIRED_TYPES]
    counts = Counter(r["status"] for r in items)
    return len(items), counts["evidenced"], counts["partly evidenced"], counts["missing"]


def group_of(result):
    total, _, _, missing = evidence(result)
    if missing == 0:
        return "all"
    return "few" if missing <= total / 3 else "most"


def label(candidate_id):
    return f"Candidate {candidate_id[-2:]}"


def real_name(candidate_id):
    """Only called after a decision is recorded."""
    _, removed = blind_cv((CV_FOLDER / f"{candidate_id}.txt").read_text())
    names = [item["text"] for item in removed if item["type"] == "NAME"]
    return names[0] if names else "name not found"


def record_decision(job, candidate_id, result, decision, reason):
    total, evidenced, partly, missing = evidence(result)
    st.session_state.setdefault("decisions", {})[(job, candidate_id)] = decision
    st.session_state.setdefault("audit_log", []).append(
        {
            "time (UTC)": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "job": job,
            "candidate": label(candidate_id),
            "decision": decision,
            "reason": reason.strip(),
            "evidence shown": f"{evidenced} of {total} required, {partly} partly, {missing} missing",
            "AI score shown": f"{result['score']}%",
            "name revealed": real_name(candidate_id),
        }
    )


def short_group(result):
    return {"all": "None missing", "few": "A few missing", "most": "Most missing"}[group_of(result)]


def show_shortlist(job, candidates):
    """One compact table. Click a row to review that candidate."""
    decisions = st.session_state.get("decisions", {})
    order = {key: position for position, (key, _, _) in enumerate(GROUPS)}
    ids = sorted(candidates, key=lambda c: (order[group_of(candidates[c])], c))
    rows = []
    for candidate_id in ids:
        total, evidenced, partly, missing = evidence(candidates[candidate_id])
        decided = decisions.get((job, candidate_id))
        rows.append(
            {
                "Candidate": label(candidate_id),
                "Evidence": short_group(candidates[candidate_id]),
                "Met": f"{evidenced} of {total}",
                "Partly": partly,
                "Missing": missing,
                "Decision": f"{decided} · {real_name(candidate_id)}" if decided else "Not reviewed",
            }
        )
    st.caption(
        "Grouped by evidence for the required items, then in number order. Not ranked by score. "
        "Click a row to review the candidate."
    )
    event = st.dataframe(
        rows, hide_index=True, on_select="rerun", selection_mode="single-row", key=f"table_{job}", width="stretch"
    )
    if event.selection.rows:
        st.session_state["open_candidate"] = ids[event.selection.rows[0]]


def show_requirements(result):
    """The evidence for each requirement, without a percentage: required items first."""
    items = [r for r in result["requirements"] if r["type"] != "eligibility"]
    required = [r for r in items if r["type"] in REQUIRED_TYPES]
    extra = [r for r in items if r["type"] not in REQUIRED_TYPES]
    order = {"evidenced": 0, "partly evidenced": 1, "missing": 2}

    def show(item):
        icon = STATUS_ICON.get(item["status"], "❔")
        quotes = item.get("cv_evidence") or []
        if isinstance(quotes, str):
            quotes = [quotes]
        if item["status"] == "missing" or not quotes:
            st.markdown(f"{icon} {item['skill']}")
            return
        with st.expander(f"{icon} {item['skill']}"):
            for quote in quotes:
                st.markdown(f"> {quote}")
            if item.get("note"):
                st.caption(item["note"])

    st.markdown("**Required**")
    for item in sorted(required, key=lambda r: order.get(r["status"], 3)):
        show(item)
    if extra:
        with st.expander(f"Nice to have ({len(extra)})"):
            for item in extra:
                show(item)


def show_review(job, candidate_id, result):
    total, evidenced, partly, missing = evidence(result)
    decided = st.session_state.get("decisions", {}).get((job, candidate_id))
    with st.container(border=True):
        st.subheader(label(candidate_id))
        if decided:
            st.success(f"**Decision recorded: {decided}.** {label(candidate_id)} is {real_name(candidate_id)}.")
        met_column, partly_column, missing_column = st.columns(3)
        met_column.metric("Required items met", f"{evidenced} of {total}")
        partly_column.metric("Partly met", partly)
        missing_column.metric("Missing", missing)

        evidence_column, decision_column = st.columns([3, 2], gap="large")
        with evidence_column:
            for item in result.get("deal_breakers") or []:
                st.error(f"**Must-have missing:** {item['requirement']}")
            for item in result.get("eligibility_checks") or []:
                st.info(f"**Check with the candidate:** {item['requirement']}")
            show_requirements(result)
        with decision_column:
            with st.form(key=f"decide_{job}_{candidate_id}"):
                st.markdown("**Your decision**")
                decision = st.radio("Decision", DECISIONS, horizontal=True, label_visibility="collapsed")
                reason = st.text_area(
                    "Reason",
                    placeholder="What in the evidence led to this decision? It goes into the audit log.",
                    height=100,
                )
                submitted = st.form_submit_button("Record decision", type="primary", width="stretch")
            st.caption("The name is shown only after you record a decision. Changing your mind adds a new line to the log.")
            if submitted:
                if len(reason.strip()) < 10:
                    st.warning("Please give a reason of at least a few words.")
                else:
                    record_decision(job, candidate_id, result, decision, reason)
                    st.rerun()
            original = (CV_FOLDER / f"{candidate_id}.txt").read_text()
            blind_text, removed = blind_cv(original)
            with st.expander(f"Blind CV ({len(removed)} personal details removed)"):
                st.code(blind_text, language=None, wrap_lines=True)


def show_audit_log():
    log = st.session_state.get("audit_log", [])
    st.subheader(f"Audit log ({len(log)})")
    if not log:
        st.caption("Every decision is recorded here with the time, the reason and the evidence shown at that moment.")
        return
    st.dataframe(log, hide_index=True)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(log[0]))
    writer.writeheader()
    writer.writerows(log)
    st.download_button("Download the log (CSV)", buffer.getvalue(), file_name="fitproof_audit_log.csv", mime="text/csv")
    st.caption("In this demo the log lasts for your visit only. A real product would keep it in a database.")


def render(max_analyses):
    results = load_results()
    with st.sidebar:
        st.header("Screen candidates")
        job = st.selectbox("Job", list(results))
        st.caption(
            f"{len(results[job]['candidates'])} fictional candidates, screened once by Claude on their blind CVs "
            "against the same requirement list. No AI call happens on this screen."
        )

    st.title("FitProof · Recruiter mode")
    st.info("Demo: all CVs and candidates are fictional.")

    candidates = results[job]["candidates"]
    show_shortlist(job, candidates)
    open_id = st.session_state.get("open_candidate")
    if open_id in candidates:
        show_review(job, open_id, candidates[open_id])
    st.divider()
    show_audit_log()
