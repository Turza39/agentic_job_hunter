from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..core.database import get_db
from ..schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from ..services.company import CompanyService


router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=201
)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db)
):
    """Create a company and its career-page job source."""

    try:
        return CompanyService.create_company(
            db,
            company_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )


@router.get(
    "/{company_id}",
    response_model=CompanyResponse
)
def get_company(
    company_id: UUID,
    db: Session = Depends(get_db)
):
    company = CompanyService.get_company(
        db,
        company_id
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return company


@router.get(
    "",
    response_model=List[CompanyResponse]
)
def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return CompanyService.list_companies(
        db,
        skip=skip,
        limit=limit
    )


@router.put(
    "/{company_id}",
    response_model=CompanyResponse
)
def update_company(
    company_id: UUID,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db)
):
    try:
        company = CompanyService.update_company(
            db,
            company_id,
            company_data
        )

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )

        return company

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )


@router.delete(
    "/{company_id}",
    status_code=204
)
def delete_company(
    company_id: UUID,
    db: Session = Depends(get_db)
):
    if not CompanyService.delete_company(
        db,
        company_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )