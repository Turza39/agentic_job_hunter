# API Service

RESTful API for the Job Application Automation System.

## Purpose

The API provides endpoints for:

- Profile and CV management
- Company and job source configuration
- Job listings and filtering
- Application management
- User preferences
- Notifications

## Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: API Keys (initially), JWT (later)
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
