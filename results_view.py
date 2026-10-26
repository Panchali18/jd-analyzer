"""Shows a FitProof analysis for a candidate: the verdict and evidence count first, then the
strongest evidence, then how to talk about the gaps. The full list and the scores per group
are folded away for anyone who wants them."""
import streamlit as st

import style
from ai_matcher import calculate_score

STATUS_ICON = {"evidenced": ":green[●]", "partly evidenced": ":orange[●]", "missing": ":red[●]"}
VERDICT_COLOUR = {"Strong fit": "#0F766E", "Possible fit": "#A16207", "Weak fit": "#B42318"}
GROUPS = [("required", "Required"), ("qualification", "Qualifications"), ("nice to have", "Nice to have")]
STATUS_ORDER = {"missing": 0, "partly evidenced": 1, "evidenced": 2}
REQUIRED_TYPES = ("required", "qualification")


def strongest_evidence(requirements, limit=3):
    """Required items that are met, with a quote the code found word for word in the CV."""
    picks = []
    for req in requirements:
        quotes = req.get("cv_evidence") or []
        if isinstance(quotes, str):
            quotes = [quotes]
        if req["type"] in REQUIRED_TYPES and req["status"] == "evidenced" and req.get("evidence_verified") and quotes:
            picks.append((req["skill"], quotes[0]))
    return picks[:limit]


def as_markdown(result, requirements, counts):
    """A plain summary to keep with application notes."""
    lines = [
        f"# {result.get('role_title') or 'Job description'}",
        "",
        f"{result['verdict']}: evidence for {counts['evidenced']} of {len(requirements)} requirements, "
        f"partly for {counts['partly evidenced']}. Match score {result['score']}%.",
        "",
        "## Requirements",
    ]
    for req in sorted(requirements, key=lambda r: STATUS_ORDER.get(r["status"], 0), reverse=True):
        lines.append(f"- {style.STATUS_WORD.get(req['status'], req['status'])}: {req['skill']}")
        quotes = req.get("cv_evidence") or []
        for q in [quotes] if isinstance(quotes, str) else quotes:
            lines.append(f'  - "{q}"')
    gaps = result.get("gap_talk") or []
    if gaps:
        lines += ["", "## Gaps and how to talk about them"]
        for gap in gaps:
            lines += [f"### {gap.get('requirement', '')}", f"How to say it: {gap.get('how_to_say_it', '')}"]
            if gap.get("how_to_close_it"):
                lines.append(f"How to close it: {gap['how_to_close_it']}")
    checks = result.get("eligibility_checks") or []
    if checks:
        lines += ["", "## Check yourself"] + [f"- {c['requirement']}" for c in checks]
    lines += ["", "AI-generated analysis by FitProof. Check the quoted evidence before relying on it."]
    return "\n".join(lines)


def show_full_list(requirements, key):
    show = st.segmented_control("Show", ["All", "Gaps only", "Met only"], default="All", key=f"{key}_show")
    if show == "Gaps only":
        visible = [r for r in requirements if r["status"] != "evidenced"]
    elif show == "Met only":
        visible = [r for r in requirements if r["status"] == "evidenced"]
    else:
        visible = requirements
    visible = sorted(visible, key=lambda r: STATUS_ORDER.get(r["status"], 0))
    if not visible:
        st.write("Nothing to show for this filter.")
    known_types = [type_key for type_key, _ in GROUPS]
    for type_key, label in GROUPS + [("other", "Other")]:
        group = [r for r in visible if (r["type"] not in known_types if type_key == "other" else r["type"] == type_key)]
        if not group:
            continue
        all_of_type = [r for r in requirements if r["type"] == type_key]
        score = f" · {calculate_score({'requirements': all_of_type})}% met" if all_of_type else ""
        st.markdown(f"**{label}**{score}")
        for req in group:
            icon = STATUS_ICON.get(req["status"], "○")
            quotes = req.get("cv_evidence") or []
            if isinstance(quotes, str):
                quotes = [quotes]
            if req["status"] == "missing" or not quotes:
                st.markdown(f"{icon} {req['skill']}")
                if req.get("note"):
                    st.caption(req["note"])
                continue
            with st.expander(f"{icon} {req['skill']}"):
                for q in quotes:
                    st.html(style.quote(q))
                if req.get("note"):
                    st.caption(req["note"])
                if not req.get("evidence_verified"):
                    st.warning("This quote wasn't found word for word in your CV. Check it before relying on it.")


