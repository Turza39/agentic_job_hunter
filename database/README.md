# Database Setup

This directory contains the database initialization scripts and migrations.

## Files

- `init.sql` - Initial PostgreSQL schema and tables
  - Profiles and CV management
  - Companies and job sources
  - Jobs and job matching
  - Applications and form fields
  - Notifications and audit logging
  - Indexes and views for performance
  - Sample data for testing

## Database Schema Overview

### Core Tables

1. **profiles** - User profile information
2. **cvs** - Multiple CVs per user
3. **companies** - Job source companies
4. **job_sources** - Different job sources (career pages, job boards, etc.)
5. **jobs** - Normalized job listings
6. **user_preferences** - Filtering preferences
7. **job_matches** - AI-generated job matches with scoring
8. **applications** - Application state and tracking
9. **application_fields** - Form field details with flexible schema (JSONB)
10. **application_tracking** - Application outcomes and interview tracking
11. **notifications** - User notifications (Telegram, email, etc.)

### Supporting Tables

- `application_logs` - Detailed logging for reliability (Phase 21)
- `audit_trail` - Audit trail of all changes

## Schema Highlights

### JSONB Flexibility

Fields like `requirements`, `skills`, `form_data`, and `metadata` use PostgreSQL's JSONB type to handle unpredictable data structures:

```json
{
    "question": "Are you willing to relocate?",
    "field_type": "boolean",
    "answer": true
}
```

### State Machine

Applications follow a defined state machine:

```
DISCOVERED → MATCHED → SHORTLISTED → AWAITING_APPROVAL → APPROVED 
→ PREPARING_APPLICATION → FORM_FILLING → WAITING_FOR_USER 
→ READY_TO_SUBMIT → SUBMITTED
```

Also: REJECTED, FAILED, NEEDS_MANUAL_INTERVENTION

### Deduplication

Jobs are deduplicated using normalized hash:
```
hash(company + title + url)
```

## How to Run

From the project root:

```bash
# Start the database
docker compose up postgres

# Or start both PostgreSQL and n8n
docker compose up

# To initialize database manually (if needed)
docker exec job-agent-db psql -U jobagent -d job_agent -f /docker-entrypoint-initdb.d/init.sql
```

## Database Access

### Connection Details

- **Host**: localhost (from host machine) or `postgres` (from docker)
- **Port**: 5432
- **Database**: job_agent
- **User**: jobagent
- **Password**: (see .env file)

### Connect with psql

```bash
psql -h localhost -U jobagent -d job_agent
```

### Connect from Docker

```bash
docker exec -it job-agent-db psql -U jobagent -d job_agent
```

## Key Views

- `vw_active_jobs_for_user` - Active jobs filtered for the user
- `vw_awaiting_user_action` - Applications awaiting user action
- `vw_application_summary` - Summary of all applications

## Future Migrations

Place new migration scripts in this directory with numbered prefixes:

- `001_initial_schema.sql` (already created as init.sql)
- `002_add_new_tables.sql`
- `003_add_indexes.sql`
- etc.

## Indexes

The schema includes appropriate indexes for common queries:

- Job lookups by company, source, status
- Application filtering by status, profile, time
- Notification delivery tracking
- Audit trail searches

Performance is optimized for:

- Finding active jobs
- Matching jobs to profiles
- Tracking application state
- Audit logging
