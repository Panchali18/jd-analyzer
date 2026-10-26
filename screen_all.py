"""Screen the recruiter shortlist CVs on their blind text and save the results.
The recruiter demo reads this file, so a visit costs nothing.

- Only the realistic CVs (cv_16 onwards) are on the shortlist. cv_01 to cv_15 are short CVs
  written to test blinding, so they stay out of the demo.
- Each job keeps the requirement list it was first screened against, so every candidate is
  measured the same way. Only CVs that haven't been screened yet cost an AI call.

Run: python screen_all.py
     python screen_all.py --global   uses Bedrock's global route instead of the EU one. Only for these
                                     fictional CVs (no real person's data), e.g. when the EU route is down.
                                     The live app always uses the EU route."""
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

import ai_matcher
from ai_matcher import analyse, extract_requirements
from blind import blind

load_dotenv()

CV_FOLDER = Path("test_data/recruiter")
FIRST_SHORTLIST_CV = 16
JOB_DESCRIPTIONS = {
    "AI Adoption & Delivery Specialist": "test_data/jd_01.txt",
    "Senior Business Analyst, GenAI": "test_data/jd_02.txt",
}
OUTPUT = CV_FOLDER / "screening_results.json"

WAITS = [20, 60, 120]  # seconds to wait before trying again when Bedrock is busy


def with_retries(step, *args):
    """Bedrock is sometimes briefly unavailable. Wait and try again rather than stopping."""
    for wait in WAITS + [None]:
        try:
            return step(*args)
        except Exception as error:
            if wait is None or "ServiceUnavailable" not in type(error).__name__ + str(error):
                raise
            print(f"    Bedrock is busy, trying again in {wait} seconds...")
            time.sleep(wait)


if "--global" in sys.argv:
    ai_matcher.MODEL_ID = ai_matcher.MODEL_ID.replace("eu.", "global.", 1)
print(f"Model route: {ai_matcher.MODEL_ID}")

saved = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {}
shortlist = [f for f in sorted(CV_FOLDER.glob("cv_*.txt")) if int(f.stem.split("_")[1]) >= FIRST_SHORTLIST_CV]

results = {}
calls = 0
for job, jd_path in JOB_DESCRIPTIONS.items():
    jd_text = Path(jd_path).read_text()
    if job in saved:
        requirements = saved[job]["requirements"]  # same yardstick as before
        print(f"\n{job}: reusing the saved list of {len(requirements['requirements'])} requirements")
    else:
        requirements = with_retries(extract_requirements, jd_text)
        calls += 1
        print(f"\n{job}: {len(requirements['requirements'])} requirements")
    previous = saved.get(job, {}).get("candidates", {})
    results[job] = {"requirements": requirements, "candidates": {}}
    for cv_file in shortlist:
        if cv_file.stem in previous:
            result = previous[cv_file.stem]
            note = "(saved)"
        else:
            blind_text, _ = blind(cv_file.read_text())
            result = with_retries(analyse, jd_text, blind_text, requirements)
            calls += 1
            note = "(new)"
        results[job]["candidates"][cv_file.stem] = result
        # Save after every candidate, keeping anything not reached yet, so a failure never loses finished work
        progress = {**saved, **results}
        OUTPUT.write_text(json.dumps(progress, indent=1))
        print(f"  {cv_file.stem}: {result['score']}% {result['verdict']} {note}")

OUTPUT.write_text(json.dumps(results, indent=1))
print(f"\nSaved to {OUTPUT}. AI calls made: {calls}")
