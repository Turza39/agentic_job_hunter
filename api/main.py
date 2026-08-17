"""
Main FastAPI application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from pathlib import Path

from database import Base, engine, get_db
from config import settings
from routes import router
from schemas import HealthResponse

# Create upload directory if it doesn't exist
Path(settings.cv_upload_dir).mkdir(parents=True, exist_ok=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Job Hunter API",
    description="API for managing job hunter profiles and applications",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="ok",
        database=db_status,
        version="0.1.0"
    )


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Agentic Job Hunter API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================================
# Startup and Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    print("=" * 60)
    print("Agentic Job Hunter API Starting...")
    print("=" * 60)
    print(f"Database: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print(f"CV Upload Directory: {settings.cv_upload_dir}")
    print(f"Debug Mode: {settings.debug}")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    print("\nAgentic Job Hunter API Shutting Down...")


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    return {
        "detail": "Internal server error",
        "error": str(exc) if settings.debug else "An error occurred"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
