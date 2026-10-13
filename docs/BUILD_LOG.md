# JD Analyzer Build Log

Every change to the JD Analyzer, with the problem, the fix, the result, and what I learned. It combines a changelog (what changed) and a decision log (why). Newest first in each table.

## Recruiter mode (parallel track, started 13 October 2026)

A recruiter-side mode that shows compliance-by-design for EU AI Act high-risk screening (Annex III 4(a), obligations from 2 December 2027). Synthetic CVs only. Plan: PRD section 9R. Increment scopes: `docs/recruiter_mode/`.

### Time and cost tracker

| Increment | Started | Finished | Build cost | Run cost per use | Eval |
| --- | --- | --- | --- | --- | --- |
| 1. Blind screening | 13 Oct 2026 | 13 Oct 2026 | £0 so far (all open-source tools) | | Held-out run 1 (official): 62% caught, 95% kept. Run 2 after fixes: 100%, 100% |

| # | Change | Why | Result | What I learned |
| --- | --- | --- | --- | --- |
| R7 | Recruiter screen tidy-up (written by Claude at my request, tested before pushing): starts empty with "Choose a candidate", banner shortened to "Demo: all CVs and candidates are fictional", screening steps shown as they happen, result above the blind CV, "Compare with the original" behind a toggle, no CV rewrites tab and "the CV" instead of "your CV" for recruiters | My review of the live demo: the rewrites tab is a candidate feature, the result sat below two long CV columns, a CV and old result appeared before I chose anything, and the banner was too long | Increment 1 done | Shared screens need an audience setting: the same result reads differently to a candidate and a recruiter. Decided not to add family status and religion rules: rare on the CVs this demo targets; noted as a known gap |
| R6 | Blind vs original comparison (`compare_blind.py`, `compare_requirements.py`), then a design fix: the AI now reads the JD once into a fixed requirement list (`extract_requirements`) and judges every CV against that list; code restores the list if the AI drops, renames or adds items (`apply_fixed_list`). Recruiter mode caches one list per job. Commit 5d37441 | First comparison showed blind scores 5 to 12 points lower on all 3 CVs, while repeat runs of the same CV were identical | Cause wasn't blinding: the AI split the JD into a different list (12 vs 14, 13 vs 16 items) whenever the CV text changed. With a fixed list: cv_01 25→24, cv_02 11→11, cv_06 10→13; remaining changes are borderline partly/missing calls on the same evidence | Check the yardstick before blaming the change. A score that moves for reasons unrelated to the candidate is a fairness and consistency problem (EU AI Act Art. 15). The AI also ignored the answer format (`"qualification": ...` instead of `"skill": ...`), so the code now accepts either. 3 CVs and one JD is a sanity check, not a bias test. Next: a saved, human-approved list per job (duplicates like the two vendor items removed) |
| R5 | Recruiter mode in the app: a Mode switch in the sidebar, a picker for the synthetic CVs and the two test JDs (no uploads), the original and blind CV side by side, and the match run on the blind CV only. Results screen moved into `results_view.py` so both modes share it. Commit 1984c21 | User stories US1 to US3: recruiter mode clearly labelled, the blind view visible, and the AI never sees identifiers | Live on https://fitproof-panchali.streamlit.app/. Synthetic CV 02 (Chukwuemeka Okafor) vs Senior BA, GenAI: 10 details removed, analysed on the blind text. The large spaCy model fits within Streamlit Cloud's memory | The "What the AI sees" column is for transparency in a demo. In a real tool the recruiter would screen from the blind version too, and names would appear only after the decision is recorded (increment 3). Splitting one long file into smaller ones (`app.py`, `recruiter.py`, `results_view.py`) made each part easier to read and change. |
| R4 | Fixed `blind.py` for everything run 1 exposed: street addresses without a label, immigration status, birthplace, referees under a References heading, names cut at line breaks, full and hyphenated names, languages, degrees | Run 1 showed the rules assumed a tidy CV layout | Run 2: development 131/131 caught and 89/89 kept; held-out 34/34 caught, 37/37 kept. Not independent any more, so run 1 (62%) stays the official result | Rerun the practice set after every fix: two fixes caused regressions (a personal website missed, "de" removed from a university name) that it caught immediately. |
| R3 | Held-out test: 4 fictional CVs written by me without seeing the rules (US, India, Australia, UAE formats), answer key agreed before the run, and a stricter eval (an item only counts as caught if every letter and digit of it is removed, everywhere it appears) | Practice CVs written alongside the rules can't show how the rules do on real CVs | **First and official result: 21/34 identifiers caught (62%), 35/37 job details kept (95%).** Misses: all addresses (no "Address:" label), all immigration statuses (no rule), birthplace, 5 of 7 referee details, one Middle Eastern surname ("Al-Hassan"). Hidden damage: "Business Analyst" removed throughout one CV. Details: `docs/recruiter_mode/increment_1_results.md` | The failures came from our own assumptions about CV layout, not from name detection. Fix the marking before the test, never the rules; and never overwrite the first score. |
| R2 | `blind.py`: Presidio (names, emails, phones, URLs, nationality) plus our own rules for addresses, date of birth, age, marital status, titles, pronouns and gender; names accepted only from the top 3 lines, then removed wherever they repeat. `eval_blind.py` scores it against `test_data/recruiter/answer_key.json` (15 synthetic CVs, names from 12 regions) | Out of the box, Presidio missed the street address, "Married" and "He", and wrongly flagged "6 years' experience" and the job city. A first version also hid "Alibaba Cloud", "Indra" and "Severn Trent" as people's names | Development set: 131/131 identifiers caught, 89/89 job details kept | An off-the-shelf privacy tool isn't a privacy feature until it's tuned to the job. 100% on a test set written alongside the rules is marking your own homework, so the headline number comes from a held-out set. |
| R1 | Added recruiter mode to the PRD (section 9R) and scoped increment 1 as user stories with acceptance criteria (`docs/recruiter_mode/increment_1_blind_screening.md`) | Plan before building; each increment becomes one LinkedIn post | Decisions: one CV at a time plus an eval; direct identifiers only, proxies kept and measured later; synthetic CVs drafted by Claude and reviewed by me; blind mode in recruiter mode only | A quick probe showed spaCy's small model missed 2 of 12 names (Indian and South African), the large model caught all 12. Blinding removes identifiers, not bias. |

