# Recruiter shortlist and decisions

**Built:** 14 October 2026 · **Status:** Done · **Owner:** Panchali Das

## What it does
A recruiter picks a job and sees all 20 fictional candidates in one table, like an applicant tracking system: candidate number, current role (from the blind CV), evidence group, required items met and missing, and stage. Ticking a row opens the evidence per requirement and the blind CV, with the decision beside it.

## Design decisions
| Decision | Choice | Why |
| --- | --- | --- |
| Order | Grouped by evidence for required items (none missing / a few missing, up to a third / most missing), then by candidate number. Never ranked, no percentage | A ranked list invites people to accept the top without checking (automation bias, AI Act Art. 14) |
| What the list shows | Current role first | Recruiters spend about 7.4 seconds on a first look, mostly at current title and employer; blinding keeps both |
| Decisions | Advance to phone screen, Hold or Reject, with a reason from a list; a note is required for "Other" | Matches how ATS tools record decisions; listed reasons make the log reportable |
| Names | Shown only after a decision is recorded | Keeps the decision itself blind |
| Left out on purpose | Bulk reject, automatic advancing, AI ranking | The parts of today's tools that make AI screening risky |
| Audit log | Append-only row per decision: time, stage, reason, note, the AI group and counts shown at that moment, name revealed; CSV download | Shows where a person overrode the AI and what they saw; demo log lasts one visit |
| Cost | `screen_all.py` screens every CV once and saves the results | The public demo makes no AI calls |

## How it was shaped
Version 1 (a list of sentences with Review buttons and the candidate report in a narrow column) looked wrong, and version 2 was built before checking how recruiters work today. Version 3 started from research into Workday, Greenhouse and similar tools, then kept the familiar list and left out the risky parts. See build log R9 to R12.

## Known gaps
- Fictional candidates only; the 15 original test CVs are short, so most land in "most missing".
- The log isn't stored between visits.
- Candidate 05's saved result was made before the address-place fix, so the AI saw "[NAME]" where the city was; no requirement depends on it.
