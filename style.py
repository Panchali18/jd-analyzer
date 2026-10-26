"""FitProof's look: one shared style sheet and small HTML pieces.
The memorable element is the evidence: a CV line set like a document excerpt,
with a highlighter mark behind it. Everything else stays quiet."""
import html

import streamlit as st

INK = "#1F2A44"
HIGHLIGHT = "#E4F57A"
STATUS_COLOUR = {"evidenced": "#0F766E", "partly evidenced": "#A16207", "missing": "#B42318"}
STATUS_WORD = {"evidenced": "Met", "partly evidenced": "Partly met", "missing": "Not shown"}

CSS = f"""
<style>
.block-container {{ max-width: 920px; padding-top: 4rem; }}
h1, h2, h3 {{ color: {INK}; letter-spacing: -0.01em; }}
.fp-wordmark {{ font-size: 1.55rem; font-weight: 600; color: {INK}; letter-spacing: -0.02em; margin: 0; }}
.fp-promise {{ font-size: 1.9rem; line-height: 1.2; font-weight: 600; color: {INK}; margin: 0.6rem 0 0.4rem; max-width: 30ch; }}
.fp-sub {{ color: #4B5468; font-size: 1.02rem; line-height: 1.5; max-width: 60ch; margin: 0 0 1rem; }}
.fp-pair {{ background: #FFFFFF; border: 1px solid #DDE1E8; border-radius: 0.5rem; padding: 1rem 1.1rem; margin: 0.4rem 0 1rem; }}
.fp-pair-label {{ color: #6B7385; font-size: 0.82rem; margin: 0 0 0.15rem; }}
.fp-pair-ask {{ color: {INK}; font-weight: 500; margin: 0 0 0.8rem; line-height: 1.4; }}
.fp-quote {{ font-family: "IBM Plex Serif", Georgia, serif; font-size: 1.02rem; line-height: 1.55; color: #1E2433; margin: 0; }}
.fp-quote mark {{ background: linear-gradient(transparent 42%, {HIGHLIGHT} 42%, {HIGHLIGHT} 92%, transparent 92%);
  color: inherit; padding: 0 0.15em; box-decoration-break: clone; -webkit-box-decoration-break: clone; }}
.fp-verdict {{ font-size: 1.9rem; font-weight: 600; margin: 0.1rem 0 0.2rem; }}
.fp-count {{ font-size: 1.05rem; color: #1E2433; margin: 0 0 0.6rem; }}
.fp-score {{ color: #6B7385; font-size: 0.92rem; margin: 0 0 0.6rem; }}
.fp-bar {{ display: flex; height: 8px; border-radius: 4px; overflow: hidden; margin: 0.2rem 0 0.5rem; background: #ECEEF2; }}
.fp-legend {{ color: #4B5468; font-size: 0.88rem; display: flex; flex-wrap: wrap; gap: 0.4rem 1.1rem; margin: 0; }}
.fp-dot {{ display: inline-block; width: 0.6em; height: 0.6em; border-radius: 50%; margin-right: 0.35em; }}
.fp-gap-say {{ margin: 0.5rem 0 0.3rem; line-height: 1.5; }}
.fp-gap-close {{ color: #4B5468; margin: 0; line-height: 1.5; }}
/* The selected mode is filled in, so it's clear which side you're on */
.st-key-mode button[aria-checked="true"] {{ background: {INK} !important; color: #FFFFFF !important; border-color: {INK} !important; }}
.st-key-mode button[aria-checked="true"] p {{ color: #FFFFFF !important; }}
/* The job brief: a light blue tint and an ink edge mark the thing every candidate is measured against */
.st-key-job_brief {{ background: #EEF2FA; border-left: 4px solid {INK}; }}
@media (max-width: 640px) {{
  .block-container {{ padding-top: 3.75rem; }}
  .fp-promise {{ font-size: 1.5rem; }}
  .fp-verdict {{ font-size: 1.55rem; }}
}}
</style>
"""


def apply():
    st.html(CSS)


def esc(text):
    return html.escape(text or "")


def quote(text):
    """A CV line set like a document excerpt, with the highlighter behind it."""
    return f'<p class="fp-quote"><mark>{esc(text)}</mark></p>'


def evidence_pair(asks, cv_line, ask_label="The job asks for", cv_label="Your CV shows"):
    return (
        f'<div class="fp-pair"><p class="fp-pair-label">{esc(ask_label)}</p>'
        f'<p class="fp-pair-ask">{esc(asks)}</p>'
        f'<p class="fp-pair-label">{esc(cv_label)}</p>{quote(cv_line)}</div>'
    )


def bar(counts):
    total = sum(counts.values()) or 1
    segments = "".join(
        f'<div style="width:{counts[s] / total * 100}%;background:{c}"></div>'
        for s, c in STATUS_COLOUR.items()
        if counts.get(s)
    )
    legend = "".join(
        f'<span><span class="fp-dot" style="background:{c}"></span>{counts.get(s, 0)} {STATUS_WORD[s].lower()}</span>'
        for s, c in STATUS_COLOUR.items()
    )
    return f'<div class="fp-bar">{segments}</div><p class="fp-legend">{legend}</p>'