## Stage 2: AI matching (started 10 October 2026)

The app is now **FitProof**, live at https://fitproof-panchali.streamlit.app/: paste a JD, upload a CV, and Claude Haiku 4.5 on Amazon Bedrock labels each requirement and quotes CV evidence. The code calculates the score and verdict from the spec (`docs/AI_SPEC.md`) and checks every quote. The keyword version is kept as `app_keyword.py`.

### Results on the test set (11 October 2026)

| JD | Keyword version | AI version | My view |
| --- | --- | --- | --- |
| jd_01: AI Solutions Adoption & Delivery Specialist | Found 10 skills; missed workshops, AI adoption, pilots to production, backlog | 55%, Possible fit. Found every answer-key item, no deal-breakers | Right: strong on AI delivery, gaps in training design and production troubleshooting |
| jd_02: Senior Business Analyst, GenAI Foundation (Danske Bank) | Found 7 skills; missed epics and user stories, procurement, workshops, APIs | 81%, Strong fit. Found every answer-key item, no deal-breakers | Right |

| # | Change | Why | Result | What I learned |
| --- | --- | --- | --- | --- |
| 21 | Deployed to Streamlit Community Cloud at https://fitproof-panchali.streamlit.app/. Bedrock key added in the app's Secrets | Make FitProof something I can share and put on my CV | Live; sample and real analyses both work | Root-level secrets become environment variables, so boto3 finds the key exactly as it does from `.env`. Secrets must be valid TOML: `NAME = "value"` on one line with straight quotes. Every `git push` redeploys the app. |
| 20 | Public-demo safeguards: "Try a sample" button showing a saved analysis of a fictional CV (`sample/`), 3 analyses per visit, 20,000-character limit per document. Commits 299ec6a, 43c7b37, 9fcc9f1 | I wanted no password or invite link, so the protection had to be invisible | A recruiter can see a full result in one click, at no cost | One analysis costs about 2 cents, and the AWS free plan stops rather than bills, so the real risks were abuse and personal data, not a big bill. The per-visit limit resets on refresh: enough for casual use, not a hard limit. Never put a real CV in a public sample. |
| 19 | Summary card: green, amber and red breakdown bar, and a score per group (Required, Qualifications, Nice to have). Requirements tab: filter (All, Gaps only, Evidenced only), gaps listed first. Commit 029b094 | 17 identical rows hid why the score was what it was | You can see where the score comes from, and what to work on, at a glance | Group scores reuse the same `calculate_score` function, so they always agree with the main score. Very long pastes can get cut off; check the end of the file after pasting. |
| 18 | CV rewrites: stricter prompt (keep every number and named system, keep who did what for whom), code drops rewrites that lose or add a number or whose "Now" line isn't in the CV, and the screen highlights every word the AI added. Commit a7377ef | Rewrites turned "drove AWS partner programme delivery" into "ran vendor assessments", added governance work I didn't do, and dropped my 70% and €500K results | Numbers now survive. Overclaims still appear, but stand out instantly in orange | For rewriting, the AI's goal (cover the requirement) conflicts with the user's need (stay truthful). Code can't judge meaning, so the design makes changes visible and leaves the decision to me. Next idea: turn rewrites into "how to talk about this gap". |
| 17 | Named the app FitProof ("See your fit. Prove it with your CV."). Custom theme in `.streamlit/config.toml`: blue accent, Inter font, warm background. Clearer wording: numbered inputs, "Analyse my fit" button, "How it works" box, tab counts. Commits b7b545e and earlier | Default Streamlit looked generic and the red button read like an error | Looks like a product rather than a demo | Theme settings only load when the app starts, and Streamlit only finds them in a folder named `.streamlit` (with the dot). RoleFit and JobFit were already taken. |
| 16 | New AI results screen in `app.py`: summary card (verdict, score, counts), deal-breaker box, tabs for requirements (with quoted evidence), CV rewrites and extra strengths. Analyse button, result kept between clicks. Keyword version renamed `app_keyword.py` | The AI output (verdict, evidence, deal-breakers) didn't fit the old bullet-list screen | Working on real JDs | Streamlit reruns the whole script on every click, so the AI call sits behind a button and the result is stored in `st.session_state`, otherwise every click would cost credits. |
| 15 | Upgraded Streamlit from 1.28.1 to 1.65.0. Commit 57c71c6 | Needed bordered cards and other newer layout features, and an upgrade before going online anyway | Old app still worked after the upgrade | Test that nothing broke before building on an upgrade. |
| 14 | Deal-breakers must quote JD wording that contains a must-word ("must", "required", "essential", "mandatory", "minimum", "at least"), checked in code. Commit 4af2e26 | On jd_02, Claude made "2-3 years of experience as a Business Analyst" a deal-breaker although the JD never says it's mandatory, and I'd marked it only partly evidenced | jd_02 went from "Not a fit" (83%) to "Strong fit" (81%) | My product rule: years of experience only block a role if the JD says "minimum", "at least" or "must". Rules that matter go in code, not just the prompt, because the model doesn't always follow instructions. |
| 13 | Evidence is a list of exact quotes, each checked separately. Deal-breakers must quote the JD's own wording, checked against the JD. "Or similar" counts as flexible. Commit e886992 | On jd_01, Claude glued separate CV parts together with "\|", changed words, and wrote opinions as quotes (6 failed the check). It also flagged 3 ordinary duties and "Master's degree or similar" as deal-breakers | Failed quotes fell from 6 to 2. Deal-breakers fell from 3-4 to none. jd_01 went from "Not a fit" to 55%, Possible fit | Make the AI prove its claims, then check the proof in code. Output varies a little between runs even at temperature 0, so judge it on a test set, not one run. |
| 12 | Added `ai_matcher.py` (prompt from the spec, Bedrock call, scoring, verdict, quote check) and `try_ai.py` (runs one JD from the terminal). CV kept in `private/`; AI results ignored by Git. Commits 66427a3, 4ed2ebf | First working version of the AI matcher | Ran end to end on jd_01 | A test result can contain personal data too: CV quotes went into `.gitignore` before the first commit. |
| 11 | Bedrock quotas approved; `test_bedrock.py` and the playground both get replies from Claude Haiku 4.5 | Needed before any AI code could run | Working | Quota requests for new accounts ask for the AWS default values. |

