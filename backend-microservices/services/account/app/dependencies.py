"""
FastAPI dependencies for the account service
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.user import User
from app.controllers.auth_controller import AuthController
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils.database import DatabaseManager
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Database manager for account schema
db_manager = DatabaseManager("account")

# Security scheme
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    
    Yields:
        Database session with account schema context
    """
    db = next(db_manager.get_session())
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Use auth controller to get current user
        auth_controller = AuthController(db)
        user = auth_controller.get_current_user(token)
        
        return user
    except HTTPException:
        # Re-raise HTTP exceptions from auth controller
        raise
    except Exception as e:
        logger.error(f"Failed to authenticate user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from JWT token (optional)
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current authenticated user or None if not authenticated
    """
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
