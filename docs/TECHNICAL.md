# Technical Design Document (TDD)
## JD Analyzer & CV Matcher

**Document Version:** 1.0  
**Last Updated:** October 2026  
**Status:** MVP Technical Blueprint

---

## 1. Objective

Build a lightweight web app that allows a user to:
- Paste a job description (JD) or upload a JD file
- Upload their CV in PDF or TXT format
- Extract relevant skills and compare them
- Display a match score and missing skills
- Offer a clear, beginner-friendly output for job tailoring

This will be built as an MVP in Python using Streamlit, with a simple keyword-based matching engine first. We will upgrade to smarter AI-based extraction later if needed.

---

## 2. Product Scope (MVP)

### In Scope
- JD input via text paste
- JD upload via PDF/TXT
- CV upload via PDF/TXT
- Text extraction from PDF using `pypdf`
- Skill extraction from text
- Match percentage calculation
- Matched skills list
- Missing skills list
- Basic UI with good readability

### Out of Scope for MVP
- User login / session management
- Database persistence
- Recruiter dashboard
- Multi-user system
- AI-generated cover letters
- Multi-language processing
- Advanced recommendation engine
- Real-time LLM-based extraction

---

## 3. Target Environment

The project is currently being built in **GitHub Codespaces** using:
- Python 3.11
- Streamlit
- pypdf
- python-dotenv
- optional Hugging Face models later

This environment is suitable for MVP development and is the fastest path to a working prototype.

---

## 4. High-Level Architecture

### Layer 1: User Interface
Responsible for:
- Displaying the sidebar with JD and CV inputs
- Accepting paste or upload actions
- Showing results in a clean layout

Technology:
- Streamlit

### Layer 2: Input Handling
Responsible for:
- Reading JD text from pasted input
- Reading JD from PDF or TXT upload
- Reading CV from PDF or TXT upload
- Validating if required inputs are present

Technology:
- Python
- `pypdf` for PDF parsing

### Layer 3: Text Processing
Responsible for:
- Normalizing text (lowercase, punctuation cleanup)
- Extracting candidate skills from user text
- Comparing against a skill dictionary

Technology:
- Python string processing
- Skill dictionary (list of keywords)

### Layer 4: Matching Engine
Responsible for:
- Comparing JD skill list with CV skill list
- Calculating match percentage
- Measuring overlap and gaps

Example logic:
- JD skills: [python, sql, aws, docker]
- CV skills: [python, sql, git]
- Matched = [python, sql]
- Missing = [aws, docker]
- Score = (2 / 4) * 100 = 50%

### Layer 5: Result View
Responsible for:
- Displaying the score
- Showing matched skills
- Showing missing skills
- Showing simple recommendation text

Technology:
- Streamlit components

---

## 5. Tech Stack

### Python
Why:
- Easy to write and read
- Great for text processing and analysis
- Good ecosystem for web app prototyping

### Streamlit
Why:
- Fastest way to build UI without frontend complexity
- Works well for small apps and data tools
- Great for MVP demonstration

### pypdf
Why:
- Extracts text from PDF files reliably enough for MVP
- Very lightweight and easy to install
- Good fit for CV and JD parsing

### python-dotenv
Why:
- Helps load environment variables safely
- Useful for future Hugging Face or API keys

### Optional Future Tools
- **Hugging Face Transformers / sentence-transformers**
  - For AI-based skill extraction
  - Better synonym handling
  - Better semantic matching
- **Pandas**
  - For processing structured comparison output
- **scikit-learn**
  - For vector similarity or simple classification later

---

## 6. Application Components

### 6.1 `app.py`
Main script for the app.

Responsibilities:
- Initialize Streamlit app
- Show sidebar and result layout
- Accept user input
- Read PDF/TXT text
- Run keyword matching logic
- Display results

### 6.2 `requirements.txt`
List of Python dependencies required for the app.

Contains:
- streamlit
- python-dotenv
- pypdf
- optionally future AI-related libraries

### 6.3 `docs/PRD.md`
The product-level definition.

Contains:
- Users and pain points
- MVP scope
- Success criteria
- Roadmap

### 6.4 `.venv/`
Isolated Python environment for project dependencies.

This prevents:
- Version conflicts between packages
- Overwriting global Python installs
- Cross-project dependency pollution

---

## 7. Data Flow

### Normal Flow
```
User inputs JD text OR uploads JD file
         ↓
App reads the text
         ↓
User uploads CV (PDF/TXT)
         ↓
App reads CV text
         ↓
Normalize text
         ↓
Extract skill keywords from JD and CV
         ↓
Compare sets of skills
         ↓
Calculate match score
         ↓
Display matched and missing skills
         ↓
Render result screen
```

### Example
```
JD text = "Python, SQL, AWS, Docker, FastAPI"
CV text = "Python, SQL, Git, Agile"

JD skills = {python, sql, aws, docker, fastapi}
CV skills = {python, sql, git, agile}

Matched = {python, sql}
Missing = {aws, docker, fastapi}
Score = 40%
```

---

## 8. Matching Strategy

### MVP Strategy: Keyword Matching
At this stage, no advanced AI is required.

The app will:
- convert text to lowercase
- remove punctuation
- compare using a defined skill dictionary
- look for skills in both JD and CV text
- count matches and missing skills

