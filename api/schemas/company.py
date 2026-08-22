from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    website: Optional[HttpUrl] = None
    career_page_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    website: Optional[HttpUrl] = None
    career_page_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    extra_data: dict = Field(
        default_factory=dict,
        serialization_alias="metadata"
    )

    class Config:
        from_attributes = True