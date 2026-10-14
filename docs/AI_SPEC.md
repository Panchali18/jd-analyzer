# AI Matching Spec (Stage 2)

**Status:** Agreed 10 October 2026
**Owner:** Panchali Das

The AI version reads the job description and the CV together and returns a weighted match score, a verdict, deal-breakers, and evidence from the CV for every matched skill. It replaces the keyword matcher, which catches tool names but misses capabilities described in sentences (see `test_data/`).

## Decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Inputs | Two calls (changed 13 October 2026): call 1 reads the JD alone and fixes the requirement list; call 2 judges the CV against that list, with the JD for context | Every candidate for a job is measured against the same list. With one call, the list changed whenever the CV text changed, moving scores by up to 12 points |
| Score | Weighted: required skills count more than nice-to-haves | A missing must-have matters more than a missing bonus |
| Deal-breakers | A missing must-have (a required tool or platform, certification, language, minimum years, degree) gives the verdict "Not a fit", whatever the score, with the reason shown at the top | "70% match, but requires a CPA" is a different message from "70% match" |
| Evidence | Every matched skill quotes the CV line that proves it | I can check every claim, and it stops the AI inventing skills |
| Partial matches | Close but not exact counts as half, shown as "partly evidenced" | Tells me which CV lines to reword |
| Suggestions | "Talking about gaps" (changed 14 October 2026, replacing CV rewrites): for up to 5 important gaps, the closest CV line, one or two honest sentences for a cover letter or interview, and one step to close the gap | Rewriting CV lines pushed the AI to overclaim. Naming a gap openly and pointing to real experience is what interviewers want anyway |
| Extras | Up to 5 relevant strengths the JD didn't ask for | Useful for cover letters and interviews |
| Right to work (added 14 October 2026) | Work eligibility, visa or sponsorship, citizenship or residency conditions are typed "eligibility": not scored, never a deal-breaker, shown as "Check yourself" (candidate) or "Check with the candidate" (recruiter) | A CV can't show right to work and usually doesn't mention it. Blocking a 60% match on it overrode the score with something the candidate already knows |

## What the AI does

1. Reads the JD on its own (call 1) and lists every requirement, labelling each as **required**, **nice to have** or **qualification**. The code holds call 2 to this list (`apply_fixed_list`).
2. Ignores boilerplate: company description, benefits, equal-opportunity statements.
3. For each requirement, checks the CV and marks it **evidenced**, **partly evidenced** or **missing**, quoting the CV line for the first two.
4. Flags any missing qualification or explicit must-have as a **deal-breaker**, and notes any related experience in the CV.
5. For up to 5 important gaps (required or qualification, missing or partly evidenced), suggests how to talk about each one honestly and one step to close it.
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

### Deal-breaker check (added 11 October 2026)

Right-to-work conditions never count as deal-breakers (see Decisions); the code moves them to a separate list with `separate_eligibility`.

A deal-breaker only counts if Claude quotes the JD's own wording, the code finds that wording in the JD, and the wording contains a must-word: "must", "required", "essential", "mandatory", "minimum" or "at least". Years of experience stated without one of these words (e.g. "2-3 years as a Business Analyst") lower the score but don't block the role. "Or similar" and "or equivalent" are flexible.

## Rules the AI must follow

- Only use what is written in the CV. Never assume experience that isn't stated.
- Every "evidenced" or "partly evidenced" item gives a list of exact CV quotes, never joined with "|" or "..." and never with explanation mixed in. The app checks each quote against the CV. No quote means "missing".
- Gap advice is one sentence of at most 30 words that starts with something specific from the CV and connects it to the requirement in plain words. It doesn't open with what's missing, doesn't promise to learn on the job, avoids stock phrases, never claims the requirement is met and adds nothing that isn't in the CV. If nothing in the CV comes close, the gap is left out. The prompt includes one bad and one good example (changed 14 October 2026, after the first version produced defensive, padded sentences).
- The app blanks a "closest experience" quote that isn't in the CV word for word, and drops any advice containing a number the CV doesn't have. (History: the earlier CV rewrites kept inserting JD phrases, e.g. turning "drove AWS partner programme delivery" into "ran vendor assessments", which is why they were replaced.)
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
  "gap_talk": [
    {
      "requirement": "Experience running vendor assessments or procurement",
      "closest_cv_evidence": "Worked with sales teams in 11 countries",
      "how_to_say_it": "I haven't run a formal vendor assessment, but I've worked closely with sales teams in 11 countries and know what a buyer needs to see.",
      "how_to_close_it": "Run a small vendor comparison for an AI tool your team is considering, using a simple scoring sheet."
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
