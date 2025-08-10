"""
Dealer Access Key repository for database operations
"""

import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from app.models.dealer_access_key import DealerAccessKey

logger = logging.getLogger(__name__)


class DealerAccessKeyRepository:
    """Repository for dealer access key operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_access_key(self, access_key: str) -> Optional[DealerAccessKey]:
        """Get dealer access key by access key string"""
        try:
            return self.db.query(DealerAccessKey).filter(
                DealerAccessKey.access_key == access_key
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting access key: {str(e)}")
            return None
    
    def validate_access_key(self, access_key: str) -> Optional[DealerAccessKey]:
        """Validate access key and return if valid"""
        try:
            # Get access key record
            key_record = self.db.query(DealerAccessKey).filter(
                and_(
                    DealerAccessKey.access_key == access_key,
                    DealerAccessKey.is_active == True
                )
            ).first()
            
            if not key_record:
                logger.warning(f"Access key not found or inactive: {access_key[:10]}...")
                return None
            
            # Check if key is valid (not expired)
            if not key_record.is_valid():
                logger.warning(f"Access key expired or invalid: {access_key[:10]}...")
                return None
            
            # Update last used timestamp
            key_record.update_last_used()
            self.db.commit()
            
            logger.info(f"Access key validated for dealer: {key_record.dealer_id}")
            return key_record
            
        except SQLAlchemyError as e:
            logger.error(f"Error validating access key: {str(e)}")
            self.db.rollback()
            return None
    
    def get_by_dealer_id(self, dealer_id: str) -> List[DealerAccessKey]:
        """Get all access keys for a dealer"""
        try:
            return self.db.query(DealerAccessKey).filter(
                DealerAccessKey.dealer_id == dealer_id
            ).order_by(DealerAccessKey.created_at.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting access keys for dealer {dealer_id}: {str(e)}")
            return []
    
    def get_active_keys_by_dealer(self, dealer_id: str) -> List[DealerAccessKey]:
        """Get active access keys for a dealer"""
        try:
            return self.db.query(DealerAccessKey).filter(
                and_(
                    DealerAccessKey.dealer_id == dealer_id,
                    DealerAccessKey.is_active == True
                )
            ).order_by(DealerAccessKey.created_at.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting active access keys for dealer {dealer_id}: {str(e)}")
            return []
    
    def create(self, dealer_id: str, name: str = None, expires_at: datetime = None) -> Optional[DealerAccessKey]:
        """Create a new access key for a dealer"""
        try:
            # Generate new access key
            access_key = DealerAccessKey.generate_access_key(dealer_id)
            
            # Create new record
            new_key = DealerAccessKey(
                dealer_id=dealer_id,
                access_key=access_key,
                name=name or f"API Key - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                expires_at=expires_at,
                is_active=True
            )
            
            self.db.add(new_key)
            self.db.commit()
            self.db.refresh(new_key)
            
            logger.info(f"Created new access key for dealer: {dealer_id}")
            return new_key
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating access key for dealer {dealer_id}: {str(e)}")
            self.db.rollback()
            return None
    
    def deactivate(self, access_key_id: str) -> bool:
        """Deactivate an access key"""
        try:
            key_record = self.db.query(DealerAccessKey).filter(
                DealerAccessKey.id == access_key_id
            ).first()
            
            if not key_record:
                logger.warning(f"Access key not found: {access_key_id}")
                return False
            
            key_record.is_active = False
            key_record.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Deactivated access key: {access_key_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deactivating access key {access_key_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def activate(self, access_key_id: str) -> bool:
        """Activate an access key"""
        try:
            key_record = self.db.query(DealerAccessKey).filter(
                DealerAccessKey.id == access_key_id
            ).first()
            
            if not key_record:
                logger.warning(f"Access key not found: {access_key_id}")
                return False
            
            key_record.is_active = True
            key_record.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Activated access key: {access_key_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error activating access key {access_key_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def update_expiry(self, access_key_id: str, expires_at: datetime = None) -> bool:
        """Update access key expiry date"""
        try:
            key_record = self.db.query(DealerAccessKey).filter(
                DealerAccessKey.id == access_key_id
            ).first()
            
            if not key_record:
                logger.warning(f"Access key not found: {access_key_id}")
                return False
            
            key_record.expires_at = expires_at
            key_record.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Updated expiry for access key: {access_key_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating expiry for access key {access_key_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def delete(self, access_key_id: str) -> bool:
        """Delete an access key (permanent removal)"""
        try:
            key_record = self.db.query(DealerAccessKey).filter(
                DealerAccessKey.id == access_key_id
            ).first()
            
            if not key_record:
                logger.warning(f"Access key not found: {access_key_id}")
                return False
            
            self.db.delete(key_record)
            self.db.commit()
            logger.info(f"Deleted access key: {access_key_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting access key {access_key_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def cleanup_expired_keys(self) -> int:
        """Remove expired keys that are older than 30 days"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            expired_keys = self.db.query(DealerAccessKey).filter(
                and_(
                    DealerAccessKey.expires_at < datetime.utcnow(),
                    DealerAccessKey.expires_at < cutoff_date
                )
            ).all()
            
            count = len(expired_keys)
            
            for key in expired_keys:
                self.db.delete(key)
            
            self.db.commit()
            logger.info(f"Cleaned up {count} expired access keys")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error cleaning up expired keys: {str(e)}")
            self.db.rollback()
            return 0