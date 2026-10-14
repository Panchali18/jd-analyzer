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
from results_view import show_result

CV_FOLDER = Path("test_data/recruiter")
RESULTS_FILE = CV_FOLDER / "screening_results.json"
REQUIRED_TYPES = ("required", "qualification")
GROUPS = [
    ("all", "Evidence for every requirement", "No required item missing."),
    ("few", "Gaps on a few", "Up to a third of required items missing."),
    ("most", "Gaps on most", "More than a third of required items missing."),
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


def show_shortlist(job, candidates):
    decisions = st.session_state.get("decisions", {})
    grouped = {key: [] for key, _, _ in GROUPS}
    for candidate_id, result in candidates.items():
        grouped[group_of(result)].append(candidate_id)

    st.subheader("Candidates")
    st.caption("Grouped by evidence for the required items, not ranked. Candidates within a group are in number order.")
    for key, title, help_text in GROUPS:
        ids = grouped[key]
        with st.expander(f"{title} ({len(ids)})", expanded=key != "most"):
            st.caption(help_text)
            if not ids:
                st.write("No candidates in this group.")
            for candidate_id in ids:
                total, evidenced, partly, _ = evidence(candidates[candidate_id])
                decided = decisions.get((job, candidate_id))
                status = f" · **{decided}** · {real_name(candidate_id)}" if decided else ""
                left, right = st.columns([4, 1])
                left.markdown(
                    f"**{label(candidate_id)}** · evidence for {evidenced} of {total} required, "
                    f"partly for {partly}{status}"
                )
                if right.button("Review", key=f"review_{job}_{candidate_id}", width="stretch"):
                    st.session_state["open_candidate"] = candidate_id


def show_review(job, candidate_id, result):
    st.subheader(f"Reviewing {label(candidate_id)}")
    decided = st.session_state.get("decisions", {}).get((job, candidate_id))
    if decided:
        st.success(f"**Decision recorded: {decided}.** {label(candidate_id)} is {real_name(candidate_id)}.")

    show_result(result, key="recruiter", recruiter=True)

    original = (CV_FOLDER / f"{candidate_id}.txt").read_text()
    blind_text, removed = blind_cv(original)
    with st.expander(f"The blind CV ({len(removed)} personal details removed)"):
        st.code(blind_text, language=None, wrap_lines=True)

    with st.form(key=f"decide_{job}_{candidate_id}", border=True):
        st.markdown("**Your decision**")
        decision = st.radio("Decision", DECISIONS, horizontal=True, label_visibility="collapsed")
        reason = st.text_area(
            "Reason",
            placeholder="What in the evidence led to this decision? This goes into the audit log.",
            height=80,
        )
        submitted = st.form_submit_button("Record decision", type="primary")
    st.caption("The name is shown only after you record a decision. Changing your mind adds a new line to the log.")
    if submitted:
        if len(reason.strip()) < 10:
            st.warning("Please give a reason of at least a few words.")
        else:
            record_decision(job, candidate_id, result, decision, reason)
            st.rerun()


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
    open_id = st.session_state.get("open_candidate")
    list_column, review_column = st.columns([2, 3], gap="large")
    with list_column:
        show_shortlist(job, candidates)
    with review_column:
        open_id = st.session_state.get("open_candidate")
        if open_id in candidates:
            show_review(job, open_id, candidates[open_id])
        else:
            st.markdown(
                "Choose **Review** next to a candidate to see the evidence from their blind CV. "
                "Record a decision with a reason, and the candidate's name is shown."
            )
    st.divider()
    show_audit_log()
