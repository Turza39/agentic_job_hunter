from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID
import hashlib

from ..models.job import Job
from ..schemas.job import JobCreate, JobUpdate


class JobService:
    """Service for managing jobs."""

    @staticmethod
    def _generate_normalized_hash(
        company_id: UUID,
        title: str,
        application_url: Optional[str]
    ) -> str:
        """
        Generate a deterministic hash used for job deduplication.
        """

        normalized_title = " ".join(title.lower().split())

        normalized_url = (
            application_url.lower().rstrip("/")
            if application_url
            else ""
        )

        hash_input = (
            f"{company_id}:"
            f"{normalized_title}:"
            f"{normalized_url}"
        )

        return hashlib.sha256(
            hash_input.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def create_job(
        db: Session,
        job_data: JobCreate
    ) -> Job:
        """
        Create a discovered job.

        Jobs are normally created by the collector/n8n pipeline,
        not directly by users.
        """

        title = job_data.title.strip()

        application_url = (
            str(job_data.application_url)
            if job_data.application_url
            else None
        )

        normalized_hash = JobService._generate_normalized_hash(
            company_id=job_data.company_id,
            title=title,
            application_url=application_url
        )

        # Deduplicate using normalized hash.
        existing_job = (
            db.query(Job)
            .filter(
                Job.normalized_hash == normalized_hash
            )
            .first()
        )

        if existing_job:
            return existing_job

        job = Job(
            company_id=job_data.company_id,
            title=title,
            description=job_data.description,
            location=job_data.location,
            job_type=job_data.job_type,
            remote_type=job_data.remote_type,
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            currency=job_data.currency,
            experience_required=job_data.experience_required,
            experience_level=job_data.experience_level,
            requirements=job_data.requirements or [],
            nice_to_have=job_data.nice_to_have or [],
            application_url=application_url,
            posted_at=job_data.posted_at,
            expires_at=job_data.expires_at,
            normalized_hash=normalized_hash,
            is_duplicate=False,
            is_active=True
        )

        db.add(job)

        try:
            db.commit()
            db.refresh(job)

            return job

        except IntegrityError:
            db.rollback()

            # Another collector process may have inserted the same job.
            existing_job = (
                db.query(Job)
                .filter(
                    Job.normalized_hash == normalized_hash
                )
                .first()
            )

            if existing_job:
                return existing_job

            raise ValueError(
                "Integrity error creating job"
            )

    @staticmethod
    def get_job(
        db: Session,
        job_id: UUID
    ) -> Optional[Job]:
        """Get a job by ID."""

        return (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

    @staticmethod
    def list_jobs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        is_duplicate: Optional[bool] = None,
        company_id: Optional[UUID] = None
    ) -> List[Job]:
        """List jobs with optional filters."""

        query = db.query(Job)

        if is_active is not None:
            query = query.filter(
                Job.is_active == is_active
            )

        if is_duplicate is not None:
            query = query.filter(
                Job.is_duplicate == is_duplicate
            )

        if company_id is not None:
            query = query.filter(
                Job.company_id == company_id
            )

        return (
            query
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_job(
        db: Session,
        job_id: UUID,
        job_data: JobUpdate
    ) -> Optional[Job]:
        """Update a discovered job."""

        job = JobService.get_job(db, job_id)

        if not job:
            return None

        update_data = job_data.model_dump(
            exclude_unset=True
        )

        if (
            "application_url" in update_data
            and update_data["application_url"]
        ):
            update_data["application_url"] = str(
                update_data["application_url"]
            )

        for field, value in update_data.items():
            setattr(job, field, value)

        # Recalculate deduplication hash if identity fields changed.
        if (
            "title" in update_data
            or "application_url" in update_data
        ):
            job.normalized_hash = (
                JobService._generate_normalized_hash(
                    company_id=job.company_id,
                    title=job.title,
                    application_url=job.application_url
                )
            )

        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def delete_job(
        db: Session,
        job_id: UUID
    ) -> bool:
        """Deactivate a job."""

        job = JobService.get_job(db, job_id)

        if not job:
            return False

        job.is_active = False

        db.commit()

        return True