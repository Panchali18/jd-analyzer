# Recruiter mode test set (synthetic)

Every CV here is **fictional**: invented names, contact details and addresses, written to test blind screening. No real person's data is used.

- `cv_01.txt` to `cv_15.txt`: synthetic CVs with names from 12 regions, including family-name-first names, accents, hyphens, four-part names and a first name repeated in the text.
- `answer_key.json`: for each CV, every personal detail that must be removed (`pii`, with its type and, for names, the region) and every job-relevant detail that must survive (`keep`).

These 15 CVs were written alongside the redaction rules, so they are a **development set**. The headline result comes from a separate held-out set written without seeing the rules.
