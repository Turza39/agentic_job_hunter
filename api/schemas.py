"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl, AliasChoices
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# Profile Schemas
class ProfileBase(BaseModel):
    """Base profile schema"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=255)
    portfolio: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    salary_expectation: Optional[int] = Field(None, ge=0)
    education: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    experience: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)


class ProfileCreate(ProfileBase):
    """Schema for creating a profile"""
    pass


class ProfileUpdate(BaseModel):
    """Schema for updating a profile (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=255)
    portfolio: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    salary_expectation: Optional[int] = Field(None, ge=0)
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    skills: Optional[List[str]] = None


class ProfileResponse(ProfileBase):
    """Schema for profile response"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    extra_data: Dict[str, Any] = Field(default_factory=dict, serialization_alias="metadata")
    
    class Config:
        from_attributes = True


class ProfileDetailResponse(ProfileResponse):
    """Detailed profile response with CVs"""
    cvs: List['CVResponse'] = Field(default_factory=list)


# CV Schemas
class CVBase(BaseModel):
    """Base CV schema"""
    filename: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    target_roles: Optional[List[str]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)


class CVCreate(CVBase):
    """Schema for creating a CV"""
    pass


class CVUpdate(BaseModel):
    """Schema for updating a CV"""
    category: Optional[str] = Field(None, max_length=100)
    target_roles: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    is_active: Optional[bool] = None


class CVResponse(CVBase):
    """Schema for CV response"""
    id: UUID
    profile_id: UUID
    file_path: str
    file_size: Optional[int]
    content_hash: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    extra_data: Dict[str, Any] = Field(default_factory=dict, serialization_alias="metadata")
    
    class Config:
        from_attributes = True


class CVDetailResponse(CVResponse):
    """Detailed CV response with file details"""
    pass


# User Preferences Schema
class UserPreferenceBase(BaseModel):
    """Base user preference schema"""
    preferred_locations: Optional[List[str]] = Field(default_factory=list)
    exclude_locations: Optional[List[str]] = Field(default_factory=list)
    allow_remote: bool = True
    allow_hybrid: bool = True
    allow_onsite: bool = True
    min_experience_years: int = Field(0, ge=0)
    max_experience_years: int = Field(100, ge=0)
    preferred_job_types: List[str] = Field(default_factory=lambda: ["Full-time"])
    min_salary: Optional[int] = Field(None, ge=0)
    max_salary: Optional[int] = Field(None, ge=0)
    required_keywords: Optional[List[str]] = Field(default_factory=list)
    excluded_keywords: Optional[List[str]] = Field(default_factory=list)
    min_match_score: int = Field(70, ge=0, le=100)
    preferred_companies: Optional[List[str]] = Field(default_factory=list)
    excluded_companies: Optional[List[str]] = Field(default_factory=list)


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences"""
    pass


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences"""
    preferred_locations: Optional[List[str]] = None
    exclude_locations: Optional[List[str]] = None
    allow_remote: Optional[bool] = None
    allow_hybrid: Optional[bool] = None
    allow_onsite: Optional[bool] = None
    min_experience_years: Optional[int] = Field(None, ge=0)
    max_experience_years: Optional[int] = Field(None, ge=0)
    preferred_job_types: Optional[List[str]] = None
    min_salary: Optional[int] = Field(None, ge=0)
    max_salary: Optional[int] = Field(None, ge=0)
    required_keywords: Optional[List[str]] = None
    excluded_keywords: Optional[List[str]] = None
    min_match_score: Optional[int] = Field(None, ge=0, le=100)
    preferred_companies: Optional[List[str]] = None
    excluded_companies: Optional[List[str]] = None


class UserPreferenceResponse(UserPreferenceBase):
    """Schema for user preference response"""
    id: UUID
    profile_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    extra_data: Dict[str, Any] = Field(default_factory=dict, serialization_alias="metadata")
    
    class Config:
        from_attributes = True


# Error Response
class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health Check
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    version: str


# Company Schemas
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    website: Optional[HttpUrl] = None
    career_page_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    website: Optional[HttpUrl] = None
    career_page_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class CompanyResponse(CompanyBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    extra_data: Dict[str, Any] = Field(default_factory=dict, serialization_alias="metadata")
    
    class Config:
        from_attributes = True


# Job Source Schemas
class JobSourceBase(BaseModel):
    company_id: UUID
    source_type: str = Field(..., max_length=50) # 'career_page', 'bdjobs', 'email', 'linkedin'
    source_url: Optional[HttpUrl] = None
    api_endpoint: Optional[HttpUrl] = None
    extraction_strategy: Optional[str] = Field(None, max_length=100) # 'html', 'json', 'rss', 'api', 'sitemap'
    auth_method: str = Field("none", max_length=50)
    auth_config: Dict[str, Any] = Field(default_factory=dict)
    polling_interval_hours: int = Field(24, ge=1)

class JobSourceCreate(JobSourceBase):
    pass

class JobSourceUpdate(BaseModel):
    source_type: Optional[str] = Field(None, max_length=50)
    source_url: Optional[HttpUrl] = None
    api_endpoint: Optional[HttpUrl] = None
    extraction_strategy: Optional[str] = Field(None, max_length=100)
    auth_method: Optional[str] = Field(None, max_length=50)
    auth_config: Optional[Dict[str, Any]] = None
    polling_interval_hours: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None

class JobSourceResponse(JobSourceBase):
    id: UUID
    last_polled_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    extra_data: Dict[str, Any] = Field(default_factory=dict, serialization_alias="metadata")
    
    class Config:
        from_attributes = True


# Job Schemas
class JobBase(BaseModel):
    company_id: UUID
    source_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    location: Optional[str] = Field(None, max_length=255)
    job_type: Optional[str] = Field(None, max_length=50)
    remote_type: Optional[str] = Field(None, max_length=50)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: str = Field("USD", max_length=10)
    experience_required: Optional[int] = Field(None, ge=0)
    experience_level: Optional[str] = Field(None, max_length=50)
    requirements: Optional[List[str]] = Field(default_factory=list)
    nice_to_have: Optional[List[str]] = Field(default_factory=list)
    application_url: Optional[HttpUrl] = None
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    job_type: Optional[str] = Field(None, max_length=50)
    remote_type: Optional[str] = Field(None, max_length=50)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    experience_required: Optional[int] = Field(None, ge=0)
    experience_level: Optional[str] = Field(None, max_length=50)
    requirements: Optional[List[str]] = None
    nice_to_have: Optional[List[str]] = None
    application_url: Optional[HttpUrl] = None
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class JobResponse(JobBase):
    id: UUID
    normalized_hash: Optional[str] = None
    is_duplicate: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    extra_data: Dict[str, Any] = Field(default_factory=dict, serialization_alias="metadata")
    
    class Config:
        from_attributes = True


# Update forward references
ProfileDetailResponse.model_rebuild()