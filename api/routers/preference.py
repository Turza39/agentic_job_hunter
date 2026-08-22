"""
User preference API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ..core.database import get_db
from ..schemas.preference import UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse
from ..services.preference import UserPreferenceService
from ..services.user import ProfileService

router = APIRouter(prefix="/profiles", tags=["preferences"])


@router.post("/{profile_id}/preferences", response_model=UserPreferenceResponse, status_code=201)
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


@router.get("/{profile_id}/preferences", response_model=UserPreferenceResponse)
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


@router.put("/{profile_id}/preferences", response_model=UserPreferenceResponse)
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