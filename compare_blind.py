"""Does blinding change the match? Run each CV with and without blinding, twice."""
from dotenv import load_dotenv

from ai_matcher import analyse
from blind import blind

load_dotenv()

JD = open("test_data/jd_02.txt").read()
CVS = ["cv_01", "cv_02", "cv_06"]
RUNS = 2

for cv_id in CVS:
    original = open(f"test_data/recruiter/{cv_id}.txt").read()
    blind_text, _ = blind(original)
    for label, text in [("original", original), ("blind", blind_text)]:
        results = [analyse(JD, text) for _ in range(RUNS)]
        scores = [r["score"] for r in results]
        verdicts = [r["verdict"] for r in results]
        print(f"{cv_id}  {label:8}  scores: {scores}  verdicts: {verdicts}")