# Personal AI-assisted job application automation system 

## 📊 Project Status

| Phase | Name | Status |
|-------|------|--------|
| 0 | Define MVP | ✅ Complete |
| 1 | Project Structure | ✅ Complete |
| 2 | Docker Environment | ✅ Complete |
| 3 | PostgreSQL Database | ✅ Complete |
| 4 | Profile & CV Management API | ✅ Complete |
| 5 | Job Source System | ⏳ Pending |
| 6 | Career Page Collector | ⏳ Pending |
| 7 | Bdjobs Collector | ⏳ Pending |
| 8-13 | Additional Phases | ⏳ Pending |
| 14 | Full Integration & Testing | ⏳ Pending |

### Phase 4 Deliverables

✅ FastAPI REST API (main.py, routes.py)
✅ SQLAlchemy ORM models for Profile, CV, UserPreference
✅ Pydantic request/response validation schemas
✅ Business logic services (ProfileService, CVService, UserPreferenceService)
✅ File upload handling for CVs (PDF, DOC, DOCX)
✅ Database connection pooling and session management
✅ Configuration management via environment variables
✅ Docker containerization (Dockerfile)
✅ Docker Compose integration with PostgreSQL
✅ API documentation and examples
✅ Test suite for all endpoints

**Running Phase 4:**
```bash
docker compose up api
# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

---

# Project Goal

The system should continuously find relevant jobs from **company career pages and Bdjobs**, evaluate them against your profile and preferences, select the most appropriate CV, and prepare applications.

The system should **never submit an application without your explicit approval**.

The core flow is:

```text
Job Sources
    ↓
Collect Jobs
    ↓
Normalize + Deduplicate
    ↓
Filter by Preferences
    ↓
AI Job Matching
    ↓
Select Appropriate CV
    ↓
Notify User
    ↓
User Approves / Rejects / Modifies
    ↓
Playwright Browser Automation
    ↓
Fill Application Form
    ↓
Handle Unknown Fields with LLM
    ↓
User Final Approval
    ↓
Submit Application
    ↓
Track Application
```

### Main design principle

> **LLM interprets and reasons; n8n orchestrates; PostgreSQL stores state; Playwright interacts with websites; the user controls irreversible actions.**

---

# Roadmap

## Phase 0 — Define the MVP

This is what V1 supports.

### Job sources

Start with:

* 2-3 company career pages
* Bdjobs
* Possibly from email-based job alerts (possibly linkedin) later

Don't try to support every career website initially.

### User features

Your MVP should support:

* Profile and Job preferences
* Multiple CVs
* Career-page URLs
* Bdjobs filters
* Job listing
* AI match score
* CV recommendation
* Application approval/rejection
* Application modification
* Application tracking
* Telegram notifications

### Explicitly postpone

Don't build these initially:

* LinkedIn automation
* WhatsApp
* Multiple users
* Complex conversational agent
* Local LLM
* Automatic CV rewriting
* Large-scale scraping
* Complex analytics

---

# Phase 1 — Architecture & Repository

Create a project structure such as:

```text
job-agent/
│
├── n8n/
├── api/
├── browser-worker/
├── database/
├── cv-storage/
├── dashboard/
├── docker-compose.yml
└── README.md
```

You don't need to implement everything immediately.

The components are:

```text
n8n             → orchestration
PostgreSQL      → persistent state
API             → application interface
Browser Worker  → Playwright
Gemini          → AI
Telegram        → notification/approval
Dashboard       → configuration + monitoring
```

---

# Phase 2 — Docker Environment

Use Docker Compose so the whole system can eventually be started with:

```text
docker compose up
```

Initially run:

```text
PostgreSQL
n8n
```

Later add:

```text
API
Browser Worker
Dashboard
```

This also makes the project much easier to move to a VPS later.

---

# Phase 3 — PostgreSQL Database

Make PostgreSQL your **source of truth**.

Start with these tables:

```text

profile
skills
cvs
companies
job_sources
jobs
job_matches
applications
application_fields
notifications
```

You can simplify this further for V1.

For example:

```text
companies
    ↓
job_sources
    ↓
jobs
    ↓
job_matches
    ↓
applications
```

And:

```text
profiles
    ↓
cvs
```

Use PostgreSQL `JSONB` for unpredictable application-form information.

For example:

```text
application_fields

{
    "question": "Are you willing to relocate?",
    "field_type": "boolean",
    "answer": true
}
```

This gives you MongoDB-like flexibility while keeping your relational structure.

---

# Phase 4 — Profile & CV Management

Create your basic profile:

```text
Name
Email
Phone
Location
Education
Experience
Skills
Portfolio
GitHub
LinkedIn
Salary expectation
```

Then implement multiple CVs:

```text
DevOps CV
ML CV
Backend CV
General CV
```

Each CV should have metadata:

```text
filename
category
target_roles
skills
active
```

Example:

```text
ML_CV.pdf

