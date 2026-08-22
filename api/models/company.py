from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Company(Base):
    """Company model"""

    __tablename__ = "companies"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(255),
        unique=True,
        nullable=False
    )

    website = Column(String(500))

    career_page_url = Column(String(500))

    description = Column(Text)

    industry = Column(String(100))

    country = Column(String(100))

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Internal metadata.
    # This should not be supplied by normal users.
    extra_data = Column(
        "metadata",
        JSON,
        default=dict
    )

    # Relationships
    jobs = relationship(
        "Job",
        back_populates="company",
        cascade="all, delete-orphan"
    )