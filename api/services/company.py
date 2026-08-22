from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID

from ..models.company import Company
from ..schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Service for managing companies"""

    @staticmethod
    def create_company(
        db: Session,
        company_data: CompanyCreate
    ) -> Company:
        """
        Create a company.

        The company's career_page_url is stored on the Company row itself;
        no separate job-source record is created.
        """

        try:
            company = Company(
                name=company_data.name,
                website=(
                    str(company_data.website)
                    if company_data.website
                    else None
                ),
                career_page_url=(
                    str(company_data.career_page_url)
                    if company_data.career_page_url
                    else None
                ),
                description=company_data.description,
                industry=company_data.industry,
                country=company_data.country,
            )

            db.add(company)
            db.commit()
            db.refresh(company)

            return company

        except IntegrityError:
            db.rollback()
            raise ValueError(
                f"Company with name '{company_data.name}' already exists"
            )

    @staticmethod
    def get_company(
        db: Session,
        company_id: UUID
    ) -> Optional[Company]:
        """Get a company by ID."""

        return (
            db.query(Company)
            .filter(Company.id == company_id)
            .first()
        )

    @staticmethod
    def list_companies(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Company]:
        """List active companies."""

        return (
            db.query(Company)
            .filter(Company.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_company(
        db: Session,
        company_id: UUID,
        company_data: CompanyUpdate
    ) -> Optional[Company]:
        """
        Update a company.
        """

        company = CompanyService.get_company(db, company_id)

        if not company:
            return None

        update_data = company_data.model_dump(exclude_unset=True)

        # Convert HttpUrl values to strings.
        for url_field in ["website", "career_page_url"]:
            if url_field in update_data and update_data[url_field]:
                update_data[url_field] = str(update_data[url_field])

        try:
            # Update company fields.
            for field, value in update_data.items():
                setattr(company, field, value)

            db.commit()
            db.refresh(company)

            return company

        except IntegrityError:
            db.rollback()
            raise ValueError("Company name conflict")

    @staticmethod
    def delete_company(
        db: Session,
        company_id: UUID
    ) -> bool:
        """
        Soft-delete/deactivate a company.

        Associated jobs are not physically deleted.
        """

        company = CompanyService.get_company(db, company_id)

        if not company:
            return False

        company.is_active = False

        # Deactivate associated jobs as well.
        for job in company.jobs:
            job.is_active = False

        db.commit()

        return True