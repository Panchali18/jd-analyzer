# Increment 1 results: blind screening

## Run 1 (13 October 2026) — first and official result

`blind.py` as built from the development set, run once on the held-out set.

| Test set | Identifiers caught | Job details kept |
| --- | --- | --- |
| Development (15 synthetic CVs written alongside the rules) | 131/131 (100%) | 89/89 (100%) |
| **Held-out (4 fictional CVs written by Panchali without seeing the rules)** | **21/34 (62%)** | **35/37 (95%)** |

Held-out results by type:

| Type | Caught |
| --- | --- |
| Address | 0/3 |
| Date of birth | 2/2 |
| Email | 4/4 |
| Immigration status | 0/3 |
| Marital status | 2/2 |
| Name (candidate) | 3/4 |
| Nationality | 2/2 |
| Origin ("Native Place") | 0/1 |
| Phone | 5/5 |
| Referee details | 2/7 |
| URL | 1/1 |

### Why each miss happened
| Miss | Cause |
| --- | --- |
| All 3 street addresses | The rule only matched a line starting "Address:"; none of the held-out CVs used that label |
| All 3 immigration statuses ("US permanent resident", "Australian citizen", "UAE residence visa") | No rule existed for immigration status |
| "Native Place: Mysuru, Karnataka" | No rule existed for birthplace or hometown |
| 5 of 7 referee details | Names were only accepted from the top 3 lines (the fix for employers like "Severn Trent" being read as people), so referees at the bottom were ignored |
| Omar Al-Hassan (second mention) | Name parts of 2 letters or fewer were skipped, so the "Al" in "Al-Hassan" was left behind |

### Damage the score did not show
- Presidio read "Ananya Rao" plus the next line, "Business Analyst", as one name. The repeated-name rule then removed "Business" and "Analyst" everywhere in that CV, including job titles and "Crestline Business Solutions". Only the company name was on the keep list, so the 95% understates the damage.
- "Arabic" and "French" (languages) were removed as nationalities; "B.Com" was removed as a web address.

### Lesson
The failures came from assumptions in our own rules about CV layout (labels, line positions, name lengths), not from the name detection itself. A 100% score on a test set written alongside the rules said nothing about real CVs.

## Run 2 (13 October 2026) — after fixing what run 1 exposed

| Test set | Identifiers caught | Job details kept |
| --- | --- | --- |
| Development (15 CVs) | 131/131 (100%) | 89/89 (100%) |
| Held-out (4 CVs) | 34/34 (100%) | 37/37 (100%) |

**This held-out score is no longer independent:** the rules were fixed using these 4 CVs. Run 1 (62%) remains the official result. A fresh held-out set is needed for a new independent score.

Fixes made:
| Fix | Addresses which miss |
| --- | --- |
| Street-address pattern (house number + street word + rest of that part of the line, with optional Flat/Apt/Unit) | Addresses without an "Address:" label |
| Immigration-status rules ("permanent resident", "[Country] citizen", "residence/work visa or permit", "Stamp 4"); right-to-work statements kept | Immigration status |
| Origin rule ("Native Place", "Place of birth", "Hometown") | Birthplace |
| Names under a References/Referees heading become `[REFEREE]` | Referee names |
| A detected name is cut at the line break | "Ananya Rao" swallowing "Business Analyst" |
| Repeated-name search also uses the full name and whole hyphenated words | "Al-Hassan" |
| Nationality-like words on a "Languages" line are ignored | "Arabic", "French" |
| Degree-shaped text ("B.Com", "M.Sc") is not a web address | "B.Com" |

Two of these fixes first caused regressions on the development set (a personal website stopped being caught; "de" in "Universidad de los Andes" was removed). Both were caught by rerunning the development set and corrected before this run.


## Blind vs original comparison (13 October 2026)

**Question:** does blinding change the match? It shouldn't, because blinding removes identity, not evidence.

**Run 1** (`compare_blind.py`, Senior BA GenAI job, 3 CVs, each version twice): blind scores were lower on every CV (cv_01 41→36, cv_02 21→15, cv_06 26–30→18). Repeat runs of the same input matched within 4 points, so this wasn't run-to-run noise.

**Diagnosis** (`compare_requirements.py`): the AI built its requirement list from the JD on every call, and the list changed whenever the CV text changed (12 vs 14, 13 vs 16, 13 vs 12 items). The score moved because the yardstick moved.

**Fix:** two calls. `extract_requirements` reads the JD once; `analyse` judges each CV against that fixed list, and `apply_fixed_list` holds the AI to it in code.

**Run 2, fixed list (16 requirements):**

| CV | Original | Blind | Change |
| --- | --- | --- | --- |
| cv_01 | 25% | 24% | −1 |
| cv_02 | 11% | 11% | 0 |
| cv_06 | 10% | 13% | +3 |

The remaining changes are borderline calls (partly evidenced vs missing) on the same evidence lines, in both directions. No sign that blinding removes evidence or shifts scores one way.

**Limits:** 3 CVs, one JD, one run each: a sanity check, not a bias test (increment 2). The list is fixed per app start, not yet saved and approved by a person; the fixed list still contains a near-duplicate (two vendor assessment items).