## Getting ready for Stage 2 (10 October 2026)

I stopped the keyword fixes here. Clean names, grouping and ranking will be replaced by the AI version, so polishing them would be wasted effort. Before starting Stage 2, I did the three things it depends on.

| # | Change | Why | Result | What I learned |
| --- | --- | --- | --- | --- |
| 9 | Set up AWS for Bedrock: new personal account on the free plan ($100 credits, no card), region eu-north-1 (Stockholm), Bedrock API key stored in `.env`, Anthropic use-case form submitted, `test_bedrock.py` written (commit 24e4a89). Requested quota increases for Haiku 4.5 cross-region: 5,000,000 tokens and 10,000 requests per minute (the AWS defaults); pending | The AI version will run on Claude through Amazon Bedrock, matching my AWS AI Practitioner and Bedrock specialisations | Blocked for now: every model shows 0 tokens per minute, Amazon Nova included. Claude Haiku 5.5 isn't available to the account; Haiku 4.5 is, once quotas rise | Read errors closely, because each one narrows the cause: AccessDenied (model not available), ResourceNotFound (form not submitted), Throttling (quota is 0). New accounts start with zero quotas. EU inference profiles keep the CV inside the EU. |
| 8 | Added boto3 1.43.111 to requirements.txt. Commit c451f58 | boto3 is Amazon's Python library for reaching Bedrock | Installed and pinned | Each new library goes into requirements.txt the moment it's installed. |
| 7 | Pinned pypdf to 6.19.0 in requirements.txt. Commit 1014400 | The file asked for pypdf 3.17.1, but the app runs on 6.19.0. Nobody could install the app from GitHub as it was | requirements.txt now matches what I tested | `==` pins an exact version so everyone gets the same setup. Streamlit 1.28.1 is from 2023 and needs upgrading before the app goes online. |
| 6 | Added a test set: 2 real JDs in `test_data/`, each with an answer key (required, nice to have, qualifications). Commit 8b7c285 | I couldn't rerun earlier tests because I didn't keep the JD. Without fixed inputs, I can't show a change helped | Keyword version finds 10 skills in jd_01 and 7 in jd_02, and misses most of what each role is about: workshops, AI adoption, pilots to production, epics and user stories, vendor procurement | Keywords catch tool names, but roles are described in sentences. That's the case for Stage 2. A test set also needs a poor-fit JD (a negative control) to check the app can say no. My CV stays out of the repo. |
| 5 | In app.py line 37, cleaned each dictionary phrase with `normalize_text` before searching. Removed "c#". Commit 82c0785 | The app stripped punctuation from the JD and CV but not from the dictionary, so 14 phrases like "node.js" and "scikit-learn" could never match | Punctuated skills now match. "c#" removed because it would become the single letter "c" | Python uses indentation to understand structure. Lines in the same block must start at the same position, or the app fails with IndentationError. |

