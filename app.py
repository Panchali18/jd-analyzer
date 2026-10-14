import io
import json

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from ai_matcher import analyse, extract_requirements
from results_view import show_result

load_dotenv()

st.set_page_config(page_title="FitProof", page_icon="📄", layout="wide")

MAX_ANALYSES = 3  # per visit, to protect the AI credits
MAX_CHARACTERS = 20000  # per document, roughly 8 pages
SAMPLE_RESULT = "sample/sample_result.json"


def read_file(uploaded_file):
    """Turn an uploaded PDF or text file into plain text."""
    if uploaded_file is None:
        return ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return uploaded_file.getvalue().decode("utf-8", errors="ignore")


def check_fit(jd_text, cv_text):
    """Run the analysis and show each step as it happens."""
    with st.status("Checking your fit...", expanded=True) as status:
        st.write("Reading the job description...")
        requirements = extract_requirements(jd_text)
        st.write(f"✓ Found {len(requirements['requirements'])} requirements")
        st.write("Looking for evidence of each one in your CV...")
        try:
            result = analyse(jd_text, cv_text, requirements)
        except Exception:
            status.update(label="Something went wrong", state="error")
            raise
        status.update(label="Done", state="complete", expanded=False)
    return result


# ---------- Mode switch ----------
mode = st.sidebar.segmented_control("Mode", ["Candidate", "Recruiter (demo)"], default="Candidate")
if mode == "Recruiter (demo)":
    import recruiter  # loaded only when needed, so candidate mode stays light

    recruiter.render(MAX_ANALYSES)
    st.stop()

st.title("FitProof")
st.caption("See your fit. Prove it with your CV.")

# ---------- Inputs: open at the start, folded away once there's a result ----------
has_result = "result" in st.session_state
with st.expander("Job description and CV", expanded=not has_result):
    job_column, cv_column = st.columns(2)
    with job_column:
        st.markdown("**1. The job**")
        jd_method = st.radio(
            "Job description", ["Paste text", "Upload file"], horizontal=True, label_visibility="collapsed", key="jd_method"
        )
        if jd_method == "Paste text":
            jd_text = st.text_area(
                "Job description",
                height=220,
                placeholder="Paste the full job description here.",
                label_visibility="collapsed",
                key="jd_paste",
            )
        else:
            jd_text = read_file(
                st.file_uploader("Job description file", type=["pdf", "txt"], label_visibility="collapsed", key="jd_file")
            )
    with cv_column:
        st.markdown("**2. Your CV**")
        cv_text = read_file(
            st.file_uploader("CV file", type=["pdf", "txt"], label_visibility="collapsed", key="cv_file")
        )
        st.caption("PDF or text. Your CV is analysed by Claude on Amazon Bedrock in the EU and never stored.")
    run_column, sample_column, _ = st.columns([1, 1, 2])
    run = run_column.button("Analyse my fit", type="primary", width="stretch")
    sample = sample_column.button("Try a sample", width="stretch", help="A fictional CV, no upload needed")

# ---------- Sample result: no AI call, no cost ----------
if sample:
    with open(SAMPLE_RESULT) as f:
        st.session_state["result"] = json.load(f)
    st.session_state["is_sample"] = True
    st.rerun()  # fold the inputs away and show the result

# ---------- Call Claude only when the button is pressed, within the limits ----------
analyses_used = st.session_state.get("analyses_used", 0)
if run and not (jd_text and cv_text):
    st.warning("Add a job description and a CV first.")
elif run and analyses_used >= MAX_ANALYSES:
    st.warning(f"This demo allows {MAX_ANALYSES} analyses per visit. Try the sample, or come back later.")
elif run and (len(jd_text) > MAX_CHARACTERS or len(cv_text) > MAX_CHARACTERS):
    st.warning("That document is too long for this demo. Please use a job description and CV under about 8 pages each.")
elif run:
    try:
        st.session_state["result"] = check_fit(jd_text, cv_text)
        st.session_state["is_sample"] = False
        st.session_state["analyses_used"] = analyses_used + 1
        st.rerun()  # fold the inputs away and show the result
    except Exception as error:
        st.session_state.pop("result", None)
        st.error(f"The analysis failed: {error}")

result = st.session_state.get("result")
if not result:
    st.markdown(
        "Add a job description and your CV above, then press **Analyse my fit**. In about 20 seconds you'll see "
        "which requirements your CV proves, with the line that proves each one, the gaps, and any must-haves you're missing."
    )
    st.stop()

if st.session_state.get("is_sample"):
    st.info("**Sample result.** A fictional CV (Jordan Ellis) analysed against a real job advert.")
show_result(result)
