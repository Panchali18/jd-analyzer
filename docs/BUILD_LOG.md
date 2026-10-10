# JD Analyzer Build Log

Every change to the JD Analyzer, with the problem, the fix, the result, and what I learned. It combines a changelog (what changed) and a decision log (why). Newest first in each table.

## Getting ready for Stage 2 (10 October 2026)

I stopped the keyword fixes here. Clean names, grouping and ranking will be replaced by the AI version, so polishing them would be wasted effort. Before starting Stage 2, I did the three things it depends on.

| # | Change | Why | Result | What I learned |
| --- | --- | --- | --- | --- |
| 9 | Set up AWS for Bedrock: new personal account on the free plan ($100 credits, no card), region eu-north-1 (Stockholm), Bedrock API key stored in `.env`, Anthropic use-case form submitted, `test_bedrock.py` written | The AI version will run on Claude through Amazon Bedrock, matching my AWS AI Practitioner and Bedrock specialisations | Blocked for now: every model shows 0 tokens per minute, Amazon Nova included. Claude Haiku 5.5 isn't available to the account; Haiku 4.5 is, once quotas rise | Read errors closely, because each one narrows the cause: AccessDenied (model not available), ResourceNotFound (form not submitted), Throttling (quota is 0). New accounts start with zero quotas. EU inference profiles keep the CV inside the EU. |
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
- [ ] Wait for AWS quotas to rise above 0; check Bedrock → Quotas daily and request an increase for Haiku 4.5 (Geo cross-region)
- [ ] If quotas are still 0 after a few days: build on Gemini's free tier first, with an `AI_PROVIDER` setting so switching to Bedrock is one word
- [ ] Stage 2: AI reads the JD, picks out skills, and marks each as required, nice-to-have or qualification
- [ ] Stage 2: treat missing qualifications (like a CPA) as deal-breakers that override the percentage
- [ ] Add a poor-fit JD to the test set: an AI job title with an accounting or finance body (CPA, CFA)
- [ ] Upgrade Streamlit from 1.28.1 and retest before putting the app online
- [ ] Idea: a third list, "Your strengths this JD didn't ask for"
- [ ] Parked (the AI version replaces these): clean skill names, technical vs soft grouping, ranking missing skills, plurals like "pipelines", generic words like "development", duplicate skills, Sage
- [ ] Stage 3: remove unsourced claims from the PRD and narrow the target user
