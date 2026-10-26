import io
import json

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from ai_matcher import analyse, extract_requirements
from job_link import JobLinkError, fetch_job
import style
from results_view import show_result, strongest_evidence

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


@st.cache_data(show_spinner=False, ttl=3600)
def job_from_link(url):
    """Fetch each link once an hour at most."""
    return fetch_job(url)


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


def example_pair():
    """A real requirement and CV line from the saved sample, for the start screen."""
    with open(SAMPLE_RESULT) as f:
        sample = json.load(f)
    picks = strongest_evidence(sample["requirements"], limit=1)
    return picks[0] if picks else None


style.apply()

# ---------- Header: name and mode switch on the page, so phones see both ----------
name_column, mode_column = st.columns([3, 2], vertical_alignment="center")
name_column.html('<p class="fp-wordmark">FitProof</p>')
mode = mode_column.segmented_control(
    "Mode", ["Candidate", "Recruiter"], default="Candidate", label_visibility="collapsed", key="mode"
)
if mode == "Recruiter":
    import recruiter  # loaded only when needed, so candidate mode stays light

    recruiter.render(MAX_ANALYSES)
    st.stop()

has_result = "result" in st.session_state

# ---------- Start screen: show the value before asking for anything ----------
sample = False
if not has_result and not st.session_state.get("show_inputs"):
    st.html(
        '<p class="fp-promise">See how well your CV proves you fit a job.</p>'
        '<p class="fp-sub">Paste a job, add your CV, and FitProof shows the line in your CV that proves each '
        "requirement, the gaps, and how to talk about them.</p>"
    )
    pair = example_pair()
    if pair:
        st.html(style.evidence_pair(*pair))
    example_column, own_column = st.columns(2)
    sample = example_column.button("See an example result", type="primary", width="stretch")
    if own_column.button("Check my own fit", width="stretch"):
        st.session_state["show_inputs"] = True
        st.rerun()
    st.caption("The example uses a fictional CV, so nothing is uploaded.")

# ---------- Inputs: open at the start, folded away once there's a result ----------
show_inputs = has_result or st.session_state.get("show_inputs")
run = False
jd_text = cv_text = ""
if show_inputs:
    with st.expander("Check another job" if has_result else "Your job and CV", expanded=not has_result):
        job_column, cv_column = st.columns(2)
        with job_column:
            st.markdown("**1. The job**")
            jd_method = st.radio(
                "Job description",
                ["Paste text", "Job link", "Upload file"],
                horizontal=True,
                label_visibility="collapsed",
                key="jd_method",
            )
            if jd_method == "Job link":
                jd_text = ""
                link = st.text_input(
                    "Job link",
                    placeholder="https://jobs.lever.co/company/...",
                    label_visibility="collapsed",
                    key="jd_link",
                )
                st.caption("Works for jobs posted through Greenhouse, Lever or Ashby. For other sites, paste the text.")
                if link:
                    try:
                        with st.spinner("Fetching the job..."):
                            title, jd_text = job_from_link(link)
                        st.success(f"Loaded: **{title or 'job description'}** ({len(jd_text):,} characters)")
                        with st.expander("Check the text"):
                            st.text(jd_text)
                    except JobLinkError as error:
                        st.warning(str(error))
            elif jd_method == "Paste text":
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
        run = st.button("Analyse my fit", type="primary")

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
    if show_inputs:
        st.caption("Add the job and your CV, then press Analyse my fit. It takes about 20 seconds.")
    st.stop()

if st.session_state.get("is_sample"):
    note_column, own_column = st.columns([3, 1], vertical_alignment="center")
    note_column.info("**Example result.** A fictional CV (Jordan Ellis) checked against a real job advert.")
    if own_column.button("Check my own fit", width="stretch", key="own_after_sample"):
        st.session_state.pop("result", None)
        st.session_state["show_inputs"] = True
        st.rerun()
show_result(result)
