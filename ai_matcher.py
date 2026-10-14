import json
import re

import boto3

MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = "eu-north-1"

# Points per requirement type, and how much of those points each status earns
WEIGHTS = {"required": 3, "qualification": 3, "nice to have": 1, "eligibility": 0}  # eligibility is checked by a person, never scored
CREDIT = {"evidenced": 1.0, "partly evidenced": 0.5, "missing": 0.0}

INSTRUCTIONS = """You compare a job description with a candidate's CV.

Step 1. Use the requirements given in <requirements> exactly as listed: same wording, same type, same order. Don't add, remove, merge or split any.

Step 2. For each requirement, check the CV and give it a status:
- "evidenced": the CV clearly shows it
- "partly evidenced": the CV shows something close, but not the same
- "missing": the CV doesn't show it
For "evidenced" and "partly evidenced", put the supporting CV text into cv_evidence as a list of quotes. Copy each quote exactly from the CV, character for character, under 30 words, with no words changed and nothing added. Use a separate quote for each separate part of the CV, and never join parts with "|" or "...". Put any explanation in note, never in cv_evidence. If you can't quote the CV, the status is "missing". Never assume experience the CV doesn't state.

Step 3. List deal-breakers. Only include a missing requirement when the job description explicitly says it is mandatory, using words such as "must", "must have", "required", "essential", "mandatory", "minimum" or "at least". Being listed under a heading like "Your tasks" or "Your profile" does not make a requirement mandatory. Treat "or similar" and "or equivalent" as flexible: if the CV shows something comparable, it is not a deal-breaker. For each deal-breaker, copy the job description's exact words that make it mandatory into jd_evidence, and copy any related CV text exactly into related_cv_evidence, or leave it empty.

Step 4. Help the candidate talk honestly about their most important gaps. Pick up to 5 requirements of type "required" or "qualification" whose status is "missing" or "partly evidenced", most important first. For each one:
- closest_cv_evidence: the CV text that comes closest to this requirement, copied exactly from the CV under the same quote rules as Step 2, or "" if nothing comes close.
- how_to_say_it: one sentence of at most 30 words, in the first person, that the candidate could say in an interview or cover letter. Start with something specific they did, taken from the CV, then say in plain words how it connects to this requirement. Don't open with what's missing ("While I haven't", "Although I lack"), don't promise to learn on the job, and don't use stock phrases like "core strength", "passionate about" or "complex processes". Never claim the requirement is met, and never add tools, numbers, employers, clients or responsibilities that aren't in the CV. If nothing in the CV comes close, leave this requirement out.
  Bad: "While I haven't worked in retail, my core strength is translating data into insights, though I'd need to learn retail specifics on the job."
  Good: "I built demand forecasts for an FMCG distributor, so I know the stock and promotion questions retail teams ask."
- how_to_close_it: one concrete step that would close the gap, such as a named certification, a short course topic or a small project. No prices or dates.

Step 5. List up to 5 strengths from the CV that are relevant to this role but not asked for in the job description.

Return only JSON in exactly this shape, with no other text:
{
  "role_title": "",
  "requirements": [
   {"skill": "", "type": "required", "status": "evidenced", "cv_evidence": [""], "note": ""}
  ],
  "deal_breakers": [
    {"requirement": "", "jd_evidence": "", "related_cv_evidence": ""}
  ],
  "gap_talk": [
    {"requirement": "", "closest_cv_evidence": "", "how_to_say_it": "", "how_to_close_it": ""}
  ],
  "extra_strengths": [""]
}"""

EXTRACT_INSTRUCTIONS = """You read a job description and list its requirements.

Skip company background, benefits and equal-opportunity text. Merge duplicates. Use one item for each bullet point or sentence that states a requirement, and don't split a bullet into several items. Give each requirement a type:
- "required": skills and experience the role needs
- "nice to have": described as a plus, preferred, beneficial, desirable or valuable
- "qualification": degrees, certifications, languages and minimum years of experience
- "eligibility": right to work, visa or sponsorship, citizenship or residency conditions

Return only JSON in exactly this shape, with no other text:
{"role_title": "", "requirements": [{"skill": "", "type": "required"}]}"""


def call_claude(system, user_text):
    """Send one message to Claude on Bedrock and return its JSON answer as a Python dictionary."""
    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
        inferenceConfig={"maxTokens": 10000, "temperature": 0},
    )
    if response.get("stopReason") == "max_tokens":
        raise ValueError("The AI's answer was too long and got cut off. Try a shorter job description.")
    reply = response["output"]["message"]["content"][0]["text"]
    # Keep only the JSON, in case Claude adds anything around it
    start = reply.find("{")
    end = reply.rfind("}") + 1
    return json.loads(reply[start:end])


def extract_requirements(jd_text):
    """Call 1: read the job description once. Every CV is then judged against this same list."""
    requirements = call_claude(EXTRACT_INSTRUCTIONS, f"<job_description>\n{jd_text}\n</job_description>")
    for item in requirements["requirements"]:
        if not item.get("skill"):
            # The AI sometimes names the field after the type, e.g. {"qualification": "..."}
            item["skill"] = next((v for k, v in item.items() if k != "type" and isinstance(v, str)), "")
    return requirements


