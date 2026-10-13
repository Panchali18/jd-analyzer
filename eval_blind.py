"""Measure how many labelled identifiers blind.py catches, and what it wrongly removes.

An identifier only counts as caught if every letter and digit of it, everywhere it
appears, was removed. Removing just "Mr" from "Mr Khalid Mansour" is a miss."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from blind import find_identifiers, merge

folder = Path(sys.argv[1] if len(sys.argv) > 1 else "test_data/recruiter")
key = json.loads((folder / "answer_key.json").read_text())

caught = defaultdict(int)
total = defaultdict(int)
by_region = defaultdict(lambda: [0, 0])
misses, over = [], []
kept_ok = kept_total = 0


def occurrences(snippet, text, whole_word):
    """Every (start, end) where the snippet appears in the original CV."""
    pattern = rf"\b{re.escape(snippet)}\b" if whole_word else re.escape(snippet)
    return [(m.start(), m.end()) for m in re.finditer(pattern, text)]


def fully_removed(start, end, text, removed_spans):
    """True if every letter and digit between start and end was inside a removed span."""
    for i in range(start, end):
        if text[i].isalnum() and not any(s <= i < e for s, e in removed_spans):
            return False
    return True


for cv_id, answer in key.items():
    original = (folder / f"{cv_id}.txt").read_text()
    removed_spans = [(s, e) for s, e, _ in merge(find_identifiers(original))]
    for item in answer["pii"]:
        total[item["type"]] += 1
        places = occurrences(item["text"], original, item.get("whole_word", False))
        found = bool(places) and all(fully_removed(s, e, original, removed_spans) for s, e in places)
        caught[item["type"]] += found
        if item["type"] == "NAME":
            by_region[item["region"]][0] += found
            by_region[item["region"]][1] += 1
        if not found:
            misses.append(f"{cv_id}: {item['type']} '{item['text']}'")
    for snippet in answer["keep"]:
        kept_total += 1
        places = occurrences(snippet, original, False)
        # kept if at least one place it appears was left untouched (a city may also be part of an address)
        untouched = [(s, e) for s, e in places if not any(s < e2 and s2 < e for s2, e2 in removed_spans)]
        if untouched:
            kept_ok += 1
        else:
            over.append(f"{cv_id}: '{snippet}'")

all_caught, all_total = sum(caught.values()), sum(total.values())
print(f"Identifiers caught: {all_caught}/{all_total} ({all_caught / all_total:.0%})")
print(f"Job details kept:   {kept_ok}/{kept_total} ({kept_ok / kept_total:.0%})\n")
print("By type:")
for kind in sorted(total):
    print(f"  {kind:18} {caught[kind]}/{total[kind]}")
print("\nNames by region:")
for region, (hit, n) in sorted(by_region.items()):
    print(f"  {region:16} {hit}/{n}")
print("\nMissed:" if misses else "\nMissed: none")
for m in misses:
    print("  " + m)
print("\nWrongly removed:" if over else "\nWrongly removed: none")
for o in over:
    print("  " + o)