"""
Customer reminder processing repository
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
import uuid

from app.models.customer_reminder_processing import CustomerReminderProcessing
from app.utils.timezone_utils import get_indonesia_utc_now

logger = logging.getLogger(__name__)


class CustomerReminderProcessingRepository:
    """Repository for customer reminder processing operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_processing_tracker(
        self, 
        transaction_id: Optional[uuid.UUID] = None,
        created_by: Optional[str] = None
    ) -> CustomerReminderProcessing:
        """Create a new processing tracker"""
        try:
            if transaction_id is None:
                transaction_id = uuid.uuid4()
            
            db_tracker = CustomerReminderProcessing(
                transaction_id=transaction_id,
                progress=0,
                status='inprogress',
                created_by=created_by or 'system',
                created_date=get_indonesia_utc_now(),
                last_modified_by=created_by or 'system',
                last_modified_date=get_indonesia_utc_now()
            )
            
            self.db.add(db_tracker)
            self.db.commit()
            self.db.refresh(db_tracker)
            
            logger.info(f"Created processing tracker: {db_tracker.transaction_id}")
            return db_tracker
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating processing tracker: {str(e)}")
            raise e
    
    def get_by_transaction_id(self, transaction_id: uuid.UUID) -> Optional[CustomerReminderProcessing]:
        """Get processing tracker by transaction ID"""
        return self.db.query(CustomerReminderProcessing).filter(
            CustomerReminderProcessing.transaction_id == transaction_id
        ).first()
    
    def update_progress(
        self, 
        transaction_id: uuid.UUID, 
        progress: int,
        modified_by: Optional[str] = None
    ) -> Optional[CustomerReminderProcessing]:
        """Update processing progress"""
        try:
            db_tracker = self.get_by_transaction_id(transaction_id)
            if not db_tracker:
                logger.warning(f"Processing tracker not found for transaction_id: {transaction_id}")
                return None
            
            # Validate progress range
            if not (0 <= progress <= 100):
                logger.warning(f"Invalid progress value: {progress}. Must be between 0 and 100")
                return None
            
            db_tracker.progress = progress
            db_tracker.last_modified_by = modified_by or 'system'
            db_tracker.last_modified_date = get_indonesia_utc_now()
            
            self.db.commit()
            self.db.refresh(db_tracker)
            
            logger.info(f"Updated progress for transaction {transaction_id}: {progress}%")
            return db_tracker
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating progress: {str(e)}")
            raise e
    
    def update_status(
        self, 
        transaction_id: uuid.UUID, 
        status: str,
        progress: Optional[int] = None,
        modified_by: Optional[str] = None
    ) -> Optional[CustomerReminderProcessing]:
        """Update processing status"""
        try:
            db_tracker = self.get_by_transaction_id(transaction_id)
            if not db_tracker:
                logger.warning(f"Processing tracker not found for transaction_id: {transaction_id}")
                return None
            
            # Validate status
            if status not in ['inprogress', 'completed']:
                logger.warning(f"Invalid status value: {status}. Must be 'inprogress' or 'completed'")
                return None
            
            db_tracker.status = status
            if progress is not None:
                if 0 <= progress <= 100:
                    db_tracker.progress = progress
                else:
                    logger.warning(f"Invalid progress value: {progress}. Progress not updated")
            
            db_tracker.last_modified_by = modified_by or 'system'
            db_tracker.last_modified_date = get_indonesia_utc_now()
            
            self.db.commit()
            self.db.refresh(db_tracker)
            
            logger.info(f"Updated status for transaction {transaction_id}: {status}")
            return db_tracker
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating status: {str(e)}")
            raise e
    
    def get_processing_stats(self, transaction_id: uuid.UUID) -> dict:
        """Get processing statistics for a transaction"""
        try:
            db_tracker = self.get_by_transaction_id(transaction_id)
            if not db_tracker:
                return {"error": "Transaction not found"}
            
            return {
                "transaction_id": str(db_tracker.transaction_id),
                "progress": db_tracker.progress,
                "status": db_tracker.status,
                "created_date": db_tracker.created_date.isoformat() if db_tracker.created_date else None,
                "last_modified_date": db_tracker.last_modified_date.isoformat() if db_tracker.last_modified_date else None
            }
            
        except Exception as e:
            logger.error(f"Error getting processing stats: {str(e)}")
            return {"error": str(e)}