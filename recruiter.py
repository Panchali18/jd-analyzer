"""Recruiter mode (demo): blind screening on synthetic CVs only.
Real CVs can't be uploaded here, because the app is public."""
from collections import Counter
from pathlib import Path

import streamlit as st

from ai_matcher import analyse, extract_requirements
from blind import blind
from results_view import show_result

CV_FOLDER = Path("test_data/recruiter")
JOB_DESCRIPTIONS = {
    "AI Adoption & Delivery Specialist": "test_data/jd_01.txt",
    "Senior Business Analyst, GenAI": "test_data/jd_02.txt",
}


@st.cache_data(show_spinner=False)
def blind_cv(text):
    """Blind a CV once and remember the answer, so switching back is instant."""
    return blind(text)


@st.cache_data(show_spinner=False)
def job_requirements(jd_text):
    """Read each job description once; every candidate is judged against the same list."""
    return extract_requirements(jd_text)


def render(max_analyses):
    with st.sidebar:
        st.header("Screen a candidate")
        st.caption("Synthetic CVs only. Real CVs can't be uploaded in this demo.")
        cv_files = sorted(CV_FOLDER.glob("cv_*.txt"))
        cv_file = st.selectbox("1. Candidate", cv_files, format_func=lambda p: f"Synthetic CV {p.stem[-2:]}")
        job = st.selectbox("2. Job", list(JOB_DESCRIPTIONS))
        run = st.button("Analyse the blind CV", type="primary", width="stretch")
        st.caption("Only the blind version is sent to Claude on Amazon Bedrock in the EU.")

    st.title("FitProof · Recruiter mode")
    st.warning(
        "**Demonstration only.** Synthetic CVs, not legal advice, and not for real hiring decisions. "
        "FitProof never rejects anyone; a person makes every decision."
    )

    original = cv_file.read_text()
    with st.spinner("Loading the redaction model. The first time takes about 20 seconds..."):
        blind_text, removed = blind_cv(original)

    # ---------- What was removed ----------
    st.subheader("Blind screening")
    counts = Counter(item["type"] for item in removed)
    summary = " · ".join(f"{n} {kind.replace('_', ' ').lower()}" for kind, n in counts.most_common())
    st.markdown(f"**{len(removed)} details removed** before the AI sees the CV: {summary}")
    left, right = st.columns(2)
    left.markdown("**Original** (synthetic)")
    left.code(original, language=None, wrap_lines=True)
    right.markdown("**What the AI sees**")
    right.code(blind_text, language=None, wrap_lines=True)
    st.caption(
        "Blinding removes direct identifiers. It doesn't remove bias: university, employers and dates "
        "stay visible because they matter for the match, and their effect is tested separately."
    )

    # ---------- Analysis of the blind CV only ----------
    selection = (cv_file.name, job)
    analyses_used = st.session_state.get("analyses_used", 0)
    if run and analyses_used >= max_analyses:
        st.warning(f"This demo allows {max_analyses} analyses per visit.")
    elif run:
        with st.spinner("Claude is reading the job description and the blind CV..."):
            try:
                jd_text = Path(JOB_DESCRIPTIONS[job]).read_text()
                st.session_state["recruiter_result"] = (selection, analyse(jd_text, blind_text, job_requirements(jd_text)))
                st.session_state["analyses_used"] = analyses_used + 1
            except Exception as error:
                st.session_state.pop("recruiter_result", None)
                st.error(f"The analysis failed: {error}")

    saved = st.session_state.get("recruiter_result")
    if saved and saved[0] == selection:
        st.success("**Blind screening: on.** Claude saw only the blind CV on the right.")
        show_result(saved[1], key="recruiter")
    else:
        st.info("Press **Analyse the blind CV** to see how this candidate matches the job.")