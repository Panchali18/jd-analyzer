import difflib
import io

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from ai_matcher import analyse

load_dotenv()

st.set_page_config(page_title="FitProof", page_icon="📄", layout="wide")

STATUS_ICON = {"evidenced": "✅", "partly evidenced": "🟡", "missing": "❌"}
VERDICT_COLOUR = {"Strong fit": "green", "Possible fit": "orange", "Weak fit": "red"}
GROUPS = [("required", "Required"), ("qualification", "Qualifications"), ("nice to have", "Nice to have")]


def read_file(uploaded_file):
    """Turn an uploaded PDF or text file into plain text."""
    if uploaded_file is None:
        return ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return uploaded_file.getvalue().decode("utf-8", errors="ignore")


def highlight_additions(current, suggested):
    """Mark the words a suggestion adds or changes, so overclaims stand out."""
    old = current.split()
    new = suggested.split()
    tidy = lambda words: [w.lower().strip(".,;:()") for w in words]
    matcher = difflib.SequenceMatcher(a=tidy(old), b=tidy(new), autojunk=False)
    parts = []
    for tag, _, _, start, end in matcher.get_opcodes():
        chunk = " ".join(new[start:end]).replace("$", "\\$")
        if not chunk:
            continue
        if tag in ("insert", "replace"):
            parts.append(f":orange-background[**{chunk}**]")
        else:
            parts.append(chunk)
    return " ".join(parts)

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

# ---------- Call Claude only when the button is pressed ----------
if run:
    with st.spinner("Claude is reading the job description and your CV..."):
        try:
            st.session_state["result"] = analyse(jd_text, cv_text)
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

# ---------- Summary card ----------
requirements = result["requirements"]
counts = {status: sum(1 for r in requirements if r["status"] == status) for status in STATUS_ICON}
verdict = result["verdict"]

with st.container(border=True):
    st.subheader(result.get("role_title") or "Job description")
    left, right = st.columns([3, 1])
    left.markdown(f"### :{VERDICT_COLOUR.get(verdict, 'red')}[{verdict}]")
    left.caption(
        f"{counts['evidenced']} evidenced · {counts['partly evidenced']} partly evidenced · {counts['missing']} missing"
    )
    right.metric("Match score", f"{result['score']}%")

if result["deal_breakers"]:
    with st.container(border=True):
        st.error("**Deal-breakers:** the job description says these are mandatory, and your CV doesn't show them.")
        for item in result["deal_breakers"]:
            st.markdown(f"**{item['requirement']}**")
            st.caption(f"Job description says: \"{item.get('jd_evidence', '')}\"")
            if item.get("related_cv_evidence"):
                st.caption(f"Related in your CV: \"{item['related_cv_evidence']}\"")

# ---------- Tabs ----------
rewrites = result.get("rewrite_suggestions") or []
extras = [e for e in (result.get("extra_strengths") or []) if e]
tab_requirements, tab_rewrites, tab_extras = st.tabs(
    [f"Requirements ({len(requirements)})", f"CV rewrites ({len(rewrites)})", f"Extra strengths ({len(extras)})"]
)

with tab_requirements:
    known_types = [key for key, _ in GROUPS]
    for type_key, label in GROUPS + [("other", "Other")]:
        if type_key == "other":
            group = [r for r in requirements if r["type"] not in known_types]
        else:
            group = [r for r in requirements if r["type"] == type_key]
        if not group:
            continue
        st.markdown(f"#### {label}")
        for req in group:
            icon = STATUS_ICON.get(req["status"], "❔")
            quotes = req.get("cv_evidence") or []
            if isinstance(quotes, str):
                quotes = [quotes]
            if req["status"] == "missing" or not quotes:
                st.markdown(f"{icon} {req['skill']}")
                if req.get("note"):
                    st.caption(req["note"])
                continue
            with st.expander(f"{icon} {req['skill']}"):
                for quote in quotes:
                    st.markdown(f"> {quote}")
                if req.get("note"):
                    st.caption(req["note"])
                if not req.get("evidence_verified"):
                    st.warning("This quote wasn't found word for word in your CV. Check it before relying on it.")

with tab_rewrites:
    if rewrites:
        st.warning(
            "These are drafts. Words the AI added are highlighted. Only use a suggestion if every highlighted word is true."
        )
    else:
        st.write("No rewrite suggestions for this role.")
    for item in rewrites:
        with st.container(border=True):
            st.caption(f"Covers: {item.get('covers', '')}")
            st.markdown(f"**Now:** {item.get('current_cv_line', '')}")
            st.markdown(
                "**Suggested:** " + highlight_additions(item.get("current_cv_line", ""), item.get("suggested_line", ""))
            )

with tab_extras:
    if extras:
        st.write("Relevant strengths from your CV that this job description didn't ask for:")
        for strength in extras:
            st.markdown(f"- {strength}")
    else:
        st.write("No extra strengths listed.")

st.caption("AI-generated analysis. Check the quoted evidence before relying on it.")