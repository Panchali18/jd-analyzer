# Held-out test set (synthetic)

Four **fictional** CVs written by Panchali without seeing the redaction rules in `blind.py`, in realistic, messy formats from the US, India, Australia and the UAE. No real person's data is used.

`answer_key.json` lists every personal detail that must be removed (including referees' details and immigration status) and every job-relevant detail that must survive. Labelling decisions are recorded in `docs/recruiter_mode/increment_1_blind_screening.md`.

**Rule:** the first eval run on this set is the reported result. Rules may be improved afterwards, but the first score is never overwritten.
