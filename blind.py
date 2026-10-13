"""Blind screening: replace a CV's direct identifiers with labelled placeholders
before the AI sees it. Presidio finds names, emails, phones, URLs and nationalities;
our own rules handle what it misses or gets wrong for CVs."""
import re

from presidio_analyzer import AnalyzerEngine

# Presidio types we trust, and the placeholder each one becomes
PRESIDIO_TYPES = {
    "PERSON": "NAME",
    "EMAIL_ADDRESS": "EMAIL",
    "PHONE_NUMBER": "PHONE",
    "URL": "URL",
    "NRP": "NATIONALITY",
}
# Presidio's DATE_TIME and LOCATION are deliberately not used:
# they would hide years of experience, job dates and job cities.

MIN_SCORE = 0.3  # phone numbers often score only 0.4
HEADER_LINES = 3  # where the candidate's own name appears

# Our own rules. Each one is (placeholder, regular expression)
CUSTOM_RULES = [
    ("ADDRESS", r"(?im)^address:\s*(.+)$"),
    ("DATE_OF_BIRTH", r"(?i)\b(?:date of birth|dob|born)\b[:\s]*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2} [A-Z][a-z]+ [0-9]{4}|[0-9]{4})"),
    ("AGE", r"(?i)\b(age:?\s*[0-9]{2}|[0-9]{2} years old)\b"),
    ("MARITAL_STATUS", r"(?i)\b(married|divorced|widowed|separated|in a civil partnership)\b"),
    ("MARITAL_STATUS", r"(?i)\bmarital status:\s*(\w+)"),
    ("GENDER_MARKER", r"\b(Mr|Mrs|Ms|Miss|Mx)\b\.?"),
    ("GENDER_MARKER", r"(?i)\b(he|she|him|her|his|hers|himself|herself)\b"),
    ("GENDER_MARKER", r"(?i)\bgender:\s*(\w+)"),
    ("NATIONALITY", r"(?im)\bnationality:\s*([^|\n]+?)\s*(?:\||$)"),
    # Street addresses without an "Address:" label: a number, up to four words, a street word, then the rest of that part of the line
    ("ADDRESS", r"(?:\b(?:Flat|Apt|Apartment|Unit|Suite|House|Villa|Room)\s+\w+,\s*)?\b\d+[A-Za-z]?\s+(?:[A-Z][\w'.-]*\s+){1,4}(?:Street|St|Road|Rd|Lane|Ln|Avenue|Ave|Drive|Dr|Close|Court|Way|Boulevard|Blvd|Crescent|Terrace|Place|Square|Gardens|Park)\b[^|\n]*"),
    # Immigration status. Right-to-work statements ("authorized to work") are kept
    ("IMMIGRATION_STATUS", r"\b(?:[A-Z]{2,3}|[A-Z][a-z]+) permanent resident\b"),
    ("IMMIGRATION_STATUS", r"(?i)\bpermanent resident\b|\bgreen card holder\b"),
    ("IMMIGRATION_STATUS", r"\b[A-Z][a-z]+ citizen(?:ship)?\b"),
    ("IMMIGRATION_STATUS", r"\b(?:[A-Z]{2,3} )?(?:residence|work|student|spouse|dependant|dependent) (?:visa|permit)\b"),
    ("IMMIGRATION_STATUS", r"(?i)\bstamp [0-9][a-z]?\b"),
    # Where someone is from, as opposed to where they live or work
        ("ORIGIN", r"(?im)^\s*(?:native place|place of birth|birthplace|home ?town)\s*:\s*(.+)$"),
]
REFERENCE_HEADING = r"(?im)^\s*(?:references|referees)\b"

_analyzer = None


def get_analyzer():
    """Load Presidio and the language model once, then reuse it."""
    global _analyzer
    if _analyzer is None:
        _analyzer = AnalyzerEngine()
    return _analyzer



def find_identifiers(text):
    """Return a list of (start, end, placeholder) for every identifier found."""
    found = []

    # The candidate's name is almost always in the first few lines
    header_end = sum(len(line) + 1 for line in text.splitlines()[:HEADER_LINES])

        # Referees are listed under a References or Referees heading
    heading = re.search(REFERENCE_HEADING, text)
    references_start = heading.start() if heading else len(text)

    # 1. Presidio, limited to the types we trust
    for item in get_analyzer().analyze(text=text, language="en", entities=list(PRESIDIO_TYPES)):
        if item.score < MIN_SCORE:
            continue
        start, end = item.start, item.end
        line_start = text.rfind("\n", 0, start) + 1
        line_end = text.find("\n", start)
        line = text[line_start : line_end if line_end != -1 else len(text)]
        if item.entity_type == "PERSON":
            end = start + len(text[start:end].split("\n")[0])  # a name never runs onto the next line
            if start >= references_start:
                found.append((start, end, "REFEREE"))
                continue
            if start >= header_end:
                continue  # names further down are usually employers or products ("Severn Trent")
        if item.entity_type == "NRP" and "language" in line.lower():
            continue  # "Arabic (native)" is a language skill, not a nationality
        if item.entity_type == "URL" and re.fullmatch(r"[A-Z][a-z]?\.[A-Z][a-z]+", text[start:end]):
            continue  # "B.Com" or "M.Sc" is a degree, not a web address
        found.append((start, end, PRESIDIO_TYPES[item.entity_type]))

    # 2. Our own rules. If a rule has a bracketed group, only that part is replaced
    for placeholder, pattern in CUSTOM_RULES:
        for match in re.finditer(pattern, text):
            group = 1 if match.re.groups else 0
            found.append((match.start(group), match.end(group), placeholder))

    # 3. The candidate's first or last name repeated later in the CV ("Fatima led the project")
    names = [text[s:e] for s, e, p in found if p == "NAME"]
    for name in names:
        words = name.split()  # "Al-Hassan" stays one word
        parts = [name] + words + [p for word in words for p in word.split("-")]
        for part in parts:
            if len(part) > 2:
                for match in re.finditer(rf"\b{re.escape(part)}\b", text):
                    found.append((match.start(), match.end(), "NAME"))
    return found


def merge(found):
    """Where findings overlap, keep the longest one."""
    found = sorted(found, key=lambda f: (f[0], -(f[1] - f[0])))
    merged = []
    for start, end, placeholder in found:
        if merged and start < merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end, merged[-1][2])
            continue
        merged.append((start, end, placeholder))
    return merged


def blind(text):
    """Return the blind CV and a list of what was removed."""
    removed = merge(find_identifiers(text))
    blind_text = text
    for start, end, placeholder in reversed(removed):
        blind_text = blind_text[:start] + f"[{placeholder}]" + blind_text[end:]
    items = [{"type": p, "text": text[s:e]} for s, e, p in removed]
    return blind_text, items