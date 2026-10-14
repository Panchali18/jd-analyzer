"""Fetch a job description from a job link. Works for job boards run on Greenhouse, Lever and Ashby,
which publish free public job APIs for exactly this. Other sites (LinkedIn, Indeed) don't, and scraping
is against their terms, so the user pastes the text instead."""
import html
import json
import re
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

TIMEOUT = 10  # seconds
MAX_BYTES = 5_000_000


class JobLinkError(ValueError):
    """A problem the user can fix, explained in plain words."""


def get_json(url):
    request = Request(url, headers={"User-Agent": "FitProof (portfolio demo)"})
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read(MAX_BYTES))
    except Exception as error:
        raise JobLinkError("Couldn't load that job. It may have closed, or the link may be wrong.") from error


def html_to_text(raw):
    """Job descriptions come as HTML (Greenhouse even escapes it twice): turn it into plain text."""
    text = html.unescape(html.unescape(raw or ""))
    text = re.sub(r"(?i)<\s*(br|/p|/li|/h\d|/div)\s*/?>", "\n", text)
    text = re.sub(r"(?i)<\s*li[^>]*>", "• ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def from_greenhouse(board, job_id, eu=False):
    path = f"/v1/boards/{board}/jobs/{job_id}"
    try:
        job = get_json(f"https://boards-api.eu.greenhouse.io{path}" if eu else f"https://boards-api.greenhouse.io{path}")
    except JobLinkError:
        if not eu:
            raise
        job = get_json(f"https://boards-api.greenhouse.io{path}")  # EU boards are sometimes served from the main API
    return job.get("title", ""), html_to_text(job.get("content", ""))


def from_lever(site, posting_id, eu=False):
    host = "api.eu.lever.co" if eu else "api.lever.co"
    posting = get_json(f"https://{host}/v0/postings/{site}/{posting_id}?mode=json")
    parts = [posting.get("descriptionPlain", "")]
    for section in posting.get("lists") or []:
        parts.append(section.get("text", ""))
        parts.append(html_to_text(section.get("content", "")))
    parts.append(posting.get("additionalPlain", ""))
    return posting.get("text", ""), "\n\n".join(p.strip() for p in parts if p and p.strip())


def from_ashby(board, job_id):
    jobs = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}").get("jobs") or []
    for job in jobs:
        if job.get("id") == job_id:
            text = job.get("descriptionPlain") or html_to_text(job.get("descriptionHtml", ""))
            return job.get("title", ""), text
    raise JobLinkError("That job isn't on the company's board any more. It may have closed.")


def fetch_job(url):
    """Return (title, description text) for a supported job link."""
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    parts = [p for p in parsed.path.split("/") if p]

    if host.endswith("greenhouse.io") and len(parts) >= 3 and parts[1] == "jobs":
        title, text = from_greenhouse(parts[0], parts[2], eu=".eu." in host)
    elif host.endswith("greenhouse.io") and "for" in parse_qs(parsed.query) and "token" in parse_qs(parsed.query):
        query = parse_qs(parsed.query)
        title, text = from_greenhouse(query["for"][0], query["token"][0])
    elif host in ("jobs.lever.co", "jobs.eu.lever.co") and len(parts) >= 2:
        title, text = from_lever(parts[0], parts[1], eu=host == "jobs.eu.lever.co")
    elif host == "jobs.ashbyhq.com" and len(parts) >= 2:
        title, text = from_ashby(parts[0], parts[1])
    else:
        raise JobLinkError(
            "This link isn't from Greenhouse, Lever or Ashby, so FitProof can't read it. "
            "Copy the job description and paste it instead."
        )
    if not text:
        raise JobLinkError("The job loaded, but it had no description. Paste the text instead.")
    return title, text
