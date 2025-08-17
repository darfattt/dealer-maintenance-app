"""
Customer reminder processing tracker model for customer service
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CustomerReminderProcessing(Base):
    """Customer reminder processing tracker model"""
    
    __tablename__ = "customer_reminder_processing"
    __table_args__ = {
        "schema": "customer"
    }
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Transaction identifier
    transaction_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True)
    
    # Processing tracking
    progress = Column(Integer, nullable=False, default=0)  # 0-100 percentage
    status = Column(String(20), nullable=False, default='inprogress')  # 'inprogress' or 'completed'
    
    # Audit fields
    created_by = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified_by = Column(String(100), nullable=True)
    last_modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CustomerReminderProcessing(id={self.id}, transaction_id={self.transaction_id}, status={self.status}, progress={self.progress})>"
    
    def to_dict(self):
        """Convert customer reminder processing to dictionary"""
        return {
            "id": str(self.id),
            "transaction_id": str(self.transaction_id),
            "progress": self.progress,
            "status": self.status,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "last_modified_by": self.last_modified_by,
            "last_modified_date": self.last_modified_date.isoformat() if self.last_modified_date else None,
        }