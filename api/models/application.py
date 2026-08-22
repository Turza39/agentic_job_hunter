"""
Application model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


class Application(Base):
    """Application model"""
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_match_id = Column(UUID(as_uuid=True), ForeignKey("job_matches.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    cv_id = Column(UUID(as_uuid=True), ForeignKey("cvs.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(100), default="DISCOVERED")
    user_approved = Column(Boolean, default=False)
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    form_url = Column(String(500))
    form_data = Column(JSON, default=dict)
    unknown_fields = Column(JSON, default=list)
    submitted_at = Column(DateTime)
    submission_error = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error = Column(Text)
    last_error_at = Column(DateTime)
    screenshot_path = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_data = Column("metadata", JSON, default=dict)

    # Relationships
    profile = relationship("Profile", back_populates="applications")
    cv = relationship("CV", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    job_match = relationship("JobMatch", back_populates="applications")