## Stage 1: honest scores

Four changes, all saved on GitHub. On my test JD and CV, RAG no longer shows as missing and the match score is 44%, up from 39%.

| # | Change | Why | Result | What I learned |
| --- | --- | --- | --- | --- |
| 4 | Added "genai" to the generative_ai line. Added a Microsoft platform group: Dynamics 365 (also "d365", "microsoft dynamics"), Power Automate, Copilot Studio, Microsoft Fabric, Azure DevOps, SharePoint. Commit f08c1dd | My CV says "GenAI", which the dictionary didn't recognise. My main tools weren't in the dictionary at all | Score rose from 39% to 44% (8 of 18): generative_ai moved to Matched. The Microsoft tools don't show yet because this JD doesn't ask for them | The file is made of groups wrapped in `{ }`. A new group goes between the `},` that closes one group and the start of the next. Lines starting with `#` are comments that Python ignores. The app only lists skills the JD asks for. |
| 3 | Removed five ambiguous words: "go", "rest", "pm", and "planning" and "reasoning" from the AI-agent skills. Kept "golang", "rest api", "product manager", "plan generation", "agentic reasoning". Commit 4567f68 | These words appear in ordinary sentences ("the rest of the team", "strong reasoning skills") far more often than as skills | Score stayed 39% (7 of 18), because my test JD doesn't use them. The skills still missing really are missing from that CV | Every word is a trade-off between false alarms and missed skills. I kept "ai" and "react" because removing them would miss more than it fixes. |
| 2 | Removed `"cv"` from the computer_vision line and deleted the duplicate `"computer_vision_cv"` line. Commit e5c6a62 | JDs say "send your CV", so the app invented a computer vision requirement. The duplicate line also claimed "computer vision" a second time | computer_vision no longer appears. Score stayed 39% because my test JD didn't trigger it | One test case can't prove a fix. I need a small set of real JDs to check each change against. |
| 1 | Deleted the duplicate `"retrieval_augmented_generation"` line in skills_dictionary.py. Commit 2346475 | The phrase "retrieval augmented generation" belonged to two skills. The later line won, so the JD showed a skill my CV seemed to lack, even though my CV says "RAG" | RAG appears only under Matched Skills | The app turns the dictionary into a lookup table with one row per phrase. A phrase listed twice gets overwritten, like a duplicate customer record in an ERP. |

