"""
Notification model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


class Notification(Base):
    """Notification model"""
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
    extra_data = Column("metadata", JSON, default=dict)

    # Relationships
    profile = relationship("Profile", back_populates="notifications")