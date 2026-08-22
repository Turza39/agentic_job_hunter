"""
Routers module - API route handlers
"""
from .user import router as user_router
from .cv import router as cv_router
from .preference import router as preference_router
from .company import router as company_router
from .job import router as job_router

__all__ = [
    "user_router",      # includes profile + CV endpoints
    "cv_router",        # standalone CV endpoints (get, update, delete, activate)
    "preference_router",
    "company_router",
    "job_router",
]