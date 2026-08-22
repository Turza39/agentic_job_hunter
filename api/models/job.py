from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Job(Base):
    """Job model"""

    __tablename__ = "jobs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(Text)

    location = Column(String(255))

    job_type = Column(String(50))

    remote_type = Column(String(50))

    salary_min = Column(Integer)

    salary_max = Column(Integer)

    currency = Column(String(10))

    experience_required = Column(Integer)

    experience_level = Column(String(50))

    requirements = Column(
        JSON,
        default=list
    )

    nice_to_have = Column(
        JSON,
        default=list
    )

    application_url = Column(String(500))

    posted_at = Column(DateTime)

    expires_at = Column(DateTime)

    normalized_hash = Column(
        String(64),
        unique=True,
        index=True
    )

    is_duplicate = Column(
        Boolean,
        default=False
    )

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

    extra_data = Column(
        "metadata",
        JSON,
        default=dict
    )

    # Relationships
    company = relationship(
        "Company",
        back_populates="jobs"
    )

    matches = relationship(
        "JobMatch",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan"
    )