category:
ML/AI

target roles:
ML Engineer
AI Engineer
GenAI Engineer
```

Initially, simply upload/store PDFs. Don't generate customized CVs yet.

---

# Phase 5 — Job Source System

Create a generic job-source abstraction.

Something conceptually like:

```text
JobSource
   │
   ├── CareerPageSource
   ├── BdjobsSource (later)
   └── EmailSource (later)
```

Every source should eventually produce the same normalized structure (you can add more if seems important):

```json
{
  "title": "...",
  "company": "...",
  "location": "...",
  "description": "...",
  "url": "...",
  "source": "...",
  "posted_at": "..."
}
```

This is important because the AI shouldn't care whether a job came from Bdjobs or a company's website.

---

# Phase 6 — Career Page Collector

Start with one company.

Build:

```text
n8n
 ↓
HTTP request
 ↓
HTML extraction
 ↓
Normalize job
 ↓
PostgreSQL
```

Then add another company.

You'll discover that career websites have different structures.

So eventually your collector should support different extraction strategies:

```text
HTML
JSON
RSS
API
Sitemap
```

For complicated JavaScript-rendered sites, you can use Playwright later.

---

# Phase 7 — Bdjobs Collector (later)

Implement your Bdjobs source according to whatever access method you're using and what its current terms permit.

Convert results into the same normalized job structure.

Then your database doesn't care whether:

```text
job.source = "bdjobs"
```

or:

```text
job.source = "company_career_page"
```

---

# Phase 8 — Deduplication

This is important.

The same job could appear:

```text
Bdjobs
Company website
Email alert
```

Create a deduplication strategy using combinations such as:

```text
company
title
location
application URL
```

You might generate a normalized hash:

```text
hash(company + title + url)
```

and put a unique constraint around it.

---

# Phase 9 — Preference Filtering

Before using an LLM, perform cheap deterministic filtering.

Example:

```text
Location
Experience
Job type
Keywords
Salary
Remote
```

Pipeline:

```text
1000 jobs
   ↓
Basic filtering
   ↓
250 jobs
   ↓
AI analysis
```

This saves API cost.

Your preferences should live in PostgreSQL and be modified from the dashboard, **not through the conversational LLM**.

---

# Phase 10 — Gemini Job Matching

Now introduce Gemini.

Give it:

```text
User profile
+
Job description
+
User preferences
```

Ask for structured output like:

```json
{
  "match_score": 91,
  "recommendation": "APPLY",
  "matched_skills": [],
  "missing_skills": [],
  "experience_match": true,
  "reason": "..."
}
```

Use structured output/schema validation rather than relying on free-form text.

---

# Phase 11 — CV Selection

Give Gemini your available CV metadata:

```text
DevOps CV → AWS, Docker, Terraform
ML CV → PyTorch, TensorFlow, LLM
Backend CV → FastAPI, Node.js
```

Then:

```text
Job
 ↓
AI matching
 ↓
Recommended CV
```

Store the decision:

```text
job_match.selected_cv_id
```

Don't let the browser worker decide this.

---

# Phase 12 — Telegram Notification

When a sufficiently good job appears:

```text
n8n
 ↓
Telegram
```

Send:

```text
🔥 New job match

ML Engineer
ABC Ltd

Match: 92%

Recommended CV:
ML Engineer CV

Matched:
✓ Python
✓ PyTorch
✓ FastAPI
✓ LLM

Missing:
✗ Kubernetes

[VIEW]
[APPROVE]
[REJECT]
[MODIFY]
```

---

# Phase 13 — Approval State Machine

Implement application states.

For example:

```text
DISCOVERED
    ↓
MATCHED
    ↓
SHORTLISTED
    ↓
AWAITING_APPROVAL
    ↓
APPROVED
    ↓
PREPARING_APPLICATION
    ↓
FORM_FILLING
    ↓
WAITING_FOR_USER
    ↓
READY_TO_SUBMIT
    ↓
SUBMITTED
```

Also:

```text
REJECTED
FAILED
NEEDS_MANUAL_INTERVENTION
```

This state machine is one of the most important parts of the system.

---

# Phase 14 — Browser Worker

Now build your Playwright service.

Its responsibility should be **only browser interaction**.

For example:

```text
POST /application/start

POST /application/fill

POST /application/answer

POST /application/submit

POST /application/stop
```

n8n calls it.

Example:

```text
n8n
 ↓
POST /application/start
 ↓
