# Phase 4 - Profile & CV Management API: Implementation Guide

## Overview

Phase 4 implements a complete FastAPI-based REST API for managing user profiles and CVs with file upload support, database persistence via PostgreSQL, and comprehensive validation.

## ✅ What's Implemented

### 1. Core API Application (`main.py`)
- FastAPI application initialization
- CORS middleware for cross-origin requests
- Health check endpoint (`/health`)
- Automatic database table creation
- Startup/shutdown event handlers
- Global exception handling
- Interactive documentation at `/docs`

### 2. API Routes (`routes.py`)
Complete REST endpoints for three resource types:

#### Profile Endpoints
- `POST /api/profiles` - Create new profile
- `GET /api/profiles/{profile_id}` - Get single profile
- `GET /api/profiles` - List all profiles with pagination
- `GET /api/profiles/email/{email}` - Get by email
- `PUT /api/profiles/{profile_id}` - Update profile
- `DELETE /api/profiles/{profile_id}` - Soft delete profile

#### CV Endpoints
- `POST /api/profiles/{profile_id}/cvs` - Upload CV with file
- `GET /api/profiles/{profile_id}/cvs` - List profile CVs
- `GET /api/cvs/{cv_id}` - Get CV details
- `PUT /api/cvs/{cv_id}` - Update CV metadata
- `DELETE /api/cvs/{cv_id}` - Delete CV and file
- `POST /api/cvs/{cv_id}/activate` - Activate CV (deactivate others)

#### Preference Endpoints
- `POST /api/profiles/{profile_id}/preferences` - Create preferences
- `GET /api/profiles/{profile_id}/preferences` - Get preferences
- `PUT /api/profiles/{profile_id}/preferences` - Update preferences

### 3. Business Logic Services (`service.py`)

#### ProfileService
- `create_profile()` - Create new profile with validation
- `get_profile()` - Retrieve by ID
- `get_profile_by_email()` - Retrieve by email
- `list_profiles()` - List with pagination
- `update_profile()` - Update fields
- `delete_profile()` - Soft delete

#### CVService
- `create_cv()` - Create CV record with file hash
- `get_cv()` - Retrieve CV
- `list_profile_cvs()` - List all CVs for profile
- `list_active_cvs()` - List active CVs only
- `update_cv()` - Update CV metadata
- `delete_cv()` - Delete CV and file
- `activate_cv()` - Activate CV (deactivate others)
- `calculate_file_hash()` - SHA-256 file hashing

#### UserPreferenceService
- `create_or_update_preferences()` - Create or update
- `get_preferences()` - Retrieve preferences
- `update_preferences()` - Update specific fields

### 4. Data Models (`models.py`)

SQLAlchemy ORM models with complete relationships:

#### Profile
```
id: UUID (Primary Key)
name: String
email: String (Unique)
phone: String
location: String
salary_expectation: Integer
skills: JSONB Array
education: JSONB Array
experience: JSONB Array
portfolio: String (URL)
github: String (URL)
linkedin: String (URL)
is_active: Boolean (default: True)
created_at: DateTime
updated_at: DateTime
metadata: JSONB

Relations:
- cvs: One-to-Many with CV
- preferences: One-to-One with UserPreference
```

#### CV
```
id: UUID (Primary Key)
profile_id: UUID (Foreign Key)
filename: String
category: String
target_roles: JSONB Array
skills: JSONB Array
file_path: String
file_size: Integer
content_hash: String (SHA-256)
is_active: Boolean (default: True)
created_at: DateTime
updated_at: DateTime

Relations:
- profile: Many-to-One with Profile
```

#### UserPreference
```
id: UUID (Primary Key)
profile_id: UUID (Foreign Key, Unique)
preferred_locations: JSONB Array
exclude_locations: JSONB Array
allow_remote: Boolean
allow_hybrid: Boolean
allow_onsite: Boolean
min_experience_years: Integer
max_experience_years: Integer
preferred_job_types: JSONB Array
min_salary: Integer
max_salary: Integer
required_keywords: JSONB Array
excluded_keywords: JSONB Array
min_match_score: Integer
created_at: DateTime
updated_at: DateTime

Relations:
- profile: One-to-One with Profile
```

### 5. Validation Schemas (`schemas.py`)

Pydantic v2 schemas with comprehensive validation:

#### Profile Schemas
- `ProfileBase` - Common fields
- `ProfileCreate` - Request validation for creation
- `ProfileUpdate` - Request validation for updates (all fields optional)
- `ProfileResponse` - Response serialization
- `ProfileDetailResponse` - Response with nested CVs

#### CV Schemas
- `CVBase` - Common fields
- `CVCreate` - Request validation
- `CVUpdate` - Request validation
- `CVResponse` - Response serialization
- `CVDetailResponse` - Extended response

#### Preference Schemas
- `UserPreferenceBase` - Common fields
- `UserPreferenceCreate` - Request validation
- `UserPreferenceUpdate` - Request validation (all optional)
- `UserPreferenceResponse` - Response serialization

#### Common Schemas
- `ErrorResponse` - Standard error format
- `HealthResponse` - Health check format

