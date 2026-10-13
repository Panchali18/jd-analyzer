# Increment 1: Blind Screening Mode

**Status:** Scoped 13 October 2026 · **Build started:** 13 October 2026, 14:22 · **Status:** Done 13 October 2026 · **Owner:** Panchali Das
**Part of:** [Recruiter mode, compliant by design](../PRD.md) (PRD section 9R)

## Goal

In recruiter mode, remove a candidate's direct identifiers from the CV **before** Claude sees it, show the recruiter exactly what was removed, and measure honestly how many identifiers the redaction catches, including names from outside Europe.

**Success measure:** the percentage of labelled PII items caught across the synthetic test set, broken down by type and by the region the name comes from. Every miss is listed and reported.

## Decisions (13 October 2026)

| Decision | Choice | Why |
| --- | --- | --- |
| Scope | One synthetic CV at a time, plus the catch-rate eval. Ranking several CVs comes later | Smallest increment that can be shown in a screen recording |
| What is redacted | Direct identifiers only: name, email, phone, home address, date of birth, age, gender markers (titles, gendered pronouns), nationality, marital status, profile URLs | GDPR data minimisation: the match doesn't need them |
| Proxies | Kept: university, employers, graduation years, job locations, career gaps | They matter for the match. Listed as known proxies and measured in increment 2 |
| Test CVs | Claude drafts about 15 synthetic CVs with labelled answer keys; Panchali reviews them | Many name origins and tricky cases, with checked labels |
| Candidate mode | Unchanged; blind mode is recruiter-only | A candidate reviewing their own CV gains little from blinding |
| Data | Synthetic CVs only. Recruiter mode has no upload | The app is public; real candidates' data must not pass through it |

## User stories

### US1: Recruiter mode, clearly labelled
*As a visitor, I can switch FitProof to recruiter mode, so I can see how a recruiter-side screen could work, without mistaking it for a real hiring tool.*

Acceptance criteria:
- [ ] A mode switch offers "Candidate" and "Recruiter (demo)". Candidate mode is the default and works exactly as before.
- [ ] Recruiter mode shows a notice: demonstration only, synthetic CVs only, not legal advice, not for real hiring decisions.
- [ ] Recruiter mode has **no CV upload**. The recruiter picks from the preloaded synthetic CVs.
- [ ] The JD can be pasted, uploaded or picked from the sample JD.

### US2: Blind view of the CV
*As a recruiter, I see the CV with direct identifiers replaced by labelled placeholders, so I can judge the candidate on their experience.*

Acceptance criteria:
- [ ] Each redacted item is replaced by a placeholder naming its type, for example `[NAME]`, `[EMAIL]`, `[PHONE]`, `[ADDRESS]`, `[DATE_OF_BIRTH]`, `[NATIONALITY]`, `[MARITAL_STATUS]`, `[GENDER_MARKER]`, `[URL]`.
- [ ] Gendered titles (Mr, Mrs, Ms, Miss) and gendered pronouns (he, she, him, her, his, hers) are replaced, using custom rules alongside Presidio.
- [ ] The original and blind versions are shown side by side, with a count of items removed by type. (Showing the original is acceptable only because every CV is synthetic.)
- [ ] Proxies listed in the decisions table are **not** redacted, and the screen says so: "Blinding removes direct identifiers. It doesn't remove bias: university, employers and dates stay visible."

### US3: Match on the blind CV only
*As a recruiter, I get the usual FitProof analysis based only on the blind CV, so the model never sees the identifiers.*

Acceptance criteria:
- [ ] The text sent to Bedrock is the redacted text. A test checks that no labelled PII item from the answer key appears in what is sent.
- [ ] The evidence check and the rewrite check compare Claude's quotes against the **redacted** CV, not the original.
- [ ] The result screen shows "Blind screening: on".
- [ ] The same 3-per-visit limit applies. The sample-style saved result can be used for the screen recording.

### US4: Catch-rate eval
*As the builder, I can run one command that measures how much PII the redaction catches, so I can report the result honestly.*

Acceptance criteria:
- [ ] One command runs redaction on every synthetic CV and compares the result with its answer key.
- [ ] Output: overall catch rate; catch rate per PII type; catch rate for names by region of origin; a list of every miss; and the number of over-redactions (text removed that wasn't PII, such as a skill or employer).
- [ ] Results are saved to `docs/recruiter_mode/increment_1_results.md` and summarised in the build log.
- [ ] A name counts as caught only if the whole name is removed. A partly removed name counts as a miss.

### US5: Time and cost tracking
*As the builder, I record build time, build cost and run cost per use, so the LinkedIn post can report real numbers.*

Acceptance criteria:
- [ ] The build log has a tracker row for increment 1, with start time, finish time and active hours.
- [ ] Build cost covers Bedrock spend during the build and any paid tools. Presidio, spaCy and Streamlit Cloud are free.
- [ ] Run cost per use is measured from the token counts of one blind analysis.

## Non-functional requirements
- Redaction runs inside the app before any network call, with no extra cloud service.
- The language model loads once per app start (cached), and redaction of one CV takes under 3 seconds.
- The app still fits in Streamlit Community Cloud's free memory. **Test this first**: the large spaCy model is several hundred MB. Fallback: the medium model, with the catch-rate difference reported.

## Assumptions
- Synthetic CVs are plain text, in English.
- Presidio with spaCy `en_core_web_lg` is accurate enough to be worth reporting. An early probe on 12 CV headers caught 12/12 full names with the large model and 10/12 with the small model; the small model missed an Indian and a South African name.
- Placeholders don't noticeably change the match score. This is checked by scoring a few CVs with blind mode on and off.

## Resolved questions (13 October 2026)
| Question | Decision |
| --- | --- |
| How are gendered pronouns replaced? | With `[GENDER_MARKER]`, never "they": always grammatical-safe and obvious what was removed |
| Is a city in a job entry an address? | No. Only home addresses are redacted; job locations are proxies |
| Compare blind and non-blind scores? | Yes, for 3 CVs in this increment; all CVs in increment 2 |
| What if the large spaCy model doesn't fit on Streamlit Cloud? | The live demo uses the medium model; results for both are reported |
| Database for increment 3 | SQLite: free, no account, nothing to pause. The log resets when the app restarts, which the screen will say |
| Langfuse | Optional, added in increment 3 only if time allows |

## Out of scope for increment 1
Ranking several CVs, bias tests, the decision step, the audit log and the model card (increments 2 to 4).


## Known gaps (decided 13 October 2026)

- Family status ("2 children", "Dependants") and a "Religion:" line aren't redacted. Both are protected grounds under Ireland's Employment Equality Acts, but rare on the CVs this demo targets; they appear mainly in traditional personal-details blocks (some Indian, Gulf and older German formats).
- Indirect mentions (a religious society, union role, health-related career break, LGBTQ+ network) are kept on purpose: removing them would also remove real evidence. Their effect on the score is for increment 2.
- The requirement list is fixed per app start, not yet saved and approved by a person (increment 3).