def ask_claude(jd_text, cv_text, requirements):
    """Call 2: judge the CV against the fixed list of requirements."""
    listed = json.dumps(requirements["requirements"], indent=1)
    return call_claude(
        INSTRUCTIONS,
        f"<job_description>\n{jd_text}\n</job_description>\n\n"
        f"<requirements>\n{listed}\n</requirements>\n\n"
        f"<cv>\n{cv_text}\n</cv>",
    )


def calculate_score(result):
    """Weighted score from the AI's labels: 3 for required and qualification, 1 for nice to have."""
    available = 0
    earned = 0
    for req in result["requirements"]:
        points = WEIGHTS.get(req["type"], 0)
        available += points
        earned += points * CREDIT.get(req["status"], 0)
    if available == 0:
        return 0
    return round(earned / available * 100)


def get_verdict(result, score):
    if result["deal_breakers"]:
        return "Not a fit: missing must-have"
    if score >= 75:
        return "Strong fit"
    if score >= 50:
        return "Possible fit"
    return "Weak fit"


def simplify(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def check_evidence(result, cv_text):
    """Mark whether every quoted CV line really appears in the CV."""
    cv = simplify(cv_text)
    for req in result["requirements"]:
        quotes = req.get("cv_evidence") or []
        if isinstance(quotes, str):
            quotes = [quotes]
        req["evidence_verified"] = bool(quotes) and all(simplify(q) in cv for q in quotes)
    return result

MUST_WORDS = ["must", "required", "essential", "mandatory", "minimum", "at least"]


# Right to work can't be judged from a CV, so these are listed for a person to check
ELIGIBILITY_WORDS = [
    "eligible to work", "eligibility to work", "right to work", "work permit", "work authori",
    "authorised to work", "authorized to work", "visa", "sponsorship", "citizenship",
    "permanent resident", "residency",
]


def is_eligibility(text):
    text = simplify(text)
    return any(word in text for word in ELIGIBILITY_WORDS)


def separate_eligibility(result):
    """Move right-to-work conditions out of the score and the deal-breakers, into a list to check."""
    checks = []
    for req in result["requirements"]:
        if req["type"] == "eligibility" or is_eligibility(req["skill"]):
            req["type"] = "eligibility"
            checks.append({"requirement": req["skill"], "jd_evidence": ""})
    kept = []
    for item in result["deal_breakers"]:
        if is_eligibility(item.get("requirement", "") + " " + item.get("jd_evidence", "")):
            checks.append({"requirement": item.get("requirement", ""), "jd_evidence": item.get("jd_evidence", "")})
        else:
            kept.append(item)
    result["deal_breakers"] = kept
    # One entry per condition, keeping the job description's wording where we have it
    unique = {}
    for check in checks:
        key = simplify(check["requirement"])
        if key not in unique or check["jd_evidence"]:
            unique[key] = check
    result["eligibility_checks"] = list(unique.values())
    return result


def check_deal_breakers(result, jd_text):
    """Keep only deal-breakers whose JD wording is real and says the requirement is mandatory."""
    jd = simplify(jd_text)
    confirmed = []
    for item in result["deal_breakers"]:
        wording = simplify(item.get("jd_evidence", ""))
        in_jd = bool(wording) and wording in jd
        mandatory = any(word in wording for word in MUST_WORDS)
        if in_jd and mandatory:
            confirmed.append(item)
    result["deal_breakers"] = confirmed
    return result

def find_numbers(text):
    """All numbers in a line, like 70, 500, 11 or 2.5."""
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def check_gap_talk(result, cv_text):
    """Keep gap advice honest: the quoted CV line must be real, and the wording may add no number the CV doesn't have."""
    cv = simplify(cv_text)
    cv_numbers = find_numbers(cv_text)
    kept = []
    for item in result.get("gap_talk") or []:
        quote = item.get("closest_cv_evidence", "")
        if quote and simplify(quote) not in cv:
            item["closest_cv_evidence"] = ""  # not a real CV line, so don't show it as one
        if find_numbers(item.get("how_to_say_it", "")) - cv_numbers:
            continue  # a number the CV doesn't contain is an overclaim
        kept.append(item)
    result["gap_talk"] = kept
    return result


def apply_fixed_list(result, requirements):
    """Hold the AI to the fixed list: same items, types from the list, anything it skipped counts as missing."""
    returned = result.get("requirements") or []
    judged = {simplify(r.get("skill") or ""): r for r in returned}
    fixed = []
    for position, item in enumerate(requirements["requirements"]):
        req = judged.get(simplify(item["skill"]))
        if req is None and len(returned) == len(requirements["requirements"]):
            req = returned[position]  # same count and order, but the name was missing or reworded
        if req is None:
            req = {"skill": item["skill"], "status": "missing", "cv_evidence": [], "note": "Not assessed by the AI"}
        req["skill"] = item["skill"]
        req["type"] = item["type"]
        fixed.append(req)
    result["requirements"] = fixed
    result["role_title"] = requirements.get("role_title") or result.get("role_title")
    return result


def analyse(jd_text, cv_text, requirements=None):
    """Give requirements to reuse a fixed list; leave it out and the job description is read first."""
    if requirements is None:
        requirements = extract_requirements(jd_text)
    result = ask_claude(jd_text, cv_text, requirements)
    result = apply_fixed_list(result, requirements)
    result = check_evidence(result, cv_text)
    result = check_deal_breakers(result, jd_text)
    result = separate_eligibility(result)
    result = check_gap_talk(result, cv_text)
    score = calculate_score(result)
    result["score"] = score
    result["verdict"] = get_verdict(result, score)
    return result