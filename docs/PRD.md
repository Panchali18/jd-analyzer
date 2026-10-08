# Product Requirements Document (PRD)
## JD Analyzer & CV Matcher

**Document Version:** 1.0  
**Last Updated:** October 2026  
**Status:** MVP Definition

---

## 1. Problem Statement

### The Challenge
Job applicants across all experience levels waste significant time:
- Manually reviewing job descriptions to identify required skills
- Comparing their CV against job requirements
- Identifying skill gaps and what to highlight
- Tailoring their CV for each application
- Deciding which projects/experiences to emphasize

This is a **universal problem** — whether you're a fresh graduate or a 20-year veteran, tailoring CVs for each role is tedious and time-consuming.

### Why This Matters
- **Time Savings:** Most job seekers apply to 5-15 roles/week. Tailoring takes 15-30 mins per application = 2-8 hours/week wasted
- **Better Results:** Tailored CVs increase interview chances by 40-60%
- **Confidence:** Applicants feel uncertain about what skills to emphasize
- **Accessibility:** Not everyone has time to manually compare skills

---

## 2. Target Audience

### Primary Users: All Job Applicants

**Who:**
- Entry-level graduates
- Mid-career professionals
- Career switchers
- Senior professionals
- Freelancers looking for full-time roles
- Anyone actively job hunting

**By Job Role (Examples):**
- Software Engineers
- Data Analysts
- Product Managers
- Business Analysts
- Marketing Professionals
- Project Managers
- Sales Professionals
- UX/UI Designers
- Operations Specialists
- Finance Professionals

**By Experience Level:**
- 0 years (fresh graduates)
- 1-3 years (junior)
- 3-7 years (mid-level)
- 7-15 years (senior)
- 15+ years (expert/director)

**Geography:**
- Global (LinkedIn users, job boards)
- English-speaking priority for MVP

**Frequency:**
- Light users: 1-2 applications/week (5-10 applications/month)
- Medium users: 3-7 applications/week (12-30 applications/month)
- Heavy users: 8-15+ applications/week (30+ applications/month)

### Common Pain Points (All Levels)
- "I don't know which skills to highlight for this role"
- "My CV doesn't look like a good fit, but I have relevant experience"
- "I'm applying to too many jobs to tailor each one"
- "I don't know what skills I'm missing"
- "Should I emphasize my technical skills or my leadership experience?"

### Why They Use It
- Save time on job applications
- Increase interview chances
- Gain confidence in tailoring
- Identify learning gaps
- Get objective feedback on fit

---

## 3. Goals & Success Metrics

### User Goals
- ✅ Quickly identify which skills they have vs. job requires (< 2 minutes)
- ✅ Get suggestions on how to tailor their CV for each role
- ✅ Understand their match score for a role
- ✅ Identify skill gaps to focus on learning
- ✅ Save time on job application process

### Business Goals (Portfolio Project)
- ✅ Build an MVP that demonstrates core value
- ✅ Create a portfolio project showing full product thinking
- ✅ Get 10-20 beta testers to validate across different experience levels
- ✅ Build foundation for future monetization (optional premium features)

### Success Metrics (MVP)
- Match score accuracy: 75%+ correctness on test cases (across all experience levels)
- User can paste JD and upload CV in <2 minutes
- Analysis completes in <5 seconds
- User can identify 5+ missing skills in results
- UI works for all experience levels (clear for juniors, valuable for seniors)

---

## 4. MVP Features

### Phase 1: MVP (Current Target)

#### 4.1 Core Features

**Feature 1: JD Input Flexibility**
- User can paste JD text from LinkedIn, job boards, emails directly
- User can upload JD as PDF or TXT file
- Support both methods (paste OR upload)
- Works with various JD formats (structured, unstructured)

**Feature 2: CV Upload**
- Upload CV as PDF or TXT
- Extract text automatically
- Support multi-page PDFs
- Clear error messages if upload fails

