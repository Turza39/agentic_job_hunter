"""
User/Profile service
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID

from ..models.user import Profile
from ..schemas.user import ProfileCreate, ProfileUpdate


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