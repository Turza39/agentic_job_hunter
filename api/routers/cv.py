"""
CV API routes (standalone endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ..core.database import get_db
from ..schemas.cv import CVUpdate, CVResponse
from ..services.cv import CVService

router = APIRouter(prefix="/cvs", tags=["cvs"])


@router.get("/{cv_id}", response_model=CVResponse)
def get_cv(
    cv_id: UUID,
    db: Session = Depends(get_db)
):
    """Get CV details"""
    cv = CVService.get_cv(db, cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


@router.put("/{cv_id}", response_model=CVResponse)
def update_cv(
    cv_id: UUID,
    cv_data: CVUpdate,
    db: Session = Depends(get_db)
):
    """Update CV metadata"""
    cv = CVService.update_cv(db, cv_id, cv_data)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


@router.delete("/{cv_id}", status_code=204)
def delete_cv(
    cv_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a CV"""
    if not CVService.delete_cv(db, cv_id):
        raise HTTPException(status_code=404, detail="CV not found")


@router.post("/{cv_id}/activate", response_model=CVResponse)
def activate_cv(
    cv_id: UUID,
    db: Session = Depends(get_db)
):
    """Activate a CV (deactivate others in same profile)"""
    cv = CVService.activate_cv(db, cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv