# Architecture Overview

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Your Computer                            │
│                                                              │
│  ┌────────────────┐  ┌─────────────┐  ┌────────────────┐     │
│  │   Dashboard    │  │  API Server │  │ Browser Worker │     │
│  │   (Frontend)   │  │  (FastAPI)  │  │  (Playwright)  │     │
│  └────────────────┘  └─────────────┘  └────────────────┘     │
│         │                    │                 │             │
│         └────────┬───────────┴─────────────────┘             │
│                  │                                           │
│         ┌────────▼───────────┐                               │
│         │   n8n Workflows    │                               │
│         │ (Orchestration)    │                               │
│         └────────┬───────────┘                               │
│                  │                                           │
│         ┌────────▼──────────────────┐                        │
│         │   PostgreSQL Database     │                        │
│         │ (Source of Truth)         │                        │
│         └────────────────────────────┘                       │
│                  │                                           │
└──────────────────┼───────────────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
   Gemini      Telegram      Career Pages
   API         Bot           & Job Boards
```

## Data Flow

### Job Collection Pipeline

```
Career Pages / Job Boards
         ↓
    n8n Workflows
         ↓
  HTTP Request / Extract
         ↓
   Normalize Data
         ↓
   PostgreSQL Jobs Table
```

### Job Matching Pipeline

```
Collected Jobs
         ↓
Preference Filtering (cheap)
         ↓
Gemini AI Analysis (expensive)
         ↓
Job Matches Table
         ↓
Telegram Notification
```

### Application Pipeline

```
User Approves Job Match
         ↓
API Creates Application
         ↓
Form Filling by Browser Worker
         ↓
Handle Unknown Fields (LLM)
         ↓
User Reviews & Approves Form
         ↓
Submit Application
         ↓
Track Application Status
```

## Component Responsibilities

### PostgreSQL
- **Responsibility**: Source of truth for all state
- **Stores**: Profiles, CVs, jobs, matches, applications, preferences, audit trail
- **Accessed by**: API, n8n, browser worker
- **Scale**: Single instance initially (can be replicated later)

### n8n
- **Responsibility**: Workflow orchestration
- **Does**: Coordinates job collection, filtering, matching, notifications, browser calls
- **Calls**: PostgreSQL, API, Gemini, Telegram, browser worker
- **Uses**: PostgreSQL for persistent workflow state
- **Never**: Makes direct decisions (LLM recommends, n8n executes based on DB state)

### API Server
- **Responsibility**: Business logic and data access
- **Does**: CRUD operations, validation, transformations
- **Serves**: n8n workflows, dashboard, browser worker
- **Uses**: PostgreSQL for persistence
- **Later**: Implements complex business rules

### Browser Worker
- **Responsibility**: Website interaction only
- **Does**: Fills forms, detects fields, uploads files
- **Does NOT**: Make decisions about what to fill
- **Receives**: Instructions from n8n with specific values to fill
- **Returns**: Screenshots, field detection, error status

### Dashboard
- **Responsibility**: User interface
- **Does**: Configuration, monitoring, manual approvals
- **Uses**: API server for data access
- **Triggers**: Approvals, rejections, modifications through API

### Gemini API
- **Responsibility**: AI analysis
- **Does**: Job matching, field type detection, conversational modification parsing
- **Called by**: n8n for job matching, browser worker for field detection
- **Returns**: Structured output (JSON, not free-form)

### Telegram Bot
- **Responsibility**: User notifications and approvals
- **Does**: Sends notifications, receives user responses
- **Triggers**: Application state changes based on user responses
- **Called by**: n8n workflows

## State Management

All state lives in PostgreSQL. The flow is:

```
n8n reads state from DB
     ↓
n8n executes business logic
     ↓
n8n updates state in DB
     ↓
Other services read new state
```

### Example: Application Approval

```
1. DB: application.status = 'AWAITING_APPROVAL'
2. n8n: Sends Telegram notification
3. User: Clicks "APPROVE" button
4. API: Updates application.status = 'APPROVED'
5. n8n: Detects status change, starts form filling
6. Browser: Fills form fields
7. DB: Updates application.status = 'FORM_FILLING'
8. API: Returns filled form for user review
9. DB: Updates application.status = 'WAITING_FOR_USER'
```

## Communication Patterns

### Synchronous (API Calls)
- Dashboard ↔ API
- n8n → API (for CRUD operations)
- n8n → Browser Worker (for form operations)
- API → Database

### Asynchronous (Message-based)
- n8n → Telegram (notifications, waits for response)
- n8n → Gemini (AI calls)

### Event-Driven (Database Polling)
- n8n polls database for new jobs, matches awaiting action
- Dashboard polls API for real-time status

## Error Handling & Recovery

### Playwright/Browser Failures
```
Browser error
     ↓
Take screenshot
     ↓
Log error details
     ↓
DB: application.status = 'NEEDS_MANUAL_INTERVENTION'
     ↓
Telegram: Notify user with screenshot
```

### API Failures
```
API call fails
     ↓
Retry (exponential backoff)
     ↓
Log error after max retries
     ↓
Telegram: Notify user
```

### Gemini Failures
```
LLM error
     ↓
Retry with same parameters
     ↓
Fall back to conservative scoring
     ↓
Flag for review
```

## Deployment Model

### Phase 1-3: Single Server
```
Host Machine
├── Docker Container: PostgreSQL
├── Docker Container: n8n
└── (Later) Docker Containers: API, Browser Worker, Dashboard
```

### Phase 20+: Distributed (Optional)
```
Cloud Infrastructure (VPS/Kubernetes)
├── PostgreSQL (managed or containerized)
├── n8n
├── API (replicated)
├── Browser Workers (multiple instances)
├── Dashboard (CDN + API)
├── Monitoring (Prometheus, Grafana)
└── Logging (ELK stack or similar)
```

## Scaling Considerations

### Database
- Indexes on frequently queried fields ✓
- JSONB for flexible schemas ✓
- Partitioning for large tables (future)

### n8n
- Horizontal scaling with multiple instances
- Job queue for reliable execution
- Webhook triggers vs polling

### Browser Workers
- Multiple instances for parallel form filling
- Session pooling for resource efficiency
- Connection limits to respect website rate limits

### API
- Stateless design for easy scaling
- Cache layer (Redis) for frequently accessed data
- Rate limiting per user/endpoint

## Security Principles

1. **Least Privilege**: Each service has minimal permissions
2. **Data at Rest**: PostgreSQL encryption (optional)
3. **Data in Transit**: HTTPS/TLS for all external communications
4. **Secrets Management**: .env files (not committed), environment variables
5. **Input Validation**: All inputs validated before DB/API calls
6. **Audit Trail**: All changes logged in audit_trail table
7. **User Control**: No automatic irreversible actions

## Key Design Principles

> **LLM interprets and reasons; n8n orchestrates; PostgreSQL stores state; Playwright interacts with websites; the user controls irreversible actions.**

1. **LLM ≠ Decision Maker**: LLM provides recommendations; human or predetermined logic decides
2. **Deterministic Before AI**: Use cheap filters first, only call Gemini for filtered results
3. **State is Sacred**: All state in PostgreSQL, never in variables or memory
4. **Approval is Checkpoint**: Any irreversible action requires user approval
5. **Modification Revokes Approval**: Changing approved application revokes approval
6. **Separation of Concerns**: Each service has one responsibility
7. **Logging Everything**: For debugging and audit trails
