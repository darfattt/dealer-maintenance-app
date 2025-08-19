"""
Health check routes for customer service
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.dependencies import get_db
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    summary="Basic health check",
    description="Basic health check endpoint"
)
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version
    }


@router.get(
    "/detailed",
    summary="Detailed health check",
    description="Detailed health check including database connectivity"
)
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check including database"""
    health_status = {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version,
        "checks": {
            "database": "unknown",
            "database_schema": settings.db_schema
        }
    }
    
    # Test database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
    
    return health_status