## Setup fixes (8 October 2026)

| # | Problem | Fix | What I learned |
| --- | --- | --- | --- |
| 3 | Error: app.py asked for CATEGORY_DISPLAY_NAMES, which the Codespace copy of skills_dictionary.py didn't have | Moved the old files into a backup folder, then ran `git pull` | The Codespace and GitHub are separate copies. `git pull` brings GitHub's latest files into the Codespace. |
| 2 | Error: No module named 'pypdf' | Ran `pip install pypdf` in a free terminal | Python apps depend on add-on packages. requirements.txt lists them. |
| 1 | App page wouldn't open | Closed both terminals, ran `pkill -f streamlit`, started the app once on port 8501, opened it from the Ports tab | A terminal running an app is busy. `0.0.0.0` only works inside the Codespace; the browser needs the forwarded app.github.dev link. |

## How to work on this project

Start of each session:

```
git pull
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.enableXsrfProtection false --server.enableCORS false
```

Then open port 8501 from the Ports tab (globe icon).

Saving a change:

1. `git status --short` shows what changed. **M** = modified, **??** = new file Git isn't tracking.
2. `git add <files> && git commit -m "note"` takes a snapshot with a note.
3. `git push` uploads it. `main -> main` means it worked.

`.gitignore` lists files that are never uploaded: `.env` (private keys), `.venv/`, `__pycache__/` and `backup/`.

## Up next

- [x] Protect `.env` with a `.gitignore` and save changes to GitHub
- [x] Remove ambiguous short words ("cv", "go", "rest", "pm", "planning", "reasoning"). "ai" and "react" kept on purpose
- [x] Add my tools: Dynamics 365, Copilot Studio, Power Automate, Azure DevOps, Fabric
- [x] Fix the 14 phrases with punctuation that can never match (Change 5)
- [x] Update requirements.txt to the tested pypdf version (Change 7)
- [x] Start a test set (Change 6: 2 JDs with answer keys)
- [x] Choose the AI service for Stage 2: Amazon Bedrock, Claude Haiku 4.5, EU profile
- [x] Write the AI matching spec (`docs/AI_SPEC.md`)
- [x] Bedrock quotas approved, Claude Haiku 4.5 working
- [x] AI matcher working from the terminal on both test JDs
- [x] Connect the AI matcher to the Streamlit screen (FitProof)
- [ ] Rewrites, next iteration: "how to talk about this gap" instead of rewriting CV lines
- [x] UI: coloured breakdown bar, per-group scores, filter with gaps first
- [x] Deploy FitProof online: https://fitproof-panchali.streamlit.app/
- [x] Recruiter mode increment 1: blind screening
- [ ] Recruiter mode increment 2: bias test suite
- [ ] Increment 3: a saved requirement list per job that a person approves; "Questions to ask at interview" instead of rewrites
- [ ] Bedrock API key expires 30 days after creation (early November): create a new one and update the app's Secrets
- [ ] AWS free plan ends 10 April 2027 or when the $100 credits run out: decide then whether to upgrade or switch provider
- [ ] 2 quotes per run still fail the evidence check: find out whether it's PDF text or Claude rewording
- [x] Stage 2: AI reads the JD, picks out requirements, and marks each as required, nice-to-have or qualification
- [x] Stage 2: missing must-haves give "Not a fit", only when the JD uses must-words
- [ ] Add a poor-fit JD to the test set: an AI job title with an accounting or finance body (CPA, CFA)
- [x] Upgrade Streamlit (1.65.0)
- [ ] Idea: a third list, "Your strengths this JD didn't ask for"
- [ ] Parked (the AI version replaces these): clean skill names, technical vs soft grouping, ranking missing skills, plurals like "pipelines", generic words like "development", duplicate skills, Sage
- [ ] Stage 3: remove unsourced claims from the PRD and narrow the target user
