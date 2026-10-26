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
import style
from results_view import STATUS_ICON

CV_FOLDER = Path("test_data/recruiter")
RESULTS_FILE = CV_FOLDER / "screening_results.json"
REQUIRED_TYPES = ("required", "qualification")
# Groups describe the CV, not the person: "no evidence" means the CV doesn't show it, not that they can't do it
GROUPS = [
    ("all", "Evidence for all required", "The CV shows evidence for every required item."),
    ("few", "Evidence for most", "No evidence for up to a third of the required items."),
    ("most", "Evidence for few", "No evidence for more than a third of the required items."),
]
JOB_FILES = {
    "AI Adoption & Delivery Specialist": "test_data/jd_01.txt",
    "Senior Business Analyst, GenAI": "test_data/jd_02.txt",
}
TYPE_LABELS = {"required": "Required", "qualification": "Qualifications", "nice to have": "Nice to have"}
# Decisions work like a real applicant tracking system: a stage plus a reason picked from a list.
# Every reason is logged, and "Other" needs a note.
STAGES = {
    "Advance to phone screen": [
        "Meets the required items",
        "Strong on most required items, gaps worth discussing",
        "Other (see note)",
    ],
    "Hold": [
        "Borderline: compare with other candidates first",
        "Waiting for hiring manager input",
        "Other (see note)",
    ],
    "Reject": [
        "Missing required experience",
        "Missing a required qualification",
        "Better matched candidates for this role",
        "Other (see note)",
    ],
}


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


def current_role(candidate_id):
    """The first job under EXPERIENCE, without dates: what recruiters look at first. Blinding keeps it."""
    blind_text, _ = blind_cv((CV_FOLDER / f"{candidate_id}.txt").read_text())
    lines = blind_text.splitlines()
    for position, line in enumerate(lines):
        if line.strip().upper() == "EXPERIENCE":
            for following in lines[position + 1 :]:
                if following.strip():
                    return following.split(" | ")[0].split(" (")[0].strip()
    return ""


def label(candidate_id):
    return f"Candidate {candidate_id[-2:]}"


def real_name(candidate_id):
    """Only called after a decision is recorded."""
    _, removed = blind_cv((CV_FOLDER / f"{candidate_id}.txt").read_text())
    names = [item["text"] for item in removed if item["type"] == "NAME"]
    return names[0] if names else "name not found"


def record_decision(job, candidate_id, result, stage, reason, note):
    total, evidenced, partly, missing = evidence(result)
    st.session_state.setdefault("decisions", {})[(job, candidate_id)] = stage
    st.session_state.setdefault("audit_log", []).append(
        {
            "time (UTC)": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "job": job,
            "candidate": label(candidate_id),
            "decision": stage,
            "reason": reason,
            "note": note.strip(),
            "AI evidence group shown": short_group(result),
            "evidence shown": f"{evidenced} of {total} required met, {partly} partly, {missing} missing",
            "name revealed": real_name(candidate_id),
        }
    )


def short_group(result):
    return {key: title for key, title, _ in GROUPS}[group_of(result)]


def evidence_summary(result):
    total, evidenced, partly, missing = evidence(result)
    return f"{evidenced} met, {partly} partly, {missing} no evidence"


def show_job_brief(job, requirement_list):
    """What every candidate is checked against, agreed before screening starts."""
    items = [r for r in requirement_list["requirements"] if r["type"] in TYPE_LABELS]
    counts = {t: sum(1 for r in items if r["type"] == t) for t in TYPE_LABELS}
    singular = {"required": "required", "qualification": "qualification", "nice to have": "nice to have"}
    plural = {"required": "required", "qualification": "qualifications", "nice to have": "nice to have"}
    parts = [f"{n} {(singular if n == 1 else plural)[t]}" for t, n in counts.items() if n]
    with st.container(border=True):
        st.markdown(f"**{job}**")
        st.caption(
            f"{len(items)} requirements: {', '.join(parts)}. They were set once from the job description, "
            "and every candidate is checked against this same list."
        )
        with st.expander("The requirements every candidate is checked against"):
            for t, title in TYPE_LABELS.items():
                group = [r["skill"] for r in items if r["type"] == t]
                if group:
                    st.markdown(f"**{title}**")
                    st.markdown("\n".join(f"- {skill}" for skill in group))
        path = JOB_FILES.get(job)
        if path and Path(path).exists():
            with st.expander("Read the job description"):
                st.text(Path(path).read_text())


