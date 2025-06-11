"""
Common controller for basic endpoints (health, root)
"""
from fastapi import APIRouter
from datetime import datetime
from models.schemas import HealthResponse, MessageResponse

router = APIRouter()


@router.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint"""
    return {"message": "Dealer Dashboard API", "version": "1.0.0"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}
