"""
Profile (User) model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


class Profile(Base):
    """User profile model"""
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    location = Column(String(255))
    education = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    skills = Column(JSON, default=list)
    portfolio = Column(String(255))
    github = Column(String(255))
    linkedin = Column(String(255))
    salary_expectation = Column(Integer)  # Annual salary
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_data = Column("metadata", JSON, default=dict)
    
    # Relationships
    cvs = relationship("CV", back_populates="profile", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="profile", uselist=False, cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="profile", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="profile", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Profile(id={self.id}, name={self.name}, email={self.email})>"