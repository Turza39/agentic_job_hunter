"""
User/Profile schemas
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


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


from .cv import CVResponse
ProfileDetailResponse.model_rebuild()