### Benefits
- Simple and reliable
- Fast to build
- Works well for a prototype
- Easy to explain to users

### Risks
- Misses synonyms
- Misses fuzzy matches
- Soft skills may be undercounted
- Could overvalue exact keyword presence

### Mitigation
- Expand skill dictionary
- Add synonyms manually
- Add phrase-based detection for common skills
- Later upgrade to LLM-based extraction

---

## 9. Skill Dictionary Design

The skill dictionary is a core component for MVP.

It will contain categories like:
- Programming languages
- Frameworks/libraries
- Cloud platforms
- Databases
- DevOps tools
- Soft skills
- Domain skills

Example:
```
{
  "python",
  "sql",
  "postgresql",
  "aws",
  "docker",
  "kubernetes",
  "fastapi",
  "django",
  "javascript",
  "react",
  "communication",
  "agile",
  "project management",
  "data analysis",
  "machine learning",
  "power bi"
}
```

### Future Improvement
Use a larger dictionary of 200-500 skills and add common synonyms.

---

## 10. PDF Handling

### PDF Input Flow
- User uploads PDF file
- File is passed to `pypdf`
- Extracted text is concatenated page by page
- The text is cleaned and normalized
- Matching engine works over clean text

### PDF Challenges
- Some PDFs may have scanned images rather than text
- Some files may contain messy formatting
- A PDF may have multiple columns or weird spacing
- OCR may be needed in the future for scanned documents

### MVP Approach
- Support common PDFs and TXT files
- Provide clear error messages when parsing fails
- Add fallback guidance for text-based content

---

## 11. Deployment Model

### Current Environment
The app runs inside GitHub Codespaces using a browser-based environment.

This works well for:
- local development
- demo testing
- quick iteration
- beta validation

### Future Deployment Options
- **Render** or **Railway** for simple deployment
- **Streamlit Community Cloud** for easy public hosting
- **Docker** if needed later
- **Azure App Service** if enterprise hosting is desired

### MVP Recommendation
Keep it simple: run it in Codespaces and later deploy on a low-cost hosting service.

---

## 12. Security Considerations

For MVP, this is a lightweight local app with no user authentication.

Current assumptions:
- No private credentials are stored in app code
- User-uploaded CVs are processed in session only
- No database or file persistence for MVP

### Future Improvements
- Add clear privacy policy
- Limit file size
- Remove uploaded files after processing
- Add secure storage if needed later

---

## 13. Risks and Technical Constraints

### Risk 1: Skill matching is too simplistic
**Problem:** Missing synonyms and variations can reduce match quality.

**Mitigation:**
- Expand skill dictionary
- Add common synonyms
- Upgrade to AI-based extraction later

### Risk 2: PDF parsing may fail for some files
**Problem:** Some PDFs do not extract cleanly.

**Mitigation:**
- Support TXT fallback
- Improve cleaning logic
- Add error messaging

### Risk 3: Output may feel too mechanical
**Problem:** Users may see exact keyword matches, but not the real job fit.

**Mitigation:**
- Add explanation text
- Improve suggestions with context
- Use AI later for better insights

### Risk 4: Dependency conflicts
**Problem:** Python package versions can conflict.

**Mitigation:**
- Use `.venv`
- Pin versions in `requirements.txt`
- Keep dependency list lean for MVP

---

## 14. Feasibility Check: Can We Build This Here?

### Yes — very feasible in the current environment.

Why:
- Python 3.11 is available in Codespaces
- Streamlit is easy to install and run
- `pypdf` works well for reading PDFs
- A simple keyword-matching app is easy to build and test
- We already have a working MVP flow with UI and text processing

### What this environment is best for
- MVP development
- UI iteration
- Proof of concept
- Testing user flow
- Demoing value to others

### What it is not best for yet
- Large-scale AI workloads
- Multi-user platform with DB
- Enterprise traffic or security requirements
- High-volume processing at scale

---

## 15. Recommended Next Technical Steps

### Step 1: Improve the matching engine
- Expand skill dictionary
- Add synonyms
- Show a clearer score breakdown

### Step 2: Improve output readability
- Display a cleaner “Matched Skills” box and “Missing Skills” box
- Add headings and icons
- Improve styling

### Step 3: Add suggestions engine
- If missing skill is "python", offer a suggestion such as:
  - "Add Python project experience to the CV"
  - "Highlight Python development experience"

### Step 4: Add better input validation
- If JD or CV is empty, show actionable error message
- If PDF read fails, show guidance

### Step 5: Optional AI Upgrade
- Add Hugging Face integration later for skill extraction
- Use a semantic model to improve match quality

---

## 16. Final Recommendation

The correct MVP architecture is:
- **Python + Streamlit** for the app
- **PyPDF** for PDF parsing
- **Simple keyword-based matching** for the first version
- **Skill dictionary** as the main matching method
- **Later AI upgrade** for improved relevance and analysis

This is the most practical and realistic setup for a project like this in a MVP phase.

---

## 17. Conclusion

This project is feasible, fast to build, and a strong portfolio piece. The current setup is enough to validate the concept, gather user feedback, and refine the matching logic before moving to more advanced AI or production-grade architecture.

This is the right phase to keep building because the product is simple, useful, and clearly solves a real pain point for job applicants.
