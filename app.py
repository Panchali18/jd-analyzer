import io
import json

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from ai_matcher import analyse
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


# ---------- Mode switch ----------
mode = st.sidebar.segmented_control("Mode", ["Candidate", "Recruiter (demo)"], default="Candidate")
if mode == "Recruiter (demo)":
    import recruiter  # loaded only when needed, so candidate mode stays light

    recruiter.render(MAX_ANALYSES)
    st.stop()

# ---------- Sidebar: inputs ----------
with st.sidebar:
    st.header("Check your fit")
    st.markdown("**1. The job**")
    jd_method = st.radio(
        "Job description", ["Paste text", "Upload file"], horizontal=True, label_visibility="collapsed"
    )
    if jd_method == "Paste text":
        jd_text = st.text_area(
            "Job description",
            height=250,
            placeholder="Paste the full job description here, then click outside the box.",
            label_visibility="collapsed",
        )
    else:
        jd_text = read_file(
            st.file_uploader("Job description file", type=["pdf", "txt"], label_visibility="collapsed")
        )
    st.markdown("**2. Your CV**")
    cv_text = read_file(st.file_uploader("CV file", type=["pdf", "txt"], label_visibility="collapsed"))
    run = st.button("Analyse my fit", type="primary", width="stretch", disabled=not (jd_text and cv_text))
    st.caption("Your CV is analysed by Claude on Amazon Bedrock in the EU. Nothing is stored.")
    st.divider()
    sample = st.button("Try a sample", width="stretch")
    st.caption("See an example result for a fictional CV, with no upload needed.")

# ---------- Sample result: no AI call, no cost ----------
if sample:
    with open(SAMPLE_RESULT) as f:
        st.session_state["result"] = json.load(f)
    st.session_state["is_sample"] = True

# ---------- Call Claude only when the button is pressed, within the limits ----------
analyses_used = st.session_state.get("analyses_used", 0)
if run and analyses_used >= MAX_ANALYSES:
    st.warning(f"This demo allows {MAX_ANALYSES} analyses per visit. Try the sample, or come back later.")
elif run and (len(jd_text) > MAX_CHARACTERS or len(cv_text) > MAX_CHARACTERS):
    st.warning("That document is too long for this demo. Please use a job description and CV under about 8 pages each.")
elif run:
    with st.spinner("Claude is reading the job description and your CV..."):
        try:
            st.session_state["result"] = analyse(jd_text, cv_text)
            st.session_state["is_sample"] = False
            st.session_state["analyses_used"] = analyses_used + 1
        except Exception as error:
            st.session_state.pop("result", None)
            st.error(f"The analysis failed: {error}")

st.title("FitProof")
st.caption("See your fit. Prove it with your CV.")

result = st.session_state.get("result")
if not result:
    with st.container(border=True):
        st.markdown("#### How it works")
        st.markdown(
            "1. Paste a job description and upload your CV on the left.\n"
            "2. Press **Analyse my fit**. It takes about 15 seconds.\n"
            "3. Get a verdict and score, the CV lines that prove each requirement, "
            "any must-haves you're missing, and suggested rewrites."
        )
    st.stop()

if st.session_state.get("is_sample"):
    st.info("**Sample result.** A fictional CV (Jordan Ellis) analysed against a real job advert.")
show_result(result)