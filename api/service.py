"""
Service layer for business logic
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Profile, CV, UserPreference, Company, JobSource, Job
from schemas import (
    ProfileCreate, ProfileUpdate, CVCreate, CVUpdate,
    UserPreferenceCreate, UserPreferenceUpdate,
    CompanyCreate, CompanyUpdate, JobSourceCreate, JobSourceUpdate,
    JobCreate, JobUpdate
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


class CompanyService:
    """Service for managing companies"""
    
    @staticmethod
    def create_company(db: Session, company_data: CompanyCreate) -> Company:
        """Create a new company"""
        try:
            company = Company(
                name=company_data.name,
                website=str(company_data.website) if company_data.website else None,
                career_page_url=str(company_data.career_page_url) if company_data.career_page_url else None,
                logo_url=str(company_data.logo_url) if company_data.logo_url else None,
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
            raise ValueError(f"Company with name '{company_data.name}' already exists")
            
    @staticmethod
    def get_company(db: Session, company_id: UUID) -> Optional[Company]:
        """Get a company by ID"""
        return db.query(Company).filter(Company.id == company_id).first()
        
    @staticmethod
    def list_companies(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
        """List active companies"""
        return db.query(Company).filter(Company.is_active == True).offset(skip).limit(limit).all()
        
    @staticmethod
    def update_company(db: Session, company_id: UUID, company_data: CompanyUpdate) -> Optional[Company]:
        """Update a company"""
        company = CompanyService.get_company(db, company_id)
        if not company:
            return None
            
        update_data = company_data.model_dump(exclude_unset=True)
        # Convert URLs to strings
        for url_field in ['website', 'career_page_url', 'logo_url']:
            if url_field in update_data and update_data[url_field]:
                update_data[url_field] = str(update_data[url_field])
                
        for field, value in update_data.items():
            setattr(company, field, value)
            
        try:
            db.commit()
            db.refresh(company)
            return company
        except IntegrityError:
            db.rollback()
            raise ValueError("Company name conflict")
            
    @staticmethod
    def delete_company(db: Session, company_id: UUID) -> bool:
        """Deactivate/Delete a company (soft delete)"""
        company = CompanyService.get_company(db, company_id)
        if not company:
            return False
        company.is_active = False
        db.commit()
        return True


class JobSourceService:
    """Service for managing job sources"""
    
    @staticmethod
    def create_job_source(db: Session, source_data: JobSourceCreate) -> JobSource:
        """Create a new job source"""
        source = JobSource(
            company_id=source_data.company_id,
            source_type=source_data.source_type,
            source_url=str(source_data.source_url) if source_data.source_url else None,
            api_endpoint=str(source_data.api_endpoint) if source_data.api_endpoint else None,
            extraction_strategy=source_data.extraction_strategy,
            auth_method=source_data.auth_method,
            auth_config=source_data.auth_config,
            polling_interval_hours=source_data.polling_interval_hours,
        )
        db.add(source)
        try:
            db.commit()
            db.refresh(source)
            return source
        except IntegrityError:
            db.rollback()
            raise ValueError("Integrity error creating job source (invalid company_id?)")
            
    @staticmethod
    def get_job_source(db: Session, source_id: UUID) -> Optional[JobSource]:
        """Get a job source by ID"""
        return db.query(JobSource).filter(JobSource.id == source_id).first()
        
    @staticmethod
    def list_job_sources(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None, source_type: Optional[str] = None) -> List[JobSource]:
        """List job sources with optional filters"""
        query = db.query(JobSource)
        if is_active is not None:
            query = query.filter(JobSource.is_active == is_active)
        if source_type is not None:
            query = query.filter(JobSource.source_type == source_type)
        return query.offset(skip).limit(limit).all()
        
    @staticmethod
    def update_job_source(db: Session, source_id: UUID, source_data: JobSourceUpdate) -> Optional[JobSource]:
        """Update a job source"""
        source = JobSourceService.get_job_source(db, source_id)
        if not source:
            return None
            
        update_data = source_data.model_dump(exclude_unset=True)
        # Convert URLs to strings
        for url_field in ['source_url', 'api_endpoint']:
            if url_field in update_data and update_data[url_field]:
                update_data[url_field] = str(update_data[url_field])
                
        for field, value in update_data.items():
            setattr(source, field, value)
            
        db.commit()
        db.refresh(source)
        return source
        
    @staticmethod
    def delete_job_source(db: Session, source_id: UUID) -> bool:
        """Deactivate/Delete a job source"""
        source = JobSourceService.get_job_source(db, source_id)
        if not source:
            return False
        source.is_active = False
        db.commit()
        return True


class JobService:
    """Service for managing jobs"""
    
    @staticmethod
    def create_job(db: Session, job_data: JobCreate) -> Job:
        """Create a job with normalization and hash generation"""
        title_stripped = job_data.title.strip()
        app_url_str = str(job_data.application_url) if job_data.application_url else None
        
        # Calculate unique normalized hash
        hash_input = f"{job_data.company_id}:{title_stripped.lower()}:{app_url_str.lower() if app_url_str else ''}"
        normalized_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
        
        # Deduplication check
        existing_job = db.query(Job).filter(
            Job.company_id == job_data.company_id,
            Job.title == title_stripped,
            Job.application_url == app_url_str
        ).first()
        
        if existing_job:
            return existing_job
            
        job = Job(
            company_id=job_data.company_id,
            source_id=job_data.source_id,
            title=title_stripped,
            description=job_data.description,
            location=job_data.location,
            job_type=job_data.job_type,
            remote_type=job_data.remote_type,
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            currency=job_data.currency,
            experience_required=job_data.experience_required,
            experience_level=job_data.experience_level,
            requirements=job_data.requirements or [],
            nice_to_have=job_data.nice_to_have or [],
            application_url=app_url_str,
            posted_at=job_data.posted_at,
            expires_at=job_data.expires_at,
            normalized_hash=normalized_hash,
            is_duplicate=False,
            is_active=True
        )
        db.add(job)
        try:
            db.commit()
            db.refresh(job)
            return job
        except IntegrityError:
            db.rollback()
            # Double check if another process inserted it
            existing = db.query(Job).filter(
                Job.company_id == job_data.company_id,
                Job.title == title_stripped,
                Job.application_url == app_url_str
            ).first()
            if existing:
                return existing
            raise ValueError("Integrity error creating job")
            
    @staticmethod
    def get_job(db: Session, job_id: UUID) -> Optional[Job]:
        """Get a job by ID"""
        return db.query(Job).filter(Job.id == job_id).first()
        
    @staticmethod
    def list_jobs(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None, is_duplicate: Optional[bool] = None, company_id: Optional[UUID] = None) -> List[Job]:
        """List jobs with filters"""
        query = db.query(Job)
        if is_active is not None:
            query = query.filter(Job.is_active == is_active)
        if is_duplicate is not None:
            query = query.filter(Job.is_duplicate == is_duplicate)
        if company_id is not None:
            query = query.filter(Job.company_id == company_id)
        return query.offset(skip).limit(limit).all()
        
    @staticmethod
    def update_job(db: Session, job_id: UUID, job_data: JobUpdate) -> Optional[Job]:
        """Update a job"""
        job = JobService.get_job(db, job_id)
        if not job:
            return None
            
        update_data = job_data.model_dump(exclude_unset=True)
        if 'application_url' in update_data and update_data['application_url']:
            update_data['application_url'] = str(update_data['application_url'])
            
        for field, value in update_data.items():
            setattr(job, field, value)
            
        db.commit()
        db.refresh(job)
        return job
        
    @staticmethod
    def delete_job(db: Session, job_id: UUID) -> bool:
        """Deactivate/Delete a job"""
        job = JobService.get_job(db, job_id)
        if not job:
            return False
        job.is_active = False
        db.commit()
        return True