Playwright
 ↓
Open application URL
```

Keep Playwright completely separate from your AI/job-processing logic.

---

# Phase 15 — Automatic Form Filling

Start with simple fields (you can create a simple google form or 1 page webpage to test):

```text
Name
Email
Phone
Address
LinkedIn
GitHub
Portfolio
CV
```

Map:

```text
profile.email
     ↓
<input type="email">
```

and:

```text
cv.file
     ↓
<input type="file">
```

Don't attempt intelligent field detection immediately.

Get deterministic fields working first.

---

# Phase 16 — Unknown Form Fields + LLM

Now implement the interesting part.

Playwright encounters:

```text
<label>
What is your current annual compensation?
</label>
```

Your system sends the label/context to Gemini.

Gemini returns:

```json
{
  "field_type": "current_salary",
  "confidence": 0.94
}
```

Then your system maps:

```text
current_salary
      ↓
profile.current_salary
```

For uncertain fields:

```text
confidence < threshold
      ↓
STOP
      ↓
Telegram
      ↓
Ask user
```

Never allow low-confidence AI guesses to silently become application answers.

---

# Phase 17 — Conversational Modification

Now add the feature we discussed.

You receive:

> "Use the backend CV instead and set expected salary to 70k."

Gemini converts it to:

```json
{
  "intent": "modify_application",
  "application_id": "APP-123",
  "changes": {
    "cv": "backend_cv",
    "expected_salary": 70000
  },
  "requires_reapproval": true
}
```

n8n validates it and updates PostgreSQL.

The LLM **doesn't directly execute anything**.

---

# Phase 18 — Final Submission Safety

Make this a hard rule:

```text
Application cannot reach SUBMITTED
unless
explicit_user_approval = true
```

And if anything changes after approval:

```text
Modification
    ↓
approval invalidated
    ↓
AWAITING_APPROVAL
```

So:

```text
Approve
 ↓
Change CV
 ↓
Approval revoked
 ↓
Ask again
```

This is a very good safety mechanism.

---

# Phase 19 — Application Tracking

After successful submission:

```text
company
position
url
cv_used
date_applied
status
```

Status:

```text
APPLIED
REJECTED
INTERVIEW
TECHNICAL_INTERVIEW
OFFER
WITHDRAWN
```

You can manually update these from the dashboard.

---

# Phase 20 — Build the Dashboard

Only **after the automation works**.

The dashboard should initially provide:

### Dashboard

```text
Jobs found
Shortlisted
Awaiting approval
Applied
Interviews
```

### Preferences

```text
Roles
Locations
Experience
Salary
Remote
Minimum match score
```

### Companies

```text
Company
Career URL
Enabled/disabled
```

### CVs

```text
Upload
Category
Skills
Active/inactive
```

### Jobs

```text
Job
Company
Match
Source
Status
```

### Applications

```text
Company
Position
CV
Applied date
Status
```

You can use whatever frontend technology you like—or even a very simple server-rendered UI. **React/Next.js is not an architectural requirement.**

---

# Phase 21 — Reliability

Before calling it "complete", add:

* retries
* timeout handling
* duplicate prevention
* browser crash recovery
* LLM failure handling
* API rate-limit handling
* structured logging
* screenshots when Playwright fails
* application state recovery
* notification failure handling

For example:

```text
Playwright fails
     ↓
Screenshot
     ↓
Save error
     ↓
DB = NEEDS_MANUAL_INTERVENTION
     ↓
Telegram notification
```

---

# Phase 22 — Optional Improvements

Only after the MVP works:

```text
Multiple LLM providers
Local small LLM
CV tailoring
Cover-letter generation
Email job sources
More career sites
Better browser field detection
Application analytics
Prometheus/Grafana
Cloud/VPS deployment
Multi-user support
```

### One thing I would deliberately postpone

**Multi-user support.**

Build it as a personal system first. If you later want other people to use it, then introduce:

```text
authentication
users
per-user profiles
per-user CVs
per-user API keys
per-user preferences
```

That is a significantly different security problem.

---

## Final MVP stack

I'd keep the first serious version around:

```text
┌──────────────────────────────────────────┐
│              YOUR COMPUTER               │
│                                          │
│  PostgreSQL                              │
│  n8n                                     │
│  Small API                               │
│  Playwright Worker                       │
│  CV Storage                              │
│                                          │
└──────────────────────────────────────────┘
             │
             ├──── Gemini API
             │
             └──── Telegram
```

And the core development order should be:

**Database → n8n → Job collection → Filtering → Gemini matching → CV selection → Telegram → Playwright → Form filling → Unknown-field handling → Approval → Submission → Tracking → Dashboard → Reliability.**


