"""
Dependencies for customer service
"""

import os
import sys
import logging
from typing import Optional, Generator
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.database import DatabaseManager
from utils.auth import decode_token
from app.config import settings

logger = logging.getLogger(__name__)

# Database manager
db_manager = DatabaseManager(settings.db_schema)

# Security scheme for Bearer token
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = next(db_manager.get_session())
    try:
        yield db
    finally:
        db.close()


class UserContext:
    """User context extracted from JWT token"""
    def __init__(self, user_id: str, email: str, role: str, dealer_id: str):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.dealer_id = dealer_id


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserContext:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        UserContext: User context with dealer information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Decode and validate JWT token
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user information from token
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        dealer_id = payload.get("dealer_id")
        
        if not user_id or not email or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # For dealer users, dealer_id is required
        if role in ["DEALER_ADMIN", "DEALER_USER"] and not dealer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Dealer ID required for dealer users",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"User authenticated: {email} (dealer: {dealer_id})")
        
        return UserContext(
            user_id=user_id,
            email=email,
            role=role,
            dealer_id=dealer_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
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
) -> Optional[UserContext]:
    """
    Get current authenticated user from JWT token (optional)
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        UserContext or None if not authenticated
    """
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None