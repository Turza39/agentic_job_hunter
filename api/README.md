# API Service - Phase 4: Profile & CV Management

FastAPI-based REST API for managing user profiles and CVs in the Agentic Job Hunter system.

## Overview

The API provides endpoints for:

- ✅ User profile creation and management (Phase 4)
- ✅ Multiple CVs per user with categories (Phase 4)
- ✅ CV file upload handling (PDF, DOC, DOCX) (Phase 4)
- ✅ User preferences/filtering configuration (Phase 4)
- Company and job source configuration (Phase 5)
- Job listings and filtering (Phase 6)
- Application management (Phase 7-9)
- Notifications (Phase 12)

## Technology Stack

- **Framework**: FastAPI 0.104.1 with Uvicorn
- **Database**: PostgreSQL 16 Alpine
- **ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.5.0
- **Authentication**: API Keys (planned Phase 11), JWT (later)
- **Docker**: Multi-container orchestration
- **Validation**: Pydantic

## Project Structure

```
api/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── config.py              # Configuration and settings
├── database.py            # Database connection
├── models/                # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── profile.py
│   ├── cv.py
│   ├── company.py
│   ├── job.py
│   ├── application.py
│   └── notification.py
├── schemas/               # Pydantic request/response schemas
│   ├── __init__.py
│   ├── profile.py
│   ├── cv.py
│   ├── job.py
│   └── application.py
├── routes/                # API routes/endpoints
│   ├── __init__.py
│   ├── profiles.py
│   ├── cvs.py
│   ├── companies.py
│   ├── jobs.py
│   ├── applications.py
│   ├── preferences.py
│   └── notifications.py
├── services/              # Business logic
│   ├── __init__.py
│   ├── profile_service.py
│   ├── job_service.py
│   ├── application_service.py
│   └── notification_service.py
├── middleware/            # Custom middleware
│   └── error_handler.py
└── tests/                 # Unit and integration tests
    ├── __init__.py
    ├── test_profiles.py
    ├── test_jobs.py
    └── test_applications.py
```

## Implementation Priority

See Phase 4 onwards in the main README.

## Notes

- This will initially be a simple CRUD API
- Later phases will add complex business logic
- Authentication will be enhanced over time
- Documentation will be generated with OpenAPI/Swagger
