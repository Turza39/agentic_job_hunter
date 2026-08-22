"""
User preference model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


class UserPreference(Base):
    """User preferences for job filtering"""
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Location preferences
    preferred_locations = Column(JSON, default=list)
    exclude_locations = Column(JSON, default=list)
    allow_remote = Column(Boolean, default=True)
    allow_hybrid = Column(Boolean, default=True)
    allow_onsite = Column(Boolean, default=True)

    # Experience preferences
    min_experience_years = Column(Integer, default=0)
    max_experience_years = Column(Integer, default=100)

    # Job type preferences
    preferred_job_types = Column(JSON, default=lambda: ["Full-time"])

    # Salary preferences
    min_salary = Column(Integer)
    max_salary = Column(Integer)

    # Keywords
    required_keywords = Column(JSON, default=list)
    excluded_keywords = Column(JSON, default=list)

    # Matching threshold
    min_match_score = Column(Integer, default=70)

    # Companies
    preferred_companies = Column(JSON, default=list)
    excluded_companies = Column(JSON, default=list)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_data = Column("metadata", JSON, default=dict)
    
    # Relationships
    profile = relationship("Profile", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(profile_id={self.profile_id})>"