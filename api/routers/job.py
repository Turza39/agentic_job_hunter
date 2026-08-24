"""
Job API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..core.database import get_db
from ..schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse
)
from ..services.job import JobService
from ..services.company import CompanyService


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)


@router.post(
    "",
    response_model=JobResponse,
    status_code=201
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db)
):

    company = CompanyService.get_company(
        db,
        job_data.company_id
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    try:

        return JobService.create_job(
            db,
            job_data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db)
):

    job = JobService.get_job(
        db,
        job_id
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


@router.get(
    "",
    response_model=List[JobResponse]
)
def list_jobs(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    is_duplicate: Optional[bool] = None,
    company_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):

    return JobService.list_jobs(
        db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        is_duplicate=is_duplicate,
        company_id=company_id
    )


@router.put(
    "/{job_id}",
    response_model=JobResponse
)
def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    db: Session = Depends(get_db)
):

    job = JobService.update_job(
        db,
        job_id,
        job_data
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


@router.delete(
    "/{job_id}",
    status_code=204
)
def delete_job(
    job_id: UUID,
    db: Session = Depends(get_db)
):

    if not JobService.delete_job(
        db,
        job_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )