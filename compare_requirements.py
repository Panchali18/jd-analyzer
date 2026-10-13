"""Which requirements change label when the CV is blinded? Every run uses one fixed list."""
from dotenv import load_dotenv

from ai_matcher import analyse, extract_requirements
from blind import blind

load_dotenv()

JD = open("test_data/jd_02.txt").read()
requirements = extract_requirements(JD)
print(f"Fixed list: {len(requirements['requirements'])} requirements")

for cv_id in ["cv_01", "cv_02", "cv_06"]:
    original = open(f"test_data/recruiter/{cv_id}.txt").read()
    before = analyse(JD, original, requirements)
    after = analyse(JD, blind(original)[0], requirements)
    print(f"\n{cv_id}: {before['score']}% -> {after['score']}%")
    for old, new in zip(before["requirements"], after["requirements"]):
        if old["status"] != new["status"]:
            print(f"  {old['skill']}: {old['status']} -> {new['status']}")
            print(f"    original evidence: {old.get('cv_evidence')}")
            print(f"    blind evidence:    {new.get('cv_evidence')}")
    skipped = [r["skill"] for r in before["requirements"] + after["requirements"] if r.get("note") == "Not assessed by the AI"]
    if skipped:
        print(f"  Skipped by the AI (counted as missing): {skipped}")