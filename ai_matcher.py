import json
import re

import boto3

MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = "eu-north-1"

# Points per requirement type, and how much of those points each status earns
WEIGHTS = {"required": 3, "qualification": 3, "nice to have": 1}
CREDIT = {"evidenced": 1.0, "partly evidenced": 0.5, "missing": 0.0}

INSTRUCTIONS = """You compare a job description with a candidate's CV.

Step 1. List the requirements in the job description. Skip company background, benefits and equal-opportunity text. Merge duplicates. Give each requirement a type:
- "required": skills and experience the role needs
- "nice to have": described as a plus, preferred, beneficial, desirable or valuable
- "qualification": degrees, certifications, languages and minimum years of experience

Step 2. For each requirement, check the CV and give it a status:
- "evidenced": the CV clearly shows it
- "partly evidenced": the CV shows something close, but not the same
- "missing": the CV doesn't show it
For "evidenced" and "partly evidenced", copy the supporting CV text word for word into cv_evidence (under 30 words). If you can't quote the CV, the status is "missing". Never assume experience the CV doesn't state.

Step 3. List deal-breakers: requirements of type "required" or "qualification" that are "missing" and that the job description states as essential (for example "must have", "required", "essential", a minimum number of years, a named certification or a language). For each, copy any related CV text word for word into related_cv_evidence, or leave it empty.

Step 4. Suggest up to 5 rewrites of existing CV lines that would better cover "partly evidenced" or "missing" requirements. Only rephrase what the CV already says. Never add tools, numbers, employers or responsibilities that aren't in the CV.

Step 5. List up to 5 strengths from the CV that are relevant to this role but not asked for in the job description.

Return only JSON in exactly this shape, with no other text:
{
  "role_title": "",
  "requirements": [
    {"skill": "", "type": "required", "status": "evidenced", "cv_evidence": "", "note": ""}
  ],
  "deal_breakers": [
    {"requirement": "", "related_cv_evidence": ""}
  ],
  "rewrite_suggestions": [
    {"current_cv_line": "", "suggested_line": "", "covers": ""}
  ],
  "extra_strengths": [""]
}"""


def ask_claude(jd_text, cv_text):
    """Send the JD and CV to Claude on Bedrock and return its answer as a Python dictionary."""
    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": INSTRUCTIONS}],
        messages=[{
            "role": "user",
            "content": [{"text": f"<job_description>\n{jd_text}\n</job_description>\n\n<cv>\n{cv_text}\n</cv>"}],
        }],
        inferenceConfig={"maxTokens": 4000, "temperature": 0},
    )
    reply = response["output"]["message"]["content"][0]["text"]
    # Keep only the JSON, in case Claude adds anything around it
    start = reply.find("{")
    end = reply.rfind("}") + 1
    return json.loads(reply[start:end])


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
    """Mark whether each quoted CV line really appears in the CV."""
    cv = simplify(cv_text)
    for req in result["requirements"]:
        quote = simplify(req.get("cv_evidence", ""))
        req["evidence_verified"] = bool(quote) and quote in cv
    return result


def analyse(jd_text, cv_text):
    result = ask_claude(jd_text, cv_text)
    result = check_evidence(result, cv_text)
    score = calculate_score(result)
    result["score"] = score
    result["verdict"] = get_verdict(result, score)
    return result