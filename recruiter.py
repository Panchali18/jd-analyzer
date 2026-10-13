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


def show_blind_cv(original, blind_text, removed):
    """The blind CV, with the original one click away."""
    counts = Counter(item["type"] for item in removed)
    summary = " · ".join(f"{n} {kind.replace('_', ' ').lower()}" for kind, n in counts.most_common())
    st.markdown(f"**{len(removed)} details removed** before the AI sees the CV: {summary}")
    if st.toggle("Compare with the original", key="recruiter_compare"):
        left, right = st.columns(2)
        left.markdown("**Original**")
        left.code(original, language=None, wrap_lines=True)
        right.markdown("**What the AI sees**")
        right.code(blind_text, language=None, wrap_lines=True)
    else:
        st.code(blind_text, language=None, wrap_lines=True)
    st.caption(
        "Blinding removes direct identifiers. It doesn't remove bias: university, employers and dates "
        "stay visible because they matter for the match, and their effect is tested separately."
    )


def screen(jd_text, blind_text):
    """Run the screening and show each step as it happens."""
    with st.status("Screening the blind CV...", expanded=True) as status:
        st.write("✓ Personal details removed")
        st.write("Reading the job description...")
        requirements = job_requirements(jd_text)
        st.write(f"✓ {len(requirements['requirements'])} requirements, the same for every candidate")
        st.write("Checking the blind CV against each requirement...")
        result = analyse(jd_text, blind_text, requirements)
        status.update(label="Screening done", state="complete", expanded=False)
    return result


def render(max_analyses):
    with st.sidebar:
        st.header("Screen a candidate")
        cv_files = sorted(CV_FOLDER.glob("cv_*.txt"))
        cv_file = st.selectbox(
            "1. Candidate",
            cv_files,
            index=None,
            placeholder="Choose a candidate",
            format_func=lambda p: f"Candidate {p.stem[-2:]}",
        )
        job = st.selectbox("2. Job", list(JOB_DESCRIPTIONS))
        run = st.button("Analyse the blind CV", type="primary", width="stretch", disabled=cv_file is None)
        st.caption("Only the blind version is sent to Claude on Amazon Bedrock in the EU.")

    st.title("FitProof · Recruiter mode")
    st.info("Demo: all CVs and candidates are fictional.")

    if cv_file is None:
        st.markdown(
            "Choose a candidate on the left. You'll see their CV with personal details removed, "
            "then you can analyse it against the job."
        )
        return

    original = cv_file.read_text()
    with st.spinner("Loading the redaction model. The first time takes about 20 seconds..."):
        blind_text, removed = blind_cv(original)

    # ---------- Analysis of the blind CV only ----------
    selection = (cv_file.name, job)
    analyses_used = st.session_state.get("analyses_used", 0)
    if run and analyses_used >= max_analyses:
        st.warning(f"This demo allows {max_analyses} analyses per visit.")
    elif run:
        try:
            jd_text = Path(JOB_DESCRIPTIONS[job]).read_text()
            st.session_state["recruiter_result"] = (selection, screen(jd_text, blind_text))
            st.session_state["analyses_used"] = analyses_used + 1
        except Exception as error:
            st.session_state.pop("recruiter_result", None)
            st.error(f"The analysis failed: {error}")

    # ---------- Result first, blind CV underneath ----------
    saved = st.session_state.get("recruiter_result")
    if saved and saved[0] == selection:
        st.success("**Blind screening: on.** Claude saw only the blind CV.")
        show_result(saved[1], key="recruiter", recruiter=True)
        with st.expander("The blind CV"):
            show_blind_cv(original, blind_text, removed)
    else:
        st.subheader("The blind CV")
        show_blind_cv(original, blind_text, removed)
