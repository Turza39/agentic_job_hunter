"""
Common schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    version: str