"""
API routes for profiles and CVs
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import os
import shutil
from pathlib import Path

from database import get_db
from schemas import (
    ProfileCreate, ProfileUpdate, ProfileResponse, ProfileDetailResponse,
    CVCreate, CVUpdate, CVResponse,
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    ErrorResponse
)
from service import ProfileService, CVService, UserPreferenceService
from config import settings

router = APIRouter(prefix="/api", tags=["api"])


# ============================================================================
# Profile Endpoints
# ============================================================================

@router.post("/profiles", response_model=ProfileResponse, status_code=201)
def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new profile"""
    try:
        profile = ProfileService.create_profile(db, profile_data)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/profiles/{profile_id}", response_model=ProfileDetailResponse)
def get_profile(
    profile_id: UUID,
    db: Session = Depends(get_db)
):
    """Get profile details including CVs"""
    profile = ProfileService.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/profiles", response_model=List[ProfileResponse])
def list_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all profiles"""
    profiles = ProfileService.list_profiles(db, skip=skip, limit=limit)
    return profiles


@router.put("/profiles/{profile_id}", response_model=ProfileResponse)
def update_profile(
    profile_id: UUID,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update a profile"""
    profile = ProfileService.update_profile(db, profile_id, profile_data)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.delete("/profiles/{profile_id}", status_code=204)
def delete_profile(
    profile_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a profile (soft delete)"""
    if not ProfileService.delete_profile(db, profile_id):
        raise HTTPException(status_code=404, detail="Profile not found")


@router.get("/profiles/email/{email}", response_model=ProfileDetailResponse)
def get_profile_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    """Get profile by email"""
    profile = ProfileService.get_profile_by_email(db, email)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


# ============================================================================
# CV Endpoints
# ============================================================================

@router.post("/profiles/{profile_id}/cvs", response_model=CVResponse, status_code=201)
async def upload_cv(
    profile_id: UUID,
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    target_roles: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a new CV for a profile"""
    
    # Verify profile exists
    profile = ProfileService.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC, and DOCX files are allowed"
        )
    
    # Create upload directory
    upload_dir = Path(settings.cv_upload_dir) / str(profile_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / file.filename
    try:
        contents = await file.read()
        file_size = len(contents)
        
        # Check file size
        if file_size > settings.max_cv_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds {settings.max_cv_size_mb}MB limit"
            )
        
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Parse target roles and skills
    target_roles_list = target_roles.split(',') if target_roles else []
    skills_list = skills.split(',') if skills else []
    
    # Create CV record
    cv_data = CVCreate(
        filename=file.filename,
        category=category,
        target_roles=[r.strip() for r in target_roles_list if r.strip()],
        skills=[s.strip() for s in skills_list if s.strip()]
    )
    
    cv = CVService.create_cv(db, profile_id, cv_data, str(file_path), file_size)
    return cv


@router.get("/cvs/{cv_id}", response_model=CVResponse)
def get_cv(
    cv_id: UUID,
    db: Session = Depends(get_db)
):
    """Get CV details"""
    cv = CVService.get_cv(db, cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


@router.get("/profiles/{profile_id}/cvs", response_model=List[CVResponse])
def list_profile_cvs(
    profile_id: UUID,
    db: Session = Depends(get_db)
):
    """List all CVs for a profile"""
    profile = ProfileService.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    cvs = CVService.list_profile_cvs(db, profile_id)
    return cvs


@router.put("/cvs/{cv_id}", response_model=CVResponse)
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


@router.delete("/cvs/{cv_id}", status_code=204)
def delete_cv(
    cv_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a CV"""
    if not CVService.delete_cv(db, cv_id):
        raise HTTPException(status_code=404, detail="CV not found")


@router.post("/cvs/{cv_id}/activate", response_model=CVResponse)
def activate_cv(
    cv_id: UUID,
    db: Session = Depends(get_db)
):
    """Activate a CV (deactivate others in same profile)"""
    cv = CVService.activate_cv(db, cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


# ============================================================================
# User Preferences Endpoints
# ============================================================================

@router.post("/profiles/{profile_id}/preferences", response_model=UserPreferenceResponse, status_code=201)
def create_preferences(
    profile_id: UUID,
    pref_data: UserPreferenceCreate,
    db: Session = Depends(get_db)
):
    """Create or update user preferences"""
    profile = ProfileService.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    prefs = UserPreferenceService.create_or_update_preferences(db, profile_id, pref_data)
    return prefs


@router.get("/profiles/{profile_id}/preferences", response_model=UserPreferenceResponse)
def get_preferences(
    profile_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    profile = ProfileService.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    prefs = UserPreferenceService.get_preferences(db, profile_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return prefs


@router.put("/profiles/{profile_id}/preferences", response_model=UserPreferenceResponse)
def update_preferences(
    profile_id: UUID,
    pref_data: UserPreferenceUpdate,
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    profile = ProfileService.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    prefs = UserPreferenceService.update_preferences(db, profile_id, pref_data)
    return prefs
