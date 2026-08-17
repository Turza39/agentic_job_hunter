"""
Service layer for business logic
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Profile, CV, UserPreference
from schemas import (
    ProfileCreate, ProfileUpdate, CVCreate, CVUpdate,
    UserPreferenceCreate, UserPreferenceUpdate
)
import hashlib
import os
from typing import List, Optional
from uuid import UUID


class ProfileService:
    """Service for managing profiles"""
    
    @staticmethod
    def create_profile(db: Session, profile_data: ProfileCreate) -> Profile:
        """Create a new profile"""
        try:
            profile = Profile(
                name=profile_data.name,
                email=profile_data.email,
                phone=profile_data.phone,
                location=profile_data.location,
                portfolio=str(profile_data.portfolio) if profile_data.portfolio else None,
                github=str(profile_data.github) if profile_data.github else None,
                linkedin=str(profile_data.linkedin) if profile_data.linkedin else None,
                salary_expectation=profile_data.salary_expectation,
                education=profile_data.education or [],
                experience=profile_data.experience or [],
                skills=profile_data.skills or [],
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            return profile
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Profile with email {profile_data.email} already exists")
    
    @staticmethod
    def get_profile(db: Session, profile_id: UUID) -> Optional[Profile]:
        """Get a profile by ID"""
        return db.query(Profile).filter(Profile.id == profile_id).first()
    
    @staticmethod
    def get_profile_by_email(db: Session, email: str) -> Optional[Profile]:
        """Get a profile by email"""
        return db.query(Profile).filter(Profile.email == email).first()
    
    @staticmethod
    def list_profiles(db: Session, skip: int = 0, limit: int = 100) -> List[Profile]:
        """List all active profiles"""
        return db.query(Profile).filter(Profile.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_profile(db: Session, profile_id: UUID, profile_data: ProfileUpdate) -> Optional[Profile]:
        """Update a profile"""
        profile = ProfileService.get_profile(db, profile_id)
        if not profile:
            return None
        
        update_data = profile_data.model_dump(exclude_unset=True)
        
        # Convert URLs to strings
        if 'portfolio' in update_data and update_data['portfolio']:
            update_data['portfolio'] = str(update_data['portfolio'])
        if 'github' in update_data and update_data['github']:
            update_data['github'] = str(update_data['github'])
        if 'linkedin' in update_data and update_data['linkedin']:
            update_data['linkedin'] = str(update_data['linkedin'])
        
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        return profile
    
    @staticmethod
    def delete_profile(db: Session, profile_id: UUID) -> bool:
        """Delete a profile (soft delete)"""
        profile = ProfileService.get_profile(db, profile_id)
        if not profile:
            return False
        
        profile.is_active = False
        db.commit()
        return True


class CVService:
    """Service for managing CVs"""
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def create_cv(db: Session, profile_id: UUID, cv_data: CVCreate, file_path: str, file_size: int) -> CV:
        """Create a new CV"""
        content_hash = CVService.calculate_file_hash(file_path)
        
        cv = CV(
            profile_id=profile_id,
            filename=cv_data.filename,
            category=cv_data.category,
            target_roles=cv_data.target_roles or [],
            skills=cv_data.skills or [],
            file_path=file_path,
            file_size=file_size,
            content_hash=content_hash,
        )
        db.add(cv)
        db.commit()
        db.refresh(cv)
        return cv
    
    @staticmethod
    def get_cv(db: Session, cv_id: UUID) -> Optional[CV]:
        """Get a CV by ID"""
        return db.query(CV).filter(CV.id == cv_id).first()
    
    @staticmethod
    def list_profile_cvs(db: Session, profile_id: UUID) -> List[CV]:
        """List all CVs for a profile"""
        return db.query(CV).filter(CV.profile_id == profile_id).all()
    
    @staticmethod
    def list_active_cvs(db: Session, profile_id: UUID) -> List[CV]:
        """List all active CVs for a profile"""
        return db.query(CV).filter(
            CV.profile_id == profile_id,
            CV.is_active == True
        ).all()
    
    @staticmethod
    def update_cv(db: Session, cv_id: UUID, cv_data: CVUpdate) -> Optional[CV]:
        """Update a CV"""
        cv = CVService.get_cv(db, cv_id)
        if not cv:
            return None
        
        update_data = cv_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cv, field, value)
        
        db.commit()
        db.refresh(cv)
        return cv
    
    @staticmethod
    def delete_cv(db: Session, cv_id: UUID) -> bool:
        """Delete a CV"""
        cv = CVService.get_cv(db, cv_id)
        if not cv:
            return False
        
        # Delete the file
        if os.path.exists(cv.file_path):
            os.remove(cv.file_path)
        
        # Delete from database
        db.delete(cv)
        db.commit()
        return True
    
    @staticmethod
    def activate_cv(db: Session, cv_id: UUID) -> Optional[CV]:
        """Activate a CV (deactivate others in same profile)"""
        cv = CVService.get_cv(db, cv_id)
        if not cv:
            return None
        
        # Deactivate all other CVs for this profile
        db.query(CV).filter(
            CV.profile_id == cv.profile_id,
            CV.id != cv_id
        ).update({CV.is_active: False})
        
        # Activate this CV
        cv.is_active = True
        db.commit()
        db.refresh(cv)
        return cv


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
