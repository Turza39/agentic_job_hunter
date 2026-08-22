"""
Schemas module - Pydantic models for request/response validation
"""
from .user import ProfileCreate, ProfileUpdate, ProfileResponse, ProfileDetailResponse
from .cv import CVCreate, CVUpdate, CVResponse
from .preference import UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse
from .company import CompanyCreate, CompanyUpdate, CompanyResponse
from .job import JobCreate, JobUpdate, JobResponse
from .common import ErrorResponse, HealthResponse

__all__ = [
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "ProfileDetailResponse",
    "CVCreate",
    "CVUpdate",
    "CVResponse",
    "UserPreferenceCreate",
    "UserPreferenceUpdate",
    "UserPreferenceResponse",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "ErrorResponse",
    "HealthResponse",
]