"""
CV service
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import hashlib
import os

from ..models.cv import CV
from ..schemas.cv import CVCreate, CVUpdate


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