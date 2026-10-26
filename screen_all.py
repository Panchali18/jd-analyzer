"""Screen the recruiter shortlist CVs on their blind text and save the results.
The recruiter demo reads this file, so a visit costs nothing.

- Only the realistic CVs (cv_16 onwards) are on the shortlist. cv_01 to cv_15 are short CVs
  written to test blinding, so they stay out of the demo.
- Each job keeps the requirement list it was first screened against, so every candidate is
  measured the same way. Only CVs that haven't been screened yet cost an AI call.

Run: python screen_all.py"""
import json
from pathlib import Path

from dotenv import load_dotenv

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
        requirements = extract_requirements(jd_text)
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
            result = analyse(jd_text, blind_text, requirements)
            calls += 1
            note = "(new)"
        results[job]["candidates"][cv_file.stem] = result
        print(f"  {cv_file.stem}: {result['score']}% {result['verdict']} {note}")

OUTPUT.write_text(json.dumps(results, indent=1))
print(f"\nSaved to {OUTPUT}. AI calls made: {calls}")
