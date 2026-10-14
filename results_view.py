"""Shows a FitProof analysis: summary card, deal-breakers and the three tabs.
Used by both candidate mode (app.py) and recruiter mode (recruiter.py)."""
import difflib

import streamlit as st

from ai_matcher import calculate_score

STATUS_ICON = {"evidenced": "✅", "partly evidenced": "🟡", "missing": "❌"}
VERDICT_COLOUR = {"Strong fit": "green", "Possible fit": "orange", "Weak fit": "red"}
GROUPS = [("required", "Required"), ("qualification", "Qualifications"), ("nice to have", "Nice to have")]
STATUS_ORDER = {"missing": 0, "partly evidenced": 1, "evidenced": 2}
BAR_COLOURS = {"evidenced": "#1F7A4D", "partly evidenced": "#E0A100", "missing": "#B42318"}


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


def breakdown_bar(counts):
    """A thin bar split into green, amber and red by the share of each status."""
    total = sum(counts.values()) or 1
    segments = "".join(
        f'<div style="width:{counts[status] / total * 100}%;background:{colour}"></div>'
        for status, colour in BAR_COLOURS.items()
        if counts[status]
    )
    return f'<div style="display:flex;height:10px;border-radius:5px;overflow:hidden;margin:4px 0 8px">{segments}</div>'



def show_result(result, key="candidate", recruiter=False):
    """Draw the result. `key` keeps the filter buttons separate for each mode.
    recruiter=True speaks about "the CV" and hides the CV rewrites, which are for candidates."""
    whose = "the CV" if recruiter else "your CV"
    # ---------- Summary card ----------
    requirements = result["requirements"]
    counts = {status: sum(1 for r in requirements if r["status"] == status) for status in STATUS_ICON}
    verdict = result["verdict"]

    with st.container(border=True):
        st.subheader(result.get("role_title") or "Job description")
        left, right = st.columns([3, 1])
        left.markdown(f"### :{VERDICT_COLOUR.get(verdict, 'red')}[{verdict}]")
        partly = f", partly for {counts['partly evidenced']} more" if counts["partly evidenced"] else ""
        left.markdown(f"Evidence for **{counts['evidenced']} of {len(requirements)}** requirements{partly}")
        right.metric("Match score", f"{result['score']}%")
        st.html(breakdown_bar(counts))
        st.caption(
            f":green[■] {counts['evidenced']} evidenced  ·  :orange[■] {counts['partly evidenced']} partly evidenced  ·  "
            f":red[■] {counts['missing']} missing"
        )
        group_columns = st.columns(len(GROUPS))
        for column, (type_key, label) in zip(group_columns, GROUPS):
            group = [r for r in requirements if r["type"] == type_key]
            if group:
                column.metric(label, f"{calculate_score({'requirements': group})}%", help=f"{len(group)} requirements")
            else:
                column.metric(label, "None", help="The job description doesn't list any")

    if result["deal_breakers"]:
        with st.container(border=True):
            st.error(f"**Deal-breakers:** the job description says these are mandatory, and {whose} doesn't show them.")
            for item in result["deal_breakers"]:
                st.markdown(f"**{item['requirement']}**")
                st.caption(f"Job description says: \"{item.get('jd_evidence', '')}\"")
                if item.get("related_cv_evidence"):
                    st.caption(f"Related in {whose}: \"{item['related_cv_evidence']}\"")

    # ---------- Tabs ----------
    rewrites = result.get("rewrite_suggestions") or []
    extras = [e for e in (result.get("extra_strengths") or []) if e]
    names = [f"Requirements ({len(requirements)})", f"Extra strengths ({len(extras)})"]
    if not recruiter:
        names.insert(1, f"CV rewrites ({len(rewrites)})")
    tabs = st.tabs(names)
    tab_requirements, tab_extras = tabs[0], tabs[-1]

    with tab_requirements:
        show = st.segmented_control("Show", ["All", "Gaps only", "Evidenced only"], default="All", key=f"{key}_show")
        if show == "Gaps only":
            visible = [r for r in requirements if r["status"] != "evidenced"]
        elif show == "Evidenced only":
            visible = [r for r in requirements if r["status"] == "evidenced"]
        else:
            visible = requirements
        visible = sorted(visible, key=lambda r: STATUS_ORDER.get(r["status"], 0))
        if not visible:
            st.write("Nothing to show for this filter.")
        known_types = [type_key for type_key, _ in GROUPS]
        for type_key, label in GROUPS + [("other", "Other")]:
            if type_key == "other":
                group = [r for r in visible if r["type"] not in known_types]
            else:
                group = [r for r in visible if r["type"] == type_key]
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
                        st.warning(f"This quote wasn't found word for word in {whose}. Check it before relying on it.")

    if not recruiter:
        with tabs[1]:
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
            st.write(f"Relevant strengths from {whose} that this job description didn't ask for:")
            for strength in extras:
                st.markdown(f"- {strength}")
        else:
            st.write("No extra strengths listed.")

    st.caption("AI-generated analysis. Check the quoted evidence before relying on it.")    