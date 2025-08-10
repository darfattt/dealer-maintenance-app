"""
Dependencies for customer service
"""

import os
import sys
import logging
from typing import Optional
from fastapi import HTTPException, status, Header, Depends
from sqlalchemy.orm import Session

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.database import DatabaseManager
from app.config import settings
from app.repositories.dealer_access_key_repository import DealerAccessKeyRepository
from app.models.dealer_access_key import DealerAccessKey

logger = logging.getLogger(__name__)

# Database manager
db_manager = DatabaseManager(settings.db_schema)


def get_db() -> Session:
    """Get database session"""
    db = next(db_manager.get_session())
    try:
        yield db
    finally:
        db.close()


def get_dealer_from_access_key(
    x_access_key: Optional[str] = Header(None, alias="X-Access-Key"),
    db: Session = Depends(get_db)
) -> DealerAccessKey:
    """
    Validate access key and return dealer access key record
    
    Args:
        x_access_key: Access key from X-Access-Key header
        db: Database session
    
    Returns:
        DealerAccessKey: Validated access key record
    
    Raises:
        HTTPException: If access key is invalid or missing
    """
    if not x_access_key:
        logger.warning("Access key missing in request headers")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access key required. Please provide X-Access-Key header."
        )
    
    # Validate access key
    access_key_repo = DealerAccessKeyRepository(db)
    access_key_record = access_key_repo.validate_access_key(x_access_key)
    
    if not access_key_record:
        logger.warning(f"Invalid or expired access key: {x_access_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access key."
        )
    
    logger.info(f"Access key validated for dealer: {access_key_record.dealer_id}")
    return access_key_record


def get_optional_dealer_from_access_key(
    x_access_key: Optional[str] = Header(None, alias="X-Access-Key"),
    db: Session = Depends(get_db)
) -> Optional[DealerAccessKey]:
    """
    Optional access key validation - returns None if no key provided
    
    Args:
        x_access_key: Access key from X-Access-Key header
        db: Database session
    
    Returns:
        Optional[DealerAccessKey]: Validated access key record or None
    """
    if not x_access_key:
        return None
    
    # Validate access key
    access_key_repo = DealerAccessKeyRepository(db)
    access_key_record = access_key_repo.validate_access_key(x_access_key)
    
    if access_key_record:
        logger.info(f"Access key validated for dealer: {access_key_record.dealer_id}")
    
    return access_key_record