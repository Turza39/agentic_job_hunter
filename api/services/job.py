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
        job_url: str
    ) -> str:
        """
        Generate deterministic hash for job identity.

        A job is identified by:
        company + normalized title + job URL
        """

        normalized_title = " ".join(
            title.lower().split()
        )

        normalized_url = (
            job_url.lower().rstrip("/")
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

        title = job_data.title.strip()

        source_url = str(
            job_data.source_url
        )

        job_url = str(
            job_data.job_url
        )

        application_url = (
            str(job_data.application_url)
            if job_data.application_url
            else None
        )

        normalized_hash = (
            JobService._generate_normalized_hash(
                company_id=job_data.company_id,
                title=title,
                job_url=job_url
            )
        )

        existing_job = (
            db.query(Job)
            .filter(
                Job.normalized_hash == normalized_hash
            )
            .first()
        )

        if existing_job:

            # Update information discovered on
            # subsequent collection runs.
            existing_job.description = (
                job_data.description
            )

            existing_job.location = (
                job_data.location
            )

            existing_job.job_type = (
                job_data.job_type
            )

            existing_job.remote_type = (
                job_data.remote_type
            )

            existing_job.salary_min = (
                job_data.salary_min
            )

            existing_job.salary_max = (
                job_data.salary_max
            )

            existing_job.currency = (
                job_data.currency
            )

            existing_job.experience_required = (
                job_data.experience_required
            )

            existing_job.experience_level = (
                job_data.experience_level
            )

            existing_job.requirements = (
                job_data.requirements
            )

            existing_job.nice_to_have = (
                job_data.nice_to_have
            )

            existing_job.application_url = (
                application_url
            )

            existing_job.posted_at = (
                job_data.posted_at
            )

            existing_job.expires_at = (
                job_data.expires_at
            )

            existing_job.is_active = True

            db.commit()
            db.refresh(existing_job)

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

            experience_required=(
                job_data.experience_required
            ),

            experience_level=(
                job_data.experience_level
            ),

            requirements=(
                job_data.requirements
            ),

            nice_to_have=(
                job_data.nice_to_have
            ),

            source_url=source_url,
            job_url=job_url,
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

            existing_job = (
                db.query(Job)
                .filter(
                    Job.normalized_hash ==
                    normalized_hash
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
            .order_by(Job.created_at.desc())
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

        job = JobService.get_job(
            db,
            job_id
        )

        if not job:
            return None

        update_data = job_data.model_dump(
            exclude_unset=True
        )

        if (
            "source_url" in update_data
            and update_data["source_url"]
        ):
            update_data["source_url"] = str(
                update_data["source_url"]
            )

        if (
            "job_url" in update_data
            and update_data["job_url"]
        ):
            update_data["job_url"] = str(
                update_data["job_url"]
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

        if (
            "title" in update_data
            or "job_url" in update_data
        ):

            job.normalized_hash = (
                JobService._generate_normalized_hash(
                    company_id=job.company_id,
                    title=job.title,
                    job_url=job.job_url
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

        job = JobService.get_job(
            db,
            job_id
        )

        if not job:
            return False

        job.is_active = False

        db.commit()

        return True