def show_result(result, key="candidate", recruiter=False):
    """Draw a candidate's result. (Recruiter mode has its own review screen.)"""
    whose = "the CV" if recruiter else "your CV"
    requirements = [r for r in result["requirements"] if r["type"] != "eligibility"]
    counts = {status: sum(1 for r in requirements if r["status"] == status) for status in STATUS_ORDER}
    verdict = result["verdict"]
    colour = VERDICT_COLOUR.get(verdict, "#B42318")
    partly = f", partly for {counts['partly evidenced']} more" if counts["partly evidenced"] else ""

    # ---------- Verdict: count first, score small ----------
    with st.container(border=True):
        st.markdown(f"**{result.get('role_title') or 'Job description'}**")
        st.html(
            f'<p class="fp-verdict" style="color:{colour}">{style.esc(verdict)}</p>'
            f'<p class="fp-count">Evidence for <strong>{counts["evidenced"]} of {len(requirements)}</strong> '
            f"requirements{partly}</p>"
            f'<p class="fp-score">Match score {result["score"]}%, weighted towards required items</p>'
            + style.bar(counts)
        )

    for item in result.get("deal_breakers") or []:
        with st.container(border=True):
            st.error(f"**Must-have missing:** {item['requirement']}")
            st.caption(f"The job description says: \"{item.get('jd_evidence', '')}\"")
            if item.get("related_cv_evidence"):
                st.caption(f"Closest in {whose}: \"{item['related_cv_evidence']}\"")

    checks = result.get("eligibility_checks") or []
    if checks:
        with st.container(border=True):
            st.info("**Check yourself:** FitProof can't tell these from a CV, so they aren't in the score or the verdict.")
            for item in checks:
                st.markdown(item["requirement"])
                if item.get("jd_evidence"):
                    st.caption(f"The job description says: \"{item['jd_evidence']}\"")

    # ---------- The strongest evidence ----------
    picks = strongest_evidence(requirements)
    if picks:
        st.subheader("Your strongest evidence", anchor=False)
        for asks, line in picks:
            st.html(style.evidence_pair(asks, line))

    # ---------- Gaps ----------
    gaps = result.get("gap_talk") or []
    if gaps and not recruiter:
        st.subheader("Gaps and how to talk about them", anchor=False)
        st.caption("For a cover letter or interview. Each line only uses experience your CV shows. Read it before you use it.")
        for gap in gaps:
            with st.container(border=True):
                st.markdown(f"**{gap.get('requirement', '')}**")
                if gap.get("closest_cv_evidence"):
                    st.html('<p class="fp-pair-label">Closest in your CV</p>' + style.quote(gap["closest_cv_evidence"]))
                st.html(
                    f'<p class="fp-gap-say"><strong>How to say it:</strong> {style.esc(gap.get("how_to_say_it", ""))}</p>'
                    + (
                        f'<p class="fp-gap-close"><strong>How to close it:</strong> {style.esc(gap["how_to_close_it"])}</p>'
                        if gap.get("how_to_close_it")
                        else ""
                    )
                )

    # ---------- Everything else, folded ----------
    with st.expander(f"All {len(requirements)} requirements"):
        show_full_list(requirements, key)
    extras = [e for e in (result.get("extra_strengths") or []) if e]
    if extras:
        with st.expander(f"Strengths the job didn't ask for ({len(extras)})"):
            for strength in extras:
                st.markdown(f"- {strength}")

    if not recruiter:
        st.download_button(
            "Download this analysis",
            as_markdown(result, requirements, counts),
            file_name="fitproof_analysis.md",
            mime="text/markdown",
            key=f"{key}_download",
        )
    st.caption("AI-generated analysis. Check the quoted evidence before relying on it.")
