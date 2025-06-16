"""
Health check routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils.database import check_database_health
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("")
def health_check():
    """
    Basic health check
    """
    return {
        "status": "healthy",
        "service": "account-service",
        "version": "1.0.0"
    }


@router.get("/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check including database connectivity
    """
    health_status = {
        "status": "healthy",
        "service": "account-service",
        "version": "1.0.0",
        "checks": {
            "database": "healthy"
        }
    }
    
    # Check database connectivity
    try:
        if not check_database_health():
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = "unhealthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = "unhealthy"
    
    return health_status


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check for Kubernetes
    """
    try:
        # Check if database is accessible
        if check_database_health():
            return {"status": "ready"}
        else:
            return {"status": "not ready", "reason": "database unavailable"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "not ready", "reason": str(e)}


@router.get("/live")
def liveness_check():
    """
    Liveness check for Kubernetes
    """
    return {"status": "alive"}
