"""
CV schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


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