**Feature 3: Skill Matching & Analysis**
- Extract skills from JD (what's required)
- Extract skills from CV (what you have)
- Calculate match percentage (0-100%)
- Display results clearly:
  - **Matched Skills:** Skills you have that are required
  - **Missing Skills:** Skills required but not in your CV
  - **Match Score:** Overall percentage match

**Feature 4: Actionable Insights**
- Display top missing skills with priority
- Simple tailoring suggestions (e.g., "Add Python project to CV", "Emphasize your leadership experience")
- Show soft skills vs technical skills
- Brief explanation of score

**Feature 5: Clean, Simple UI**
- Sidebar for inputs (paste/upload JD, upload CV)
- Main panel for results and analysis
- Clear visual hierarchy (score prominent, then skills)
- Mobile-friendly (but desktop-first for MVP)
- Works on any device

#### 4.2 Out of Scope (Phase 2+)
- Real-time AI skill extraction with LLMs
- Auto-generated cover letters
- Interview prep questions
- Job recommendations
- Multi-language support
- User accounts & authentication
- Save/compare multiple JDs
- Learning resource recommendations
- Resume builder
- ATS compatibility checker

---

## 5. User Personas

### Persona 1: Priya (Fresh Graduate)
- **Age:** 22 years old
- **Experience:** 0 years (just graduated)
- **Background:** Computer Science degree
- **Situation:** First job hunt, unsure how to present academic projects vs real skills
- **Pain:** "I'm qualified but my CV doesn't show it clearly. I don't know what skills companies want"
- **Usage:** 3-5 applications/week, ~10 minutes per application
- **Goal:** "Help me show companies I can do the job despite having no work experience"
- **Success:** "I got an interview because I matched my academic projects to the job requirements"

### Persona 2: Marcus (Mid-Career Professional)
- **Age:** 31 years old
- **Experience:** 6 years as a Product Manager
- **Situation:** Comfortable but looking for growth, applying to different companies
- **Pain:** "Each company wants different things. I have 6 years of experience but I don't know what to highlight for each role"
- **Usage:** 2-3 applications/week, ~5 minutes per application
- **Goal:** "Tell me exactly what to emphasize in my CV for each role"
- **Success:** "I identified that I need to highlight my data analysis skills more, and it helped me land interviews"

### Persona 3: Rajesh (Career Switcher)
- **Age:** 28 years old
- **Experience:** 5 years in consulting, switching to tech
- **Situation:** Has transferable skills but worried they won't be recognized
- **Pain:** "I have relevant skills but they're called different names in my background"
- **Usage:** 4-6 applications/week, ~15 minutes per application (longer search)
- **Goal:** "Show me how my consulting background matches tech roles"
- **Success:** "I realized my project management experience is valuable for Product Manager roles. This helped me reframe my CV"

### Persona 4: Aisha (Senior Professional)
- **Age:** 40 years old
- **Experience:** 15+ years as Software Engineer, now leadership-focused
- **Situation:** Looking for senior/director roles, competitive market
- **Pain:** "I have deep expertise but too much experience. I'm not sure what to highlight"
- **Usage:** 1-2 applications/week (selective search), ~20 minutes per application
- **Goal:** "Help me see which of my skills are most relevant vs. outdated"
- **Success:** "Identified that companies want cloud expertise more than older technologies. Helped me update my CV"

---

## 6. MVP User Flow

### Happy Path
```
1. User lands on app
   ↓
2. Chooses: Paste JD OR Upload JD file
   ↓
3. Provides JD (from LinkedIn/email/job board)
   ↓
4. Uploads CV (PDF or TXT)
   ↓
5. App analyzes and shows:
   - Match Score (big number, clear)
   - ✅ Matched Skills (things you have)
   - ❌ Missing Skills (things you need)
   - 💡 Suggestions (how to tailor)
   ↓
6. User reads insights and tailors CV
   ↓
7. User applies for job with confidence
```

### Error Cases Handled
- User pastes empty JD → "Please enter a job description"
- User uploads CV that can't be read → "Please try a different file format"
- No skills detected → "No skills detected. Please check your CV format"
- Perfect match → "Great match! This role suits your profile"

---

## 7. Success Criteria (MVP Completion)

**Functionality:**
- ✅ User can paste JD and see it accepted
- ✅ User can upload CV (PDF/TXT) and see it processed
- ✅ Match score calculated (0-100%) based on skill comparison
- ✅ At least 5-10 matched skills displayed with checkmark
- ✅ At least 3-5 missing skills displayed clearly
- ✅ Simple tailoring suggestions provided
- ✅ No crashes on reasonable input

**User Experience:**
- ✅ UI is clean and professional
- ✅ Results are easy to understand for all experience levels
- ✅ Process takes < 2 minutes from start to results
- ✅ Mobile-friendly layout

**Quality:**
- ✅ Works on sample JDs from LinkedIn, job boards, emails
- ✅ Supports common CV formats (standard PDFs, TXT)
- ✅ Skill matching is reasonably accurate (80%+ correct on test cases)
- ✅ No sensitive data stored locally

---

## 8. Skill Categories for MVP

### Technical Skills (Examples)
- Programming: Python, JavaScript, Java, C++, Ruby, Go, Rust, PHP, C#
- Web: React, Vue, Angular, Node.js, Django, Flask, FastAPI
- Data: SQL, PostgreSQL, MySQL, Spark, Pandas, NumPy, Tableau, Power BI
- Cloud: AWS, GCP, Azure, Docker, Kubernetes
- DevOps: CI/CD, Git, Jenkins, GitHub Actions, Terraform
- ML/AI: Machine Learning, Deep Learning, TensorFlow, PyTorch, NLP

### Soft Skills (Examples)
- Communication, Leadership, Problem Solving, Team Collaboration
- Project Management, Agile, Scrum, Stakeholder Management
- Business Analysis, Data Analysis, Critical Thinking
- Presentation, Negotiation, Time Management

### Domain Skills (Examples)
- Product Management, Business Analysis, Finance, Marketing, Sales
- Healthcare, E-commerce, FinTech, EdTech, SaaS

---

## 9. Future Features (Phase 2+)

### Phase 2: Smarter Matching
- AI-powered skill extraction (using open-source LLMs)
- Synonym detection (e.g., "Python" = "Py", "communication" = "presentation skills")
- Skill level detection (junior, mid, senior requirements)
- Required vs optional skill classification
- Soft skill matching

### Phase 3: Enhanced Recommendations
- CV tailoring suggestions (specific, actionable)
- Learning gap recommendations (what to learn first)
- Similar roles you might qualify for
- Salary range insights

### Phase 4: Comparison & History
- Compare multiple JD comparisons
- Track which roles you applied for
- See trends (most common missing skills)
- Export results as PDF

### Phase 5: Monetization (Optional)
- Premium: AI-powered resume rewriting
- Premium: Mock interview based on job description
- Premium: Unlimited comparisons (if needed)
- Premium: Career coach access

---

## 10. Competitive Landscape

### Existing Solutions
- **Jobscan** - ATS scanner, expensive ($8.33-15/month per month), corporate-focused
- **Talentdesk** - Limited free tier, complex UI
- **JDIS** - Outdated, not actively maintained
- **LinkedIn Job Match** - Basic matching, not detailed analysis
- **Rezi** - Resume builder, not JD matching

### Our Advantage
- ✅ Free for all job applicants
- ✅ Quick & simple (no sign-up required for MVP)
- ✅ Both paste & upload options (flexible)
- ✅ Actionable suggestions (not just "match" numbers)
- ✅ Works for any experience level (juniors to seniors)
- ✅ Open-source friendly

---

## 11. Assumptions & Risks

### Assumptions
1. Users have digital copies of JDs (true - mostly LinkedIn)
2. CVs in PDF/TXT format are sufficient (true for most roles)
3. Keyword-based matching is good enough for MVP (reasonable for v1)
4. Users want quick results over perfect accuracy (yes for MVP)
5. Problem exists for all experience levels (validated through personas)

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Skill matching accuracy (synonyms missed) | Low match scores discouraging users | Start with common 200 skills, expand to 500+. Plan AI upgrade for Phase 2 |
| PDF extraction issues | User frustration with PDFs | Support TXT fallback, clear error messages, guide users |
| Outdated skill dictionary | Misses modern skills | Quarterly updates, collect user feedback, community contributions |
| Low scores for switchers | Career changers feel discouraged | Show "transferable skills" messaging, soft skills matching |
| No differentiation vs competitors | Users prefer established tools | Focus on simplicity, no sign-up, better UX for all levels |

---

## 12. Timeline & Milestones

### MVP Phase (This Month - Weeks 1-4)
- **Week 1-2:** ✅ PRD & Technical Design (CURRENT)
- **Week 2-3:** Core matching logic, skill dictionary, UI improvements
- **Week 3-4:** Testing with 5-10 users, refinement
- **Week 4:** Launch for feedback

### Phase 2 (Next Month - Weeks 5-8)
- AI-powered skill extraction
- Enhanced skill matching (synonyms, levels)
- Improved UI and results display
- User feedback integration

### Phase 3 (Month 3 - Weeks 9-12)
- CV tailoring suggestions
- Learning gap recommendations
- Public launch & marketing

---

## 13. Questions to Validate with Users

Before full launch, validate with target users:
1. Is keyword-based matching good enough? (Test on 10 real JDs across roles)
2. What experience levels care most about this? (Interview 3-5 from each level)
3. Which skills should we prioritize in dictionary? (Feedback from beta users)
4. Do users want suggestions outside skills? (Formatting, achievements, etc.)
5. Would users pay for premium features? (Survey 20-30 people)

---

## 14. Success Stories (Future - How Users Will Talk About It)

- **Priya:** "I used this tool to match my projects to the job description, got an interview, and landed my first job"
- **Marcus:** "Saved me 5 minutes per application × 30 applications = 2.5 hours saved per month. Worth it!"
- **Rajesh:** "Helped me see how my consulting background maps to tech. Changed how I present myself"
- **Aisha:** "Identified that my old skills were hurting me. Helped me focus on modern tech"

---

**Next Step:**
1. ✅ PRD Finalized
2. ⬜ Create Technical Design Document (Next)
3. ⬜ Expand skill dictionary with 200+ skills
4. ⬜ Implement MVP features
5. ⬜ Get user feedback from 10 beta testers
