"""
User preference schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


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
    extra_data: dict = Field(default_factory=dict, serialization_alias="metadata")
    
    class Config:
        from_attributes = True