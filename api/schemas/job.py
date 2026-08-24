"""
Job schemas
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class JobBase(BaseModel):

    company_id: UUID

    title: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    description: str = Field(
        ...,
        min_length=1
    )

    location: Optional[str] = Field(
        None,
        max_length=255
    )

    job_type: Optional[str] = Field(
        None,
        max_length=50
    )

    remote_type: Optional[str] = Field(
        None,
        max_length=50
    )

    salary_min: Optional[int] = Field(
        None,
        ge=0
    )

    salary_max: Optional[int] = Field(
        None,
        ge=0
    )

    currency: Optional[str] = Field(
        None,
        max_length=10
    )

    experience_required: Optional[int] = Field(
        None,
        ge=0
    )

    experience_level: Optional[str] = Field(
        None,
        max_length=50
    )

    requirements: List[str] = Field(
        default_factory=list
    )

    nice_to_have: List[str] = Field(
        default_factory=list
    )

    source_url: HttpUrl

    job_url: HttpUrl

    application_url: Optional[HttpUrl] = None

    posted_at: Optional[datetime] = None

    expires_at: Optional[datetime] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255
    )

    description: Optional[str] = Field(
        None,
        min_length=1
    )

    location: Optional[str] = Field(
        None,
        max_length=255
    )

    job_type: Optional[str] = Field(
        None,
        max_length=50
    )

    remote_type: Optional[str] = Field(
        None,
        max_length=50
    )

    salary_min: Optional[int] = Field(
        None,
        ge=0
    )

    salary_max: Optional[int] = Field(
        None,
        ge=0
    )

    currency: Optional[str] = Field(
        None,
        max_length=10
    )

    experience_required: Optional[int] = Field(
        None,
        ge=0
    )

    experience_level: Optional[str] = Field(
        None,
        max_length=50
    )

    requirements: Optional[List[str]] = None

    nice_to_have: Optional[List[str]] = None

    source_url: Optional[HttpUrl] = None

    job_url: Optional[HttpUrl] = None

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

    extra_data: dict = Field(
        default_factory=dict,
        serialization_alias="metadata"
    )

    class Config:
        from_attributes = True