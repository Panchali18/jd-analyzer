# JD Analyzer & CV Matcher

Paste a job description, upload your CV, and see how well you fit: which requirements you meet, where the gaps are, and how to reword your CV for that role.

I'm building it as a portfolio project for AI product roles, and I use it in my own job search.

## What it does

**Today (version 1, keyword matching)**
- Reads a job description (pasted or uploaded) and a CV (PDF or text)
- Finds skills in both using a dictionary of about 240 skills and their synonyms
- Shows a match score, matched skills, missing skills and tailoring tips

**Next (version 2, AI matching)**

Keywords catch tool names like Python or Power BI, but miss capabilities written as sentences, like "run workshops" or "take pilots into production". Version 2 uses Claude to read the JD and CV together. It:
- labels each requirement as required, nice to have or a qualification
- quotes the CV line that proves each match, so every claim can be checked
- gives a weighted score and a verdict: Strong, Possible or Weak fit
- says "Not a fit" when a must-have is missing, such as a certification, whatever the score
- suggests CV rewrites based only on experience already in the CV

The AI does the judging, and the code does the scoring, so the same labels always give the same score. Full details are in the [AI spec](docs/AI_SPEC.md).

## Tools

| Tool | What it's for |
| --- | --- |
| Python | The language the app is written in |
| Streamlit | Turns the Python script into a web page, with no web code needed |
| pypdf | Reads the text out of PDF files |
| Amazon Bedrock | AWS's service for using AI models. Version 2 uses Claude Haiku 4.5 through the EU profile, so CV data stays in the EU |
| boto3 | Amazon's Python library, used to send requests to Bedrock |
| GitHub Codespaces | A browser-based workspace for running and testing the app |

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

## Status

Version 1 works. Version 2 is specified, and AWS is set up. It's waiting on Bedrock quota approval before the build starts.
