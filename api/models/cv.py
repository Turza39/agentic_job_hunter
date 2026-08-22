"""
CV model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


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
    extra_data = Column("metadata", JSON, default=dict)
    
    # Relationships
    profile = relationship("Profile", back_populates="cvs")
    applications = relationship("Application", back_populates="cv")

    def __repr__(self):
        return f"<CV(id={self.id}, filename={self.filename}, category={self.category})>"