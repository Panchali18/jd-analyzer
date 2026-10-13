"""Measure how many labelled identifiers blind.py catches, and what it wrongly removes."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from blind import blind

folder = Path(sys.argv[1] if len(sys.argv) > 1 else "test_data/recruiter")
key = json.loads((folder / "answer_key.json").read_text())

caught = defaultdict(int)
total = defaultdict(int)
by_region = defaultdict(lambda: [0, 0])
misses, over = [], []
kept_ok = kept_total = 0


def still_there(snippet, text, whole_word):
    if whole_word:
        return re.search(rf"\b{re.escape(snippet)}\b", text) is not None
    return snippet in text


for cv_id, answer in key.items():
    original = (folder / f"{cv_id}.txt").read_text()
    blind_text, _ = blind(original)
    for item in answer["pii"]:
        total[item["type"]] += 1
        found = not still_there(item["text"], blind_text, item.get("whole_word", False))
        caught[item["type"]] += found
        if item["type"] == "NAME":
            by_region[item["region"]][0] += found
            by_region[item["region"]][1] += 1
        if not found:
            misses.append(f"{cv_id}: {item['type']} '{item['text']}'")
    for snippet in answer["keep"]:
        kept_total += 1
        if snippet in blind_text:
            kept_ok += 1
        else:
            over.append(f"{cv_id}: '{snippet}'")

all_caught, all_total = sum(caught.values()), sum(total.values())
print(f"Identifiers caught: {all_caught}/{all_total} ({all_caught / all_total:.0%})")
print(f"Job details kept:   {kept_ok}/{kept_total} ({kept_ok / kept_total:.0%})\n")
print("By type:")
for kind in sorted(total):
    print(f"  {kind:15} {caught[kind]}/{total[kind]}")
print("\nNames by region:")
for region, (hit, n) in sorted(by_region.items()):
    print(f"  {region:16} {hit}/{n}")
print("\nMissed:" if misses else "\nMissed: none")
for m in misses:
    print("  " + m)
print("\nWrongly removed:" if over else "\nWrongly removed: none")
for o in over:
    print("  " + o)