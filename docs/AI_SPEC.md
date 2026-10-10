# AI Matching Spec (Stage 2)

**Status:** Agreed 10 October 2026
**Owner:** Panchali Das

The AI version reads the job description and the CV together and returns a weighted match score, a verdict, deal-breakers, and evidence from the CV for every matched skill. It replaces the keyword matcher, which catches tool names but misses capabilities described in sentences (see `test_data/`).

## Decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Inputs | JD and CV together, in one call | The AI can see that "GenAI" in the CV matches "generative AI" in the JD |
| Score | Weighted: required skills count more than nice-to-haves | A missing must-have matters more than a missing bonus |
| Deal-breakers | A missing must-have (a required tool or platform, certification, language, minimum years, degree) gives the verdict "Not a fit", whatever the score, with the reason shown at the top | "70% match, but requires a CPA" is a different message from "70% match" |
| Evidence | Every matched skill quotes the CV line that proves it | I can check every claim, and it stops the AI inventing skills |
| Partial matches | Close but not exact counts as half, shown as "partly evidenced" | Tells me which CV lines to reword |
| Suggestions | Rewrite tips based only on experience already in the CV | Never suggests claiming something I haven't done |
| Extras | Up to 5 relevant strengths the JD didn't ask for | Useful for cover letters and interviews |

## What the AI does

1. Reads the JD and lists every requirement, labelling each as **required**, **nice to have** or **qualification**.
2. Ignores boilerplate: company description, benefits, equal-opportunity statements.
3. For each requirement, checks the CV and marks it **evidenced**, **partly evidenced** or **missing**, quoting the CV line for the first two.
4. Flags any missing qualification or explicit must-have as a **deal-breaker**, and notes any related experience in the CV.
5. Suggests up to 5 rewrites of existing CV lines to cover partly evidenced or missing requirements.
6. Lists up to 5 CV strengths relevant to the role that the JD didn't ask for.

## Scoring

| Requirement type | Points available |
| --- | --- |
| Required | 3 |
| Qualification | 3 |
| Nice to have | 1 |

Evidenced earns full points, partly evidenced earns half, missing earns 0.

**Match score** = points earned ÷ points available × 100, rounded.

The app calculates the score in code from the AI's labels, rather than asking the AI for a number. The AI judges, and the code does the arithmetic, so the same labels always give the same score.

| Verdict | Rule | Meaning |
| --- | --- | --- |
| Not a fit: missing must-have | Any deal-breaker, whatever the score | Shows each missing must-have, plus any related experience in the CV |
| Strong fit | Score 75 or more | Apply |
| Possible fit | Score 50 to 74 | Worth applying after tailoring the CV |
| Weak fit | Score below 50 | Probably skip |

When a must-have is missing but the CV shows something related, the app says so, e.g. "Requires Google Cloud. You have AWS and Azure, so check whether they'd accept equivalent experience." I make the final call.

## Rules the AI must follow

- Only use what is written in the CV. Never assume experience that isn't stated.
- Every "evidenced" or "partly evidenced" item must quote CV text word for word. No quote means "missing".
- Rewrite suggestions may rephrase existing experience but must not add tools, numbers or responsibilities that aren't in the CV.
- Return only the structured output below, with no extra commentary.

## Output format

The AI returns JSON, which the app reads and displays:

```json
{
  "role_title": "Senior Business Analyst, GenAI",
  "requirements": [
    {
      "skill": "Writing epics and user stories",
      "type": "required",
      "status": "partly evidenced",
      "cv_evidence": "Wrote UAT success criteria for the order assistant",
      "note": "Shows acceptance criteria, but not epics or user stories by name"
    }
  ],
  "deal_breakers": [
    {
      "requirement": "Google Cloud experience (must have)",
      "related_cv_evidence": "AWS Certified AI Practitioner; Azure DevOps"
    }
  ],
  "rewrite_suggestions": [
    {
      "current_cv_line": "Worked with sales teams in 11 countries",
      "suggested_line": "Coordinated requirements with stakeholders across 11 countries",
      "covers": "Stakeholder coordination across locations"
    }
  ],
  "extra_strengths": ["Power Automate agent live in 11 countries"]
}
```

## How we'll test it

Run each JD in `test_data/` with the same CV and compare the AI's requirements list with the answer key:

- **Recall:** how many answer-key requirements the AI found
- **Precision:** how many of the AI's requirements are real (not invented or boilerplate)
- **Type accuracy:** required, nice to have and qualification labelled correctly
- **Evidence check:** every quoted CV line actually appears in the CV

Target from the PRD: 75% or better on recall and precision. Each result goes in the build log next to the keyword version's result for the same JD.

## Privacy

- Requests go to Claude Haiku on Amazon Bedrock through the EU inference profile, so the CV is processed inside the EU.
- The app doesn't store CVs or results. Nothing leaves the session except the request to Bedrock.
- My CV is never committed to this repository.

## Open questions

None. Weights of 3 (required), 3 (qualification) and 1 (nice to have) confirmed on 10 October 2026. Revisit only if testing shows scores that don't match my judgement.
