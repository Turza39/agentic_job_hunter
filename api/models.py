"""
SQLAlchemy models for database tables
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


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
    extra_data = Column(JSON, default=dict)
    
    # Relationships
    cvs = relationship("CV", back_populates="profile", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="profile", uselist=False, cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="profile", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="profile", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="profile", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Profile(id={self.id}, name={self.name}, email={self.email})>"


class CV(Base):
    """CV model for multiple CVs per user"""
    __tablename__ = "cvs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    category = Column(String(100))  # e.g., "ML/AI", "DevOps", "Backend", "General"
    target_roles = Column(JSON, default=list)
    skills = Column(JSON, default=list)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    content_hash = Column(String(64))  # SHA-256 hash
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_data = Column(JSON, default=dict)
    
    # Relationships
    profile = relationship("Profile", back_populates="cvs")
    applications = relationship("Application", back_populates="cv")
    
    def __repr__(self):
        return f"<CV(id={self.id}, filename={self.filename}, category={self.category})>"


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
    extra_data = Column(JSON, default=dict)
    
    # Relationships
    profile = relationship("Profile", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference(profile_id={self.profile_id})>"


# Import other models to avoid circular import issues
from sqlalchemy.orm import relationship as orm_relationship


class JobMatch(Base):
    """Job match model (placeholder for relationships)"""
    __tablename__ = "job_matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False)
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
    extra_data = Column(JSON, default=dict)
    
    profile = orm_relationship("Profile", back_populates="matches")
    

class Application(Base):
    """Application model (placeholder)"""
    __tablename__ = "applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_match_id = Column(UUID(as_uuid=True), nullable=False)
    job_id = Column(UUID(as_uuid=True), nullable=False)
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
    extra_data = Column(JSON, default=dict)
    
    profile = orm_relationship("Profile", back_populates="applications")
    cv = orm_relationship("CV", back_populates="applications")


class Notification(Base):
    """Notification model (placeholder)"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    job_match_id = Column(UUID(as_uuid=True))
    notification_type = Column(String(50))
    title = Column(String(255))
    message = Column(Text)
    delivery_channel = Column(String(50), default="telegram")
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    delivery_status = Column(String(50))
    delivery_error = Column(Text)
    action_required = Column(Boolean, default=False)
    action_type = Column(String(100))
    user_action = Column(Text)
    user_action_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_data = Column(JSON, default=dict)
    
    profile = orm_relationship("Profile", back_populates="notifications")