def show_shortlist(job, candidates):
    """One compact table. Tick a row to review that candidate."""
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
                "Group": short_group(candidates[candidate_id]),
                f"Required items ({total})": evidence_summary(candidates[candidate_id]),
                "Stage": f"{decided} · {real_name(candidate_id)}" if decided else "New",
                "Current role": current_role(candidate_id),
            }
        )
    st.caption(
        "Grouped by how much evidence the CV shows for the required items, then in number order. Not ranked by "
        "score. \"No evidence\" means the CV doesn't show it, not that the candidate can't do it."
    )
    event = st.dataframe(
        rows, hide_index=True, on_select="rerun", selection_mode="single-row", key=f"table_{job}", width="stretch"
    )
    # Only a new tick opens a candidate, so the dropdown can still switch to someone else
    ticked = ids[event.selection.rows[0]] if event.selection.rows else None
    if ticked and ticked != st.session_state.get(f"ticked_{job}"):
        st.session_state["open_candidate"] = ticked
    st.session_state[f"ticked_{job}"] = ticked


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
                st.html(style.quote(quote))
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
        st.subheader(label(candidate_id), anchor=False)
        if decided:
            st.success(f"**Decision recorded: {decided}.** {label(candidate_id)} is {real_name(candidate_id)}.")
        st.caption(current_role(candidate_id))
        st.html(
            f'<p class="fp-count">Required items met: <strong>{evidenced} of {total}</strong></p>'
            + style.bar({"evidenced": evidenced, "partly evidenced": partly, "missing": missing})
        )

        evidence_column, decision_column = st.columns([3, 2], gap="large")
        with evidence_column:
            for item in result.get("deal_breakers") or []:
                st.error(f"**Must-have missing:** {item['requirement']}")
            for item in result.get("eligibility_checks") or []:
                st.info(f"**Check with the candidate:** {item['requirement']}")
            show_requirements(result)
        with decision_column:
            st.markdown("**Your decision**")
            prefix = f"{job}_{candidate_id}"
            stage = st.radio("Stage", list(STAGES), key=f"stage_{prefix}", label_visibility="collapsed")
            reason = st.selectbox("Reason", STAGES[stage], index=None, placeholder="Choose a reason", key=f"reason_{prefix}")
            note = st.text_area("Note (optional, required for Other)", key=f"note_{prefix}", height=80)
            if st.button("Record decision", type="primary", width="stretch", key=f"record_{prefix}"):
                if reason is None:
                    st.warning("Choose a reason.")
                elif reason.startswith("Other") and len(note.strip()) < 10:
                    st.warning("Add a short note to explain \"Other\".")
                else:
                    record_decision(job, candidate_id, result, stage, reason, note)
                    st.rerun()
            st.caption(
                "You decide each candidate individually; there's no bulk reject and nothing moves forward "
                "automatically. The name is shown after you record a decision. Changing your mind adds a new line to the log."
            )
            original = (CV_FOLDER / f"{candidate_id}.txt").read_text()
            blind_text, removed = blind_cv(original)
            with st.expander(f"Blind CV ({len(removed)} personal details removed)"):
                st.code(blind_text, language=None, wrap_lines=True)


def show_audit_log():
    log = st.session_state.get("audit_log", [])
    st.subheader(f"Audit log ({len(log)})", anchor=False)
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
    st.html(
        '<p class="fp-promise">Screen candidates on evidence, with their identity hidden.</p>'
        '<p class="fp-sub">A demo with fictional candidates. The AI only sees blind CVs, candidates are grouped '
        "by evidence rather than ranked, and you make every decision.</p>"
    )

    job = st.selectbox("Job you're screening for", list(results))
    candidates = results[job]["candidates"]
    show_job_brief(job, results[job]["requirements"])
    st.subheader(f"Applicants ({len(candidates)})", anchor=False)
    st.caption("Each CV was screened once by Claude, with personal details hidden. No AI call happens on this screen.")
    show_shortlist(job, candidates)
    order = {key: position for position, (key, _, _) in enumerate(GROUPS)}
    ids = sorted(candidates, key=lambda c: (order[group_of(candidates[c])], c))
    pick_key = f"pick_{job}"
    st.session_state.setdefault(pick_key, None)
    if st.session_state.get("open_candidate") in ids:
        st.session_state[pick_key] = st.session_state["open_candidate"]  # keep the dropdown in step with a tick

    def open_picked():
        st.session_state["open_candidate"] = st.session_state[pick_key]

    st.selectbox(
        "Review a candidate",
        ids,
        format_func=lambda c: f"{label(c)} · {short_group(candidates[c])}",
        placeholder="Choose a candidate",
        key=pick_key,
        on_change=open_picked,
    )
    open_id = st.session_state.get("open_candidate")
    if open_id in candidates:
        show_review(job, open_id, candidates[open_id])
    else:
        st.caption("Choose a candidate above, or tick their row in the table, to see the evidence and record a decision.")
    st.divider()
    show_audit_log()
