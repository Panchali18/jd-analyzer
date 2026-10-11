import json
import sys

from dotenv import load_dotenv
from pypdf import PdfReader

from ai_matcher import analyse

load_dotenv()

jd_file = sys.argv[1]
jd_text = open(jd_file).read()
cv_text = "\n".join(page.extract_text() for page in PdfReader("private/cv.pdf").pages)

result = analyse(jd_text, cv_text)

print(f"\n{result['role_title']}")
print(f"Score: {result['score']}%  |  Verdict: {result['verdict']}\n")
for req in result["requirements"]:
    tick = "" if req["evidence_verified"] or req["status"] == "missing" else "  (quote not found in CV)"
    print(f"[{req['type']}] {req['skill']}: {req['status']}{tick}")
print("\nDeal-breakers:", [d["requirement"] for d in result["deal_breakers"]] or "none")

with open(jd_file.replace(".txt", "_ai_result.json"), "w") as f:
    json.dump(result, f, indent=2)