**Validation Features:**
- Email validation (EmailStr)
- URL validation (HttpUrl) for portfolio, GitHub, LinkedIn
- Length constraints on strings
- Numeric bounds (min/max for salary, experience)
- Optional fields with proper defaults
- Array validation for skills, roles, keywords

### 6. Database Configuration (`database.py`)
- SQLAlchemy engine with connection pooling
- Session factory pattern
- FastAPI dependency injection setup
- Environment-based database URL construction
- Connection pool pre-ping for reliability

### 7. Application Settings (`config.py`)
- Settings class using Pydantic BaseSettings
- Environment variable loading from .env
- Type-safe configuration
- Default values for optional settings

### 8. File Upload Handling
- Multipart form-data support
- File type validation (PDF, DOC, DOCX)
- File size validation (configurable 10MB limit)
- Directory creation per profile
- SHA-256 content hashing
- File path management

### 9. Docker Integration

#### Dockerfile
- Python 3.11-slim base image
- System dependencies (gcc, postgresql-client)
- Python dependency installation
- Application code copying
- Directory creation
- Health check setup
- Uvicorn server startup

#### Docker Compose Integration
```yaml
api:
  build: ./api
  container_name: job-agent-api
  ports:
    - "8000:8000"
  volumes:
    - ./api:/app
    - ./cv-storage:/app/cv-storage
  depends_on:
    postgres:
      condition: service_healthy
  environment:
    - PostgreSQL connection details
    - API_HOST, API_PORT
    - DEBUG flag
    - CV storage settings
```

### 10. Testing & Documentation

#### Test Suite (`test_api.py`)
Comprehensive test coverage:
- Health check validation
- Profile CRUD operations
- CV upload and management
- CV activation and deactivation
- Preference management
- Error handling
- Integration testing

#### API Documentation (`api/README.md`)
- Installation instructions
- Project structure overview
- Complete endpoint documentation
- Usage examples (Python, cURL)
- Database model documentation
- Configuration guide
- Error handling reference

#### Interactive API Docs
- Swagger UI at `http://localhost:8000/docs`
- ReDoc at `http://localhost:8000/redoc`
- Auto-generated from code

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL connection (via Docker)

### Quick Start

#### Option 1: Docker (Recommended)
```bash
# Setup with provided script
# On Windows PowerShell:
.\setup_phase4.ps1

# On Linux/Mac:
bash setup_phase4.sh

# Or manually:
docker-compose up api
```

#### Option 2: Local Development
```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Access the API
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📝 Example Workflows

### Create a Profile
```bash
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "location": "San Francisco, CA",
    "salary_expectation": 150000,
    "skills": ["Python", "FastAPI", "PostgreSQL"]
  }'
```

### Upload a CV
```bash
curl -X POST http://localhost:8000/api/profiles/{profile_id}/cvs \
  -F "file=@resume.pdf" \
  -F "category=Backend" \
  -F "target_roles=Senior Engineer" \
  -F "skills=Python,FastAPI"
```

### Set Job Preferences
```bash
curl -X POST http://localhost:8000/api/profiles/{profile_id}/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_locations": ["San Francisco", "New York"],
    "allow_remote": true,
    "min_salary": 120000,
    "max_salary": 200000
  }'
```

## 🧪 Testing

Run the test suite:
```bash
# From project root
python api/test_api.py

# With Docker
docker-compose exec api python test_api.py
```

Expected output:
```
============================================================
AGENTIC JOB HUNTER API - TEST SUITE
============================================================
============================================================
TEST: Health Check
============================================================
Status: 200
✅ Health check passed

... (more tests)

✅ ALL TESTS PASSED!
============================================================
```

## 📊 Project Structure

```
api/
├── main.py                 # FastAPI app entry point
├── routes.py               # REST endpoint handlers
├── service.py              # Business logic layer
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic validation
├── database.py             # Database connection
├── config.py               # Settings
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container config
├── test_api.py             # Test suite
├── README.md               # API documentation
└── __init__.py             # Package init
```

## 🔧 Configuration

Environment variables (`.env`):
```
POSTGRES_USER=jobagent
POSTGRES_PASSWORD=turza039
POSTGRES_DB=job_agent
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

API_HOST=0.0.0.0
API_PORT=8000

DEBUG=false

CV_UPLOAD_DIR=cv-storage/uploads
MAX_CV_SIZE_MB=10
```

## 🐛 Troubleshooting

### API won't start
```bash
# Check logs
docker-compose logs api

# Ensure PostgreSQL is running
docker-compose logs postgres
```

### Database connection error
```bash
# Check PostgreSQL is healthy
docker-compose exec postgres pg_isready

# Test connection
docker-compose exec api python -c "from database import SessionLocal; db = SessionLocal(); print('Connected!')"
```

### File upload issues
```bash
# Check directory permissions
ls -la cv-storage/uploads/

# Ensure directory exists for profile
mkdir -p cv-storage/uploads/{profile_id}
```

## 📚 Next Steps

After Phase 4 is complete:

1. **Phase 5**: Job Source System (Implement job source abstraction)
2. **Phase 6**: Career Page Collector (n8n integration)
3. **Phase 7+**: Job matching, application automation, browser integration

## 📖 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
