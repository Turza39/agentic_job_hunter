# n8n Workflows

This directory contains the orchestration workflows for the Job Application Automation System.

## Purpose

n8n handles the main orchestration:

- Job collection from multiple sources
- Job deduplication
- Preference filtering
- Triggering Gemini API for matching
- Calling the API service
- Calling Playwright browser worker
- Sending Telegram notifications
- State management

## Workflow Structure

```
workflows/
├── 01_job_collection_career_page.json
├── 02_job_collection_bdjobs.json
├── 03_deduplicate_jobs.json
├── 04_filter_by_preferences.json
├── 05_gemini_job_matching.json
├── 06_select_cv.json
├── 07_send_telegram_notification.json
├── 08_application_form_filling.json
├── 09_submit_application.json
└── 10_application_tracking.json
```

## Design Pattern

All workflows follow this pattern:

```
Trigger
  ↓
Error handling
  ↓
Business logic
  ↓
Database update
  ↓
Notification (if needed)
```

## Key Concepts

### State Machine

n8n reads and updates application states in PostgreSQL:

```
n8n reads: status = "AWAITING_APPROVAL"
n8n executes: form filling
n8n updates: status = "FORM_FILLING"
```

### API Integration

n8n calls the API service for data:

```
POST /api/jobs/unprocessed
POST /api/applications/{id}/fill-form
POST /api/applications/{id}/submit
```

### Playwright Integration

n8n calls the browser worker:

```
POST http://browser-worker:3000/application/start
POST http://browser-worker:3000/application/fill
POST http://browser-worker:3000/application/submit
```

### Telegram Notifications

For user interactions (approvals, rejections):

```
POST https://api.telegram.org/bot{token}/sendMessage
```

## Implementation Phases

- **Phase 6**: Career page collector
- **Phase 7**: Bdjobs collector
- **Phase 8**: Deduplication workflow
- **Phase 9**: Preference filtering
- **Phase 10**: Gemini matching
- **Phase 12**: Telegram notifications
- **Phase 14**: Browser automation orchestration

## Notes

- Start simple with one job source
- Gradually add complexity
- Use n8n's error handling extensively
- Log all workflow executions for debugging
