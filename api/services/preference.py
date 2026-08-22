"""
User preference service
"""
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ..models.preference import UserPreference
from ..schemas.preference import UserPreferenceCreate, UserPreferenceUpdate


class UserPreferenceService:
    """Service for managing user preferences"""
    
    @staticmethod
    def create_or_update_preferences(
        db: Session,
        profile_id: UUID,
        pref_data: UserPreferenceCreate
    ) -> UserPreference:
        """Create or update preferences for a profile"""
        prefs = db.query(UserPreference).filter(UserPreference.profile_id == profile_id).first()
        
        if prefs:
            # Update existing
            update_data = pref_data.model_dump()
            for field, value in update_data.items():
                setattr(prefs, field, value)
        else:
            # Create new
            prefs = UserPreference(
                profile_id=profile_id,
                **pref_data.model_dump()
            )
            db.add(prefs)
        
        db.commit()
        db.refresh(prefs)
        return prefs
    
    @staticmethod
    def get_preferences(db: Session, profile_id: UUID) -> Optional[UserPreference]:
        """Get preferences for a profile"""
        return db.query(UserPreference).filter(UserPreference.profile_id == profile_id).first()
    
    @staticmethod
    def update_preferences(
        db: Session,
        profile_id: UUID,
        pref_data: UserPreferenceUpdate
    ) -> Optional[UserPreference]:
        """Update preferences for a profile"""
        prefs = UserPreferenceService.get_preferences(db, profile_id)
        if not prefs:
            # Create new preferences with defaults
            create_data = UserPreferenceCreate(**pref_data.model_dump(exclude_unset=True))
            return UserPreferenceService.create_or_update_preferences(db, profile_id, create_data)
        
        update_data = pref_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prefs, field, value)
        
        db.commit()
        db.refresh(prefs)
        return prefs