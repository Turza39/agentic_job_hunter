"""
Job match model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


class JobMatch(Base):
    """Job match model"""
    __tablename__ = "job_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    selected_cv_id = Column(UUID(as_uuid=True), ForeignKey("cvs.id", ondelete="SET NULL"))
    match_score = Column(Integer)
    recommendation = Column(String(50))
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    experience_match = Column(Boolean)
    reason = Column(Text)
    ai_evaluation = Column(JSON, default=dict)
    evaluated_at = Column(DateTime)
    status = Column(String(50), default="DISCOVERED")
    notified_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_data = Column("metadata", JSON, default=dict)

    # Relationships
    profile = relationship("Profile", back_populates="matches")
    job = relationship("Job", back_populates="matches")
    applications = relationship("Application", back_populates="job_match")