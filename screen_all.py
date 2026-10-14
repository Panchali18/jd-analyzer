"""Screen every fictional CV against each job once, on the blind CV, and save the results.
The recruiter demo then reads this file, so a visit costs nothing and every candidate
for a job is judged against the same saved requirement list.

Run: python screen_all.py   (about 32 AI calls, roughly 70 cents)"""
import json
from pathlib import Path

from dotenv import load_dotenv

from ai_matcher import analyse, extract_requirements
from blind import blind

load_dotenv()

CV_FOLDER = Path("test_data/recruiter")
JOB_DESCRIPTIONS = {
    "AI Adoption & Delivery Specialist": "test_data/jd_01.txt",
    "Senior Business Analyst, GenAI": "test_data/jd_02.txt",
}
OUTPUT = Path("test_data/recruiter/screening_results.json")

results = {}
for job, jd_path in JOB_DESCRIPTIONS.items():
    jd_text = Path(jd_path).read_text()
    requirements = extract_requirements(jd_text)
    print(f"\n{job}: {len(requirements['requirements'])} requirements")
    results[job] = {"requirements": requirements, "candidates": {}}
    for cv_file in sorted(CV_FOLDER.glob("cv_*.txt")):
        blind_text, _ = blind(cv_file.read_text())
        result = analyse(jd_text, blind_text, requirements)
        results[job]["candidates"][cv_file.stem] = result
        print(f"  {cv_file.stem}: {result['score']}% {result['verdict']}")

OUTPUT.write_text(json.dumps(results, indent=1))
print(f"\nSaved to {OUTPUT}")
