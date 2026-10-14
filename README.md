# FitProof

**See your fit. Prove it with your CV.**

**Try it live: [fitproof-panchali.streamlit.app](https://fitproof-panchali.streamlit.app/)** (click *Try a sample* to see an example without uploading anything)

Paste a job description, upload your CV, and see how well you fit: which requirements you meet, with the CV line that proves each one, where the gaps are, and any must-haves you're missing.

I'm building it as a portfolio project for AI product roles, and I use it in my own job search.

## What it does

**Version 1: keyword matching** (kept as `app_keyword.py`)
- Reads a job description (pasted or uploaded) and a CV (PDF or text)
- Finds skills in both using a dictionary of about 240 skills and their synonyms
- Shows a match score, matched skills, missing skills and tailoring tips

**Version 2: AI matching** (`app.py`, live)

Keywords catch tool names like Python or Power BI, but miss capabilities written as sentences, like "run workshops" or "take pilots into production". Version 2 uses Claude to read the JD and CV together. It:
- labels each requirement as required, nice to have or a qualification
- quotes the CV line that proves each match, so every claim can be checked
- gives a weighted score and a verdict: Strong, Possible or Weak fit
- says "Not a fit" when a must-have is missing, such as a certification, whatever the score
- lists right-to-work conditions separately as "Check yourself", because a CV can't show them, so they never block the verdict
- suggests CV rewrites and highlights every word the AI added, so overclaims are easy to spot

The AI does the judging, and the code does the scoring, so the same labels always give the same score. The job description is read once into a fixed list of requirements, so every CV is measured against the same list. Full details are in the [AI spec](docs/AI_SPEC.md).

**Recruiter mode (demo)**

Switch the mode in the sidebar to see the other side: screening a candidate with their personal details hidden. CV screening is a high-risk use under the EU AI Act, so this mode is built to show what compliance by design looks like. Fictional CVs only.
- removes names, contact details, address, age, gender markers, nationality, marital status, immigration status and referees before the AI sees the CV
- tested on 19 fictional CVs from 12 regions, with the first held-out score kept as the official result (62%, since fixed)
- checked that blinding doesn't change the match (−1, 0 and +3 points on three CVs)

Next: a bias test suite, a recruiter decision step with an audit log, and a model card. Plan and results: [docs/recruiter_mode](docs/recruiter_mode/).

## Tools

| Tool | What it's for |
| --- | --- |
| Python | The language the app is written in |
| Streamlit | Turns the Python script into a web page, with no web code needed |
| pypdf | Reads the text out of PDF files |
| Amazon Bedrock | AWS's service for using AI models. Version 2 uses Claude Haiku 4.5 through the EU profile, so CV data stays in the EU |
| boto3 | Amazon's Python library, used to send requests to Bedrock |
| Microsoft Presidio and spaCy | Find personal details in a CV so recruiter mode can hide them. Both free and open source |
| GitHub Codespaces | A browser-based workspace for running and testing the app |
| Streamlit Community Cloud | Free hosting: runs the app from this GitHub repository and redeploys on every push. The Bedrock key is stored in its Secrets, never in the code |

## How I'm building it

- **Spec first.** [AI_SPEC.md](docs/AI_SPEC.md) sets out what the AI must and must not do.
- **Measured, not guessed.** [test_data/](test_data/) holds real job descriptions with my own answer keys. Both versions are scored against them.
- **Every change logged.** The [build log](docs/BUILD_LOG.md) records each change, why I made it and what I learned.
- **Privacy.** CVs are never stored or committed. API keys live in `.env`, which `.gitignore` keeps out of the repository.

## Run it

In GitHub Codespaces:

```
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.enableXsrfProtection false --server.enableCORS false
```

Then open port 8501 from the **Ports** tab.

For version 2, add a Bedrock API key to a `.env` file:

```
AWS_BEARER_TOKEN_BEDROCK=your-key-here
```

## Documents

- [Product requirements (PRD)](docs/PRD.md)
- [Technical design](docs/TECHNICAL.md)
- [AI matching spec](docs/AI_SPEC.md)
- [Build log](docs/BUILD_LOG.md)
- [Recruiter mode plan and results](docs/recruiter_mode/)

## Status

FitProof is live on Streamlit Community Cloud, running Claude Haiku 4.5 via Amazon Bedrock (EU). On both test JDs it found every requirement in my answer key, where keyword matching missed most of them. Recruiter mode (blind screening on fictional CVs) is live as a demo. Public-demo safeguards: a free sample result, 3 analyses per visit, a document length limit, and no storage of uploaded CVs.
