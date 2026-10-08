import io
import re

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from skills_dictionary import CATEGORY_DISPLAY_NAMES, get_skill_category, normalize_skill_name

load_dotenv()

st.set_page_config(page_title="JD Analyzer & CV Matcher", layout="wide")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills_from_text(text: str):
    if not text:
        return set()

    cleaned_text = normalize_text(text)
    found_skills = set()

    # Import the skill synonym map from the dictionary file
    from skills_dictionary import SKILL_SYNONYMS

    for synonym, canonical_skill in SKILL_SYNONYMS.items():
        pattern = r"\b" + re.escape(synonym) + r"\b"
        if re.search(pattern, cleaned_text):
            found_skills.add(canonical_skill)

    return found_skills


def read_pdf_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def read_text_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    return uploaded_file.read().decode("utf-8", errors="ignore")


st.title("📄 JD Analyzer & CV Matcher")
st.write("Analyze job descriptions and match them against your CV")

st.sidebar.header("📋 Input Your Information")
st.sidebar.subheader("Job Description")

jd_input_method = st.sidebar.radio("Choose JD input method:", ["📝 Paste Text", "📁 Upload File"])

jd_text = ""
if jd_input_method == "📝 Paste Text":
    jd_text = st.sidebar.text_area(
        "Paste your Job Description here:",
        height=220,
        placeholder="Paste the full JD text from LinkedIn, job boards, or emails.",
    )
elif jd_input_method == "📁 Upload File":
    jd_file = st.sidebar.file_uploader("Upload Job Description (PDF or TXT)", type=["pdf", "txt"])
    if jd_file:
        if jd_file.type == "application/pdf":
            jd_text = read_pdf_file(jd_file)
        else:
            jd_text = read_text_file(jd_file)

st.sidebar.subheader("Your CV")
cv_file = st.sidebar.file_uploader("Upload Your CV (PDF or TXT)", type=["pdf", "txt"])

cv_text = ""
if cv_file:
    if cv_file.type == "application/pdf":
        cv_text = read_pdf_file(cv_file)
    else:
        cv_text = read_text_file(cv_file)


if jd_text and cv_text:
    jd_skills = extract_skills_from_text(jd_text)
    cv_skills = extract_skills_from_text(cv_text)

    matched_skills = sorted(jd_skills.intersection(cv_skills), key=str.lower)
    missing_skills = sorted(jd_skills - cv_skills, key=str.lower)

    score = 0
    if jd_skills:
        score = round((len(matched_skills) / len(jd_skills)) * 100)

    st.success("✅ Both JD and CV loaded successfully!")

    with st.expander("📄 View Uploaded Content"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Job Description:**")
            st.write(jd_text[:800] + "..." if len(jd_text) > 800 else jd_text)

        with col2:
            st.write("**Your CV:**")
            st.write(cv_text[:800] + "..." if len(cv_text) > 800 else cv_text)

    st.subheader("📊 Match Result")
    st.metric("Match Score", f"{score}%")

    st.subheader("✅ Matched Skills")
    if matched_skills:
        for skill in matched_skills:
            st.write(f"• {skill}")
    else:
        st.write("No direct matches found.")

    st.subheader("❌ Missing Skills")
    if missing_skills:
        for skill in missing_skills:
            st.write(f"• {skill}")
    else:
        st.write("No missing skills found.")

    st.subheader("💡 Suggested CV Tailoring")
    if missing_skills:
        top_missing = missing_skills[:5]
        for skill in top_missing:
            st.write(f"- Add more evidence of '{skill}' in your CV, such as a project, responsibility, or achievement.")
    else:
        st.write("Your CV already covers most of the JD requirements.")

else:
    if not jd_text:
        st.info("👈 Please paste or upload a Job Description")
    if not cv_text:
        st.info("👈 Please upload your CV")

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Made with Streamlit")
